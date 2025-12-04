import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, UserPlus, Mail, Phone, Building2, Calendar, FileText, Clock } from 'lucide-react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { clients } from '../../../data/dummyData';
import type { Client } from '../../../types';

export const ClientsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive' | 'pending'>('all');
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);

  const filteredClients = clients.filter((client) => {
    const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         client.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || client.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'inactive': return 'bg-gray-500';
      case 'pending': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Clients</h1>
          <p className="text-gray-600">Manage all your clients and their information</p>
        </div>
        <Button className="flex items-center gap-2">
          <UserPlus size={20} />
          Add New Client
        </Button>
      </div>

      <Card>
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search clients by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredClients.map((client, index) => (
            <motion.div
              key={client.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => setSelectedClient(client)}
              className="bg-gray-50 rounded-lg p-5 hover:bg-gray-100 transition-colors cursor-pointer border border-gray-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center font-bold text-lg">
                    {client.name.charAt(0)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">{client.name}</h3>
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold text-white ${getStatusColor(client.status)}`}>
                      {client.status}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <Mail size={16} />
                  <span className="truncate">{client.email}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone size={16} />
                  <span>{client.phone}</span>
                </div>
                {client.company && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Building2 size={16} />
                    <span>{client.company}</span>
                  </div>
                )}
                <div className="flex items-center gap-2 text-gray-600">
                  <Calendar size={16} />
                  <span>Joined: {client.joinedDate}</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 flex justify-between text-sm">
                <div className="flex items-center gap-1 text-gray-700">
                  <FileText size={16} />
                  <span>{client.totalFilings} filings</span>
                </div>
                <div className="flex items-center gap-1 text-orange-600 font-semibold">
                  <Clock size={16} />
                  <span>{client.pendingTasks} pending</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredClients.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No clients found</p>
          </div>
        )}
      </Card>

      {/* Client Details Modal */}
      {selectedClient && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedClient(null)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-white rounded-xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Client Details</h2>
            
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-primary text-white flex items-center justify-center font-bold text-2xl">
                  {selectedClient.name.charAt(0)}
                </div>
                <div>
                  <h3 className="text-xl font-semibold">{selectedClient.name}</h3>
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold text-white ${getStatusColor(selectedClient.status)}`}>
                    {selectedClient.status}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-medium">{selectedClient.email}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Phone</p>
                  <p className="font-medium">{selectedClient.phone}</p>
                </div>
                {selectedClient.company && (
                  <div>
                    <p className="text-sm text-gray-600">Company</p>
                    <p className="font-medium">{selectedClient.company}</p>
                  </div>
                )}
                <div>
                  <p className="text-sm text-gray-600">Type</p>
                  <p className="font-medium capitalize">{selectedClient.type}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Joined Date</p>
                  <p className="font-medium">{selectedClient.joinedDate}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Filings</p>
                  <p className="font-medium">{selectedClient.totalFilings}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Pending Tasks</p>
                  <p className="font-medium text-orange-600">{selectedClient.pendingTasks}</p>
                </div>
              </div>

              <div className="flex gap-4 pt-6">
                <Button variant="primary" className="flex-1">Edit Client</Button>
                <Button variant="outline" className="flex-1" onClick={() => setSelectedClient(null)}>Close</Button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};
