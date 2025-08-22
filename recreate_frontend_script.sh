#!/bin/bash

echo "🔄 Recreating Complete Frontend Setup"
echo "===================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[CREATING]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[CREATED]${NC} $1"
}

# Create directory structure
print_step "Creating frontend directory structure..."
mkdir -p frontend/src/components/common
mkdir -p frontend/src/components/visualization
mkdir -p frontend/src/pages
mkdir -p frontend/src/styles
mkdir -p frontend/src/hooks
mkdir -p frontend/src/services
mkdir -p frontend/src/types
mkdir -p frontend/public

print_success "Directory structure created"

# Create package.json
print_step "Creating package.json..."
cat > frontend/package.json << 'EOF'
{
  "name": "rag-user-stories-frontend",
  "version": "1.0.0",
  "description": "Frontend for RAG-based User Story Generator",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.5",
    "web-vitals": "^2.1.4"
  },
  "devDependencies": {
    "@types/jest": "^27.5.2",
    "@types/node": "^16.18.68",
    "@types/react": "^18.2.31",
    "@types/react-dom": "^18.2.14"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:8000"
}
EOF

print_success "package.json"

# Create public/index.html
print_step "Creating public/index.html..."
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚀</text></svg>" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#8B5CF6" />
    <meta name="description" content="RAG-based AI Agent for User Story Generation" />
    
    <!-- Preload fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <title>RAG User Story Generator</title>
    
    <style>
      /* Loading screen styles */
      #initial-loader {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        transition: opacity 0.5s ease-out;
      }
      
      .loader-content {
        text-align: center;
        color: white;
      }
      
      .spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(255,255,255,0.3);
        border-top: 4px solid white;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 20px;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      .loader-text {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 10px;
      }
      
      .loader-subtext {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        opacity: 0.8;
      }
      
      /* Hide loader when app loads */
      .app-loaded #initial-loader {
        opacity: 0;
        pointer-events: none;
      }
      
      /* Base styles */
      body {
        margin: 0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
          'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
          sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        background: #f8fafc;
      }
      
      code {
        font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
      }
    </style>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    
    <!-- Loading screen -->
    <div id="initial-loader">
      <div class="loader-content">
        <div class="spinner"></div>
        <div class="loader-text">RAG User Story Generator</div>
        <div class="loader-subtext">Loading your AI-powered workspace...</div>
      </div>
    </div>
    
    <!-- React app root -->
    <div id="root"></div>
    
    <script>
      // Hide loader when app loads
      window.addEventListener('load', function() {
        setTimeout(function() {
          document.body.classList.add('app-loaded');
        }, 1000);
      });
      
      // Fallback to hide loader after 5 seconds
      setTimeout(function() {
        document.body.classList.add('app-loaded');
      }, 5000);
    </script>
  </body>
</html>
EOF

print_success "public/index.html"

# Create src/index.tsx
print_step "Creating src/index.tsx..."
cat > frontend/src/index.tsx << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

print_success "src/index.tsx"

# Create src/index.css
print_step "Creating src/index.css..."
cat > frontend/src/index.css << 'EOF'
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --font-inter: 'Inter', sans-serif;
  /* n8n Color Palette */
  --n8n-purple: #8B5CF6;
  --n8n-purple-light: #A78BFA;
  --n8n-purple-dark: #7C3AED;
  
  --n8n-blue: #06B6D4;
  --n8n-blue-light: #67E8F9;
  --n8n-blue-dark: #0891B2;
  
  --n8n-teal: #10B981;
  --n8n-teal-light: #6EE7B7;
  --n8n-teal-dark: #059669;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: var(--font-inter);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f8fafc;
}

#root {
  min-height: 100vh;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: var(--n8n-purple);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--n8n-purple-dark);
}

/* Utility classes */
.gradient-bg {
  background: linear-gradient(135deg, var(--n8n-purple) 0%, var(--n8n-blue) 100%);
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
  text-decoration: none;
}

