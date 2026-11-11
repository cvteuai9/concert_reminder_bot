## Context

使用者的 Windows 10 電腦大部分時間是開著的。原本的架構(GitHub Actions)是為了「不需要電腦開著」而設計,但代價是 tixCraft/KKTIX/Ticket Plus 這三個平台擋 GitHub 的雲端 IP(見 [[github_actions_ip_block]] 相關討論)。既然使用者接受「電腦要在排定時間點開著」這個前提,改到本機執行可以一次解決全部 7 個平台的 IP 問題,且這個程式執行一次只要幾秒鐘、資源消耗極低,排程成每小時跑一次對電腦沒有負擔。

專案已經有 `.venv`(虛擬環境)、`.env`(本機測試用的 `DISCORD_WEBHOOK_URL`)、`requirements.txt`,這些都可以直接沿用,不需要重新建置。

## Goals / Non-Goals

**Goals:**
- 用 Windows 工作排程器取代 GitHub Actions 的 `schedule` 觸發,排程本身的執行邏輯(`src/main.py`)完全不用改
- 讓 `DISCORD_WEBHOOK_URL` 這個機密只在腳本執行期間存在於那個行程的環境變數,不寫進 Windows 全域的使用者環境變數(避免機密留在比 `.env` 檔案更大的曝露範圍)
- 移除 GitHub Actions 的自動排程,避免本機與雲端同時執行造成重複通知或 git push 衝突
- 讓使用者事後可以看到最近幾次本機執行的結果(log 檔)

**Non-Goals:**
- 不處理「電腦真的關機時怎麼辦」——使用者已經接受這個前提(大部分時間開著,偶爾跳過可接受)
- 不做 log 自動輪替/清理機制——這是單人使用的本機程式,log 檔案增長速度很慢,之後真的需要再手動清或加輪替,不在這次範圍內先做
- 不移除 GitHub Actions workflow 檔案本身,只移除自動排程觸發,保留 `workflow_dispatch` 當作「需要時可以手動在雲端測試」的備用選項——這不違反「單一執行路徑」原則,因為它不會自動觸發,不會跟本機排程衝突

## Decisions

### 用 PowerShell 腳本(`run_check.ps1`)包裝執行邏輯,而非直接在工作排程器裡寫指令
工作排程器的「動作」只能填一行指令,把「啟用虛擬環境、讀取 `.env`、設定環境變數、執行 Python、把輸出導向 log 檔」這些步驟寫在一行指令裡很不好維護。寫成一個 `.ps1` 腳本,工作排程器只需要呼叫這個腳本,之後要調整執行細節只要改這個檔案,不用重新設定工作排程器。

### 腳本自己解析 `.env`,不新增 `python-dotenv` 依賴
`.env` 檔案格式單純(`KEY=VALUE`),PowerShell 幾行就能解析並用 `$env:DISCORD_WEBHOOK_URL = ...` 設定成**這次 PowerShell 行程**的環境變數,子行程(`python -m src.main`)會繼承到。這個環境變數的生命週期只到這次排程執行結束,不會留在系統裡,也不需要在 Python 那邊加新套件。

已考慮過的替代方案:用 `setx` 把 Webhook URL 寫成 Windows 使用者的永久環境變數。這樣設定一次就不用每次讀 `.env`,但代價是這個機密會变成系統內所有以該使用者身份執行的程式都能讀到,曝露範圍比現在的 `.env` 檔案(只有這個專案目錄裡的程式會去讀)更大,不採用。

### 用 PowerShell 的 `ScheduledTasks` 模組註冊排程,而非舊版 `schtasks.exe`
`Register-ScheduledTask` / `New-ScheduledTaskSettingsSet` 支援 `-WakeToRun`(電腦睡眠時喚醒執行)這種細緻設定,比 `schtasks.exe` 的命令列參數更直覺、更好維護。設定:每小時重複執行、`StartWhenAvailable`(錯過的執行時間點一到電腦恢復就補跑,而不是等到下一個小時)、`WakeToRun`(若電腦是睡眠而非關機,會嘗試喚醒來執行)。工作本身設定成只在該使用者登入的工作階段下執行(不需要另外儲存密碼、不需要用高權限的「不管是否登入都執行」模式),符合「大部分時間電腦開著且登入」的實際使用情境。

