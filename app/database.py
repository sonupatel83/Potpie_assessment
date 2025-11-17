# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from .config import Config
# from sqlalchemy import create_engine, Column, String, Text
# from sqlalchemy.ext.declarative import declarative_base


# # Initialize database engine
# engine = create_engine(Config.DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()


# # Dependency for database sessions
# def get_db():
#     db = Session()
#     try:
#         yield db
#     finally:
#         db.close()

# class TaskResult(Base):
#     __tablename__ = 'task_results'
#     task_id = Column(String, primary_key=True)
#     result = Column(Text)

# Base.metadata.create_all(engine)

# def save_task_result(task_id, result):
#     session = Session()
#     task = TaskResult(task_id=task_id, result=result)
#     session.add(task)
#     session.commit()
#     session.close()
