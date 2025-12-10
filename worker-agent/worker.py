#!/usr/bin/env python3
"""
BI-COMPUTE WORKER
Agent d'exécution de tâches distribuées
Compatible Linux / PC / Termux
"""

import requests
import time
import subprocess
import platform
import argparse
import sys
import os
import tempfile
from datetime import datetime


class BIWorker:
    def __init__(self, coordinator_url, name=None):
        self.coordinator_url = coordinator_url.rstrip("/")
        self.name = name or f"worker-{platform.node()}"
        self.worker_id = None
        self.running = True

    # -------------------------------------------------
    # REGISTRATION
    # -------------------------------------------------
    def register(self):
        payload = {
            "name": self.name,
            "cpu_cores": os.cpu_count() or 1,
            "memory_mb": 1024,
            "platform": platform.system()
        }

        try:
            r = requests.post(
                f"{self.coordinator_url}/api/workers/register",
                json=payload,
                timeout=10
            )
            if r.status_code == 200:
                self.worker_id = r.json()["worker_id"]
                print(f"✅ Worker enregistré")
                print(f"   Nom : {self.name}")
                print(f"   ID  : {self.worker_id}")
                return True
            else:
                print("❌ Échec enregistrement")
        except Exception as e:
            print("❌ Erreur réseau :", e)

        return False

    # -------------------------------------------------
    # FETCH TASKS
    # -------------------------------------------------
    def fetch_tasks(self):
        try:
            r = requests.get(
                f"{self.coordinator_url}/api/tasks/available",
                timeout=5
            )
            if r.status_code == 200:
                return r.json().get("available_tasks", [])
        except Exception as e:
            print("⚠️ Erreur récupération tâches :", e)

        return []

    # -------------------------------------------------
    # EXECUTE TASK
    # -------------------------------------------------
    def execute_task(self, task):
        task_id = task["task_id"]
        command_data = eval(task["command"]) if isinstance(task["command"], str) else task["command"]
        task_type = command_data.get("type", "shell")

        print(f"🔧 Exécution tâche {task_id} ({task_type})")

        start = time.time()

        try:
            if task_type == "shell":
                result = subprocess.run(
                    command_data["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

            elif task_type == "python":
                with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                    f.write(command_data["command"])
                    filename = f.name

                result = subprocess.run(
                    [sys.executable, filename],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(filename)

            else:
                return {
                    "success": False,
                    "error": f"Type non supporté : {task_type}"
                }

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "execution_time": round(time.time() - start, 2)
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout dépassé"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -------------------------------------------------
    # SUBMIT RESULT
    # -------------------------------------------------
    def submit_result(self, task_id, result):
        payload = {
            "worker_id": self.worker_id,
            "result": result,
            "execution_time": result.get("execution_time", 0)
        }

        try:
            r = requests.post(
                f"{self.coordinator_url}/api/tasks/{task_id}/results",
                json=payload,
                timeout=10
            )
            if r.status_code == 200:
                print(f"✅ Résultat envoyé pour tâche {task_id}")
                return True
            else:
                print("❌ Erreur envoi résultat")
        except Exception as e:
            print("❌ Erreur réseau :", e)

        return False

    # -------------------------------------------------
    # MAIN LOOP
    # -------------------------------------------------
    def run(self):
        print("\n🚀 BI-COMPUTE WORKER DÉMARRÉ")
        print(f"📡 Coordinateur : {self.coordinator_url}")
        print("⏳ En attente de tâches...\n")

        while self.running:
            try:
                tasks = self.fetch_tasks()
                for task in tasks:
                    result = self.execute_task(task)
                    self.submit_result(task["task_id"], result)

                time.sleep(5)

            except KeyboardInterrupt:
                print("\n🛑 Arrêt demandé")
                self.running = False
            except Exception as e:
                print("⚠️ Erreur boucle worker :", e)
                time.sleep(10)


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="BI-COMPUTE Worker")
    parser.add_argument("--coordinator", default="http://localhost:5000",
                        help="URL du coordinateur")
    parser.add_argument("--name", help="Nom du worker")

    args = parser.parse_args()

    worker = BIWorker(args.coordinator, args.name)

    if worker.register():
        worker.run()
    else:
        print("❌ Impossible de démarrer le worker")


if __name__ == "__main__":
    main()