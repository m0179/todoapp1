"""
Database connection and session management.
Configures SQLAlchemy engine and session factory.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from typing import Generator

# Create database engine
# pool_pre_ping: Verify connections before using them
# echo: Log all SQL statements (useful for debugging)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    This is used as a FastAPI dependency to inject database sessions
    into route handlers. The session is automatically closed after use.
    
    Yields:
        Session: SQLAlchemy database session
    
    Example:
        @app.get("/todos")
        def get_todos(db: Session = Depends(get_db)):
            return db.query(Todo).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
