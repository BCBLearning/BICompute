#!/usr/bin/env python3
"""
SCRIPT DE DÉMONSTRATION FINAL
Pour la présentation du hackathon
"""
import os
import sys
import time
import json
import subprocess
import threading
import requests
from datetime import datetime

def print_header(text):
    """Afficher un en-tête"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_step(num, text):
    """Afficher une étape"""
    print(f"\n[{num}] {text}")

def run_demo():
    """Exécuter la démonstration complète"""
    print_header("🎬 DÉMONSTRATION BI-COMPUTE")
    print("Hackathon: Compute for the People, by the People")
    
    coordinator_url = "http://localhost:5000"
    dashboard_url = "http://localhost:8501"
    
    # Étape 1: Démarrer le coordinateur
    print_step(1, "Démarrage du coordinateur")
    
    def start_coordinator():
        os.chdir("../coordinator")
        subprocess.run([sys.executable, "app.py"])
    
    coord_thread = threading.Thread(target=start_coordinator, daemon=True)
    coord_thread.start()
    time.sleep(3)
    
    # Vérifier
    try:
        response = requests.get(f"{coordinator_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Coordinateur démarré")
        else:
            print("❌ Erreur coordinateur")
            return
    except:
        print("❌ Impossible de contacter le coordinateur")
        return
    
    # Étape 2: Démarrer des workers
    print_step(2, "Démarrage des workers")
    
    def start_worker(name):
        os.chdir("../worker-agent")
        subprocess.run([sys.executable, "worker.py", "--name", name])
    
    worker_names = ["Worker-Alpha", "Worker-Beta", "Worker-Gamma"]
    
    for i, name in enumerate(worker_names[:2]):  # Démarrer 2 workers
        worker_thread = threading.Thread(
            target=start_worker,
            args=(name,),
            daemon=True
        )
        worker_thread.start()
        print(f"✅ {name} démarré")
        time.sleep(1)
    
    # Étape 3: Démarrer le dashboard
    print_step(3, "Démarrage du dashboard")
    
    def start_dashboard():
        os.chdir("../dashboard")
        subprocess.run(["streamlit", "run", "app.py", "--server.headless", "true"])
    
    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    dashboard_thread.start()
    time.sleep(5)
    
    print(f"✅ Dashboard disponible sur {dashboard_url}")
    
    # Étape 4: Soumettre des tâches de démonstration
    print_step(4, "Soumission des tâches de démonstration")
    
    demo_tasks = [
        {
            "name": "Calcul Mathématique Avancé",
            "command": "python3 -c \"import math; print(f'π ≈ {math.pi:.10f}')\"",
            "type": "shell"
        },
        {
            "name": "Analyse de Texte",
            "command": "echo 'apple banana apple orange banana' | tr ' ' '\\n' | sort | uniq -c",
            "type": "shell"
        },
        {
            "name": "Benchmark Système",
            "command": "echo 'CPU Cores:' && nproc && echo 'Memory:' && free -h",
            "type": "shell"
        },
        {
            "name": "Génération Hash",
            "command": "echo 'BI-Compute Network Demo' | sha256sum",
            "type": "shell"
        }
    ]
    
    submitted_tasks = []
    
    for task in demo_tasks:
        try:
            response = requests.post(
                f"{coordinator_url}/api/tasks",
                json={
                    "name": task["name"],
                    "type": task["type"],
                    "command": {
                        "type": "shell",
                        "command": task["command"]
                    }
                },
                timeout=10
            )
            
            if response.status_code == 201:
                task_id = response.json().get("task_id")
                submitted_tasks.append({"id": task_id, "name": task["name"]})
                print(f"✅ {task['name']}")
            else:
                print(f"❌ {task['name']} - Erreur")
                
        except Exception as e:
            print(f"❌ {task['name']} - {e}")
    
    # Étape 5: Surveiller l'exécution
    print_step(5, "Surveillance de l'exécution")
    print("\n⏳ Les tâches sont en cours d'exécution...")
    print("Les workers traitent les tâches en parallèle")
    print("\nProgression:")
    
    completed_count = 0
    start_time = time.time()
    timeout = 120  # 2 minutes max
    
    while completed_count < len(submitted_tasks) and (time.time() - start_time) < timeout:
        # Afficher le statut
        try:
            response = requests.get(f"{coordinator_url}/api/network/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                completed = stats.get('performance', {}).get('tasks_completed', 0)
                
                progress = (completed / len(submitted_tasks)) * 100
                print(f"  📊 {progress:.0f}% - {completed}/{len(submitted_tasks)} tâches complétées")
                
                if completed > completed_count:
                    completed_count = completed
                    
        except:
            pass
        
        time.sleep(5)
    
    # Étape 6: Afficher les résultats
    print_step(6, "Résultats finaux")
    
    try:
        response = requests.get(f"{coordinator_url}/api/network/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            
            print("\n" + "-" * 40)
            print("📈 STATISTIQUES FINALES")
            print("-" * 40)
            print(f"Workers actifs: {stats['workers']['total_active']}")
            print(f"CPU totaux: {stats['workers']['total_cpu_cores']} cœurs")
            print(f"Tâches complétées: {stats['performance']['tasks_completed']}")
            print(f"Tâches en attente: {stats['performance']['tasks_pending']}")
            print(f"Taux de réussite: {(completed_count/len(submitted_tasks)*100):.1f}%")
    except Exception as e:
        print(f"Erreur stats: {e}")
    
    # Étape 7: Conclusion
    print_step(7, "Démonstration terminée")
    
    print("\n" + "=" * 60)
    print("🎉 DÉMONSTRATION RÉUSSIE!")
    print("=" * 60)
    
    print("\n📋 Résumé:")
    print(f"  • Tâches soumises: {len(submitted_tasks)}")
    print(f"  • Tâches complétées: {completed_count}")
    print(f"  • Workers utilisés: 2")
    print(f"  • Temps total: {time.time() - start_time:.1f}s")
    
    print("\n🔗 Services actifs:")
    print(f"  • Coordinateur: {coordinator_url}")
    print(f"  • Dashboard: {dashboard_url}")
    
    print("\n💡 Commandes utiles:")
    print("  python ../cli/compute_cli.py stats")
    print("  streamlit run ../dashboard/app.py")
    
    print("\n" + "=" * 60)
    print("Prêt pour la présentation du hackathon! 🚀")
    print("=" * 60)
    
    # Garder les services en cours d'exécution
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Arrêt de la démonstration")

if __name__ == "__main__":
    run_demo()