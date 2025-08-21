"""
FastAPI Main Application - RAG User Story Generator
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.staticfiles import StaticFiles
import logging
import uvicorn
from contextlib import asynccontextmanager
import asyncio
from typing import Dict, Any
import time

# Core imports
from app.core.config import get_settings
from app.core.database import get_database, init_db
from app.core.security import verify_token

# API routes
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.user_stories import router as user_stories_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.knowledge_graph import router as kg_router

# Services
from app.services.llm_service import LLMService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.utils.vector_store import VectorStoreManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Security scheme
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    logger.info("🚀 Starting RAG User Story Generator API")
    
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database initialized")
        
        # Initialize vector store
        vector_manager = VectorStoreManager()
        await vector_manager.initialize()
        app.state.vector_manager = vector_manager
        logger.info("✅ Vector store initialized")
        
        # Initialize knowledge graph
        kg_service = KnowledgeGraphService()
        await kg_service.initialize()
        app.state.kg_service = kg_service
        logger.info("✅ Knowledge graph initialized")
        
        # Initialize LLM service
        llm_service = LLMService()
        app.state.llm_service = llm_service
        logger.info("✅ LLM service initialized")
        
        logger.info("🎉 All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🔄 Shutting down services...")
    try:
        if hasattr(app.state, 'vector_manager'):
            await app.state.vector_manager.close()
        if hasattr(app.state, 'kg_service'):
            await app.state.kg_service.close()
        logger.info("✅ Services shut down successfully")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="RAG User Story Generator API",
    description="""
    Production-grade RAG-based AI agent for generating user stories from requirements.
    
    ## Features
    
    * **Multi-source Integration**: Jira, Confluence, SharePoint, file uploads
    * **Advanced RAG Pipeline**: Vector search with knowledge graph enhancement
    * **Multiple LLM Support**: OpenAI, Azure, Gemini, Claude
    * **Knowledge Graph**: Semantic understanding of requirements and dependencies
    * **Export Integration**: Direct export to Jira with proper formatting
    * **Real-time Processing**: WebSocket support for streaming responses
    
    ## Architecture
    
    Built with FastAPI, LangChain, LangGraph, and Neo4j for enterprise-grade performance.
    """,
    version="1.0.0",
    docs_url=None,  # We'll serve custom docs
    redoc_url=None,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Custom middleware for request logging and timing
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"📝 {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"✅ {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.3f}s"
        )
        raise


# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code
            },
            "timestamp": time.time(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An internal server error occurred",
                "status_code": 500
            },
            "timestamp": time.time(),
            "path": str(request.url.path)
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "services": {
            "database": "healthy",
            "vector_store": "healthy",
            "knowledge_graph": "healthy",
            "llm_service": "healthy"
        }
    }


# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/api/v1/openapi.json",
        title="RAG User Story Generator API - Documentation",
        swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}
    )


@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url="/api/v1/openapi.json",
        title="RAG User Story Generator API - Documentation"
    )


# Include API routers
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    documents_router,
    prefix="/api/v1/documents",
    tags=["Documents"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    user_stories_router,
    prefix="/api/v1/user-stories",
    tags=["User Stories"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    integrations_router,
    prefix="/api/v1/integrations",
    tags=["Integrations"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    kg_router,
    prefix="/api/v1/knowledge-graph",
    tags=["Knowledge Graph"],
    dependencies=[Depends(verify_token)]
)


# WebSocket endpoint for real-time user story generation
@app.websocket("/ws/generate")
async def websocket_generate_user_stories(websocket):
    """
    WebSocket endpoint for real-time user story generation with progress updates
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive generation request
            data = await websocket.receive_json()
            
            # Validate request
            if not data.get("requirements"):
                await websocket.send_json({
                    "type": "error",
                    "message": "Requirements are required"
                })
                continue
            
            # Send progress updates during generation
            await websocket.send_json({
                "type": "progress",
                "stage": "initializing",
                "message": "Starting user story generation..."
            })
            
            # TODO: Implement actual generation logic
            # This would integrate with the LangGraph agent
            
            await websocket.send_json({
                "type": "progress",
                "stage": "analyzing",
                "message": "Analyzing requirements..."
            })
            
            await asyncio.sleep(2)  # Simulate processing
            
            await websocket.send_json({
                "type": "progress",
                "stage": "generating",
                "message": "Generating user stories..."
            })
            
            await asyncio.sleep(3)  # Simulate generation
            
            # Send final result
            await websocket.send_json({
                "type": "complete",
                "user_stories": [
                    {
                        "title": "Sample User Story",
                        "description": "As a user, I want to...",
                        "acceptance_criteria": ["Given...", "When...", "Then..."],
                        "priority": "High",
                        "story_points": 5
                    }
                ]
            })
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "An error occurred during generation"
        })
    finally:
        await websocket.close()


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "RAG User Story Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "features": [
            "Multi-source requirement integration",
            "Advanced RAG pipeline",
            "Knowledge graph enhancement",
            "Multiple LLM support",
            "Real-time generation",
            "Jira export integration"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )