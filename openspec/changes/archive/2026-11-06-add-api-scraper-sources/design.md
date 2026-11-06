## Context

遠大售票(Ticket Plus)與 7-ELEVEN ibon 的首頁都是前端框架(Vue/Angular)渲染,直接拿首頁 HTML 不會有活動內容,原本評估需要 Playwright。但用瀏覽器開發工具的網路面板觀察頁面載入過程後,發現兩者的前端其實是呼叫自己的公開 JSON API 取得資料,這些 API 本身不需要認證、不檢查 Referer/Origin,可以直接用 `requests` 呼叫:

- **遠大售票**:`GET https://apis.ticketplus.com.tw/config/api/v1/getS3?path=main/mainEvents.json`,回傳 `{"allEventMainPageInfo": {"<event_id>": {"title", "start_date", "end_date", "hidden", ...}}}`。活動詳細頁網址規則是 `https://ticketplus.com.tw/activity/{event_id}`(從對方前端的 Vue Router 設定 `path:"/activity/:id"` 確認)。
- **7-ELEVEN ibon**:`GET https://ticket.ibon.com.tw/api/ActivityInfo/GetIndexData?pattern=entertainment`,回傳 `{"Item": {"List": [{"ActivityID", "ActivityName", "ActivitySDate", "GameTicketURL", ...}]}}`。`GameTicketURL` 是相對路徑(例如 `/ActivityInfo/Details?id=39575&pattern=entertainment`),用 `urljoin` 補上網域即可。

## Goals / Non-Goals

**Goals:**
- 用 `requests` 直接呼叫這兩個 JSON API,不引入 Playwright,沿用其他 scraper 的錯誤隔離模式
- 把第三方 API 的回應結構轉換成既有的統一 `Event` 格式

**Non-Goals:**
- 不處理這兩個 API 以外、同網站可能存在的其他功能性 API(例如 ibon 的電影、票務查詢等),只取用列出演出/演唱會的那個端點
- 不嘗試讓這兩個來源回傳場地資訊——目前觀察到的 API 回應都沒有提供場地欄位,`Event.venue` 維持 `None`

## Decisions

### 直接呼叫對方前端用的內部 API,而非重新實作一個瀏覽器
這兩個 API 回應的是乾淨的結構化 JSON,比起啟動瀏覽器渲染後再解析 DOM,直接呼叫 API 更快、更穩定(不受前端版面改動影響,只要 API 的資料結構不變就不會壞)。這跟 KKTIX 解析 `data-react-props` 內嵌 JSON 是同樣的精神——優先找資料本身的結構化來源,而不是解析渲染後的畫面。

已考慮過的替代方案:Playwright。在 API 已知可直接呼叫的情況下,多一層瀏覽器渲染只會增加 CI 時間與維護負擔,沒有對應的好處。

### Ticket Plus:過濾 `hidden: true` 的活動
`allEventMainPageInfo` 裡每個活動有 `hidden` 欄位,`true` 代表對方系統裡標記為不對外顯示的活動(可能是測試資料或已下架)。只保留 `hidden` 為 `false` 的活動,避免通知使用者實際上看不到、買不到票的場次。

### ibon:標題做 `strip()` 處理
觀察到的回應中,`ActivityName` 有些結尾帶有一串 tab 字元(例如 `"Pami in Taipei 2026\t\t\t\t\t\t\t\t\t\t\t"`),直接用會讓比對/通知顯示不乾淨,統一 `strip()` 處理。

## Risks / Trade-offs

- **[風險] 這些是對方前端實際呼叫的內部 API,沒有公開文件與穩定性保證,未來可能改版、加認證,或回應格式改變。** → 緩解方式:沿用既有的錯誤隔離模式(try/except、失敗回傳空清單),單一來源失效不影響其他來源;發現失效時只需要重新觀察對方前端的網路請求、更新對應的 scraper。
- **[風險] 直接呼叫內部 API 比爬公開頁面更容易被視為非預期的使用方式。** → 緩解方式:請求頻率跟其他來源一樣(每 30 分鐘一次、各一個請求),屬於低頻率的個人非商業用途查詢。

## Open Questions

(無)
