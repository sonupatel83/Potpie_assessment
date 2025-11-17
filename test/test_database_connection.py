from sqlalchemy import create_engine
from logger import logging

DATABASE_URL = "postgresql+psycopg2://postgres:sunny@localhost:5432/github_data_test_AI_agent"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        logging.info("Database connection successful!")
        print("Connection successful!")
except Exception as e:
    logging.error(f"Database connection failed: {e}")
    print(f"Connection failed: {e}")
