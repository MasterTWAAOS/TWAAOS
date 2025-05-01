from typing import Iterator
from sqlalchemy.orm import Session

from config.database import SessionLocal


def get_db_session() -> Session:
    """Provide a database session.
    
    This function is used by the dependency injector to provide a database session
    to the repositories.
    
    Returns:
        Session: A database session
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
