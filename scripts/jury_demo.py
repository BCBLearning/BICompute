#!/usr/bin/env python3
"""
Script de démonstration pour les jurys du hackathon
BesmaInfo © 2025 - Hackathon LabLab AI
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

COORDINATOR_URL = os.getenv("COORDINATOR_URL", "https://bi-compute.railway.app")

def print_step(step, message):
    """Afficher une étape de la démo"""
    print(f"\n{step}. {message}")
    print("   " + "-" * 40)

def jury_demo():
    """Démo pour les jurys"""
    print("=" * 70)
    print("🎬 DÉMO BI-COMPUTE POUR LES JURYS")
    print("=" * 70)
    
    # Étape 1: Présentation
    print_step("1", "Présentation du projet")
    print("   BI-COMPUTE: Computing distribué pour le peuple")
    print("   Hackathon: 'Compute for the People, by the People'")
    print(f"   URL: {COORDINATOR_URL}")
    time.sleep(2)
    
    # Étape 2: Vérification API
    print_step("2", "Vérification de l'API")
    try:
        health = requests.get(f"{COORDINATOR_URL}/api/health", timeout=10).json()
        print(f"   ✅ Service: {health['service']}")
        print(f"   ✅ Status: {health['status']}")
        print(f"   ✅ Version: {health['version']}")
    except:
        print("   ❌ API inaccessible")
        return
    time.sleep(2)
    
    # Étape 3: Démarrer un worker
    print_step("3", "Démarrage d'un worker de démo")
    print("   Enregistrement d'un worker...")
    
    worker_data = {
        "name": f"Jury-Demo-{datetime.now().strftime('%H%M%S')}",
        "cpu_cores": 8,
        "memory_mb": 16384,
        "platform": "jury-demo-system"
    }
    
    try:
        worker_resp = requests.post(
            f"{COORDINATOR_URL}/api/workers/register",
            json=worker_data
        )
        
        if worker_resp.status_code == 200:
            worker_id = worker_resp.json()["worker_id"]
            print(f"   ✅ Worker démarré (ID: {worker_id})")
    except Exception as e:
        print(f"   ⚠️ Erreur: {e}")
    time.sleep(2)
    
    # Étape 4: Soumettre une tâche
    print_step("4", "Soumission d'une tâche de démo")
    
    task_data = {
        "name": "🧠 Calcul IA: Training distribué simulé",
        "type": "python",
        "command": {
            "type": "python",
            "command": """import time, random\nprint("=== SIMULATION TRAINING IA DISTRIBUÉ ===\\n")\n\n# Simulation d'un training distribué\nepochs = 10\nfor epoch in range(epochs):\n    accuracy = 0.7 + epoch * 0.03 + random.uniform(-0.02, 0.02)\n    loss = 0.5 - epoch * 0.04 + random.uniform(-0.01, 0.01)\n    \n    print(f"Epoch {epoch+1}/{epochs}")\n    print(f"  Accuracy: {accuracy:.4f}")\n    print(f"  Loss:     {loss:.4f}")\n    print(f"  Workers:  {random.randint(3, 8)}")\n    print(f"  Time:     {random.uniform(0.5, 2.0):.2f}s\\n")\n    \n    time.sleep(0.5)\n\nprint("✅ Training terminé avec succès!")\nprint(f"Final Accuracy: {accuracy:.4f}")\nprint("Modèle prêt pour le déploiement")"""
        }
    }
    
    try:
        task_resp = requests.post(
            f"{COORDINATOR_URL}/api/tasks",
            json=task_data
        )
        
        if task_resp.status_code == 201:
            task_id = task_resp.json()["task_id"]
            print(f"   ✅ Tâche soumise (ID: {task_id})")
            print("   🤖 Un worker va l'exécuter automatiquement")
    except Exception as e:
        print(f"   ⚠️ Erreur: {e}")
    time.sleep(2)
    
    # Étape 5: Voir les stats
    print_step("5", "Statistiques en temps réel")
    
    for i in range(5):
        try:
            stats = requests.get(f"{COORDINATOR_URL}/api/stats").json()
            
            print(f"   Mise à jour {i+1}:")
            print(f"     Workers actifs: {stats['workers']['active']}")
            print(f"     Tâches totales: {stats['tasks']['total']}")
            print(f"     Tâches terminées: {stats['tasks']['completed']}")
            print(f"     Taux: {stats['performance']['completion_rate']}%")
            
        except:
            print("   ⚠️ Impossible de récupérer les stats")
        
        time.sleep(3)
    
    # Étape 6: Conclusion
    print_step("6", "Points clés à retenir")
    print("   ✅ Architecture distribuée et scalable")
    print("   ✅ Multi-plateforme (PC, Mobile, Serveur)")
    print("   ✅ Hébergement cloud gratuit (Railway)")
    print("   ✅ Code open-source et extensible")
    print("   ✅ Réel impact démocratique")
    
    print("\n" + "=" * 70)
    print("🎉 DÉMO TERMINÉE - QUESTIONS DES JURYS")
    print("=" * 70)
    print(f"\n📊 Dashboard: {COORDINATOR_URL}")
    print("📱 Les jurys peuvent participer:")
    print("   1. Ouvrir le dashboard sur leur téléphone")
    print("   2. Démarrer un worker sur leur machine")
    print("   3. Soumettre leurs propres tâches")

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = COORDINATOR_URL
    
    try:
        jury_demo()
    except KeyboardInterrupt:
        print("\n👋 Démo interrompue")

if __name__ == "__main__":
    main()