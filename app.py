import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request

# ── 應用程式初始化 ──────────────────────────────────────────────
app = Flask(__name__)
app.json.ensure_ascii = False  # 讓 JSON 回傳正確顯示中文

DATABASE = "tasks.db"

# ── 日誌設定 ───────────────────────────────────────────────────
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "error.log")

os.makedirs(LOG_DIR, exist_ok=True)  # 程式執行時自動建立 logs/


def write_error_log(message):
    """將錯誤訊息以 [時間戳] 格式附加寫入 error.log。"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except PermissionError:
        pass  # 權限問題時略過，避免程式崩潰


# ── 資料庫輔助函式 ─────────────────────────────────────────────
def get_db_connection():
    """建立並回傳 SQLite 連線，欄位可用名稱存取。"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row):
    """將 sqlite3.Row 轉換為一般 dict。"""
    return dict(row)


# ── 路由：取得所有任務 GET /api/tasks ──────────────────────────
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """回傳所有任務清單。"""
    conn = None
    try:
        conn = get_db_connection()
        tasks = conn.execute("SELECT * FROM tasks").fetchall()
        return jsonify({
            "message": "成功取得任務列表",
            "data": [row_to_dict(task) for task in tasks]
        }), 200
    except Exception as e:
        write_error_log(f"GET /api/tasks 發生錯誤：{e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "伺服器處理失敗，請稍後再試"
        }), 500
    finally:
        if conn:
            conn.close()  # 確保無論成功或失敗都會關閉連線


# ── 路由：取得單一任務 GET /api/tasks/<task_id> ────────────────
@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """根據 ID 回傳單一任務；找不到則回傳 404。"""
    conn = None
    try:
        conn = get_db_connection()
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if task is None:
            return jsonify({
                "error": "Not Found",
                "message": f"找不到 ID 為 {task_id} 的任務"
            }), 404

        return jsonify({
            "message": "成功取得任務",
            "data": row_to_dict(task)
        }), 200
    except Exception as e:
        write_error_log(f"GET /api/tasks/{task_id} 發生錯誤：{e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "伺服器處理失敗，請稍後再試"
        }), 500
    finally:
        if conn:
            conn.close()


# ── 路由：新增任務 POST /api/tasks ────────────────────────────
@app.route("/api/tasks", methods=["POST"])
def create_task():
    """接收 JSON 建立新任務；title 為必填欄位。"""
    data = request.get_json(silent=True)

    # 防呆：確保 data 不是 None 且轉換為字串安全檢查
    if data is None or not str(data.get("title", "")).strip():
        return jsonify({
            "error": "Bad Request",
            "message": "請求內容必須是合法 JSON，且 title 為必填欄位"
        }), 400

    title = str(data["title"]).strip()
    description = data.get("description", "")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.execute(
            "INSERT INTO tasks (title, description, done) VALUES (?, ?, 0)",
            (title, description)
        )
        conn.commit()
        new_id = cursor.lastrowid

        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (new_id,)
        ).fetchone()

        return jsonify({
            "message": "任務建立成功",
            "data": row_to_dict(task)
        }), 201
    except Exception as e:
        write_error_log(f"POST /api/tasks 發生錯誤：{e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "伺服器處理失敗，請稍後再試"
        }), 500
    finally:
        if conn:
            conn.close()


# ── 路由：更新任務 PUT /api/tasks/<task_id> ───────────────────
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """全量更新指定任務；task_id 不存在回傳 404，驗證失敗回傳 400。"""
    data = request.get_json(silent=True)

    if data is None or not str(data.get("title", "")).strip():
        return jsonify({
            "error": "Bad Request",
            "message": "請求內容必須是合法 JSON，且 title 為必填欄位"
        }), 400

    title = str(data["title"]).strip()
    description = data.get("description", "")
    
    # 確保 done 的型態安全（相容字串、數字與布林值）
    raw_done = data.get("done", 0)
    done = 1 if raw_done in [1, True, "1"] else 0

    conn = None
    try:
        conn = get_db_connection()
        existing = conn.execute(
            "SELECT id FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if existing is None:
            return jsonify({
                "error": "Not Found",
                "message": f"找不到 ID 為 {task_id} 的任務"
            }), 404

        conn.execute(
            "UPDATE tasks SET title = ?, description = ?, done = ? WHERE id = ?",
            (title, description, done, task_id)
        )
        conn.commit()

        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        return jsonify({
            "message": "任務更新成功",
            "data": row_to_dict(task)
        }), 200
    except Exception as e:
        write_error_log(f"PUT /api/tasks/{task_id} 發生錯誤：{e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "伺服器處理失敗，請稍後再試"
        }), 500
    finally:
        if conn:
            conn.close()


# ── 路由：刪除任務 DELETE /api/tasks/<task_id> ────────────────
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """刪除指定任務；task_id 不存在回傳 404。"""
    conn = None
    try:
        conn = get_db_connection()
        existing = conn.execute(
            "SELECT id FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if existing is None:
            return jsonify({
                "error": "Not Found",
                "message": f"找不到 ID 為 {task_id} 的任務"
            }), 404

        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

        return jsonify({
            "message": f"ID 為 {task_id} 的任務已刪除"
        }), 200
    except Exception as e:
        write_error_log(f"DELETE /api/tasks/{task_id} 發生錯誤：{e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "伺服器處理失敗，請稍後再試"
        }), 500
    finally:
        if conn:
            conn.close()
