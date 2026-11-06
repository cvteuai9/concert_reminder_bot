## Why

使用者想追蹤喜歡的樂團/藝人,只要在台灣開演唱會售票資訊上架,就能即時收到通知,不用自己每天手動查各個售票網站。LINE Notify 已於 2025/4/1 停止服務,改用 Messaging API 需要申請官方帳號且有訊息額度限制,因此選擇 Discord Webhook 作為通知管道,搭配 GitHub Actions 排程,不需要使用者自己開機或維護伺服器。

## What Changes

- 新增一個 Python 專案,定期(預設每 30 分鐘)爬取台灣售票平台的活動列表,比對使用者在設定檔中列出的追蹤藝人/樂團,有新場次就發 Discord 通知
- 新增可插拔的 scraper 架構,v1 先實作 tixCraft 拓元售票(確認為靜態 HTML,可直接爬取),之後可依相同介面擴充 ibon、寬宏等平台,不用改動比對/通知邏輯
- 新增以藝人關鍵字(含別名)比對活動標題的邏輯
- 新增 Discord Webhook 通知邏輯,訊息包含藝人、標題、場地、日期、售票連結
- 新增已通知活動的去重狀態紀錄,避免同一場次重複通知
- 新增 GitHub Actions 排程 workflow,定期執行檢查並把去重狀態 commit 回 repo

## Capabilities

### New Capabilities
- `concert-source-scraping`: 從台灣售票平台抓取演唱會活動列表的能力,以可插拔的方式支援多個來源,v1 實作 tixCraft
- `artist-watch-matching`: 依使用者設定的追蹤藝人清單(含別名關鍵字),比對抓到的活動標題,找出相符的活動
- `discord-alerting`: 將新符合的活動透過 Discord Webhook 發送通知,並避免同一活動被重複通知
- `scheduled-check-run`: 串接抓取、比對、通知、狀態存檔的整體執行流程,並透過 GitHub Actions 定期排程自動執行

### Modified Capabilities
(無,這是全新專案)

## Impact

- 新增全新的 Python 專案程式碼(目前 repo 中沒有任何應用程式碼)
- 新增對外部網站(tixCraft)的 HTTP 請求行為,需注意請求頻率與 User-Agent,避免造成對方網站負擔
- 新增 GitHub Actions workflow,需要使用者在 GitHub repo 設定 Secret `DISCORD_WEBHOOK_URL`,並給予 workflow `contents: write` 權限以便 commit 回去重狀態檔
- 不影響任何既有系統(本次為全新建置)
