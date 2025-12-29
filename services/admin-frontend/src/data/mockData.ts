/**
 * @deprecated This file contains mock data that was used during development.
 * All pages now use real data from the backend API.
 * 
 * This file is kept for reference only. Do not import from this file in new code.
 * Use the API service (@/services/api) instead.
 */

import { Client, Document, Payment, Note, AuditLog, User } from '@/types';

// All mock data has been removed - use real API data instead
export const mockClients: Client[] = [];
export const mockDocuments: Document[] = [];
export const mockPayments: Payment[] = [];
export const mockNotes: Note[] = [];
export const mockAdmins: User[] = [];
export const mockAuditLogs: AuditLog[] = [];

export const getAnalyticsData = () => ({
  totalClients: 0,
  totalAdmins: 0,
  pendingDocuments: 0,
  pendingPayments: 0,
  completedFilings: 0,
  totalRevenue: 0,
  monthlyRevenue: [],
  clientsByStatus: [],
  adminWorkload: [],
});
