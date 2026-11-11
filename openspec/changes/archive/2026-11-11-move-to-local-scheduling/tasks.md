## 1. 本機啟動腳本(對應 spec: scheduled-check-run)

- [x] 1.1 建立 `run_check.ps1`:解析 `.env` 取得 `DISCORD_WEBHOOK_URL` 並設為行程環境變數、啟用 `.venv`、執行 `python -m src.main`,輸出(stdout/stderr)附加寫入 `logs/run.log`,並驗證在 PowerShell 手動執行這個腳本時行為跟直接跑 `python -m src.main` 一致(有抓到活動、`logs/run.log` 有對應內容)
- [x] 1.2 建立 `logs/` 目錄與 `.gitignore` 規則排除 log 檔,並驗證執行腳本後 log 檔確實被建立且內容可讀

## 2. 停止用 git 持久化狀態(對應 spec: scheduled-check-run)

- [x] 2.1 修改 `.gitignore` 加入 `data/*.json`,對 `data/seen_events.json`、`data/source_health.json` 執行 `git rm --cached`,並驗證這兩個檔案在本機磁碟上內容不變、但 `git status` 不再把它們列為追蹤中的變更

## 3. 移除 GitHub Actions 自動排程(對應 spec: scheduled-check-run)

- [x] 3.1 修改 `.github/workflows/check_concerts.yml`,移除 `on.schedule`,只保留 `workflow_dispatch`,並驗證 YAML 仍可被解析、且不再含有 `schedule` 區塊

## 4. 註冊本機排程工作

- [x] 4.1 用 PowerShell `Register-ScheduledTask` 建立一個每小時執行 `run_check.ps1` 的排程工作(設定 `StartWhenAvailable`、`WakeToRun`),並驗證 `Get-ScheduledTask` 能查到這個工作、設定內容正確
- [x] 4.2 手動觸發這個排程工作一次(`Start-ScheduledTask`),驗證執行成功、`logs/run.log` 有新內容、`data/seen_events.json`/`data/source_health.json` 有被正常讀寫

## 5. 文件更新

- [x] 5.1 更新 `README.md`:移除/調整「部署到 GitHub Actions」章節,改成「部署到本機排程」的說明,包含 `run_check.ps1` 的用途與排程工作的查詢/移除方式
