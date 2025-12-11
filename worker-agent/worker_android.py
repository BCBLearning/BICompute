#!/usr/bin/env python3
"""
BI-COMPUTE WORKER - Version Android/Termux
BesmaInfo © 2025 - Hackathon LabLab AI
"""

import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime

# Configuration minimale
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ANDROID - %(levelname)s - %(message)s'
)

# Commandes autorisées (liste blanche)
SAFE_COMMANDS = [
    "echo", "cat", "ls", "pwd", "whoami", "date",
    "python", "python3", "pip", "node", "npm",
    "wc", "grep", "sort", "uniq", "head", "tail",
    "sha256sum", "md5sum", "curl", "wget"
]

class AndroidWorker:
    
    def __init__(self, coordinator_url, name="Android-Worker"):
        self.coordinator_url = coordinator_url.rstrip("/")
        self.name = name
        self.worker_id = None
        
        print(f"🤖 BI-COMPUTE Worker Android")
        print(f"📱 Nom: {self.name}")
        print(f"📡 Serveur: {self.coordinator_url}")
    
    def register(self):
        """Enregistrement simplifié"""
        try:
            import requests
            import platform
            
            payload = {
                "name": self.name,
                "cpu_cores": 4,  # Valeur standard
                "memory_mb": 2048,
                "platform": f"android-{platform.machine()}"
            }
            
            response = requests.post(
                f"{self.coordinator_url}/api/workers/register",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                self.worker_id = response.json().get("worker_id")
                print(f"✅ Enregistré (ID: {self.worker_id})")
                return True
                
        except Exception as e:
            print(f"❌ Erreur enregistrement: {e}")
        
        return False
    
    def execute_safe(self, command):
        """Exécuter une commande de manière sécurisée"""
        # Vérifier la première commande
        first_cmd = command.strip().split()[0] if command.strip() else ""
        
        if first_cmd not in SAFE_COMMANDS:
            return {
                "success": False,
                "error": f"Commande non autorisée: {first_cmd}",
                "stdout": "",
                "stderr": ""
            }
        
        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,  # Timeout court pour mobile
                encoding='utf-8',
                errors='ignore'
            )
            
            return {
                "success": process.returncode == 0,
                "stdout": process.stdout[:1000],
                "stderr": process.stderr[:1000],
                "exit_code": process.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout (60s dépassé)",
                "stdout": "",
                "stderr": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    def run(self):
        """Boucle principale"""
        if not self.register():
            print("❌ Impossible de démarrer")
            return
        
        print("⏳ En attente de tâches...")
        
        try:
            while True:
                import requests
                
                # Récupérer les tâches
                try:
                    response = requests.get(
                        f"{self.coordinator_url}/api/tasks/available",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        tasks = response.json().get("available_tasks", [])
                        
                        for task in tasks:
                            print(f"📥 Tâche: {task.get('name')}")
                            
                            # Extraire la commande
                            cmd_data = task.get("command", "")
                            if isinstance(cmd_data, str):
                                try:
                                    cmd_obj = json.loads(cmd_data)
                                    command = cmd_obj.get("command", "")
                                except:
                                    command = cmd_data
                            else:
                                command = cmd_data.get("command", "")
                            
                            # Exécuter
                            result = self.execute_safe(command)
                            
                            # Soumettre le résultat
                            if self.worker_id:
                                payload = {
                                    "worker_id": self.worker_id,
                                    "result": result
                                }
                                
                                requests.post(
                                    f"{self.coordinator_url}/api/tasks/{task['task_id']}/results",
                                    json=payload,
                                    timeout=15
                                )
                                
                                print(f"📤 Résultat soumis")
                
                except requests.exceptions.RequestException as e:
                    print(f"⚠️ Erreur réseau: {e}")
                
                # Attendre avant la prochaine vérification
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n👋 Arrêt demandé")
        except Exception as e:
            print(f"❌ Erreur: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Worker Android BI-Compute")
    parser.add_argument(
        "--coordinator",
        default=os.getenv("COORDINATOR_URL", "http://localhost:5000"),
        help="URL du coordinateur"
    )
    parser.add_argument(
        "--name",
        default=os.getenv("WORKER_NAME", "Android-Worker"),
        help="Nom du worker"
    )
    
    args = parser.parse_args()
    
    worker = AndroidWorker(args.coordinator, args.name)
    worker.run()

if __name__ == "__main__":
    main()