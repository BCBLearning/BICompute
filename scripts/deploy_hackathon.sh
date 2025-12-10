#!/bin/bash

echo "🚀 SCRIPT DE DÉPLOIEMENT POUR HACKATHON 🚀"
echo "=========================================="

# Créer la structure
echo "1. Création de la structure du projet..."
mkdir -p ~/bi-compute-hackathon
cd ~/bi-compute-hackathon

# Copier tous les fichiers
echo "2. Copie des fichiers..."
# Note: Vous devrez copier manuellement les fichiers depuis votre appareil
# ou les télécharger depuis GitHub

echo "3. Installation des dépendances..."
python3 -m venv venv
source venv/bin/activate

pip install flask flask-cors requests streamlit pandas

echo "4. Configuration terminée!"
echo ""
echo "📁 Structure créée:"
echo "  ~/bi-compute-hackathon/"
echo "  ├── coordinator/"
echo "  ├── worker-agent/"
echo "  ├── cli/"
echo "  ├── dashboard/"
echo "  └── scripts/"
echo ""
echo "🚀 Pour démarrer:"
echo "  cd ~/bi-compute-hackathon"
echo "  source venv/bin/activate"
echo "  python scripts/final_demo.py"