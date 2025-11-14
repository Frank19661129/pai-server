"""
FastAPI dependencies for dependency injection.
Following Clean Architecture principles.
"""
from typing import Generator
from sqlalchemy.orm import Session
from app.infrastructure.database.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Automatically closes the session after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
