## Purpose

將比對出的新活動透過 Discord Webhook 發送通知給使用者,並確保同一活動不會被重複通知。

## Requirements

### Requirement: 發送 Discord 通知
System SHALL 對於每個新符合追蹤藝人的活動,透過設定的 Discord Webhook 發送一則訊息,訊息內容包含藝人名稱、活動標題、售票連結,並在可取得時包含場地與日期。

#### Scenario: 成功發送通知
- **WHEN** 系統找到一個新符合追蹤藝人且尚未通知過的活動
- **THEN** 系統對 Discord Webhook 發出請求,訊息中包含該活動的藝人名稱、標題與售票連結

### Requirement: 避免重複通知
System SHALL 記錄已經通知過的活動,下次執行檢查到相同活動時不再重複發送通知。

#### Scenario: 同一活動重複出現
- **WHEN** 系統在前一次執行已經通知過某個活動,且該活動仍出現在最新抓取結果中
- **THEN** 系統不會再對該活動發送第二次通知

### Requirement: 通知失敗不遺失活動的待通知狀態
System SHALL 只在 Discord 通知實際發送成功後,才將該活動標記為已通知;若發送失敗,該活動應在下次執行時重試通知。

#### Scenario: Discord Webhook 回應錯誤
- **WHEN** 對 Discord Webhook 發送請求時收到失敗的回應
- **THEN** 系統不將該活動標記為已通知,讓下次執行時可以重新嘗試發送
