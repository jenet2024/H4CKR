from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base


class Score(Base):
    __tablename__ = "scores"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    level_id   = Column(Integer, ForeignKey("levels.id"), nullable=False)
    points     = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)   # secondes
    attempts   = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user  = relationship("User", back_populates="scores")
    level = relationship("Level", back_populates="scores")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    level_id       = Column(Integer, ForeignKey("levels.id"), nullable=False)
    enigma_id      = Column(String(100), nullable=False)
    solved         = Column(Integer, default=0)   # 0=not started, 1=solved
    hints_used     = Column(Integer, default=0)
    solved_at      = Column(DateTime, nullable=True)

    user  = relationship("User", back_populates="progresses")
    level = relationship("Level")
