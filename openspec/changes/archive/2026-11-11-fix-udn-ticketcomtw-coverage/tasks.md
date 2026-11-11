## 1. 修正 udn 覆蓋率(對應 spec: concert-source-scraping)

- [x] 1.1 修改 `src/scrapers/udn.py`:標題選擇器改成「`.yd_card-title` 優先、沒有則用 `.yd_card-text`」,連結改成同時接受 `PRODUCT_ID=` 或 `AGId=` 兩種參數抓取活動 ID,並驗證對真實網站執行時能抓到首頁三個頁籤合計的卡片數(約 35 筆,扣除重複與無效卡片後的實際數量)
- [x] 1.2 驗證修正後的結果仍然沒有重複(同一活動 ID 不會出現兩次),且原本「推薦節目」頁籤抓到的 12 筆活動,其日期/場地資訊跟修正前一致(確認沒有改壞原本能用的部分)

## 2. 修正年代售票改用節目總表頁面(對應 spec: concert-source-scraping)

- [x] 2.1 修改 `src/scrapers/ticket_com_tw.py`:改抓 `UTK0101_06.aspx?TYPE=1&CATEGORY=205`,解析 `div.moreBox` 卡片(`.list-group-item-heading` 標題、`.list-group-item-date` 日期),移除原本解析首頁兩個輪播部件的邏輯,並驗證對真實網站執行時能抓到完整的演唱會清單且標題乾淨無空值
- [x] 2.2 驗證錯誤隔離模式仍然有效:刻意傳入錯誤網址時不會拋出未處理例外,回傳空清單

## 3. 整合驗證

- [x] 3.1 本機執行 `python -m src.main`,驗證七個來源都正常運作,udn 跟年代售票抓到的活動數量比修正前明顯增加,且比對/通知/去重邏輯對新抓到的活動一樣正常運作
