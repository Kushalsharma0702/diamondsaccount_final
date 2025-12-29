import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { StatCard } from '@/components/ui/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import { apiService } from '@/services/api';
import { Users, FileText, CreditCard, CheckCircle, DollarSign, UserCog, Loader2, Plus } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { StatusBadge } from '@/components/ui/status-badge';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { Client } from '@/types';
import { useToast } from '@/hooks/use-toast';

const COLORS = ['hsl(200, 98%, 39%)', 'hsl(213, 93%, 67%)', 'hsl(215, 20%, 65%)', 'hsl(215, 16%, 46%)', 'hsl(120, 40%, 50%)'];

export default function Dashboard() {
  const { user, isSuperAdmin } = useAuth();
  const { formatAmount } = useCurrency();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [analytics, setAnalytics] = useState<any>(null);
  const [recentClients, setRecentClients] = useState<Client[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch analytics and clients in parallel
      const [analyticsData, clientsData] = await Promise.all([
        apiService.getAnalytics(),
        apiService.getClients({ page: 1, page_size: 5 })
      ]);

      setAnalytics(analyticsData);
      setRecentClients(clientsData.clients || []);
    } catch (error: any) {
      console.error('Failed to load dashboard data:', error);
      toast({
        title: 'Error loading dashboard',
        description: error.message || 'Failed to load dashboard data',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout
        title="Dashboard"
        breadcrumbs={[{ label: 'Dashboard' }]}
      >
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  if (!analytics) {
    return (
      <DashboardLayout
        title="Dashboard"
        breadcrumbs={[{ label: 'Dashboard' }]}
      >
        <div className="text-center py-12">
          <p className="text-muted-foreground">Failed to load dashboard data</p>
          <Button onClick={loadDashboardData} className="mt-4">Retry</Button>
        </div>
      </DashboardLayout>
    );
  }

  const hasNoData = (analytics.total_clients || 0) === 0 && 
                    (analytics.total_revenue || 0) === 0 && 
                    (analytics.total_admins || 0) === 0;

  return (
    <DashboardLayout
      title={`Welcome back, ${user?.name?.split(' ')[0] || 'Admin'}`}
      breadcrumbs={[{ label: 'Dashboard' }]}
    >
      {hasNoData ? (
        <div className="flex flex-col items-center justify-center py-16 space-y-4">
          <div className="text-center space-y-2">
            <h3 className="text-xl font-semibold">Welcome to Tax Hub Dashboard</h3>
            <p className="text-muted-foreground">Get started by adding your first client</p>
          </div>
          <Button onClick={() => navigate('/clients')} size="lg">
            <Plus className="h-4 w-4 mr-2" />
            Add Your First Client
          </Button>
        </div>
      ) : (
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total Clients"
            value={analytics.total_clients || 0}
            icon={Users}
          />
          <StatCard
            title="Pending Documents"
            value={analytics.pending_documents || 0}
            icon={FileText}
          />
          <StatCard
            title="Pending Payments"
            value={analytics.pending_payments || 0}
            icon={CreditCard}
          />
          <StatCard
            title="Completed Filings"
            value={analytics.completed_filings || 0}
            icon={CheckCircle}
          />
        </div>

        {isSuperAdmin() && (
          <div className="grid gap-4 md:grid-cols-2">
            <StatCard
              title="Total Revenue"
              value={formatAmount(analytics.total_revenue || 0)}
              icon={DollarSign}
            />
            <StatCard
              title="Total Admins"
              value={analytics.total_admins || 0}
              icon={UserCog}
            />
          </div>
        )}

        {/* Charts Row */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Revenue Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Monthly Revenue</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analytics.monthly_revenue || []}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="month" className="text-xs" />
                    <YAxis className="text-xs" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                    />
                    <Bar dataKey="revenue" fill="hsl(200, 98%, 39%)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Status Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Clients by Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={analytics.clients_by_status || []}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="count"
                      nameKey="status"
                      label={({ status, count }) => `${status}: ${count}`}
                      labelLine={false}
                    >
                      {(analytics.clients_by_status || []).map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Admin Workload & Recent Clients */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Admin Workload */}
          {isSuperAdmin() && analytics.admin_workload && analytics.admin_workload.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Admin Workload</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics.admin_workload.map((admin: any, i: number) => (
                    <div key={i} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{admin.name}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full"
                            style={{ width: `${Math.min(100, (admin.clients / 10) * 100)}%` }}
                          />
                        </div>
                        <span className="text-sm text-muted-foreground w-16">{admin.clients} clients</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Clients */}
          <Card className={isSuperAdmin() && analytics.admin_workload?.length > 0 ? '' : 'lg:col-span-2'}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg">Recent Clients</CardTitle>
              <Button variant="outline" size="sm" onClick={() => navigate('/clients')}>
                View All
              </Button>
            </CardHeader>
            <CardContent>
              {recentClients.length > 0 ? (
                <div className="space-y-3">
                  {recentClients.map((client) => (
                    <div
                      key={client.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors"
                      onClick={() => navigate(`/clients/${client.id}`)}
                    >
                      <div>
                        <p className="font-medium text-sm">{client.name}</p>
                        <p className="text-xs text-muted-foreground">{client.email}</p>
                      </div>
                      <StatusBadge status={client.status} type="client" />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">No clients yet</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
      )}
    </DashboardLayout>
  );
}
