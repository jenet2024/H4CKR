from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database.db import Base


class AuthProvider(str, enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"
    TWITTER = "twitter"


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    pseudo        = Column(String(50), unique=True, index=True, nullable=False)
    email         = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)       # null if OAuth
    avatar_url    = Column(String(512), nullable=True)

    # OAuth
    auth_provider = Column(Enum(AuthProvider), default=AuthProvider.LOCAL)
    oauth_id      = Column(String(255), nullable=True, unique=True)

    # Status
    is_active     = Column(Boolean, default=True)
    is_verified   = Column(Boolean, default=False)
    is_admin      = Column(Boolean, default=False)

    # Dates
    created_at    = Column(DateTime, default=datetime.utcnow)
    last_login    = Column(DateTime, nullable=True)

    # Relations
    scores        = relationship("Score", back_populates="user", cascade="all, delete-orphan")
    badges        = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    progresses    = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    certificates  = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.pseudo}>"
