"""
Génère automatiquement tous les fichiers d'énigmes de démonstration.
Lance avec : python generate_assets.py

Fichiers générés dans src/assets/enigmas/ :
  mission_01.png       — PNG avec métadonnées EXIF cachées (GHOST)
  signal_01.wav        — WAV avec mot inversé (CYBER)
  data_07.txt          — Texte ROT13 (FRPHER → SECURE)
  audio_08.mp3         — Texte avec tag ID3 Comment: FIREWALL (simulation)
  final_beginner.png   — PNG avec stégano LSB (BLACKHAT)
  server_logs.txt      — Faux logs serveur (IP intrus: 192.168.42.13)
  forensic.png         — PNG EXIF expert (p4ssw0rd_h1dd3n)
  spectrogram.wav      — WAV placeholder (spectrogramme PHANTOM)
"""
import struct
import random
from pathlib import Path
from PIL import Image, ImageDraw, PngImagePlugin

ENIGMA_DIR = Path("src/assets/enigmas")
ENIGMA_DIR.mkdir(parents=True, exist_ok=True)

# ── Couleurs style H4CKR ──────────────────────────────────────────────────────
BG     = (6,   11,  6)
GREEN  = (57,  255, 20)
GDIM   = (30,  100, 15)
RED    = (255, 0,   60)
CYAN   = (0,   200, 255)
WHITE  = (200, 245, 200)
GRAY   = (80,  120, 80)


