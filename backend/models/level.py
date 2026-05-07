from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base


class Level(Base):
    __tablename__ = "levels"

    id          = Column(Integer, primary_key=True, index=True)
    slug        = Column(String(50), unique=True, nullable=False)  # "beginner" | "expert"
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    order       = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    video_file  = Column(String(255), nullable=True)   # assets/videos/level1_intro.mp4
    max_points  = Column(Integer, default=1000)

    scores  = relationship("Score", back_populates="level")
    enigmas = relationship("Enigma", back_populates="level", order_by="Enigma.order")


class Enigma(Base):
    __tablename__ = "enigmas"

    id           = Column(Integer, primary_key=True, index=True)
    level_id     = Column(Integer, ForeignKey("levels.id"), nullable=False)
    slug         = Column(String(100), nullable=False)
    title        = Column(String(200), nullable=False)
    description  = Column(Text, nullable=False)
    type         = Column(String(50), nullable=False)
    # Types: base64 | caesar | stegano | audio | logs | terminal | metadata
    file_path    = Column(String(512), nullable=True)   # fichier associé
    hint1        = Column(Text, nullable=True)
    hint2        = Column(Text, nullable=True)
    hint3        = Column(Text, nullable=True)
    answer_hash  = Column(String(255), nullable=False)  # bcrypt hash de la réponse
    points       = Column(Integer, default=100)
    order        = Column(Integer, default=0)
    is_active    = Column(Boolean, default=True)

    level = relationship("Level", back_populates="enigmas")
