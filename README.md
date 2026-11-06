# concert-reminder

追蹤喜歡的樂團/藝人,只要在台灣售票平台(目前支援 tixCraft 拓元)上架新場次,就透過 Discord 收到通知。

## 設定要追蹤的藝人

編輯 `config.yaml`,每個藝人填 `name`(顯示用)與 `keywords`(比對活動標題用的關鍵字,可填中文名、英文名等多個別名):

```yaml
artists:
  - name: "告五人"
    keywords: ["告五人"]
  - name: "Taylor Swift"
    keywords: ["Taylor Swift", "泰勒絲"]
```

## 本機執行

1. 建立虛擬環境並安裝套件:
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate   # Windows Git Bash;PowerShell 用 .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. 複製 `.env.example` 成 `.env`,填入你的 Discord Webhook URL(在 Discord 頻道設定 → 整合 → Webhook 建立)。
3. 執行:
   ```bash
   python -m src.main
   ```
   第一次執行會抓取目前 tixCraft 上架的活動並比對 `config.yaml` 中的藝人,符合的會發 Discord 通知,並記錄在 `data/seen_events.json`。之後重複執行只會通知「新出現」的場次。

## 部署到 GitHub Actions(定期自動檢查)

1. 建立 GitHub repo 並 push 這個專案。
2. 到 repo 的 Settings → Secrets and variables → Actions,新增 secret `DISCORD_WEBHOOK_URL`。
3. `.github/workflows/check_concerts.yml` 預設每 30 分鐘自動執行一次,也可以到 Actions 頁面手動觸發(`workflow_dispatch`)測試。
4. 每次執行後,若有新通知,`data/seen_events.json` 會被自動 commit 回 repo,用來記住哪些場次已經通知過,避免重複通知。

## 新增其他售票平台

在 `src/scrapers/` 下新增一個模組,實作一個回傳 `list[Event]`(見 `src/scrapers/base.py`)的函式,再把它加進 `src/scrapers/__init__.py` 的 `SCRAPERS` 清單即可,不用改動比對/通知邏輯。
