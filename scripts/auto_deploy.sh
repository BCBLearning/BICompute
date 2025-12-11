#!/bin/bash

# Script de déploiement automatique pour Railway
# BesmaInfo © 2025 - Hackathon LabLab AI

echo "🚀 SCRIPT DE DÉPLOIEMENT BI-COMPUTE HACKATHON"
echo "=============================================="
echo ""

# Vérifications
echo "🔍 Vérifications préliminaires..."
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    exit 1
fi

echo "✅ Toutes les vérifications passées"
echo ""

# Instructions pour Railway
echo "📋 INSTRUCTIONS POUR RAILWAY:"
echo ""
echo "1. Allez sur https://railway.app"
echo "2. Connectez-vous avec GitHub"
echo "3. Cliquez 'New Project' → 'Deploy from GitHub repo'"
echo "4. Autorisez Railway à accéder à votre compte GitHub"
echo "5. Sélectionnez votre dépôt 'BICompute'"
echo "6. Railway détectera automatiquement la configuration"
echo "7. Attendez 2-3 minutes pour le déploiement"
echo "8. Cliquez sur l'URL générée"
echo ""

# Instructions pour GitHub
echo "📋 INSTRUCTIONS POUR GITHUB:"
echo ""
echo "1. Assurez-vous que tous les fichiers sont dans le dossier BICompute/"
echo "2. Git add ."
echo "3. Git commit -m 'Déploiement hackathon'"
echo "4. Git push origin main"
echo ""

echo "🎉 Votre application sera en ligne en quelques minutes !"
echo ""
echo "🔗 Liens utiles:"
echo "   - Dashboard Railway: https://railway.app"
echo "   - Documentation: docs/DEMO_GUIDE.md"
echo "   - CLI: python cli/compute_cli.py --help"
echo ""
echo "🤖 Bonne chance pour le hackathon !"