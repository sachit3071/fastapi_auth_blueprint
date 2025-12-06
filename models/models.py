from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from config.database import DatabaseConfig
from sqlalchemy import MetaData
from datetime import datetime

metadata = MetaData(schema=DatabaseConfig.from_env().erp_db_schema_name)
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": DatabaseConfig.from_env().erp_db_schema_name}

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    creation_date = Column(DateTime, nullable=False, default=datetime.now())
    last_updated_date = Column(DateTime, nullable=False, default=datetime.now())
    refresh_token = Column(String(255), nullable=False)
    access_token = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
