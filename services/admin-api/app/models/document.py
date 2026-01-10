"""
Document model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filing_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    encrypted = Column(Boolean, default=False, nullable=False)
    encryption_key_hash = Column(String(255), nullable=True)
    
    section_name = Column(String(100), nullable=True)
    question_id = Column(String(50), nullable=True, index=True)
    question_name = Column(String(255), nullable=True)
    question_key = Column(String(200), nullable=True)
    document_type = Column(String(100), nullable=False)
    document_requirement_label = Column(String(255), nullable=True)
    
    status = Column(String(20), nullable=False, default="pending", index=True)
    notes = Column(Text, nullable=True)
    
    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    t1_form_id = Column(UUID(as_uuid=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


