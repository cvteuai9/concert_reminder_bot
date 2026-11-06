## ADDED Requirements

### Requirement: 從遠大售票抓取活動列表
System SHALL 從遠大售票(Ticket Plus)的公開活動資料 API 抓取目前上架的活動,並回傳每個活動的標題、詳細頁連結,以及可取得的日期資訊。

#### Scenario: 成功抓取遠大售票活動列表
- **WHEN** 系統對遠大售票的活動資料 API 發出請求且回應成功
- **THEN** 系統回傳一個活動清單,每個活動至少包含標題與可供識別的唯一 ID/連結

### Requirement: 從 7-ELEVEN ibon 抓取活動列表
System SHALL 從 7-ELEVEN ibon 售票系統的公開活動資料 API 抓取目前上架的活動,並回傳每個活動的標題、詳細頁連結,以及可取得的日期資訊。

#### Scenario: 成功抓取 ibon 活動列表
- **WHEN** 系統對 ibon 的活動資料 API 發出請求且回應成功
- **THEN** 系統回傳一個活動清單,每個活動至少包含標題與可供識別的唯一 ID/連結
