// Diamonds Accounts Admin System JavaScript

// Global State Management
const AdminSystem = {
    currentUser: null,
    clients: [],
    admins: [],
    nextClientId: 676, // Starting ID as specified
    syncChannel: null, // BroadcastChannel for real-time sync
    
    // Initialize the system
    init() {
        this.initRealTimeSync();
        this.loadPersistedData();
        this.bindEvents();
        this.showLoginPage();
    },

    // Initialize real-time synchronization
    initRealTimeSync() {
        // Create broadcast channel for cross-tab communication
        this.syncChannel = new BroadcastChannel('diamonds-accounts-sync');
        
        // Listen for updates from other tabs/windows
        this.syncChannel.addEventListener('message', (event) => {
            const { type, data, timestamp } = event.data;
            
            switch (type) {
                case 'CLIENT_UPDATED':
                    this.handleClientUpdate(data);
                    break;
                case 'ADMIN_UPDATED':
                    this.handleAdminUpdate(data);
                    break;
                case 'CLIENT_ADDED':
                    this.handleClientAdded(data);
                    break;
                case 'ADMIN_ADDED':
                    this.handleAdminAdded(data);
                    break;
                case 'CLIENT_DELETED':
                    this.handleClientDeleted(data);
                    break;
                case 'ADMIN_DELETED':
                    this.handleAdminDeleted(data);
                    break;
                case 'DOCUMENT_STATUS_CHANGED':
                    this.handleDocumentStatusChange(data);
                    break;
                case 'PAYMENT_STATUS_CHANGED':
                    this.handlePaymentStatusChange(data);
                    break;
            }
        });

        // Sync with external systems (Flutter app)
        this.initFlutterSync();
    },

    // Initialize Flutter app synchronization
    initFlutterSync() {
        // Listen for messages from Flutter app
        window.addEventListener('message', (event) => {
            // Verify origin for security
            if (event.origin !== window.location.origin) return;
            
            const { type, data } = event.data;
            
            if (type === 'FLUTTER_SYNC') {
                this.handleFlutterMessage(data);
            }
        });

        // Setup periodic sync check
        setInterval(() => {
            this.syncWithExternalSources();
        }, 5000); // Sync every 5 seconds
    },

    // Load data from localStorage or fallback to dummy data
    loadPersistedData() {
        try {
            const savedClients = localStorage.getItem('diamonds-clients');
            const savedAdmins = localStorage.getItem('diamonds-admins');
            const savedNextId = localStorage.getItem('diamonds-next-id');

            if (savedClients) {
                this.clients = JSON.parse(savedClients);
            } else {
                this.loadDummyData();
                this.persistData();
            }

            if (savedAdmins) {
                this.admins = JSON.parse(savedAdmins);
            } else {
                this.loadDummyAdmins();
                this.persistData();
            }

            if (savedNextId) {
                this.nextClientId = parseInt(savedNextId, 10);
            }
        } catch (error) {
            console.warn('Failed to load persisted data:', error);
            this.loadDummyData();
        }
    },

    // Persist data to localStorage
    persistData() {
        try {
            localStorage.setItem('diamonds-clients', JSON.stringify(this.clients));
            localStorage.setItem('diamonds-admins', JSON.stringify(this.admins));
            localStorage.setItem('diamonds-next-id', this.nextClientId.toString());
            
            // Broadcast data change to other tabs
            this.broadcastDataChange();
        } catch (error) {
            console.error('Failed to persist data:', error);
        }
    },

    // Broadcast data changes to other tabs/windows
    broadcastDataChange() {
        if (this.syncChannel) {
            this.syncChannel.postMessage({
                type: 'DATA_SYNC',
                data: {
                    clients: this.clients,
                    admins: this.admins,
                    nextClientId: this.nextClientId
                },
                timestamp: Date.now(),
                source: 'admin-dashboard'
            });
        }
    },

    // Load sample data
    loadDummyData() {
        this.loadDummyAdmins();
        this.loadDummyClients();
    },

    // Load sample admins
    loadDummyAdmins() {
        this.admins = [
            {
                id: 1,
                name: 'John Admin',
                email: 'admin@diamonds.com',
                password: 'admin123',
                role: 'admin',
                permissions: {
                    viewSummary: true,
                    updateStatus: true,
                    requestDocs: true,
                    paymentToggle: true
                },
                createdDate: '2024-01-15'
            },
            {
                id: 2,
                name: 'Sarah Manager',
                email: 'sarah@diamonds.com',
                password: 'admin123',
                role: 'admin',
                permissions: {
                    viewSummary: true,
                    updateStatus: true,
                    requestDocs: true,
                    paymentToggle: false
                },
                createdDate: '2024-02-01'
            },
            {
                id: 3,
                name: 'Mike Senior',
                email: 'mike@diamonds.com',
                password: 'admin123',
                role: 'admin',
                permissions: {
                    viewSummary: true,
                    updateStatus: false,
                    requestDocs: true,
                    paymentToggle: false
                },
                createdDate: '2024-02-15'
            }
        ];
    },

    // Load sample clients
    loadDummyClients() {
        this.clients = [
            {
                id: this.nextClientId++,
                name: 'Vinod Kumar',
                assignedAdmin: 'John Admin',
                status: 'pending',
                lastUpdated: '2024-11-15',
                createdDate: '2024-11-01',
                paymentReceived: false,
                notes: 'Client needs to submit updated bank statement.',
                documents: {
                    panCard: { required: true, submitted: true },
                    bankStatement: { required: true, submitted: false },
                    itrForm: { required: true, submitted: true },
                    salarySlips: { required: true, submitted: false },
                    rentReceipts: { required: false, submitted: true }
                }
            },
            {
                id: this.nextClientId++,
                name: 'Priya Sharma',
                assignedAdmin: 'Sarah Manager',
                status: 'assigned',
                lastUpdated: '2024-11-18',
                createdDate: '2024-10-25',
                paymentReceived: true,
                notes: 'All documents submitted. Processing ITR.',
                documents: {
                    panCard: { required: true, submitted: true },
                    bankStatement: { required: true, submitted: true },
                    itrForm: { required: true, submitted: true },
                    salarySlips: { required: true, submitted: true },
                    rentReceipts: { required: false, submitted: false }
                }
            },
            {
                id: this.nextClientId++,
                name: 'Rajesh Gupta',
                assignedAdmin: 'Mike Senior',
                status: 'completed',
                lastUpdated: '2024-11-10',
                createdDate: '2024-10-15',
                paymentReceived: true,
                notes: 'ITR filed successfully. Client notified.',
                documents: {
                    panCard: { required: true, submitted: true },
                    bankStatement: { required: true, submitted: true },
                    itrForm: { required: true, submitted: true },
                    salarySlips: { required: true, submitted: true },
                    rentReceipts: { required: true, submitted: true }
                }
            },
            {
                id: this.nextClientId++,
                name: 'Anita Desai',
                assignedAdmin: 'John Admin',
                status: 'unassigned',
                lastUpdated: '2024-11-19',
                createdDate: '2024-11-18',
                paymentReceived: false,
                notes: 'New client - initial consultation completed.',
                documents: {
                    panCard: { required: true, submitted: false },
                    bankStatement: { required: true, submitted: false },
                    itrForm: { required: true, submitted: false },
                    salarySlips: { required: true, submitted: false },
                    rentReceipts: { required: false, submitted: false }
                }
            },
            {
                id: this.nextClientId++,
                name: 'Suresh Reddy',
                assignedAdmin: 'Sarah Manager',
                status: 'pending',
                lastUpdated: '2024-11-17',
                createdDate: '2024-11-05',
                paymentReceived: false,
                notes: 'Waiting for additional salary slips from client.',
                documents: {
                    panCard: { required: true, submitted: true },
                    bankStatement: { required: true, submitted: true },
                    itrForm: { required: true, submitted: false },
                    salarySlips: { required: true, submitted: false },
                    rentReceipts: { required: true, submitted: true }
                }
            },
            {
                id: this.nextClientId++,
                name: 'Kavitha Nair',
                assignedAdmin: 'Mike Senior',
                status: 'assigned',
                lastUpdated: '2024-11-16',
                createdDate: '2024-11-08',
                paymentReceived: true,
                notes: 'Professional consultation scheduled for next week.',
                documents: {
                    panCard: { required: true, submitted: true },
                    bankStatement: { required: true, submitted: true },
                    itrForm: { required: true, submitted: true },
                    salarySlips: { required: true, submitted: true },
                    rentReceipts: { required: false, submitted: false }
                }
            },
            {
                id: this.nextClientId++,
                name: 'Amit Patel',
                assignedAdmin: 'John Admin',
                status: 'draft',
                lastUpdated: '2024-11-19',
                createdDate: '2024-11-19',
                paymentReceived: false,
                notes: 'Initial draft prepared, review pending.',
                documents: {
                    panCard: { required: true, submitted: true },
                    bankStatement: { required: true, submitted: false },
                    itrForm: { required: true, submitted: false },
                    salarySlips: { required: true, submitted: true },
                    rentReceipts: { required: false, submitted: false }
                }
            }
        ];
    },

    // Real-time sync handlers
    handleClientUpdate(clientData) {
        const index = this.clients.findIndex(c => c.id === clientData.id);
        if (index !== -1) {
            this.clients[index] = { ...this.clients[index], ...clientData };
            this.refreshCurrentView();
            this._notify({ message: `Client ${clientData.name} updated by another user`, type: 'success' });
        }
    },

    handleAdminUpdate(adminData) {
        const index = this.admins.findIndex(a => a.id === adminData.id);
        if (index !== -1) {
            this.admins[index] = { ...this.admins[index], ...adminData };
            this.refreshCurrentView();
            this._notify({ message: `Admin ${adminData.name} updated by another user`, type: 'success' });
        }
    },

    handleClientAdded(clientData) {
        const exists = this.clients.some(c => c.id === clientData.id);
        if (!exists) {
            this.clients.push(clientData);
            this.refreshCurrentView();
            this._notify({ message: `New client ${clientData.name} added by another user`, type: 'success' });
        }
    },

    handleAdminAdded(adminData) {
        const exists = this.admins.some(a => a.id === adminData.id);
        if (!exists) {
            this.admins.push(adminData);
            this.refreshCurrentView();
            this._notify({ message: `New admin ${adminData.name} added by another user`, type: 'success' });
        }
    },

    handleClientDeleted(clientId) {
        this.clients = this.clients.filter(c => c.id !== clientId);
        this.refreshCurrentView();
        this._notify({ message: 'Client deleted by another user', type: 'warning' });
    },

    handleAdminDeleted(adminId) {
        this.admins = this.admins.filter(a => a.id !== adminId);
        this.refreshCurrentView();
        this._notify({ message: 'Admin deleted by another user', type: 'warning' });
    },

    handleDocumentStatusChange(data) {
        const { clientId, docType, submitted } = data;
        const client = this.clients.find(c => c.id === clientId);
        if (client && client.documents[docType]) {
            client.documents[docType].submitted = submitted;
            this.refreshCurrentView();
        }
    },

    handlePaymentStatusChange(data) {
        const { clientId, paymentReceived } = data;
        const client = this.clients.find(c => c.id === clientId);
        if (client) {
            client.paymentReceived = paymentReceived;
            this.refreshCurrentView();
        }
    },

    // Handle Flutter app messages
    handleFlutterMessage(data) {
        const { type, payload } = data;
        
        switch (type) {
            case 'CLIENT_STATUS_UPDATE':
                this.handleClientUpdate(payload);
                break;
            case 'DOCUMENT_UPLOAD':
                this.handleDocumentStatusChange(payload);
                break;
            case 'PAYMENT_UPDATE':
                this.handlePaymentStatusChange(payload);
                break;
        }
    },

    // Sync with external sources
    syncWithExternalSources() {
        // Check for updates from backend API or other sources
        // This could be expanded to include REST API calls
        
        // For now, just ensure localStorage is in sync
        try {
            const currentData = {
                clients: JSON.parse(localStorage.getItem('diamonds-clients') || '[]'),
                admins: JSON.parse(localStorage.getItem('diamonds-admins') || '[]'),
                nextClientId: parseInt(localStorage.getItem('diamonds-next-id') || '676', 10)
            };

            let hasChanges = false;

            // Check if external data is different
            if (JSON.stringify(currentData.clients) !== JSON.stringify(this.clients)) {
                this.clients = currentData.clients;
                hasChanges = true;
            }

            if (JSON.stringify(currentData.admins) !== JSON.stringify(this.admins)) {
                this.admins = currentData.admins;
                hasChanges = true;
            }

            if (currentData.nextClientId !== this.nextClientId) {
                this.nextClientId = currentData.nextClientId;
                hasChanges = true;
            }

            if (hasChanges) {
                this.refreshCurrentView();
            }
        } catch (error) {
            console.error('Sync error:', error);
        }
    },

    // Refresh current view based on active section
    refreshCurrentView() {
        const activeSection = document.querySelector('.content-section.active');
        if (!activeSection) return;

        const sectionId = activeSection.id;
        
        if (sectionId === 'clientsSection') {
            this.loadClientsTable();
            this.updateAnalytics();
        } else if (sectionId === 'adminsSection') {
            this.loadAdminsTable();
        } else if (sectionId === 'analyticsSection') {
            this.updateAnalytics();
        }

        // Update client modal if it's open
        const clientModal = document.getElementById('clientModal');
        if (clientModal.classList.contains('active') && this.currentClientId) {
            const client = this.clients.find(c => c.id === this.currentClientId);
            if (client) {
                this.showClientSummary(client.id);
            }
        }
    },

    // Broadcast specific change types
    broadcastClientUpdate(client) {
        if (this.syncChannel) {
            this.syncChannel.postMessage({
                type: 'CLIENT_UPDATED',
                data: client,
                timestamp: Date.now(),
                source: 'admin-dashboard'
            });
        }
    },

    broadcastAdminUpdate(admin) {
        if (this.syncChannel) {
            this.syncChannel.postMessage({
                type: 'ADMIN_UPDATED',
                data: admin,
                timestamp: Date.now(),
                source: 'admin-dashboard'
            });
        }
    },

    broadcastClientAdded(client) {
        if (this.syncChannel) {
            this.syncChannel.postMessage({
                type: 'CLIENT_ADDED',
                data: client,
                timestamp: Date.now(),
                source: 'admin-dashboard'
            });
        }
    },

    broadcastDocumentStatusChange(clientId, docType, submitted) {
        if (this.syncChannel) {
            this.syncChannel.postMessage({
                type: 'DOCUMENT_STATUS_CHANGED',
                data: { clientId, docType, submitted },
                timestamp: Date.now(),
                source: 'admin-dashboard'
            });
        }
    },

    broadcastPaymentStatusChange(clientId, paymentReceived) {
        if (this.syncChannel) {
            this.syncChannel.postMessage({
                type: 'PAYMENT_STATUS_CHANGED',
                data: { clientId, paymentReceived },
                timestamp: Date.now(),
                source: 'admin-dashboard'
            });
        }
    },

    // Bind event listeners
    bindEvents() {
        // Login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Logout button
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });

        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showSection(e.target.dataset.section);
            });
        });

        // Search functionality
        document.getElementById('clientSearch').addEventListener('input', (e) => {
            this.filterClients();
        });

        // Status filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setActiveFilter(e.target);
                this.filterClients();
            });
        });

        // Date filters
        document.getElementById('startDate').addEventListener('change', () => {
            this.filterClients();
        });
        document.getElementById('endDate').addEventListener('change', () => {
            this.filterClients();
        });

        // Modal handlers
        this.bindModalEvents();

        // Add client/admin buttons
        document.getElementById('addClientBtn').addEventListener('click', () => {
            this.showAddClientModal();
        });

        document.getElementById('addAdminBtn').addEventListener('click', () => {
            this.showAddAdminModal();
        });
    },

    // Bind modal events
    bindModalEvents() {
        // Client modal
        document.getElementById('closeModal').addEventListener('click', () => {
            this.hideModal('clientModal');
        });

        document.getElementById('updateClientBtn').addEventListener('click', () => {
            this.updateClient();
        });

        document.getElementById('requestDocsBtn').addEventListener('click', () => {
            this.requestDocuments();
        });

        document.getElementById('requestFeesBtn').addEventListener('click', () => {
            this.requestFees();
        });

        document.getElementById('downloadFilesBtn').addEventListener('click', () => {
            this.downloadFiles();
        });

        // Admin modal
        document.getElementById('closeAdminModal').addEventListener('click', () => {
            this.hideModal('adminModal');
        });

        document.getElementById('cancelAdminBtn').addEventListener('click', () => {
            this.hideModal('adminModal');
        });

        document.getElementById('addAdminForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addNewAdmin();
        });

        // Add client modal
        document.getElementById('closeAddClientModal').addEventListener('click', () => {
            this.hideModal('addClientModal');
        });

        document.getElementById('cancelClientBtn').addEventListener('click', () => {
            this.hideModal('addClientModal');
        });

        document.getElementById('addClientForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addNewClient();
        });

        // Close modals when clicking outside
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });
    },

    // Authentication
    handleLogin() {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const errorDiv = document.getElementById('loginError');

        // Check for superadmin
        if (email === 'superadmin@diamonds.com' && password === 'admin123') {
            this.currentUser = {
                id: 0,
                name: 'Super Admin',
                email: email,
                role: 'superadmin',
                permissions: {
                    viewSummary: true,
                    updateStatus: true,
                    requestDocs: true,
                    paymentToggle: true,
                    requestFees: true,
                    manageAdmins: true
                }
            };
            this.showDashboard();
            return;
        }

        // Check for regular admins
        const admin = this.admins.find(a => a.email === email && a.password === password);
        if (admin) {
            this.currentUser = admin;
            this.showDashboard();
            return;
        }

        // Show error
        errorDiv.textContent = 'Invalid email or password';
        errorDiv.style.display = 'block';
    },

    logout() {
        this.currentUser = null;
        this.showLoginPage();
    },

    // Page Navigation
    showLoginPage() {
        document.getElementById('loginPage').classList.add('active');
        document.getElementById('dashboardPage').classList.remove('active');
        
        // Clear login form
        document.getElementById('loginForm').reset();
        document.getElementById('loginError').style.display = 'none';
    },

    showDashboard() {
        document.getElementById('loginPage').classList.remove('active');
        document.getElementById('dashboardPage').classList.add('active');
        
        // Update user info
        document.getElementById('userInfo').textContent = `${this.currentUser.name} (${this.currentUser.role})`;
        
        // Show/hide superadmin elements
        if (this.currentUser.role === 'superadmin') {
            document.querySelectorAll('.superadmin-only').forEach(el => {
                el.classList.add('show');
            });
        }
        
        // Load initial data
        this.showSection('clients');
        this.updateAnalytics();
    },

    showSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Show section
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}Section`).classList.add('active');

        // Load section-specific data
        switch (sectionName) {
            case 'clients':
                this.loadClientsTable();
                break;
            case 'admins':
                this.loadAdminsTable();
                break;
            case 'analytics':
                this.updateAnalytics();
                break;
        }
    },

    // Client Management
    loadClientsTable() {
        const tbody = document.getElementById('clientTableBody');
        tbody.innerHTML = '';
        
        const filteredClients = this.getFilteredClients();
        
        filteredClients.forEach(client => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>#${client.id}</strong></td>
                <td>${client.name}</td>
                <td>
                    ${this.currentUser.role === 'superadmin' ? 
                        `<select onchange="AdminSystem.updateClientAdmin(${client.id}, this.value)">
                            ${this.getAdminOptions(client.assignedAdmin)}
                        </select>` : 
                        client.assignedAdmin
                    }
                </td>
                <td>
                    ${this.currentUser.permissions.updateStatus ?
                        `<select onchange="AdminSystem.updateClientStatus(${client.id}, this.value)">
                            ${this.getStatusOptions(client.status)}
                        </select>` :
                        `<span class="status-badge status-${client.status}">${this.capitalizeFirst(client.status)}</span>`
                    }
                </td>
                <td>${this.formatDate(client.lastUpdated)}</td>
                <td>
                    <button class="action-btn" onclick="AdminSystem.showClientSummary(${client.id})">
                        View Details
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    },

    getFilteredClients() {
        let filtered = [...this.clients];
        
        // Search filter
        const searchTerm = document.getElementById('clientSearch').value.toLowerCase();
        if (searchTerm) {
            filtered = filtered.filter(client => 
                client.id.toString().includes(searchTerm) ||
                client.name.toLowerCase().includes(searchTerm)
            );
        }
        
        // Status filter
        const activeStatusFilter = document.querySelector('.filter-btn.active').dataset.status;
        if (activeStatusFilter !== 'all') {
            filtered = filtered.filter(client => client.status === activeStatusFilter);
        }
        
        // Date filter
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        if (startDate) {
            filtered = filtered.filter(client => client.createdDate >= startDate);
        }
        
        if (endDate) {
            filtered = filtered.filter(client => client.createdDate <= endDate);
        }
        
        // Sort by ID (First Come On Top)
        return filtered.sort((a, b) => a.id - b.id);
    },

    filterClients() {
        this.loadClientsTable();
    },

    setActiveFilter(button) {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');
    },

    updateClientAdmin(clientId, newAdmin) {
        const client = this.clients.find(c => c.id === clientId);
        if (client) {
            client.assignedAdmin = newAdmin;
            client.lastUpdated = this.getCurrentDate();
            this.loadClientsTable();
        }
    },

    updateClientStatus(clientId, newStatus) {
        const client = this.clients.find(c => c.id === clientId);
        if (client) {
            client.status = newStatus;
            client.lastUpdated = this.getCurrentDate();
            this.loadClientsTable();
        }
    },

    // Client Summary Modal
    showClientSummary(clientId) {
        const client = this.clients.find(c => c.id === clientId);
        if (!client) return;

        // Populate modal with client data
        document.getElementById('clientId').textContent = `#${client.id}`;
        document.getElementById('clientName').textContent = client.name;
        document.getElementById('assignedAdmin').textContent = client.assignedAdmin;
        document.getElementById('currentStatus').textContent = this.capitalizeFirst(client.status);
        document.getElementById('clientNotes').value = client.notes || '';
        document.getElementById('paymentReceived').checked = client.paymentReceived;

        // Load documents
        this.loadDocuments(client.documents);

        // Store current client ID for updates
        this.currentClientId = clientId;

        this.showModal('clientModal');
    },

    loadDocuments(documents) {
        const container = document.getElementById('documentsList');
        container.innerHTML = '';

        Object.entries(documents).forEach(([docType, docInfo]) => {
            const docElement = document.createElement('div');
            docElement.className = 'document-item';
            docElement.innerHTML = `
                <input type="checkbox" ${docInfo.submitted ? 'checked' : ''} 
                       onchange="AdminSystem.updateDocumentStatus('${docType}', this.checked)">
                <span class="document-name">${this.formatDocumentName(docType)}</span>
                <span class="document-status ${docInfo.submitted ? 'document-submitted' : 'document-missing'}">
                    ${docInfo.submitted ? 'Submitted' : 'Missing'}
                </span>
            `;
            container.appendChild(docElement);
        });
    },

    updateDocumentStatus(docType, isSubmitted) {
        const client = this.clients.find(c => c.id === this.currentClientId);
        if (client && client.documents[docType]) {
            client.documents[docType].submitted = isSubmitted;
            client.lastUpdated = this.getCurrentDate();
        }
    },

    updateClient() {
        const client = this.clients.find(c => c.id === this.currentClientId);
        if (!client) return;

        // Update payment status
        client.paymentReceived = document.getElementById('paymentReceived').checked;
        
        // Update notes
        client.notes = document.getElementById('clientNotes').value;
        
        // Update last modified date
        client.lastUpdated = this.getCurrentDate();

        this.hideModal('clientModal');
        this.loadClientsTable();
        this.showSuccessMessage('Client updated successfully!');
    },

    requestDocuments() {
        const client = this.clients.find(c => c.id === this.currentClientId);
        if (!client) return;

        // Simulate sending request
        this.showSuccessMessage(`Document request sent to ${client.name} successfully!`);
        
        // Add note about the request
        const currentNotes = client.notes || '';
        client.notes = currentNotes + `\n[${this.getCurrentDate()}] Document request sent to client.`;
        document.getElementById('clientNotes').value = client.notes;
    },

    requestFees() {
        const client = this.clients.find(c => c.id === this.currentClientId);
        if (!client) return;

        if (this.currentUser.role !== 'superadmin') {
            this.showErrorMessage('Only Superadmin can request fees!');
            return;
        }

        // Simulate sending fee request
        this.showSuccessMessage(`Fee request sent to ${client.name} successfully!`);
        
        // Add note about the fee request
        const currentNotes = client.notes || '';
        client.notes = currentNotes + `\n[${this.getCurrentDate()}] Fee request sent by ${this.currentUser.name}.`;
        document.getElementById('clientNotes').value = client.notes;
    },

    downloadFiles() {
        const client = this.clients.find(c => c.id === this.currentClientId);
        if (!client) return;

        // Simulate file download
        this.showSuccessMessage(`Downloading files for ${client.name}...`);
        
        // In a real application, this would trigger actual file downloads
        console.log(`Downloading files for client #${client.id} - ${client.name}`);
    },

    // Admin Management
    loadAdminsTable() {
        const tbody = document.getElementById('adminTableBody');
        tbody.innerHTML = '';
        
        this.admins.forEach(admin => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${admin.name}</td>
                <td>${admin.email}</td>
                <td>${this.formatPermissions(admin.permissions)}</td>
                <td>${this.formatDate(admin.createdDate)}</td>
                <td>
                    <button class="action-btn" onclick="AdminSystem.editAdmin(${admin.id})">
                        Edit
                    </button>
                    <button class="btn btn-warning" onclick="AdminSystem.deleteAdmin(${admin.id})" style="margin-left: 0.5rem;">
                        Delete
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    },

    formatPermissions(permissions) {
        const activePerms = Object.entries(permissions)
            .filter(([key, value]) => value)
            .map(([key]) => this.formatPermissionName(key));
        
        return activePerms.length > 0 ? activePerms.join(', ') : 'No permissions';
    },

    formatPermissionName(perm) {
        const names = {
            viewSummary: 'View Summary',
            updateStatus: 'Update Status',
            requestDocs: 'Request Docs',
            paymentToggle: 'Payment Toggle'
        };
        return names[perm] || perm;
    },

    showAddAdminModal() {
        this.showModal('adminModal');
    },

    addNewAdmin() {
        const name = document.getElementById('adminName').value;
        const email = document.getElementById('adminEmail').value;
        const password = document.getElementById('adminPassword').value;
        
        // Check if email already exists
        if (this.admins.find(a => a.email === email)) {
            this.showErrorMessage('Email already exists!');
            return;
        }

        const permissions = {
            viewSummary: document.getElementById('permViewSummary').checked,
            updateStatus: document.getElementById('permUpdateStatus').checked,
            requestDocs: document.getElementById('permRequestDocs').checked,
            paymentToggle: document.getElementById('permPaymentToggle').checked
        };

        const newAdmin = {
            id: this.admins.length + 1,
            name: name,
            email: email,
            password: password,
            role: 'admin',
            permissions: permissions,
            createdDate: this.getCurrentDate()
        };

        this.admins.push(newAdmin);
        this.hideModal('adminModal');
        this.loadAdminsTable();
        this.showSuccessMessage('Admin added successfully!');
        
        // Reset form
        document.getElementById('addAdminForm').reset();
    },

    editAdmin(adminId) {
        // This would open an edit modal in a full implementation
        this.showSuccessMessage('Edit functionality would open here in full implementation');
    },

    deleteAdmin(adminId) {
        if (confirm('Are you sure you want to delete this admin?')) {
            const admin = this.admins.find(a => a.id === adminId);
            this.admins = this.admins.filter(a => a.id !== adminId);
            
            // Persist and broadcast change
            this.persistData();
            if (this.syncChannel) {
                this.syncChannel.postMessage({
                    type: 'ADMIN_DELETED',
                    data: { adminId },
                    timestamp: Date.now(),
                    source: 'admin-dashboard'
                });
            }
            
            this.loadAdminsTable();
            this._notify({ 
                message: admin ? `Admin ${admin.name} deleted successfully` : 'Admin deleted successfully', 
                type: 'success' 
            });
        }
    },

    // Add new admin with real-time sync
    addNewAdmin() {
        const name = document.getElementById('newAdminName').value;
        const email = document.getElementById('newAdminEmail').value;
        const password = document.getElementById('newAdminPassword').value;

        // Check if email already exists
        if (this.admins.some(admin => admin.email === email)) {
            this._notify({ 
                message: 'Email already exists', 
                type: 'error' 
            });
            return;
        }

        const newAdmin = {
            id: Math.max(...this.admins.map(a => a.id), 0) + 1,
            name: name,
            email: email,
            password: password,
            role: 'admin',
            permissions: {
                viewSummary: true,
                updateStatus: true,
                requestDocs: true,
                paymentToggle: false
            },
            createdDate: this.getCurrentDate()
        };

        this.admins.push(newAdmin);
        
        // Persist data and broadcast change
        this.persistData();
        this.broadcastAdminAdded(newAdmin);
        
        this.hideModal('addAdminModal');
        this.loadAdminsTable();
        this._notify({ 
            message: 'Admin added successfully', 
            type: 'success' 
        });
        
        // Reset form
        document.getElementById('addAdminForm').reset();
    },

    // Edit admin with real-time sync
    editAdmin(adminId) {
        const admin = this.admins.find(a => a.id === adminId);
        if (!admin) return;

        // Populate edit modal
        document.getElementById('editAdminId').value = admin.id;
        document.getElementById('editAdminName').value = admin.name;
        document.getElementById('editAdminEmail').value = admin.email;
        
        // Set permissions checkboxes
        document.getElementById('editViewSummary').checked = admin.permissions.viewSummary;
        document.getElementById('editUpdateStatus').checked = admin.permissions.updateStatus;
        document.getElementById('editRequestDocs').checked = admin.permissions.requestDocs;
        document.getElementById('editPaymentToggle').checked = admin.permissions.paymentToggle;

        this.showModal('editAdminModal');
    },

    // Save admin changes with real-time sync
    saveAdminChanges() {
        const adminId = parseInt(document.getElementById('editAdminId').value);
        const admin = this.admins.find(a => a.id === adminId);
        if (!admin) return;

        // Update admin data
        admin.name = document.getElementById('editAdminName').value;
        admin.email = document.getElementById('editAdminEmail').value;
        admin.permissions = {
            viewSummary: document.getElementById('editViewSummary').checked,
            updateStatus: document.getElementById('editUpdateStatus').checked,
            requestDocs: document.getElementById('editRequestDocs').checked,
            paymentToggle: document.getElementById('editPaymentToggle').checked
        };

        // Persist data and broadcast changes
        this.persistData();
        this.broadcastAdminUpdate(admin);

        this.hideModal('editAdminModal');
        this.loadAdminsTable();
        this._notify({ 
            message: `Admin ${admin.name} updated successfully`, 
            type: 'success' 
        });
    },

    // Add Client Modal
    showAddClientModal() {
        // Populate admin dropdown
        const select = document.getElementById('assignAdmin');
        select.innerHTML = '<option value="">Select Admin</option>';
        
        this.admins.forEach(admin => {
            const option = document.createElement('option');
            option.value = admin.name;
            option.textContent = admin.name;
            select.appendChild(option);
        });

        this.showModal('addClientModal');
    },

    addNewClient() {
        const name = document.getElementById('newClientName').value;
        const assignedAdmin = document.getElementById('assignAdmin').value;
        const status = document.getElementById('clientStatus').value;

        const newClient = {
            id: this.nextClientId++,
            name: name,
            assignedAdmin: assignedAdmin,
            status: status,
            lastUpdated: this.getCurrentDate(),
            createdDate: this.getCurrentDate(),
            paymentReceived: false,
            notes: 'New client added to system.',
            documents: {
                panCard: { required: true, submitted: false },
                bankStatement: { required: true, submitted: false },
                itrForm: { required: true, submitted: false },
                salarySlips: { required: true, submitted: false },
                rentReceipts: { required: false, submitted: false }
            }
        };

        this.clients.push(newClient);
        
        // Persist data and broadcast change
        this.persistData();
        this.broadcastClientAdded(newClient);
        
        this.hideModal('addClientModal');
        this.loadClientsTable();
        this.showSuccessMessage('Client added successfully!');
        
        // Reset form
        document.getElementById('addClientForm').reset();
    },

    // Save client changes with real-time sync
    saveClientChanges() {
        const client = this.clients.find(c => c.id === this.currentClientId);
        if (!client) return;

        // Get updated values from the modal
        const statusSelect = document.getElementById('client-status');
        const adminSelect = document.getElementById('client-admin');
        const notesTextarea = document.getElementById('client-notes');

        client.status = statusSelect.value;
        client.assignedAdmin = adminSelect.value;
        client.notes = notesTextarea.value;
        client.lastUpdated = new Date().toISOString().split('T')[0];

        // Persist data and broadcast changes
        this.persistData();
        this.broadcastClientUpdate(client);

        this._notify({ 
            message: `Client ${client.name} updated successfully`, 
            type: 'success' 
        });

        this.loadClientsTable();
        this.closeModal('clientModal');
    },

    // Update payment status with real-time sync
    updatePaymentStatus(clientId, received) {
        const client = this.clients.find(c => c.id === clientId);
        if (!client) return;

        client.paymentReceived = received;
        client.lastUpdated = new Date().toISOString().split('T')[0];

        // Persist and broadcast change
        this.persistData();
        this.broadcastPaymentStatusChange(clientId, received);

        this._notify({ 
            message: `Payment status updated for ${client.name}`, 
            type: 'success' 
        });

        this.loadClientsTable();
        this.updateAnalytics();
    },

    // Toggle document status with real-time sync
    toggleDocumentStatus(clientId, docType) {
        const client = this.clients.find(c => c.id === clientId);
        if (!client || !client.documents[docType]) return;

        const currentStatus = client.documents[docType].submitted;
        client.documents[docType].submitted = !currentStatus;
        client.lastUpdated = new Date().toISOString().split('T')[0];

        // Persist and broadcast change
        this.persistData();
        this.broadcastDocumentStatusChange(clientId, docType, !currentStatus);

        this._notify({ 
            message: `Document ${docType} ${!currentStatus ? 'submitted' : 'removed'} for ${client.name}`, 
            type: 'success' 
        });

        // Refresh modal if open
        if (this.currentClientId === clientId) {
            this.showClientSummary(clientId);
        }
        this.loadClientsTable();
    },

    // Delete client with real-time sync
    deleteClient(clientId) {
        if (confirm('Are you sure you want to delete this client?')) {
            const client = this.clients.find(c => c.id === clientId);
            this.clients = this.clients.filter(c => c.id !== clientId);
            
            // Persist and broadcast change
            this.persistData();
            if (this.syncChannel) {
                this.syncChannel.postMessage({
                    type: 'CLIENT_DELETED',
                    data: { clientId },
                    timestamp: Date.now(),
                    source: 'admin-dashboard'
                });
            }
            
            this.loadClientsTable();
            this.updateAnalytics();
            this._notify({ 
                message: client ? `Client ${client.name} deleted successfully` : 'Client deleted successfully', 
                type: 'success' 
            });
        }
    },

    // Analytics
    updateAnalytics() {
        const totalClients = this.clients.length;
        const pendingCases = this.clients.filter(c => c.status === 'pending').length;
        const completedThisMonth = this.clients.filter(c => 
            c.status === 'completed' && 
            new Date(c.lastUpdated).getMonth() === new Date().getMonth()
        ).length;
        
        // Simulate revenue calculation
        const revenueThisMonth = completedThisMonth * 2500; // Average ₹2500 per case

        document.getElementById('totalClients').textContent = totalClients;
        document.getElementById('pendingCases').textContent = pendingCases;
        document.getElementById('completedMonth').textContent = completedThisMonth;
        document.getElementById('revenueMonth').textContent = `₹${revenueThisMonth.toLocaleString()}`;
    },

    // Utility Functions
    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    },

    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    },

    closeModal(modalId) {
        this.hideModal(modalId);
    },

    getCurrentDate() {
        return new Date().toISOString().split('T')[0];
    },

    // Flutter App Integration
    setupFlutterIntegration() {
        // Listen for messages from Flutter app via WebView postMessage
        window.addEventListener('message', (event) => {
            if (event.origin !== window.location.origin) return;
            
            try {
                const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
                if (data.source === 'flutter-app') {
                    this.handleFlutterMessage(data);
                }
            } catch (error) {
                console.error('Error handling Flutter message:', error);
            }
        });

        // Setup periodic sync check
        setInterval(() => {
            this.syncWithExternalSources();
        }, 5000); // Check every 5 seconds
    },

    // Send data to Flutter app
    sendToFlutterApp(data) {
        // Post message to Flutter WebView
        if (window.flutter_inappwebview) {
            window.flutter_inappwebview.callHandler('admin_dashboard_update', data);
        }
        
        // Also use postMessage for web Flutter apps
        const message = {
            type: 'ADMIN_DASHBOARD_UPDATE',
            payload: data,
            timestamp: Date.now(),
            source: 'admin-dashboard'
        };
        
        window.parent.postMessage(message, '*');
    },

    // API endpoints simulation for Flutter integration
    setupAPIEndpoints() {
        // Simulate REST API endpoints that Flutter app can call
        window.adminAPI = {
            getClients: () => this.clients,
            getClient: (id) => this.clients.find(c => c.id === id),
            updateClient: (id, data) => {
                const client = this.clients.find(c => c.id === id);
                if (client) {
                    Object.assign(client, data);
                    this.persistData();
                    this.broadcastClientUpdate(client);
                    return { success: true, client };
                }
                return { success: false, error: 'Client not found' };
            },
            getDocumentStatus: (clientId) => {
                const client = this.clients.find(c => c.id === clientId);
                return client ? client.documents : null;
            },
            updateDocumentStatus: (clientId, docType, submitted) => {
                this.toggleDocumentStatus(clientId, docType);
                return { success: true };
            },
            updatePaymentStatus: (clientId, paid) => {
                this.updatePaymentStatus(clientId, paid);
                return { success: true };
            }
        };
    },

    // Enhanced notification system for real-time updates
    _notify({ message, type = 'info', duration = 5000 }) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;
        
        const container = document.getElementById('notificationCenter') || this.createNotificationCenter();
        container.appendChild(notification);
        
        // Auto remove after duration
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    },

    createNotificationCenter() {
        let container = document.getElementById('notificationCenter');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notificationCenter';
            container.className = 'notification-center';
            document.body.appendChild(container);
        }
        return container;
    },

    getNotificationIcon(type) {
        switch (type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            default: return 'fa-info-circle';
        }
    },

    // Legacy notification support
    showSuccessMessage(message) {
        this._notify({ message, type: 'success' });
    },

    showErrorMessage(message) {
        this._notify({ message, type: 'error' });
    },

    showWarningMessage(message) {
        this._notify({ message, type: 'warning' });
    },

    // Helper methods
    getAdminOptions(selectedAdmin) {
        let options = '';
        this.admins.forEach(admin => {
            const selected = admin.name === selectedAdmin ? 'selected' : '';
            options += `<option value="${admin.name}" ${selected}>${admin.name}</option>`;
        });
        return options;
    },

    getStatusOptions(selectedStatus) {
        const statuses = ['assigned', 'unassigned', 'pending', 'completed', 'draft'];
        let options = '';
        statuses.forEach(status => {
            const selected = status === selectedStatus ? 'selected' : '';
            options += `<option value="${status}" ${selected}>${this.capitalizeFirst(status)}</option>`;
        });
        return options;
    },

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },

    formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString('en-IN');
    },

    formatDocumentName(docType) {
        const names = {
            panCard: 'PAN Card',
            bankStatement: 'Bank Statement',
            itrForm: 'ITR Form',
            salarySlips: 'Salary Slips',
            rentReceipts: 'Rent Receipts'
        };
        return names[docType] || docType;
    }
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Initialize the system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    AdminSystem.init();
});