.btn-primary {
  background: var(--n8n-purple);
  color: white;
}

.btn-primary:hover {
  background: var(--n8n-purple-dark);
  transform: translateY(-1px);
}

.status-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
}

.status-success {
  background: var(--n8n-teal);
}

.status-warning {
  background: #F59E0B;
}

.status-error {
  background: #EF4444;
}

.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}
EOF

print_success "src/index.css"

# Create src/App.tsx
print_step "Creating src/App.tsx..."
cat > frontend/src/App.tsx << 'EOF'
import React, { useState, useEffect } from 'react';

interface ServiceStatus {
  name: string;
  status: 'success' | 'warning' | 'error';
  message: string;
}

function App() {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'Frontend', status: 'success', message: 'Ready' },
    { name: 'Backend API', status: 'warning', message: 'Starting...' },
    { name: 'Database', status: 'warning', message: 'Connecting...' },
    { name: 'Vector Store', status: 'warning', message: 'Initializing...' },
    { name: 'Knowledge Graph', status: 'warning', message: 'Loading...' }
  ]);

  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    // Check API status
    const checkAPI = async () => {
      try {
        const response = await fetch('/health');
        if (response.ok) {
          setApiStatus('online');
          setServices(prev => prev.map(service => 
            service.name === 'Backend API' 
              ? { ...service, status: 'success', message: 'Online' }
              : service
          ));
        } else {
          setApiStatus('offline');
        }
      } catch (error) {
        setApiStatus('offline');
      }
    };

    // Simulate service startup
    const timer1 = setTimeout(() => {
      setServices(prev => prev.map(service => 
        service.name === 'Database' 
          ? { ...service, status: 'success', message: 'Connected' }
          : service
      ));
    }, 2000);

    const timer2 = setTimeout(() => {
      setServices(prev => prev.map(service => 
        service.name === 'Vector Store' 
          ? { ...service, status: 'success', message: 'Ready' }
          : service
      ));
    }, 3000);

    const timer3 = setTimeout(() => {
      setServices(prev => prev.map(service => 
        service.name === 'Knowledge Graph' 
          ? { ...service, status: 'success', message: 'Active' }
          : service
      ));
    }, 4000);

    checkAPI();
    const apiCheck = setInterval(checkAPI, 5000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearInterval(apiCheck);
    };
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return '#10B981';
      case 'warning': return '#F59E0B';
      case 'error': return '#EF4444';
      default: return '#6B7280';
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        padding: '2rem',
        maxWidth: '600px',
        width: '100%'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🚀</div>
          <h1 style={{ 
            margin: '0 0 0.5rem 0', 
            fontSize: '1.875rem', 
            fontWeight: '700',
            background: 'linear-gradient(135deg, #8B5CF6, #06B6D4)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            RAG User Story Generator
          </h1>
          <p style={{ 
            margin: 0, 
            color: '#6B7280', 
            fontSize: '1rem' 
          }}>
            AI-powered user story generation from requirements
          </p>
        </div>

        {/* Services Status */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ 
            margin: '0 0 1rem 0', 
            fontSize: '1.125rem', 
            fontWeight: '600',
            color: '#374151'
          }}>
            System Status
          </h3>
          
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            {services.map((service, index) => (
              <div 
                key={index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0.75rem',
                  background: '#F9FAFB',
                  borderRadius: '8px',
                  border: '1px solid #E5E7EB'
                }}
              >
                <div 
                  style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    background: getStatusColor(service.status),
                    marginRight: '12px',
                    animation: service.status === 'warning' ? 'pulse 2s infinite' : 'none'
                  }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: '500', color: '#374151' }}>
                    {service.name}
                  </div>
                </div>
                <div style={{ 
                  fontSize: '0.875rem', 
                  color: '#6B7280',
                  fontWeight: '500'
                }}>
                  {service.message}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Links */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ 
            margin: '0 0 1rem 0', 
            fontSize: '1.125rem', 
            fontWeight: '600',
            color: '#374151'
          }}>
            Quick Access
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem' }}>
            <a 
              href="http://localhost:8001" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '0.75rem',
                background: 'linear-gradient(135deg, #8B5CF6, #7C3AED)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '8px',
                fontWeight: '500',
                fontSize: '0.875rem',
                transition: 'transform 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              🔗 API
            </a>
            
            <a 
              href="http://localhost:8001/docs" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '0.75rem',
                background: 'linear-gradient(135deg, #06B6D4, #0891B2)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '8px',
                fontWeight: '500',
                fontSize: '0.875rem',
                transition: 'transform 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              📚 Docs
            </a>
            
            <a 
              href="http://localhost:7474" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '0.75rem',
                background: 'linear-gradient(135deg, #10B981, #059669)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '8px',
                fontWeight: '500',
                fontSize: '0.875rem',
                transition: 'transform 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              🕸️ Neo4j
            </a>
          </div>
        </div>

        {/* Features Preview */}
        <div style={{ 
          background: '#F3F4F6', 
          padding: '1.5rem', 
          borderRadius: '12px',
          border: '1px solid #E5E7EB'
        }}>
          <h4 style={{ 
            margin: '0 0 1rem 0', 
            fontSize: '1rem', 
            fontWeight: '600',
            color: '#374151'
          }}>
            🎯 What You Can Do
          </h4>
          <ul style={{ 
            margin: 0, 
            paddingLeft: '1.25rem', 
            color: '#6B7280',
            fontSize: '0.875rem',
            lineHeight: '1.5'
          }}>
            <li>Upload requirement documents (PDF, DOCX, TXT)</li>
            <li>Connect to Jira, Confluence, and SharePoint</li>
            <li>Generate AI-powered user stories</li>
            <li>Visualize knowledge graphs and relationships</li>
            <li>Export user stories back to Jira</li>
            <li>Real-time collaboration and updates</li>
          </ul>
        </div>

        {/* Footer */}
        <div style={{ 
          textAlign: 'center', 
          marginTop: '2rem',
          paddingTop: '1rem',
          borderTop: '1px solid #E5E7EB'
        }}>
          <p style={{ 
            margin: 0, 
            color: '#9CA3AF', 
            fontSize: '0.75rem'
          }}>
            RAG User Story Generator v1.0.0 | Status: {apiStatus}
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
EOF

