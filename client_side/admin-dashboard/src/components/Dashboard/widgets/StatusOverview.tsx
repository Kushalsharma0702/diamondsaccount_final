import React from 'react';
import { motion } from 'framer-motion';
import { Users, FileText, Clock, CheckCircle } from 'lucide-react';
import { Card } from '../../common/Card';
import { statusOverview } from '../../../data/dummyData';

export const StatusOverview: React.FC = () => {
  const stats = [
    {
      icon: Users,
      label: 'Total Clients',
      value: statusOverview.totalClients,
      color: 'bg-blue-500',
      trend: '+12%',
    },
    {
      icon: FileText,
      label: 'Active Filings',
      value: statusOverview.activeFilings,
      color: 'bg-purple-500',
      trend: '+8%',
    },
    {
      icon: Clock,
      label: 'Pending Reviews',
      value: statusOverview.pendingReviews,
      color: 'bg-orange-500',
      trend: '-5%',
    },
    {
      icon: CheckCircle,
      label: 'Completed Today',
      value: statusOverview.completedToday,
      color: 'bg-green-500',
      trend: '+15%',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <Card hover className="relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                <h3 className="text-3xl font-bold text-gray-800">{stat.value}</h3>
                <span className={`text-xs font-semibold ${stat.trend.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                  {stat.trend} from last week
                </span>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                {React.createElement(stat.icon, {
                  size: 28,
                  className: 'text-white',
                })}
              </div>
            </div>
            <div className={`absolute bottom-0 left-0 right-0 h-1 ${stat.color}`} />
          </Card>
        </motion.div>
      ))}
    </div>
  );
};
