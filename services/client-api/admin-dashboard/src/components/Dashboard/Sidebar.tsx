import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  Upload, 
  BarChart3, 
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import type { DashboardView } from '../../types';

interface SidebarProps {
  currentView: DashboardView;
  onViewChange: (view: DashboardView) => void;
}

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', view: 'overview' as DashboardView },
  { icon: Users, label: 'Clients', view: 'clients' as DashboardView },
  { icon: FileText, label: 'Requests', view: 'requests' as DashboardView },
  { icon: Upload, label: 'Submissions', view: 'submissions' as DashboardView },
  { icon: BarChart3, label: 'Analytics', view: 'analytics' as DashboardView },
  { icon: Settings, label: 'Settings', view: 'settings' as DashboardView },
];

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onViewChange }) => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <motion.aside
      initial={{ x: -300 }}
      animate={{ x: 0, width: collapsed ? 80 : 256 }}
      transition={{ duration: 0.5 }}
      className="bg-gradient-to-b from-primary-dark to-primary text-white shadow-xl relative"
    >
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-20 bg-white text-primary rounded-full p-1 shadow-lg hover:scale-110 transition-transform z-10"
      >
        {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
      </button>

      <div className="p-6">
        <nav className="space-y-2 mt-8">
          {menuItems.map((item, index) => (
            <motion.button
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => onViewChange(item.view)}
              className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-all ${
                currentView === item.view
                  ? 'bg-white bg-opacity-20 text-white shadow-lg'
                  : 'hover:bg-white hover:bg-opacity-10 text-gray-200'
              }`}
            >
              <item.icon size={24} />
              {!collapsed && (
                <span className="font-medium text-sm">{item.label}</span>
              )}
            </motion.button>
          ))}
        </nav>
      </div>

      {!collapsed && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="absolute bottom-0 left-0 right-0 p-6 bg-primary-dark bg-opacity-50"
        >
          <div className="bg-white bg-opacity-10 rounded-lg p-4">
            <h3 className="font-semibold text-sm mb-2">Need Help?</h3>
            <p className="text-xs text-gray-300 mb-3">
              Contact support for assistance
            </p>
            <button className="w-full bg-white text-primary px-4 py-2 rounded-lg text-sm font-semibold hover:bg-opacity-90 transition-all">
              Get Support
            </button>
          </div>
        </motion.div>
      )}
    </motion.aside>
  );
};