def _draw_terminal_bg(draw, w, h, title, lines, border_color=GREEN):
    """Dessine un fond style terminal sur une image PIL."""
    # Fond
    draw.rectangle([0, 0, w, h], fill=BG)
    # Bordure
    draw.rectangle([4, 4, w-4, h-4], outline=border_color, width=2)
    # Barre titre
    draw.rectangle([4, 4, w-4, 28], fill=(10, 25, 10))
    # Points macOS
    for i, col in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        cx = 18 + i * 16
        draw.ellipse([cx-5, 10, cx+5, 20], fill=col)
    # Titre
    draw.text((w//2 - len(title)*3, 10), title, fill=GRAY)
    # Lignes
    y = 40
    for kind, txt in lines:
        col = GREEN if kind == "green" else (RED if kind == "red" else (CYAN if kind == "cyan" else GRAY))
        draw.text((14, y), txt, fill=col)
        y += 20
    return draw


# ── 1. mission_01.png — stégano métadonnées (GHOST) ──────────────────────────
def gen_mission_01():
    w, h = 500, 320
    img  = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    lines = [
        ("green",  "> H4CKR — FICHIER SUSPECT"),
        ("gray",   "> Agent, analysez ce fichier."),
        ("gray",   "> Les métadonnées contiennent"),
        ("gray",   "> un mot de passe caché."),
        ("green",  "> Utilisez ExifTool ou"),
        ("green",  "> vérifiez le champ Comment."),
        ("cyan",   ""),
        ("cyan",   "> Indice : champ Comment"),
        ("gray",   "> des métadonnées PNG"),
        ("red",    "> [DONNÉES CACHÉES DÉTECTÉES]"),
    ]
    _draw_terminal_bg(draw, w, h, "H4CKR — mission_01.png", lines)
    # Grille décorative
    for gx in range(0, w, 40):
        draw.line([(gx, 0), (gx, h)], fill=(10, 20, 10), width=1)

    meta = PngImagePlugin.PngInfo()
    meta.add_text("Comment", "GHOST")
    meta.add_text("Author",  "Unknown Agent")
    meta.add_text("Software","H4CKR-Tools v1.0")
    meta.add_text("Warning", "Ce fichier contient des données cachées")

    path = ENIGMA_DIR / "mission_01.png"
    img.save(str(path), pnginfo=meta)
    print(f"✅ {path}  (Comment: GHOST)")


# ── 2. signal_01.wav — audio inversé (CYBER) ─────────────────────────────────
def gen_signal_01():
    """
    Génère un WAV avec un signal sinusoïdal.
    Le 'mot inversé' est une convention — dans un vrai jeu, enregistrez
    'REBEC' (CYBER à l'envers) puis inversez avec Audacity/pydub.
    Ce fichier est un placeholder sonore cohérent.
    """
    sample_rate  = 44100
    duration     = 4.0
    num_samples  = int(sample_rate * duration)

    import math
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        # Signal complexe multi-fréquences (sonore et intéressant)
        val = (
            0.4 * math.sin(2 * math.pi * 440 * t) +
            0.3 * math.sin(2 * math.pi * 880 * t * (1 + 0.1 * math.sin(t))) +
            0.2 * math.sin(2 * math.pi * 220 * t) +
            0.1 * (random.random() - 0.5)
        )
        # Fade in/out
        fade = min(t / 0.3, 1.0, (duration - t) / 0.3)
        sample = int(val * fade * 16000)
        sample = max(-32768, min(32767, sample))
        samples.append(struct.pack('<h', sample))

    data    = b"".join(samples)
    data_sz = len(data)
    header  = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + data_sz, b'WAVE',
        b'fmt ', 16, 1, 1,
        sample_rate, sample_rate * 2, 2, 16,
        b'data', data_sz,
    )
    path = ENIGMA_DIR / "signal_01.wav"
    with open(str(path), 'wb') as f:
        f.write(header + data)
    print(f"✅ {path}  (réponse: CYBER — inversez la piste dans Audacity)")


# ── 3. data_07.txt — ROT13 (FRPHER → SECURE) ─────────────────────────────────
def gen_data_07():
    content = """\
=== H4CKR — FICHIER CHIFFRÉ ===
Classification : CONFIDENTIEL

Ce message a été protégé par un chiffrement ROT13.
Déchiffrez le contenu pour obtenir le mot de passe.

MESSAGE CHIFFRÉ :
------------------
FRPHER
------------------

Indice : ROT13 déplace chaque lettre de 13 positions.
Outil en ligne : rot13.com
Python : import codecs; codecs.decode('FRPHER', 'rot_13')
"""
    path = ENIGMA_DIR / "data_07.txt"
    path.write_text(content, encoding="utf-8")
    print(f"✅ {path}  (FRPHER → SECURE via ROT13)")


# ── 4. audio_08_meta.txt — simulation tag ID3 ────────────────────────────────
def gen_audio_08():
    """
    Génère un fichier texte simulant les métadonnées ID3 d'un MP3.
    (Un vrai MP3 nécessite mutagen ou ffmpeg)
    """
    content = """\
=== H4CKR — MÉTADONNÉES AUDIO ===
Fichier : audio_08.mp3

[Analyse des tags ID3]
---------------------------------
Titre     : Unknown Track
Artiste   : Unknown
Album     : H4CKR Mission Files
Année     : 2024
Genre     : Electronic
Durée     : 00:03:42
---------------------------------
Commentaire : FIREWALL
---------------------------------

Indice : Le mot de passe est dans le champ "Commentaire".
Pour lire les vrais tags ID3 : pip install mutagen
>>> from mutagen.mp3 import MP3
>>> from mutagen.id3 import ID3
>>> tags = ID3('audio_08.mp3')
>>> print(tags['COMM'])
"""
    path = ENIGMA_DIR / "audio_08_meta.txt"
    path.write_text(content, encoding="utf-8")
    print(f"✅ {path}  (Commentaire: FIREWALL)")

    # Génère aussi un WAV simple comme audio_08.mp3 placeholder
    sample_rate = 22050
    duration    = 2.0
    num_samples = int(sample_rate * duration)
    import math
    samples = []
    for i in range(num_samples):
        t   = i / sample_rate
        val = int(math.sin(2 * math.pi * 523 * t) * 8000)
        val = max(-32768, min(32767, val))
        samples.append(struct.pack('<h', val))
    data    = b"".join(samples)
    data_sz = len(data)
    header  = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + data_sz, b'WAVE',
        b'fmt ', 16, 1, 1,
        sample_rate, sample_rate * 2, 2, 16,
        b'data', data_sz,
    )
    wav_path = ENIGMA_DIR / "audio_08.wav"
    with open(str(wav_path), 'wb') as f:
        f.write(header + data)
    print(f"✅ {wav_path}  (placeholder — réponse dans audio_08_meta.txt)")


