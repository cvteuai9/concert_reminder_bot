## 1. 寬宏藝術 scraper(對應 spec: concert-source-scraping)

- [x] 1.1 實作 `src/scrapers/kham.py`:對寬宏藝術首頁發出 GET 請求,解析 `a[href*='PRODUCT_ID='] p` 卡片區塊取得標題,用 `urljoin(response.url, href)` 還原完整連結,轉成 `Event` 清單,並驗證對真實網站執行時能抓到多筆活動
- [x] 1.2 為 `kham.py` 加上 try/except,失敗時記錄錯誤並回傳空清單,並驗證刻意傳入錯誤網址時不會拋出未處理例外

## 2. 整合與驗證

- [x] 2.1 把 `kham.py` 加進 `src/scrapers/__init__.py` 的 `SCRAPERS` 清單,並驗證從外部呼叫能拿到 `Event` 清單
- [x] 2.2 本機執行 `python -m src.main`(用測試用 webhook),驗證四個來源都有被呼叫、比對/通知/去重邏輯對寬宏藝術的活動一樣正常運作
