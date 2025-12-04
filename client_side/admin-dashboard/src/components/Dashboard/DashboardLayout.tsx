import React, { useState } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { StatusOverview } from './widgets/StatusOverview';
import { ClientRequests } from './widgets/ClientRequests';
import { DataSubmissions } from './widgets/DataSubmissions';
import { ClientsPage } from './pages/ClientsPage';
import { RequestsPage } from './pages/RequestsPage';
import { SubmissionsPage } from './pages/SubmissionsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { motion } from 'framer-motion';
import type { DashboardView } from '../../types';

export const DashboardLayout: React.FC = () => {
  const [currentView, setCurrentView] = useState<DashboardView>('overview');

  const renderContent = () => {
    switch (currentView) {
      case 'overview':
        return (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">Dashboard Overview</h1>
              <p className="text-gray-600">Welcome back! Here's what's happening today.</p>
            </div>

            <div className="space-y-6">
              <StatusOverview />
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <ClientRequests />
                <DataSubmissions />
              </div>
            </div>
          </motion.div>
        );
      case 'clients':
        return (
          <motion.div
            key="clients"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <ClientsPage />
          </motion.div>
        );
      case 'requests':
        return (
          <motion.div
            key="requests"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <RequestsPage />
          </motion.div>
        );
      case 'submissions':
        return (
          <motion.div
            key="submissions"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <SubmissionsPage />
          </motion.div>
        );
      case 'analytics':
        return (
          <motion.div
            key="analytics"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <AnalyticsPage />
          </motion.div>
        );
      case 'settings':
        return (
          <motion.div
            key="settings"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <SettingsPage />
          </motion.div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};
