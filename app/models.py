from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    sub_category = Column(String)
    seo_tags = Column(Text)  # JSON string
    sustainability_filters = Column(Text)  # JSON string
    confidence_score = Column(Float)
    created_at = Column(DateTime, server_default=func.now())


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    industry = Column(String)
    budget = Column(Float)
    generated_proposal = Column(Text)  # JSON string
    created_at = Column(DateTime, server_default=func.now())


class AILog(Base):
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String, nullable=False)
    prompt_sent = Column(Text)
    response_received = Column(Text)
    tokens_used = Column(Integer, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
