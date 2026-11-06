## 2. 年代售票 scraper(對應 spec: concert-source-scraping)

- [x] 2.1 實作 `src/scrapers/ticket_com_tw.py`:對年代售票首頁發出 GET 請求,解析 `.portfolio-item a.portfolio-link` 與 `.wrap a[href*=PRODUCT_ID]` 兩種卡片區塊,依 `PRODUCT_ID` 去重後轉成 `Event` 清單,並驗證對真實網站執行時能抓到多筆活動
- [x] 2.2 為 `ticket_com_tw.py` 加上 try/except,失敗時記錄錯誤並回傳空清單,並驗證刻意傳入錯誤網址時不會拋出未處理例外

## 3. udn售票網 scraper(對應 spec: concert-source-scraping)

- [x] 3.1 實作 `src/scrapers/udn.py`:對 udn售票網首頁發出 GET 請求,解析 `.yd_card` 卡片區塊(標題、連結、日期、場地),轉成 `Event` 清單,並驗證對真實網站執行時能抓到多筆活動
- [x] 3.2 為 `udn.py` 加上 try/except,失敗時記錄錯誤並回傳空清單,並驗證刻意傳入錯誤網址時不會拋出未處理例外

## 4. 整合與驗證

- [x] 4.1 把兩個新 scraper 加進 `src/scrapers/__init__.py` 的 `SCRAPERS` 清單,並驗證從外部呼叫每個 scraper 都能拿到 `Event` 清單
- [x] 4.2 本機執行 `python -m src.main`(用測試用 webhook),驗證三個來源(tixCraft + 兩個新來源)都有被呼叫、抓到的活動數量加總合理,且比對/通知/去重邏輯對新來源的活動一樣正常運作