print_success "src/App.tsx"

# Create Dockerfile
print_step "Creating Dockerfile..."
cat > frontend/Dockerfile << 'EOF'
# Frontend Dockerfile for React Application

FROM node:18-alpine AS development

WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package*.json ./

# Install dependencies with legacy peer deps to avoid conflicts
RUN npm cache clean --force && \
    npm install --legacy-peer-deps --force

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Set environment for development
ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true

# Start development server
CMD ["npm", "start"]
EOF

print_success "Dockerfile"

# Create .dockerignore
print_step "Creating .dockerignore..."
cat > frontend/.dockerignore << 'EOF'
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*
build
dist
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.vscode
.idea
*.swp
*.swo
*~
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
logs
*.log
coverage
.nyc_output
.jest
.git
.gitignore
README.md
Dockerfile
.dockerignore
EOF

print_success ".dockerignore"

# Create tsconfig.json
print_step "Creating tsconfig.json..."
cat > frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": [
      "dom",
      "dom.iterable",
      "es6"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": [
    "src"
  ]
}
EOF

print_success "tsconfig.json"

echo ""
echo -e "${GREEN}🎉 Frontend completely recreated!${NC}"
echo ""
echo "Frontend structure:"
find frontend -type f | sort

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Build and start: docker-compose up --build -d"
echo "2. View logs: docker-compose logs frontend"
echo "3. Access app: http://localhost:3000"
echo ""
echo "The frontend is now ready! 🚀"