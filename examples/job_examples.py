#!/usr/bin/env python3
"""
Exemples de jobs pour la démonstration
"""

import requests
import time
import json

COORDINATOR_URL = "http://localhost:5000"

def submit_example_jobs():
    """Soumettre des jobs de démonstration"""
    
    examples = [
        {
            "name": "Job 1: Calcul simple",
            "command": "echo 'Résultat: $(( 5 * 20 ))'"
        },
        {
            "name": "Job 2: Hash d'un fichier",
            "command": "echo 'test content' > test.txt && sha256sum test.txt && rm test.txt"
        },
        {
            "name": "Job 3: Traitement Python",
            "command": {
                "type": "python",
                "code": """
import hashlib
text = "Hello Decentralized World"
hash_obj = hashlib.sha256(text.encode())
print(f"Texte: {text}")
print(f"SHA256: {hash_obj.hexdigest()}")
"""
            }
        },
        {
            "name": "Job 4: Word count",
            "command": "echo 'apple banana apple orange banana apple' | tr ' ' '\\n' | sort | uniq -c"
        }
    ]
    
    submitted_jobs = []
    
    for example in examples:
        print(f"\n📤 Soumission: {example['name']}")
        
        if isinstance(example['command'], str):
            job_data = {
                "type": "shell",
                "command": {
                    "type": "shell",
                    "command": example['command']
                }
            }
        else:
            job_data = {
                "type": "python",
                "command": example['command']
            }
        
        try:
            response = requests.post(
                f"{COORDINATOR_URL}/api/jobs",
                json=job_data,
                timeout=10
            )
            
            if response.status_code == 200:
                job_id = response.json().get('job_id')
                print(f"✅ Soumis - Job ID: {job_id}")
                submitted_jobs.append(job_id)
            else:
                print(f"❌ Échec: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    return submitted_jobs

def monitor_jobs(job_ids):
    """Surveiller l'exécution des jobs"""
    print("\n👀 Surveillance des jobs...")
    
    completed = []
    
    while len(completed) < len(job_ids):
        for job_id in job_ids:
            if job_id in completed:
                continue
            
            try:
                response = requests.get(
                    f"{COORDINATOR_URL}/api/jobs/{job_id}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status')
                    
                    if status == 'completed':
                        print(f"✅ Job {job_id} terminé")
                        result = data.get('result')
                        if result:
                            result_data = json.loads(result)
                            if result_data.get('stdout'):
                                print(f"   Sortie: {result_data['stdout'][:100]}...")
                        completed.append(job_id)
                    elif status == 'failed':
                        print(f"❌ Job {job_id} échoué")
                        completed.append(job_id)
                    else:
                        print(f"⏳ Job {job_id}: {status}")
            
            except Exception as e:
                print(f"⚠️ Erreur vérification {job_id}: {e}")
        
        if len(completed) < len(job_ids):
            time.sleep(3)
    
    print("\n🎉 Tous les jobs sont terminés!")

if __name__ == "__main__":
    print("🧪 Démonstration du système de computing distribué")
    print("=" * 50)
    
    # Soumettre les jobs
    job_ids = submit_example_jobs()
    
    if job_ids:
        # Surveiller l'exécution
        monitor_jobs(job_ids)
    else:
        print("❌ Aucun job soumis")
