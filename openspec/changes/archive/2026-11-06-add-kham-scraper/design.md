## Context

延續 `add-static-scraper-sources` change 的模式(`src/scrapers/ticket_com_tw.py`、`src/scrapers/udn.py`)。寬宏藝術首頁(`https://kham.com.tw/`)請求後會 302 轉址到實際首頁(目前是 `.../application/utk01/UTK0101_03.aspx`),內容是靜態 HTML。活動卡片的結構是:

```html
<a href='../UTK02/UTK0201_.aspx?PRODUCT_ID=P1GSEUSW'>
  <img src='...' alt='' onerror="...">
  <p>KPOP PLANET in TAIPEI</p>
</a>
```

即 `<a href 含 PRODUCT_ID>` 內有一個 `<p>` 標籤是標題文字,沒有日期/場地資訊(這個區塊純粹是圖+標題的卡片)。這批卡片的 href 是**相對路徑**(`../UTK02/...`),跟 tixCraft/年代售票/udn 的絕對網址不同,需要用 `urllib.parse.urljoin` 搭配實際回應的 URL(考慮到前面已經發生過 302 轉址)來還原成完整網址。

首頁上還有其他含 `PRODUCT_ID` 的連結(輪播廣告圖、頂部彈跳視窗),但這些連結旁邊沒有可靠的標題文字(`alt=''` 是空的),所以只解析「`<a>` 內有 `<p>` 標籤」這種卡片,不嘗試從其他區塊撈資料。

## Goals / Non-Goals

**Goals:**
- 用與年代售票、udn 相同的 `requests + BeautifulSoup` 模式新增寬宏藝術
- 不新增依賴、不改 CI

**Non-Goals:**
- 不處理首頁上沒有標題文字的輪播廣告連結(資料不足,寧可少抓不要抓到空標題)
- 不處理日期/場地(這個版面沒有提供),`Event.date`、`Event.venue` 維持 `None`

## Decisions

### 只解析 `a[href*='PRODUCT_ID='] > p` 這種有標題的卡片
首頁其他含 `PRODUCT_ID` 的連結(banner、彈跳視窗)都沒有可靠的標題文字,硬解析只會拿到空字串或圖片 alt 文字(品質不穩定)。只抓有清楚 `<p>` 標題的卡片區塊,符合既有「統一資料格式」規則裡「缺少的欄位用空值表示」但「標題不可為空」的精神(呼應 base scraper 的作法:沒有標題就跳過該筆)。

### 用 `urljoin` 處理相對連結
寬宏藝術這批卡片的 href 是相對路徑,且頁面本身是從 `kham.com.tw/` 302 轉址過去的,直接用字串拼接網域容易出錯(不知道轉址後的實際路徑深度)。改用 `urllib.parse.urljoin(response.url, href)`,用 `requests` 回應物件的 `response.url`(轉址後的最終網址)當作 base,交給標準函式庫處理相對路徑運算,比自己手刻字串處理可靠。

## Risks / Trade-offs

- **[風險] 首頁版面調整可能讓「有 `<p>` 標題」這個卡片區塊消失或改名。** → 緩解方式:沿用既有的錯誤隔離模式,失敗時回傳空清單、記錄警告,不影響其他來源;之後改版只需要修 `kham.py` 的選擇器。

## Open Questions

(無)
