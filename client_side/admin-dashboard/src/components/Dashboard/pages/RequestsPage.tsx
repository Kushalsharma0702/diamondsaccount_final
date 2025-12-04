import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, FileText, Calendar, User, AlertCircle, CheckCircle2, Clock, XCircle } from 'lucide-react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { clientRequests } from '../../../data/dummyData';
import { STATUS_COLORS, PRIORITY_COLORS } from '../../../utils/constants';
import type { ClientRequest } from '../../../types';

export const RequestsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'pending' | 'in-progress' | 'completed' | 'rejected'>('all');
  const [selectedRequest, setSelectedRequest] = useState<ClientRequest | null>(null);

  const filteredRequests = clientRequests.filter((request) => {
    const matchesSearch = request.clientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.requestType.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || request.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return Clock;
      case 'in-progress': return AlertCircle;
      case 'completed': return CheckCircle2;
      case 'rejected': return XCircle;
      default: return Clock;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Client Requests</h1>
          <p className="text-gray-600">Manage and track all client filing requests</p>
        </div>
      </div>

      <Card>
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by client name or request type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="in-progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="rejected">Rejected</option>
          </select>
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
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRequests.map((request, index) => {
                const StatusIcon = getStatusIcon(request.status);
                return (
                  <motion.tr
                    key={request.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => setSelectedRequest(request)}
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
                    <td className="py-4 px-4">
                      <Button size="sm" variant="outline">View</Button>
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredRequests.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No requests found</p>
          </div>
        )}
      </Card>

      {/* Request Details Modal */}
      {selectedRequest && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedRequest(null)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-white rounded-xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Request Details</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center font-bold">
                    {selectedRequest.clientName.charAt(0)}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold">{selectedRequest.clientName}</h3>
                    <p className="text-gray-600">{selectedRequest.requestType}</p>
                  </div>
                </div>
                <span
                  className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-semibold text-white"
                  style={{ backgroundColor: STATUS_COLORS[selectedRequest.status] }}
                >
                  {React.createElement(getStatusIcon(selectedRequest.status), { size: 16 })}
                  {selectedRequest.status.replace('-', ' ')}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-sm text-gray-600 flex items-center gap-2">
                    <Calendar size={16} />
                    Submitted
                  </p>
                  <p className="font-medium">{selectedRequest.dateSubmitted}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 flex items-center gap-2">
                    <Clock size={16} />
                    Due Date
                  </p>
                  <p className="font-medium">{selectedRequest.dueDate}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Priority</p>
                  <span
                    className="inline-block px-3 py-1 rounded-full text-xs font-semibold text-white"
                    style={{ backgroundColor: PRIORITY_COLORS[selectedRequest.priority] }}
                  >
                    {selectedRequest.priority}
                  </span>
                </div>
                {selectedRequest.assignedTo && (
                  <div>
                    <p className="text-sm text-gray-600 flex items-center gap-2">
                      <User size={16} />
                      Assigned To
                    </p>
                    <p className="font-medium">{selectedRequest.assignedTo}</p>
                  </div>
                )}
                <div>
                  <p className="text-sm text-gray-600 flex items-center gap-2">
                    <FileText size={16} />
                    Documents
                  </p>
                  <p className="font-medium">{selectedRequest.documents || 0} files</p>
                </div>
              </div>

              {selectedRequest.description && (
                <div className="pt-4 border-t">
                  <p className="text-sm text-gray-600 mb-2">Description</p>
                  <p className="text-gray-800">{selectedRequest.description}</p>
                </div>
              )}

              <div className="flex gap-4 pt-6">
                <Button variant="primary" className="flex-1">Update Status</Button>
                <Button variant="outline" className="flex-1" onClick={() => setSelectedRequest(null)}>Close</Button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};
