#!/bin/bash

# Check current project structure and identify what needs to be moved

echo "📋 Current Project Structure Analysis"
echo "===================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${BLUE}🗂️  Root Directory Contents:${NC}"
ls -la

echo -e "\n${BLUE}📁 Backend Directory:${NC}"
if [ -d "backend" ]; then
    find backend -type f | sort
else
    echo "❌ Backend directory doesn't exist"
fi

echo -e "\n${BLUE}📁 Frontend Directory:${NC}"
if [ -d "frontend" ]; then
    find frontend -type f | sort
else
    echo "❌ Frontend directory doesn't exist"
fi

echo -e "\n${YELLOW}📝 Files that need to be moved:${NC}"

# Files that should be in backend/app/core/
echo -e "\n${BLUE}Should be in backend/app/core/:${NC}"
for file in config.py database.py security.py; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file (needs to move)"
    else
        echo -e "${RED}✗${NC} $file (missing)"
    fi
done

# Files that should be in backend/app/
echo -e "\n${BLUE}Should be in backend/app/:${NC}"
for file in main.py; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file (needs to move)"
    else
        echo -e "${RED}✗${NC} $file (missing)"
    fi
done

# Files that should be in backend/app/models/
echo -e "\n${BLUE}Should be in backend/app/models/:${NC}"
for file in user_model.py document_model.py project_model.py; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file (needs to move)"
    else
        echo -e "${RED}✗${NC} $file (missing)"
    fi
done

# Files that should be in backend/app/services/
echo -e "\n${BLUE}Should be in backend/app/services/:${NC}"
for file in llm_service.py; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file (needs to move)"
    else
        echo -e "${RED}✗${NC} $file (missing)"
    fi
done

# Files that should be in backend/
echo -e "\n${BLUE}Should be in backend/:${NC}"
for file in requirements.txt; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file (needs to move)"
    else
        echo -e "${RED}✗${NC} $file (missing)"
    fi
done

# Files that should be in frontend/src/
echo -e "\n${BLUE}Should be in frontend/src/:${NC}"
for file in app.tsx; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file (needs to move to App.tsx)"
    else
        echo -e "${RED}✗${NC} $file (missing)"
    fi
done

# Files that should be in frontend/src/pages/
echo -e "\n${BLUE}Should be in frontend/src/pages/:${NC}"
for file in dashboard.tsx; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file (needs to move to Dashboard.tsx)"
    else
        echo -e "${RED}✗${NC} $file (missing)"
    fi
done

# Files that should be in frontend/src/components/visualization/
echo -e "\n${BLUE}Should be in frontend/src/components/visualization/:${NC}"
for file in visualization.tsx; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file (needs to move to WorkflowVisualization.tsx)"
    else
        echo -e "${RED}✗${NC} $file (missing)"
    fi
done

# Files that should be in frontend/src/styles/
echo -e "\n${BLUE}Should be in frontend/src/styles/:${NC}"
for file in n8n-theme.css; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file (needs to move)"
    else
        echo -e "${RED}✗${NC} $file (missing)"
    fi
done

echo -e "\n${YELLOW}💡 Recommendations:${NC}"
echo "1. Run the organize_files.sh script to move files automatically"
echo "2. Or manually move files to their correct locations"
echo "3. Then run: docker-compose up --build -d"

echo -e "\n${BLUE}Ready to organize? Run:${NC}"
echo "./organize_files.sh"