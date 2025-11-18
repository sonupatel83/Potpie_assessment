from sqlalchemy import Column, String, Text, Enum, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import Config
from ..logger import logging

Base = declarative_base()
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URL
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Task(Base):
    __tablename__ = "Github_table"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String(255), nullable=False)
    status = Column(String(50), Enum("pending", "processing", "completed", "failed", name="status_enum"), default="pending")
    result = Column(Text, nullable=True)

# Table creation function
def create_tables():
    try:
        logging.info("Creating tables (if not already present)...")
        Base.metadata.create_all(bind=engine)
        logging.info("Tables created successfully.")
    except Exception as e:
        logging.error(f"Error while creating tables: {e}")
        # Don't raise - allow app to start even if table creation fails
        # This helps with connection issues during startup

# Try to create tables, but don't fail if database connection is not ready
try:
    create_tables()
except Exception as e:
    logging.warning(f"Could not create tables on import: {e}. Will retry on first use.")
