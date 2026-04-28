# H4CKR — Jeu de Simulation de Hacking

Jeu Python / Pygame éducatif sur la cybersécurité.
Résolvez des énigmes pour progresser dans deux niveaux : Débutant et Expert.

## Architecture

```
h4ckr_game/
├── main.py                        ← Point d'entrée — machine d'états
├── config.py                      ← Constantes globales (couleurs, chemins, OAuth)
├── build.spec                     ← Config PyInstaller pour générer le .exe
├── requirements.txt
├── generate_assets.py             ← Génère les fichiers d'énigmes de démonstration
├── .env                           ← Clés API (à remplir)
└── src/
    ├── constants.py               ← Données des 16 énigmes complètes
    ├── screens/
    │   ├── auth_screen.py         ← Login / Inscription / OAuth Google & Twitter
    │   ├── menu_screen.py         ← Menu principal (carte joueur, badges, stats)
    │   ├── game_screen.py         ← Jeu (énigmes, terminal expert, popup midpoint)
    │   └── leaderboard_screen.py  ← Classement, Guide, Contact, Certificat
    ├── utils/
    │   ├── renderer.py            ← Composants UI pygame
    │   ├── api.py                 ← Client HTTP FastAPI
    │   ├── oauth.py               ← Serveur OAuth local
    │   └── robot_video.py         ← Robot animé + voix pyttsx3
    └── assets/
        ├── enigmas/               ← Fichiers d'énigmes (PNG, WAV, TXT)
        ├── audio/
        ├── images/
        └── certificates/
```

## Démarrage rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Générer les fichiers d'énigmes
python generate_assets.py

# 3. Démarrer le backend (dans /backend)
uvicorn main:app --reload --port 8000

# 4. Lancer le jeu
python main.py
```

## Générer le .exe

```bash
pyinstaller build.spec
# → dist/H4CKR.exe
```

## Clés OAuth

Éditez `.env` avec vos clés :
- Google : https://console.cloud.google.com → Credentials → OAuth 2.0
  Redirect URI : http://localhost:8765/callback/google
- Twitter : https://developer.twitter.com → Your App → OAuth 2.0
  Callback URI : http://localhost:8765/callback/twitter
