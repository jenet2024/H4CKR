import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Chemins ───────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "src" / "assets"
VIDEO_DIR  = ASSETS_DIR / "videos"
ENIGMA_DIR = ASSETS_DIR / "enigmas"
AUDIO_DIR  = ASSETS_DIR / "audio"
IMAGE_DIR  = ASSETS_DIR / "images"

# ── API ───────────────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ── OAuth ─────────────────────────────────────────────────────────────────────
# Google OAuth 2.0 — https://console.cloud.google.com/
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI  = "http://localhost:8765/callback/google"

# Twitter/X OAuth 2.0 — https://developer.twitter.com/en/portal/dashboard
TWITTER_CLIENT_ID     = os.getenv("TWITTER_CLIENT_ID", "YOUR_TWITTER_CLIENT_ID")
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET", "YOUR_TWITTER_CLIENT_SECRET")
TWITTER_REDIRECT_URI  = "http://localhost:8765/callback/twitter"

# ── Fenêtre ───────────────────────────────────────────────────────────────────
WINDOW_W   = 1280
WINDOW_H   = 760
FPS        = 60
TITLE      = "H4CKR — Hacking Simulation Game"

# ── Couleurs ──────────────────────────────────────────────────────────────────
C_BG        = (6,   11,  6)
C_BG2       = (10,  20,  10)
C_GREEN     = (57,  255, 20)
C_GREEN_DIM = (30,  100, 15)
C_GREEN_MID = (40,  150, 40)
C_RED       = (255, 0,   60)
C_YELLOW    = (255, 220, 0)
C_CYAN      = (0,   200, 255)
C_WHITE     = (200, 245, 200)
C_GRAY      = (80,  120, 80)
C_DARK      = (15,  30,  15)
C_BORDER    = (30,  60,  30)
C_GOLD      = (255, 215, 0)
C_ORANGE    = (255, 140, 0)

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_MONO = "Courier New"
