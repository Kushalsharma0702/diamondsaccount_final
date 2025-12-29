/**
 * API service for connecting to the backend
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002/api/v1';

interface RequestOptions extends RequestInit {
  skipAuth?: boolean;
}

class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any
  ) {
    super(data?.detail || statusText);
    this.name = 'ApiError';
  }
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const { skipAuth, ...fetchOptions } = options;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    };

    if (!skipAuth) {
      const token = localStorage.getItem('taxease_access_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
      });

      // Log for debugging
      if (process.env.NODE_ENV === 'development') {
        console.log(`API ${options.method || 'GET'} ${url}`, {
          status: response.status,
          ok: response.ok
        });
      }

      if (!response.ok) {
        let errorData: any = {};
        try {
          errorData = await response.json();
        } catch {
          errorData = { detail: response.statusText || 'Unknown error' };
        }
        
        // Log error for debugging
        console.error('API Error:', {
          url,
          status: response.status,
          error: errorData
        });
        
        throw new ApiError(
          response.status,
          response.statusText,
          errorData
        );
      }

      // Handle empty responses
      if (response.status === 204) {
        return undefined as T;
      }

      return response.json();
    } catch (error) {
      // Re-throw ApiError as-is
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Handle network errors
      console.error('Network error:', error);
      throw new ApiError(
        0,
        'Network error',
        { detail: error instanceof Error ? error.message : 'Failed to connect to server' }
      );
    }
  }

  // Authentication
  async login(email: string, password: string) {
    const response = await this.request<{
      user: any;
      token: {
        access_token: string;
        refresh_token: string;
        token_type: string;
        expires_in: number;
      };
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      skipAuth: true,
    });

    // Store tokens
    if (response.token?.access_token) {
      localStorage.setItem('taxease_access_token', response.token.access_token);
      localStorage.setItem('taxease_refresh_token', response.token.refresh_token);
    }

    return response;
  }

  async getCurrentUser() {
    return this.request<any>('/auth/me');
  }

  logout() {
    localStorage.removeItem('taxease_access_token');
    localStorage.removeItem('taxease_refresh_token');
    localStorage.removeItem('taxease_user');
  }

  // Clients
  async getClients(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    year?: number;
    search?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.year) queryParams.append('year', params.year.toString());
    if (params?.search) queryParams.append('search', params.search);

    const query = queryParams.toString();
    return this.request<{
      clients: any[];
      total: number;
      page: number;
      page_size: number;
      total_pages: number;
    }>(`/clients${query ? `?${query}` : ''}`);
  }

  async getClient(id: string) {
    return this.request<any>(`/clients/${id}`);
  }

  async createClient(data: {
    name: string;
    email: string;
    phone?: string;
    filing_year: number;
    assigned_admin_id?: string;
  }) {
    return this.request<any>('/clients', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateClient(id: string, data: Partial<{
    name: string;
    email: string;
    phone: string;
    filing_year: number;
    status: string;
    payment_status: string;
    assigned_admin_id: string;
    total_amount: number;
    paid_amount: number;
  }>) {
    return this.request<any>(`/clients/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteClient(id: string) {
    return this.request<void>(`/clients/${id}`, {
      method: 'DELETE',
    });
  }

  // Admin Users
  async getAdminUsers() {
    return this.request<any[]>('/admin-users');
  }

  async getAdminUser(id: string) {
    return this.request<any>(`/admin-users/${id}`);
  }

  async createAdminUser(data: {
    name: string;
    email: string;
    password: string;
    role: 'admin' | 'superadmin';
    permissions: string[];
  }) {
    return this.request<any>('/admin-users', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAdminUser(id: string, data: Partial<{
    name: string;
    email: string;
    role: string;
    permissions: string[];
    is_active: boolean;
  }>) {
    return this.request<any>(`/admin-users/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteAdminUser(id: string) {
    return this.request<void>(`/admin-users/${id}`, {
      method: 'DELETE',
    });
  }

  // Documents
  async getDocuments(params?: {
    status?: string;
    search?: string;
    client_id?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.search) queryParams.append('search', params.search);
    if (params?.client_id) queryParams.append('client_id', params.client_id);

    const query = queryParams.toString();
    return this.request<{
      documents: any[];
      total: number;
    }>(`/documents${query ? `?${query}` : ''}`);
  }

  async createDocument(data: {
    client_id: string;
    name: string;
    type: string;
    status?: string;
    notes?: string;
  }) {
    return this.request<any>('/documents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteDocument(id: string) {
    return this.request<void>(`/documents/${id}`, {
      method: 'DELETE',
    });
  }

  // Payments
  async getPayments(params?: { client_id?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.client_id) queryParams.append('client_id', params.client_id);

    const query = queryParams.toString();
    return this.request<{
      payments: any[];
      total: number;
      total_revenue: number;
      avg_payment: number;
    }>(`/payments${query ? `?${query}` : ''}`);
  }

  async updatePayment(id: string, data: {
    amount?: number;
    method?: string;
    note?: string;
  }) {
    return this.request<any>(`/payments/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deletePayment(id: string) {
    return this.request<void>(`/payments/${id}`, {
      method: 'DELETE',
    });
  }

  async createPayment(data: {
    client_id: string;
    amount: number;
    method: string;
    note?: string;
  }) {
    return this.request<any>('/payments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Analytics
  async getAnalytics() {
    return this.request<{
      total_clients: number;
      total_admins: number;
      pending_documents: number;
      pending_payments: number;
      completed_filings: number;
      total_revenue: number;
      monthly_revenue: Array<{ month: string; revenue: number }>;
      clients_by_status: Array<{ status: string; count: number }>;
      admin_workload: Array<{ name: string; clients: number }>;
    }>('/analytics');
  }

  // Audit Logs
  async getAuditLogs(params?: {
    page?: number;
    page_size?: number;
    entity_type?: string;
    action?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.entity_type) queryParams.append('entity_type', params.entity_type);
    if (params?.action) queryParams.append('action', params.action);

    const query = queryParams.toString();
    return this.request<{
      logs: any[];
      total: number;
      page: number;
      page_size: number;
      total_pages: number;
    }>(`/audit-logs${query ? `?${query}` : ''}`);
  }

  // T1 Forms
  async getT1Forms(params?: {
    client_id?: string;
    client_email?: string;
    status_filter?: string;
    limit?: number;
    offset?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.client_id) queryParams.append('client_id', params.client_id);
    if (params?.client_email) queryParams.append('client_email', params.client_email);
    if (params?.status_filter) queryParams.append('status_filter', params.status_filter);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const query = queryParams.toString();
    return this.request<{
      forms: Array<{
        id: string;
        user_id?: string;
        tax_year: number;
        status: string;
        first_name?: string;
        last_name?: string;
        client_email?: string;
        created_at?: string;
        updated_at?: string;
        submitted_at?: string;
      }>;
      total: number;
      offset: number;
      limit: number;
    }>(`/t1-forms${query ? `?${query}` : ''}`);
  }

  // Files/Uploaded Documents
  async getFiles(params?: {
    client_id?: string;
    client_email?: string;
    status_filter?: string;
    limit?: number;
    offset?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.client_id) queryParams.append('client_id', params.client_id);
    if (params?.client_email) queryParams.append('client_email', params.client_email);
    if (params?.status_filter) queryParams.append('status_filter', params.status_filter);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const query = queryParams.toString();
    return this.request<{
      files: Array<{
        id: string;
        user_id?: string;
        filename: string;
        original_filename: string;
        file_type: string;
        file_size: number;
        upload_status: string;
        created_at?: string;
        client_email?: string;
      }>;
      total: number;
      offset: number;
      limit: number;
    }>(`/files${query ? `?${query}` : ''}`);
  }
}

export const apiService = new ApiService();
export { ApiError };

