from collections.abc import AsyncGenerator
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  , async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship  
from datetime import datetime
# THIS IS A LOCAL DATABASE URL FOR TESTING PURPOSES. IN PRODUCTION, YOU WOULD USE A DIFFERENT DATABASE URL.
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    pass
class Post(Base):

    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    caption = Column(Text)
    url = Column(Text, nullable=False)
    file_type = Column(String, nullable=False)
    created_at = Column(DateTime,  nullable=False)
    updated_at = Column(DateTime,  nullable=False)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session