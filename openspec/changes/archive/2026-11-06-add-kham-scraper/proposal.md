## Why

使用者想追蹤的藝人也可能在寬宏藝術售票。第一次技術調查時誤測了會動態載入分類的頁面,得出「需要瀏覽器渲染」的錯誤結論;重新測試寬宏藝術首頁(`kham.com.tw/`)後確認實際轉址到的頁面是靜態 HTML,活動資訊(含標題、連結)直接存在於頁面中,跟年代售票、udn售票網背後是同一套票務系統(圖片 CDN 同為 `imgs2.utiki.com.tw`)。因此可以用跟前兩個平台一樣的 `requests + BeautifulSoup` 方式新增,不需要新增依賴或改動 CI。

## What Changes

- 新增 `src/scrapers/kham.py`:從寬宏藝術首頁的活動列表區塊解析活動清單(標題、連結)
- 把新 scraper 加進 `src/scrapers/__init__.py` 的 `SCRAPERS` 清單
- 不新增任何依賴套件、不修改 GitHub Actions workflow

## Capabilities

### New Capabilities
(無)

### Modified Capabilities
- `concert-source-scraping`: 新增寬宏藝術這個售票平台來源的抓取需求,沿用既有的「統一資料格式」與「單一來源失敗不影響其他來源」規則

## Impact

- 新增一個新的售票平台的 HTTP 請求行為,同樣需注意請求頻率與 User-Agent
- 不影響現有的 tixCraft、年代售票、udn 三個 scraper,也不影響比對/通知/排程邏輯
