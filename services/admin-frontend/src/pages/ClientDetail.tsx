import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/ui/status-badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
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
import { STATUS_LABELS, ClientStatus, PERMISSIONS, Note, Document as DocType, Client } from '@/types';
import {
  User,
  Mail,
  Phone,
  Calendar,
  FileText,
  CreditCard,
  MessageSquare,
  Clock,
  Edit,
  ArrowLeft,
  Send,
  Trash2,
  Loader2,
  Plus,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/services/api';

export default function ClientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { hasPermission, user } = useAuth();
  const { formatAmount } = useCurrency();
  const { toast } = useToast();

  const [client, setClient] = useState<Client | null>(null);
  const [documents, setDocuments] = useState<DocType[]>([]);
  const [payments, setPayments] = useState<any[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const [newNote, setNewNote] = useState('');
  const [isClientFacing, setIsClientFacing] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isAddPaymentOpen, setIsAddPaymentOpen] = useState(false);
  const [isDeleteDocOpen, setIsDeleteDocOpen] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<DocType | null>(null);
  const [editForm, setEditForm] = useState({ name: '', email: '', phone: '' });
  const [paymentAmount, setPaymentAmount] = useState('');

  useEffect(() => {
    if (id) {
      loadClientData();
    }
  }, [id]);

  const loadClientData = async () => {
    if (!id) return;
    
    try {
      setIsLoading(true);
      
      const [clientData, docsData, paymentsData] = await Promise.all([
        apiService.getClient(id),
        apiService.getDocuments({ client_id: id }),
        apiService.getPayments({ client_id: id }),
      ]);

      setClient(clientData);
      setEditForm({
        name: clientData.name,
        email: clientData.email,
        phone: clientData.phone || '',
      });
      setDocuments(docsData.documents || []);
      setPayments(paymentsData.payments || []);
      // Notes would need a separate API endpoint - for now empty
      setNotes([]);
    } catch (error: any) {
      console.error('Failed to load client data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load client details',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateStatus = async (newStatus: ClientStatus) => {
    if (!client) return;

    setIsSaving(true);
    try {
      await apiService.updateClient(client.id, { status: newStatus });
      await loadClientData();
      toast({
        title: 'Status Updated',
        description: `Client status updated to ${STATUS_LABELS[newStatus]}`,
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to update status',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!client) return;

    setIsSaving(true);
    try {
      await apiService.updateClient(client.id, {
        name: editForm.name,
        email: editForm.email,
        phone: editForm.phone || undefined,
      });
      
      await loadClientData();
      setIsEditOpen(false);
      toast({
        title: 'Client Updated',
        description: 'Client information has been updated.',
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to update client',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddPayment = async () => {
    if (!client || !paymentAmount) return;

    setIsSaving(true);
    try {
      await apiService.createPayment({
        client_id: client.id,
        amount: parseFloat(paymentAmount),
        method: 'E-Transfer',
      });
      
      await loadClientData(); // Reload to get updated paid_amount
      setIsAddPaymentOpen(false);
      const amount = paymentAmount;
      setPaymentAmount('');
      
      toast({
        title: 'Payment Recorded',
        description: `${formatAmount(amount)} payment has been added and is now visible to ${client.name}. Their paid amount has been updated.`,
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to add payment',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteDocument = async () => {
    if (!selectedDoc) return;

    setIsSaving(true);
    try {
      await apiService.deleteDocument(selectedDoc.id);
      await loadClientData();
      setIsDeleteDocOpen(false);
      setSelectedDoc(null);
      toast({
        title: 'Document Deleted',
        description: 'Document has been removed.',
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete document',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout
        title="Client Details"
        breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Clients', href: '/clients' }, { label: 'Details' }]}
      >
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  if (!client) {
    return (
      <DashboardLayout
        title="Client Details"
        breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Clients', href: '/clients' }, { label: 'Details' }]}
      >
        <div className="text-center py-12">
          <p className="text-muted-foreground">Client not found</p>
          <Button onClick={() => navigate('/clients')} className="mt-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Clients
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      title={client.name}
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Clients', href: '/clients' },
        { label: client.name }
      ]}
    >
      <div className="space-y-6">
        {/* Back Button */}
        <Button variant="outline" onClick={() => navigate('/clients')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Clients
        </Button>

        {/* Client Info Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Client Information</CardTitle>
            <div className="flex gap-2">
              <StatusBadge status={client.status} type="client" />
              <StatusBadge status={client.paymentStatus} type="payment" />
              {hasPermission('add_edit_client') && (
                <Button variant="outline" size="sm" onClick={() => setIsEditOpen(true)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex items-center gap-3">
                <User className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Full Name</p>
                  <p className="font-medium">{client.name}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Mail className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{client.email}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Phone className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Phone</p>
                  <p className="font-medium">{client.phone || 'N/A'}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Filing Year</p>
                  <p className="font-medium">{client.filingYear}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <CreditCard className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Payment Status</p>
                  <p className="font-medium">
                    {formatAmount(client.paidAmount)} / {formatAmount(client.totalAmount)}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Status Update */}
        {hasPermission('update_workflow') && (
          <Card>
            <CardHeader>
              <CardTitle>Update Status</CardTitle>
            </CardHeader>
            <CardContent>
              <Select
                value={client.status}
                onValueChange={(value) => handleUpdateStatus(value as ClientStatus)}
                disabled={isSaving}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(STATUS_LABELS).map(([key, label]) => (
                    <SelectItem key={key} value={key}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>
        )}

        {/* Tabs */}
        <Tabs defaultValue="documents" className="space-y-4">
          <TabsList>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="payments">Payments</TabsTrigger>
            <TabsTrigger value="notes">Notes</TabsTrigger>
          </TabsList>

          <TabsContent value="documents" className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Documents</h3>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add Document
              </Button>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {documents.map((doc) => (
                <Card key={doc.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-primary" />
                        <div>
                          <p className="font-medium">{doc.name}</p>
                          <p className="text-sm text-muted-foreground">{doc.type}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <StatusBadge status={doc.status} type="document" />
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedDoc(doc);
                            setIsDeleteDocOpen(true);
                          }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            {documents.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8">No documents yet</p>
            )}
          </TabsContent>

          <TabsContent value="payments" className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold">Payments</h3>
                <p className="text-sm text-muted-foreground">
                  Payment information is shared with the client
                </p>
              </div>
              {hasPermission('add_edit_payment') && (
                <Button size="sm" onClick={() => setIsAddPaymentOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Payment
                </Button>
              )}
            </div>
            
            {/* Payment Summary */}
            <Card>
              <CardContent className="p-4">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Amount</p>
                    <p className="text-xl font-bold">{formatAmount(client.totalAmount)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Paid Amount</p>
                    <p className="text-xl font-bold text-green-600">{formatAmount(client.paidAmount)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Remaining</p>
                    <p className="text-xl font-bold text-orange-600">
                      {formatAmount(client.totalAmount - client.paidAmount)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <div className="space-y-2">
              {payments.map((payment) => (
                <Card key={payment.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-lg">{formatAmount(payment.amount || 0)}</p>
                        <p className="text-sm text-muted-foreground">{payment.method || '-'}</p>
                        {payment.note && (
                          <p className="text-sm text-muted-foreground mt-1 italic">{payment.note}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">
                          {new Date(payment.created_at).toLocaleDateString()}
                        </p>
                        {payment.created_by_name && (
                          <p className="text-xs text-muted-foreground">by {payment.created_by_name}</p>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            {payments.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8">No payments recorded yet</p>
            )}
          </TabsContent>

          <TabsContent value="notes" className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Notes</h3>
            </div>
            <Card>
              <CardContent className="p-4 space-y-4">
                <Textarea
                  placeholder="Add a note..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                />
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="client-facing"
                    checked={isClientFacing}
                    onChange={(e) => setIsClientFacing(e.target.checked)}
                  />
                  <Label htmlFor="client-facing">Client-facing note</Label>
                </div>
                <Button disabled={!newNote.trim()}>
                  <Send className="h-4 w-4 mr-2" />
                  Add Note
                </Button>
              </CardContent>
            </Card>
            {notes.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8">No notes yet</p>
            )}
          </TabsContent>
        </Tabs>

        {/* Edit Dialog */}
        <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Client</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Name</Label>
                <Input
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  type="email"
                  value={editForm.email}
                  onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <Input
                  value={editForm.phone}
                  onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsEditOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSaveEdit} disabled={isSaving}>
                {isSaving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Save
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Add Payment Dialog */}
        <Dialog open={isAddPaymentOpen} onOpenChange={setIsAddPaymentOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Record Payment</DialogTitle>
              <DialogDescription>
                Record a payment received from {client.name}. This amount will be added to their paid amount and will be visible to them.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Payment Amount *</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  placeholder="0.00"
                />
                <p className="text-xs text-muted-foreground">
                  Current paid: {formatAmount(client.paidAmount)} / {formatAmount(client.totalAmount)} total
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddPaymentOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddPayment} disabled={isSaving || !paymentAmount}>
                {isSaving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Record Payment
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Document Dialog */}
        <AlertDialog open={isDeleteDocOpen} onOpenChange={setIsDeleteDocOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Document</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete <strong>{selectedDoc?.name}</strong>?
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDeleteDocument}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                {isSaving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </DashboardLayout>
  );
}
