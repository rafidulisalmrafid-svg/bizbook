import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.config import settings

# Engine configuration
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Sync engine for Alembic and sync tools
sync_connect_args = {"check_same_thread": False} if "sqlite" in settings.SYNC_DATABASE_URL else {}
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False,
    connect_args=sync_connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
