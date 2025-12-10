#!/usr/bin/env python3
"""
BI-COMPUTE WORKER - Android / Termux Edition
"""

import os
import sys
import time
import requests
import subprocess
import platform
from datetime import datetime

SAFE_COMMANDS = [
    "echo",
    "date",
    "whoami",
    "uname",
    "python",
    "python3"
]

class AndroidBIWorker:

    def __init__(self, coordinator_url, name="Android-Worker"):
        self.coordinator_url = coordinator_url.rstrip("/")
        self.name = name
        self.worker_id = None

    # --------------------------------------------------

    def register(self):
        payload = {
            "name": self.name,
            "cpu_cores": os.cpu_count() or 1,
            "memory_mb": 1024,
            "platform": "android-termux"
        }

        r = requests.post(f"{self.coordinator_url}/api/workers/register", json=payload)

        if r.status_code == 200:
            self.worker_id = r.json()["worker_id"]
            print(f"✅ Registered as {self.worker_id}")
            return True

        print("❌ Registration failed")
        return False

    # --------------------------------------------------

    def fetch_tasks(self):
        r = requests.get(f"{self.coordinator_url}/api/tasks/available")
        return r.json().get("available_tasks", [])

    # --------------------------------------------------

    def execute_task(self, task):
        cmd = task["command"].get("command", "")
        first = cmd.split()[0] if cmd else ""

        if first not in SAFE_COMMANDS:
            return {
                "success": False,
                "error": f"Command not allowed: {first}"
            }

        start = time.time()
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": round(time.time() - start, 2)
        }

    # --------------------------------------------------

    def submit_result(self, task_id, result):
        payload = {
            "worker_id": self.worker_id,
            "result": result,
            "execution_time": result.get("execution_time", 0)
        }

        requests.post(
            f"{self.coordinator_url}/api/tasks/{task_id}/results",
            json=payload
        )

    # --------------------------------------------------

    def start(self):
        print("🤖 BI-COMPUTE ANDROID WORKER")
        print(f"📡 Coordinator: {self.coordinator_url}")

        if not self.register():
            return

        while True:
            tasks = self.fetch_tasks()
            for task in tasks:
                print(f"🔧 Executing {task['task_id']}")
                result = self.execute_task(task)
                self.submit_result(task["task_id"], result)
            time.sleep(5)

# --------------------------------------------------

if __name__ == "__main__":
    COORDINATOR = os.getenv("COORDINATOR_URL", "http://localhost:5000")
    worker = AndroidBIWorker(COORDINATOR)
    worker.start()