from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    tasks = relationship("Task", back_populates="agent")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending", index=True)  # pending, running, completed, failed

    # Внешние ключи
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Результаты
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    progress = Column(Float, default=0.0)

    # Дополнительные данные
    task_metadata = Column(JSON, nullable=True)

    # Отношения
    project = relationship("Project", back_populates="tasks")
    agent = relationship("Agent", back_populates="tasks")