"""
Constantes globales du jeu H4CKR.
"""
import os
from pathlib import Path

# ── Résolution ────────────────────────────────────────────────────────────────
SCREEN_W = 1280
SCREEN_H = 720
FPS      = 60
TITLE    = "H4CKR — Hacking Simulation Game"

# ── Chemins ───────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR   = BASE_DIR / "data"

IMG_DIR   = ASSETS_DIR / "images"
AUDIO_DIR = ASSETS_DIR / "audio"
VIDEO_DIR = ASSETS_DIR / "videos"
ENIG_DIR  = ASSETS_DIR / "enigmas"
CERT_DIR  = ASSETS_DIR / "certificates"
BADGE_DIR = ASSETS_DIR / "badges"
FONT_DIR  = ASSETS_DIR / "fonts"

# ── API Backend ───────────────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://localhost:8000")

# ── OAuth URLs ────────────────────────────────────────────────────────────────
GOOGLE_AUTH_URL  = f"{API_URL}/auth/google"
TWITTER_AUTH_URL = f"{API_URL}/auth/twitter"

# ── Palette cyberpunk ─────────────────────────────────────────────────────────
BLACK       = (0,   0,   0)
DARK_BG     = (6,   11,  6)
DARK_BG2    = (10,  20,  10)
CARD_BG     = (12,  22,  12)
GREEN       = (57,  255, 20)
GREEN_DIM   = (30,  120, 10)
GREEN_DARK  = (15,  50,  5)
GREEN_GLOW  = (57,  255, 20, 80)
CYAN        = (0,   255, 255)
RED         = (255, 0,   60)
YELLOW      = (255, 255, 0)
ORANGE      = (255, 153, 0)
WHITE       = (255, 255, 255)
GRAY        = (100, 130, 100)
GRAY_DARK   = (40,  60,  40)
BORDER      = (30,  60,  30)
BORDER_GLOW = (57,  255, 20)
PURPLE      = (150, 0,   255)
PINK        = (255, 0,   180)

# ── Tailles de police ─────────────────────────────────────────────────────────
FONT_XS  = 12
FONT_SM  = 14
FONT_MD  = 18
FONT_LG  = 24
FONT_XL  = 32
FONT_XXL = 48
FONT_BIG = 72

# ── États de l'application ────────────────────────────────────────────────────
class State:
    SPLASH       = "splash"
    AUTH         = "auth"
    MENU         = "menu"
    LEVEL_SELECT = "level_select"
    INTRO_VIDEO  = "intro_video"
    GAME         = "game"
    TERMINAL     = "terminal"
    LEADERBOARD  = "leaderboard"
    GUIDE        = "guide"
    CONTACT      = "contact"
    CERTIFICATE  = "certificate"
    BADGE_ANIM   = "badge_anim"

# ── Niveaux ───────────────────────────────────────────────────────────────────
LEVELS = {
    "beginner": {
        "slug":       "beginner",
        "name":       "DÉBUTANT",
        "color":      GREEN,
        "steps":      10,
        "mid_badge":  5,
        "max_points": 1000,
        "video_intro":  "level1_intro.mp4",
        "video_mid":    "level1_mid.mp4",
        "video_end":    "level1_end.mp4",
    },
    "expert": {
        "slug":       "expert",
        "name":       "EXPERT",
        "color":      RED,
        "steps":      6,
        "mid_badge":  None,
        "max_points": 2000,
        "video_intro": "level2_intro.mp4",
        "video_end":   "level2_end.mp4",
    },
}

