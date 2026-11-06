## 1. 設定與資料結構(對應 spec: source-health-alerting)

- [ ] 1.1 在 `config.yaml` 新增 `monitoring.consecutive_empty_threshold`(預設 3),並在 `src/config.py` 新增讀取函式,驗證沒有設定該欄位時會回退到預設值 3
- [ ] 1.2 把 `src/scrapers/__init__.py` 的 `SCRAPERS` 改成 `list[tuple[str, Callable]]`(用各模組的 `SOURCE` 常數配對 `fetch_events`),並驗證改動後仍能從外部拿到「名稱+抓取結果」

## 2. 健康狀態追蹤(對應 spec: source-health-alerting)

- [x] 2.1 實作 `src/health.py` 的 `load_health`/`save_health`(讀寫 `data/source_health.json`,檔案不存在時視為空字典),並驗證讀寫一輪後資料一致
- [x] 2.2 實作 `src/health.py` 的 `record_result(health, source, had_events, threshold) -> bool`,並以單元測試驗證四種情境:連續達門檻時回傳 `True` 且只回傳一次、未達門檻回傳 `False`、恢復後重置計數、恢復後再次連續失效會重新觸發一次告警

## 3. 告警發送(對應 spec: source-health-alerting)

- [x] 3.1 在 `src/notifier.py` 新增 `send_health_alert(webhook_url, source, consecutive_empty) -> bool`,訊息內容包含來源名稱與連續失敗次數,並驗證對測試用 webhook 執行時 Discord 頻道確實收到告警訊息

## 4. 串接進主流程(對應 spec: scheduled-check-run)

- [x] 4.1 修改 `src/main.py`:改用新的 `SCRAPERS` 格式分別取得每個來源的抓取結果,執行完比對/通知後,呼叫 `health.py` 更新每個來源的健康狀態,對 `record_result` 回傳 `True` 的來源呼叫 `send_health_alert`,並在結束時 `save_health`
- [x] 4.2 本機驗證:暫時讓某一個 scraper 強制回傳空清單,連續執行 3 次 `python -m src.main`,確認第 3 次(剛好達門檻)才觸發告警,第 4 次不會重複告警;接著讓它恢復回傳真實資料、再強制清空 3 次,驗證會再觸發第二次告警
