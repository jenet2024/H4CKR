# H4CKR - Escape Game de Cybersécurité

Une application web immersive et élégante pour un escape game de cybersécurité avec style cyberpunk, animations fluides et gameplay interactif.

## 🎮 Fonctionnalités

### 🎨 Frontend React
- **Page d'accueil cyberpunk** : Design élégant avec effets glitch, scanlines et grille néon
- **Authentification JWT** : Connexion et inscription avec formulaires animés
- **Écran de jeu interactif** : Affichage des énigmes, saisie des réponses, barre de progression
- **Terminal expert** : Interface CLI hacker avec historique scrollable et exécution de commandes
- **Système d'indices** : Indices avec compteur et pénalité de points visible en temps réel
- **Badges et certificats** : Récompenses animées pour chaque niveau complété
- **Leaderboard** : Classement des joueurs avec statistiques
- **Sélection de niveaux** : 3 niveaux (Débutant, Intermédiaire, Expert) avec accès progressif

### 🔧 Backend FastAPI
- **API REST complète** : Endpoints pour authentification, jeu, terminal, leaderboard
- **Documentation Swagger** : API auto-documentée et testable à `/api/docs`
- **Authentification JWT** : Tokens sécurisés avec expiration configurable
- **Base de données SQLite** : Modèles pour utilisateurs, énigmes, scores, badges
- **Système de progression** : Déblocage conditionnel des niveaux
- **Seed de données** : Script d'initialisation avec énigmes et badges

### 🐳 Déploiement
- **Dockerfile** : Conteneurisation du backend FastAPI
- **docker-compose.yml** : Orchestration complète (backend + frontend)
- **Configuration CORS** : Prêt pour le déploiement en production

## 🚀 Démarrage rapide

### Prérequis
- Node.js 18+ (pour le frontend)
- Python 3.11+ (pour le backend)
- Docker & Docker Compose (optionnel, pour déploiement)

### Installation et démarrage local

#### 1. Backend FastAPI

```bash
cd backend
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Le backend sera accessible à `http://localhost:8000`
Documentation Swagger : `http://localhost:8000/api/docs`

#### 2. Frontend React

```bash
cd ..
pnpm install
pnpm dev
```

Le frontend sera accessible à `http://localhost:5173`

### Avec Docker Compose

```bash
docker-compose up
```

Cela démarrera :
- Backend FastAPI : `http://localhost:8000`
- Frontend React : `http://localhost:5173`

## 📁 Structure du projet

```
h4ckr_webapp/
├── backend/                    # Backend FastAPI
│   ├── main.py                # Application principale
│   ├── config.py              # Configuration
│   ├── models.py              # Modèles SQLAlchemy
│   ├── schemas.py             # Schémas Pydantic
│   ├── database.py            # Configuration BD
│   ├── auth.py                # Authentification JWT
│   ├── routes_auth.py         # Routes d'authentification
│   ├── routes_game.py         # Routes du jeu
│   ├── seed.py                # Script d'initialisation
│   ├── requirements.txt        # Dépendances Python
│   ├── Dockerfile             # Configuration Docker
│   └── README.md              # Documentation backend
│
├── client/                     # Frontend React
│   ├── src/
│   │   ├── pages/             # Pages React
│   │   │   ├── Landing.tsx    # Page d'accueil
│   │   │   ├── Login.tsx      # Connexion
│   │   │   ├── Register.tsx   # Inscription
│   │   │   ├── Dashboard.tsx  # Tableau de bord
│   │   │   ├── Game.tsx       # Écran de jeu
│   │   │   ├── Leaderboard.tsx # Leaderboard
│   │   │   └── Completion.tsx # Certificat
│   │   ├── lib/
│   │   │   └── api.ts         # Client API
│   │   ├── styles/
│   │   │   └── cyberpunk.css  # Styles cyberpunk
│   │   └── App.tsx            # Routeur principal
│   ├── package.json           # Dépendances Node
│   └── vite.config.ts         # Configuration Vite
│
├── docker-compose.yml         # Orchestration Docker
└── README.md                  # Ce fichier
```

## 🎯 Endpoints API

### Authentification
- `POST /api/auth/register` - Enregistrer un nouvel utilisateur
- `POST /api/auth/login` - Connecter un utilisateur
- `GET /api/auth/me` - Récupérer l'utilisateur actuel
- `POST /api/auth/logout` - Déconnecter l'utilisateur

### Jeu
- `GET /api/levels` - Récupérer tous les niveaux
- `GET /api/levels/{level_id}` - Récupérer un niveau spécifique
- `POST /api/enigmas/{enigma_id}/submit` - Soumettre une réponse
- `GET /api/enigmas/{enigma_id}/hint` - Récupérer un indice
- `POST /api/terminal/command` - Exécuter une commande terminal
- `GET /api/leaderboard` - Récupérer le leaderboard
- `GET /api/user/progress` - Récupérer la progression de l'utilisateur

## 🎨 Design et Animations

### Effets Cyberpunk
- **Glitch** : Effet de texte glitchant avec décalages de couleur
- **Scanlines** : Lignes horizontales animées pour effet CRT
- **Grille Néon** : Grille de fond avec teinte verte
- **Néon Glow** : Texte et bordures avec effet de lueur
- **Transitions fluides** : Animations de slide, fade et scale

### Palette de couleurs
- Primaire (Vert) : `#00ff88`
- Secondaire (Rose) : `#ff006e`
- Tertiaire (Cyan) : `#00d9ff`
- Fond sombre : `#0a0e27`
- Surface : `#1a1f3a`

## 🔐 Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification. Le token est stocké en `localStorage` côté client et envoyé dans le header `Authorization: Bearer <token>` pour chaque requête protégée.

## 📊 Base de données

La base de données SQLite contient les tables suivantes :
- `users` - Utilisateurs
- `levels` - Niveaux de jeu
- `enigmas` - Énigmes
- `enigma_attempts` - Tentatives de résolution
- `scores` - Scores des utilisateurs
- `badges` - Badges disponibles
- `user_badges` - Badges gagnés
- `certificates` - Certificats de completion

## 🚀 Déploiement en production

### Variables d'environnement

**Backend** (`.env`) :
```env
DEBUG=false
JWT_SECRET=your-strong-secret-key
DATABASE_URL=sqlite:///./h4ckr.db
FRONTEND_URL=https://your-domain.com
```

**Frontend** (`.env.local`) :
```env
VITE_API_URL=https://api.your-domain.com
```

### Avec Docker
```bash
docker-compose -f docker-compose.yml up -d
```

### Avec Kubernetes
Adaptez les fichiers YAML selon votre infrastructure.

## 🧪 Tests

### Backend
```bash
cd backend
pytest tests/
```

### Frontend
```bash
pnpm test
```

## 📝 Notes de développement

- Les mots de passe sont hashés avec bcrypt
- Les tokens JWT expirent après 24 heures (configurable)
- CORS est configuré pour accepter les requêtes du frontend
- La base de données est initialisée automatiquement au démarrage
- Les énigmes et badges sont seedés via `seed.py`

## 🤝 Contribution

Les contributions sont bienvenues! Veuillez :
1. Fork le projet
2. Créer une branche pour votre feature
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

MIT License - Voir LICENSE pour plus de détails

## 📞 Support

Pour les questions ou problèmes :
- Consultez la documentation FastAPI : https://fastapi.tiangolo.com/
- Consultez la documentation React : https://react.dev/
- Ouvrez une issue sur le repository

---

**Prêt à relever le défi? Commencez votre aventure H4CKR! 🎮**
