/**
 * Dashboard Component - Main overview page
 * Features: Real-time metrics, activity feed, quick actions, visual workflow
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';
import {
  DocumentTextIcon,
  UserGroupIcon,
  ChartBarIcon,
  CogIcon,
  PlayIcon,
  PlusIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  LightBulbIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';

// Hooks
import { useQuery } from 'react-query';
import { useDashboard } from '../hooks/useDashboard';
import { useWebSocket } from '../hooks/useWebSocket';

// Components
import MetricCard from '../components/common/MetricCard';
import ActivityFeed from '../components/common/ActivityFeed';
import QuickActions from '../components/common/QuickActions';
import WorkflowVisualization from '../components/visualization/WorkflowVisualization';
import RecentProjects from '../components/common/RecentProjects';
import GenerationProgress from '../components/common/GenerationProgress';

// Types
import { DashboardData, Activity, Project, UserStory } from '../types';

// Services
import { dashboardService } from '../services/api';

const Dashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [activeGeneration, setActiveGeneration] = useState<string | null>(null);

  // Fetch dashboard data
  const { data: dashboardData, isLoading, error, refetch } = useQuery<DashboardData>(
    ['dashboard', timeRange],
    () => dashboardService.getDashboardData(timeRange),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
      staleTime: 10000,
    }
  );

  // WebSocket for real-time updates
  const { lastMessage, connectionStatus } = useWebSocket('/ws/dashboard');

  // Handle real-time updates
  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data);
      
      switch (data.type) {
        case 'generation_progress':
          setActiveGeneration(data.session_id);
          break;
        case 'generation_complete':
          setActiveGeneration(null);
          refetch(); // Refresh dashboard data
          break;
        case 'new_activity':
          refetch(); // Refresh to show new activity
          break;
      }
    }
  }, [lastMessage, refetch]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="n8n-loading">
          <div className="n8n-spinner"></div>
          <span className="text-gray-600 dark:text-gray-400">Loading dashboard...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            Failed to load dashboard
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            There was an error loading your dashboard data.
          </p>
          <button
            onClick={() => refetch()}
            className="n8n-btn n8n-btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const metrics = dashboardData?.metrics || {};
  const activities = dashboardData?.activities || [];
  const projects = dashboardData?.recentProjects || [];
  const chartData = dashboardData?.chartData || {};

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Welcome back! Here's what's happening with your user stories.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="flex items-center gap-4 mt-4 sm:mt-0"
        >
          {/* Connection Status */}
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${
              connectionStatus === 'Connected' ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-gray-600 dark:text-gray-400">
              {connectionStatus}
            </span>
          </div>

          {/* Time Range Selector */}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as '7d' | '30d' | '90d')}
            className="n8n-input n8n-select w-32"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </motion.div>
      </div>

      {/* Active Generation Progress */}
      {activeGeneration && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          <GenerationProgress sessionId={activeGeneration} />
        </motion.div>
      )}

      {/* Metrics Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        <MetricCard
          title="Total Projects"
          value={metrics.totalProjects || 0}
          change={metrics.projectsChange || 0}
          icon={UserGroupIcon}
          color="purple"
        />
        <MetricCard
          title="Documents Processed"
          value={metrics.totalDocuments || 0}
          change={metrics.documentsChange || 0}
          icon={DocumentTextIcon}
          color="blue"
        />
        <MetricCard
          title="User Stories Generated"
          value={metrics.totalUserStories || 0}
          change={metrics.userStoriesChange || 0}
          icon={ChartBarIcon}
          color="teal"
        />
        <MetricCard
          title="Average Quality Score"
          value={`${(metrics.averageQuality || 0).toFixed(1)}%`}
          change={metrics.qualityChange || 0}
          icon={ArrowTrendingUpIcon}
          color="pink"
        />
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <QuickActions />
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Charts */}
        <div className="lg:col-span-2 space-y-8">
          {/* User Stories Generation Trend */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="n8n-card p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                User Stories Generation Trend
              </h3>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <ArrowTrendingUpIcon className="w-4 h-4" />
                <span>+{metrics.userStoriesChange || 0}% vs last period</span>
              </div>
            </div>
            
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData.userStoriesTrend || []}>
                <defs>
                  <linearGradient id="colorStories" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis 
                  dataKey="date" 
                  stroke="#6B7280"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#6B7280"
                  fontSize={12}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="stories" 
                  stroke="#8B5CF6" 
                  fillOpacity={1} 
                  fill="url(#colorStories)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Document Processing Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="n8n-card p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
              Document Processing Statistics
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Processing Status Pie Chart */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Processing Status
                </h4>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={chartData.documentStatus || []}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {(chartData.documentStatus || []).map((entry, index) => {
                        const colors = ['#10B981', '#F59E0B', '#EF4444', '#6B7280'];
                        return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                      })}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Processing Time Bar Chart */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Average Processing Time by Type
                </h4>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={chartData.processingTime || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis 
                      dataKey="type" 
                      stroke="#6B7280"
                      fontSize={10}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis 
                      stroke="#6B7280"
                      fontSize={10}
                    />
                    <Tooltip 
                      formatter={(value) => [`${value}s`, 'Processing Time']}
                    />
                    <Bar 
                      dataKey="time" 
                      fill="url(#gradientBar)"
                      radius={[4, 4, 0, 0]}
                    />
                    <defs>
                      <linearGradient id="gradientBar" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.6}/>
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </motion.div>

          {/* Workflow Visualization */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="n8n-card p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
              RAG Workflow Overview
            </h3>
            <WorkflowVisualization />
          </motion.div>
        </div>

        {/* Right Column - Activity Feed & Recent Projects */}
        <div className="space-y-8">
          {/* Recent Projects */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="n8n-card p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Recent Projects
              </h3>
              <button className="text-sm text-purple-600 hover:text-purple-700 font-medium">
                View All
              </button>
            </div>
            <RecentProjects projects={projects} />
          </motion.div>

          {/* Activity Feed */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="n8n-card p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Recent Activity
              </h3>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-xs text-gray-500">Live</span>
              </div>
            </div>
            <ActivityFeed activities={activities} />
          </motion.div>

          {/* System Health */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="n8n-card p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
              System Health
            </h3>
            
            <div className="space-y-4">
              <HealthIndicator
                label="API Status"
                status="healthy"
                value="99.9% uptime"
              />
              <HealthIndicator
                label="Vector Database"
                status="healthy"
                value="Connected"
              />
              <HealthIndicator
                label="Knowledge Graph"
                status="healthy"
                value="Active"
              />
              <HealthIndicator
                label="LLM Services"
                status="warning"
                value="2/3 providers"
              />
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

// Health Indicator Component
interface HealthIndicatorProps {
  label: string;
  status: 'healthy' | 'warning' | 'error';
  value: string;
}

const HealthIndicator: React.FC<HealthIndicatorProps> = ({ label, status, value }) => {
  const statusColors = {
    healthy: 'text-green-600 bg-green-100',
    warning: 'text-yellow-600 bg-yellow-100',
    error: 'text-red-600 bg-red-100',
  };

  const statusIcons = {
    healthy: CheckCircleIcon,
    warning: ExclamationTriangleIcon,
    error: ExclamationTriangleIcon,
  };

  const StatusIcon = statusIcons[status];

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className={`p-1 rounded-full ${statusColors[status]}`}>
          <StatusIcon className="w-4 h-4" />
        </div>
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </span>
      </div>
      <span className="text-sm text-gray-500 dark:text-gray-400">
        {value}
      </span>
    </div>
  );
};

export default Dashboard;