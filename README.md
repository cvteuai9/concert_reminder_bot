# concert-reminder

追蹤喜歡的樂團/藝人,只要在台灣售票平台上架新場次,就透過 Discord 收到通知。

目前支援的售票平台:tixCraft 拓元、年代售票(Ticket.com.tw)、udn售票網、寬宏藝術、KKTIX、遠大售票(Ticket Plus)、7-ELEVEN ibon。

## 設定要追蹤的藝人

編輯 `config.yaml`,每個藝人填 `name`(顯示用)與 `keywords`(比對活動標題用的關鍵字,可填中文名、英文名等多個別名):

```yaml
artists:
  - name: "動力火車"
    keywords: ["動力火車"]

monitoring:
  consecutive_empty_threshold: 3  # 某平台連續幾次抓不到活動才告警,見「平台失敗告警」
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
   第一次執行會抓取各平台目前上架的活動並比對 `config.yaml` 中的藝人,符合的會發 Discord 通知,並記錄在 `data/seen_events.json`。之後重複執行只會通知「新出現」的場次。

## 部署到 GitHub Actions(定期自動檢查)

1. 建立 GitHub repo 並 push 這個專案。
2. 到 repo 的 Settings → Secrets and variables → Actions,新增 secret `DISCORD_WEBHOOK_URL`。
3. `.github/workflows/check_concerts.yml` 預設每小時自動執行一次(GitHub Actions 對分鐘等級的排程不保證準時,甚至可能跳過,每小時比較符合實際行為),也可以到 Actions 頁面手動觸發(`workflow_dispatch`)測試。
4. 每次執行後,`data/seen_events.json`(已通知的活動)與 `data/source_health.json`(各平台健康狀態,見下方)都會被自動 commit 回 repo,用來跨執行保留狀態。

## 平台失敗告警

每個 scraper 都會把請求/解析錯誤包在 try/except 裡,單一平台失敗不會讓整個流程中斷,但也代表它會悄悄回傳空清單。系統會記錄每個平台「連續幾次沒抓到任何活動」(`data/source_health.json`),達到 `config.yaml` 設定的門檻(預設 3 次)就會發一則 Discord 告警,提醒你該平台可能需要檢查。同一輪失效只會告警一次,等該平台恢復抓到資料後,下次再失效才會重新觸發。

**已知限制:tixCraft、KKTIX、遠大售票(Ticket Plus)在 GitHub Actions 上可能持續收到 403**
這三個平台的防護機制(WAF/Cloudflare)會擋掉 GitHub Actions 虛擬機的 IP 範圍——這在本機或一般網路環境是正常的,只有在 GitHub 的雲端執行環境才會被擋。這不是程式碼壞掉或網站改版,單純改爬蟲邏輯無法解決,因為問題在於請求從哪個 IP 發出,不在請求內容本身。目前的取捨是接受這個限制、不引入付費 proxy 或自架伺服器,所以這三個平台在 GitHub Actions 上會持續觸發一次告警後維持「已告警」狀態,不會再重複通知,但也不會真的抓到新場次——這幾個平台的新場次目前只能靠你自己額外查看。另外 4 個平台(年代售票、udn售票網、寬宏藝術、7-ELEVEN ibon)運作正常。

## 新增其他售票平台

在 `src/scrapers/` 下新增一個模組(含 `SOURCE` 常數與 `fetch_events()` 函式,回傳 `list[Event]`,見 `src/scrapers/base.py`),再把它加進 `src/scrapers/__init__.py` 的 `SCRAPERS` 清單即可,不用改動比對/通知/健康告警邏輯。
