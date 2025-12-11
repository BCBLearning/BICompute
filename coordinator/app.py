#!/usr/bin/env python3
"""
BI-COMPUTE COORDINATOR + DASHBOARD
Version hackathon - BesmaInfo © 2025
"""

from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
import os
import sys
import json
import logging
import random
import string
from flask_cors import CORS

# ==================== CONFIGURATION ====================

app = Flask(__name__)
CORS(app)

# Clé secrète pour sessions
app.secret_key = os.environ.get("SECRET_KEY", "".join(random.choices(string.ascii_letters + string.digits, k=32)))

# Configuration Railway
IS_RAILWAY = os.environ.get("RAILWAY_ENVIRONMENT") is not None
PORT = int(os.environ.get("PORT", 5000))

# Base de données - différent pour Railway
if IS_RAILWAY:
    DB_FILE = "/tmp/coordinator.db"
    DATA_DIR = "/tmp"
else:
    DB_FILE = "coordinator.db"
    DATA_DIR = "."

# S'assurer que le dossier existe
os.makedirs(DATA_DIR, exist_ok=True)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(DATA_DIR, 'coordinator.log'))
    ]
)
logger = logging.getLogger(__name__)

# ==================== BASE DE DONNÉES ====================

def init_db():
    """Initialiser la base de données avec les tables"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Table workers
        c.execute('''
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cpu_cores INTEGER DEFAULT 1,
                memory_mb INTEGER DEFAULT 1024,
                platform TEXT,
                last_seen TEXT,
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                tasks_completed INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Table tasks
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT DEFAULT 'shell',
                command TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                result_output TEXT,
                result_error TEXT,
                assigned_worker TEXT
            )
        ''')
        
        # Table pour les démos
        c.execute('''
            CREATE TABLE IF NOT EXISTS demos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                worker_count INTEGER DEFAULT 0,
                task_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Ajouter des tâches de démo si la table est vide
        add_demo_data()
        
        logger.info(f"✅ Base de données initialisée: {DB_FILE}")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation DB: {e}")
        raise

def add_demo_data():
    """Ajouter des données de démonstration"""
    demo_tasks = [
        {
            "name": "🧮 Calcul de π (Monte Carlo)",
            "type": "python",
            "command": json.dumps({
                "type": "python",
                "command": """import random, math, time\nprint("Calcul de π avec méthode Monte Carlo")\npoints = 100000\ninside = 0\nfor i in range(points):\n    x, y = random.random(), random.random()\n    if x*x + y*y <= 1:\n        inside += 1\npi_estimate = 4 * inside / points\nerror = abs(math.pi - pi_estimate)\nprint(f"π ≈ {pi_estimate:.6f}")\nprint(f"Erreur: {error:.6f}")\nprint(f"Points calculés: {points}")"""
            })
        },
        {
            "name": "📊 Analyse de texte distribué",
            "type": "shell",
            "command": json.dumps({
                "type": "shell",
                "command": """echo "BI-Compute Hackathon 2024: Computing for the People by the People Distributed Edge Network AI ML Cloud" | tr ' ' '\\n' | sort | uniq -c | sort -nr"""
            })
        },
        {
            "name": "🔐 Hash cryptographique",
            "type": "shell",
            "command": json.dumps({
                "type": "shell",
                "command": """echo "Secure distributed computing platform" | sha256sum"""
            })
        },
        {
            "name": "⚡ Performance benchmark",
            "type": "python",
            "command": json.dumps({
                "type": "python",
                "command": """import time, math\nprint("Benchmark de performance CPU")\nstart = time.time()\nresult = 0\nfor i in range(1, 1000001):\n    result += 1/(i*i)\npi_approx = math.sqrt(result * 6)\nexec_time = time.time() - start\nprint(f"π approximé: {pi_approx:.10f}")\nprint(f"Temps d'exécution: {exec_time:.3f} secondes")\nprint(f"Performance: {1000000/exec_time:.0f} itérations/sec")"""
            })
        }
    ]
    
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Vérifier si on a déjà des tâches
        c.execute("SELECT COUNT(*) FROM tasks")
        count = c.fetchone()[0]
        
        if count == 0:
            logger.info("📝 Ajout des tâches de démo...")
            for task in demo_tasks:
                c.execute(
                    """INSERT INTO tasks (name, type, command, status) 
                       VALUES (?, ?, ?, 'pending')""",
                    (task["name"], task["type"], task["command"])
                )
            
            # Ajouter une démo
            c.execute(
                """INSERT INTO demos (name, description, worker_count, task_count) 
                   VALUES (?, ?, ?, ?)""",
                ("Hackathon 2024", "Démo BI-Compute pour le hackathon", 0, len(demo_tasks))
            )
            
            conn.commit()
            logger.info(f"✅ {len(demo_tasks)} tâches de démo ajoutées")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Erreur ajout données démo: {e}")

# Initialiser la DB
init_db()

# ==================== FONCTIONS UTILITAIRES ====================

def get_db_connection():
    """Obtenir une connexion à la base de données"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_worker_stats():
    """Obtenir les statistiques des workers"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Workers actifs (dernières 2 minutes)
    active_timeout = datetime.now() - timedelta(minutes=2)
    c.execute("""
        SELECT COUNT(*) as active_workers,
               SUM(cpu_cores) as total_cpu,
               SUM(memory_mb) as total_memory
        FROM workers 
        WHERE last_seen > ? AND is_active = 1
    """, (active_timeout.isoformat(),))
    
    stats = c.fetchone()
    conn.close()
    
    return {
        "active_workers": stats["active_workers"] or 0,
        "total_cpu": stats["total_cpu"] or 0,
        "total_memory": stats["total_memory"] or 0
    }

def get_task_stats():
    """Obtenir les statistiques des tâches"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
    completed_tasks = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
    pending_tasks = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM tasks WHERE status = 'failed'")
    failed_tasks = c.fetchone()[0]
    
    conn.close()
    
    return {
        "total": total_tasks,
        "completed": completed_tasks,
        "pending": pending_tasks,
        "failed": failed_tasks
    }

