# 任務管理 RESTful API

使用 Flask 框架與 SQLite 資料庫實作的任務管理 RESTful API，提供任務的增刪查改功能。

## 專案結構

```
學號q3/
├── app.py              # 主程式
├── run.cmd             # 啟動伺服器批次檔
├── requirements.txt    # 套件清單
├── tasks.db            # SQLite 資料庫
├── .gitignore
├── README.md
└── logs/
    └── error.log       # 執行時自動產生
```

## 環境需求

- Python 3.x
- Flask

## 安裝與執行

**1. 建立並啟動虛擬環境**

```cmd
python -m venv env
env\Scripts\activate
```

**2. 安裝套件**

```cmd
pip install -r requirements.txt
```

**3. 啟動伺服器**

```cmd
run.cmd
```

伺服器啟動後可透過 `http://127.0.0.1/api/tasks` 存取 API。

---

## API 路由說明

| 功能 | HTTP 方法 | 路徑 |
|------|-----------|------|
| 取得所有任務 | GET | `/api/tasks` |
| 取得單一任務 | GET | `/api/tasks/<task_id>` |
| 新增任務 | POST | `/api/tasks` |
| 更新任務 | PUT | `/api/tasks/<task_id>` |
| 刪除任務 | DELETE | `/api/tasks/<task_id>` |

---

### 1. GET /api/tasks

取得所有任務清單。

**回傳範例（200）**

```json
{
  "message": "成功取得任務列表",
  "data": [
    { "id": 1, "title": "買雜貨", "description": "牛奶、麵包、雞蛋", "done": 0, "created_at": "..." },
    { "id": 2, "title": "寫作業", "description": "完成資訊小考", "done": 1, "created_at": "..." }
  ]
}
```

---

### 2. GET /api/tasks/\<task_id\>

根據 ID 取得單一任務。

**回傳範例（200）**

```json
{
  "message": "成功取得任務",
  "data": { "id": 1, "title": "買雜貨", "description": "牛奶、麵包、雞蛋", "done": 0, "created_at": "..." }
}
```

**找不到時（404）**

```json
{
  "error": "Not Found",
  "message": "找不到 ID 為 99 的任務"
}
```

---

### 3. POST /api/tasks

新增一筆任務，`title` 為必填欄位。

**請求格式**

```json
{
  "title": "準備考試",
  "description": "複習 Flask API"
}
```

**新增成功（201）**

```json
{
  "message": "任務建立成功",
  "data": { "id": 3, "title": "準備考試", "description": "複習 Flask API", "done": 0, "created_at": "..." }
}
```

**缺少 title 或格式錯誤（400）**

```json
{
  "error": "Bad Request",
  "message": "請求內容必須是合法 JSON，且 title 為必填欄位"
}
```

**資料庫錯誤（500）**

```json
{
  "error": "Internal Server Error",
  "message": "伺服器處理失敗，請稍後再試"
}
```

---

### 4. PUT /api/tasks/\<task_id\>

全量更新指定任務，所有欄位皆需提供。

**請求格式**

```json
{
  "title": "準備考試 - 更新",
  "description": "加強練習",
  "done": 1
}
```

**更新成功（200）**

```json
{
  "message": "任務更新成功",
  "data": { "id": 3, "title": "準備考試 - 更新", "description": "加強練習", "done": 1, "created_at": "..." }
}
```

**找不到時（404）** / **驗證失敗（400）** 同上方格式。

---

### 5. DELETE /api/tasks/\<task_id\>

刪除指定任務。

**刪除成功（200）**

```json
{
  "message": "ID 為 3 的任務已刪除"
}
```

**找不到時（404）**

```json
{
  "error": "Not Found",
  "message": "找不到 ID 為 3 的任務"
}
```

---

## 錯誤處理

| 狀態碼 | 說明 |
|--------|------|
| 200 | 成功取得資料 |
| 201 | 成功建立資源 |
| 400 | 請求格式錯誤或缺少必要欄位 |
| 404 | 找不到指定資源 |
| 500 | 伺服器內部錯誤 |

所有錯誤詳情會寫入 `logs/error.log`，不會回傳給客戶端。

---

## 測試指令（Windows CMD）

```cmd
# 取得所有任務
curl -isS http://127.0.0.1/api/tasks

# 取得 ID 為 1 的任務
curl -isS http://127.0.0.1/api/tasks/1

# 新增任務
curl -isS -X POST http://127.0.0.1/api/tasks ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"準備考試\",\"description\":\"複習 Flask API\"}"

# 更新 ID 為 3 的任務
curl -isS -X PUT http://127.0.0.1/api/tasks/3 ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"準備考試 - 更新\",\"description\":\"加強練習\",\"done\":1}"

# 刪除 ID 為 3 的任務
curl -isS -X DELETE http://127.0.0.1/api/tasks/3

# 嘗試取得已刪除的任務（預期 404）
curl -isS http://127.0.0.1/api/tasks/3
```
