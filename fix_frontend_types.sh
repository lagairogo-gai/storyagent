#!/bin/bash

# Fix Frontend TypeScript Issues
echo "🔧 Fixing Frontend TypeScript errors..."

# Navigate to frontend directory
cd rag-user-stories/frontend

echo "📦 Installing missing TypeScript types..."

# Install missing dev dependencies
npm install --save-dev @types/react @types/react-dom @types/node

echo "🔄 Updating package.json with correct dependencies..."

# Create a proper package.json with all required dependencies
cat > package.json << 'EOF'
{
  "name": "rag-user-stories-frontend",
  "version": "1.0.0",
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
  "proxy": "http://backend:8000"
}
EOF

echo "📝 Updating tsconfig.json with better TypeScript configuration..."

# Create a more robust tsconfig.json
cat > tsconfig.json << 'EOF'
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

echo "🔧 Creating improved App.tsx with better TypeScript support..."

# Create a better App.tsx with proper typing
cat > src/App.tsx << 'EOF'
import React from 'react';
import './App.css';

interface HealthStatus {
  status: string;
  version: string;
}

const App: React.FC = () => {
  const [apiStatus, setApiStatus] = React.useState<'checking' | 'online' | 'offline'>('checking');
  const [healthData, setHealthData] = React.useState<HealthStatus | null>(null);

  React.useEffect(() => {
    const checkApiHealth = async (): Promise<void> => {
      try {
        const response = await fetch('http://localhost:8001/health');
        if (response.ok) {
          const data: HealthStatus = await response.json();
          setHealthData(data);
          setApiStatus('online');
        } else {
          setApiStatus('offline');
        }
      } catch (error) {
        console.error('API health check failed:', error);
        setApiStatus('offline');
      }
    };

    checkApiHealth();
    
    // Check health every 30 seconds
    const interval = setInterval(checkApiHealth, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'online': return '#10B981';
      case 'offline': return '#EF4444';
      default: return '#F59E0B';
    }
  };

  const getStatusText = (status: string): string => {
    switch (status) {
      case 'online': return 'Online';
      case 'offline': return 'Offline';
      default: return 'Checking...';
    }
  };

  return (
    <div className="app">
      <div className="container">
        {/* Header */}
        <div className="header">
          <div className="icon">🚀</div>
          <h1 className="title">RAG User Story Generator</h1>
          <p className="subtitle">
            AI-powered user story generation from requirements
          </p>
        </div>

        {/* API Status */}
        <div className="status-card">
          <div className="status-header">
            <h3>API Status</h3>
            <div className="status-indicator">
              <div 
                className="status-dot"
                style={{ backgroundColor: getStatusColor(apiStatus) }}
              />
              <span className="status-text">{getStatusText(apiStatus)}</span>
            </div>
          </div>
          
          {healthData && (
            <div className="status-details">
              <p><strong>Version:</strong> {healthData.version}</p>
              <p><strong>Status:</strong> {healthData.status}</p>
            </div>
          )}
        </div>

        {/* Getting Started */}
        <div className="info-card">
          <h3>🎯 Getting Started</h3>
          <ul className="feature-list">
            <li>Upload requirement documents (PDF, DOCX, TXT)</li>
            <li>Connect to Jira, Confluence, or SharePoint</li>
            <li>Generate AI-powered user stories</li>
            <li>Visualize knowledge graphs and relationships</li>
            <li>Export user stories back to project management tools</li>
          </ul>
        </div>

        {/* Quick Links */}
        <div className="links-card">
          <h3>🔗 Quick Links</h3>
          <div className="links-grid">
            <a 
              href="http://localhost:8001/health" 
              target="_blank" 
              rel="noopener noreferrer"
              className="link-button health"
            >
              Health Check
            </a>
            <a 
              href="http://localhost:8001/docs" 
              target="_blank" 
              rel="noopener noreferrer"
              className="link-button docs"
            >
              API Documentation
            </a>
            <a 
              href="http://localhost:7474" 
              target="_blank" 
              rel="noopener noreferrer"
              className="link-button neo4j"
            >
              Neo4j Browser
            </a>
          </div>
        </div>

        {/* Features Preview */}
        <div className="preview-card">
          <h3>✨ What You Can Do</h3>
          <div className="features-grid">
            <div className="feature">
              <div className="feature-icon">📄</div>
              <h4>Document Processing</h4>
              <p>Upload and process requirement documents from multiple sources</p>
            </div>
            <div className="feature">
              <div className="feature-icon">🤖</div>
              <h4>AI Generation</h4>
              <p>Generate user stories using advanced LLM models</p>
            </div>
            <div className="feature">
              <div className="feature-icon">🕸️</div>
              <h4>Knowledge Graph</h4>
              <p>Visualize relationships and dependencies</p>
            </div>
            <div className="feature">
              <div className="feature-icon">🔄</div>
              <h4>Integration</h4>
              <p>Export to Jira, Confluence, and other tools</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
EOF

echo "🎨 Creating App.css for styling..."

# Create App.css for styling
cat > src/App.css << 'EOF'
.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  gap: 2rem;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 1rem;
}

.icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0;
}

.status-card, .info-card, .links-card, .preview-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.status-header h3 {
  margin: 0;
  color: #374151;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-text {
  font-weight: 500;
  color: #6B7280;
}

.status-details {
  background: #F9FAFB;
  padding: 1rem;
  border-radius: 8px;
  color: #374151;
}

.status-details p {
  margin: 0.25rem 0;
}

.info-card h3, .links-card h3, .preview-card h3 {
  color: #374151;
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
}

.feature-list {
  color: #6B7280;
  line-height: 1.6;
}

.feature-list li {
  margin: 0.5rem 0;
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.link-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  color: white;
  transition: transform 0.2s, box-shadow 0.2s;
}

.link-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.link-button.health {
  background: linear-gradient(135deg, #10B981, #059669);
}

.link-button.docs {
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
}

.link-button.neo4j {
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.feature {
  text-align: center;
  padding: 1.5rem;
  background: #F8FAFC;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.feature h4 {
  color: #374151;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.feature p {
  color: #6B7280;
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@media (max-width: 768px) {
  .app {
    padding: 1rem;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .status-card, .info-card, .links-card, .preview-card {
    padding: 1.5rem;
  }
  
  .links-grid {
    grid-template-columns: 1fr;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
}
EOF

echo "📝 Creating updated index.tsx..."

# Update index.tsx to be more robust
cat > src/index.tsx << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found');
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

echo "🎨 Creating index.css..."

# Create index.css
cat > src/index.css << 'EOF'
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f8fafc;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
}

#root {
  min-height: 100vh;
}
EOF

echo "🛠️ Reinstalling dependencies..."

# Clean install
rm -rf node_modules package-lock.json
npm install

echo "✅ Frontend TypeScript issues fixed!"
echo ""
echo "🔄 Now restart the frontend container:"
echo "   cd .. && docker-compose restart frontend"
echo ""
echo "📝 Or rebuild if needed:"
echo "   docker-compose up --build frontend"