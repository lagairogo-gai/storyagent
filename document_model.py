"""
Document model for managing requirement documents from various sources
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import enum
import os

from app.core.database import Base


class DocumentSource(str, enum.Enum):
    """Document source enumeration"""
    UPLOAD = "upload"
    JIRA = "jira"
    CONFLUENCE = "confluence"
    SHAREPOINT = "sharepoint"
    URL = "url"
    EMAIL = "email"
    API = "api"


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    REQUIREMENTS = "requirements"
    SPECIFICATION = "specification"
    USER_STORY = "user_story"
    EPIC = "epic"
    FEATURE = "feature"
    BUG_REPORT = "bug_report"
    TEST_CASE = "test_case"
    DESIGN = "design"
    MEETING_NOTES = "meeting_notes"
    EMAIL = "email"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ProcessingStage(str, enum.Enum):
    """Document processing stages"""
    UPLOADED = "uploaded"
    EXTRACTING_TEXT = "extracting_text"
    ANALYZING_CONTENT = "analyzing_content"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    BUILDING_KNOWLEDGE_GRAPH = "building_knowledge_graph"
    COMPLETED = "completed"
    ERROR = "error"


class Document(Base):
    """
    Document model for storing and managing requirement documents
    """
    __tablename__ = "documents"

    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # File information
    filename = Column(String(255), nullable=True)
    file_path = Column(String(1000), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_extension = Column(String(10), nullable=True)
    mime_type = Column(String(100), nullable=True)
    checksum = Column(String(64), nullable=True)  # SHA-256 hash
    
    # Document metadata
    source = Column(SQLEnum(DocumentSource), nullable=False, default=DocumentSource.UPLOAD)
    document_type = Column(SQLEnum(DocumentType), nullable=False, default=DocumentType.REQUIREMENTS)
    status = Column(SQLEnum(DocumentStatus), nullable=False, default=DocumentStatus.PENDING)
    processing_stage = Column(SQLEnum(ProcessingStage), nullable=False, default=ProcessingStage.UPLOADED)
    
    # Content
    raw_content = Column(Text, nullable=True)  # Original extracted text
    processed_content = Column(Text, nullable=True)  # Cleaned and processed text
    content_summary = Column(Text, nullable=True)  # AI-generated summary
    
    # Source-specific metadata
    source_metadata = Column(JSON, nullable=True)  # Jira issue data, Confluence page info, etc.
    external_id = Column(String(255), nullable=True, index=True)  # External system ID
    external_url = Column(String(1000), nullable=True)  # URL to original document
    
    # Processing metadata
    processing_log = Column(JSON, default=list)  # Processing steps and errors
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_duration = Column(Float, nullable=True)  # Duration in seconds
    
    # AI analysis results
    extracted_requirements = Column(JSON, default=list)  # Structured requirements
    identified_entities = Column(JSON, default=list)  # Named entities
    topics = Column(JSON, default=list)  # Topic classification
    sentiment_score = Column(Float, nullable=True)  # Sentiment analysis
    complexity_score = Column(Float, nullable=True)  # Document complexity
    quality_score = Column(Float, nullable=True)  # Content quality assessment
    
    # Embedding and indexing
    embedding_model = Column(String(100), nullable=True)  # Model used for embeddings
    vector_id = Column(String(255), nullable=True)  # Vector store document ID
    chunk_count = Column(Integer, default=0)  # Number of text chunks
    
    # Knowledge graph integration
    kg_entities = Column(JSON, default=list)  # Knowledge graph entities
    kg_relationships = Column(JSON, default=list)  # Relationships to other documents
    
    # Version control
    version = Column(Integer, default=1, nullable=False)
    parent_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    is_latest_version = Column(Boolean, default=True, nullable=False)
    
    # Access control
    is_public = Column(Boolean, default=False, nullable=False)
    access_level = Column(String(20), default="private")  # private, team, public
    tags = Column(JSON, default=list)  # User-defined tags
    
    # Analytics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    generation_count = Column(Integer, default=0)  # How many user stories generated from this doc
    
    # Relationships
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    uploaded_by = relationship("User", back_populates="documents")
    project = relationship("Project", back_populates="documents")
    parent_document = relationship("Document", remote_side=[id])
    child_documents = relationship("Document", back_populates="parent_document")
    
    # User stories generated from this document
    generated_user_stories = relationship("UserStory", back_populates="source_document")
    
    # Document chunks for vector search
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_accessed_at = Column(DateTime, nullable=True)

    def __init__(self, **kwargs):
        # Initialize default processing log
        if 'processing_log' not in kwargs:
            kwargs['processing_log'] = []
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', source='{self.source}')>"
    
    def __str__(self):
        return f"{self.title} ({self.source.value})"
    
    @property
    def file_size_formatted(self) -> str:
        """Get formatted file size"""
        if not self.file_size:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024
        return f"{self.file_size:.1f} TB"
    
    @property
    def processing_progress(self) -> float:
        """Calculate processing progress as percentage"""
        stage_order = [
            ProcessingStage.UPLOADED,
            ProcessingStage.EXTRACTING_TEXT,
            ProcessingStage.ANALYZING_CONTENT,
            ProcessingStage.CHUNKING,
            ProcessingStage.EMBEDDING,
            ProcessingStage.INDEXING,
            ProcessingStage.BUILDING_KNOWLEDGE_GRAPH,
            ProcessingStage.COMPLETED
        ]
        
        if self.processing_stage == ProcessingStage.ERROR:
            return 0.0
        
        try:
            current_index = stage_order.index(self.processing_stage)
            return (current_index / (len(stage_order) - 1)) * 100
        except ValueError:
            return 0.0
    
    @property
    def is_processing_complete(self) -> bool:
        """Check if document processing is complete"""
        return self.processing_stage == ProcessingStage.COMPLETED
    
    @property
    def has_content(self) -> bool:
        """Check if document has extractable content"""
        return bool(self.raw_content or self.processed_content)
    
    def add_processing_log(self, stage: str, message: str, level: str = "info", details: dict = None):
        """Add entry to processing log"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": stage,
            "level": level,
            "message": message,
            "details": details or {}
        }
        
        if self.processing_log is None:
            self.processing_log = []
        
        self.processing_log.append(log_entry)
    
    def start_processing(self):
        """Mark processing as started"""
        self.status = DocumentStatus.PROCESSING
        self.processing_started_at = datetime.utcnow()
        self.add_processing_log("processing", "Document processing started")
    
    def complete_processing(self):
        """Mark processing as completed"""
        self.status = DocumentStatus.PROCESSED
        self.processing_stage = ProcessingStage.COMPLETED
        self.processing_completed_at = datetime.utcnow()
        
        if self.processing_started_at:
            duration = (self.processing_completed_at - self.processing_started_at).total_seconds()
            self.processing_duration = duration
        
        self.add_processing_log("processing", "Document processing completed successfully")
    
    def fail_processing(self, error_message: str, details: dict = None):
        """Mark processing as failed"""
        self.status = DocumentStatus.FAILED
        self.processing_stage = ProcessingStage.ERROR
        self.add_processing_log("error", error_message, "error", details)
    
    def update_processing_stage(self, stage: ProcessingStage, message: str = None):
        """Update processing stage"""
        self.processing_stage = stage
        if message:
            self.add_processing_log(stage.value, message)
    
    def add_requirement(self, requirement: dict):
        """Add extracted requirement"""
        if self.extracted_requirements is None:
            self.extracted_requirements = []
        
        requirement["id"] = len(self.extracted_requirements) + 1
        requirement["extracted_at"] = datetime.utcnow().isoformat()
        self.extracted_requirements.append(requirement)
    
    def add_entity(self, entity: dict):
        """Add identified entity"""
        if self.identified_entities is None:
            self.identified_entities = []
        
        # Check if entity already exists
        existing = next(
            (e for e in self.identified_entities if e.get("text") == entity.get("text")),
            None
        )
        
        if not existing:
            self.identified_entities.append(entity)
    
    def add_topic(self, topic: str, confidence: float):
        """Add identified topic"""
        if self.topics is None:
            self.topics = []
        
        topic_data = {
            "topic": topic,
            "confidence": confidence,
            "identified_at": datetime.utcnow().isoformat()
        }
        self.topics.append(topic_data)
    
    def increment_view_count(self):
        """Increment view count and update last accessed time"""
        self.view_count += 1
        self.last_accessed_at = datetime.utcnow()
    
    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
    
    def increment_generation_count(self):
        """Increment user story generation count"""
        self.generation_count += 1
    
    def get_content(self) -> str:
        """Get the best available content"""
        return self.processed_content or self.raw_content or ""
    
    def has_external_source(self) -> bool:
        """Check if document has an external source"""
        return self.source in [DocumentSource.JIRA, DocumentSource.CONFLUENCE, DocumentSource.SHAREPOINT]
    
    def can_be_updated(self) -> bool:
        """Check if document can be updated from external source"""
        return self.has_external_source() and bool(self.external_id)
    
    def create_new_version(self) -> 'Document':
        """Create a new version of this document"""
        # Mark current document as not latest
        self.is_latest_version = False
        
        # Create new document version
        new_doc = Document(
            title=self.title,
            description=self.description,
            filename=self.filename,
            source=self.source,
            document_type=self.document_type,
            source_metadata=self.source_metadata,
            external_id=self.external_id,
            external_url=self.external_url,
            uploaded_by_id=self.uploaded_by_id,
            project_id=self.project_id,
            parent_document_id=self.id,
            version=self.version + 1,
            is_latest_version=True,
            tags=self.tags,
            access_level=self.access_level,
            is_public=self.is_public
        )
        
        return new_doc
    
    def to_dict(self, include_content: bool = False, include_processing: bool = False) -> dict:
        """Convert document to dictionary"""
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "filename": self.filename,
            "file_size": self.file_size,
            "file_size_formatted": self.file_size_formatted,
            "file_extension": self.file_extension,
            "mime_type": self.mime_type,
            "source": self.source.value,
            "document_type": self.document_type.value,
            "status": self.status.value,
            "processing_stage": self.processing_stage.value,
            "processing_progress": self.processing_progress,
            "is_processing_complete": self.is_processing_complete,
            "external_url": self.external_url,
            "version": self.version,
            "is_latest_version": self.is_latest_version,
            "chunk_count": self.chunk_count,
            "tags": self.tags or [],
            "view_count": self.view_count,
            "download_count": self.download_count,
            "generation_count": self.generation_count,
            "uploaded_by_id": self.uploaded_by_id,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "processing_started_at": self.processing_started_at.isoformat() if self.processing_started_at else None,
            "processing_completed_at": self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            "processing_duration": self.processing_duration
        }
        
        if include_content:
            data.update({
                "raw_content": self.raw_content,
                "processed_content": self.processed_content,
                "content_summary": self.content_summary,
                "extracted_requirements": self.extracted_requirements or [],
                "identified_entities": self.identified_entities or [],
                "topics": self.topics or [],
                "sentiment_score": self.sentiment_score,
                "complexity_score": self.complexity_score,
                "quality_score": self.quality_score,
                "kg_entities": self.kg_entities or [],
                "kg_relationships": self.kg_relationships or []
            })
        
        if include_processing:
            data.update({
                "processing_log": self.processing_log or [],
                "source_metadata": self.source_metadata
            })
        
        return data


