from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id: int = Column(Integer, unique=True, nullable=False)
    username: Optional[str] = Column(String, nullable=True)
    current_state: Optional[str] = Column(String, nullable=True)
    exam_type: Optional[str] = Column(String, nullable=True)
    skill_type: Optional[str] = Column(String, nullable=True)
    mode: Optional[str] = Column(String, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    last_interaction: datetime = Column(DateTime, default=datetime.utcnow)
    settings: dict = Column(JSON, default={})

    def __repr__(self) -> str:
        return f"User(id={self.id}, telegram_id={self.telegram_id})"
