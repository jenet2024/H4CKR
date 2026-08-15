# H4CKR — Escape Game Cybersécurité

Application web full-stack (React + FastAPI + MySQL), déployée via Docker.  
**Plus de `.exe` — tout tourne dans le navigateur.**

---
## 📸 Aperçu du projet

![Auth](screenshots/auth.png)
![Cesar](screenshots/cesar.png)
![Imge](screenshots/imge_suspecte.png)
![Log](screenshots/log.png)
![Ssh](screenshots/ssh.png)

## Architecture

```
h4ckr/
├── docker-compose.yml          ← Orchestre les 3 services
├── .env.example                ← Variables d'environnement (à copier en .env)
├── backend/                    ← FastAPI + SQLAlchemy
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── auth/                   ← /auth/register, /auth/login, /auth/me...
│   ├── game/                   ← /game/levels, /game/answer, /game/terminal...
│   ├── models/
│   └── database/
└── frontend/                   ← React + Vite
    ├── Dockerfile
    ├── nginx.conf              ← Sert le build + SPA routing
    ├── src/
    │   ├── api/client.ts       ← Tous les appels vers le backend
    │   ├── hooks/useAuth.tsx   ← Contexte d'authentification
    │   ├── pages/
    │   │   ├── AuthPage.tsx    ← Connexion/inscription (animée)
    │   │   └── GamePage.tsx    ← Le jeu complet
    │   └── App.tsx
    └── package.json
```

---

## Lancement rapide (Docker)

```bash
# 1. Copiez les variables d'environnement
cp .env.example .env
# Editez .env selon votre configuration

# 2. Lancez tout
docker-compose up --build -d

# Frontend → http://localhost
# Backend  → http://localhost:8000
# API docs → http://localhost:8000/docs
```

---


## Développement local (sans Docker)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt



# Créez un .env ou exportez les variables :
export DATABASE_URL="mysql+pymysql://root:root@localhost:3306/h4ckr_game"
export SECRET_KEY="dev_secret_key"
export FRONTEND_URL="http://localhost:5173"

uvicorn main:app --reload --port 8000
```




### Frontend
```bash
cd frontend
npm install
# Créez un .env.local :
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
# → http://localhost:5173
```

---
![Swagger](screenshots/swagger.png)

## Variables d'environnement importantes

| Variable | Description |
|---|---|
| `DATABASE_URL` | URL MySQL (auto-configuré en Docker) |
| `SECRET_KEY` | Clé JWT (changez en production !) |
| `FRONTEND_URL` | URL du frontend (pour CORS) |
| `VITE_API_URL` | URL du backend vu par le navigateur |
| `GOOGLE_CLIENT_ID` | OAuth Google (optionnel) |
| `TWITTER_CLIENT_ID` | OAuth Twitter (optionnel) |

---

## Déploiement en production

1. Mettez à jour `.env` avec vos vrais domaines
2. Changez `SECRET_KEY` pour une clé aléatoire forte (32+ chars)
3. Configurez votre reverse proxy (Nginx, Traefik...) devant les containers
4. `docker-compose up -d --build`

**API Swagger** disponible sur `/docs` pour tester tous les endpoints.

---

## Endpoints API principaux

### Auth
- `POST /auth/register` — Inscription
- `POST /auth/login` — Connexion (retourne JWT)
- `GET  /auth/me` — Profil utilisateur
- `POST /auth/refresh` — Rafraîchit le token
- `GET  /auth/google` — OAuth Google
- `GET  /auth/twitter` — OAuth Twitter

### Jeu
- `GET  /game/levels` — Tous les niveaux + progression
- `POST /game/answer` — Soumettre une réponse
- `POST /game/hint/{id}` — Demander un indice
- `POST /game/terminal` — Terminal interactif
- `GET  /game/leaderboard` — Classement
- `GET  /game/my-badges` — Mes badges
- `POST /game/certificate/{slug}` — Générer certificat PDF

![Certif](screenshots/certif.png)

