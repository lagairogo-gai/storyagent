#!/bin/bash

# RAG User Story Generator - Quick Setup Script
# This script helps you get the application running quickly

set -e

echo "🚀 RAG User Story Generator - Setup Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}[STEP]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed ✓"
}

# Create .env file if it doesn't exist
setup_env() {
    print_step "Setting up environment configuration"
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_status "Created .env file from .env.example"
            print_warning "Please edit .env file and add your API keys before continuing"
            
            echo -e "\n${YELLOW}Required API Keys:${NC}"
            echo "- OPENAI_API_KEY (for OpenAI GPT models)"
            echo "- Or CLAUDE_API_KEY (for Anthropic Claude)"
            echo "- Or GEMINI_API_KEY (for Google Gemini)"
            echo "- Or configure Ollama for local models"
            
            echo -e "\n${YELLOW}Optional Integrations:${NC}"
            echo "- JIRA_API_TOKEN (for Jira integration)"
            echo "- CONFLUENCE_API_TOKEN (for Confluence integration)"
            echo "- SharePoint credentials (for SharePoint integration)"
            
            read -p "Press Enter after you've configured your .env file..."
        else
            print_error ".env.example file not found. Please create a .env file manually."
            exit 1
        fi
    else
        print_status ".env file already exists ✓"
    fi
}

# Create necessary directories
create_directories() {
    print_step "Creating necessary directories"
    
    mkdir -p data/uploads
    mkdir -p data/chromadb
    mkdir -p logs
    mkdir -p backend/logs
    
    print_status "Directories created ✓"
}

# Pull required Docker images
pull_images() {
    print_step "Pulling Docker images (this may take a few minutes)"
    
    docker-compose pull
    
    print_status "Docker images pulled ✓"
}

# Start the application
start_application() {
    print_step "Starting the application"
    
    # Start all services
    docker-compose up -d
    
    print_status "Services are starting up..."
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Some services failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
    
    print_status "Application started successfully ✓"
}

# Initialize the database
init_database() {
    print_step "Initializing database"
    
    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    sleep 15
    
    # Run database migrations
    if docker-compose exec -T backend alembic upgrade head; then
        print_status "Database migrations completed ✓"
    else
        print_warning "Database migrations failed. You may need to run them manually."
    fi
}

# Download Ollama models (optional)
setup_ollama() {
    print_step "Setting up Ollama (optional local models)"
    
    read -p "Do you want to download Ollama models for local LLM inference? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Downloading Ollama models..."
        
        # Download popular models
        docker-compose exec ollama ollama pull llama2 || print_warning "Failed to download llama2"
        docker-compose exec ollama ollama pull codellama || print_warning "Failed to download codellama"
        
        print_status "Ollama models downloaded ✓"
    else
        print_status "Skipping Ollama model download"
    fi
}

# Show final information
show_info() {
    print_step "Setup Complete!"
    
    echo -e "\n${GREEN}🎉 RAG User Story Generator is now running!${NC}"
    echo -e "\n${BLUE}Access URLs:${NC}"
    echo "• Frontend Application: http://localhost:3000"
    echo "• Backend API: http://localhost:8001"
    echo "• API Documentation: http://localhost:8001/docs"
    echo "• Neo4j Browser: http://localhost:7474 (neo4j/neo4j_password)"
    echo "• Celery Flower: http://localhost:5555"
    
    echo -e "\n${BLUE}Default Login:${NC}"
    echo "• Username: admin"
    echo "• Password: admin123"
    
    echo -e "\n${BLUE}Useful Commands:${NC}"
    echo "• View logs: docker-compose logs -f"
    echo "• Stop services: docker-compose down"
    echo "• Restart services: docker-compose restart"
    echo "• Update images: docker-compose pull && docker-compose up -d"
    
    echo -e "\n${YELLOW}Next Steps:${NC}"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Log in with the default credentials"
    echo "3. Create a new project"
    echo "4. Upload some requirement documents"
    echo "5. Generate your first user stories!"
    
    echo -e "\n${YELLOW}Need Help?${NC}"
    echo "• Check the README.md for detailed documentation"
    echo "• View logs if something isn't working: docker-compose logs [service-name]"
    echo "• Join our community: https://github.com/your-org/rag-user-stories/discussions"
}

# Main execution
main() {
    echo "Starting setup process..."
    
    check_docker
    setup_env
    create_directories
    pull_images
    start_application
    init_database
    setup_ollama
    show_info
    
    echo -e "\n${GREEN}Setup completed successfully! 🚀${NC}"
}

# Handle script interruption
trap 'echo -e "\n${RED}Setup interrupted. Run docker-compose down to clean up.${NC}"; exit 1' INT

# Run main function
main "$@"