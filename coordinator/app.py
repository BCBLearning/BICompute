from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3, os

app = Flask(__name__)
DB_FILE = "coordinator.db"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE workers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        cpu_cores INTEGER,
                        memory_mb INTEGER,
                        platform TEXT,
                        last_seen TEXT
                     )''')
        c.execute('''CREATE TABLE tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        type TEXT,
                        command TEXT,
                        status TEXT,
                        created_at TEXT,
                        completed_at TEXT
                     )''')
        conn.commit()
        conn.close()

init_db()

@app.route("/api/health")
def health():
    return jsonify({
        "service": "BI-COMPUTE Coordinator",
        "stats": {"active_workers": get_worker_count(), "total_tasks": get_task_count()}
    })

@app.route("/api/workers/register", methods=["POST"])
def register_worker():
    data = request.get_json()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO workers (name, cpu_cores, memory_mb, platform, last_seen) VALUES (?, ?, ?, ?, ?)",
              (data.get("name"), data.get("cpu_cores"), data.get("memory_mb"), data.get("platform"), datetime.now()))
    worker_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"worker_id": worker_id})

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (name, type, command, status, created_at) VALUES (?, ?, ?, ?, ?)",
              (data.get("name"), data.get("type"), str(data.get("command")), "pending", datetime.now()))
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"task_id": task_id, "message": "Task created"}), 201

@app.route("/api/tasks/available")
def available_tasks():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE status='pending'")
    tasks = c.fetchall()
    conn.close()
    tasks_list = []
    for t in tasks:
        tasks_list.append({"task_id": t[0], "name": t[1], "type": t[2], "command": t[3], "status": t[4]})
    return jsonify({"available_tasks": tasks_list})

@app.route("/api/tasks/<int:task_id>/results", methods=["POST"])
def submit_result(task_id):
    data = request.get_json()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tasks SET status='completed', completed_at=? WHERE id=?",
              (datetime.now(), task_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Result submitted"})

@app.route("/api/network/stats")
def network_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM workers")
    total_workers = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE status='completed'")
    completed_tasks = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE status='pending'")
    pending_tasks = c.fetchone()[0]
    conn.close()
    return jsonify({
        "network_name": "BI-COMPUTE Network",
        "timestamp": str(datetime.now()),
        "workers": {"total_active": total_workers, "total_cpu_cores": total_workers*4, "total_memory_mb": total_workers*1024},
        "tasks": {"completed": completed_tasks, "pending": pending_tasks},
        "recent_tasks": [],
        "top_workers": []
    })

def get_worker_count():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM workers")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_task_count():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM tasks")
    count = c.fetchone()[0]
    conn.close()
    return count

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)