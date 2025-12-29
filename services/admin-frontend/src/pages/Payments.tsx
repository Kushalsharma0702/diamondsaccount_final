import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { DataTable } from '@/components/ui/data-table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { PERMISSIONS } from '@/types';
import { Plus, Loader2, Edit, Trash2, DollarSign } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/services/api';
import { Client } from '@/types';

interface PaymentWithClient {
  id: string;
  clientId?: string;
  client_id?: string;
  clientName?: string;
  client_name?: string;
  amount: number;
  method: string;
  note?: string;
  created_at?: string;
  createdAt?: Date | string;
  created_by?: string;
  created_by_name?: string;
  createdBy?: string;
}

export default function Payments() {
  const { hasPermission } = useAuth();
  const { currency, setCurrency, formatAmount } = useCurrency();
  const { toast } = useToast();
  const [payments, setPayments] = useState<PaymentWithClient[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingPayments, setIsLoadingPayments] = useState(true);
  const [selectedPayment, setSelectedPayment] = useState<PaymentWithClient | null>(null);
  const [newPayment, setNewPayment] = useState({
    clientId: '',
    amount: '',
    method: 'etransfer',
    note: '',
  });
  const [editPayment, setEditPayment] = useState({
    amount: '',
    method: 'etransfer',
    note: '',
  });

  useEffect(() => {
    loadPayments();
    loadClients();
  }, []);

  const loadPayments = async () => {
    try {
      setIsLoadingPayments(true);
      const response = await apiService.getPayments();
      
      // Map payments with proper field names - handle all possible field variations
      const paymentsWithClients = (response.payments || []).map((payment: any) => {
        // Safely handle date fields
        let createdAt: string | Date | undefined = payment.created_at || payment.createdAt;
        if (createdAt && typeof createdAt === 'string') {
          try {
            const date = new Date(createdAt);
            if (isNaN(date.getTime())) {
              createdAt = undefined;
            } else {
              createdAt = date.toISOString();
            }
          } catch {
            createdAt = undefined;
          }
        }
        
        return {
          id: payment.id || '',
          clientId: payment.client_id || payment.clientId || '',
          client_id: payment.client_id || '',
          clientName: payment.client_name || payment.clientName || 'Unknown',
          client_name: payment.client_name || '',
          amount: parseFloat(payment.amount) || 0,
          method: payment.method || '',
          note: payment.note || '',
          createdAt: createdAt,
          created_at: payment.created_at || createdAt,
          createdBy: payment.created_by_name || payment.createdBy || payment.created_by || '',
          created_by_name: payment.created_by_name || '',
        };
      });
      
      setPayments(paymentsWithClients);
    } catch (error: any) {
      console.error('Failed to load payments:', error);
      toast({
        title: 'Error',
        description: 'Failed to load payments',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingPayments(false);
    }
  };

  const loadClients = async () => {
    try {
      const response = await apiService.getClients({ page: 1, page_size: 100 });
      setClients(response.clients || []);
    } catch (error) {
      console.error('Failed to load clients:', error);
    }
  };

  const handleAddPayment = async () => {
    if (!newPayment.clientId || !newPayment.amount) {
      toast({
        title: 'Validation Error',
        description: 'Please select a client and enter an amount.',
        variant: 'destructive',
      });
      return;
    }

    const amount = parseFloat(newPayment.amount);
    if (isNaN(amount) || amount <= 0) {
      toast({
        title: 'Validation Error',
        description: 'Please enter a valid amount greater than 0.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    try {
      await apiService.createPayment({
        client_id: newPayment.clientId,
        amount: amount,
        method: newPayment.method === 'etransfer' ? 'E-Transfer' : 
                newPayment.method === 'credit' ? 'Credit Card' : 
                newPayment.method === 'debit' ? 'Debit' : 
                newPayment.method === 'cash' ? 'Cash' : 'Check',
        note: newPayment.note || undefined,
      });

      toast({
        title: 'Payment Recorded',
        description: `${formatAmount(amount)} payment has been added. This amount is visible to the client.`,
      });
      
      setNewPayment({ clientId: '', amount: '', method: 'etransfer', note: '' });
      setIsAddOpen(false);
      await loadPayments();
      await loadClients();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to add payment',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditPayment = (payment: PaymentWithClient) => {
    setSelectedPayment(payment);
    // Convert method back to lowercase for the form
    const methodValue = payment.method?.toLowerCase().replace(/\s+/g, '') || 'etransfer';
    setEditPayment({
      amount: payment.amount?.toString() || '',
      method: methodValue.includes('transfer') ? 'etransfer' : 
              methodValue.includes('credit') ? 'credit' : 
              methodValue.includes('debit') ? 'debit' : 
              methodValue.includes('cash') ? 'cash' : 'check',
      note: payment.note || '',
    });
    setIsEditOpen(true);
  };

  const handleUpdatePayment = async () => {
    if (!selectedPayment || !editPayment.amount) {
      toast({
        title: 'Validation Error',
        description: 'Please enter an amount.',
        variant: 'destructive',
      });
      return;
    }

    const amount = parseFloat(editPayment.amount);
    if (isNaN(amount) || amount <= 0) {
      toast({
        title: 'Validation Error',
        description: 'Please enter a valid amount greater than 0.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    try {
      await apiService.updatePayment(selectedPayment.id, {
        amount: amount,
        method: editPayment.method === 'etransfer' ? 'E-Transfer' : 
                editPayment.method === 'credit' ? 'Credit Card' : 
                editPayment.method === 'debit' ? 'Debit' : 
                editPayment.method === 'cash' ? 'Cash' : 'Check',
        note: editPayment.note || undefined,
      });

      toast({
        title: 'Payment Updated',
        description: 'Payment has been updated successfully.',
      });
      
      setIsEditOpen(false);
      setSelectedPayment(null);
      await loadPayments();
      await loadClients();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to update payment',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeletePayment = async () => {
    if (!selectedPayment) return;

    setIsLoading(true);
    try {
      await apiService.deletePayment(selectedPayment.id);

      toast({
        title: 'Payment Deleted',
        description: 'Payment has been removed successfully.',
      });
      
      setIsDeleteOpen(false);
      setSelectedPayment(null);
      await loadPayments();
      await loadClients();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete payment',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const columns = [
    {
      key: 'clientName',
      header: 'Client',
      sortable: true,
      render: (payment: PaymentWithClient) => payment.clientName || payment.client_name || '-',
    },
    {
      key: 'amount',
      header: 'Amount',
      sortable: true,
      render: (payment: PaymentWithClient) => (
        <span className="font-medium">{formatAmount(payment.amount || 0)}</span>
      ),
    },
    {
      key: 'method',
      header: 'Method',
      render: (payment: PaymentWithClient) => payment.method || '-',
    },
    {
      key: 'note',
      header: 'Note',
      render: (payment: PaymentWithClient) => payment.note || '-',
    },
    {
      key: 'createdAt',
      header: 'Date',
      sortable: true,
      render: (payment: PaymentWithClient) => {
        const dateStr = payment.created_at || payment.createdAt;
        if (!dateStr) return '-';
        
        try {
          const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr;
          if (date instanceof Date && !isNaN(date.getTime())) {
            return date.toLocaleDateString();
          }
          return '-';
        } catch {
          return '-';
        }
      },
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (payment: PaymentWithClient) => (
        hasPermission(PERMISSIONS.ADD_EDIT_PAYMENT) ? (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleEditPayment(payment)}
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSelectedPayment(payment);
                setIsDeleteOpen(true);
              }}
              className="text-destructive hover:text-destructive"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ) : null
      ),
    },
  ];

  if (isLoadingPayments) {
    return (
      <DashboardLayout
        title="Payment Management"
        breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Payments' }]}
      >
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      title="Payment Management"
      breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Payments' }]}
    >
      <div className="space-y-6">
        {/* Currency Selector */}
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold">Payment History</h2>
          <div className="flex gap-2">
            <Select
              value={currency}
              onValueChange={(value) => setCurrency(value as '$' | '₹')}
            >
              <SelectTrigger className="w-[150px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="$">
                  <div className="flex items-center gap-2">
                    <DollarSign className="h-4 w-4" />
                    <span>Dollar ($)</span>
                  </div>
                </SelectItem>
                <SelectItem value="₹">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">₹</span>
                    <span>Rupees (₹)</span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
            {hasPermission(PERMISSIONS.ADD_EDIT_PAYMENT) && (
              <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Payment
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Record Payment</DialogTitle>
                    <DialogDescription>
                      Add a new payment record for a client. The amount will be visible to them.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label>Client *</Label>
                      <Select
                        value={newPayment.clientId}
                        onValueChange={(v) => setNewPayment({ ...newPayment, clientId: v })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select client" />
                        </SelectTrigger>
                        <SelectContent>
                          {clients.map((client) => (
                            <SelectItem key={client.id} value={client.id}>
                              {client.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Payment Amount *</Label>
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        placeholder="0.00"
                        value={newPayment.amount}
                        onChange={(e) => setNewPayment({ ...newPayment, amount: e.target.value })}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        This amount will be added to the client's paid amount and will be visible to them.
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Payment Method</Label>
                      <Select
                        value={newPayment.method}
                        onValueChange={(v) => setNewPayment({ ...newPayment, method: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="etransfer">E-Transfer</SelectItem>
                          <SelectItem value="credit">Credit Card</SelectItem>
                          <SelectItem value="debit">Debit</SelectItem>
                          <SelectItem value="cash">Cash</SelectItem>
                          <SelectItem value="check">Check</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Note (Optional)</Label>
                      <Input
                        placeholder="Payment note (visible to client)..."
                        value={newPayment.note}
                        onChange={(e) => setNewPayment({ ...newPayment, note: e.target.value })}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        Optional note about this payment. This will be visible to the client.
                      </p>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setIsAddOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleAddPayment} disabled={isLoading}>
                      {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                      Record Payment
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </div>

        {/* Payment Table */}
        <Card>
          <CardContent className="p-0">
            <DataTable
              data={payments}
              columns={columns}
              searchKey="clientName"
              searchPlaceholder="Search by client name..."
            />
          </CardContent>
        </Card>

        {/* Edit Payment Dialog */}
        <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Payment</DialogTitle>
              <DialogDescription>
                Update payment information. Changes will be visible to the client.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Payment Amount *</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  value={editPayment.amount}
                  onChange={(e) => setEditPayment({ ...editPayment, amount: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Payment Method</Label>
                <Select
                  value={editPayment.method}
                  onValueChange={(v) => setEditPayment({ ...editPayment, method: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="etransfer">E-Transfer</SelectItem>
                    <SelectItem value="credit">Credit Card</SelectItem>
                    <SelectItem value="debit">Debit</SelectItem>
                    <SelectItem value="cash">Cash</SelectItem>
                    <SelectItem value="check">Check</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Note (Optional)</Label>
                <Input
                  placeholder="Payment note (visible to client)..."
                  value={editPayment.note}
                  onChange={(e) => setEditPayment({ ...editPayment, note: e.target.value })}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  This note will be visible to the client.
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsEditOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleUpdatePayment} disabled={isLoading}>
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Update Payment
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Payment</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete this payment of {selectedPayment ? formatAmount(selectedPayment.amount) : ''}? 
                This will update the client's paid amount. This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDeletePayment}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                disabled={isLoading}
              >
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </DashboardLayout>
  );
}
