from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database.db import get_db
from models.user import User
from models.level import Level, Enigma
from models.score import Score
from models.badge import Badge, UserBadge
from auth.security import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

class UserAdminOut(BaseModel):
    id: int
    pseudo: str
    email: str
    is_admin: bool
    is_active: bool
    is_verified: bool
    auth_provider: str
    created_at: datetime
    total_points: int
    badges_count: int
    class Config:
        from_attributes = True

class StatsOut(BaseModel):
    total_users: int
    total_scores: int
    total_badges_earned: int
    total_levels: int
    total_enigmas: int
    top_player: Optional[str] = None
    top_score: int

class UserUpdateRequest(BaseModel):
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class EnigmaUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    hint1: Optional[str] = None
    hint2: Optional[str] = None
    hint3: Optional[str] = None
    points: Optional[int] = None

@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    top = (db.query(User.pseudo, func.sum(Score.points).label("pts"))
           .join(Score, Score.user_id == User.id, isouter=True)
           .group_by(User.id)
           .order_by(func.sum(Score.points).desc())
           .first())
    return StatsOut(
        total_users=db.query(User).count(),
        total_scores=db.query(Score).count(),
        total_badges_earned=db.query(UserBadge).count(),
        total_levels=db.query(Level).count(),
        total_enigmas=db.query(Enigma).count(),
        top_player=top.pseudo if top else None,
        top_score=int(top.pts or 0) if top else 0,
    )

@router.get("/users")
def list_users(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        total_pts = db.query(func.sum(Score.points)).filter(Score.user_id == u.id).scalar() or 0
        badges_count = db.query(UserBadge).filter(UserBadge.user_id == u.id).count()
        result.append({
            "id": u.id, "pseudo": u.pseudo, "email": u.email,
            "is_admin": u.is_admin, "is_active": u.is_active, "is_verified": u.is_verified,
            "auth_provider": u.auth_provider.value if hasattr(u.auth_provider, 'value') else str(u.auth_provider),
            "created_at": u.created_at.isoformat(),
            "total_points": total_pts, "badges_count": badges_count,
        })
    return result

@router.patch("/users/{user_id}")
def update_user(user_id: int, body: UserUpdateRequest, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "Utilisateur introuvable")
    if body.is_admin is not None:    user.is_admin = body.is_admin
    if body.is_active is not None:   user.is_active = body.is_active
    if body.is_verified is not None: user.is_verified = body.is_verified
    db.commit()
    return {"message": "Utilisateur mis à jour"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    if user_id == admin.id: raise HTTPException(400, "Impossible de supprimer votre propre compte")
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "Utilisateur introuvable")
    db.delete(user); db.commit()
    return {"message": "Utilisateur supprimé"}

@router.post("/users/{user_id}/reset-scores")
def reset_scores(user_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    db.query(Score).filter(Score.user_id == user_id).delete()
    db.commit()
    return {"message": "Scores réinitialisés"}

@router.get("/levels")
def get_levels(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    levels = db.query(Level).order_by(Level.order).all()
    return [{"id": l.id, "slug": l.slug, "name": l.name, "order": l.order,
             "is_active": l.is_active, "max_points": l.max_points,
             "enigmas_count": len(l.enigmas)} for l in levels]

@router.patch("/levels/{level_id}/toggle")
def toggle_level(level_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level: raise HTTPException(404, "Niveau introuvable")
    level.is_active = not level.is_active; db.commit()
    return {"message": f"Niveau {'activé' if level.is_active else 'désactivé'}", "is_active": level.is_active}

@router.get("/certificates")
def list_certificates(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    from models.certificate import Certificate
    certs = db.query(Certificate).order_by(Certificate.issued_at.desc()).all()
    result = []
    for c in certs:
        user = db.query(User).filter(User.id == c.user_id).first()
        result.append({"id": c.id, "unique_code": c.unique_code, "level": c.level,
            "score": c.score, "issued_at": c.issued_at.isoformat(),
            "user_pseudo": user.pseudo if user else "?", "user_email": user.email if user else "?"})
    return result

@router.delete("/certificates/{cert_id}")
def delete_certificate(cert_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    from models.certificate import Certificate
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert: raise HTTPException(404, "Certificat introuvable")
    db.delete(cert); db.commit()
    return {"message": "Certificat supprimé"}

@router.get("/badges")
def list_badges(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    badges = db.query(Badge).all()
    return [{"id": b.id, "slug": b.slug, "name": b.name, "icon": b.icon,
             "color": b.color, "points_reward": b.points_reward,
             "earned_count": db.query(UserBadge).filter(UserBadge.badge_id == b.id).count()} for b in badges]