class DocumentChunk(Base):
    """
    Document chunk model for vector search and RAG
    """
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    
    # Content
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, table, image_caption, etc.
    
    # Position and metadata
    chunk_index = Column(Integer, nullable=False)  # Position in document
    start_char = Column(Integer, nullable=True)  # Character position in original text
    end_char = Column(Integer, nullable=True)
    
    # Size metrics
    token_count = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=False)
    
    # Embedding information
    embedding_model = Column(String(100), nullable=True)
    vector_id = Column(String(255), nullable=True)  # Vector store chunk ID
    
    # Context and relationships
    section_title = Column(String(500), nullable=True)  # Document section
    page_number = Column(Integer, nullable=True)  # For PDFs
    metadata = Column(JSON, default=dict)  # Additional chunk metadata
    
    # Relationships
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    document = relationship("Document", back_populates="chunks")
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index})>"
    
    def to_dict(self) -> dict:
        """Convert chunk to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "content_type": self.content_type,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "token_count": self.token_count,
            "character_count": self.character_count,
            "section_title": self.section_title,
            "page_number": self.page_number,
            "metadata": self.metadata or {},
            "document_id": self.document_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class DocumentTemplate(Base):
    """
    Document template model for standardizing document structures
    """
    __tablename__ = "document_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template configuration
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    schema = Column(JSON, nullable=False)  # JSON schema for validation
    extraction_rules = Column(JSON, default=dict)  # Rules for content extraction
    
    # Usage
    is_active = Column(Boolean, default=True, nullable=False)
    usage_count = Column(Integer, default=0)
    
    # Relationships
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<DocumentTemplate(id={self.id}, name='{self.name}', type='{self.document_type}')>"
    
    def to_dict(self) -> dict:
        """Convert template to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "document_type": self.document_type.value,
            "schema": self.schema,
            "extraction_rules": self.extraction_rules or {},
            "is_active": self.is_active,
            "usage_count": self.usage_count,
            "created_by_id": self.created_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }