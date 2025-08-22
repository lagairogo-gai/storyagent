#!/bin/bash

# RAG User Story Generator - Automated Setup Script
set -e

echo "🚀 RAG User Story Generator - Automated Setup"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check prerequisites
check_docker() {
    print_step "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_status "Docker and Docker Compose are available"
}

# Create project structure
create_structure() {
    print_step "Creating project structure..."
    
    # Create directories
    mkdir -p rag-user-stories/{backend/{app/{core,models,services,api/v1,schemas,utils,agents},scripts},frontend/{src/{components/{common,visualization},pages,styles,hooks,services,types},public}}
    
    # Create essential files
    touch rag-user-stories/backend/app/__init__.py
    touch rag-user-stories/backend/app/core/__init__.py
    touch rag-user-stories/backend/app/models/__init__.py
    touch rag-user-stories/backend/app/services/__init__.py
    touch rag-user-stories/backend/app/api/__init__.py
    touch rag-user-stories/backend/app/api/v1/__init__.py
    
    print_status "Project structure created"
}

# Create Docker Compose file
create_docker_compose() {
    print_step "Creating docker-compose.yml..."
    
    cat > rag-user-stories/docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: rag-postgres
    environment:
      POSTGRES_DB: rag_user_stories
      POSTGRES_USER: rag_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-rag_password}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - rag-network
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: rag-redis
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis_password}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - rag-network
    restart: unless-stopped

  # Neo4j Knowledge Graph
  neo4j:
    image: neo4j:5.13-community
    container_name: rag-neo4j
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD:-neo4j_password}
      NEO4J_PLUGINS: '["apoc"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
    networks:
      - rag-network
    restart: unless-stopped

  # ChromaDB Vector Database
  chromadb:
    image: ghcr.io/chroma-core/chroma:latest
    container_name: rag-chromadb
    ports:
      - "8000:8000"
    volumes:
      - chromadb_data:/chroma/chroma
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
    networks:
      - rag-network
    restart: unless-stopped

  # Backend FastAPI
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: rag-backend
    environment:
      DATABASE_URL: postgresql://rag_user:${POSTGRES_PASSWORD:-rag_password}@postgres:5432/rag_user_stories
      REDIS_URL: redis://:${REDIS_PASSWORD:-redis_password}@redis:6379/0
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: ${NEO4J_PASSWORD:-neo4j_password}
      CHROMA_DB_HOST: chromadb
      CHROMA_DB_PORT: 8000
      SECRET_KEY: ${SECRET_KEY:-your-secret-key-change-in-production}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      CLAUDE_API_KEY: ${CLAUDE_API_KEY}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      DEBUG: "true"
      ENVIRONMENT: development
    ports:
      - "8001:8000"
    volumes:
      - ./backend:/app
      - backend_uploads:/app/uploads
    depends_on:
      - postgres
      - redis
      - neo4j
      - chromadb
    networks:
      - rag-network
    restart: unless-stopped

  # Frontend React
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: rag-frontend
    environment:
      - REACT_APP_API_URL=http://localhost:8001
      - CHOKIDAR_USEPOLLING=true
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - rag-network
    restart: unless-stopped

networks:
  rag-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  neo4j_data:
  chromadb_data:
  backend_uploads:
EOF

    print_status "Docker Compose file created"
}

# Create environment file
create_env() {
    print_step "Creating .env file..."
    
    cat > rag-user-stories/.env << 'EOF'
# Database Passwords
POSTGRES_PASSWORD=rag_password
REDIS_PASSWORD=redis_password
NEO4J_PASSWORD=neo4j_password

# JWT Secret (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# LLM Provider API Keys (Add at least one)
# OPENAI_API_KEY=sk-your-openai-key-here
# CLAUDE_API_KEY=sk-ant-your-claude-key-here  
# GEMINI_API_KEY=your-gemini-key-here

# Optional: External Integrations
# JIRA_SERVER_URL=https://yourcompany.atlassian.net
# JIRA_USERNAME=your-email@company.com
# JIRA_API_TOKEN=your-jira-token

# CONFLUENCE_SERVER_URL=https://yourcompany.atlassian.net/wiki
# CONFLUENCE_USERNAME=your-email@company.com
# CONFLUENCE_API_TOKEN=your-confluence-token
EOF

    print_status ".env file created"
    print_warning "Please edit .env file and add your API keys!"
}

