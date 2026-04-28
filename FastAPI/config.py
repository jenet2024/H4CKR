from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "H4CKR"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/h4ckr_game"

    # JWT
    SECRET_KEY: str = "CHANGE_ME_SUPER_SECRET_KEY_256_BITS"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth Google
    GOOGLE_CLIENT_ID: str = "YOUR_GOOGLE_CLIENT_ID"
    GOOGLE_CLIENT_SECRET: str = "YOUR_GOOGLE_CLIENT_SECRET"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # OAuth Twitter
    TWITTER_CLIENT_ID: str = "YOUR_TWITTER_CLIENT_ID"
    TWITTER_CLIENT_SECRET: str = "YOUR_TWITTER_CLIENT_SECRET"
    TWITTER_REDIRECT_URI: str = "http://localhost:8000/auth/twitter/callback"

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # Assets
    ASSETS_DIR: str = "./assets"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
