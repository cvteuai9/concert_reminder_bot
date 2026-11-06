## Context

現有架構(見 `concert-reminder` change 的 design.md)已經把「每個售票平台一個 scraper 檔案,回傳統一的 `Event` 清單」這個模式建立起來了(`src/scrapers/tixcraft.py` + `src/scrapers/base.py`)。這次只是依照同樣的模式新增兩個來源。針對這兩個平台實際抓取測試後,發現的具體頁面結構如下:

- **年代售票 Ticket.com.tw**(`ticket.com.tw`):請求首頁相關路徑會先 302 轉址到實際首頁,內容為靜態 HTML,活動資訊分散在兩種卡片區塊:`.portfolio-item a.portfolio-link`(內含 `h4` 標題、`p.text-muted` 日期文字)與 `.wrap a[href*=PRODUCT_ID]`(內含 `h3` 標題、同層 `p` 的開賣時間文字)。
- **udn售票網**(`tickets.udnfunlife.com`):同樣會 302 轉址到實際首頁,活動卡片的 class 是 `.yd_card`,內含 `.yd_card-title`(標題)、兩個 `.yd_card-iconText`(依序為日期、場地)。

這兩個平台背後圖片 CDN 網域都是 `imgs2.utiki.com.tw`,推測是同一套票務系統(UTK/UTIKI)的不同品牌前端,但前端樣板不同,所以仍各寫一個獨立的 scraper 檔案,不共用解析邏輯。

**關於 KKTIX**:原本規劃這次一起做,但實際發起請求時發現 `kktix.com/events` 有 Cloudflare 機器人偵測——用 `requests` 發請求會被導向 Cloudflare 的 JS 驗證頁(回應 403,`server: cloudflare`,內容是「Just a moment...」挑戰頁)。這跟先前用 `curl` 測試時沒有被擋不一致,推測是 Cloudflare 的 bot 偵測機制會依 TLS/HTTP client 的指紋(JA3 等)區分 `curl` 與 Python `requests`/`urllib3`,`curl` 的指紋沒有被規則命中,但 `requests` 的有。這代表 KKTIX 無法沿用「單純 `requests` 拿 HTML」的作法,需要額外的反偵測手段(例如可以模擬瀏覽器 TLS 指紋的 `curl_cffi`、或完整的 headless browser),因此移到下一個處理「需要特殊處理的平台」的 change,和寬宏藝術、遠大售票 Ticket Plus、7-ELEVEN ibon 一起評估。

## Goals / Non-Goals

**Goals:**
- 用與 tixCraft 相同的「`requests` 拿 HTML → `BeautifulSoup` 解析 → 回傳統一 `Event` 清單」模式,新增這兩個來源
- 不改動 `main.py`、`matcher.py`、`notifier.py`、`state.py`、GitHub Actions workflow
- 不新增任何依賴套件

**Non-Goals:**
- 不處理需要瀏覽器渲染或反機器人偵測的平台(KKTIX、寬宏藝術、遠大售票 Ticket Plus、7-ELEVEN ibon、OPENTIX),這些留給下一個 change
- 不嘗試把兩個新 scraper 的解析邏輯抽成共用的「UTK 系統」基底類別——前端樣板不同,抽象化的收益不足以抵過增加的間接層,等之後有第三個同系統平台時再評估

## Decisions

### 年代售票與 udn:各自解析兩種卡片區塊,以 PRODUCT_ID 當作活動 ID 去重
年代售票首頁有兩種呈現同類型活動的卡片區塊(本月熱門 `portfolio-item` 與即將開賣輪播 `wrap`),為了不漏抓,兩種都解析,再用 URL 中的 `PRODUCT_ID` 做去重(同一個 `Event` 字典,後出現的覆蓋先出現的即可,邏輯跟 tixCraft scraper 一致)。udn售票網的卡片結構單一(`.yd_card`),只需一種選擇器。

### 沿用既有的錯誤隔離模式
兩個新 scraper 都遵循 `concert-source-scraping` spec 既有的「單一來源失敗不影響其他來源」需求:對外請求與解析都包在 try/except 裡,失敗時記錄 warning 並回傳空清單,不拋出例外。

## Risks / Trade-offs

- **[風險] 年代售票與 udn售票網的首頁版面經常有行銷性的輪播/熱門區塊異動,比 tixCraft 的活動列表頁更容易改版。** → 緩解方式:兩種卡片區塊都解析以提高覆蓋率,且錯誤隔離機制確保單一平台改版只會讓該平台暫時抓不到東西,不影響其他來源;日後改版可以直接修對應的 scraper 檔案。
- **[風險] KKTIX 的 Cloudflare 偵測未來可能也套用到其他平台,或現有平台(tixCraft、年代售票、udn)之後也加上類似機制。** → 緩解方式:錯誤隔離機制會讓被擋的來源回傳空清單而不是讓整個流程掛掉,屆時只需要針對該來源評估要不要導入 `curl_cffi` 或 headless browser,不影響其他來源的運作。

## Open Questions

(無)
