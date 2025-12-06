from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    @staticmethod
    def from_env():
        return DatabaseConfig(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db_name=os.getenv("DB_NAME"),
            erp_db_schema_name=os.getenv("ERP_DB_SCHEMA_NAME", "public"),
        )

    def __init__(self, host, port, user, password, db_name, erp_db_schema_name):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.erp_db_schema_name = erp_db_schema_name

    def get_database_url(self):
        # Use asyncpg for async operations
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


# Initialize database configuration
DATABASE_URL = DatabaseConfig.from_env().get_database_url()

# Create async engine
engine = create_async_engine(
    url=DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,  # Set to True for SQL query logging
)

# Create async sessionmaker
sessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for declarative models
Base = declarative_base()


# Async dependency function for FastAPI
async def get_db_session():
    """
    Async database dependency for FastAPI routes.
    Yields a database session and ensures it's closed after use.
    """
    async with sessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