# ── 5. final_beginner.png — stégano LSB (BLACKHAT) ───────────────────────────
def gen_final_beginner():
    """
    Cache le mot 'BLACKHAT' dans les bits de poids faible (LSB) des pixels.
    """
    w, h = 500, 340
    img  = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)

    lines = [
        ("red",    "> MISSION FINALE — DÉBUTANT"),
        ("gray",   "> Un texte est caché DANS"),
        ("gray",   "> les pixels de cette image."),
        ("cyan",   "> Technique : LSB Steganography"),
        ("green",  "> Outil : StegSolve ou zsteg"),
        ("gray",   "> zsteg final_beginner.png"),
        ("green",  "> Ou : stegano (Python)"),
        ("gray",   "> from stegano import lsb"),
        ("gray",   "> lsb.reveal('image.png')"),
        ("red",    "> [DONNÉES LSB DÉTECTÉES]"),
    ]
    _draw_terminal_bg(draw, w, h, "H4CKR — MISSION FINALE", lines, RED)

    pixels = list(img.getdata())   # liste de tuples (R,G,B)

    # Encode 'BLACKHAT' + terminateur null en LSB
    message   = "BLACKHAT\x00"
    bits      = []
    for char in message:
        byte = ord(char)
        for b in range(7, -1, -1):
            bits.append((byte >> b) & 1)

    new_pixels = list(pixels)
    for i, bit in enumerate(bits):
        if i >= len(new_pixels):
            break
        r, g, b_val = new_pixels[i]
        r = (r & 0xFE) | bit
        new_pixels[i] = (r, g, b_val)

    img.putdata(new_pixels)

    meta = PngImagePlugin.PngInfo()
    meta.add_text("Description", "Mission finale niveau debutant")
    path = ENIGMA_DIR / "final_beginner.png"
    img.save(str(path), pnginfo=meta)
    print(f"✅ {path}  (LSB: BLACKHAT)")


# ── 6. server_logs.txt — logs avec IP intrus ─────────────────────────────────
def gen_server_logs():
    content = """\
=== LOGS SERVEUR — prod-server-01 ===
Date : 2024-01-15 | Fuseau : UTC+1

[03:38:00] INFO  — Service SSH démarré (port 22)
[03:39:12] INFO  — Connexion : user=deploy         | IP: 10.0.0.5      | OK
[03:40:00] INFO  — Backup automatique lancé
[03:41:55] INFO  — Connexion : user=monitoring     | IP: 10.0.0.12     | OK
[03:42:11] WARN  — Tentative échouée : user=admin  | IP: 192.168.42.13 | FAILED
[03:42:33] WARN  — Tentative échouée : user=root   | IP: 192.168.42.13 | FAILED
[03:42:45] WARN  — Tentative échouée : user=admin  | IP: 192.168.42.13 | FAILED
[03:42:58] WARN  — Tentative échouée : user=test   | IP: 192.168.42.13 | FAILED
[03:43:02] INFO  — Connexion réussie : user=s3cur1ty_t3am | IP: 192.168.42.13 | OK
[03:43:15] INFO  — Accès fichier : /var/secret/vault.key
[03:43:28] INFO  — Accès fichier : /etc/shadow
[03:43:44] INFO  — Accès fichier : /root/.ssh/id_rsa
[03:44:00] WARN  — Fichier modifié : /etc/passwd
[03:44:18] WARN  — Fichier modifié : /etc/crontab
[03:44:30] ERROR — INTRUSION DÉTECTÉE — Source IP: 192.168.42.13
[03:44:31] ERROR — Exfiltration de données suspectée (3.2 MB envoyés)
[03:44:45] INFO  — Déconnexion : user=s3cur1ty_t3am
[03:44:46] WARN  — Alerte sécurité transmise à l'équipe SOC
[03:45:00] INFO  — Isolation du serveur en cours...

=== FIN DES LOGS ===

Analyste SOC : identifiez l'adresse IP source de l'intrusion.
"""
    path = ENIGMA_DIR / "server_logs.txt"
    path.write_text(content, encoding="utf-8")
    print(f"✅ {path}  (IP intrus: 192.168.42.13)")


# ── 7. forensic.png — EXIF expert (p4ssw0rd_h1dd3n) ─────────────────────────
def gen_forensic():
    w, h = 500, 340
    img  = Image.new("RGB", (w, h), (5, 10, 5))
    draw = ImageDraw.Draw(img)

    lines = [
        ("red",    "> CLASSIFIED — NIVEAU EXPERT"),
        ("gray",   "> Fichier récupéré sur"),
        ("gray",   "> le serveur compromis."),
        ("cyan",   "> Analysez les métadonnées EXIF"),
        ("green",  "> ExifTool : exiftool forensic.png"),
        ("green",  "> Ou : PIL / piexif (Python)"),
        ("gray",   "> from PIL import Image"),
        ("gray",   "> img.info  # → métadonnées"),
        ("red",    "> Cherchez le champ Comment"),
        ("red",    "> [ACCÈS RESTREINT — NIVEAU 2]"),
    ]
    _draw_terminal_bg(draw, w, h, "H4CKR — forensic.png", lines, RED)

    # Grille rouge
    for gx in range(0, w, 40):
        draw.line([(gx, 0), (gx, h)], fill=(20, 5, 5), width=1)

    meta = PngImagePlugin.PngInfo()
    meta.add_text("Comment",       "p4ssw0rd_h1dd3n")
    meta.add_text("Author",        "Unknown")
    meta.add_text("Creation Time", "2024-01-15T03:41:00")
    meta.add_text("GPS",           "48.8566 N, 2.3522 E")
    meta.add_text("Software",      "GIMP 2.10")
    meta.add_text("Warning",       "Fichier classifié — usage interne uniquement")

    path = ENIGMA_DIR / "forensic.png"
    img.save(str(path), pnginfo=meta)
    print(f"✅ {path}  (Comment: p4ssw0rd_h1dd3n)")


# ── 8. spectrogram.wav — audio avec texte dans spectrogramme ─────────────────
def gen_spectrogram():
    """
    Génère un WAV où 'PHANTOM' est encodé dans le spectrogramme.
    On superpose des sinusoïdes à des fréquences formant les lettres visuellement.
    Ce fichier est un placeholder — idéalement généré avec un outil spécialisé
    comme Coagula Light ou un script scipy.
    """
    sample_rate = 44100
    duration    = 5.0
    num_samples = int(sample_rate * duration)

    import math

    # Génère un signal avec plusieurs fréquences (simulant un spectrogramme chargé)
    freqs_per_letter = {
        'P': [2000, 2200, 2400],
        'H': [2600, 2800, 3000],
        'A': [3200, 3400, 3600],
        'N': [3800, 4000, 4200],
        'T': [4400, 4600, 4800],
        'O': [5000, 5200, 5400],
        'M': [5600, 5800, 6000],
    }

    all_freqs = [f for freqs in freqs_per_letter.values() for f in freqs]

    samples = []
    for i in range(num_samples):
        t   = i / sample_rate
        val = 0.0
        for freq in all_freqs:
            # Chaque lettre active ses fréquences dans une fenêtre temporelle
            letter_idx = all_freqs.index(freq) // 3
            t_start    = letter_idx * (duration / 7)
            t_end      = t_start + duration / 7 * 0.8
            if t_start <= t <= t_end:
                val += 0.05 * math.sin(2 * math.pi * freq * t)
        # Bruit de fond léger
        val += 0.02 * (random.random() - 0.5)
        sample = int(val * 32000)
        sample = max(-32768, min(32767, sample))
        samples.append(struct.pack('<h', sample))

    data    = b"".join(samples)
    data_sz = len(data)
    header  = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + data_sz, b'WAVE',
        b'fmt ', 16, 1, 1,
        sample_rate, sample_rate * 2, 2, 16,
        b'data', data_sz,
    )
    path = ENIGMA_DIR / "spectrogram.wav"
    with open(str(path), 'wb') as f:
        f.write(header + data)
    print(f"✅ {path}  (spectrogramme: PHANTOM — ouvrir dans Audacity)")


# ── 9. Fichier d'aide stégano ──────────────────────────────────────────────────
def gen_readme():
    content = """\
=== H4CKR — GUIDE DES FICHIERS D'ÉNIGMES ===

NIVEAU DÉBUTANT
===============

mission_01.png
  Type    : Stéganographie (métadonnées PNG)
  Réponse : GHOST
  Méthode : Lisez le champ "Comment" des métadonnées PNG
            Outils : exiftool, PIL/Pillow, propriétés fichier

signal_01.wav
  Type    : Audio inversé
  Réponse : CYBER
  Méthode : Ouvrez dans Audacity → Effets → Inverser
            Le mot 'CYBER' est prononcé à l'envers

data_07.txt
  Type    : ROT13
  Réponse : SECURE
  Méthode : Décodez 'FRPHER' via ROT13
            Python : codecs.decode('FRPHER', 'rot_13')

audio_08 (métadonnées)
  Type    : Métadonnées ID3
  Réponse : FIREWALL
  Méthode : Lisez audio_08_meta.txt pour les tags ID3 simulés

final_beginner.png
  Type    : Stéganographie LSB
  Réponse : BLACKHAT
  Méthode : Lisez les bits de poids faible des pixels rouges
            Python :
            from stegano import lsb
            print(lsb.reveal('final_beginner.png'))

NIVEAU EXPERT
=============

server_logs.txt
  Type    : Analyse de logs
  Réponse : 192.168.42.13
  Méthode : Cherchez la ligne "INTRUSION DÉTECTÉE"

forensic.png
  Type    : Métadonnées EXIF avancées
  Réponse : p4ssw0rd_h1dd3n
  Méthode : exiftool forensic.png → champ Comment
            Python : Image.open('forensic.png').info

spectrogram.wav
  Type    : Spectrogramme audio
  Réponse : PHANTOM
  Méthode : Audacity → Vue Spectrogramme
            Les fréquences dessinent le mot PHANTOM
"""
    path = ENIGMA_DIR / "GUIDE_ENIGMES.txt"
    path.write_text(content, encoding="utf-8")
    print(f"✅ {path}  (guide des réponses)")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🎯 Génération des fichiers d'énigmes H4CKR...\n")
    gen_mission_01()
    gen_signal_01()
    gen_data_07()
    gen_audio_08()
    gen_final_beginner()
    gen_server_logs()
    gen_forensic()
    gen_spectrogram()
    gen_readme()
    print(f"\n✅ Tous les fichiers générés dans : {ENIGMA_DIR.resolve()}")
    print("\nRécapitulatif des réponses :")
    print("  mission_01.png     → GHOST")
    print("  signal_01.wav      → CYBER")
    print("  data_07.txt        → SECURE")
    print("  audio_08           → FIREWALL")
    print("  final_beginner.png → BLACKHAT")
    print("  server_logs.txt    → 192.168.42.13")
    print("  forensic.png       → p4ssw0rd_h1dd3n")
    print("  spectrogram.wav    → PHANTOM")
