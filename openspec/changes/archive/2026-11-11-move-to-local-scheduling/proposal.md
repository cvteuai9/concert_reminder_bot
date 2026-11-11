## Why

tixCraft、KKTIX、遠大售票 Ticket Plus 這三個平台的防護機制會擋掉 GitHub Actions 虛擬機的雲端 IP,但使用者家中網路的一般住宅 IP 不會被擋。使用者的電腦大部分時間都是開著的,且這個程式本身執行一次只要幾秒鐘、幾乎不耗資源,因此決定把排程執行的位置從 GitHub Actions 完全改成使用者本機,用 Windows 的工作排程器定期執行,讓全部 7 個平台都用家用 IP 發請求,不再有任何平台因為 IP 被擋而抓不到資料。

## What Changes

- 新增一個本機排程用的啟動腳本(PowerShell),負責讀取 `.env` 的 `DISCORD_WEBHOOK_URL`、啟動虛擬環境、執行 `python -m src.main`
- 在使用者的 Windows 工作排程器註冊一個排程工作,定期(預設每小時)自動執行上述腳本
- 移除 GitHub Actions workflow 的 `schedule` 自動觸發(保留 `workflow_dispatch` 作為手動測試用途,不再是正式的執行路徑),避免本機與雲端同時執行造成重複通知或狀態衝突
- `data/seen_events.json`、`data/source_health.json` 改為純本機檔案,不再需要 CI 的「commit 回 repo」機制來跨執行持久化(因為本機本身就是持久的執行環境),改為加入 `.gitignore`、從 git 版本控制中移除追蹤(保留本機磁碟上的檔案內容不變)

## Capabilities

### New Capabilities
(無)

### Modified Capabilities
- `scheduled-check-run`: 「定期自動執行」的機制從 GitHub Actions 排程改為 Windows 工作排程器,需要使用者電腦在排定時間點是開機連網的狀態(不再是「不管電腦開不開都會跑」);「狀態可跨執行持久化」改為依賴本機磁碟的持久性,不再需要跨環境的持久化機制(例如 CI commit 回 repo)

## Impact

- 新增本機啟動腳本與 Windows 工作排程器設定(屬於使用者機器上的設定,不是程式碼範疇,但腳本本身會進 repo)
- 修改 `.github/workflows/check_concerts.yml`,移除自動排程觸發
- `data/*.json` 從 git 追蹤移除(改進 `.gitignore`),現有的 `seen_events.json`、`source_health.json` 內容保留在本機磁碟,不受影響
- 不影響 `src/` 底下的任何程式邏輯(scraper、比對、通知、健康告警都不用改,因為它們本來就只是讀寫本機檔案,跟「這個本機是不是持久環境」無關)
