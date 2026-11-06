## Context

現有 7 個 scraper(`tixcraft`、`ticket_com_tw`、`udn`、`kham`、`kktix`、`ticketplus`、`ibon`)都遵循同一個模式:內部 try/except 吞掉請求/解析錯誤,失敗時回傳空清單 `[]`,讓 `main.py` 不會因為單一來源掛掉而中斷。這個設計對「不讓整個流程崩潰」是對的,但代價是錯誤變成無聲的——`main.py` 現在完全看不出某次 `[]` 是「這個平台本來就沒有新場次」還是「選擇器壞了/被擋了」。

`src/scrapers/__init__.py` 目前的 `SCRAPERS` 是一個 `list[Callable]`,呼叫端只拿到 `list[Event]`,沒有來源名稱資訊——如果該次回傳空清單,連「是哪個來源」都無法得知,因為來源名稱原本是從 `Event.source` 欄位反推的,而空清單裡沒有任何 `Event`。

## Goals / Non-Goals

**Goals:**
- 讓 `main.py` 知道「這次是哪個來源回傳了空結果」,不只是「拿到幾筆活動」
- 用簡單、可跨執行持久化的計數器判斷「連續空結果」,達門檻時觸發一次 Discord 告警
- 告警只發一次(直到該來源恢復、再重新進入新一輪失效),避免每 30 分鐘一直重複洗版

**Non-Goals:**
- 不區分「請求層失敗」(連線錯誤、HTTP 錯誤)與「解析層失敗」(選擇器找不到東西但請求成功)——兩者現有的 try/except 都已經統一轉成空清單,這次也統一用「空清單」當判斷依據,不去改動各 scraper 內部已經區分 request 失敗 vs parse 失敗的 log 訊息
- 不做更複雜的健康儀表板或歷史趨勢分析,只做「連續失敗 N 次告警」這個最小可用的機制

## Decisions

### 用「連續空結果次數」當判斷依據,不區分失敗原因
這 7 個來源都是持續在賣票的大型平台,正常情況下每次執行都會有數十筆活動,不會真的變成 0。所以「連續 N 次回傳空清單」本身就是很強的異常訊號,不需要額外去區分是連線被擋、HTTP 錯誤、還是選擇器找不到東西——這三種情況使用者要做的事都一樣:去檢查那個 scraper。這也同時涵蓋了最危險的情況:**選擇器悄悄壞掉但程式沒有拋出任何例外**,這種情況用「有沒有拋 exception」是抓不到的,但用「有沒有抓到活動」可以。

已考慮過的替代方案:在每個 scraper 內部把「request 失敗」「parse 失敗」「成功但 0 筆」三種情況分開回傳(例如回傳一個狀態 enum)。這樣資訊更精確,但每個 scraper 都要改回傳介面,對這個規模的專案是過度設計;現有的「空清單=異常訊號」已經能達到使用者真正需要的效果(知道該去檢查哪個平台)。

### 把 `SCRAPERS` 從 `list[Callable]` 改成 `list[tuple[str, Callable]]`
每個 scraper 模組本來就有一個 `SOURCE` 常數(例如 `tixcraft.SOURCE = "tixcraft"`),`src/scrapers/__init__.py` 改成直接用這些常數建立 `(來源名稱, 抓取函式)` 的配對清單。這樣 `main.py` 不管該次回傳的活動清單是不是空的,都能明確知道是哪個來源,不需要從 `Event.source` 反推。

### 新增 `src/health.py`,獨立於 `src/state.py`
`state.py` 的職責是「已通知活動的去重」,`health.py` 的職責是「來源健康狀態」,兩者資料結構、生命週期都不同(一個是活動 id 集合,一個是每個來源的連續失敗計數+是否已告警),分開成兩個模組、兩個狀態檔(`data/seen_events.json` vs `data/source_health.json`),職責單一、互不影響。

核心邏輯:
```python
def record_result(health: dict, source: str, had_events: bool, threshold: int) -> bool:
    entry = health.setdefault(source, {"consecutive_empty": 0, "alerted": False})
    if had_events:
        entry["consecutive_empty"] = 0
        entry["alerted"] = False
        return False
    entry["consecutive_empty"] += 1
    return entry["consecutive_empty"] >= threshold and not entry["alerted"]
```
`record_result` 只負責判斷「現在該不該發告警」,不會自己把 `alerted` 設成 `True`——呼叫端(`main.py`)在 `send_health_alert` 真的發送成功之後才把 `entry["alerted"] = True`。這跟既有的活動通知邏輯(只有實際發送成功才標記已通知)用同一個模式:告警發送失敗的話,`alerted` 保持 `False`,下次執行會重試發送,不會因為 Discord 一時故障就永久錯過這個告警。`alerted` 被設為 `True` 之後,之後即使持續失敗也不會重複觸發,直到該來源恢復(`had_events=True` 把 `alerted` 重置)才會讓下一輪失效可以再告警一次。

### 告警門檻放在 `config.yaml`,沿用 `notifier.py` 發送
在 `config.yaml` 新增一個 `monitoring.consecutive_empty_threshold` 欄位(預設 3),`src/config.py` 新增一個讀取函式。告警訊息透過在 `notifier.py` 新增 `send_health_alert()` 函式發送——跟現有的活動通知共用同一個 Discord Webhook,只是 embed 內容與顏色不同(用警示色,內容是「哪個來源」「連續幾次」),不需要另外設定第二個 webhook。

## Risks / Trade-offs

- **[風險] 如果某個來源真的某個時間點剛好合法地没有任何活動(理論上機率很低,但不是零),可能會觸發誤報。** → 緩解方式:門檻預設 3 次(即連續 1.5 小時都是空的,以 30 分鐘排程頻率計算),對這 7 個持續在賣票的大型平台幾乎不可能是正常情況;且誤報的代價只是使用者去檢查一下、發現平台其實正常,不是嚴重後果,門檻也可以在 `config.yaml` 調整。
- **[風險] 健康狀態檔跟 `seen_events.json` 一樣需要 CI commit 回 repo,理論上有一樣的並行寫入衝突風險。** → 緩解方式:跟現有機制共用同一次 commit(一起 commit,不是兩次獨立 commit),不會增加額外的衝突機會。

## Open Questions

(無)
