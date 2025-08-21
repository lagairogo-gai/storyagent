# RAG-Based AI Agent for User Story Generation

A production-grade, enterprise-ready system that generates high-quality user stories from requirement documents using Retrieval-Augmented Generation (RAG) with knowledge graph enhancement.

## 🌟 Features

### Core Capabilities
- **Multi-Source Integration**: Jira, Confluence, SharePoint, and file uploads
- **Advanced RAG Pipeline**: Vector search enhanced with knowledge graph semantics
- **Multiple LLM Support**: OpenAI, Azure OpenAI, Google Gemini, Anthropic Claude, and local models via Ollama
- **Knowledge Graph**: Semantic understanding of requirements and dependencies using Neo4j
- **Real-time Processing**: WebSocket-based streaming with live progress updates
- **Export Integration**: Direct export to Jira with proper formatting

### Architecture Highlights
- **Frontend**: React 18 + TypeScript with n8n-inspired animated UI
- **Backend**: FastAPI with async processing and LangChain/LangGraph
- **Databases**: PostgreSQL, Redis, Neo4j, ChromaDB
- **Processing**: Celery for background tasks with Flower monitoring
- **Deployment**: Docker Compose with production-ready configuration

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Knowledge     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│     Graph       │
│                 │    │                 │    │    (Neo4j)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │  Vector Store   │              │
         └──────────────►│   (ChromaDB)    │◄─────────────┘
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │   LLM Services  │
                        │ OpenAI/Claude/  │
                        │ Gemini/Ollama   │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/rag-user-stories.git
cd rag-user-stories
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys and configuration
nano .env
```

### 3. Start Development Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Initialize the System
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create default admin user
docker-compose exec backend python scripts/create_admin.py

# Download Ollama models (optional)
docker-compose exec ollama ollama pull llama2
docker-compose exec ollama ollama pull codellama
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Neo4j Browser**: http://localhost:7474
- **Celery Flower**: http://localhost:5555

## 🔧 Configuration

### Environment Variables

#### Core Application
```bash
# Database
DATABASE_URL=postgresql://rag_user:rag_password@postgres:5432/rag_user_stories
REDIS_URL=redis://:redis_password@redis:6379/0

# Security
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Knowledge Graph
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password
```

#### LLM Configuration
```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# Anthropic Claude
CLAUDE_API_KEY=sk-ant-your-claude-api-key
CLAUDE_MODEL=claude-3-sonnet-20240229

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro

# Ollama (Local)
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
```

#### External Integrations
```bash
# Jira
JIRA_SERVER_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token

# Confluence
CONFLUENCE_SERVER_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your-confluence-api-token

# SharePoint
SHAREPOINT_TENANT_ID=your-tenant-id
SHAREPOINT_CLIENT_ID=your-client-id
SHAREPOINT_CLIENT_SECRET=your-client-secret
SHAREPOINT_SITE_URL=https://yourcompany.sharepoint.com/sites/yoursite
```

## 📖 Usage Guide

### 1. Creating a Project
```bash
# Via API
curl -X POST "http://localhost:8001/api/v1/projects" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "key": "MP",
    "description": "Project description",
    "project_type": "software_development"
  }'
```

### 2. Uploading Documents
```bash
# Upload a requirements document
curl -X POST "http://localhost:8001/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@requirements.pdf" \
  -F "project_id=1" \
  -F "document_type=requirements"
```

### 3. Generating User Stories
```python
import asyncio
import websockets
import json

async def generate_stories():
    uri = "ws://localhost:8001/ws/generate"
    
    async with websockets.connect(uri) as websocket:
        # Send generation request
        request = {
            "requirements": "User should be able to login with email and password",
            "project_id": 1,
            "preferences": {
                "include_acceptance_criteria": True,
                "include_story_points": True
            }
        }
        
        await websocket.send(json.dumps(request))
        
        # Receive real-time updates
        async for message in websocket:
            data = json.loads(message)
            print(f"Status: {data['type']} - {data.get('message', '')}")
            
            if data['type'] == 'complete':
                print("Generated User Stories:")
                for story in data['user_stories']:
                    print(f"- {story['title']}: {story['description']}")
                break

