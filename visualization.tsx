/**
 * Workflow Visualization Component
 * Shows the RAG pipeline with animated connectors in n8n style
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  DocumentTextIcon,
  CpuChipIcon,
  MagnifyingGlassIcon,
  LightBulbIcon,
  ShareIcon,
  CogIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  PlayIcon,
  PauseIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

// Types
interface WorkflowNode {
  id: string;
  type: 'source' | 'process' | 'output';
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  status: 'idle' | 'running' | 'success' | 'error';
  position: { x: number; y: number };
  metrics?: {
    processed: number;
    total: number;
    duration?: number;
  };
}

interface Connection {
  from: string;
  to: string;
  animated: boolean;
  progress: number;
  data?: any;
}

const WorkflowVisualization: React.FC = () => {
  const [nodes, setNodes] = useState<WorkflowNode[]>([
    {
      id: 'document-input',
      type: 'source',
      title: 'Document Input',
      description: 'Jira, Confluence, SharePoint, Uploads',
      icon: DocumentTextIcon,
      status: 'success',
      position: { x: 50, y: 100 },
      metrics: { processed: 24, total: 30 }
    },
    {
      id: 'text-extraction',
      type: 'process',
      title: 'Text Extraction',
      description: 'Parse and extract content',
      icon: CpuChipIcon,
      status: 'running',
      position: { x: 250, y: 60 },
      metrics: { processed: 18, total: 24, duration: 45 }
    },
    {
      id: 'knowledge-graph',
      type: 'process',
      title: 'Knowledge Graph',
      description: 'Build semantic relationships',
      icon: ShareIcon,
      status: 'running',
      position: { x: 250, y: 140 },
      metrics: { processed: 15, total: 18, duration: 120 }
    },
    {
      id: 'vectorization',
      type: 'process',
      title: 'Vectorization',
      description: 'Create embeddings',
      icon: CogIcon,
      status: 'success',
      position: { x: 450, y: 100 },
      metrics: { processed: 24, total: 24, duration: 30 }
    },
    {
      id: 'rag-retrieval',
      type: 'process',
      title: 'RAG Retrieval',
      description: 'Semantic search & context',
      icon: MagnifyingGlassIcon,
      status: 'idle',
      position: { x: 650, y: 100 },
      metrics: { processed: 0, total: 10 }
    },
    {
      id: 'llm-generation',
      type: 'process',
      title: 'LLM Generation',
      description: 'Generate user stories',
      icon: LightBulbIcon,
      status: 'idle',
      position: { x: 850, y: 100 },
      metrics: { processed: 0, total: 10 }
    }
  ]);

  const [connections, setConnections] = useState<Connection[]>([
    { from: 'document-input', to: 'text-extraction', animated: true, progress: 0.7 },
    { from: 'document-input', to: 'knowledge-graph', animated: true, progress: 0.5 },
    { from: 'text-extraction', to: 'vectorization', animated: true, progress: 0.3 },
    { from: 'knowledge-graph', to: 'vectorization', animated: false, progress: 0 },
    { from: 'vectorization', to: 'rag-retrieval', animated: false, progress: 0 },
    { from: 'rag-retrieval', to: 'llm-generation', animated: false, progress: 0 }
  ]);

  const [isPlaying, setIsPlaying] = useState(true);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  // Animate workflow progress
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setConnections(prev => 
        prev.map(conn => ({
          ...conn,
          progress: conn.animated ? (conn.progress + 0.02) % 1 : conn.progress
        }))
      );

      // Simulate node status changes
      setNodes(prev => 
        prev.map(node => {
          if (node.metrics && node.status === 'running') {
            const newProcessed = Math.min(
              node.metrics.processed + Math.random() * 0.5,
              node.metrics.total
            );
            
            return {
              ...node,
              metrics: {
                ...node.metrics,
                processed: newProcessed
              },
              status: newProcessed >= node.metrics.total ? 'success' : 'running'
            };
          }
          return node;
        })
      );
    }, 100);

    return () => clearInterval(interval);
  }, [isPlaying]);

  const getNodeStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'from-blue-500 to-purple-500';
      case 'success': return 'from-green-500 to-teal-500';
      case 'error': return 'from-red-500 to-pink-500';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return ArrowPathIcon;
      case 'success': return CheckCircleIcon;
      case 'error': return ExclamationTriangleIcon;
      default: return ClockIcon;
    }
  };

  return (
    <div className="relative w-full h-96 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-lg overflow-hidden">
      {/* Controls */}
      <div className="absolute top-4 right-4 flex items-center gap-2 z-20">
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow"
          title={isPlaying ? 'Pause Animation' : 'Play Animation'}
        >
          {isPlaying ? (
            <PauseIcon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          ) : (
            <PlayIcon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          )}
        </button>
      </div>

      {/* SVG for connections */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 1 }}>
        <defs>
          <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.3" />
            <stop offset="50%" stopColor="#06B6D4" stopOpacity="1" />
            <stop offset="100%" stopColor="#10B981" stopOpacity="0.3" />
          </linearGradient>
          
          <filter id="connectionGlow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge> 
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {connections.map((connection, index) => {
          const fromNode = nodes.find(n => n.id === connection.from);
          const toNode = nodes.find(n => n.id === connection.to);
          
          if (!fromNode || !toNode) return null;

          const startX = fromNode.position.x + 40; // Node width/2
          const startY = fromNode.position.y + 40; // Node height/2
          const endX = toNode.position.x + 40;
          const endY = toNode.position.y + 40;

          // Create curved path
          const midX = (startX + endX) / 2;
          const midY = Math.min(startY, endY) - 30;
          const pathD = `M ${startX} ${startY} Q ${midX} ${midY} ${endX} ${endY}`;

          return (
            <g key={`connection-${index}`}>
              {/* Connection path */}
              <path
                d={pathD}
                fill="none"
                stroke="url(#connectionGradient)"
                strokeWidth="3"
                opacity={connection.animated ? "0.8" : "0.3"}
                filter={connection.animated ? "url(#connectionGlow)" : "none"}
              />
              
              {/* Animated data flow */}
              {connection.animated && (
                <circle
                  r="4"
                  fill="#06B6D4"
                  filter="url(#connectionGlow)"
                  opacity="0.9"
                >
                  <animateMotion
                    dur="3s"
                    repeatCount="indefinite"
                    path={pathD}
                  />
                  <animate
                    attributeName="r"
                    values="3;5;3"
                    dur="1s"
                    repeatCount="indefinite"
                  />
                </circle>
              )}
            </g>
          );
        })}
      </svg>

      {/* Nodes */}
      {nodes.map((node, index) => {
        const StatusIcon = getStatusIcon(node.status);
        const NodeIcon = node.icon;
        const progress = node.metrics ? (node.metrics.processed / node.metrics.total) * 100 : 0;

        return (
          <motion.div
            key={node.id}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="absolute cursor-pointer group"
            style={{
              left: node.position.x,
              top: node.position.y,
              zIndex: 10
            }}
            onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)}
          >
            {/* Node */}
            <div className={`relative w-20 h-20 rounded-xl bg-gradient-to-br ${getNodeStatusColor(node.status)} 
              shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110`}>
              
              {/* Node Icon */}
              <div className="absolute inset-0 flex items-center justify-center">
                <NodeIcon className="w-8 h-8 text-white" />
              </div>

              {/* Status Indicator */}
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-white dark:bg-gray-800 rounded-full 
                flex items-center justify-center shadow-md">
                <StatusIcon className={`w-4 h-4 ${
                  node.status === 'running' ? 'text-blue-500 animate-spin' :
                  node.status === 'success' ? 'text-green-500' :
                  node.status === 'error' ? 'text-red-500' : 'text-gray-400'
                }`} />
              </div>

              {/* Progress Ring */}
              {node.status === 'running' && node.metrics && (
                <svg className="absolute -inset-1 w-22 h-22">
                  <circle
                    cx="44"
                    cy="44"
                    r="42"
                    fill="none"
                    stroke="rgba(255,255,255,0.3)"
                    strokeWidth="2"
                  />
                  <circle
                    cx="44"
                    cy="44"
                    r="42"
                    fill="none"
                    stroke="white"
                    strokeWidth="2"
                    strokeDasharray={`${2 * Math.PI * 42}`}
                    strokeDashoffset={`${2 * Math.PI * 42 * (1 - progress / 100)}`}
                    transform="rotate(-90 44 44)"
                    className="transition-all duration-300"
                  />
                </svg>
              )}
            </div>

            {/* Node Label */}
            <div className="absolute top-24 left-1/2 transform -translate-x-1/2 text-center">
              <div className="text-xs font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
                {node.title}
              </div>
              {node.metrics && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {Math.round(node.metrics.processed)}/{node.metrics.total}
                </div>
              )}
            </div>

            {/* Tooltip */}
            <AnimatePresence>
              {selectedNode === node.id && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8, y: 10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.8, y: 10 }}
                  className="absolute top-28 left-1/2 transform -translate-x-1/2 z-30"
                >
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 
                    dark:border-gray-700 p-4 min-w-48">
                    <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                      {node.title}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {node.description}
                    </p>
                    
                    {node.metrics && (
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Progress:</span>
                          <span className="font-medium text-gray-900 dark:text-gray-100">
                            {Math.round(progress)}%
                          </span>
                        </div>
                        
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                        
                        {node.metrics.duration && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Duration:</span>
                            <span className="font-medium text-gray-900 dark:text-gray-100">
                              {node.metrics.duration}s
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        );
      })}

      