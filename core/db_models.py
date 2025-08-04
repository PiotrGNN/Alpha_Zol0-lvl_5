from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://zol0_postgres_user:password@localhost:5432/zol0_postgres"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Decision(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    decision = Column(String(32), nullable=False)
    details = Column(Text)


class Equity(Base):
    __tablename__ = "equity"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    equity = Column(Float, nullable=False)
    pnl = Column(Float, nullable=False)


# Model logów do bazy
class LogEntry(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    event = Column(String(64), nullable=False)
    details = Column(Text)


def init_db():
    Base.metadata.create_all(bind=engine)
