import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { StatusBadge } from '@/components/ui/status-badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
import { Document as DocType, Client } from '@/types';
import { FileText, Search, Send, Trash2, Loader2, User, ChevronDown, ChevronUp } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { PERMISSIONS } from '@/types';
import { apiService } from '@/services/api';
import { useNavigate } from 'react-router-dom';

interface DocumentWithClient extends DocType {
  clientName?: string;
  clientId?: string;
  client_id?: string;
}

interface ClientDocumentGroup {
  clientId: string;
  clientName: string;
  clientEmail: string;
  documents: DocumentWithClient[];
  totalDocs: number;
  completeDocs: number;
  pendingDocs: number;
  missingDocs: number;
}

export default function Documents() {
  const { hasPermission } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [documents, setDocuments] = useState<DocumentWithClient[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [groupedByClient, setGroupedByClient] = useState<ClientDocumentGroup[]>([]);
  const [expandedClients, setExpandedClients] = useState<Set<string>>(new Set());
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<DocumentWithClient | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);

  useEffect(() => {
    loadDocuments();
    loadClients();
  }, [statusFilter]);

  useEffect(() => {
    groupDocumentsByClient();
  }, [documents, clients]);

  useEffect(() => {
    const debounce = setTimeout(() => {
      if (search || statusFilter !== 'all') {
        loadDocuments();
      }
    }, 500);
    return () => clearTimeout(debounce);
  }, [search]);

  const loadDocuments = async () => {
    try {
      setIsLoadingDocuments(true);
      const params: any = {};
      
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      if (search) {
        params.search = search;
      }

      const response = await apiService.getDocuments(params);
      // Map API response to frontend format
      const mappedDocs = (response.documents || []).map((doc: any) => ({
        ...doc,
        clientId: doc.client_id || doc.clientId,
        clientName: doc.client_name || undefined,
      }));
      setDocuments(mappedDocs);
    } catch (error: any) {
      console.error('Failed to load documents:', error);
      toast({
        title: 'Error',
        description: 'Failed to load documents',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingDocuments(false);
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

  const groupDocumentsByClient = () => {
    const clientMap = new Map<string, ClientDocumentGroup>();

    // Initialize all clients with empty documents
    clients.forEach(client => {
      clientMap.set(client.id, {
        clientId: client.id,
        clientName: client.name,
        clientEmail: client.email,
        documents: [],
        totalDocs: 0,
        completeDocs: 0,
        pendingDocs: 0,
        missingDocs: 0,
      });
    });

    // Group documents by client
    documents.forEach(doc => {
      const clientId = doc.clientId || (doc as any).client_id;
      if (clientId) {
        if (clientMap.has(clientId)) {
          const group = clientMap.get(clientId)!;
          group.documents.push(doc);
          group.totalDocs++;
          if (doc.status === 'complete') group.completeDocs++;
          else if (doc.status === 'pending') group.pendingDocs++;
          else if (doc.status === 'missing') group.missingDocs++;
        } else {
          // Client not in map, but document exists - create group
          clientMap.set(clientId, {
            clientId: clientId,
            clientName: doc.clientName || 'Unknown Client',
            clientEmail: '',
            documents: [doc],
            totalDocs: 1,
            completeDocs: doc.status === 'complete' ? 1 : 0,
            pendingDocs: doc.status === 'pending' ? 1 : 0,
            missingDocs: doc.status === 'missing' ? 1 : 0,
          });
        }
      }
    });

    // Filter by search and convert to array
    let grouped = Array.from(clientMap.values()).filter(group => {
      if (search) {
        const matchesSearch = 
          group.clientName.toLowerCase().includes(search.toLowerCase()) ||
          group.clientEmail.toLowerCase().includes(search.toLowerCase()) ||
          group.documents.some(doc => doc.name.toLowerCase().includes(search.toLowerCase()));
        if (!matchesSearch) return false;
      }
      return group.totalDocs > 0;
    });

    // Sort by client name
    grouped.sort((a, b) => a.clientName.localeCompare(b.clientName));

    setGroupedByClient(grouped);
    
    // Auto-expand all clients by default
    if (expandedClients.size === 0 && grouped.length > 0) {
      setExpandedClients(new Set(grouped.map(g => g.clientId)));
    }
  };

  const toggleClientExpansion = (clientId: string) => {
    setExpandedClients(prev => {
      const newSet = new Set(prev);
      if (newSet.has(clientId)) {
        newSet.delete(clientId);
      } else {
        newSet.add(clientId);
      }
      return newSet;
    });
  };

  const stats = {
    total: documents.length,
    complete: documents.filter((d) => d.status === 'complete').length,
    pending: documents.filter((d) => d.status === 'pending').length,
    missing: documents.filter((d) => d.status === 'missing').length,
  };

  const handleRequestDocument = (docName: string) => {
    toast({
      title: 'Request Sent',
      description: `Document request for "${docName}" has been sent to the client.`,
    });
  };

  const handleDeleteDocument = async () => {
    if (!selectedDoc) return;

    setIsLoading(true);
    try {
      await apiService.deleteDocument(selectedDoc.id);

      toast({
        title: 'Document Deleted',
        description: 'The document has been removed from the system.',
      });

      setIsDeleteOpen(false);
      setSelectedDoc(null);
      await loadDocuments();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete document',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoadingDocuments) {
    return (
      <DashboardLayout
        title="Document Management"
        breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Documents' }]}
      >
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      title="Document Management"
      breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Documents' }]}
    >
      <div className="space-y-6 animate-fade-in">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Total Documents', value: stats.total, color: '' },
            { label: 'Complete', value: stats.complete, color: 'text-green-600' },
            { label: 'Pending', value: stats.pending, color: 'text-amber-600' },
            { label: 'Missing', value: stats.missing, color: 'text-red-600' },
          ].map((stat, index) => (
            <Card 
              key={stat.label}
              className="transition-all duration-300 hover:shadow-md hover:-translate-y-1"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <CardContent className="p-4">
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search by client name or document..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 transition-all duration-200 focus:scale-[1.01]"
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="complete">Complete</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="missing">Missing</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Client Cards with Documents */}
        {groupedByClient.length > 0 ? (
          <div className="space-y-4">
            {groupedByClient.map((clientGroup, index) => {
              const isExpanded = expandedClients.has(clientGroup.clientId);
              
              return (
                <Card 
                  key={clientGroup.clientId}
                  className="transition-all duration-300 hover:shadow-md"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <CardHeader 
                    className="cursor-pointer hover:bg-muted/50 transition-colors"
                    onClick={() => toggleClientExpansion(clientGroup.clientId)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                          <User className="h-5 w-5 text-primary" />
                        </div>
                        <div className="flex-1">
                          <CardTitle className="text-lg">{clientGroup.clientName}</CardTitle>
                          <p className="text-sm text-muted-foreground">{clientGroup.clientEmail}</p>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>{clientGroup.totalDocs} document{clientGroup.totalDocs !== 1 ? 's' : ''}</span>
                          {isExpanded ? (
                            <ChevronUp className="h-5 w-5" />
                          ) : (
                            <ChevronDown className="h-5 w-5" />
                          )}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/clients/${clientGroup.clientId}`);
                        }}
                      >
                        View Client
                      </Button>
                    </div>
                    
                    {/* Document stats for client */}
                    <div className="flex gap-4 mt-2 text-xs">
                      {clientGroup.completeDocs > 0 && (
                        <span className="text-green-600">✓ {clientGroup.completeDocs} Complete</span>
                      )}
                      {clientGroup.pendingDocs > 0 && (
                        <span className="text-amber-600">⏳ {clientGroup.pendingDocs} Pending</span>
                      )}
                      {clientGroup.missingDocs > 0 && (
                        <span className="text-red-600">✗ {clientGroup.missingDocs} Missing</span>
                      )}
                    </div>
                  </CardHeader>

                  {/* Documents List */}
                  {isExpanded && (
                    <CardContent className="pt-0">
                      <div className="space-y-3">
                        {clientGroup.documents.map((doc) => (
                          <div
                            key={doc.id}
                            className="flex items-center justify-between p-3 rounded-lg bg-muted/30 border border-border hover:bg-muted/50 transition-colors"
                          >
                            <div className="flex items-center gap-3 flex-1">
                              <div className="flex h-8 w-8 items-center justify-center rounded bg-primary/10">
                                <FileText className="h-4 w-4 text-primary" />
                              </div>
                              <div className="flex-1">
                                <p className="font-medium text-sm">{doc.name}</p>
                                <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                                  <span>Type: {doc.type}</span>
                                  <span>•</span>
                                  <span>Version {doc.version}</span>
                                  {doc.uploadedAt && (
                                    <>
                                      <span>•</span>
                                      <span>
                                        Uploaded: {new Date(doc.uploadedAt).toLocaleDateString()}
                                      </span>
                                    </>
                                  )}
                                </div>
                              </div>
                              <StatusBadge status={doc.status} type="document" />
                            </div>
                            <div className="flex gap-2 ml-4">
                              {doc.status === 'missing' && hasPermission(PERMISSIONS.REQUEST_DOCUMENTS) && (
                                <Button 
                                  variant="outline" 
                                  size="sm"
                                  onClick={() => handleRequestDocument(doc.name)}
                                >
                                  <Send className="h-3 w-3 mr-1" />
                                  Request
                                </Button>
                              )}
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setSelectedDoc(doc);
                                  setIsDeleteOpen(true);
                                }}
                                className="text-destructive hover:text-destructive"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  )}
                </Card>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-12 animate-fade-in">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No documents found.</p>
            <p className="text-sm text-muted-foreground mt-2">
              Documents will appear here once clients upload them.
            </p>
          </div>
        )}

        {/* Delete Confirmation */}
        <AlertDialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
          <AlertDialogContent className="animate-scale-in">
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Document</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete <strong>{selectedDoc?.name}</strong>? This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction 
                onClick={handleDeleteDocument}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
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
