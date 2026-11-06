## 1. 依賴與 KKTIX scraper(對應 spec: concert-source-scraping)

- [x] 1.1 把 `curl_cffi` 加進 `requirements.txt`,並驗證 `pip install -r requirements.txt` 成功
- [x] 1.2 實作 `src/scrapers/kktix.py`:用 `curl_cffi.requests.get(..., impersonate="chrome")` 向 `kktix.com/events` 發請求,解析 `data-react-props` JSON 屬性取得活動清單(id、title、url 來自 JSON,date 由 `start_at` 轉換,venue 為 `None`),並驗證對真實網站執行時能抓到多筆活動且不是 Cloudflare 挑戰頁
- [x] 1.3 為 `kktix.py` 加上 try/except(涵蓋請求失敗與 JSON 解析失敗兩種情況),失敗時記錄錯誤並回傳空清單,並驗證刻意破壞解析邏輯或傳入錯誤網址時不會拋出未處理例外

## 2. 整合與驗證

- [x] 2.1 把 `kktix.py` 加進 `src/scrapers/__init__.py` 的 `SCRAPERS` 清單,並驗證從外部呼叫能拿到 `Event` 清單
- [x] 2.2 本機執行 `python -m src.main`(用測試用 webhook),驗證五個來源都有被呼叫、比對/通知/去重邏輯對 KKTIX 的活動一樣正常運作
