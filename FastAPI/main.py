from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
# from dotenv import load_dotenv
# load_dotenv()  # Charge les variables d'environnement depuis .env

from config import get_settings
from database.db import init_db
from auth.router import router as auth_router
from game.router import router as game_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise la DB et seed les données au démarrage."""
    print(f"🚀 Démarrage {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()

    # Seed automatique si la DB est vide
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


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend du jeu H4CKR — Escape Game cybersécurité",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(game_router)

# ── Static assets ─────────────────────────────────────────────────────────────

assets_path = Path(settings.ASSETS_DIR)
assets_path.mkdir(parents=True, exist_ok=True)
(assets_path / "videos").mkdir(exist_ok=True)
(assets_path / "enigmas").mkdir(exist_ok=True)
(assets_path / "certificates").mkdir(exist_ok=True)

app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

# ── Health check ──────────────────────────────────────────────────────────────

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
