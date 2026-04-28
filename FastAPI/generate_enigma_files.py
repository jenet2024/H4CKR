"""
Génère les fichiers d'énigmes de démonstration.
Lance avec : python generate_enigma_files.py
Dépendances : Pillow (déjà dans requirements.txt)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from PIL import Image, PngImagePlugin
import base64

ENIGMAS_DIR = Path("./assets/enigmas")
ENIGMAS_DIR.mkdir(parents=True, exist_ok=True)


def create_suspect_png():
    """Image PNG avec métadonnées cachées (niveau débutant)."""
    img = Image.new("RGB", (400, 300), color=(10, 20, 10))

    # Dessine un texte vert style terminal
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 380, 280], outline=(57, 255, 20), width=2)
    draw.text((40, 50),  "H4CKR",         fill=(57, 255, 20))
    draw.text((40, 90),  "> FICHIER SUSPECT", fill=(57, 255, 20))
    draw.text((40, 130), "> ANALYSE EN COURS...", fill=(40, 150, 40))
    draw.text((40, 170), "> DONNÉES CACHÉES DÉTECTÉES", fill=(200, 80, 80))
    draw.text((40, 210), "> Cherchez les métadonnées...", fill=(40, 150, 40))

    # Ajoute le commentaire caché dans les métadonnées PNG
    meta = PngImagePlugin.PngInfo()
    meta.add_text("Comment", "GHOST_PROTOCOL")
    meta.add_text("Author", "Unknown Agent")
    meta.add_text("Software", "H4CKR-Tools v1.0")

    path = ENIGMAS_DIR / "suspect.png"
    img.save(str(path), pnginfo=meta)
    print(f"✅ {path} créé (Comment: GHOST_PROTOCOL)")


def create_suspect_expert_png():
    """Image PNG avec métadonnées avancées (niveau expert)."""
    img = Image.new("RGB", (400, 300), color=(5, 10, 5))

    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 390, 290], outline=(255, 0, 60), width=2)
    draw.text((30, 40),  "CLASSIFIED",        fill=(255, 0, 60))
    draw.text((30, 80),  "> NIVEAU : EXPERT", fill=(57, 255, 20))
    draw.text((30, 120), "> ACCÈS RESTREINT", fill=(200, 80, 80))
    draw.text((30, 160), "> Analysez les EXIF", fill=(40, 150, 40))
    draw.text((30, 200), "> Indice : champ Comment", fill=(40, 150, 40))
    draw.text((30, 240), "████████████████████", fill=(30, 60, 30))

    meta = PngImagePlugin.PngInfo()
    meta.add_text("Comment", "p4ssw0rd_h1dd3n_h3r3")
    meta.add_text("Author", "Unknown")
    meta.add_text("Creation Time", "2024-01-15T03:41:00")
    meta.add_text("GPS", "48.8566 N, 2.3522 E")

    path = ENIGMAS_DIR / "suspect_expert.png"
    img.save(str(path), pnginfo=meta)
    print(f"✅ {path} créé (Comment: p4ssw0rd_h1dd3n_h3r3)")


def create_logs_file():
    """Faux fichier de logs serveur."""
    content = """\
=== LOGS SERVEUR — server-prod-01 ===
Date: 2024-01-15

[2024-01-15 03:40:00] INFO  — Démarrage du service SSH
[2024-01-15 03:41:12] INFO  — Connexion : user=deploy | IP: 10.0.0.5
[2024-01-15 03:42:11] WARN  — Tentative connexion échouée : user=admin | IP: 192.168.42.13
[2024-01-15 03:42:33] WARN  — Tentative connexion échouée : user=root  | IP: 192.168.42.13
[2024-01-15 03:42:45] WARN  — Tentative connexion échouée : user=admin | IP: 192.168.42.13
[2024-01-15 03:43:02] INFO  — Connexion réussie : user=s3cur1ty_t3am  | IP: 192.168.42.13
[2024-01-15 03:43:15] INFO  — Accès fichier : /var/secret/vault.key
[2024-01-15 03:43:44] INFO  — Accès fichier : /etc/shadow
[2024-01-15 03:44:00] WARN  — Fichier modifié : /etc/passwd
[2024-01-15 03:44:30] ERROR — Intrusion détectée — Source IP: 192.168.42.13
[2024-01-15 03:44:31] ERROR — Exfiltration de données suspectée
[2024-01-15 03:44:45] INFO  — Déconnexion : user=s3cur1ty_t3am
[2024-01-15 03:45:00] WARN  — Alerte sécurité envoyée à l'équipe SOC
=== FIN DES LOGS ===
"""
    path = ENIGMAS_DIR / "logs_serveur.txt"
    path.write_text(content, encoding="utf-8")
    print(f"✅ {path} créé (IP intrus: 192.168.42.13)")


def create_base64_file():
    """Fichier Base64 pour le terminal expert."""
    message = "Hello Agent, le mot de passe est : HACKER2025"
    encoded = base64.b64encode(message.encode()).decode()
    path = ENIGMAS_DIR / "message_chiffre.b64"
    path.write_text(encoded + "\n", encoding="utf-8")
    print(f"✅ {path} créé (décode en: '{message}')")


def create_wav_placeholder():
    """Fichier WAV placeholder (signal audio)."""
    # WAV minimal valide (44 octets header + silence)
    import struct
    sample_rate = 8000
    duration = 3
    num_samples = sample_rate * duration
    data_size = num_samples * 2

    header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + data_size, b'WAVE',
        b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16,
        b'data', data_size,
    )
    silence = b'\x00' * data_size

    path = ENIGMAS_DIR / "signal.wav"
    with open(str(path), 'wb') as f:
        f.write(header + silence)
    print(f"✅ {path} créé (placeholder WAV — remplacez par un vrai fichier audio inversé)")
    print("   👉 Voir assets/enigmas/README.md pour créer le vrai fichier")


if __name__ == "__main__":
    print("🎯 Génération des fichiers d'énigmes...\n")
    create_suspect_png()
    create_suspect_expert_png()
    create_logs_file()
    create_base64_file()
    create_wav_placeholder()
    print("\n✅ Tous les fichiers d'énigmes ont été générés dans ./assets/enigmas/")
