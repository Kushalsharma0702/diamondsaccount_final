export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'client';
}

export interface Client {
  id: string;
  name: string;
  email: string;
  phone: string;
  company?: string;
  type: 'individual' | 'business';
  status: 'active' | 'inactive' | 'pending';
  joinedDate: string;
  totalFilings: number;
  pendingTasks: number;
}

export interface ClientRequest {
  id: string;
  clientName: string;
  clientId: string;
  requestType: string;
  status: 'pending' | 'in-progress' | 'completed' | 'rejected';
  priority: 'low' | 'medium' | 'high';
  dateSubmitted: string;
  dueDate: string;
  assignedTo?: string;
  description?: string;
  documents?: number;
}

export interface DataSubmission {
  id: string;
  clientName: string;
  clientId: string;
  documentType: string;
  status: 'submitted' | 'under-review' | 'approved' | 'rejected';
  submittedDate: string;
  reviewedBy?: string;
  fileSize: string;
  fileName: string;
  notes?: string;
}

export interface StatusOverview {
  totalClients: number;
  activeFilings: number;
  pendingReviews: number;
  completedToday: number;
}

export interface AnalyticsData {
  monthlyFilings: { month: string; count: number }[];
  requestsByType: { type: string; count: number }[];
  statusDistribution: { status: string; count: number }[];
}

export type AppView = 'intro' | 'guide' | 'login' | 'dashboard';
export type DashboardView = 'overview' | 'clients' | 'requests' | 'submissions' | 'analytics' | 'settings';
