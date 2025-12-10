# 🖥️ BI-COMPUTE
## Réseau de Computing Distribué

### 🎯 Description
BI-Compute est une plateforme de computing distribué qui permet d'exécuter des tâches sur un réseau de machines volontaires. Développé pour le hackathon "Compute for the People, by the People".

### 🚀 Installation Rapide

```bash
# 1. Cloner le projet
git clone https://github.com/BesmaInfo/BI-Compute.git
cd BI-Compute

# 2. Installer les dépendances
pip install -r coordinator/requirements.txt
pip install -r worker-agent/requirements.txt
pip install -r cli/requirements.txt
pip install -r dashboard/requirements.txt

# 3. Lancer la démo
python scripts/final_demo.py