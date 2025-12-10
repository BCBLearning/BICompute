#!/usr/bin/env python3
"""
Script de déploiement sur Railway.app
"""
import os
import subprocess
import sys

def check_requirements():
    """Vérifier les prérequis"""
    print("🔍 Vérification des prérequis...")
    
    # Vérifier Railway CLI
    try:
        subprocess.run(["railway", "--version"], 
                      capture_output=True, check=True)
        print("✅ Railway CLI installé")
    except:
        print("❌ Railway CLI non installé")
        print("Installez-le: npm install -g @railway/cli")
        return False
    
    # Vérifier la connexion
    try:
        subprocess.run(["railway", "whoami"], 
                      capture_output=True, check=True)
        print("✅ Connecté à Railway")
    except:
        print("❌ Non connecté à Railway")
        print("Connectez-vous: railway login")
        return False
    
    return True

def deploy_to_railway():
    """Déployer sur Railway"""
    print("\n🚀 Déploiement sur Railway...")
    
    # Aller dans le dossier coordinateur
    os.chdir("../coordinator")
    
    # Initialiser Railway
    print("1. Initialisation Railway...")
    subprocess.run(["railway", "init"], check=True)
    
    # Déployer
    print("2. Déploiement en cours...")
    result = subprocess.run(["railway", "up"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Déploiement réussi!")
        
        # Obtenir l'URL
        print("3. Obtention de l'URL...")
        url_result = subprocess.run(["railway", "url"], 
                                   capture_output=True, text=True)
        
        if url_result.returncode == 0:
            url = url_result.stdout.strip()
            print(f"🌐 Votre application est disponible sur: {url}")
            
            # Créer un fichier avec l'URL
            with open("../DEPLOYMENT_INFO.txt", "w") as f:
                f.write(f"BI-COMPUTE sur Railway\n")
                f.write(f"URL: {url}\n")
                f.write(f"\nPour tester:\n")
                f.write(f"curl {url}/api/health\n")
            
            print("📄 Information sauvegardée dans DEPLOYMENT_INFO.txt")
        else:
            print("⚠️ Impossible d'obtenir l'URL")
            print("Vérifiez manuellement: railway url")
    
    else:
        print("❌ Échec du déploiement")
        print("Erreur:", result.stderr)
    
    return result.returncode == 0

def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("DÉPLOIEMENT BI-COMPUTE SUR RAILWAY.APP")
    print("=" * 60)
    
    if not check_requirements():
        sys.exit(1)
    
    print("\n📋 Ce script va:")
    print("1. Déployer le coordinateur sur Railway")
    print("2. Configurer automatiquement l'application")
    print("3. Vous fournir l'URL de déploiement")
    
    confirm = input("\nContinuer? (o/N): ").strip().lower()
    
    if confirm != 'o':
        print("❌ Annulé")
        sys.exit(0)
    
    if deploy_to_railway():
        print("\n" + "=" * 60)
        print("🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!")
        print("=" * 60)
        print("\nVotre application BI-Compute est maintenant en ligne!")
        print("\nProchaines étapes:")
        print("1. Testez l'API avec curl")
        print("2. Configurez les variables d'environnement si nécessaire")
        print("3. Partagez l'URL avec votre équipe")
    else:
        print("\n❌ Le déploiement a échoué")
        print("Consultez les logs pour plus d'informations")

if __name__ == "__main__":
    main()