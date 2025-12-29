import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Users, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Card } from '../../common/Card';
import { analyticsData, statusOverview } from '../../../data/dummyData';

export const AnalyticsPage: React.FC = () => {
  const maxFilings = Math.max(...analyticsData.monthlyFilings.map(m => m.count));
  const maxRequests = Math.max(...analyticsData.requestsByType.map(r => r.count));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Analytics & Reports</h1>
        <p className="text-gray-600">Comprehensive insights and performance metrics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { icon: Users, label: 'Total Clients', value: statusOverview.totalClients, color: 'bg-blue-500' },
          { icon: FileText, label: 'Active Filings', value: statusOverview.activeFilings, color: 'bg-purple-500' },
          { icon: AlertCircle, label: 'Pending Reviews', value: statusOverview.pendingReviews, color: 'bg-orange-500' },
          { icon: CheckCircle, label: 'Completed Today', value: statusOverview.completedToday, color: 'bg-green-500' },
        ].map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="text-center">
              <div className={`${stat.color} w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4`}>
                {React.createElement(stat.icon, { size: 32, className: 'text-white' })}
              </div>
              <p className="text-3xl font-bold text-gray-800 mb-2">{stat.value}</p>
              <p className="text-gray-600">{stat.label}</p>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Monthly Filings Chart */}
      <Card>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Monthly Filings Trend</h2>
            <p className="text-gray-600">Last 7 months performance</p>
          </div>
          <TrendingUp className="text-green-500" size={32} />
        </div>
        
        <div className="space-y-4">
          {analyticsData.monthlyFilings.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-4"
            >
              <div className="w-12 text-sm font-semibold text-gray-700">{item.month}</div>
              <div className="flex-1 bg-gray-200 rounded-full h-8 relative overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(item.count / maxFilings) * 100}%` }}
                  transition={{ delay: index * 0.1 + 0.3, duration: 0.5 }}
                  className="bg-gradient-to-r from-primary to-primary-light h-full rounded-full flex items-center justify-end pr-3"
                >
                  <span className="text-white font-semibold text-sm">{item.count}</span>
                </motion.div>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Requests by Type */}
        <Card>
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Requests by Type</h2>
          <div className="space-y-4">
            {analyticsData.requestsByType.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between"
              >
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">{item.type}</span>
                    <span className="text-sm font-bold text-gray-800">{item.count}</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(item.count / maxRequests) * 100}%` }}
                      transition={{ delay: index * 0.1 + 0.3, duration: 0.5 }}
                      className="bg-primary h-full rounded-full"
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </Card>

        {/* Status Distribution */}
        <Card>
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Status Distribution</h2>
          <div className="space-y-4">
            {analyticsData.statusDistribution.map((item, index) => {
              const colors = {
                'Completed': 'bg-green-500',
                'In Progress': 'bg-blue-500',
                'Pending': 'bg-orange-500',
                'Rejected': 'bg-red-500',
              };
              const total = analyticsData.statusDistribution.reduce((sum, s) => sum + s.count, 0);
              const percentage = ((item.count / total) * 100).toFixed(1);

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg"
                >
                  <div className={`w-12 h-12 rounded-full ${colors[item.status as keyof typeof colors]} flex items-center justify-center text-white font-bold`}>
                    {percentage}%
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-800">{item.status}</p>
                    <p className="text-sm text-gray-600">{item.count} requests</p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </Card>
      </div>
    </div>
  );
};
