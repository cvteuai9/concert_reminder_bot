## 1. 專案骨架

- [x] 1.1 建立目錄結構(`src/`、`src/scrapers/`、`data/`、`.github/workflows/`)與 `requirements.txt`(`requests`、`beautifulsoup4`、`pyyaml`),並驗證 `pip install -r requirements.txt` 成功
- [x] 1.2 建立 `.env.example`(列出 `DISCORD_WEBHOOK_URL`)與 `README.md`(說明如何設定 `config.yaml`、本機執行方式、GitHub secret 設定),並驗證檔案存在且內容可讀

## 2. concert-source-scraping(對應 spec: concert-source-scraping)

- [x] 2.1 實作 `src/scrapers/base.py` 的 `Event` dataclass(欄位:`source`、`id`、`title`、`url`、`date`、`venue`,後兩者預設為 `None`),並驗證可以建立一個 `Event` 實例
- [x] 2.2 實作 `src/scrapers/tixcraft.py`:對 `tixcraft.com/activity` 發出 GET 請求(帶合理的 User-Agent),用 BeautifulSoup 解析出每個活動的標題、連結(`/activity/detail/{id}`),轉成 `Event` 清單,並驗證對真實網站執行時能抓到多筆活動
- [x] 2.3 為 `tixcraft.py` 的抓取流程加上 try/except,連線失敗或解析失敗時記錄錯誤並回傳空清單,並驗證刻意傳入錯誤網址時不會拋出未處理例外
- [x] 2.4 實作 `src/scrapers/__init__.py`,匯出一個 `SCRAPERS` 清單(目前只含 tixcraft 的抓取函式),並驗證從外部呼叫 `SCRAPERS` 中的每個函式都能拿到 `Event` 清單

## 3. artist-watch-matching(對應 spec: artist-watch-matching)

- [x] 3.1 建立 `config.yaml` 範例(`artists` 清單,每個藝人含 `name` 與 `keywords` 陣列,放 2-3 個示範藝人),並驗證檔案是合法 YAML
- [x] 3.2 實作 `src/config.py` 讀取 `config.yaml` 並回傳藝人清單結構,並驗證讀到的藝人數量與關鍵字數量與檔案內容一致
- [x] 3.3 實作 `src/matcher.py`:將活動標題與每個藝人關鍵字標準化(小寫、trim)後做子字串比對,回傳符合的 `(artist_name, Event)` 配對清單,並以單元測試驗證「標題含關鍵字→相符」與「標題不含任何關鍵字→不相符」兩種情況

## 4. discord-alerting(對應 spec: discord-alerting)

- [x] 4.1 實作 `src/state.py`:讀取/寫入 `data/seen_events.json`(已通知的活動 id 集合),檔案不存在時視為空集合,並驗證讀寫一輪後資料一致
- [x] 4.2 實作 `src/notifier.py`:對 `DISCORD_WEBHOOK_URL` 發送 Discord embed 訊息(含藝人名稱、標題、連結、場地/日期若有),回傳是否成功發送,並驗證對測試用 webhook 執行時 Discord 頻道確實收到訊息
- [x] 4.3 驗證 `notifier.py` 在 webhook 回應失敗(例如錯誤的 URL)時回傳失敗而不拋出未處理例外,呼叫端據此判斷是否要標記為已通知

## 5. scheduled-check-run 主流程(對應 spec: scheduled-check-run)

- [x] 5.1 實作 `src/main.py`:依序呼叫 `SCRAPERS` 取得所有活動 → `matcher` 比對 → 用 `state` 過濾出未通知過的新配對 → 逐一呼叫 `notifier` 發送 → 只對發送成功的活動更新 `seen_events.json`,並驗證本機執行一次後,`data/seen_events.json` 內容與實際發送成功的通知一致
- [x] 5.2 重複執行 `python -m src.main` 第二次,驗證同一批活動不會被重複發送通知(對應 discord-alerting 的去重需求)

## 6. 排程與部署(對應 spec: scheduled-check-run)

- [x] 6.1 建立 `.github/workflows/check_concerts.yml`:`schedule`(`*/30 * * * *`)+ `workflow_dispatch` 觸發,steps 為 checkout → setup-python → `pip install -r requirements.txt` → `python -m src.main`(帶入 secret `DISCORD_WEBHOOK_URL`),並賦予 `contents: write` 權限
- [x] 6.2 在 workflow 最後加上「若 `data/seen_events.json` 有變動才 commit & push」的步驟,並驗證 workflow 語法透過 `actionlint` 或 GitHub 介面檢查無誤(若本機沒有 actionlint,至少確認 YAML 可被 `yaml.safe_load` 解析)
- [x] 6.3 `git init` 並建立初次 commit(不含 `.env`、任何真實 webhook URL 等機密),並驗證 `git status` 顯示 working tree clean

## 7. 端到端驗證

- [x] 7.1 本機完整跑一次:設定好 `.env` 的測試 webhook、`config.yaml` 填入一個目前 tixCraft 上真的有場次的藝人關鍵字,執行 `python -m src.main`,並在 Discord 測試頻道確認收到對應通知
- [x] 7.2(需使用者協助)在 GitHub 建立 repo、push 程式碼、設定 `DISCORD_WEBHOOK_URL` secret,手動觸發一次 `workflow_dispatch`,驗證 CI 執行成功且 `data/seen_events.json` 被 commit 回 repo
