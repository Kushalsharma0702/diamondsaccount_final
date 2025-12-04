import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { Card } from '../../common/Card';
import { clientRequests } from '../../../data/dummyData';
import { STATUS_COLORS, PRIORITY_COLORS } from '../../../utils/constants';

export const ClientRequests: React.FC = () => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return Clock;
      case 'in-progress':
        return AlertCircle;
      case 'completed':
        return CheckCircle2;
      case 'rejected':
        return XCircle;
      default:
        return Clock;
    }
  };

  return (
    <Card className="col-span-1 lg:col-span-2">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Client Requests</h2>
        <span className="text-sm text-gray-500">Last updated: Just now</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Client</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Request Type</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Priority</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Due Date</th>
            </tr>
          </thead>
          <tbody>
            {clientRequests.map((request, index) => {
              const StatusIcon = getStatusIcon(request.status);
              return (
                <motion.tr
                  key={request.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  <td className="py-4 px-4">
                    <div className="flex items-center">
                      <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-semibold mr-3">
                        {request.clientName.charAt(0)}
                      </div>
                      <span className="font-medium text-gray-800">{request.clientName}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-gray-700">{request.requestType}</td>
                  <td className="py-4 px-4">
                    <span
                      className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold text-white"
                      style={{ backgroundColor: STATUS_COLORS[request.status] }}
                    >
                      <StatusIcon size={14} />
                      {request.status.replace('-', ' ')}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <span
                      className="inline-block px-3 py-1 rounded-full text-xs font-semibold text-white"
                      style={{ backgroundColor: PRIORITY_COLORS[request.priority] }}
                    >
                      {request.priority}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-gray-700">{request.dueDate}</td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
