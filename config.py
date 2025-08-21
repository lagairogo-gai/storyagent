"""
Configuration settings for the RAG User Story Generator API
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional, Dict, Any
import os
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """
    
    # Application settings
    APP_NAME: str = "RAG User Story Generator"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    HOST: str = Field(default="0.0.0.0", description="Host to bind to")
    PORT: int = Field(default=8000, description="Port to bind to")
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins"
    )
    
    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/rag_user_stories",
        description="PostgreSQL database URL"
    )
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    
    # Redis settings
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # Security settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="JWT secret key"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=1440,  # 24 hours
        description="Access token expiration in minutes"
    )
    
    # Vector Database settings
    VECTOR_DB_TYPE: str = Field(
        default="chromadb",  # chromadb, pinecone, weaviate
        description="Vector database type"
    )
    CHROMA_DB_PATH: str = Field(
        default="./data/chromadb",
        description="ChromaDB storage path"
    )
    PINECONE_API_KEY: Optional[str] = Field(
        default=None,
        description="Pinecone API key"
    )
    PINECONE_ENVIRONMENT: Optional[str] = Field(
        default=None,
        description="Pinecone environment"
    )
    
    # Knowledge Graph settings (Neo4j)
    NEO4J_URI: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j connection URI"
    )
    NEO4J_USER: str = Field(default="neo4j", description="Neo4j username")
    NEO4J_PASSWORD: str = Field(
        default="password",
        description="Neo4j password"
    )
    
    # LLM Provider settings
    DEFAULT_LLM_PROVIDER: str = Field(
        default="openai",  # openai, azure, gemini, claude, ollama
        description="Default LLM provider"
    )
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI model name"
    )
    OPENAI_TEMPERATURE: float = Field(
        default=0.1,
        description="OpenAI temperature setting"
    )
    
    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="Azure OpenAI API key"
    )
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(
        default=None,
        description="Azure OpenAI endpoint"
    )
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = Field(
        default=None,
        description="Azure OpenAI deployment name"
    )
    AZURE_OPENAI_API_VERSION: str = Field(
        default="2024-02-15-preview",
        description="Azure OpenAI API version"
    )
    
    # Google Gemini settings
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-pro",
        description="Gemini model name"
    )
    
    # Anthropic Claude settings
    CLAUDE_API_KEY: Optional[str] = Field(
        default=None,
        description="Anthropic Claude API key"
    )
    CLAUDE_MODEL: str = Field(
        default="claude-3-sonnet-20240229",
        description="Claude model name"
    )
    
    # Ollama settings (for local models)
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL"
    )
    OLLAMA_MODEL: str = Field(
        default="llama2",
        description="Ollama model name"
    )
    
    # External Integration settings
    
    # Jira settings
    JIRA_SERVER_URL: Optional[str] = Field(
        default=None,
        description="Jira server URL"
    )
    JIRA_USERNAME: Optional[str] = Field(
        default=None,
        description="Jira username"
    )
    JIRA_API_TOKEN: Optional[str] = Field(
        default=None,
        description="Jira API token"
    )
    
    # Confluence settings
    CONFLUENCE_SERVER_URL: Optional[str] = Field(
        default=None,
        description="Confluence server URL"
    )
    CONFLUENCE_USERNAME: Optional[str] = Field(
        default=None,
        description="Confluence username"
    )
    CONFLUENCE_API_TOKEN: Optional[str] = Field(
        default=None,
        description="Confluence API token"
    )
    
    # SharePoint settings
    SHAREPOINT_TENANT_ID: Optional[str] = Field(
        default=None,
        description="SharePoint tenant ID"
    )
    SHAREPOINT_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="SharePoint client ID"
    )
    SHAREPOINT_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="SharePoint client secret"
    )
    SHAREPOINT_SITE_URL: Optional[str] = Field(
        default=None,
        description="SharePoint site URL"
    )
    
    # File Upload settings
    MAX_FILE_SIZE: int = Field(
        default=50 * 1024 * 1024,  # 50MB
        description="Maximum file upload size in bytes"
    )
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".docx", ".txt", ".md", ".xlsx", ".csv"],
        description="Allowed file extensions for upload"
    )
    UPLOAD_DIR: str = Field(
        default="./data/uploads",
        description="Directory for file uploads"
    )
    
    # Processing settings
    CHUNK_SIZE: int = Field(
        default=1000,
        description="Text chunk size for vector embedding"
    )
    CHUNK_OVERLAP: int = Field(
        default=200,
        description="Text chunk overlap"
    )
    
    # RAG settings
    RETRIEVAL_TOP_K: int = Field(
        default=10,
        description="Number of top documents to retrieve"
    )
    RERANK_TOP_K: int = Field(
        default=5,
        description="Number of documents after re-ranking"
    )
    
    # Background task settings
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend URL"
    )
    
    # Logging settings
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_FILE: str = Field(
        default="app.log",
        description="Log file path"
    )
    
    # Performance settings
    MAX_WORKERS: int = Field(
        default=4,
        description="Maximum number of worker processes"
    )
    REQUEST_TIMEOUT: int = Field(
        default=300,  # 5 minutes
        description="Request timeout in seconds"
    )
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def validate_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_EXTENSIONS", pre=True)
    def validate_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @property
    def llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on the selected provider"""
        configs = {
            "openai": {
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "temperature": self.OPENAI_TEMPERATURE,
            },
            "azure": {
                "api_key": self.AZURE_OPENAI_API_KEY,
                "endpoint": self.AZURE_OPENAI_ENDPOINT,
                "deployment_name": self.AZURE_OPENAI_DEPLOYMENT_NAME,
                "api_version": self.AZURE_OPENAI_API_VERSION,
            },
            "gemini": {
                "api_key": self.GEMINI_API_KEY,
                "model": self.GEMINI_MODEL,
            },
            "claude": {
                "api_key": self.CLAUDE_API_KEY,
                "model": self.CLAUDE_MODEL,
            },
            "ollama": {
                "base_url": self.OLLAMA_BASE_URL,
                "model": self.OLLAMA_MODEL,
            }
        }
        return configs.get(self.DEFAULT_LLM_PROVIDER, {})
    
    @property
    def jira_config(self) -> Optional[Dict[str, str]]:
        """Get Jira configuration if available"""
        if all([self.JIRA_SERVER_URL, self.JIRA_USERNAME, self.JIRA_API_TOKEN]):
            return {
                "server": self.JIRA_SERVER_URL,
                "username": self.JIRA_USERNAME,
                "token": self.JIRA_API_TOKEN,
            }
        return None
    
    @property
    def confluence_config(self) -> Optional[Dict[str, str]]:
        """Get Confluence configuration if available"""
        if all([self.CONFLUENCE_SERVER_URL, self.CONFLUENCE_USERNAME, self.CONFLUENCE_API_TOKEN]):
            return {
                "server": self.CONFLUENCE_SERVER_URL,
                "username": self.CONFLUENCE_USERNAME,
                "token": self.CONFLUENCE_API_TOKEN,
            }
        return None
    
    @property
    def sharepoint_config(self) -> Optional[Dict[str, str]]:
        """Get SharePoint configuration if available"""
        if all([
            self.SHAREPOINT_TENANT_ID,
            self.SHAREPOINT_CLIENT_ID,
            self.SHAREPOINT_CLIENT_SECRET,
            self.SHAREPOINT_SITE_URL
        ]):
            return {
                "tenant_id": self.SHAREPOINT_TENANT_ID,
                "client_id": self.SHAREPOINT_CLIENT_ID,
                "client_secret": self.SHAREPOINT_CLIENT_SECRET,
                "site_url": self.SHAREPOINT_SITE_URL,
            }
        return None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Development settings
class DevelopmentSettings(Settings):
    """
    Development-specific settings
    """
    DEBUG: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"


# Production settings
class ProductionSettings(Settings):
    """
    Production-specific settings
    """
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Override with stricter security settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour


# Testing settings
class TestingSettings(Settings):
    """
    Testing-specific settings
    """
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/15"  # Use different Redis DB
    SECRET_KEY: str = "test-secret-key"


def get_settings_for_environment(environment: str = None) -> Settings:
    """
    Get settings based on environment
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestingSettings,
    }
    
    settings_class = settings_map.get(environment, Settings)
    return settings_class()