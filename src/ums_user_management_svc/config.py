import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DOMAIN_URL = os.getenv('DOMAIN_URL')

class Database:
    url = os.getenv('DATABASE_URL')

engine = create_engine(Database.url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
