"""
Database models and schemas
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

Base = declarative_base()


# SQLAlchemy Models (PostgreSQL)
class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Message model"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON)  # Sources, steps, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class UserSettings(Base):
    """User settings and personalization"""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    custom_prompts = Column(JSON)  # Array of custom prompts
    preferences = Column(JSON)  # UI preferences, display settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="settings")


class Feedback(Base):
    """Feedback model for learning"""
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"))
    rating = Column(Integer)  # 1-5 or thumbs up/down
    comment = Column(Text)
    query_embedding = Column(JSON)  # Store embedding for similarity search
    improved_response = Column(Text)  # If user provides better answer
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="feedbacks")


class KnowledgeEntry(Base):
    """Learned knowledge from feedback"""
    __tablename__ = "knowledge_entries"

    id = Column(Integer, primary_key=True, index=True)
    query_pattern = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    entry_metadata = Column(JSON)  # Context, domain, etc.
    confidence_score = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Schemas for API
class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    title: str = "New Conversation"


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    message_id: Optional[int] = None
    rating: Optional[int] = None
    comment: Optional[str] = None
    improved_response: Optional[str] = None


class UserSettingsUpdate(BaseModel):
    custom_prompts: Optional[list] = None
    preferences: Optional[Dict[str, Any]] = None


# MongoDB Document Schemas (Material/Part Information)
class MaterialDocument(BaseModel):
    """Material information stored in MongoDB"""
    materialId: str = Field(..., description="Material code (key)")
    name: str
    category: str
    specifications: Dict[str, Any]
    supplier: Optional[str] = None
    inventory: Optional[Dict[str, Any]] = None
    purchase_history: Optional[list] = None
    usage_history: Optional[list] = None
    installation_history: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = None
