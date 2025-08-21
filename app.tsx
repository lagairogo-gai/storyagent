/**
 * Main React Application - RAG User Story Generator
 * Features n8n-inspired design with animated connectors
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import Sidebar from './components/common/Sidebar';
import Header from './components/common/Header';
import LoadingSpinner from './components/common/LoadingSpinner';
import ErrorBoundary from './components/common/ErrorBoundary';

// Pages
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Documents from './pages/Documents';
import UserStories from './pages/UserStories';
import Integrations from './pages/Integrations';
import KnowledgeGraph from './pages/KnowledgeGraph';
import Settings from './pages/Settings';
import Login from './pages/Login';

// Hooks
import { useAuth } from './hooks/useAuth';
import { useTheme } from './hooks/useTheme';

// Types
import { User, Theme } from './types';

// Styles
import './styles/globals.css';
import './styles/animations.css';
import './styles/n8n-theme.css';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const { user, loading: authLoading, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  // Show loading spinner during initial load
  if (isLoading || authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-n8n-purple-light via-n8n-blue-light to-n8n-teal-light dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
        <LoadingSpinner size="large" message="Loading RAG User Story Generator..." />
      </div>
    );
  }

  // Show login if not authenticated
  if (!user) {
    return (
      <QueryClientProvider client={queryClient}>
        <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </Router>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              className: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
            }}
          />
        </div>
      </QueryClientProvider>
    );
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
          <Router>
            <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
              {/* Animated Background */}
              <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <AnimatedBackground />
              </div>

              {/* Sidebar */}
              <AnimatePresence>
                {sidebarOpen && (
                  <motion.div
                    initial={{ x: -280 }}
                    animate={{ x: 0 }}
                    exit={{ x: -280 }}
                    transition={{ type: "spring", damping: 20 }}
                    className="relative z-10"
                  >
                    <Sidebar
                      user={user}
                      onClose={() => setSidebarOpen(false)}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Main Content */}
              <div className={`flex-1 flex flex-col transition-all duration-300 ${
                sidebarOpen ? 'ml-0' : ''
              }`}>
                <Header
                  user={user}
                  sidebarOpen={sidebarOpen}
                  setSidebarOpen={setSidebarOpen}
                  theme={theme}
                  toggleTheme={toggleTheme}
                  onLogout={logout}
                />

                <main className="flex-1 overflow-auto relative z-10">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="container mx-auto px-6 py-8"
                  >
                    <Routes>
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/projects" element={<Projects />} />
                      <Route path="/projects/:id" element={<Projects />} />
                      <Route path="/documents" element={<Documents />} />
                      <Route path="/user-stories" element={<UserStories />} />
                      <Route path="/integrations" element={<Integrations />} />
                      <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
                      <Route path="/settings" element={<Settings />} />
                      <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                  </motion.div>
                </main>
              </div>
            </div>
          </Router>

          {/* Toast Notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              className: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100',
              style: {
                background: 'var(--toast-bg)',
                color: 'var(--toast-color)',
                border: '1px solid var(--toast-border)',
              },
            }}
          />
        </div>

        {/* React Query DevTools */}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

/**
 * Animated Background Component with n8n-style connectors
 */
const AnimatedBackground: React.FC = () => {
  const [nodes, setNodes] = useState<Array<{ x: number; y: number; id: string }>>([]);
  const [connections, setConnections] = useState<Array<{ from: string; to: string; progress: number }>>([]);

  useEffect(() => {
    // Generate random nodes
    const generateNodes = () => {
      const newNodes = Array.from({ length: 8 }, (_, i) => ({
        id: `node-${i}`,
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
      }));
      setNodes(newNodes);

      // Generate connections between nearby nodes
      const newConnections: Array<{ from: string; to: string; progress: number }> = [];
      for (let i = 0; i < newNodes.length; i++) {
        for (let j = i + 1; j < newNodes.length; j++) {
          const distance = Math.sqrt(
            Math.pow(newNodes[i].x - newNodes[j].x, 2) + 
            Math.pow(newNodes[i].y - newNodes[j].y, 2)
          );
          
          if (distance < 300 && Math.random() > 0.6) {
            newConnections.push({
              from: newNodes[i].id,
              to: newNodes[j].id,
              progress: 0,
            });
          }
        }
      }
      setConnections(newConnections);
    };

    generateNodes();

    // Animate connection progress
    const animateConnections = () => {
      setConnections(prev => 
        prev.map(conn => ({
          ...conn,
          progress: (conn.progress + 0.02) % 1,
        }))
      );
    };

    const interval = setInterval(animateConnections, 50);
    const resizeHandler = () => generateNodes();
    
    window.addEventListener('resize', resizeHandler);

    return () => {
      clearInterval(interval);
      window.removeEventListener('resize', resizeHandler);
    };
  }, []);

  return (
    <svg className="absolute inset-0 w-full h-full opacity-30 dark:opacity-20">
      <defs>
        <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0" />
          <stop offset="50%" stopColor="#06B6D4" stopOpacity="1" />
          <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
        </linearGradient>
        
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      {/* Render connections */}
      {connections.map((connection, index) => {
        const fromNode = nodes.find(n => n.id === connection.from);
        const toNode = nodes.find(n => n.id === connection.to);
        
        if (!fromNode || !toNode) return null;

        const length = Math.sqrt(
          Math.pow(toNode.x - fromNode.x, 2) + Math.pow(toNode.y - fromNode.y, 2)
        );
        
        const angle = Math.atan2(toNode.y - fromNode.y, toNode.x - fromNode.x);
        
        return (
          <g key={`connection-${index}`}>
            {/* Connection line */}
            <line
              x1={fromNode.x}
              y1={fromNode.y}
              x2={toNode.x}
              y2={toNode.y}
              stroke="url(#connectionGradient)"
              strokeWidth="2"
              opacity="0.6"
            />
            
            {/* Animated pulse */}
            <circle
              cx={fromNode.x + (toNode.x - fromNode.x) * connection.progress}
              cy={fromNode.y + (toNode.y - fromNode.y) * connection.progress}
              r="4"
              fill="#06B6D4"
              filter="url(#glow)"
              opacity="0.8"
            >
              <animate
                attributeName="r"
                values="4;6;4"
                dur="2s"
                repeatCount="indefinite"
              />
            </circle>
          </g>
        );
      })}

      {/* Render nodes */}
      {nodes.map((node, index) => (
        <g key={node.id}>
          <circle
            cx={node.x}
            cy={node.y}
            r="6"
            fill="#8B5CF6"
            opacity="0.8"
            filter="url(#glow)"
          >
            <animate
              attributeName="opacity"
              values="0.4;0.8;0.4"
              dur={`${2 + index * 0.3}s`}
              repeatCount="indefinite"
            />
          </circle>
          
          {/* Node pulse ring */}
          <circle
            cx={node.x}
            cy={node.y}
            r="10"
            fill="none"
            stroke="#8B5CF6"
            strokeWidth="1"
            opacity="0.4"
          >
            <animate
              attributeName="r"
              values="6;20;6"
              dur="3s"
              repeatCount="indefinite"
              begin={`${index * 0.5}s`}
            />
            <animate
              attributeName="opacity"
              values="0.6;0;0.6"
              dur="3s"
              repeatCount="indefinite"
              begin={`${index * 0.5}s`}
            />
          </circle>
        </g>
      ))}
    </svg>
  );
};

export default App;