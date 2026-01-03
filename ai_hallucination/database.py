import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from dotenv import load_dotenv

# Only needed for local testing; Render provides env vars automatically
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ADD THIS CHECK: Prevents the "ArgumentError" if Render hasn't loaded the key yet
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check your Render Environment tab!")

# Future=True is now default in 2.0, but echo=True helps you see SQL logs in Render
engine = create_async_engine(DATABASE_URL, echo=True, connect_args={"ssl": True})

# Use async_sessionmaker for cleaner session creation
async_session_factory = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session