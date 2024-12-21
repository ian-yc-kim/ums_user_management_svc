from sqlalchemy import Column, PrimaryKeyConstraint, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from ums_user_management_svc.config import Database

Base = declarative_base()

engine = create_engine(Database.url)
SessionLocal = sessionmaker(bind=engine)


def get_session() -> Session:
    session = scoped_session(sessionmaker(bind=engine))
    try:
        yield session
    finally:
        session.close()