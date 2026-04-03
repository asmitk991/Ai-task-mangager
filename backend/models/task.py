from sqlalchemy import Column, Date, DateTime, Integer, String, Text, func

from database.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(Date, nullable=True)
    priority = Column(String(20), nullable=False, default="medium")
    category = Column(String(100), nullable=False, default="general")
    status = Column(String(30), nullable=False, default="pending")
    raw_input = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
