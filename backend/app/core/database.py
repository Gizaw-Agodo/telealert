from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession , async_sessionmaker
from app.core.config import settings
from app.models import Base 


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,               
    pool_pre_ping=True, 
    pool_size=10, 
    max_overflow=20
    ) 

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session: 
        yield session