# ==================== ROUTES DASHBOARD ====================

@app.route("/")
def dashboard():
    """Dashboard principal"""
    try:
        # Statistiques
        worker_stats = get_worker_stats()
        task_stats = get_task_stats()
        
        # Calculer le taux de complétion
        completion_rate = 0
        if task_stats["total"] > 0:
            completion_rate = round(task_stats["completed"] / task_stats["total"] * 100, 1)
        
        # Récupérer les workers récents
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT name, platform, last_seen, tasks_completed
            FROM workers 
            WHERE is_active = 1
            ORDER BY last_seen DESC 
            LIMIT 10
        """)
        recent_workers = [dict(row) for row in c.fetchall()]
        
        # Récupérer les tâches récentes
        c.execute("""
            SELECT id, name, status, created_at, assigned_worker
            FROM tasks 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_tasks = [dict(row) for row in c.fetchall()]
        
        conn.close()
        
        # Générer l'URL du coordinateur
        if IS_RAILWAY:
            coordinator_url = f"https://{request.host}"
        else:
            coordinator_url = f"http://{request.host}"
        
        return render_template("index.html",
            active_workers=worker_stats["active_workers"],
            total_cpu=worker_stats["total_cpu"],
            total_memory=worker_stats["total_memory"],
            total_tasks=task_stats["total"],
            completed_tasks=task_stats["completed"],
            pending_tasks=task_stats["pending"],
            failed_tasks=task_stats["failed"],
            completion_rate=completion_rate,
            recent_workers=recent_workers,
            recent_tasks=recent_tasks,
            coordinator_url=coordinator_url,
            is_railway=IS_RAILWAY,
            current_time=datetime.now().strftime("%H:%M:%S")
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur dashboard: {e}")
        return render_template("error.html", error=str(e))

@app.route("/submit", methods=["POST"])
def submit_task():
    """Soumettre une nouvelle tâche depuis le dashboard"""
    try:
        name = request.form.get("name", "Nouvelle tâche")
        task_type = request.form.get("type", "shell")
        command = request.form.get("command", "")
        
        if not name or not command:
            flash("❌ Nom et commande sont requis", "danger")
            return redirect(url_for("dashboard"))
        
        # Créer l'objet commande
        command_obj = {"type": task_type, "command": command}
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute(
            """INSERT INTO tasks (name, type, command, status) 
               VALUES (?, ?, ?, 'pending')""",
            (name, task_type, json.dumps(command_obj))
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Tâche soumise: {name}")
        flash("✅ Tâche soumise avec succès !", "success")
        
    except Exception as e:
        logger.error(f"❌ Erreur soumission tâche: {e}")
        flash(f"❌ Erreur: {str(e)}", "danger")
    
    return redirect(url_for("dashboard"))

# ==================== ROUTES API ====================

@app.route("/api/health")
def api_health():
    """Endpoint de santé de l'API"""
    return jsonify({
        "service": "BI-COMPUTE Hackathon Demo",
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": "railway" if IS_RAILWAY else "development",
        "database": "connected",
        "url": f"https://{request.host}" if IS_RAILWAY else f"http://{request.host}",
        "endpoints": {
            "workers": "/api/workers",
            "tasks": "/api/tasks",
            "stats": "/api/stats",
            "demo": "/api/demo"
        }
    })

@app.route("/api/workers/register", methods=["POST"])
def api_register_worker():
    """Enregistrer un nouveau worker"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Données JSON requises"}), 400
        
        name = data.get("name", f"Worker-{datetime.now().strftime('%H%M%S')}")
        cpu_cores = data.get("cpu_cores", 1)
        memory_mb = data.get("memory_mb", 1024)
        platform = data.get("platform", "unknown")
        
        now = datetime.now().isoformat()
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Vérifier si le worker existe déjà
        c.execute(
            "SELECT id FROM workers WHERE name = ? AND is_active = 1",
            (name,)
        )
        existing = c.fetchone()
        
        if existing:
            # Mettre à jour le worker existant
            worker_id = existing['id']
            c.execute(
                """UPDATE workers SET 
                    cpu_cores = ?, 
                    memory_mb = ?, 
                    platform = ?, 
                    last_seen = ?,
                    is_active = 1
                   WHERE id = ?""",
                (cpu_cores, memory_mb, platform, now, worker_id)
            )
            action = "updated"
        else:
            # Créer un nouveau worker
            c.execute(
                """INSERT INTO workers 
                   (name, cpu_cores, memory_mb, platform, last_seen, is_active)
                   VALUES (?, ?, ?, ?, ?, 1)""",
                (name, cpu_cores, memory_mb, platform, now)
            )
            worker_id = c.lastrowid
            action = "registered"
        
        conn.commit()
        conn.close()
        
        logger.info(f"👷 Worker {action}: {name} (ID: {worker_id})")
        
        return jsonify({
            "worker_id": worker_id,
            "name": name,
            "action": action,
            "message": f"Worker {action} successfully"
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur registration worker: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    """Créer une nouvelle tâche via API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Données JSON requises"}), 400
        
        name = data.get("name", f"Task-{datetime.now().strftime('%H%M%S')}")
        task_type = data.get("type", "shell")
        command = data.get("command", "")
        
        # Si command est un dict, le convertir en JSON
        if isinstance(command, dict):
            command = json.dumps(command)
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute(
            """INSERT INTO tasks (name, type, command, status, created_at)
               VALUES (?, ?, ?, 'pending', ?)""",
            (name, task_type, command, datetime.now().isoformat())
        )
        
        task_id = c.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"📝 Tâche créée: {name} (ID: {task_id})")
        
        return jsonify({
            "task_id": task_id,
            "name": name,
            "type": task_type,
            "status": "pending",
            "message": "Task created successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Erreur création tâche: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/available")
def api_available_tasks():
    """Récupérer les tâches disponibles pour les workers"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT id, name, type, command, created_at
            FROM tasks 
            WHERE status = 'pending'
            ORDER BY created_at ASC 
            LIMIT 10
        """)
        
        tasks = []
        for row in c.fetchall():
            tasks.append({
                "task_id": row['id'],
                "name": row['name'],
                "type": row['type'],
                "command": row['command'],
                "created_at": row['created_at']
            })
        
        conn.close()
        
        return jsonify({
            "available_tasks": tasks,
            "count": len(tasks)
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération tâches: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/<int:task_id>/results", methods=["POST"])
def api_submit_result(task_id):
    """Soumettre le résultat d'une tâche"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Données JSON requises"}), 400
        
        worker_id = data.get("worker_id")
        result = data.get("result", {})
        
        success = result.get("success", False)
        output = result.get("stdout", "")
        error = result.get("stderr", "") or result.get("error", "")
        
        now = datetime.now().isoformat()
        status = "completed" if success else "failed"
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Mettre à jour la tâche
        c.execute(
            """UPDATE tasks SET 
                status = ?,
                completed_at = ?,
                result_output = ?,
                result_error = ?,
                assigned_worker = ?
               WHERE id = ?""",
            (status, now, output, error, worker_id, task_id)
        )
        
        # Mettre à jour le compteur du worker
        if worker_id and success:
            c.execute(
                "UPDATE workers SET tasks_completed = tasks_completed + 1, last_seen = ? WHERE id = ?",
                (now, worker_id)
            )
        
        conn.commit()
        conn.close()
        
        logger.info(f"📤 Résultat soumis pour tâche {task_id} (succès: {success})")
        
        return jsonify({
            "task_id": task_id,
            "status": status,
            "message": "Result submitted successfully"
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur soumission résultat: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats")
def api_stats():
    """Récupérer les statistiques du réseau"""
    try:
        worker_stats = get_worker_stats()
        task_stats = get_task_stats()
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Calculer le taux de complétion
        completion_rate = 0
        if task_stats["total"] > 0:
            completion_rate = round(task_stats["completed"] / task_stats["total"] * 100, 2)
        
        conn.close()
        
        return jsonify({
            "network": {
                "name": "BI-COMPUTE Hackathon Network",
                "environment": "railway" if IS_RAILWAY else "development",
                "coordinator_url": f"https://{request.host}" if IS_RAILWAY else f"http://{request.host}",
                "timestamp": datetime.now().isoformat()
            },
            "workers": {
                "active": worker_stats["active_workers"],
                "total_cpu": worker_stats["total_cpu"],
                "total_memory_mb": worker_stats["total_memory"],
                "total_memory_gb": round(worker_stats["total_memory"] / 1024, 1)
            },
            "tasks": task_stats,
            "performance": {
                "completion_rate": completion_rate,
                "tasks_per_worker": round(task_stats["completed"] / max(worker_stats["active_workers"], 1), 1),
                "uptime": "100%"  # Simplifié pour la démo
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur statistiques: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/demo/reset", methods=["POST"])
def api_reset_demo():
    """Réinitialiser la démo pour les jurys"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Supprimer toutes les tâches et workers
        c.execute("DELETE FROM tasks")
        c.execute("DELETE FROM workers")
        c.execute("DELETE FROM demos")
        
        # Réinitialiser les séquences
        c.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
        c.execute("DELETE FROM sqlite_sequence WHERE name='workers'")
        c.execute("DELETE FROM sqlite_sequence WHERE name='demos'")
        
        # Recréer les données de démo
        add_demo_data()
        
        conn.commit()
        conn.close()
        
        logger.info("🔄 Démo réinitialisée pour les jurys")
        
        return jsonify({
            "success": True,
            "message": "Demo reset successfully",
            "tasks_added": 4
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur réinitialisation démo: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/demo/start", methods=["POST"])
def api_start_demo():
    """Démarrer une démo automatique"""
    try:
        data = request.get_json() or {}
        worker_count = data.get("workers", 3)
        
        # Créer des workers fictifs pour la démo
        conn = get_db_connection()
        c = conn.cursor()
        
        platforms = ["linux", "windows", "macos", "android", "termux"]
        
        for i in range(worker_count):
            name = f"Demo-Worker-{i+1}"
            platform = random.choice(platforms)
            cpu = random.randint(1, 8)
            memory = random.choice([1024, 2048, 4096, 8192])
            
            c.execute(
                """INSERT INTO workers (name, cpu_cores, memory_mb, platform, last_seen, is_active)
                   VALUES (?, ?, ?, ?, ?, 1)""",
                (name, cpu, memory, platform, datetime.now().isoformat())
            )
        
        conn.commit()
        conn.close()
        
        logger.info(f"🎬 Démo démarrée avec {worker_count} workers")
        
        return jsonify({
            "success": True,
            "message": f"Demo started with {worker_count} workers",
            "worker_count": worker_count
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur démarrage démo: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== ROUTES UTILITAIRES ====================

@app.route("/api/workers")
def api_list_workers():
    """Lister tous les workers"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT * FROM workers 
            ORDER BY last_seen DESC
        """)
        
        workers = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify({
            "workers": workers,
            "count": len(workers)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/all")
def api_list_tasks():
    """Lister toutes les tâches"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT * FROM tasks 
            ORDER BY created_at DESC
        """)
        
        tasks = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify({
            "tasks": tasks,
            "count": len(tasks)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/worker")
def download_worker():
    """Télécharger le script worker"""
    worker_script = """#!/usr/bin/env python3
# BI-COMPUTE Worker pour Hackathon
import requests, time, subprocess, json, sys

coordinator_url = "{{ coordinator_url }}"

def main():
    print("🚀 BI-COMPUTE Worker - Hackathon Demo")
    print(f"📡 Connexion à: {coordinator_url}")
    
    # Enregistrement
    worker_data = {
        "name": f"Worker-{time.strftime('%H%M%S')}",
        "cpu_cores": 4,
        "memory_mb": 8192,
        "platform": "hackathon-demo"
    }
    
    try:
        r = requests.post(f"{coordinator_url}/api/workers/register", 
                         json=worker_data, timeout=10)
        if r.status_code == 200:
            worker_id = r.json()["worker_id"]
            print(f"✅ Enregistré (ID: {worker_id})")
            
            # Boucle de travail
            while True:
                # Récupérer les tâches
                tasks = requests.get(f"{coordinator_url}/api/tasks/available").json()
                
                for task in tasks.get("available_tasks", []):
                    print(f"🔧 Exécution: {task['name']}")
                    
                    # Simuler l'exécution
                    time.sleep(2)
                    
                    # Soumettre le résultat
                    result = {
                        "success": True,
                        "stdout": f"Tâche {task['task_id']} exécutée avec succès!",
                        "stderr": ""
                    }
                    
                    requests.post(f"{coordinator_url}/api/tasks/{task['task_id']}/results",
                                 json={"worker_id": worker_id, "result": result})
                
                time.sleep(5)
                
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
"""
    
    # Remplacer l'URL du coordinateur
    if IS_RAILWAY:
        url = f"https://{request.host}"
    else:
        url = f"http://{request.host}"
    
    worker_script = worker_script.replace("{{ coordinator_url }}", url)
    
    return worker_script, 200, {
        'Content-Type': 'application/x-python',
        'Content-Disposition': 'attachment; filename=bi_compute_worker.py'
    }

# ==================== GESTION D'ERREURS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint non trouvé"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"❌ Erreur interne: {error}")
    return jsonify({"error": "Erreur interne du serveur"}), 500

# ==================== DÉMARRAGE ====================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 BI-COMPUTE HACKATHON DEMO")
    logger.info(f"🌐 Environnement: {'RAILWAY' if IS_RAILWAY else 'DEVELOPMENT'}")
    logger.info(f"🔌 Port: {PORT}")
    logger.info(f"💾 Base de données: {DB_FILE}")
    logger.info("=" * 60)
    
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=not IS_RAILWAY,
        threaded=True
    )