## Why

在排查 KKTIX 漏抓「芒果醬」的過程中,使用者問了一個好問題:其他平台會不會也有類似的「只抓到部分活動」問題?逐一檢查後確認:
- **udn售票網**:首頁其實有 3 個分類頁籤(推薦節目/近期節目/套票組合),共 35 張活動卡片都已經在同一次請求拿到的靜態 HTML 裡,但現有的解析邏輯只認得「推薦節目」頁籤的卡片結構(`.yd_card-title`、純 `PRODUCT_ID` 連結),另外兩個頁籤的 23 張卡片因為用不同的標題 class(`.yd_card-text`)或不同的連結參數(`AGId` 而非 `PRODUCT_ID`)而被靜默跳過
- **年代售票 Ticket.com.tw**:首頁的兩個小部件(本月熱門輪播、即將開賣輪播)只是首頁精選,使用者實際去網站找到了真正完整的「演唱會節目總表」頁面(`UTK0101_06.aspx?TYPE=1&CATEGORY=205`),這個頁面用乾淨的卡片結構(`.moreBox`)列出完整的演唱會清單,比首頁的兩個部件更完整(首頁兩個部件合計只抓到 11 筆,其中還有 8 筆是首頁最上面大圖輪播、完全沒有文字可抓;這個完整列表頁有 13 筆全部帶有乾淨的標題文字)
- ibon、遠大售票 Ticket Plus 的 API 經使用者確認回傳的就是完整資料,不需要調整

## What Changes

- 修改 `src/scrapers/udn.py`:解析邏輯同時支援 `.yd_card-title`/`.yd_card-text` 兩種標題結構,以及 `PRODUCT_ID`/`AGId` 兩種連結參數,涵蓋首頁三個頁籤的所有卡片
- 修改 `src/scrapers/ticket_com_tw.py`:改用「演唱會節目總表」頁面(`UTK0101_06.aspx?TYPE=1&CATEGORY=205`)取代原本解析首頁兩個輪播部件的做法,解析 `.moreBox` 卡片結構
- 不改變對外介面(`fetch_events()` 仍回傳 `list[Event]`),不影響其他 5 個來源

## Capabilities

### New Capabilities
(無)

### Modified Capabilities
- `concert-source-scraping`: 「從年代售票抓取活動列表」「從 udn售票網抓取活動列表」這兩條需求,補上「涵蓋所有分類/頁籤的活動,不只是首頁精選」的要求

## Impact

- 只影響 `src/scrapers/udn.py`、`src/scrapers/ticket_com_tw.py`,不影響其他來源或比對/通知/健康告警邏輯
- udn 的請求次數不變(同一次首頁請求,只是解析邏輯更完整),ticket_com_tw 改抓的是另一個網址,請求次數也不變(還是一次請求)
