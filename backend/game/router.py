from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from pathlib import Path

from database.db import get_db
from auth.security import get_current_user
from models.user import User
from models.level import Level, Enigma
from models.score import Score, UserProgress
from models.badge import Badge, UserBadge, Certificate
from game.schemas import (
    LevelOut, EnigmaOut, AnswerRequest, AnswerResponse,
    TerminalCommand, TerminalResponse,
    LeaderboardEntry, BadgeOut, CertificateOut, ContactRequest,
)
from game.enigma_engine import check_answer, get_hint, process_terminal_command
from game.badge_engine import check_and_award_badges
from game.certificate import generate_certificate
from config import get_settings

settings = get_settings()
router = APIRouter(prefix="/game", tags=["Game"])


# ── Levels ────────────────────────────────────────────────────────────────────

@router.get("/levels", response_model=list[LevelOut])
def get_levels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne tous les niveaux avec les énigmes et la progression du joueur."""
    levels = db.query(Level).filter(Level.is_active == True).order_by(Level.order).all()

    result = []
    for level in levels:
        level_out = LevelOut.model_validate(level)

        # Enrichit chaque énigme avec la progression du joueur
        enriched_enigmas = []
        for enigma in level.enigmas:
            if not enigma.is_active:
                continue
            progress = db.query(UserProgress).filter(
                UserProgress.user_id == current_user.id,
                UserProgress.enigma_id == str(enigma.id),
            ).first()

            e_out = EnigmaOut.model_validate(enigma)
            e_out.solved = bool(progress and progress.solved)
            e_out.hints_used = progress.hints_used if progress else 0
            enriched_enigmas.append(e_out)

        level_out.enigmas = enriched_enigmas
        result.append(level_out)

    return result


@router.get("/levels/{level_slug}", response_model=LevelOut)
def get_level(
    level_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    level = db.query(Level).filter(Level.slug == level_slug, Level.is_active == True).first()
    if not level:
        raise HTTPException(404, "Niveau introuvable")
    return level


# ── Answer submission ─────────────────────────────────────────────────────────

@router.post("/answer", response_model=AnswerResponse)
def submit_answer(
    body: AnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enigma = db.query(Enigma).filter(Enigma.id == body.enigma_id, Enigma.is_active == True).first()
    if not enigma:
        raise HTTPException(404, "Énigme introuvable")

    # Récupère ou crée le progrès
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.enigma_id == str(enigma.id),
    ).first()
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            level_id=enigma.level_id,
            enigma_id=str(enigma.id),
        )
        db.add(progress)
        db.flush()

    if progress.solved:
        return AnswerResponse(correct=True, message="Vous avez déjà résolu cette énigme !", points_earned=0)

    progress.hints_used = progress.hints_used or 0
    progress.solved = getattr(progress, "solved", 0)

    # Incrémente les tentatives
    score_record = db.query(Score).filter(
        Score.user_id == current_user.id,
        Score.level_id == enigma.level_id,
    ).first()
    if not score_record:
        score_record = Score(user_id=current_user.id, level_id=enigma.level_id, points=0)
        db.add(score_record)
        db.flush()

    score_record.attempts = (score_record.attempts or 0) + 1

    # Vérifie la réponse
    is_correct = check_answer(enigma, body.answer)

    if is_correct:
        progress.solved = 1
        progress.solved_at = datetime.utcnow()

        # Calcul des points (pénalité selon indices utilisés)
        hint_penalty = progress.hints_used * 10
        points = max(enigma.points - hint_penalty, enigma.points // 2)
        score_record.points = (score_record.points or 0) + points

        db.commit()

        # Badges
        new_badges = check_and_award_badges(
            user=current_user,
            enigma_type=enigma.type,
            hints_used=progress.hints_used,
            attempts=score_record.attempts,
            db=db,
        )

        badge_out = None
        if new_badges:
            badge_out = BadgeOut.model_validate(new_badges[0])

        return AnswerResponse(
            correct=True,
            message=f"✅ Bonne réponse ! +{points} points",
            points_earned=points,
            badge_earned=badge_out,
        )
    else:
        db.commit()

        # Propose un indice après 3 tentatives
        hint = None
        if score_record.attempts >= 3:
            hint = get_hint(enigma, progress.hints_used)

        return AnswerResponse(
            correct=False,
            message="❌ Mauvaise réponse. Réessayez !",
            points_earned=0,
            hint=hint,
        )


# ── Hint ──────────────────────────────────────────────────────────────────────

@router.post("/hint/{enigma_id}")
def request_hint(
    enigma_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enigma = db.query(Enigma).filter(Enigma.id == enigma_id).first()
    if not enigma:
        raise HTTPException(404, "Énigme introuvable")

    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.enigma_id == str(enigma_id),
    ).first()
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            level_id=enigma.level_id,
            enigma_id=str(enigma_id),
            hints_used=0,
        )
        db.add(progress)
        db.flush()

    hint = get_hint(enigma, progress.hints_used or 0)
    if not hint:
        return {"hint": None, "message": "Plus d'indices disponibles pour cette énigme."}

    progress.hints_used = (progress.hints_used or 0) + 1

    # Pénalité de points
    score_record = db.query(Score).filter(
        Score.user_id == current_user.id,
        Score.level_id == enigma.level_id,
    ).first()
    if score_record:
        score_record.points = max((score_record.points or 0) - 10, 0)

    db.commit()
    return {"hint": hint, "message": f"Indice {progress.hints_used}/3 (-10 pts)"}


# ── Terminal (niveau expert) ──────────────────────────────────────────────────

@router.post("/terminal", response_model=TerminalResponse)
def terminal_command(
    body: TerminalCommand,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Traite une commande du terminal interactif (niveau expert)."""
    output, success, points = process_terminal_command(body.command)

    if points > 0:
        expert_level = db.query(Level).filter(Level.slug == "expert").first()
        if expert_level:
            score_record = db.query(Score).filter(
                Score.user_id == current_user.id,
                Score.level_id == expert_level.id,
            ).first()
            if not score_record:
                score_record = Score(user_id=current_user.id, level_id=expert_level.id, points=0)
                db.add(score_record)
            score_record.points = (score_record.points or 0) + points
            db.commit()

    return TerminalResponse(output=output, success=success, points_earned=points)