# Run the example
asyncio.run(generate_stories())
```

### 4. Integrating with Jira
```python
from app.services.jira_service import JiraService

# Export user stories to Jira
jira_service = JiraService()
project_key = "MYPROJ"

for story in generated_stories:
    issue = await jira_service.create_user_story(
        project_key=project_key,
        summary=story['title'],
        description=story['description'],
        acceptance_criteria=story['acceptance_criteria'],
        story_points=story['story_points']
    )
    print(f"Created Jira issue: {issue.key}")
```

## 🏭 Production Deployment

### Using Docker Compose (Recommended)
```bash
# Production deployment
docker-compose --profile production up -d

# With monitoring
docker-compose --profile production --profile monitoring up -d
```

### Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n rag-system
```

### Environment-Specific Configurations

#### Production
```bash
# Use production environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Secure database connections
DATABASE_URL=postgresql://user:pass@prod-db:5432/rag_db?sslmode=require

# Production Redis with clustering
REDIS_URL=redis://prod-redis-cluster:6379/0
```

#### Staging
```bash
ENVIRONMENT=staging
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🔍 Monitoring & Observability

### Health Checks
```bash
# Application health
curl http://localhost:8001/health

# Database connectivity
curl http://localhost:8001/health/db

# LLM services status
curl http://localhost:8001/health/llm
```

### Metrics & Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Application Metrics**: Custom dashboards for user story generation metrics

### Logging
```bash
# View application logs
docker-compose logs -f backend

# View specific service logs
docker-compose logs -f celery-worker

# Export logs
docker-compose logs backend > backend.log
```

## 🧪 Testing

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### API Testing
```bash
# Install testing tools
pip install httpx pytest-asyncio

# Run API tests
pytest tests/test_api.py -v
```

### Load Testing
```bash
# Using locust
pip install locust
locust -f tests/load_test.py --host=http://localhost:8001
```

## 🛠️ Development

### Local Development Setup
```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend development
cd frontend
npm install
npm start
```

### Code Quality
```bash
# Backend formatting
black app/
isort app/
flake8 app/

# Frontend formatting
npm run format
npm run lint:fix
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📚 API Documentation

### Authentication
```bash
# Login
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "admin123"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Core Endpoints
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `POST /api/v1/documents/upload` - Upload document
- `POST /api/v1/user-stories/generate` - Generate user stories
- `GET /api/v1/knowledge-graph/entities` - Get knowledge graph entities

### WebSocket Events
- `generation_progress` - Real-time generation updates
- `document_processing` - Document processing status
- `system_notification` - System-wide notifications

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Standards
- **Backend**: Follow PEP 8, use type hints, write docstrings
- **Frontend**: Use TypeScript, follow React best practices
- **Documentation**: Update README and API docs for changes
- **Testing**: Maintain >80% test coverage

### Pull Request Guidelines
- Include tests for new features
- Update documentation
- Follow conventional commit messages
- Ensure all CI checks pass

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up postgres -d
```

#### LLM API Errors
```bash
# Check API key configuration
docker-compose exec backend python -c "from app.core.config import get_settings; print(get_settings().OPENAI_API_KEY)"

# Test LLM connectivity
curl -X GET "http://localhost:8001/health/llm"
```

#### Frontend Build Issues
```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check for dependency conflicts
npm audit fix
```

### Performance Optimization

#### Database Performance
```sql
-- Optimize PostgreSQL for better performance
ANALYZE;
REINDEX DATABASE rag_user_stories;

-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;
```

#### Vector Store Optimization
```python
# Optimize ChromaDB collections
collection.delete(where={"document_id": {"$in": old_document_ids}})
collection.persist()
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for the powerful LLM framework
- **FastAPI** for the excellent web framework
- **React** and **Tailwind CSS** for the modern frontend
- **n