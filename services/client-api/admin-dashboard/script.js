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

    // Authentication with backend API integration
    async handleLogin() {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const errorDiv = document.getElementById('loginError');
        const loginButton = document.querySelector('#loginForm button[type="submit"]');
        
        // Disable button and show loading
        loginButton.disabled = true;
        loginButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
        errorDiv.style.display = 'none';

        try {
            // Try to authenticate with backend API
            const response = await fetch('/admin/api/v1/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            if (response.ok) {
                const data = await response.json();
                
                // Store tokens - backend returns { user: {...}, token: {...} }
                localStorage.setItem('admin_access_token', data.token.access_token);
                localStorage.setItem('admin_refresh_token', data.token.refresh_token);
                localStorage.setItem('admin_token_type', data.token.token_type);
                
                // Set current user
                this.currentUser = {
                    id: data.user.id,
                    name: data.user.name,
                    email: data.user.email,
                    role: data.user.role,
                    permissions: this.parsePermissions(data.user.role, data.user.permissions)
                };
                
                console.log('✅ Login successful:', this.currentUser.name);
                this.showDashboard();
                return;
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }
        } catch (error) {
            console.error('Backend authentication failed, trying local fallback:', error);
            
            // Fallback to local authentication for development
            if (this.tryLocalLogin(email, password)) {
                return;
            }
            
            // Show error
            errorDiv.textContent = error.message || 'Invalid email or password';
            errorDiv.style.display = 'block';
        } finally {
            // Re-enable button
            loginButton.disabled = false;
            loginButton.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
        }
    },

    // Fallback local authentication for development
    tryLocalLogin(email, password) {
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
            return true;
        }

        // Check for regular admins
        const admin = this.admins.find(a => a.email === email && a.password === password);
        if (admin) {
            this.currentUser = admin;
            this.showDashboard();
            return true;
        }

        return false;
    },

    // Parse permissions based on role
    parsePermissions(role, permissions) {
        if (role === 'superadmin') {
            return {
                viewSummary: true,
                updateStatus: true,
                requestDocs: true,
                paymentToggle: true,
                requestFees: true,
                manageAdmins: true
            };
        }
        
        // For regular admins, use permissions array
        return {
            viewSummary: permissions.includes('view_summary') || true,
            updateStatus: permissions.includes('update_status') || true,
            requestDocs: permissions.includes('request_docs') || true,
            paymentToggle: permissions.includes('payment_toggle') || false,
            requestFees: permissions.includes('request_fees') || false,
            manageAdmins: permissions.includes('manage_admins') || false
        };
    },

    logout() {
        this.currentUser = null;
        // Clear tokens
        localStorage.removeItem('admin_access_token');
        localStorage.removeItem('admin_refresh_token');
        this.showLoginPage();
    },

    // Helper to get auth headers
    getAuthHeaders() {
        const token = localStorage.getItem('admin_access_token');
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    },

    // Helper to make authenticated API requests
    async fetchWithAuth(url, options = {}) {
        const defaultOptions = {
            headers: this.getAuthHeaders()
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...(options.headers || {})
            }
        };

        try {
            const response = await fetch(url, mergedOptions);
            
            // Handle 401 Unauthorized - token expired
            if (response.status === 401) {
                console.warn('Authentication expired, redirecting to login');
                this.logout();
                return null;
            }
            
            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
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

        // Try to load real T1 form data, fallback to mock data
        this.loadEnhancedClientData(client);

        // Store current client ID for updates
        this.currentClientId = clientId;

        this.showModal('clientModal');
    },

    // Enhanced function to load real T1 form data with fallback to mock
    async loadEnhancedClientData(client) {
        try {
            // Try to fetch real T1 form data from backend API
            const response = await this.fetchWithAuth(`/admin/api/v1/t1-forms?client_email=${encodeURIComponent(client.email || client.name.toLowerCase().replace(' ', '.') + '@example.com')}`);
            
            if (response && response.ok) {
                const data = await response.json();
                if (data.forms && data.forms.length > 0) {
                    // Get detailed form data for the first form
                    const formId = data.forms[0].id;
                    const detailResponse = await this.fetchWithAuth(`/admin/api/v1/t1-forms/${formId}/detailed`);
                    
                    if (detailResponse && detailResponse.ok) {
                        const detailData = await detailResponse.json();
                        this.loadFormSummaryFromAPI(detailData.form_sections);
                        this.loadFileAttachmentsByCategory(detailData.categorized_files);
                        this.loadGeneralDocuments(client.documents);
                        return;
                    }
                }
            }
        } catch (error) {
            console.warn('Failed to load T1 form data from API, using mock data:', error);
        }

        // Fallback to mock data if API fails
        this.loadFormSummary(client);
        this.loadFileAttachmentsByCategory(client);
        this.loadGeneralDocuments(client.documents);
    },

    // Function to load form sections from API response
    loadFormSummaryFromAPI(sections) {
        const container = document.getElementById('formSectionsGrid');
        container.innerHTML = '';

        sections.forEach(section => {
            const sectionElement = document.createElement('div');
            sectionElement.className = `form-section ${section.completed ? 'completed' : 'incomplete'}`;
            sectionElement.innerHTML = `
                <div class="section-header">
                    <i class="fas ${section.icon}"></i>
                    <h6>${section.name}</h6>
                    <span class="completion-badge ${section.completed ? 'complete' : 'incomplete'}">
                        ${section.completed ? 'Complete' : 'Incomplete'}
                    </span>
                </div>
                <div class="section-details">
                    <small>${section.description}</small>
                    ${section.file_count > 0 ? `<div class="file-count"><i class="fas fa-file"></i> ${section.file_count} files</div>` : ''}
                </div>
            `;
            container.appendChild(sectionElement);
        });
    },

    // Function to load file attachments from API response
    loadFileAttachmentsByCategory(categorizedFiles) {
        const container = document.getElementById('fileCategories');
        container.innerHTML = '';

        // Handle both API response format and mock data format
        const filesData = typeof categorizedFiles === 'object' ? categorizedFiles : this.getCategorizedFiles({ id: this.currentClientId });

        Object.entries(filesData).forEach(([category, files]) => {
            if (files.length === 0) return;

            const categoryElement = document.createElement('div');
            categoryElement.className = 'file-category';
            categoryElement.innerHTML = `
                <div class="category-header">
                    <h6><i class="fas fa-folder"></i> ${category}</h6>
                    <span class="file-count-badge">${files.length} files</span>
                </div>
                <div class="category-files">
                    ${files.map(file => `
                        <div class="file-item">
                            <div class="file-info">
                                <i class="fas ${this.getFileIcon(file.type)}"></i>
                                <span class="file-name">${file.name}</span>
                                <span class="file-size">${file.size}</span>
                            </div>
                            <div class="file-actions">
                                <button class="btn-icon" onclick="AdminSystem.previewFile('${file.id}')" title="Preview">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn-icon" onclick="AdminSystem.downloadFile('${file.id}')" title="Download">
                                    <i class="fas fa-download"></i>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            container.appendChild(categoryElement);
        });

        if (Object.keys(filesData).length === 0) {
            container.innerHTML = '<div class="no-files-message">No categorized files found</div>';
        }
    },

    // Enhanced function to show form sections summary
    loadFormSummary(client) {
        const container = document.getElementById('formSectionsGrid');
        container.innerHTML = '';

        // Mock T1 form data - in real implementation, this would come from the backend
        const formSections = this.getClientFormSections(client);

        formSections.forEach(section => {
            const sectionElement = document.createElement('div');
            sectionElement.className = `form-section ${section.completed ? 'completed' : 'incomplete'}`;
            sectionElement.innerHTML = `
                <div class="section-header">
                    <i class="fas ${section.icon}"></i>
                    <h6>${section.name}</h6>
                    <span class="completion-badge ${section.completed ? 'complete' : 'incomplete'}">
                        ${section.completed ? 'Complete' : 'Incomplete'}
                    </span>
                </div>
                <div class="section-details">
                    <small>${section.description}</small>
                    ${section.fileCount > 0 ? `<div class="file-count"><i class="fas fa-file"></i> ${section.fileCount} files</div>` : ''}
                </div>
            `;
            container.appendChild(sectionElement);
        });
    },

    // Function to categorize and display files by form sections
    loadFileAttachmentsByCategory(client) {
        const container = document.getElementById('fileCategories');
        container.innerHTML = '';

        // Mock file categorization - in real implementation, this would come from the backend
        const categorizedFiles = this.getCategorizedFiles(client);

        Object.entries(categorizedFiles).forEach(([category, files]) => {
            if (files.length === 0) return;

            const categoryElement = document.createElement('div');
            categoryElement.className = 'file-category';
            categoryElement.innerHTML = `
                <div class="category-header">
                    <h6><i class="fas fa-folder"></i> ${category}</h6>
                    <span class="file-count-badge">${files.length} files</span>
                </div>
                <div class="category-files">
                    ${files.map(file => `
                        <div class="file-item">
                            <div class="file-info">
                                <i class="fas ${this.getFileIcon(file.type)}"></i>
                                <span class="file-name">${file.name}</span>
                                <span class="file-size">${file.size}</span>
                            </div>
                            <div class="file-actions">
                                <button class="btn-icon" onclick="AdminSystem.previewFile('${file.id}')" title="Preview">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn-icon" onclick="AdminSystem.downloadFile('${file.id}')" title="Download">
                                    <i class="fas fa-download"></i>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            container.appendChild(categoryElement);
        });

        if (Object.keys(categorizedFiles).length === 0) {
            container.innerHTML = '<div class="no-files-message">No categorized files found</div>';
        }
    },

    // Mock function to get client's form sections - replace with actual API call
    getClientFormSections(client) {
        // This would normally come from the T1 form data in the backend
        return [
            {
                name: 'Personal Information',
                icon: 'fa-user',
                completed: true,
                description: 'Basic personal details, SIN, address',
                fileCount: 2
            },
            {
                name: 'Employment Income',
                icon: 'fa-briefcase',
                completed: true,
                description: 'T4 slips, employment details',
                fileCount: 3
            },
            {
                name: 'Moving Expenses',
                icon: 'fa-truck',
                completed: client.id === 676, // Mock: only first client has moving expenses
                description: 'Moving receipts, travel expenses, company relocation',
                fileCount: client.id === 676 ? 5 : 0
            },
            {
                name: 'Self Employment',
                icon: 'fa-store',
                completed: client.id === 677, // Mock: second client is self-employed
                description: 'Business income, expenses, receipts',
                fileCount: client.id === 677 ? 8 : 0
            },
            {
                name: 'Medical Expenses',
                icon: 'fa-heart-pulse',
                completed: true,
                description: 'Medical receipts, insurance claims',
                fileCount: 1
            },
            {
                name: 'Charitable Donations',
                icon: 'fa-hand-holding-heart',
                completed: false,
                description: 'Donation receipts, charitable contributions',
                fileCount: 0
            },
            {
                name: 'Foreign Property',
                icon: 'fa-globe',
                completed: client.id === 679, // Mock: fourth client has foreign property
                description: 'Foreign income, property details',
                fileCount: client.id === 679 ? 3 : 0
            }
        ];
    },

    // Mock function to get categorized files - replace with actual API call
    getCategorizedFiles(client) {
        // This would normally come from the uploadedDocuments field in T1 form
        const mockFiles = {
            'Moving Expenses': client.id === 676 ? [
                { id: '1', name: 'moving_receipt_1.pdf', size: '2.3 MB', type: 'pdf' },
                { id: '2', name: 'travel_expenses.pdf', size: '1.8 MB', type: 'pdf' },
                { id: '3', name: 'company_relocation_letter.pdf', size: '856 KB', type: 'pdf' },
                { id: '4', name: 'new_address_proof.jpg', size: '1.2 MB', type: 'image' },
                { id: '5', name: 'distance_calculation.pdf', size: '445 KB', type: 'pdf' }
            ] : [],
            'Self Employment': client.id === 677 ? [
                { id: '6', name: 'business_income_2024.pdf', size: '3.1 MB', type: 'pdf' },
                { id: '7', name: 'expense_receipts.zip', size: '15.2 MB', type: 'zip' },
                { id: '8', name: 'client_invoices.pdf', size: '4.7 MB', type: 'pdf' },
                { id: '9', name: 'home_office_expenses.xlsx', size: '892 KB', type: 'excel' },
                { id: '10', name: 'vehicle_log.pdf', size: '1.1 MB', type: 'pdf' },
                { id: '11', name: 'business_license.jpg', size: '756 KB', type: 'image' },
                { id: '12', name: 'hst_returns.pdf', size: '2.3 MB', type: 'pdf' },
                { id: '13', name: 'bank_statements.pdf', size: '5.4 MB', type: 'pdf' }
            ] : [],
            'Employment Income': [
                { id: '14', name: 't4_slip_2024.pdf', size: '623 KB', type: 'pdf' },
                { id: '15', name: 'pay_stubs.pdf', size: '2.1 MB', type: 'pdf' },
                { id: '16', name: 'employment_letter.pdf', size: '445 KB', type: 'pdf' }
            ],
            'Medical Expenses': [
                { id: '17', name: 'medical_receipts_2024.pdf', size: '1.8 MB', type: 'pdf' }
            ],
            'Foreign Property': client.id === 679 ? [
                { id: '18', name: 'foreign_income_statement.pdf', size: '2.7 MB', type: 'pdf' },
                { id: '19', name: 'property_tax_receipt.pdf', size: '934 KB', type: 'pdf' },
                { id: '20', name: 'currency_conversion.xlsx', size: '567 KB', type: 'excel' }
            ] : []
        };

        // Filter out empty categories
        return Object.fromEntries(
            Object.entries(mockFiles).filter(([key, value]) => value.length > 0)
        );
    },

    // Get appropriate icon for file type
    getFileIcon(fileType) {
        const iconMap = {
            'pdf': 'fa-file-pdf text-red',
            'image': 'fa-file-image text-blue',
            'zip': 'fa-file-archive text-orange',
            'excel': 'fa-file-excel text-green',
            'word': 'fa-file-word text-blue',
            'default': 'fa-file text-gray'
        };
        return iconMap[fileType] || iconMap['default'];
    },

    // Enhanced file action handlers with real API integration
    async previewFile(fileId) {
        try {
            // First get file metadata
            const response = await this.fetchWithAuth(`/admin/api/v1/files/${fileId}/metadata`);
            if (!response || !response.ok) {
                throw new Error('Failed to get file metadata');
            }
            
            const fileInfo = await response.json();
            
            // For PDF files, show in iframe
            if (fileInfo.file_type.toLowerCase().includes('pdf')) {
                this.showPDFPreview(fileId, fileInfo.original_filename);
            } 
            // For images, show in image modal
            else if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].some(ext => fileInfo.file_type.toLowerCase().includes(ext))) {
                this.showImagePreview(fileId, fileInfo.original_filename);
            }
            // For other files, attempt to download
            else {
                this.downloadFile(fileId);
            }
        } catch (error) {
            console.error('Error previewing file:', error);
            this.showErrorMessage(`Error previewing file: ${error.message}`);
        }
    },

    async downloadFile(fileId) {
        try {
            this.showSuccessMessage('Preparing file download...');
            
            // Create download link
            const downloadUrl = `/admin/api/v1/files/${fileId}/download`;
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = '';
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            console.log('Download initiated for file:', fileId);
        } catch (error) {
            console.error('Error downloading file:', error);
            this.showErrorMessage(`Error downloading file: ${error.message}`);
        }
    },

    // Show PDF preview in modal
    showPDFPreview(fileId, filename) {
        const modal = document.createElement('div');
        modal.className = 'modal file-preview-modal';
        modal.innerHTML = `
            <div class="modal-content large-modal">
                <div class="modal-header">
                    <h3>PDF Preview: ${filename}</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <iframe src="/admin/api/v1/files/${fileId}/download" width="100%" height="600px"></iframe>
                </div>
                <div class="modal-actions">
                    <button class="btn btn-secondary" onclick="AdminSystem.downloadFile('${fileId}')">
                        <i class="fas fa-download"></i> Download
                    </button>
                    <button class="btn btn-primary" onclick="this.closest('.modal').remove()">
                        Close
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        modal.classList.add('active');
    },

    // Show image preview in modal
    showImagePreview(fileId, filename) {
        const modal = document.createElement('div');
        modal.className = 'modal file-preview-modal';
        modal.innerHTML = `
            <div class="modal-content large-modal">
                <div class="modal-header">
                    <h3>Image Preview: ${filename}</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <img src="/admin/api/v1/files/${fileId}/download" style="max-width: 100%; max-height: 600px;">
                </div>
                <div class="modal-actions">
                    <button class="btn btn-secondary" onclick="AdminSystem.downloadFile('${fileId}')">
                        <i class="fas fa-download"></i> Download
                    </button>
                    <button class="btn btn-primary" onclick="this.closest('.modal').remove()">
                        Close
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        modal.classList.add('active');
    },

    loadGeneralDocuments(documents) {
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
