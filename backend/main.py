from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager

from auth.security import decode_token
from config import get_settings
from database.db import init_db
from auth.router import router as auth_router
from game.router import router as game_router

settings = get_settings()


# ───────────────────────────────────────────────────────────────────────────────
# LIFESPAN
# ───────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Démarrage {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()

    from database.db import SessionLocal
    from models.level import Level

    db = SessionLocal()
    if db.query(Level).count() == 0:
        print("📦 Base vide détectée — lancement du seeder...")
        from database.seeder import seed
        seed()
    db.close()

    print("✅ Serveur prêt")
    yield
    print("🛑 Arrêt du serveur")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend du jeu H4CKR — Escape Game cybersécurité",
    lifespan=lifespan,
)


# ───────────────────────────────────────────────────────────────────────────────
# MIDDLEWARE D’AUTHENTIFICATION
# ───────────────────────────────────────────────────────────────────────────────

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    # Endpoints publics
    PUBLIC_PATHS = [
        "/auth/login",
        "/auth/register",
        "/docs",
        "/openapi.json",
    ]

    # 🔓 Certificat VISIBLE sans auth
    if path.startswith("/game/certificate/view"):
        return await call_next(request)

    # 🔓 Certificat TÉLÉCHARGEABLE sans auth
    if path.startswith("/game/certificate/download"):
        return await call_next(request)

    # 🔓 Assets statiques
    if path.startswith("/assets"):
        return await call_next(request)

    # 🔓 Endpoints publics
    if any(path.startswith(p) for p in PUBLIC_PATHS):
        return await call_next(request)

    # 🔐 Vérification JWT obligatoire pour le reste
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]
    decode_token(token)

    return await call_next(request)


# ───────────────────────────────────────────────────────────────────────────────
# CORS
# ───────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:80",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ───────────────────────────────────────────────────────────────────────────────
# ROUTERS
# ───────────────────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(game_router)


# ───────────────────────────────────────────────────────────────────────────────
# STATIC ASSETS
# ───────────────────────────────────────────────────────────────────────────────

assets_path = Path(settings.ASSETS_DIR)
assets_path.mkdir(parents=True, exist_ok=True)
(assets_path / "videos").mkdir(exist_ok=True)
(assets_path / "enigmas").mkdir(exist_ok=True)
(assets_path / "certificates").mkdir(exist_ok=True)
(assets_path / "badges").mkdir(exist_ok=True)

print("📁 ASSETS_DIR =", assets_path.resolve())

app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")


# ───────────────────────────────────────────────────────────────────────────────
# HEALTHCHECK
# ───────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
