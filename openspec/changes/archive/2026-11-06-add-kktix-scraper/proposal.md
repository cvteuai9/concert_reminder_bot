## Why

使用者想追蹤的藝人也可能在 KKTIX 售票。KKTIX 的活動探索頁(`kktix.com/events`)背後有 Cloudflare 機器人偵測,用一般的 `requests` 發請求會被導向驗證頁(403,Cloudflare「Just a moment...」挑戰頁),這是在 `add-static-scraper-sources` change 實作時發現的,因此當時把 KKTIX 移出那批。經過驗證,`curl_cffi`(一個模擬真實瀏覽器 TLS 指紋的輕量套件,底層用 BoringSSL 重現 Chrome 的 TLS handshake,讓 Cloudflare 的偵測規則判斷為正常瀏覽器流量)可以穩定繞過這層防護(連續測試 3 次都成功拿到含真實活動資料的回應),不需要上完整的 headless browser。

## What Changes

- 新增依賴 `curl_cffi`,只用在 KKTIX 這個來源(其他來源仍用原本的 `requests`)
- 新增 `src/scrapers/kktix.py`:用 `curl_cffi` 模擬 Chrome 向 `kktix.com/events` 發請求,解析頁面中內嵌的 `data-react-props` JSON 屬性取得活動清單
- 把新 scraper 加進 `src/scrapers/__init__.py` 的 `SCRAPERS` 清單
- 更新 `requirements.txt` 加入 `curl_cffi`;不需要修改 GitHub Actions workflow(`curl_cffi` 是純 pip 套件,不需要像 Playwright 一樣額外安裝瀏覽器執行檔)

## Capabilities

### New Capabilities
(無)

### Modified Capabilities
- `concert-source-scraping`: 新增 KKTIX 這個售票平台來源的抓取需求,沿用既有的「統一資料格式」與「單一來源失敗不影響其他來源」規則

## Impact

- 新增一個新的依賴套件 `curl_cffi`(僅 KKTIX scraper 使用)
- 新增對 KKTIX 的 HTTP 請求行為
- 不影響現有四個 scraper(tixCraft、年代售票、udn、寬宏藝術)與其他邏輯
- 風險:Cloudflare 的偵測規則可能隨時調整,屆時 `curl_cffi` 的繞過方式可能失效;已有的「單一來源失敗不影響其他來源」機制會讓這個風險只影響 KKTIX 這一個來源
