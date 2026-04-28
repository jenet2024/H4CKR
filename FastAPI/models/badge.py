from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base


class Badge(Base):
    __tablename__ = "badges"

    id          = Column(Integer, primary_key=True, index=True)
    slug        = Column(String(100), unique=True, nullable=False)
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon        = Column(String(10), nullable=False)    # emoji
    color       = Column(String(20), default="#39ff14")
    condition   = Column(String(255), nullable=False)   # description condition
    points_reward = Column(Integer, default=0)

    users = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    __tablename__ = "user_badges"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id   = Column(Integer, ForeignKey("badges.id"), nullable=False)
    earned_at  = Column(DateTime, default=datetime.utcnow)

    user  = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="users")


class Certificate(Base):
    __tablename__ = "certificates"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    level        = Column(String(50), nullable=False)   # "beginner" | "expert"
    score        = Column(Integer, default=0)
    issued_at    = Column(DateTime, default=datetime.utcnow)
    pdf_path     = Column(String(512), nullable=True)
    unique_code  = Column(String(64), unique=True, nullable=False)

    user = relationship("User", back_populates="certificates")
