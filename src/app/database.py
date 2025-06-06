from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from contextlib import contextmanager
from app.core.config import settings

# Always use the unified settings config for DB URL
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Create the declarative base
Base = declarative_base()

def get_db() -> Session:
    """Dependency for getting a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def init_db():
    """Initialize the database by creating all tables"""
    from . import models  # Import models here to avoid circular imports
    Base.metadata.create_all(bind=engine)