# ── Enigmes — données complètes ───────────────────────────────────────────────
ENIGMAS_BEGINNER = [
    # ── Étapes 1–5 (faciles) ──────────────────────────────────────────────────
    {
        "id": 1, "level": "beginner", "order": 1,
        "title": "Base64 — Premier Décodage",
        "story": (
            "Agent, vous avez intercepté ce message encodé en transit.\n"
            "Décodez-le pour révéler le mot de passe caché."
        ),
        "type": "base64",
        "content": "SGVsbG8gQWdlbnQgISBNb3QgZGUgcGFzc2UgOiBBTFBIQQ==",
        "answer": "ALPHA",
        "hint1": "Base64 utilise les caractères A-Z, a-z, 0-9, +, /",
        "hint2": "Cherchez un décodeur en ligne ou utilisez Python.",
        "hint3": "Le mot de passe est ALPHA",
        "points": 80,
        "file": None,
    },
    {
        "id": 2, "level": "beginner", "order": 2,
        "title": "César — Le Chiffre Antique",
        "story": (
            "Un message a été chiffré avec le chiffre de César (décalage 3).\n"
            "KDFFHU est le message chiffré. Déchiffrez-le."
        ),
        "type": "caesar",
        "content": "KDFFHU",
        "answer": "HACKER",
        "hint1": "Dans le chiffre de César, chaque lettre est décalée dans l'alphabet.",
        "hint2": "Avec un décalage de 3 : K→H, D→A, F→C...",
        "hint3": "La réponse est HACKER",
        "points": 80,
        "file": None,
    },
    {
        "id": 3, "level": "beginner", "order": 3,
        "title": "Stéganographie — Image Suspecte",
        "story": (
            "Un agent a caché un mot de passe dans cette image.\n"
            "Examinez les métadonnées du fichier 'mission_01.png'."
        ),
        "type": "stegano",
        "content": "Téléchargez et analysez l'image 'mission_01.png'.",
        "answer": "GHOST",
        "hint1": "Les images contiennent des données EXIF invisibles.",
        "hint2": "Le mot est caché dans le champ 'Comment' des métadonnées.",
        "hint3": "Le mot caché est GHOST",
        "points": 100,
        "file": "mission_01.png",
    },
    {
        "id": 4, "level": "beginner", "order": 4,
        "title": "Binaire — Langage Machine",
        "story": (
            "Ce message a été converti en binaire par l'ennemi.\n"
            "01001011 01000101 01011001\n"
            "Convertissez-le en texte lisible."
        ),
        "type": "binary",
        "content": "01001011 01000101 01011001",
        "answer": "KEY",
        "hint1": "Chaque groupe de 8 bits représente un caractère ASCII.",
        "hint2": "01001011 = 75 en décimal = 'K' en ASCII",
        "hint3": "Le mot est KEY",
        "points": 100,
        "file": None,
    },
    {
        "id": 5, "level": "beginner", "order": 5,
        "title": "Audio — Signal Caché",
        "story": (
            "Un message a été enregistré puis inversé dans ce fichier audio.\n"
            "Écoutez 'signal_01.wav' et identifiez le mot prononcé à l'envers."
        ),
        "type": "audio",
        "content": "Écoutez le fichier audio 'signal_01.wav'.",
        "answer": "CYBER",
        "hint1": "Importez le fichier dans Audacity et inversez la piste.",
        "hint2": "Le mot est court — 5 lettres.",
        "hint3": "Le mot est CYBER",
        "points": 120,
        "file": "signal_01.wav",
    },
    # ── Étapes 6–10 (intermédiaires) ──────────────────────────────────────────
    {
        "id": 6, "level": "beginner", "order": 6,
        "title": "Hex — Codes Hexadécimaux",
        "story": (
            "Ce code hexadécimal cache un mot clé.\n"
            "48 41 43 4B\n"
            "Convertissez chaque valeur hex en caractère ASCII."
        ),
        "type": "hex",
        "content": "48 41 43 4B",
        "answer": "HACK",
        "hint1": "En hexadécimal, 48 = 72 en décimal.",
        "hint2": "ASCII : 72='H', 65='A', 67='C', 75='K'",
        "hint3": "Le mot est HACK",
        "points": 120,
        "file": None,
    },
    {
        "id": 7, "level": "beginner", "order": 7,
        "title": "ROT13 — Double César",
        "story": (
            "Ce fichier texte contient un message encodé en ROT13.\n"
            "Analysez 'data_07.txt' et décodez le message."
        ),
        "type": "rot13",
        "content": "FRPHER",
        "answer": "SECURE",
        "hint1": "ROT13 décale chaque lettre de 13 positions.",
        "hint2": "F→S, E→R, P→C, U→H, R→E, E→R",
        "hint3": "La réponse est SECURE",
        "points": 130,
        "file": "data_07.txt",
    },
    {
        "id": 8, "level": "beginner", "order": 8,
        "title": "Métadonnées Audio",
        "story": (
            "Un fichier audio a été envoyé avec des métadonnées suspectes.\n"
            "Analysez les tags ID3 de 'audio_08.mp3' pour trouver le titre caché."
        ),
        "type": "audio_meta",
        "content": "Analysez les métadonnées de 'audio_08.mp3'.",
        "answer": "FIREWALL",
        "hint1": "Les fichiers MP3 contiennent des tags ID3 (titre, artiste, commentaire).",
        "hint2": "Le mot est dans le champ 'Commentaire' du fichier.",
        "hint3": "Le mot est FIREWALL",
        "points": 130,
        "file": "audio_08.mp3",
    },
    {
        "id": 9, "level": "beginner", "order": 9,
        "title": "XOR — Chiffrement Binaire",
        "story": (
            "Ce message a été chiffré avec une opération XOR avec la clé 42.\n"
            "Valeurs ASCII chiffrées : 106 107 121 127\n"
            "Déchiffrez-les."
        ),
        "type": "xor",
        "content": "106 107 121 127",
        "answer": "PENG",
        "hint1": "XOR est réversible : (a XOR k) XOR k = a",
        "hint2": "106 XOR 42 = 80 = 'P', 107 XOR 42 = 65 = ... etc",
        "hint3": "La réponse est PENG (non, c'est PENT — vérifiez vos calculs !)",
        "points": 150,
        "file": None,
    },
    {
        "id": 10, "level": "beginner", "order": 10,
        "title": "Stégano Avancée — PNG Caché",
        "story": (
            "MISSION FINALE DÉBUTANT.\n"
            "Un texte secret est caché DANS les pixels de l'image 'final_beginner.png'.\n"
            "Trouvez le mot de passe final pour valider le niveau."
        ),
        "type": "stegano_lsb",
        "content": "Analysez les bits de poids faible de 'final_beginner.png'.",
        "answer": "BLACKHAT",
        "hint1": "La stéganographie LSB cache des données dans le bit le moins significatif de chaque pixel.",
        "hint2": "Utilisez un outil comme StegSolve ou zsteg.",
        "hint3": "Le mot final est BLACKHAT",
        "points": 200,
        "file": "final_beginner.png",
    },
]

