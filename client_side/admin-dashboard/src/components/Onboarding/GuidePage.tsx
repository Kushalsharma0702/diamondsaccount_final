import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Upload, CheckSquare, Bell, Shield, TrendingUp } from 'lucide-react';
import { Button } from '../common/Button';

interface GuidePageProps {
  onComplete: () => void;
}

const features = [
  {
    icon: FileText,
    title: 'Client Requests',
    description: 'View and manage all incoming client filing requests',
  },
  {
    icon: Upload,
    title: 'Document Submissions',
    description: 'Review and approve client-submitted documents',
  },
  {
    icon: CheckSquare,
    title: 'Status Tracking',
    description: 'Monitor filing progress in real-time',
  },
  {
    icon: Bell,
    title: 'Notifications',
    description: 'Stay updated with instant alerts',
  },
  {
    icon: Shield,
    title: 'Secure & Encrypted',
    description: 'Bank-level security for all data',
  },
  {
    icon: TrendingUp,
    title: 'Analytics Dashboard',
    description: 'Comprehensive insights and reports',
  },
];

export const GuidePage: React.FC<GuidePageProps> = ({ onComplete }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center mb-6">
            <img 
              src="/DIAMOND ACCOUNTS LOGO.png" 
              alt="Diamond Accounts" 
              className="h-24 w-auto"
            />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            Welcome to Diamond Accounts
          </h1>
          <p className="text-xl text-gray-600">
            Your complete tax filing management system
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index, duration: 0.5 }}
              className="bg-white rounded-xl p-6 shadow-md hover-lift"
            >
              <div className="bg-primary bg-opacity-10 rounded-lg p-3 inline-block mb-4">
                {React.createElement(feature.icon, {
                  size: 32,
                  className: 'text-primary',
                })}
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="text-center"
        >
          <Button onClick={onComplete} size="lg" className="px-12">
            Continue to Login
          </Button>
        </motion.div>
      </div>
    </div>
  );
};
