## Context

這是全新專案,repo 目前沒有任何應用程式碼。動機與範圍請參考 proposal.md。以下是已確認的關鍵限制:

- 通知管道是 Discord Webhook(LINE Notify 已停止服務)。
- 執行環境是 GitHub Actions 排程,不依賴使用者本機常駐。
- 語言是 Python。
- 實際調查 tixCraft 活動列表頁(`tixcraft.com/activity`)後確認是**靜態 HTML**,可用 `requests + BeautifulSoup` 直接爬取,活動連結格式固定為 `/activity/detail/{id}`。
- 其他候選平台(ibon、寬宏 kham.com.tw)在初步測試中顯示部分或全部依賴 JavaScript 動態載入,需要 headless browser(Playwright)才能抓取,且 ibon 直接請求時出現連線層級的失敗,可行性尚未確認。

## Goals / Non-Goals

**Goals:**
- 交付一個端到端可運作的系統:至少一個確認可行的售票平台來源 → 比對 → Discord 通知 → 去重狀態 → 排程自動執行。
- 架構上讓新增售票平台來源是「加一個模組」,不是「改既有邏輯」。
- 讓追蹤的藝人清單是使用者可自行編輯的設定檔,不用改程式碼。

**Non-Goals:**
- 本次不實作 ibon、寬宏等需要 headless browser 的來源(架構留出擴充點,但不在本次 tasks 範圍內)。
- 本次不實作 LINE 或其他第二通知管道。
- 不做模糊比對/NLP 式的藝人名稱比對,只做大小寫無關的子字串比對。
- 不引入資料庫,狀態用一個 JSON 檔案即可。

## Decisions

### 專案結構

```
concert_reminder/
├── requirements.txt
├── config.yaml                  # 要追蹤的藝人清單(含別名)
├── .env.example                 # 本機測試用環境變數範例
├── README.md
├── .github/workflows/
│   └── check_concerts.yml       # 排程 workflow
├── data/
│   └── seen_events.json         # 已通知過的活動 id(去重用,由 CI commit 回 repo)
└── src/
    ├── main.py                  # 主流程:抓資料 → 比對 → 通知 → 存狀態
    ├── config.py                # 讀 config.yaml + 環境變數
    ├── state.py                 # 讀寫 data/seen_events.json
    ├── matcher.py                # 比對活動標題是否符合追蹤的藝人
    ├── notifier.py               # 發送 Discord Webhook 訊息
    └── scrapers/
        ├── base.py              # Event dataclass(source, id, title, date, venue, url)
        ├── tixcraft.py           # requests+BeautifulSoup 爬 tixcraft.com/activity
        └── __init__.py          # SCRAPERS 清單,之後加平台就加在這裡
```

**為什麼用這個結構而不是單一腳本**:`scrapers/` 下每個平台一個檔案、共用 `base.py` 的 `Event` 資料結構,是對應 `concert-source-scraping` spec 中「統一資料格式」與「單一來源失敗不影響其他來源」這兩個需求最直接的實作方式——每個 scraper 獨立 try/except,回傳統一格式,`main.py` 不需要知道平台細節。

### 爬取方式:`requests + BeautifulSoup`,不用 Playwright
tixCraft 活動列表是靜態 HTML,`requests` 就能拿到完整內容,不需要啟動瀏覽器,CI 執行更快、更穩定。若之後要加 ibon/寬宏這類需要 JS 的來源,屆時再為那些來源個別引入 Playwright,不影響 tixCraft 的實作。

已考慮過的替代方案:一開始就統一用 Playwright 處理所有來源,好處是爬蟲寫法一致,但對 tixCraft 這種靜態頁面是不必要的開銷(CI 時間更長、需要額外安裝 browser),故不採用。

### 狀態持久化:JSON 檔案 + CI commit 回 repo
GitHub Actions 每次執行都是全新環境,`data/seen_events.json` 需要在 workflow 跑完後 git commit + push 回 repo,下次執行才讀得到上次紀錄。這是常見的 CI 狀態持久化手法,workflow 需要 `contents: write` 權限。

已考慮過的替代方案:外部資料庫(如 SQLite on 一個持久 volume、或雲端 KV)。對這個規模(一個使用者、幾十個藝人)來說是過度設計,JSON 檔案已足夠且不需要額外服務。

### 比對邏輯:標準化後子字串比對
把活動標題與關鍵字都轉小寫、去除前後空白後做子字串比對。符合 `artist-watch-matching` spec 的需求,且實作與除錯都很直接。不做模糊比對(例如 edit distance)以避免誤判。

### 通知時機:只有實際發送成功才標記已通知
對應 `discord-alerting` spec 的「通知失敗不遺失活動的待通知狀態」需求——`main.py` 的流程是先呼叫 `notifier.send()`,確認回應成功後才把該活動 id 加入即將寫入 `seen_events.json` 的集合,失敗的活動維持「未通知」,下次執行會重試。

### 排程頻率:每 30 分鐘
在「接近即時」與「不浪費 GitHub Actions 分鐘數」之間取平衡,使用 `.github/workflows/check_concerts.yml` 的 `schedule: cron: "*/30 * * * *"`,並加 `workflow_dispatch` 方便手動測試。GitHub Actions 的排程本身有數分鐘的延遲誤差,這點在 Risks 中說明。

## Risks / Trade-offs

- **[風險] GitHub Actions 的 `schedule` 事件在負載高時可能延遲數分鐘到數十分鐘才觸發,不是真正的即時。** → 緩解方式:對「演唱會售票公告」這種場景,數十分鐘的延遲是可接受的,且保留 `workflow_dispatch` 可手動立即檢查。
- **[風險] tixCraft 網站改版可能讓目前的 HTML 選擇器失效。** → 緩解方式:scraper 包在 try/except 中,單一來源失敗只記錄錯誤、回傳空清單,不會讓整個流程掛掉;之後維護時只需修對應的 scraper 檔案。
- **[風險] 爬取行為可能被視為對目標網站的負擔,或違反其使用條款。** → 緩解方式:控制請求頻率(每 30 分鐘一次、單一請求)、設定合理的 User-Agent,且用途是個人非商業用途的小量查詢;若之後 tixCraft 有官方 API 或明確禁止爬取的條款,需重新評估。
- **[風險] CI 把 `seen_events.json` commit 回 repo,若同一時間有兩個 workflow run 並行,可能產生 git push 衝突。** → 緩解方式:排程間隔(30 分鐘)遠大於單次執行時間,加上只用 `workflow_dispatch`/`schedule` 兩種觸發方式,實務上重疊機率極低;若真的衝突,CI 這次執行的 push 失敗但下次執行仍會讀到最新狀態,不會造成資料損毀。

## Migration Plan

全新專案,無需遷移既有系統。建置順序:

1. 建立專案骨架與 `scrapers/base.py`、`tixcraft.py`
2. 實作 `matcher.py`、`state.py`、`config.py`、`notifier.py`
3. 串起 `main.py` 並本機測試(用真實或測試用 Discord webhook)
4. 建立 `config.yaml` 範例與 `.github/workflows/check_concerts.yml`
5. `git init`、推送到 GitHub、設定 `DISCORD_WEBHOOK_URL` secret、開啟 Actions 排程

若要回滾,直接停用/刪除 GitHub Actions workflow 即可,不影響任何既有系統。

## Open Questions

(無——所有會影響 spec、架構或 tasks 拆分的問題都已在規劃階段確認完畢。)
