"""
Project model for organizing user stories and documents
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import enum

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectType(str, enum.Enum):
    """Project type enumeration"""
    SOFTWARE_DEVELOPMENT = "software_development"
    BUSINESS_ANALYSIS = "business_analysis"
    REQUIREMENTS_GATHERING = "requirements_gathering"
    PRODUCT_MANAGEMENT = "product_management"
    RESEARCH = "research"
    CONSULTING = "consulting"
    OTHER = "other"


class TeamRole(str, enum.Enum):
    """Team member role enumeration"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"


# Association table for project team members
project_team_members = Table(
    'project_team_members',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('role', String(20), default=TeamRole.CONTRIBUTOR.value, nullable=False),
    Column('joined_at', DateTime, default=func.now(), nullable=False),
    Column('permissions', JSON, default=list),
    Column('is_active', Boolean, default=True, nullable=False)
)


class Project(Base):
    """
    Project model for organizing user stories and documents
    """
    __tablename__ = "projects"

    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, index=True, nullable=False)  # Short project key (e.g., "PROJ-001")
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Project details
    project_type = Column(SQLEnum(ProjectType), nullable=False, default=ProjectType.SOFTWARE_DEVELOPMENT)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.ACTIVE)
    
    # Dates
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    # Configuration
    settings = Column(JSON, default=dict)  # Project-specific settings
    preferences = Column(JSON, default=dict)  # User story generation preferences
    
    # Integration settings
    jira_project_key = Column(String(50), nullable=True)
    jira_project_id = Column(String(50), nullable=True)
    confluence_space_key = Column(String(50), nullable=True)
    sharepoint_site_id = Column(String(255), nullable=True)
    
    # AI/LLM configuration
    default_llm_provider = Column(String(50), nullable=True)
    llm_settings = Column(JSON, default=dict)
    prompt_templates = Column(JSON, default=dict)
    
    # Access control
    is_public = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    access_level = Column(String(20), default="private")  # private, team, public
    
    # Analytics and metrics
    total_documents = Column(Integer, default=0)
    total_user_stories = Column(Integer, default=0)
    total_requirements = Column(Integer, default=0)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    
    # Team members (many-to-many relationship)
    team_members = relationship(
        "User",
        secondary=project_team_members,
        back_populates="projects"
    )
    
    # Project content
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    user_stories = relationship("UserStory", back_populates="project", cascade="all, delete-orphan")
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    def __init__(self, **kwargs):
        # Set default settings and preferences
        default_settings = {
            "auto_process_documents": True,
            "enable_knowledge_graph": True,
            "notification_settings": {
                "document_processed": True,
                "story_generated": True,
                "integration_errors": True
            },
            "generation_settings": {
                "max_stories_per_batch": 50,
                "include_acceptance_criteria": True,
                "include_story_points": True,
                "default_priority": "Medium"
            }
        }
        
        default_preferences = {
            "story_format": "As a [user], I want [goal] so that [reason]",
            "include_technical_details": False,
            "generate_sub_tasks": False,
            "default_estimation_unit": "story_points",
            "quality_threshold": 0.7
        }
        
        default_prompt_templates = {
            "user_story_generation": {
                "system": "You are an expert business analyst. Generate well-structured user stories from requirements.",
                "user": "Generate user stories from the following requirements: {requirements}"
            },
            "acceptance_criteria": {
                "system": "Generate clear, testable acceptance criteria for user stories.",
                "user": "Generate acceptance criteria for: {user_story}"
            }
        }
        
        if 'settings' not in kwargs:
            kwargs['settings'] = default_settings
        if 'preferences' not in kwargs:
            kwargs['preferences'] = default_preferences
        if 'prompt_templates' not in kwargs:
            kwargs['prompt_templates'] = default_prompt_templates
            
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<Project(id={self.id}, key='{self.key}', name='{self.name}')>"
    
    def __str__(self):
        return f"{self.key}: {self.name}"
    
    @property
    def display_name(self) -> str:
        """Get project display name"""
        return f"{self.key} - {self.name}"
    
    @property
    def is_overdue(self) -> bool:
        """Check if project is overdue"""
        if self.deadline:
            return datetime.utcnow() > self.deadline
        return False
    
    @property
    def days_until_deadline(self) -> Optional[int]:
        """Get days until deadline"""
        if self.deadline:
            delta = self.deadline - datetime.utcnow()
            return delta.days
        return None
    
    @property
    def progress_percentage(self) -> float:
        """Calculate project progress based on completed user stories"""
        if self.total_user_stories == 0:
            return 0.0
        
        completed_stories = sum(
            1 for story in self.user_stories 
            if story.status in ["done", "completed", "accepted"]
        )
        return (completed_stories / self.total_user_stories) * 100
    
    def add_team_member(self, user_id: int, role: TeamRole = TeamRole.CONTRIBUTOR, permissions: List[str] = None):
        """Add a team member to the project"""
        # This would be implemented in the service layer
        # The relationship is handled through the association table
        pass
    
    def remove_team_member(self, user_id: int):
        """Remove a team member from the project"""
        # This would be implemented in the service layer
        pass
    
    def get_team_member_role(self, user_id: int) -> Optional[str]:
        """Get the role of a team member"""
        # This would query the association table
        # For now, return basic logic
        if user_id == self.owner_id:
            return TeamRole.OWNER.value
        return TeamRole.CONTRIBUTOR.value
    
    def can_user_access(self, user_id: int) -> bool:
        """Check if user can access the project"""
        if self.is_public:
            return True
        
        if user_id == self.owner_id:
            return True
        
        # Check if user is team member
        return any(member.id == user_id for member in self.team_members)
    
    def can_user_edit(self, user_id: int) -> bool:
        """Check if user can edit the project"""
        if user_id == self.owner_id:
            return True
        
        role = self.get_team_member_role(user_id)
        return role in [TeamRole.ADMIN.value, TeamRole.MANAGER.value]
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity_at = datetime.utcnow()
    
    def increment_document_count(self):
        """Increment document count"""
        self.total_documents += 1
        self.update_activity()
    
    def increment_user_story_count(self):
        """Increment user story count"""
        self.total_user_stories += 1
        self.update_activity()
    
    def increment_requirements_count(self, count: int = 1):
        """Increment requirements count"""
        self.total_requirements += count
        self.update_activity()
    
    def get_integration_config(self, integration_type: str) -> Optional[Dict[str, Any]]:
        """Get integration configuration"""
        integrations = {
            "jira": {
                "project_key": self.jira_project_key,
                "project_id": self.jira_project_id,
                "enabled": bool(self.jira_project_key)
            },
            "confluence": {
                "space_key": self.confluence_space_key,
                "enabled": bool(self.confluence_space_key)
            },
            "sharepoint": {
                "site_id": self.sharepoint_site_id,
                "enabled": bool(self.sharepoint_site_id)
            }
        }
        return integrations.get(integration_type)
    
    def set_integration_config(self, integration_type: str, config: Dict[str, Any]):
        """Set integration configuration"""
        if integration_type == "jira":
            self.jira_project_key = config.get("project_key")
            self.jira_project_id = config.get("project_id")
        elif integration_type == "confluence":
            self.confluence_space_key = config.get("space_key")
        elif integration_type == "sharepoint":
            self.sharepoint_site_id = config.get("site_id")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for the project"""
        return {
            "provider": self.default_llm_provider,
            "settings": self.llm_settings or {},
            "prompt_templates": self.prompt_templates or {}
        }
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update project settings"""
        current_settings = self.settings or {}
        current_settings.update(new_settings)
        self.settings = current_settings
    
    def update_preferences(self, new_preferences: Dict[str, Any]):
        """Update project preferences"""
        current_preferences = self.preferences or {}
        current_preferences.update(new_preferences)
        self.preferences = current_preferences
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get project statistics"""
        return {
            "total_documents": self.total_documents,
            "total_user_stories": self.total_user_stories,
            "total_requirements": self.total_requirements,
            "progress_percentage": self.progress_percentage,
            "team_members_count": len(self.team_members),
            "is_overdue": self.is_overdue,
            "days_until_deadline": self.days_until_deadline,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None
        }
    
    def to_dict(self, include_team: bool = False, include_stats: bool = False) -> Dict[str, Any]:
        """Convert project to dictionary"""
        data = {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "project_type": self.project_type.value,
            "status": self.status.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "is_public": self.is_public,
            "is_active": self.is_active,
            "access_level": self.access_level,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "settings": self.settings or {},
            "preferences": self.preferences or {},
            "integrations": {
                "jira": self.get_integration_config("jira"),
                "confluence": self.get_integration_config("confluence"),
                "sharepoint": self.get_integration_config("sharepoint")
            },
            "llm_config": self.get_llm_config()
        }
        
        if include_team:
            data["team_members"] = [
                {
                    "id": member.id,
                    "username": member.username,
                    "full_name": member.full_name,
                    "email": member.email,
                    "role": self.get_team_member_role(member.id)
                }
                for member in self.team_members
            ]
        
        if include_stats:
            data["statistics"] = self.get_statistics()
        
        return data


class ProjectTemplate(Base):
    """
    Project template model for creating standardized projects
    """
    __tablename__ = "project_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template configuration
    project_type = Column(SQLEnum(ProjectType), nullable=False)
    default_settings = Column(JSON, default=dict)
    default_preferences = Column(JSON, default=dict)
    default_prompt_templates = Column(JSON, default=dict)
    
    # Template structure
    document_templates = Column(JSON, default=list)  # List of document template IDs
    workflow_templates = Column(JSON, default=list)  # Predefined workflows
    
    # Usage and visibility
    is_public = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    usage_count = Column(Integer, default=0)
    
    # Relationships
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<ProjectTemplate(id={self.id}, name='{self.name}', type='{self.project_type}')>"
    
    def create_project(self, name: str, key: str, owner_id: int, **kwargs) -> Project:
        """Create a new project from this template"""
        project_data = {
            "name": name,
            "key": key,
            "owner_id": owner_id,
            "project_type": self.project_type,
            "settings": self.default_settings.copy(),
            "preferences": self.default_preferences.copy(),
            "prompt_templates": self.default_prompt_templates.copy(),
            **kwargs
        }
        
        # Increment usage count
        self.usage_count += 1
        
        return Project(**project_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type.value,
            "default_settings": self.default_settings or {},
            "default_preferences": self.default_preferences or {},
            "default_prompt_templates": self.default_prompt_templates or {},
            "document_templates": self.document_templates or [],
            "workflow_templates": self.workflow_templates or [],
            "is_public": self.is_public,
            "is_active": self.is_active,
            "usage_count": self.usage_count,
            "created_by_id": self.created_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ProjectInvitation(Base):
    """
    Project invitation model for inviting users to projects
    """
    __tablename__ = "project_invitations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Invitation details
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(20), default=TeamRole.CONTRIBUTOR.value, nullable=False)
    permissions = Column(JSON, default=list)
    message = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default="pending", nullable=False)  # pending, accepted, declined, expired
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Response
    responded_at = Column(DateTime, nullable=True)
    response_message = Column(Text, nullable=True)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    accepted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    project = relationship("Project")
    invited_by = relationship("User", foreign_keys=[invited_by_id])
    accepted_by = relationship("User", foreign_keys=[accepted_by_id])
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<ProjectInvitation(id={self.id}, email='{self.email}', project_id={self.project_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if invitation is expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_pending(self) -> bool:
        """Check if invitation is still pending"""
        return self.status == "pending" and not self.is_expired
    
    def accept(self, user_id: int, message: str = None):
        """Accept the invitation"""
        self.status = "accepted"
        self.accepted_by_id = user_id
        self.responded_at = datetime.utcnow()
        self.response_message = message
    
    def decline(self, message: str = None):
        """Decline the invitation"""
        self.status = "declined"
        self.responded_at = datetime.utcnow()
        self.response_message = message
    
    def expire(self):
        """Mark invitation as expired"""
        self.status = "expired"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert invitation to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "permissions": self.permissions or [],
            "message": self.message,
            "status": self.status,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired,
            "is_pending": self.is_pending,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "response_message": self.response_message,
            "project_id": self.project_id,
            "invited_by_id": self.invited_by_id,
            "accepted_by_id": self.accepted_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }