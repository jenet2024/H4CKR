"""
Génération des certificats PDF avec ReportLab.
"""
import os
import secrets
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from config import get_settings

settings = get_settings()
CERTS_DIR = Path(settings.ASSETS_DIR) / "certificates"
CERTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_certificate(
    pseudo: str,
    level: str,
    score: int,
    user_id: int,
) -> tuple[str, str]:
    """
    Génère un certificat PDF et retourne (chemin_fichier, code_unique).
    """
    unique_code = secrets.token_hex(16).upper()
    level_label = "Débutant" if level == "beginner" else "Expert"
    filename = f"cert_{user_id}_{level}_{unique_code[:8]}.pdf"
    filepath = CERTS_DIR / filename

    # ── Création du PDF ───────────────────────────────────────────────────────
    c = canvas.Canvas(str(filepath), pagesize=landscape(A4))
    w, h = landscape(A4)

    # Fond noir
    c.setFillColor(colors.HexColor("#060b06"))
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Bordure verte néon
    c.setStrokeColor(colors.HexColor("#39ff14"))
    c.setLineWidth(3)
    c.rect(1.5*cm, 1.5*cm, w - 3*cm, h - 3*cm, fill=0, stroke=1)

    # Bordure intérieure (tirets)
    c.setLineWidth(0.5)
    c.setDash(6, 4)
    c.rect(2*cm, 2*cm, w - 4*cm, h - 4*cm, fill=0, stroke=1)
    c.setDash()

    # Titre principal
    c.setFont("Courier-Bold", 42)
    c.setFillColor(colors.HexColor("#39ff14"))
    c.drawCentredString(w / 2, h - 5*cm, "H4CKR")

    # Sous-titre
    c.setFont("Courier-Bold", 18)
    c.setFillColor(colors.HexColor("#7ecf7e"))
    c.drawCentredString(w / 2, h - 6.5*cm, "CERTIFICAT DE COMPLETION")

    # Ligne décorative
    c.setStrokeColor(colors.HexColor("#39ff14"))
    c.setLineWidth(1)
    c.line(5*cm, h - 7.2*cm, w - 5*cm, h - 7.2*cm)

    # Corps
    c.setFont("Courier", 16)
    c.setFillColor(colors.HexColor("#c8f5c8"))
    c.drawCentredString(w / 2, h - 9*cm, "Ce certificat atteste que")

    c.setFont("Courier-Bold", 28)
    c.setFillColor(colors.HexColor("#39ff14"))
    c.drawCentredString(w / 2, h - 10.5*cm, pseudo.upper())

    c.setFont("Courier", 16)
    c.setFillColor(colors.HexColor("#c8f5c8"))
    c.drawCentredString(w / 2, h - 12*cm, f"a complété avec succès le niveau {level_label}")
    c.drawCentredString(w / 2, h - 13*cm, f"du jeu de simulation de hacking H4CKR")

    # Score
    c.setFont("Courier-Bold", 22)
    c.setFillColor(colors.HexColor("#ffff00"))
    c.drawCentredString(w / 2, h - 14.5*cm, f"Score final : {score} points")

    # Date
    c.setFont("Courier", 12)
    c.setFillColor(colors.HexColor("#5a9e5a"))
    date_str = datetime.utcnow().strftime("%d/%m/%Y")
    c.drawCentredString(w / 2, h - 16*cm, f"Délivré le {date_str}")

    # Code unique
    c.setFont("Courier", 10)
    c.setFillColor(colors.HexColor("#3a5a3a"))
    c.drawCentredString(w / 2, 2.5*cm, f"Code de vérification : {unique_code}")

    # Coins décoratifs
    green = colors.HexColor("#39ff14")
    for (x, y) in [(2.5*cm, h-2.5*cm), (w-2.5*cm, h-2.5*cm), (2.5*cm, 2.5*cm), (w-2.5*cm, 2.5*cm)]:
        c.setFillColor(green)
        c.circle(x, y, 4, fill=1, stroke=0)

    c.save()
    return str(filepath), unique_code
