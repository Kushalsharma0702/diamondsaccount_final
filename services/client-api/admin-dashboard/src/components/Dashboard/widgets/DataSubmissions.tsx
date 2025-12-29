import React from 'react';
import { motion } from 'framer-motion';
import { FileText, CheckCircle2, Clock, XCircle } from 'lucide-react';
import { Card } from '../../common/Card';
import { dataSubmissions } from '../../../data/dummyData';
import { STATUS_COLORS } from '../../../utils/constants';

export const DataSubmissions: React.FC = () => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'submitted':
        return Clock;
      case 'under-review':
        return FileText;
      case 'approved':
        return CheckCircle2;
      case 'rejected':
        return XCircle;
      default:
        return FileText;
    }
  };

  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Recent Data Submissions</h2>
      </div>

      <div className="space-y-4">
        {dataSubmissions.map((submission, index) => {
          const StatusIcon = getStatusIcon(submission.status);
          return (
            <motion.div
              key={submission.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center flex-1">
                <div className="w-12 h-12 rounded-lg bg-primary text-white flex items-center justify-center mr-4">
                  <FileText size={24} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800">{submission.clientName}</h3>
                  <p className="text-sm text-gray-600">{submission.documentType}</p>
                  <p className="text-xs text-gray-500 mt-1">{submission.submittedDate}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">{submission.fileSize}</span>
                <span
                  className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold text-white"
                  style={{ backgroundColor: STATUS_COLORS[submission.status] }}
                >
                  <StatusIcon size={14} />
                  {submission.status.replace('-', ' ')}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </Card>
  );
};