ENIGMAS_EXPERT = [
    {
        "id": 11, "level": "expert", "order": 1,
        "title": "Analyse de Logs Serveur",
        "story": (
            "Un serveur a été compromis cette nuit.\n"
            "Analysez 'server_logs.txt' et identifiez l'adresse IP de l'intrus."
        ),
        "type": "logs",
        "content": "Téléchargez et analysez 'server_logs.txt'.",
        "answer": "192.168.42.13",
        "hint1": "Cherchez les lignes avec 'ERROR' ou 'Intrusion'.",
        "hint2": "L'IP source est enregistrée après chaque tentative de connexion.",
        "hint3": "L'IP est 192.168.42.13",
        "points": 250,
        "file": "server_logs.txt",
    },
    {
        "id": 12, "level": "expert", "order": 2,
        "title": "Terminal SSH — Infiltration",
        "story": (
            "Vous avez accès au terminal du système compromis.\n"
            "Utilisez les commandes disponibles pour trouver le nom d'utilisateur\n"
            "qui a réussi à se connecter frauduleusement."
        ),
        "type": "terminal",
        "content": "Utilisez le terminal. Tapez 'help' pour commencer.",
        "answer": "s3cur1ty_t3am",
        "hint1": "Commencez par 'help' puis 'cat logs_serveur.txt'.",
        "hint2": "Cherchez la ligne avec 'Connexion réussie'.",
        "hint3": "Le user est s3cur1ty_t3am",
        "points": 300,
        "file": None,
    },
    {
        "id": 13, "level": "expert", "order": 3,
        "title": "Extraction EXIF — Métadonnées Forensics",
        "story": (
            "Une image a été trouvée sur le serveur compromis.\n"
            "Extrayez les métadonnées EXIF de 'forensic.png' pour trouver\n"
            "le mot de passe caché dans le champ Comment."
        ),
        "type": "metadata",
        "content": "Analysez 'forensic.png' avec un outil EXIF.",
        "answer": "p4ssw0rd_h1dd3n",
        "hint1": "ExifTool : exiftool forensic.png",
        "hint2": "Ou dans le terminal du jeu : extract forensic.png",
        "hint3": "Le mot de passe est p4ssw0rd_h1dd3n",
        "points": 350,
        "file": "forensic.png",
    },
    {
        "id": 14, "level": "expert", "order": 4,
        "title": "Décodage Multi-couches",
        "story": (
            "Ce message a subi 3 couches de chiffrement :\n"
            "1) ROT13  2) Base64  3) Hex\n"
            "Décodez dans le bon ordre pour obtenir le mot final."
        ),
        "type": "multi_decode",
        "content": "5a47567362454a68593255675a5735685a413d3d",
        "answer": "KERNEL",
        "hint1": "Décodez d'abord le Hex, puis le Base64, puis le ROT13.",
        "hint2": "Hex → 'ZGVsbBAcuZW5hZA==' → Base64 → ROT13 → ?",
        "hint3": "La réponse est KERNEL",
        "points": 400,
        "file": None,
    },
    {
        "id": 15, "level": "expert", "order": 5,
        "title": "Stéganographie Audio — Spectrogramme",
        "story": (
            "Un message secret a été encodé dans le spectrogramme\n"
            "du fichier audio 'spectrogram.wav'.\n"
            "Visualisez le spectrogramme pour lire le mot caché."
        ),
        "type": "spectrogram",
        "content": "Analysez le spectrogramme de 'spectrogram.wav'.",
        "answer": "PHANTOM",
        "hint1": "Ouvrez le fichier dans Audacity → Affichage Spectrogramme.",
        "hint2": "Le texte est visible dans les fréquences hautes.",
        "hint3": "Le mot est PHANTOM",
        "points": 400,
        "file": "spectrogram.wav",
    },
    {
        "id": 16, "level": "expert", "order": 6,
        "title": "MISSION FINALE — Clé Maître",
        "story": (
            "MISSION FINALE EXPERT.\n"
            "Assemblez les indices de toutes les missions précédentes.\n"
            "La clé finale = IP_user_motdepasse\n"
            "(les 3 éléments trouvés, séparés par _)"
        ),
        "type": "assembly",
        "content": "Combinez vos découvertes pour former la clé finale.",
        "answer": "192.168.42.13_s3cur1ty_t3am_p4ssw0rd_h1dd3n",
        "hint1": "Les 3 éléments viennent des missions 1, 2 et 3.",
        "hint2": "Format : IP_utilisateur_motdepasse",
        "hint3": "192.168.42.13_s3cur1ty_t3am_p4ssw0rd_h1dd3n",
        "points": 500,
        "file": None,
    },
]
