## Context

KKTIX 活動探索頁(`kktix.com/events`)的活動資料本身是靜態內嵌的 JSON(`data-react-class="SearchWrapper"` 的 `data-react-props` 屬性),跟原本規劃的一樣容易解析。問題不在資料格式,而在於請求本身:這個網域前面有 Cloudflare 的機器人偵測,會依照 HTTP client 的 TLS/HTTP 指紋判斷是否為自動化流量。實測結果:

- 用 `curl`(含瀏覽器風格的 User-Agent)請求 → 200,拿到真實內容
- 用 Python `requests`(即使帶上完整的瀏覽器 header)→ 403,回應是 Cloudflare 的「Just a moment...」JS 挑戰頁(`server: cloudflare`)
- 用 `curl_cffi`(`impersonate="chrome"`)→ 200,拿到真實內容(連續測試 3 次皆成功)

這說明 Cloudflare 的判斷依據是 TLS handshake 層級的指紋(例如 JA3),不是單純看 header。`curl_cffi` 底層用 BoringSSL 重現真實 Chrome 的 TLS 行為,因此能通過這層檢查。

## Goals / Non-Goals

**Goals:**
- 讓 KKTIX scraper 能穩定取得真實活動資料,不被 Cloudflare 擋下
- 把新依賴限制在最小範圍:只有 `kktix.py` 用 `curl_cffi`,其他 scraper 不受影響
- 沿用既有的「統一資料格式」與「單一來源失敗不影響其他來源」規則

**Non-Goals:**
- 不保證長期有效——Cloudflare 的偵測規則會持續演進,`curl_cffi` 的 impersonate 設定也需要跟著更新版本維護;這不是一次性解決的問題,而是這個來源長期要承擔的維護成本
- 不引入完整的 headless browser(Playwright)——這個規模的反偵測用 `curl_cffi` 就足夠,沒必要為了一個靜態資料的平台付出瀏覽器啟動的效能成本

## Decisions

### 用 `curl_cffi` 取代 `requests`,只用在 KKTIX 這個 scraper
`curl_cffi` 的 API 設計上跟 `requests`幾乎一樣(`curl_cffi.requests.get(...)`),只是多一個 `impersonate` 參數指定要模擬的瀏覽器版本,替換成本很低。只在 `kktix.py` 裡面用,不去動其他四個 scraper 的 `requests` 用法——它們沒有被擋,沒有理由承擔額外依賴的風險。

已考慮過的替代方案:
- **Playwright**:能處理任何反偵測情境(包含真正執行 JS 的挑戰),但對 KKTIX 這種「資料本身是靜態 JSON、只是連線層被擋」的情況太重,CI 時間與維護成本都高出一截
- **放棄 KKTIX**:最簡單,但使用者明確想要這個來源,且 `curl_cffi` 的驗證結果顯示成本可控

### 解析邏輯沿用原本規劃的 `data-react-props` JSON 解法
抓到頁面後的解析邏輯(找到 `data-react-props` 屬性、`html.unescape()`、`json.loads()`、轉成 `Event` 清單)跟最初在 `add-static-scraper-sources` change 設計時規劃的一樣,這部分沒有因為改用 `curl_cffi` 而改變。

## Risks / Trade-offs

- **[風險] Cloudflare 之後可能調整偵測規則,讓 `curl_cffi` 目前的 impersonate 設定失效。** → 緩解方式:錯誤隔離機制讓這個來源失效時只影響 KKTIX,不影響其他四個來源;屆時需要升級 `curl_cffi` 版本或調整 `impersonate` 參數,是純粹的維護工作,不需要改架構。
- **[風險] `curl_cffi` 是一個相對新的第三方套件,比 `requests` 的生態成熟度低。** → 緩解方式:只在這一個 scraper 使用,出問題的影響範圍是可控的;且目前（2026年）這個套件已有穩定的 release 歷史與廣泛使用於反偵測爬蟲場景。

## Open Questions

(無)
