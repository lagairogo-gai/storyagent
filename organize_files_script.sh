#!/bin/bash

# File Organization Script for RAG User Story Generator
# This script moves files to their correct directories

set -e

echo "🗂️  Organizing project files..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[ORGANIZING]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[MOVED]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Create directory structure
print_step "Creating directory structure..."

# Backend directories
mkdir -p backend/app/core
mkdir -p backend/app/models
mkdir -p backend/app/services
mkdir -p backend/app/api/v1
mkdir -p backend/app/schemas
mkdir -p backend/app/utils
mkdir -p backend/app/agents

# Frontend directories
mkdir -p frontend/src/components/common
mkdir -p frontend/src/components/visualization
mkdir -p frontend/src/pages
mkdir -p frontend/src/styles
mkdir -p frontend/src/types
mkdir -p frontend/src/hooks
mkdir -p frontend/src/services
mkdir -p frontend/public

print_success "Directory structure created"

# Move backend files
print_step "Moving backend files..."

# Core files
if [ -f "config.py" ]; then
    mv config.py backend/app/core/
    print_success "config.py → backend/app/core/"
fi

if [ -f "database.py" ]; then
    mv database.py backend/app/core/
    print_success "database.py → backend/app/core/"
fi

if [ -f "security.py" ]; then
    mv security.py backend/app/core/
    print_success "security.py → backend/app/core/"
fi

if [ -f "main.py" ]; then
    mv main.py backend/app/
    print_success "main.py → backend/app/"
fi

# Model files
if [ -f "user_model.py" ]; then
    mv user_model.py backend/app/models/user.py
    print_success "user_model.py → backend/app/models/user.py"
fi

if [ -f "document_model.py" ]; then
    mv document_model.py backend/app/models/document.py
    print_success "document_model.py → backend/app/models/document.py"
fi

if [ -f "project_model.py" ]; then
    mv project_model.py backend/app/models/project.py
    print_success "project_model.py → backend/app/models/project.py"
fi

# Service files
if [ -f "llm_service.py" ]; then
    mv llm_service.py backend/app/services/
    print_success "llm_service.py → backend/app/services/"
fi

# Requirements
if [ -f "requirements.txt" ]; then
    mv requirements.txt backend/
    print_success "requirements.txt → backend/"
fi

# Create __init__.py files for Python packages
print_step "Creating Python package files..."

touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/utils/__init__.py
touch backend/app/agents/__init__.py

print_success "Python package files created"

# Move frontend files
print_step "Moving frontend files..."

# React components
if [ -f "app.tsx" ]; then
    mv app.tsx frontend/src/App.tsx
    print_success "app.tsx → frontend/src/App.tsx"
fi

if [ -f "dashboard.tsx" ]; then
    mv dashboard.tsx frontend/src/pages/Dashboard.tsx
    print_success "dashboard.tsx → frontend/src/pages/Dashboard.tsx"
fi

if [ -f "visualization.tsx" ]; then
    mv visualization.tsx frontend/src/components/visualization/WorkflowVisualization.tsx
    print_success "visualization.tsx → frontend/src/components/visualization/WorkflowVisualization.tsx"
fi

# Styles
if [ -f "n8n-theme.css" ]; then
    mv n8n-theme.css frontend/src/styles/
    print_success "n8n-theme.css → frontend/src/styles/"
fi

# Clean up any remaining scattered files
print_step "Cleaning up remaining files..."

if [ -f "project_structure.py" ]; then
    mv project_structure.py backend/app/utils/
    print_success "project_structure.py → backend/app/utils/"
fi

# Check current backend structure
print_step "Checking backend structure..."
echo "Backend structure:"
find backend -type f -name "*.py" | head -20

print_step "Checking frontend structure..."
echo "Frontend structure:"
find frontend -type f | head -20

# Verify critical files exist
print_step "Verifying critical files..."

critical_files=(
    "backend/app/main.py"
    "backend/requirements.txt"
    "frontend/src/App.tsx"
    "docker-compose.yml"
    ".env"
)

missing_files=()

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file exists"
    else
        missing_files+=("$file")
        echo -e "${YELLOW}[MISSING]${NC} $file"
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All files organized successfully!${NC}"
    echo -e "\n${BLUE}Next steps:${NC}"
    echo "1. Run: docker-compose up --build -d"
    echo "2. Check logs: docker-compose logs -f"
    echo "3. Access frontend: http://localhost:3000"
    echo "4. Access backend: http://localhost:8001"
else
    echo -e "\n${YELLOW}⚠️  Some files are missing. You may need to create them manually.${NC}"
    printf '%s\n' "${missing_files[@]}"
fi

echo -e "\n${BLUE}Project structure is now organized! 📁${NC}"