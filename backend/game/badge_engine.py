"""
Moteur d'attribution des badges.
Appelé après chaque action significative du joueur.
"""
from sqlalchemy.orm import Session
from models.user import User
from models.badge import Badge, UserBadge
from models.score import Score, UserProgress


BADGE_DEFINITIONS = [
    {
        "slug": "first_blood",
        "name": "First Blood",
        "description": "Résoudre votre première énigme",
        "icon": "🩸",
        "color": "#ff4444",
        "condition": "Première énigme résolue",
        "points_reward": 50,
    },
    {
        "slug": "decoder",
        "name": "Déchiffreur",
        "description": "Décoder un message Base64 ou César",
        "icon": "🔓",
        "color": "#39ff14",
        "condition": "Énigme de type base64 ou caesar résolue",
        "points_reward": 75,
    },
    {
        "slug": "stega_master",
        "name": "Stega Master",
        "description": "Trouver un indice caché dans une image",
        "icon": "🖼️",
        "color": "#00cfff",
        "condition": "Énigme stéganographie résolue",
        "points_reward": 100,
    },
    {
        "slug": "audio_detective",
        "name": "Détective Audio",
        "description": "Analyser et décoder un fichier audio",
        "icon": "🎧",
        "color": "#ff9900",
        "condition": "Énigme audio résolue",
        "points_reward": 100,
    },
    {
        "slug": "log_analyst",
        "name": "Analyste de Logs",
        "description": "Analyser des logs serveur pour trouver une intrusion",
        "icon": "📋",
        "color": "#ffff00",
        "condition": "Énigme logs résolue",
        "points_reward": 75,
    },
    {
        "slug": "no_hints",
        "name": "Sans Filet",
        "description": "Terminer un niveau sans utiliser d'indices",
        "icon": "🦅",
        "color": "#39ff14",
        "condition": "Niveau terminé sans indices",
        "points_reward": 200,
    },
    {
        "slug": "speed_hacker",
        "name": "Speed Hacker",
        "description": "Terminer le niveau Débutant en moins de 10 minutes",
        "icon": "⚡",
        "color": "#ffff00",
        "condition": "Niveau débutant < 600 secondes",
        "points_reward": 150,
    },
    {
        "slug": "black_hat",
        "name": "Black Hat",
        "description": "Terminer le niveau Expert",
        "icon": "🎩",
        "color": "#ff003c",
        "condition": "Niveau expert complété",
        "points_reward": 500,
    },
    {
        "slug": "persistent",
        "name": "Persévérant",
        "description": "Réessayer une énigme 5 fois ou plus",
        "icon": "💪",
        "color": "#cc44ff",
        "condition": "5 tentatives sur une même énigme",
        "points_reward": 25,
    },
    {
        "slug": "top_hacker",
        "name": "Top Hacker",
        "description": "Atteindre le top 3 du classement",
        "icon": "🏆",
        "color": "#ffd700",
        "condition": "Top 3 du classement général",
        "points_reward": 300,
    },
]


def seed_badges(db: Session):
    """Insère les badges en base s'ils n'existent pas encore."""
    for badge_data in BADGE_DEFINITIONS:
        existing = db.query(Badge).filter(Badge.slug == badge_data["slug"]).first()
        if not existing:
            db.add(Badge(**badge_data))
    db.commit()


def award_badge(user: User, badge_slug: str, db: Session) -> Badge | None:
    """Attribue un badge à un utilisateur s'il ne l'a pas déjà."""
    badge = db.query(Badge).filter(Badge.slug == badge_slug).first()
    if not badge:
        return None

    already = db.query(UserBadge).filter(
        UserBadge.user_id == user.id,
        UserBadge.badge_id == badge.id,
    ).first()
    if already:
        return None

    db.add(UserBadge(user_id=user.id, badge_id=badge.id))
    db.commit()
    return badge


def check_and_award_badges(
    user: User,
    enigma_type: str,
    hints_used: int,
    attempts: int,
    db: Session,
) -> list[Badge]:
    """
    Vérifie les conditions et attribue les badges mérités.
    Retourne la liste des nouveaux badges obtenus.
    """
    earned = []

    # Total d'énigmes résolues par ce joueur
    total_solved = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.solved == 1,
    ).count()

    # First Blood
    if total_solved == 1:
        b = award_badge(user, "first_blood", db)
        if b:
            earned.append(b)

    # Type-based badges
    type_badge_map = {
        "base64": "decoder",
        "caesar": "decoder",
        "stegano": "stega_master",
        "audio": "audio_detective",
        "logs": "log_analyst",
    }
    if enigma_type in type_badge_map:
        b = award_badge(user, type_badge_map[enigma_type], db)
        if b:
            earned.append(b)

    # Persévérant
    if attempts >= 5:
        b = award_badge(user, "persistent", db)
        if b:
            earned.append(b)

    return earned