# Create essential backend files
create_backend_files() {
    print_step "Creating essential backend files..."
    
    # Create minimal requirements.txt
    cat > rag-user-stories/backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
redis==5.0.1
langchain==0.0.347
openai==1.6.1
anthropic==0.8.1
google-generativeai==0.3.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.2
pydantic-settings==2.1.0
python-dotenv==1.0.0
chromadb==0.4.18
neo4j==5.15.0
aiofiles==23.2.1
gunicorn==21.2.0
EOF

    # Create simple Dockerfile
    cat > rag-user-stories/backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

    # Create minimal main.py
    cat > rag-user-stories/backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RAG User Story Generator API",
    description="AI-powered user story generation from requirements",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "RAG User Story Generator API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}
EOF

    print_status "Backend files created"
}

# Create essential frontend files
create_frontend_files() {
    print_step "Creating essential frontend files..."
    
    # Create package.json
    cat > rag-user-stories/frontend/package.json << 'EOF'
{
  "name": "rag-user-stories-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.5"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  },
  "proxy": "http://backend:8000"
}
EOF

    # Create Dockerfile
    cat > rag-user-stories/frontend/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

ENV CHOKIDAR_USEPOLLING=true

CMD ["npm", "start"]
EOF

    # Create basic React app
    cat > rag-user-stories/frontend/src/App.tsx << 'EOF'
import React from 'react';

function App() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>🚀 RAG User Story Generator</h1>
      <p>Welcome to your AI-powered user story generation platform!</p>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>🎯 Getting Started</h2>
        <ul>
          <li>Upload requirement documents</li>
          <li>Connect to Jira, Confluence, or SharePoint</li>
          <li>Generate AI-powered user stories</li>
          <li>Export back to your project management tools</li>
        </ul>
      </div>
      
      <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f0f8ff', borderRadius: '8px' }}>
        <p><strong>API Status:</strong> Check <a href="http://localhost:8001/health">http://localhost:8001/health</a></p>
        <p><strong>Documentation:</strong> <a href="http://localhost:8001/docs">http://localhost:8001/docs</a></p>
      </div>
    </div>
  );
}

export default App;
EOF

    cat > rag-user-stories/frontend/src/index.tsx << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(<App />);
EOF

    cat > rag-user-stories/frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>RAG User Story Generator</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
EOF

    # Create tsconfig.json
    cat > rag-user-stories/frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
EOF

    print_status "Frontend files created"
}

# Build and start services
start_services() {
    print_step "Building and starting services..."
    
    cd rag-user-stories
    
    # Build and start
    docker-compose up --build -d
    
    print_status "Services are starting..."
    
    # Wait for services
    echo "Waiting for services to be ready (30 seconds)..."
    sleep 30
    
    # Check health
    if curl -f http://localhost:8001/health &> /dev/null; then
        print_status "Backend is healthy"
    else
        print_warning "Backend may still be starting up"
    fi
}

# Show completion info
show_completion() {
    echo ""
    echo -e "${GREEN}🎉 Setup Complete!${NC}"
    echo ""
    echo -e "${BLUE}Access URLs:${NC}"
    echo "• Frontend: http://localhost:3000"
    echo "• Backend API: http://localhost:8001"
    echo "• API Docs: http://localhost:8001/docs"
    echo "• Neo4j Browser: http://localhost:7474 (neo4j/neo4j_password)"
    echo ""
    echo -e "${YELLOW}⚠️  Important Next Steps:${NC}"
    echo "1. Edit .env file and add your API keys"
    echo "2. Restart services: docker-compose restart"
    echo "3. Check logs: docker-compose logs -f"
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo "• Stop: docker-compose down"
    echo "• Restart: docker-compose restart"
    echo "• Logs: docker-compose logs [service]"
}

# Main execution
main() {
    check_docker
    create_structure
    create_docker_compose
    create_env
    create_backend_files
    create_frontend_files
    start_services
    show_completion
}

# Handle interruption
trap 'echo -e "\n${RED}Setup interrupted.${NC}"; exit 1' INT

# Run main function
main "$@"