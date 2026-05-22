from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager

from config import get_settings
from database.db import init_db
from auth.router import router as auth_router
from game.router import router as game_router
from admin.router import router as admin_router   # ← NOUVEAU

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Démarrage {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    yield
    print("🛑 Arrêt du serveur")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(game_router)
app.include_router(admin_router)   # ← NOUVEAU

# Static assets
assets_path = Path(settings.ASSETS_DIR)
assets_path.mkdir(parents=True, exist_ok=True)
(assets_path / "videos").mkdir(exist_ok=True)
(assets_path / "enigmas").mkdir(exist_ok=True)
(assets_path / "certificates").mkdir(exist_ok=True)
(assets_path / "badges").mkdir(exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")


@app.get("/", tags=["Health"])
def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}