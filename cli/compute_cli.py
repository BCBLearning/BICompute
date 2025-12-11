#!/usr/bin/env python3
"""
BI-COMPUTE CLI - Interface en ligne de commande
BesmaInfo © 2025 - Hackathon LabLab AI
"""

import argparse
import requests
import json
import sys
from datetime import datetime

class BICLI:
    """Interface CLI pour BI-COMPUTE"""
    
    VERSION = "2.0.0"
    
    def __init__(self, url="http://localhost:5000"):
        self.url = url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"BI-CLI/{self.VERSION}",
            "Accept": "application/json"
        })
    
    def health(self):
        """Vérifier la santé du coordinateur"""
        try:
            response = self.session.get(f"{self.url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ BI-COMPUTE COORDINATOR")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Environment: {data.get('environment', 'unknown')}")
                print(f"   URL: {self.url}")
                return True
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Impossible de se connecter à {self.url}")
            return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def submit(self, command, name=None, task_type="shell"):
        """Soumettre une nouvelle tâche"""
        if not name:
            name = f"CLI Task {datetime.now().strftime('%H:%M:%S')}"
        
        # Si la commande commence par @, lire depuis un fichier
        if command.startswith("@"):
            try:
                filename = command[1:]
                with open(filename, 'r') as f:
                    command_content = f.read()
                
                if filename.endswith('.py'):
                    task_type = "python"
                    command_obj = {
                        "type": "python",
                        "command": command_content
                    }
                else:
                    task_type = "shell"
                    command_obj = {
                        "type": "shell",
                        "command": command_content
                    }
            except FileNotFoundError:
                print(f"❌ Fichier non trouvé: {command[1:]}")
                return False
        else:
            if task_type == "python":
                command_obj = {
                    "type": "python",
                    "command": command
                }
            else:
                command_obj = {
                    "type": "shell",
                    "command": command
                }
        
        payload = {
            "name": name,
            "type": task_type,
            "command": command_obj
        }
        
        try:
            response = self.session.post(
                f"{self.url}/api/tasks",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Tâche soumise avec succès")
                print(f"   ID: {data.get('task_id')}")
                print(f"   Nom: {data.get('name')}")
                print(f"   Status: {data.get('status')}")
                return True
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def stats(self):
        """Afficher les statistiques du réseau"""
        try:
            response = self.session.get(f"{self.url}/api/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                print("📊 STATISTIQUES BI-COMPUTE")
                print("=" * 50)
                
                # Informations réseau
                network = data.get("network", {})
                print(f"🌐 Réseau: {network.get('name', 'BI-COMPUTE')}")
                print(f"   Environnement: {network.get('environment', 'unknown')}")
                print(f"   URL: {network.get('coordinator_url', self.url)}")
                print(f"   Timestamp: {network.get('timestamp', 'N/A')}")
                
                # Workers
                workers = data.get("workers", {})
                print(f"\n👷 WORKERS")
                print(f"   Actifs: {workers.get('active', 0)}")
                print(f"   CPU totaux: {workers.get('total_cpu', 0)} cœurs")
                print(f"   Mémoire: {workers.get('total_memory_mb', 0)} MB "
                      f"({workers.get('total_memory_gb', 0)} GB)")
                
                # Tâches
                tasks = data.get("tasks", {})
                print(f"\n📋 TÂCHES")
                print(f"   Total: {tasks.get('total', 0)}")
                print(f"   Terminées: {tasks.get('completed', 0)}")
                print(f"   En attente: {tasks.get('pending', 0)}")
                print(f"   Échouées: {tasks.get('failed', 0)}")
                
                # Performance
                perf = data.get("performance", {})
                print(f"\n⚡ PERFORMANCE")
                print(f"   Taux de complétion: {perf.get('completion_rate', 0)}%")
                print(f"   Tâches/worker: {perf.get('tasks_per_worker', 0)}")
                print(f"   Uptime: {perf.get('uptime', '100%')}")
                
                return True
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def status(self, task_id):
        """Vérifier le statut d'une tâche"""
        try:
            response = self.session.get(f"{self.url}/api/tasks/{task_id}", timeout=5)
            if response.status_code == 200:
                task = response.json()
                
                print(f"📋 TÂCHE #{task_id}")
                print("=" * 30)
                
                print(f"Nom: {task.get('name', 'N/A')}")
                print(f"Type: {task.get('type', 'N/A')}")
                print(f"Status: {task.get('status', 'N/A')}")
                print(f"Créée: {task.get('created_at', 'N/A')}")
                
                if task.get('completed_at'):
                    print(f"Terminée: {task.get('completed_at')}")
                
                if task.get('result_output'):
                    print(f"\n📤 OUTPUT:")
                    output = task.get('result_output', '')
                    if len(output) > 500:
                        print(output[:500] + "...")
                    else:
                        print(output)
                
                if task.get('result_error'):
                    print(f"\n❌ ERREUR:")
                    error = task.get('result_error', '')
                    if len(error) > 500:
                        print(error[:500] + "...")
                    else:
                        print(error)
                
                return True
            elif response.status_code == 404:
                print(f"❌ Tâche #{task_id} non trouvée")
                return False
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def workers(self):
        """Lister tous les workers"""
        try:
            response = self.session.get(f"{self.url}/api/workers", timeout=5)
            if response.status_code == 200:
                data = response.json()
                workers = data.get("workers", [])
                
                print(f"👷 WORKERS ({len(workers)} total)")
                print("=" * 60)
                
                for worker in workers:
                    name = worker.get('name', 'Unknown')
                    platform = worker.get('platform', 'Unknown')
                    last_seen = worker.get('last_seen', 'Never')
                    completed = worker.get('tasks_completed', 0)
                    active = "✅" if worker.get('is_active') else "❌"
                    
                    print(f"{active} {name}")
                    print(f"   Platform: {platform}")
                    print(f"   Tâches complétées: {completed}")
                    print(f"   Dernière activité: {last_seen}")
                    print()
                
                return True
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def demo(self, action="start"):
        """Gérer les démos"""
        if action == "start":
            try:
                response = self.session.post(
                    f"{self.url}/api/demo/start",
                    json={"workers": 3},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Démo démarrée avec {data.get('worker_count')} workers")
                    return True
                else:
                    print(f"❌ HTTP {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ Erreur: {e}")
                return False
        
        elif action == "reset":
            try:
                response = self.session.post(
                    f"{self.url}/api/demo/reset",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Démo réinitialisée")
                    print(f"   Tâches ajoutées: {data.get('tasks_added', 0)}")
                    return True
                else:
                    print(f"❌ HTTP {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ Erreur: {e}")
                return False
        
        else:
            print(f"❌ Action inconnue: {action}")
            return False
    
    def tasks(self):
        """Lister toutes les tâches"""
        try:
            response = self.session.get(f"{self.url}/api/tasks/all", timeout=5)
            if response.status_code == 200:
                data = response.json()
                tasks = data.get("tasks", [])
                
                print(f"📋 TÂCHES ({len(tasks)} total)")
                print("=" * 70)
                
                for task in tasks[:10]:  # Limiter à 10 pour l'affichage
                    task_id = task.get('id', '?')
                    name = task.get('name', 'Unknown')
                    status = task.get('status', 'unknown')
                    created = task.get('created_at', 'N/A')
                    
                    # Symboles de statut
                    if status == 'completed':
                        status_icon = '✅'
                    elif status == 'pending':
                        status_icon = '⏳'
                    elif status == 'failed':
                        status_icon = '❌'
                    else:
                        status_icon = '❓'
                    
                    print(f"{status_icon} #{task_id}: {name}")
                    print(f"   Status: {status}")
                    print(f"   Créée: {created}")
                    
                    if task.get('assigned_worker'):
                        print(f"   Worker: {task.get('assigned_worker')}")
                    
                    if task.get('execution_time'):
                        print(f"   Temps: {task.get('execution_time')}s")
                    
                    print()
                
                if len(tasks) > 10:
                    print(f"... et {len(tasks) - 10} autres tâches")
                
                return True
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="BI-COMPUTE CLI - Interface en ligne de commande",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s health
  %(prog)s --url https://bi-compute.railway.app stats
  %(prog)s submit "echo Hello World" --name "Test Task"
  %(prog)s submit @script.py --type python
  %(prog)s status 123
  %(prog)s workers
  %(prog)s demo start
  %(prog)s demo reset
        """
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:5000",
        help="URL du coordinateur (défaut: http://localhost:5000)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"BI-COMPUTE CLI v{BICLI.VERSION} - BesmaInfo © 2025"
    )
    
    # Sous-commandes
    subparsers = parser.add_subparsers(
        dest="command",
        help="Commande à exécuter"
    )
    
    # Health
    subparsers.add_parser(
        "health",
        help="Vérifier la santé du coordinateur"
    )
    
    # Stats
    subparsers.add_parser(
        "stats",
        help="Afficher les statistiques du réseau"
    )
    
    # Submit
    submit_parser = subparsers.add_parser(
        "submit",
        help="Soumettre une nouvelle tâche"
    )
    submit_parser.add_argument(
        "command",
        help="Commande à exécuter ou fichier (préfixé avec @)"
    )
    submit_parser.add_argument(
        "--name",
        help="Nom de la tâche"
    )
    submit_parser.add_argument(
        "--type",
        choices=["shell", "python"],
        default="shell",
        help="Type de tâche (défaut: shell)"
    )
    
    # Status
    status_parser = subparsers.add_parser(
        "status",
        help="Vérifier le statut d'une tâche"
    )
    status_parser.add_argument(
        "task_id",
        type=int,
        help="ID de la tâche"
    )
    
    # Workers
    subparsers.add_parser(
        "workers",
        help="Lister tous les workers"
    )
    
    # Tasks
    subparsers.add_parser(
        "tasks",
        help="Lister toutes les tâches"
    )
    
    # Demo
    demo_parser = subparsers.add_parser(
        "demo",
        help="Gérer les démonstrations"
    )
    demo_parser.add_argument(
        "action",
        choices=["start", "reset"],
        help="Action à effectuer"
    )
    
    # Analyser les arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialiser le CLI
    cli = BICLI(args.url)
    
    # Exécuter la commande
    if args.command == "health":
        cli.health()
    elif args.command == "stats":
        cli.stats()
    elif args.command == "submit":
        cli.submit(args.command, args.name, args.type)
    elif args.command == "status":
        cli.status(args.task_id)
    elif args.command == "workers":
        cli.workers()
    elif args.command == "tasks":
        cli.tasks()
    elif args.command == "demo":
        cli.demo(args.action)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()