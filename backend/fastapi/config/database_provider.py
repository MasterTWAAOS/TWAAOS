from typing import AsyncGenerator
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import SessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session.
    
    This function is used by the dependency injector to provide a database session
    to the repositories. It properly handles closing the async session.
    
    Returns:
        AsyncSession: An async database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Properly await the close coroutine
        await db.close()
