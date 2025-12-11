#!/usr/bin/env python3
"""
BI-COMPUTE WORKER AGENT
Version hackathon - BesmaInfo © 2025
"""

import os
import sys
import json
import time
import platform
import logging
import requests
import subprocess
import tempfile
import argparse
from datetime import datetime

# Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WORKER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HackathonWorker:
    """Worker simplifié pour le hackathon"""
    
    def __init__(self, coordinator_url, name=None):
        self.coordinator_url = coordinator_url.rstrip("/")
        self.name = name or f"Hackathon-Worker-{platform.node()[:10]}"
        self.worker_id = None
        self.running = True
        self.task_count = 0
        
    def register(self):
        """S'enregistrer auprès du coordinateur"""
        try:
            payload = {
                "name": self.name,
                "cpu_cores": os.cpu_count() or 4,
                "memory_mb": 8192,
                "platform": platform.platform()
            }
            
            response = requests.post(
                f"{self.coordinator_url}/api/workers/register",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.worker_id = data["worker_id"]
                logger.info(f"✅ Enregistré: {self.name} (ID: {self.worker_id})")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement: {e}")
        
        return False
    
    def fetch_tasks(self):
        """Récupérer les tâches disponibles"""
        try:
            response = requests.get(
                f"{self.coordinator_url}/api/tasks/available",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("available_tasks", [])
                
        except Exception as e:
            logger.error(f"⚠️ Erreur récupération tâches: {e}")
        
        return []
    
    def execute_task(self, task):
        """Exécuter une tâche"""
        task_id = task["task_id"]
        task_name = task["name"]
        
        logger.info(f"🔧 Exécution: {task_name}")
        
        try:
            # Parser la commande
            command_data = task["command"]
            if isinstance(command_data, str):
                command_data = json.loads(command_data)
            
            task_type = command_data.get("type", "shell")
            command = command_data.get("command", "")
            
            start_time = time.time()
            result = {"success": False}
            
            if task_type == "shell":
                # Exécuter commande shell
                process = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                result = {
                    "success": process.returncode == 0,
                    "stdout": process.stdout[:5000],  # Limiter la taille
                    "stderr": process.stderr[:5000],
                    "exit_code": process.returncode
                }
                
            elif task_type == "python":
                # Exécuter code Python
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(command)
                    script_path = f.name
                
                process = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                os.unlink(script_path)
                
                result = {
                    "success": process.returncode == 0,
                    "stdout": process.stdout[:5000],
                    "stderr": process.stderr[:5000],
                    "exit_code": process.returncode
                }
            
            result["execution_time"] = round(time.time() - start_time, 2)
            
            if result["success"]:
                logger.info(f"✅ Tâche {task_id} terminée en {result['execution_time']}s")
            else:
                logger.warning(f"⚠️ Tâche {task_id} échouée")
                
            return result
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout (30s dépassé)",
                "execution_time": 30
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0
            }
    
    def submit_result(self, task_id, result):
        """Soumettre le résultat"""
        try:
            payload = {
                "worker_id": self.worker_id,
                "result": result
            }
            
            response = requests.post(
                f"{self.coordinator_url}/api/tasks/{task_id}/results",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"📤 Résultat soumis pour tâche {task_id}")
                self.task_count += 1
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur soumission résultat: {e}")
        
        return False
    
    def run(self):
        """Boucle principale du worker"""
        print("=" * 60)
        print("🚀 BI-COMPUTE HACKATHON WORKER")
        print(f"📡 Coordinateur: {self.coordinator_url}")
        print(f"🤖 Worker: {self.name}")
        print("=" * 60)
        
        if not self.register():
            logger.error("❌ Impossible de démarrer")
            return
        
        logger.info("⏳ En attente de tâches...")
        
        try:
            while self.running:
                # Récupérer les tâches
                tasks = self.fetch_tasks()
                
                # Exécuter chaque tâche
                for task in tasks:
                    if not self.running:
                        break
                    
                    result = self.execute_task(task)
                    self.submit_result(task["task_id"], result)
                
                # Pause entre les vérifications
                time.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Arrêt demandé")
        except Exception as e:
            logger.error(f"❌ Erreur fatale: {e}")
        
        logger.info(f"👋 Arrêt. Tâches exécutées: {self.task_count}")

def main():
    parser = argparse.ArgumentParser(description="BI-COMPUTE Hackathon Worker")
    parser.add_argument(
        "--coordinator",
        default=os.environ.get("COORDINATOR_URL", "http://localhost:5000"),
        help="URL du coordinateur"
    )
    parser.add_argument(
        "--name",
        help="Nom du worker"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Mode debug"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    worker = HackathonWorker(args.coordinator, args.name)
    
    try:
        worker.run()
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()