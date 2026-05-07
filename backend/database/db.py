from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()

# engine = create_engine(
#     settings.DATABASE_URL,
#     connect_args={"check_same_thread": False},  # SQLite only
# )


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency injection — FastAPI route."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables on startup."""
    from models import user, score, badge, level  # noqa: F401 — import triggers table creation
    Base.metadata.create_all(bind=engine)