### 執行輸出導向本機 log 檔,不做輪替
把 `python -m src.main` 的 stdout/stderr 用 `>>`(附加)導向 `logs/run.log`,讓使用者事後可以打開這個檔案看最近執行的狀況(有沒有抓到活動、有沒有發通知、有沒有來源健康告警)。這個 log 檔會持續變大,但這個程式一天最多跑 24 次、每次輸出就幾行文字,成長速度很慢,不值得現在就做自動輪替。

### `data/*.json` 停止進 git 版本控制
這兩個狀態檔原本因為 GitHub Actions 是「用完就銷毀」的環境,必須 commit 回 repo 才能跨執行保留。改到本機執行後,同一台機器的磁碟本身就是持久的,不需要再透過 git 才能讓下次執行讀到上次的狀態。把 `data/*.json` 加進 `.gitignore`、`git rm --cached` 移除追蹤(保留本機磁碟上現有內容不變),之後這兩個檔案就是純粹的本機執行狀態,不再出現在 commit 歷史裡。

### 移除 GitHub Actions 的 `schedule` 觸發,保留 `workflow_dispatch`
`.github/workflows/check_concerts.yml` 的 `on.schedule` 整段移除,只留 `workflow_dispatch`。這樣 GitHub Actions 不會再自動執行(避免跟本機排程重複通知、或兩邊同時想 commit 狀態檔造成衝突——雖然狀態檔已經不進 git 了,但 workflow 裡原本commit的那一步如果還留著、又讀不到本機的狀態檔,會導致雲端那邊的去重邏輯錯亂,所以移除自動排程是必要的),但保留手動觸發的能力,萬一之後想在不開電腦的情況下臨時從雲端測一次,還有這個管道可以用(明確知道它不會自動跑,只是備用工具)。

## Risks / Trade-offs

- **[風險] 電腦睡眠或關機時,該次排定的執行會被跳過;如果連續好幾個小時沒開機,這段時間的新場次就不會被即時通知到。** → 緩解方式:使用者已經評估並接受這個取捨(大部分時間電腦是開著的);`StartWhenAvailable` 設定讓電腦恢復開機/連網後盡快補跑一次,不會無限期延後到下一個整點。
- **[風險] 工作排程器設定成只在使用者登入時執行,如果使用者登出(不是只是鎖定螢幕、是真的登出帳號),排程就不會跑。** → 緩解方式:這對一般個人使用情境(開著電腦、鎖螢幕但沒登出)是可接受的;真的需要「不管有沒有登入都要跑」的話,之後可以改成儲存密碼的高權限模式,但那樣機密管理會變複雜,目前不需要做到這麼嚴格。
- **[風險] log 檔案會無限增長。** → 緩解方式:已在 Non-Goals 說明,成長速度慢,之後需要再處理。

## Migration Plan

1. 建立 `run_check.ps1`
2. 修改 `.github/workflows/check_concerts.yml`,移除 `schedule` 觸發
3. 修改 `.gitignore`,加入 `data/*.json`;對已追蹤的 `data/seen_events.json`、`data/source_health.json` 執行 `git rm --cached`(本機檔案內容不變,只是 git 不再追蹤)
4. 用 PowerShell 的 `Register-ScheduledTask` 在使用者電腦上註冊排程工作
5. 手動觸發一次排程工作(或等它自然觸發),確認本機執行成功、log 檔有內容、狀態檔有更新

若要回滾:`Unregister-ScheduledTask` 移除本機排程工作,把 `.github/workflows/check_concerts.yml` 的 `schedule` 觸發加回去即可恢復原本的 GitHub Actions 排程(狀態檔屆時需要重新手動 commit 一次當作新的起點)。

## Open Questions

(無)