# ── Leaderboard ───────────────────────────────────────────────────────────────

@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Classement général par total de points."""
    results = (
        db.query(
            User.id,
            User.pseudo,
            User.avatar_url,
            func.sum(Score.points).label("total_points"),
        )
        .join(Score, Score.user_id == User.id, isouter=True)
        .group_by(User.id)
        .order_by(func.sum(Score.points).desc())
        .limit(50)
        .all()
    )

    entries = []
    for rank, row in enumerate(results, start=1):
        badges_count = db.query(UserBadge).filter(UserBadge.user_id == row.id).count()

        # Niveau atteint
        levels_completed = db.query(UserProgress).filter(
            UserProgress.user_id == row.id,
            UserProgress.solved == 1,
        ).count()
        if levels_completed == 0:
            level_reached = "Aucun"
        elif levels_completed < 5:
            level_reached = "Débutant"
        else:
            level_reached = "Expert"

        entries.append(LeaderboardEntry(
            rank=rank,
            user_id=row.id,
            pseudo=row.pseudo,
            avatar_url=row.avatar_url,
            total_points=row.total_points or 0,
            badges_count=badges_count,
            level_reached=level_reached,
        ))

    return entries


# ── Badges ────────────────────────────────────────────────────────────────────

@router.get("/badges", response_model=list[BadgeOut])
def all_badges(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Badge).all()


@router.get("/my-badges", response_model=list[BadgeOut])
def my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_badges = (
        db.query(Badge)
        .join(UserBadge, UserBadge.badge_id == Badge.id)
        .filter(UserBadge.user_id == current_user.id)
        .all()
    )
    return user_badges


# ── Certificate ───────────────────────────────────────────────────────────────

@router.post("/certificate/{level_slug}", response_model=CertificateOut)
def generate_cert(
    level_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Génère le certificat PDF si le niveau est complété."""
    level = db.query(Level).filter(Level.slug == level_slug).first()
    if not level:
        raise HTTPException(404, "Niveau introuvable")

    # Vérifie que toutes les énigmes sont résolues
    total_enigmas = db.query(Enigma).filter(
        Enigma.level_id == level.id, Enigma.is_active == True
    ).count()
    solved_enigmas = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.level_id == level.id,
        UserProgress.solved == 1,
    ).count()

    if solved_enigmas < total_enigmas:
        raise HTTPException(
            400,
            f"Niveau non complété : {solved_enigmas}/{total_enigmas} énigmes résolues"
        )

    # Score total
    score_record = db.query(Score).filter(
        Score.user_id == current_user.id,
        Score.level_id == level.id,
    ).first()
    total_score = score_record.points if score_record else 0

    # Certificat existant ?
    existing = db.query(Certificate).filter(
        Certificate.user_id == current_user.id,
        Certificate.level == level_slug,
    ).first()
    if existing:
        return CertificateOut.model_validate(existing)

    # Génère le PDF
    pdf_path, unique_code = generate_certificate(
        pseudo=current_user.pseudo,
        level=level_slug,
        score=total_score,
        user_id=current_user.id,
    )

    cert = Certificate(
        user_id=current_user.id,
        level=level_slug,
        score=total_score,
        pdf_path=pdf_path,
        unique_code=unique_code,
    )
    db.add(cert)

    # Badge Black Hat si niveau expert
    if level_slug == "expert":
        from game.badge_engine import award_badge
        award_badge(current_user, "black_hat", db)

    db.commit()
    db.refresh(cert)
    return CertificateOut.model_validate(cert)


