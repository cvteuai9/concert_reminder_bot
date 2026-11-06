## 1. 遠大售票(Ticket Plus)scraper(對應 spec: concert-source-scraping)

- [x] 1.1 實作 `src/scrapers/ticketplus.py`:呼叫 `apis.ticketplus.com.tw/config/api/v1/getS3?path=main/mainEvents.json`,解析 `allEventMainPageInfo`,過濾 `hidden=true` 的項目,轉成 `Event` 清單(url 組成 `https://ticketplus.com.tw/activity/{id}`),並驗證對真實 API 執行時能抓到多筆活動
- [x] 1.2 為 `ticketplus.py` 加上 try/except,失敗時記錄錯誤並回傳空清單,並驗證刻意傳入錯誤網址時不會拋出未處理例外

## 2. 7-ELEVEN ibon scraper(對應 spec: concert-source-scraping)

- [x] 2.1 實作 `src/scrapers/ibon.py`:呼叫 `ticket.ibon.com.tw/api/ActivityInfo/GetIndexData?pattern=entertainment`,解析 `Item.List`,標題做 `strip()`,用 `urljoin` 補完 `GameTicketURL` 的相對路徑,轉成 `Event` 清單,並驗證對真實 API 執行時能抓到多筆活動
- [x] 2.2 為 `ibon.py` 加上 try/except,失敗時記錄錯誤並回傳空清單,並驗證刻意傳入錯誤網址時不會拋出未處理例外

## 3. 整合與驗證

- [x] 3.1 把兩個新 scraper 加進 `src/scrapers/__init__.py` 的 `SCRAPERS` 清單,並驗證從外部呼叫每個 scraper 都能拿到 `Event` 清單
- [x] 3.2 本機執行 `python -m src.main`(用測試用 webhook),驗證七個來源都有被呼叫、比對/通知/去重邏輯對這兩個新來源的活動一樣正常運作
