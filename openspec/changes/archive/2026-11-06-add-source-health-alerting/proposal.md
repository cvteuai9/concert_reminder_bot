## Why

目前每個 scraper 遇到錯誤(連線失敗、平台改版導致選擇器失效、被反爬機制擋下)都只會記錄一行 log 警告、回傳空清單讓流程繼續跑,使用者完全不會被主動通知。GitHub Actions 的執行結果仍顯示「成功」(因為程式沒有 crash),使用者必須自己去翻 Actions 的執行紀錄才可能發現某個平台已經悄悄失效。隨著來源數增加到 7 個,人工定期檢查不現實,需要讓系統主動告警。

## What Changes

- 新增一個「來源健康狀態」追蹤機制:記錄每個 scraper 最近幾次執行是否抓到任何活動
- 當某個來源連續 N 次(預設 3,可在 `config.yaml` 調整)都回傳空清單時,透過 Discord 發送一則告警訊息,提醒使用者該平台可能被改版或擋住,需要人工檢查
- 告警只在「剛跨過門檻的那一次」發送一次,不會每次執行都重複發送;當該來源恢復抓到資料後,下次再連續失敗會重新計數、可以再觸發一次告警
- 健康狀態存成 `data/source_health.json`,跟現有的 `data/seen_events.json` 一樣由 GitHub Actions commit 回 repo 以跨執行持久化

## Capabilities

### New Capabilities
- `source-health-alerting`: 追蹤每個售票平台來源的抓取健康狀態,連續多次抓不到資料時透過 Discord 主動告警

### Modified Capabilities
- `scheduled-check-run`: 端到端執行流程新增「更新來源健康狀態、必要時發送告警」這個步驟

## Impact

- 新增 `data/source_health.json` 狀態檔
- `src/main.py` 的主流程會多一個步驟,但不影響既有的抓取/比對/通知/去重邏輯
- 不新增依賴套件、不修改 GitHub Actions workflow(沿用既有的 commit-state-back 機制)
