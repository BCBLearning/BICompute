#!/usr/bin/env python3
"""
Point d'entrée Railway pour BI-COMPUTE Hackathon Demo
BesmaInfo © 2025 - Hackathon LabLab AI
"""

import os
import sys

# Ajouter le répertoire courant au chemin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    print("=" * 60)
    print("🚀 BI-COMPUTE HACKATHON DEMO - RAILWAY DEPLOYMENT")
    print(f"🌐 Port: {port}")
    print(f"🔗 URL: https://{os.environ.get('RAILWAY_STATIC_URL', 'localhost:' + str(port))}")
    print("=" * 60)
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        threaded=True
    )