from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import httpx
import secrets

from database.db import get_db
from models.user import User, AuthProvider
from auth.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user,
)
from auth.schemas import (
    RegisterRequest, LoginRequest,
    TokenResponse, RefreshRequest, UserOut, OAuthCallbackRequest,
)
from config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Helper ────────────────────────────────────────────────────────────────────

def _build_token_response(user: User) -> TokenResponse:
    access  = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserOut.model_validate(user),
    )


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email déjà utilisé")
    if db.query(User).filter(User.pseudo == body.pseudo).first():
        raise HTTPException(400, "Pseudo déjà pris")

    user = User(
        pseudo=body.pseudo,
        email=body.email,
        hashed_password=hash_password(body.password),
        auth_provider=AuthProvider.LOCAL,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _build_token_response(user)


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password or ""):
        raise HTTPException(401, "Email ou mot de passe incorrect")
    if not user.is_active:
        raise HTTPException(403, "Compte désactivé")

    user.last_login = datetime.utcnow()
    db.commit()
    return _build_token_response(user)


# ── Refresh token ─────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Token de refresh invalide")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(401, "Utilisateur introuvable")
    return _build_token_response(user)


# ── Me ────────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ── OAuth Google ──────────────────────────────────────────────────────────────

@router.get("/google")
def google_login():
    """Redirect vers la page d'autorisation Google."""
    if settings.GOOGLE_CLIENT_ID == "YOUR_GOOGLE_CLIENT_ID":
        raise HTTPException(501, "OAuth Google non configuré — ajoutez vos clés dans .env")

    state = secrets.token_urlsafe(16)
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
        f"&state={state}"
    )
    return RedirectResponse(url)

# get de tous les users avec le * all pour tour le monde 

@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserOut.model_validate(u) for u in users]


@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Échange le code contre un token Google et connecte/crée l'utilisateur."""
    async with httpx.AsyncClient() as client:
        # Échange code → token
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_data = token_res.json()
        if "error" in token_data:
            raise HTTPException(400, f"Erreur Google OAuth : {token_data['error']}")

        # Récupère les infos utilisateur
        user_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        info = user_res.json()

    user = db.query(User).filter(User.oauth_id == info["id"]).first()
    if not user:
        user = db.query(User).filter(User.email == info["email"]).first()
        if user:
            user.oauth_id = info["id"]
            user.auth_provider = AuthProvider.GOOGLE
        else:
            pseudo_base = info.get("name", "hacker").replace(" ", "_").lower()[:40]
            pseudo = pseudo_base
            i = 1
            while db.query(User).filter(User.pseudo == pseudo).first():
                pseudo = f"{pseudo_base}_{i}"
                i += 1

            user = User(
                pseudo=pseudo,
                email=info["email"],
                avatar_url=info.get("picture"),
                auth_provider=AuthProvider.GOOGLE,
                oauth_id=info["id"],
                is_verified=True,
            )
            db.add(user)

    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return _build_token_response(user)


# ── OAuth Twitter ─────────────────────────────────────────────────────────────

@router.get("/twitter")
def twitter_login():
    """Redirect vers la page d'autorisation Twitter/X."""
    if settings.TWITTER_CLIENT_ID == "YOUR_TWITTER_CLIENT_ID":
        raise HTTPException(501, "OAuth Twitter non configuré — ajoutez vos clés dans .env")

    state = secrets.token_urlsafe(16)
    url = (
        "https://twitter.com/i/oauth2/authorize"
        f"?client_id={settings.TWITTER_CLIENT_ID}"
        f"&redirect_uri={settings.TWITTER_REDIRECT_URI}"
        "&response_type=code"
        "&scope=tweet.read users.read offline.access"
        "&code_challenge=challenge"
        "&code_challenge_method=plain"
        f"&state={state}"
    )
    return RedirectResponse(url)


@router.get("/twitter/callback", response_model=TokenResponse)
async def twitter_callback(code: str, db: Session = Depends(get_db)):
    """Échange le code contre un token Twitter et connecte/crée l'utilisateur."""
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://api.twitter.com/2/oauth2/token",
            data={
                "code": code,
                "client_id": settings.TWITTER_CLIENT_ID,
                "redirect_uri": settings.TWITTER_REDIRECT_URI,
                "grant_type": "authorization_code",
                "code_verifier": "challenge",
            },
            auth=(settings.TWITTER_CLIENT_ID, settings.TWITTER_CLIENT_SECRET),
        )
        token_data = token_res.json()
        if "error" in token_data:
            raise HTTPException(400, f"Erreur Twitter OAuth : {token_data['error']}")

        user_res = await client.get(
            "https://api.twitter.com/2/users/me?user.fields=profile_image_url",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        info = user_res.json().get("data", {})

    user = db.query(User).filter(User.oauth_id == info["id"]).first()
    if not user:
        pseudo_base = info.get("username", "hacker")[:40]
        pseudo = pseudo_base
        i = 1
        while db.query(User).filter(User.pseudo == pseudo).first():
            pseudo = f"{pseudo_base}_{i}"
            i += 1

        user = User(
            pseudo=pseudo,
            email=f"{info['id']}@twitter.placeholder",
            avatar_url=info.get("profile_image_url"),
            auth_provider=AuthProvider.TWITTER,
            oauth_id=info["id"],
            is_verified=True,
        )
        db.add(user)

    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return _build_token_response(user)
