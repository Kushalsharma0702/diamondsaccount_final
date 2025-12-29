import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StatCard } from '@/components/ui/stat-card';
import { apiService } from '@/services/api';
import { Users, FileText, DollarSign, CheckCircle, TrendingUp, Loader2 } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from 'recharts';

const COLORS = ['hsl(200, 98%, 39%)', 'hsl(213, 93%, 67%)', 'hsl(120, 40%, 50%)', 'hsl(40, 90%, 50%)', 'hsl(0, 70%, 50%)'];

export default function Analytics() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setIsLoading(true);
      const data = await apiService.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout
        title="Analytics & Reports"
        breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Analytics' }]}
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
        title="Analytics & Reports"
        breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Analytics' }]}
      >
        <div className="text-center py-12">
          <p className="text-muted-foreground">Failed to load analytics data</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      title="Analytics & Reports"
      breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Analytics' }]}
    >
      <div className="space-y-6">
        {/* Overview Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total Clients"
            value={analytics.total_clients || 0}
            icon={Users}
          />
          <StatCard
            title="Total Revenue"
            value={`$${((analytics.total_revenue || 0) / 1000).toFixed(1)}K`}
            icon={DollarSign}
          />
          <StatCard
            title="Completed Filings"
            value={analytics.completed_filings || 0}
            icon={CheckCircle}
          />
          <StatCard
            title="Documents Processed"
            value={analytics.total_documents || 0}
            icon={FileText}
          />
        </div>

        {/* Charts Row 1 */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Monthly Revenue */}
          {analytics.monthly_revenue && analytics.monthly_revenue.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Monthly Revenue</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={analytics.monthly_revenue}>
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
                      <Line
                        type="monotone"
                        dataKey="revenue"
                        stroke="hsl(200, 98%, 39%)"
                        strokeWidth={2}
                        dot={{ fill: 'hsl(200, 98%, 39%)' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Clients by Status */}
          {analytics.clients_by_status && analytics.clients_by_status.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Clients by Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={analytics.clients_by_status}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={2}
                        dataKey="count"
                        nameKey="status"
                      >
                        {analytics.clients_by_status.map((entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Admin Performance */}
        {analytics.admin_workload && analytics.admin_workload.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Admin Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analytics.admin_workload}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="name" className="text-xs" />
                    <YAxis className="text-xs" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                    />
                    <Bar dataKey="clients" fill="hsl(200, 98%, 39%)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}

        {(!analytics.monthly_revenue || analytics.monthly_revenue.length === 0) &&
         (!analytics.clients_by_status || analytics.clients_by_status.length === 0) &&
         (!analytics.admin_workload || analytics.admin_workload.length === 0) && (
          <Card>
            <CardContent className="p-12 text-center">
              <p className="text-muted-foreground">No analytics data available yet</p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
