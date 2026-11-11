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

## 部署:本機排程(目前的做法)

tixCraft、KKTIX、遠大售票(Ticket Plus)這三個平台的防護機制會擋掉 GitHub Actions 虛擬機的雲端 IP,但家用網路的 IP 不會被擋,所以排程改成在本機用 Windows 工作排程器執行,不再依賴 GitHub Actions 的 `schedule`(`.github/workflows/check_concerts.yml` 現在只保留 `workflow_dispatch`,當作需要時的手動雲端測試工具,不會自動執行)。

1. 確保 `.venv` 已建立、套件已安裝(見上方「本機執行」),且 `.env` 已填好 `DISCORD_WEBHOOK_URL`。
2. 用 PowerShell 註冊排程工作(已經幫你註冊好一次,目前設定是每天台灣時間凌晨 5 點執行一次;之後要重建可以用這段):
   ```powershell
   $ScriptPath = "C:\Users\cvtey\concert_reminder\run_check.ps1"
   $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
   $trigger = New-ScheduledTaskTrigger -Daily -At "5:00AM"
   $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
   Register-ScheduledTask -TaskName "ConcertReminderCheck" -Action $action -Trigger $trigger -Settings $settings -Description "Run concert_reminder's daily check (src/main.py) locally"
   ```
   想改成其他頻率(例如每小時),只要換成 `New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650)` 再用 `Set-ScheduledTask -TaskName "ConcertReminderCheck" -Trigger $trigger` 更新既有工作,不用整個刪掉重建。
3. 查詢狀態、手動觸發一次測試、或移除排程:
   ```powershell
   Get-ScheduledTask -TaskName "ConcertReminderCheck"
   Get-ScheduledTaskInfo -TaskName "ConcertReminderCheck"   # 看上次執行結果、下次執行時間
   Start-ScheduledTask -TaskName "ConcertReminderCheck"      # 手動觸發一次
   Unregister-ScheduledTask -TaskName "ConcertReminderCheck" -Confirm:$false   # 移除排程
   ```
4. 每次執行(排程或手動觸發)的輸出都會附加寫入 `logs/run.log`,可以打開這個檔案看最近幾次有沒有抓到活動、有沒有發通知、有沒有平台健康告警。
5. `data/seen_events.json`、`data/source_health.json` 現在是純本機檔案(已加進 `.gitignore`,不再進 git),同一台機器重複執行會自動讀到上次留下的狀態。

**前提**:排定的時間點電腦要是開機、連網的狀態才會執行(已設定 `WakeToRun`,電腦若是睡眠會嘗試喚醒,但關機或登出不會);如果電腦當時沒開,那次就會跳過,等電腦恢復上線或等到下一天凌晨 5 點再執行,不會補發錯過的通知。

## 平台失敗告警

每個 scraper 都會把請求/解析錯誤包在 try/except 裡,單一平台失敗不會讓整個流程中斷,但也代表它會悄悄回傳空清單。系統會記錄每個平台「連續幾次沒抓到任何活動」(`data/source_health.json`),達到 `config.yaml` 設定的門檻(目前設為 2 次)就會發一則 Discord 告警,提醒你該平台可能需要檢查。同一輪失效只會告警一次,等該平台恢復抓到資料後,下次再失效才會重新觸發。**注意**:排程是每天一次,所以「連續 2 次」代表連續 2 天都抓不到,從出問題到收到告警大約會晚 1-2 天。

## 新增其他售票平台

在 `src/scrapers/` 下新增一個模組(含 `SOURCE` 常數與 `fetch_events()` 函式,回傳 `list[Event]`,見 `src/scrapers/base.py`),再把它加進 `src/scrapers/__init__.py` 的 `SCRAPERS` 清單即可,不用改動比對/通知/健康告警邏輯。
