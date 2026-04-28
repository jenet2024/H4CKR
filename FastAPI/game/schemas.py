from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Levels ────────────────────────────────────────────────────────────────────

class EnigmaOut(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    type: str
    file_path: Optional[str] = None
    points: int
    order: int
    solved: bool = False
    hints_used: int = 0

    class Config:
        from_attributes = True


class LevelOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    order: int
    video_file: Optional[str] = None
    max_points: int
    enigmas: List[EnigmaOut] = []

    class Config:
        from_attributes = True


# ── Answers ───────────────────────────────────────────────────────────────────

class AnswerRequest(BaseModel):
    enigma_id: int
    answer: str


class AnswerResponse(BaseModel):
    correct: bool
    message: str
    points_earned: int = 0
    hint: Optional[str] = None
    badge_earned: Optional["BadgeOut"] = None


# ── Terminal ──────────────────────────────────────────────────────────────────

class TerminalCommand(BaseModel):
    command: str
    enigma_id: Optional[int] = None


class TerminalResponse(BaseModel):
    output: str
    success: bool = False
    points_earned: int = 0


# ── Scores ────────────────────────────────────────────────────────────────────

class ScoreOut(BaseModel):
    id: int
    user_id: int
    level_id: int
    points: int
    time_spent: int
    attempts: int
    created_at: datetime

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    pseudo: str
    avatar_url: Optional[str] = None
    total_points: int
    badges_count: int
    level_reached: str


# ── Badges ────────────────────────────────────────────────────────────────────

class BadgeOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    icon: str
    color: str
    points_reward: int

    class Config:
        from_attributes = True


# ── Certificate ───────────────────────────────────────────────────────────────

class CertificateOut(BaseModel):
    id: int
    level: str
    score: int
    issued_at: datetime
    unique_code: str
    pdf_path: Optional[str] = None

    class Config:
        from_attributes = True


# ── Contact ───────────────────────────────────────────────────────────────────

class ContactRequest(BaseModel):
    subject: str
    message: str
    category: str = "bug"   # bug | suggestion | other


AnswerResponse.model_rebuild()
