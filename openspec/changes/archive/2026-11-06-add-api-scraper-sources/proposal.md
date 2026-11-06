## Why

使用者想追蹤的藝人也可能在遠大售票(Ticket Plus)或 7-ELEVEN ibon 售票。這兩個平台原本評估需要瀏覽器渲染(Vue/Angular SPA,首頁 HTML 裡沒有真正的活動內容),但用瀏覽器開發工具觀察頁面載入時發出的網路請求後,發現兩者其實都有公開、不需要認證的 JSON API,可以直接用 `requests` 呼叫取得完整的活動清單,不需要 Playwright 或任何瀏覽器渲染。

## What Changes

- 新增 `src/scrapers/ticketplus.py`:呼叫 `apis.ticketplus.com.tw/config/api/v1/getS3?path=main/mainEvents.json` 取得遠大售票的活動清單
- 新增 `src/scrapers/ibon.py`:呼叫 `ticket.ibon.com.tw/api/ActivityInfo/GetIndexData?pattern=entertainment` 取得 7-ELEVEN ibon 的活動清單
- 把這兩個新 scraper 加進 `src/scrapers/__init__.py` 的 `SCRAPERS` 清單
- 不新增任何依賴套件、不修改 GitHub Actions workflow(跟之前推測的「需要 Playwright」不同,這兩個來源實際上不需要)

## Capabilities

### New Capabilities
(無)

### Modified Capabilities
- `concert-source-scraping`: 新增遠大售票(Ticket Plus)與 7-ELEVEN ibon 這兩個售票平台來源的抓取需求,沿用既有的「統一資料格式」與「單一來源失敗不影響其他來源」規則

## Impact

- 新增兩個新的售票平台的 HTTP 請求行為(呼叫 JSON API,而非爬 HTML)
- 不影響現有五個 scraper(tixCraft、年代售票、udn、寬宏藝術、KKTIX)與其他邏輯
- 風險:這些是對方前端實際呼叫的內部 API,沒有公開文件,未來可能改版或要求額外認證;已有的「單一來源失敗不影響其他來源」機制會讓這個風險只影響這兩個來源各自
