"""
Database configuration and session management
"""

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
import sqlite3
import asyncio
from typing import AsyncGenerator, Generator
import logging
from contextlib import asynccontextmanager

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base
Base = declarative_base()

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base.metadata.naming_convention = convention


# SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key support for SQLite"""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class DatabaseManager:
    """
    Database manager for handling connections and sessions
    """
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        
    async def create_tables(self):
        """Create all database tables"""
        try:
            # Import all models to ensure they're registered
            from app.models import user, document, user_story, knowledge_graph, project
            
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Database tables created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            raise
    
    async def drop_tables(self):
        """Drop all database tables"""
        try:
            logger.info("Dropping database tables...")
            Base.metadata.drop_all(bind=self.engine)
            logger.info("✅ Database tables dropped successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to drop database tables: {e}")
            raise
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session"""
        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database session error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[Session, None]:
        """Get async database session"""
        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await asyncio.get_event_loop().run_in_executor(None, db.rollback)
            raise
        finally:
            await asyncio.get_event_loop().run_in_executor(None, db.close)
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_async_session() as db:
                # Simple query to test connection
                await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: db.execute("SELECT 1").scalar()
                )
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def close(self):
        """Close database connections"""
        try:
            self.engine.dispose()
            logger.info("✅ Database connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing database connections: {e}")


# Global database manager instance
db_manager = DatabaseManager()


# Dependency functions
def get_database() -> Generator[Session, None, None]:
    """
    FastAPI dependency for getting database session
    """
    yield from db_manager.get_session()


async def get_async_database() -> AsyncGenerator[Session, None]:
    """
    Async dependency for getting database session
    """
    async with db_manager.get_async_session() as session:
        yield session


# Database initialization
async def init_db():
    """
    Initialize database with tables and default data
    """
    try:
        # Create tables
        await db_manager.create_tables()
        
        # Create default data
        await create_default_data()
        
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def create_default_data():
    """
    Create default data for the application
    """
    try:
        from app.models.user import User
        from app.models.project import Project
        from app.core.security import get_password_hash
        
        async with db_manager.get_async_session() as db:
            # Check if admin user exists
            admin_user = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: db.query(User).filter(User.email == "admin@example.com").first()
            )
            
            if not admin_user:
                # Create admin user
                admin_user = User(
                    email="admin@example.com",
                    username="admin",
                    full_name="System Administrator",
                    hashed_password=get_password_hash("admin123"),
                    is_active=True,
                    is_superuser=True
                )
                
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: db.add(admin_user)
                )
                
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: db.commit()
                )
                
                logger.info("✅ Default admin user created")
            
            # Check if default project exists
            default_project = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: db.query(Project).filter(Project.key == "DEFAULT").first()
            )
            
            if not default_project:
                # Create default project
                default_project = Project(
                    key="DEFAULT",
                    name="Default Project",
                    description="Default project for user stories",
                    owner_id=admin_user.id if admin_user else 1,
                    is_active=True
                )
                
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: db.add(default_project)
                )
                
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: db.commit()
                )
                
                logger.info("✅ Default project created")
        
        logger.info("✅ Default data created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create default data: {e}")
        # Don't raise here as it's not critical for app startup


# Database utilities
class DatabaseTransaction:
    """
    Context manager for database transactions
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def __enter__(self):
        return self.db
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        else:
            self.db.commit()


async def execute_with_retry(operation, max_retries: int = 3, delay: float = 1.0):
    """
    Execute database operation with retry logic
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            last_exception = e
            logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    logger.error(f"Database operation failed after {max_retries} attempts")
    raise last_exception


# Migration utilities
async def run_migrations():
    """
    Run database migrations using Alembic
    """
    try:
        from alembic import command
        from alembic.config import Config
        
        logger.info("Running database migrations...")
        
        # Load Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Run migrations
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: command.upgrade(alembic_cfg, "head")
        )
        
        logger.info("✅ Database migrations completed")
        
    except ImportError:
        logger.warning("Alembic not available, skipping migrations")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


# Database monitoring
class DatabaseMetrics:
    """
    Database performance metrics collector
    """
    
    def __init__(self):
        self.query_count = 0
        self.slow_queries = []
        self.connection_pool_stats = {}
    
    def record_query(self, query: str, execution_time: float):
        """Record query execution metrics"""
        self.query_count += 1
        
        if execution_time > 1.0:  # Log slow queries (>1 second)
            self.slow_queries.append({
                "query": query[:200],  # Truncate long queries
                "execution_time": execution_time,
                "timestamp": asyncio.get_event_loop().time()
            })
    
    def get_stats(self) -> dict:
        """Get database statistics"""
        return {
            "total_queries": self.query_count,
            "slow_queries_count": len(self.slow_queries),
            "recent_slow_queries": self.slow_queries[-5:],  # Last 5 slow queries
            "connection_pool": {
                "size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
                "invalid": engine.pool.invalid()
            }
        }


# Global metrics instance
db_metrics = DatabaseMetrics()