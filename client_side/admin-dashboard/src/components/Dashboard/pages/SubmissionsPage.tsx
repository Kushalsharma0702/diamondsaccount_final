import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, FileText, CheckCircle2, Clock, XCircle, Download, Eye } from 'lucide-react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { dataSubmissions } from '../../../data/dummyData';
import { STATUS_COLORS } from '../../../utils/constants';
import type { DataSubmission } from '../../../types';

export const SubmissionsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'submitted' | 'under-review' | 'approved' | 'rejected'>('all');
  const [selectedSubmission, setSelectedSubmission] = useState<DataSubmission | null>(null);

  const filteredSubmissions = dataSubmissions.filter((submission) => {
    const matchesSearch = submission.clientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         submission.documentType.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || submission.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'submitted': return Clock;
      case 'under-review': return FileText;
      case 'approved': return CheckCircle2;
      case 'rejected': return XCircle;
      default: return FileText;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Document Submissions</h1>
          <p className="text-gray-600">Review and manage client document submissions</p>
        </div>
      </div>

      <Card>
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by client or document type..."
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
            <option value="submitted">Submitted</option>
            <option value="under-review">Under Review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        <div className="space-y-4">
          {filteredSubmissions.map((submission, index) => {
            const StatusIcon = getStatusIcon(submission.status);
            return (
              <motion.div
                key={submission.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                onClick={() => setSelectedSubmission(submission)}
              >
                <div className="flex items-center flex-1 gap-4">
                  <div className="w-14 h-14 rounded-lg bg-primary text-white flex items-center justify-center">
                    <FileText size={28} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800">{submission.clientName}</h3>
                    <p className="text-sm text-gray-600">{submission.documentType}</p>
                    <p className="text-xs text-gray-500 mt-1">{submission.fileName}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="text-right hidden md:block">
                    <p className="text-sm text-gray-600">{submission.submittedDate}</p>
                    <p className="text-xs text-gray-500">{submission.fileSize}</p>
                  </div>
                  <span
                    className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold text-white whitespace-nowrap"
                    style={{ backgroundColor: STATUS_COLORS[submission.status] }}
                  >
                    <StatusIcon size={14} />
                    {submission.status.replace('-', ' ')}
                  </span>
                  <div className="flex gap-2">
                    <button className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
                      <Eye size={20} className="text-gray-600" />
                    </button>
                    <button className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
                      <Download size={20} className="text-gray-600" />
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {filteredSubmissions.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No submissions found</p>
          </div>
        )}
      </Card>

      {/* Submission Details Modal */}
      {selectedSubmission && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedSubmission(null)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-white rounded-xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Submission Details</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center font-bold">
                    {selectedSubmission.clientName.charAt(0)}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold">{selectedSubmission.clientName}</h3>
                    <p className="text-gray-600">{selectedSubmission.documentType}</p>
                  </div>
                </div>
                <span
                  className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-semibold text-white"
                  style={{ backgroundColor: STATUS_COLORS[selectedSubmission.status] }}
                >
                  {React.createElement(getStatusIcon(selectedSubmission.status), { size: 16 })}
                  {selectedSubmission.status.replace('-', ' ')}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-sm text-gray-600">File Name</p>
                  <p className="font-medium break-all">{selectedSubmission.fileName}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">File Size</p>
                  <p className="font-medium">{selectedSubmission.fileSize}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Submitted Date</p>
                  <p className="font-medium">{selectedSubmission.submittedDate}</p>
                </div>
                {selectedSubmission.reviewedBy && (
                  <div>
                    <p className="text-sm text-gray-600">Reviewed By</p>
                    <p className="font-medium">{selectedSubmission.reviewedBy}</p>
                  </div>
                )}
              </div>

              {selectedSubmission.notes && (
                <div className="pt-4 border-t">
                  <p className="text-sm text-gray-600 mb-2">Review Notes</p>
                  <p className="text-gray-800 bg-gray-50 p-3 rounded-lg">{selectedSubmission.notes}</p>
                </div>
              )}

              <div className="flex gap-4 pt-6">
                {selectedSubmission.status !== 'approved' && (
                  <Button variant="primary" className="flex-1">Approve</Button>
                )}
                {selectedSubmission.status !== 'rejected' && (
                  <Button variant="outline" className="flex-1">Reject</Button>
                )}
                <Button variant="ghost" onClick={() => setSelectedSubmission(null)}>Close</Button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};
