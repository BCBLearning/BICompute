#!/usr/bin/env python3
"""
Script de démonstration pour le hackathon
BesmaInfo © 2025 - Hackathon LabLab AI
"""

import os
import sys
import time
import json
import requests
import threading
import random
from datetime import datetime

COORDINATOR_URL = os.getenv("COORDINATOR_URL", "https://bi-compute.railway.app")

class DemoShowcase:
    def __init__(self, coordinator_url):
        self.coordinator_url = coordinator_url
        self.demo_running = True
        self.workers = []
        self.tasks_submitted = []
        
    def print_header(self, text):
        print("\n" + "="*70)
        print(f" {text}")
        print("="*70)
    
    def check_api(self):
        """Vérifier que l'API est accessible"""
        try:
            response = requests.get(f"{self.coordinator_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API accessible: {data['service']}")
                print(f"   URL: {self.coordinator_url}")
                print(f"   Version: {data['version']}")
                return True
        except Exception as e:
            print(f"❌ API inaccessible: {e}")
        return False
    
    def start_demo_workers(self, count=5):
        """Démarrer des workers de démonstration"""
        print(f"\n🚀 Démarrage de {count} workers de démo...")
        
        for i in range(count):
            worker_name = f"Demo-Worker-{i+1}"
            thread = threading.Thread(
                target=self.simulate_worker,
                args=(worker_name,),
                daemon=True
            )
            thread.start()
            self.workers.append(thread)
            print(f"   👷 {worker_name} démarré")
            time.sleep(0.5)
    
    def simulate_worker(self, name):
        """Simuler un worker qui exécute des tâches"""
        # Enregistrement
        try:
            response = requests.post(
                f"{self.coordinator_url}/api/workers/register",
                json={
                    "name": name,
                    "cpu_cores": random.randint(2, 8),
                    "memory_mb": random.choice([2048, 4096, 8192]),
                    "platform": random.choice(["linux", "windows", "macos", "docker"])
                },
                timeout=10
            )
            
            if response.status_code == 200:
                worker_id = response.json()["worker_id"]
                
                # Boucle de travail
                while self.demo_running:
                    try:
                        # Récupérer les tâches
                        tasks_resp = requests.get(f"{self.coordinator_url}/api/tasks/available")
                        if tasks_resp.status_code == 200:
                            tasks = tasks_resp.json().get("available_tasks", [])
                            
                            for task in tasks[:2]:  # Max 2 tâches à la fois
                                # Simuler l'exécution
                                exec_time = random.uniform(1, 4)
                                time.sleep(exec_time)
                                
                                # Résultat simulé
                                result = {
                                    "success": random.random() > 0.1,  # 90% de succès
                                    "stdout": f"✅ Tâche {task['id']} exécutée par {name} en {exec_time:.1f}s",
                                    "stderr": "",
                                    "execution_time": exec_time
                                }
                                
                                # Soumettre
                                requests.post(
                                    f"{self.coordinator_url}/api/tasks/{task['task_id']}/results",
                                    json={"worker_id": worker_id, "result": result},
                                    timeout=5
                                )
                    
                    except:
                        pass
                    
                    time.sleep(random.uniform(5, 10))
                    
        except Exception as e:
            print(f"⚠️ Erreur worker {name}: {e}")
    
    def submit_demo_tasks(self):
        """Soumettre des tâches de démonstration impressionnantes"""
        demo_tasks = [
            {
                "name": "🌟 Calcul distribué de π (Monte Carlo)",
                "type": "python",
                "command": {
                    "type": "python",
                    "command": """import random, math, time\nprint("=== CALCUL DISTRIBUÉ DE π ===")\nprint("Méthode Monte Carlo avec 1,000,000 de points")\n\nstart = time.time()\npoints = 1000000\ninside = 0\n\nfor i in range(points):\n    if i % 100000 == 0:\n        print(f"Progression: {i/points*100:.1f}%")\n    x, y = random.random(), random.random()\n    if x*x + y*y <= 1:\n        inside += 1\n\npi_est = 4 * inside / points\nerror = abs(math.pi - pi_est)\nexec_time = time.time() - start\n\nprint(f"\\n🎯 RÉSULTATS:")\nprint(f"π estimé: {pi_est:.8f}")\nprint(f"π réel:    {math.pi:.8f}")\nprint(f"Erreur:    {error:.8f}")\nprint(f"Précision: {100 - error*100:.4f}%")\nprint(f"Temps:     {exec_time:.2f} secondes")\nprint(f"Performance: {points/exec_time:.0f} points/sec")"""
                }
            },
            {
                "name": "📊 Analyse de texte: Mots les plus fréquents",
                "type": "shell", 
                "command": {
                    "type": "shell",
                    "command": """echo "BI-Compute Hackathon Distributed Computing Edge Network Artificial Intelligence Machine Learning Cloud Fog IoT Blockchain Decentralized Scalable Resilient Open Source Community Innovation Technology Future Digital Revolution" | tr ' ' '\\n' | tr '[:upper:]' '[:lower:]' | sort | uniq -c | sort -nr | head -10"""
                }
            },
            {
                "name": "🔐 Benchmarks cryptographiques",
                "type": "shell",
                "command": {
                    "type": "shell", 
                    "command": """echo "=== BENCHMARKS CRYPTO ==="
echo "Test SHA-256:"
time echo "BI-Compute Hackathon 2024" | sha256sum
echo -e "\\nTest MD5:"
time echo "BI-Compute Hackathon 2024" | md5sum
echo -e "\\nPerformance cryptographique mesurée""""
                }
            },
            {
                "name": "⚡ Performance CPU: Calcul de nombres premiers",
                "type": "python",
                "command": {
                    "type": "python",
                    "command": """import time, math\nprint("=== CALCUL DE NOMBRES PREMIERS ===")\n\nstart = time.time()\nlimit = 100000\nprimes = []\n\nfor num in range(2, limit):\n    is_prime = True\n    for i in range(2, int(math.sqrt(num)) + 1):\n        if num % i == 0:\n            is_prime = False\n            break\n    if is_prime:\n        primes.append(num)\n\nend = time.time()\nexec_time = end - start\n\nprint(f"Trouvé {len(primes)} nombres premiers jusqu'à {limit:,}")\nprint(f"Derniers 5 premiers: {primes[-5:]}")\nprint(f"Temps d'exécution: {exec_time:.2f} secondes")\nprint(f"Performance: {limit/exec_time:.0f} nombres/sec")"""
                }
            }
        ]
        
        print("\n📤 Soumission des tâches de démo...")
        
        for task in demo_tasks:
            try:
                response = requests.post(
                    f"{self.coordinator_url}/api/tasks",
                    json=task,
                    timeout=10
                )
                
                if response.status_code == 201:
                    task_id = response.json().get("task_id")
                    self.tasks_submitted.append(task_id)
                    print(f"   ✅ {task['name']}")
                else:
                    print(f"   ⚠️ Échec: {task['name']}")
                    
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
    
    def show_live_stats(self, duration=120):
        """Afficher les statistiques en direct"""
        print("\n📊 STATISTIQUES EN DIRECT")
        print("   Temps | Workers | Tâches | Terminées | Taux")
        print("   " + "-"*50)
        
        start_time = time.time()
        
        while time.time() - start_time < duration and self.demo_running:
            try:
                response = requests.get(f"{self.coordinator_url}/api/stats", timeout=5)
                if response.status_code == 200:
                    stats = response.json()
                    
                    workers = stats["workers"]["active"]
                    total_tasks = stats["tasks"]["total"]
                    completed = stats["tasks"]["completed"]
                    rate = stats["performance"]["completion_rate"]
                    
                    elapsed = int(time.time() - start_time)
                    
                    print(f"   {elapsed:3d}s | {workers:7d} | {total_tasks:6d} | {completed:9d} | {rate:5.1f}%")
                    
                    # Arrêter si tout est terminé
                    if completed >= len(self.tasks_submitted) and elapsed > 30:
                        break
                        
            except:
                pass
            
            time.sleep(3)
    
    def run_showcase(self):
        """Exécuter la démo complète"""
        self.print_header("🎬 DÉMONSTRATION BI-COMPUTE HACKATHON")
        
        # 1. Vérifier l'API
        if not self.check_api():
            return
        
        # 2. Démarrer les workers
        self.start_demo_workers(5)
        time.sleep(3)
        
        # 3. Soumettre les tâches
        self.submit_demo_tasks()
        time.sleep(2)
        
        # 4. Montrer les stats en direct
        self.show_live_stats(180)
        
        # 5. Conclusion
        self.demo_running = False
        
        # Attendre que les threads se terminent
        for thread in self.workers:
            thread.join(timeout=1)
        
        self.print_header("🎉 DÉMONSTRATION TERMINÉE !")
        print(f"\n🌐 Dashboard: {self.coordinator_url}")
        print("📊 Les jurys peuvent maintenant:")
        print("   1. Voir les résultats sur le dashboard")
        print("   2. Démarrer leurs propres workers")
        print("   3. Soumettre de nouvelles tâches")
        print("\n🤖 Merci d'avoir participé !")

def main():
    # Récupérer l'URL depuis les arguments
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = COORDINATOR_URL
    
    showcase = DemoShowcase(url)
    
    try:
        showcase.run_showcase()
    except KeyboardInterrupt:
        print("\n👋 Démo interrompue")
        showcase.demo_running = False

if __name__ == "__main__":
    main()