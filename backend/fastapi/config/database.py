from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import Engine
import os
import asyncio
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# Get database connection details from environment variables or use defaults
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "twaaos")

# Update the URL to use async driver
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

# Async dependency to get DB session with improved transaction management
async def get_db():
    session = SessionLocal()
    try:
        yield session
        # If we get here without an exception, commit the transaction
        # This will only be executed after the dependent function has completed
        await session.commit()
    except Exception as e:
        # If an error occurs, rollback the transaction
        await session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        # Always close the session
        await session.close()