@router.get("/certificate/download/{unique_code}")
def download_certificate(
    unique_code: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    cert = db.query(Certificate).filter(Certificate.unique_code == unique_code).first()
    if not cert or not cert.pdf_path:
        raise HTTPException(404, "Certificat introuvable")

    path = Path(cert.pdf_path)
    if not path.exists():
        raise HTTPException(404, "Fichier PDF introuvable")

    return FileResponse(
        str(path),
        media_type="application/pdf",
        filename=f"H4CKR_certificat_{cert.level}_{unique_code[:8]}.pdf",
    )


# ── Contact ───────────────────────────────────────────────────────────────────

@router.post("/contact", status_code=201)
def contact(
    body: ContactRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Enregistre un message de contact.
    En production : envoyer un email via SMTP ou stocker en base.
    """
    print(
        f"\n[CONTACT] De: {current_user.pseudo} ({current_user.email})\n"
        f"  Catégorie: {body.category}\n"
        f"  Sujet: {body.subject}\n"
        f"  Message: {body.message}\n"
    )
    return {
        "status": "ok",
        "message": "Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais."
    }


# ── Assets ────────────────────────────────────────────────────────────────────

@router.get("/video/{filename}")
def get_video(filename: str, _: User = Depends(get_current_user)):
    """Sert les vidéos d'intro des niveaux."""
    path = Path(settings.ASSETS_DIR) / "videos" / filename
    if not path.exists():
        raise HTTPException(404, "Vidéo introuvable")
    return FileResponse(str(path), media_type="video/mp4")


@router.get("/enigma-file/{filename}")
def get_enigma_file(filename: str, _: User = Depends(get_current_user)):
    """Sert les fichiers d'énigmes (images, audio…)."""
    path = Path(settings.ASSETS_DIR) / "enigmas" / filename
    if not path.exists():
        raise HTTPException(404, "Fichier introuvable")
    return FileResponse(str(path))
