/**
 * TaxEase T1 Form - Backend API Integration
 * This script handles form submission and authentication with the FastAPI backend
 */

// Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        REGISTER: '/api/v1/auth/register',
        LOGIN: '/api/v1/auth/login',
        ENCRYPTION_SETUP: '/api/v1/encryption/setup',
        T1_FORMS: '/api/v1/t1-forms/',
        T1_FORMS_BY_ID: (id) => `/api/v1/t1-forms/${id}`
    }
};

// Token Management
const TokenManager = {
    getToken() {
        return localStorage.getItem('access_token');
    },
    
    setToken(token) {
        localStorage.setItem('access_token', token);
    },
    
    getUserEmail() {
        return localStorage.getItem('user_email');
    },
    
    setUserEmail(email) {
        localStorage.setItem('user_email', email);
    },
    
    clear() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_email');
    },
    
    isAuthenticated() {
        return !!this.getToken();
    }
};

// API Helper Functions
const API = {
    async request(endpoint, options = {}) {
        const url = `${API_CONFIG.BASE_URL}${endpoint}`;
        const token = TokenManager.getToken();
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token && !options.skipAuth) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },
    
    async register(email, password, firstName, lastName, phone = null) {
        return this.request(API_CONFIG.ENDPOINTS.REGISTER, {
            method: 'POST',
            skipAuth: true,
            body: JSON.stringify({
                email,
                password,
                first_name: firstName,
                last_name: lastName,
                phone: phone,
                accept_terms: true
            })
        });
    },
    
    async login(email, password) {
        // Send JSON login data
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LOGIN}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }
        
        TokenManager.setToken(data.access_token);
        TokenManager.setUserEmail(email);
        
        return data;
    },
    
    async setupEncryption() {
        return this.request(API_CONFIG.ENDPOINTS.ENCRYPTION_SETUP, {
            method: 'POST'
        });
    },
    
    async createT1Form(formData) {
        return this.request(API_CONFIG.ENDPOINTS.T1_FORMS, {
            method: 'POST',
            body: JSON.stringify(formData)
        });
    },
    
    async updateT1Form(formId, formData) {
        return this.request(API_CONFIG.ENDPOINTS.T1_FORMS_BY_ID(formId), {
            method: 'PUT',
            body: JSON.stringify(formData)
        });
    },
    
    async getT1Form(formId) {
        return this.request(API_CONFIG.ENDPOINTS.T1_FORMS_BY_ID(formId), {
            method: 'GET'
        });
    }
};

// Form Data Collection Functions
const FormDataCollector = {
    // Helper to get input value safely
    getValue(selector) {
        const element = document.querySelector(selector);
        return element ? element.value.trim() : '';
    },
    
    // Helper to get radio button value
    getRadioValue(name) {
        const radio = document.querySelector(`input[name="${name}"]:checked`);
        return radio ? radio.value === 'yes' : false;
    },
    
    // Helper to get all values from a dynamic section
    getArrayFromSection(containerSelector, fieldMapping) {
        const container = document.querySelector(containerSelector);
        if (!container) return [];
        
        const rows = container.querySelectorAll('.dynamic-row');
        return Array.from(rows).map(row => {
            const data = {};
            Object.keys(fieldMapping).forEach(key => {
                const input = row.querySelector(fieldMapping[key]);
                if (input) {
                    data[key] = input.value.trim();
                }
            });
            return data;
        });
    },
    
    // Collect Personal Information
    collectPersonalInfo() {
        const personalInfo = {
            firstName: this.getValue('input[placeholder="First Name (Individual)"]'),
            middleName: this.getValue('input[placeholder="Middle Name (Individual)"]'),
            lastName: this.getValue('input[placeholder="Last Name (Individual)"]'),
            sin: this.getValue('input[placeholder="Individual SIN"]'),
            dateOfBirth: this.getValue('input[type="date"]'),
            address: this.getValue('input[placeholder="Individual Address"]'),
            phoneNumber: this.getValue('input[placeholder="Individual Phone"]'),
            email: this.getValue('input[placeholder="Individual Email"]'),
            isCanadianCitizen: this.getRadioValue('canadianCitizen'),
            maritalStatus: this.getValue('#maritalStatus')
        };
        
        // Add spouse info if applicable
        const maritalStatus = this.getValue('#maritalStatus');
        if (['married', 'common_law'].includes(maritalStatus)) {
            const spouseDetails = document.querySelector('#spouseDetails');
            if (spouseDetails && spouseDetails.style.display !== 'none') {
                personalInfo.spouseInfo = {
                    firstName: spouseDetails.querySelector('input[placeholder*="First Name"]')?.value || '',
                    middleName: spouseDetails.querySelector('input[placeholder*="Middle Name"]')?.value || '',
                    lastName: spouseDetails.querySelector('input[placeholder*="Last Name"]')?.value || '',
                    sin: spouseDetails.querySelector('input[placeholder*="SIN"]')?.value || '',
                    dateOfBirth: spouseDetails.querySelector('input[type="date"]')?.value || ''
                };
            }
        }
        
        // Add children if any
        const childrenContainer = document.querySelector('#childrenContainer');
        if (childrenContainer) {
            const childRows = childrenContainer.querySelectorAll('.child-row');
            if (childRows.length > 0) {
                personalInfo.children = Array.from(childRows).map(row => ({
                    firstName: row.querySelector('input[placeholder*="First Name"]')?.value || '',
                    middleName: row.querySelector('input[placeholder*="Middle Name"]')?.value || '',
                    lastName: row.querySelector('input[placeholder*="Last Name"]')?.value || '',
                    sin: row.querySelector('input[placeholder*="SIN"]')?.value || '',
                    dateOfBirth: row.querySelector('input[type="date"]')?.value || ''
                }));
            }
        }
        
        return personalInfo;
    },
    
    // Collect Foreign Property Details
    collectForeignProperty() {
        const hasForeignProperty = this.getRadioValue('foreignProperty');
        if (!hasForeignProperty) {
            return { hasForeignProperty: false, foreignProperties: [] };
        }
        
        const foreignProperties = [];
        const container = document.querySelector('#foreignPropertyDetails');
        if (container) {
            const rows = container.querySelectorAll('.foreign-property-row');
            rows.forEach(row => {
                foreignProperties.push({
                    investmentDetails: row.querySelector('input[placeholder*="Investment Details"]')?.value || '',
                    grossIncome: parseFloat(row.querySelector('input[placeholder*="Gross Income"]')?.value) || 0,
                    gainLossOnSale: parseFloat(row.querySelector('input[placeholder*="Gain/Loss"]')?.value) || 0,
                    maxCostDuringYear: parseFloat(row.querySelector('input[placeholder*="Max Cost"]')?.value) || 0,
                    costAmountYearEnd: parseFloat(row.querySelector('input[placeholder*="Cost Amount"]')?.value) || 0,
                    country: row.querySelector('input[placeholder*="Country"]')?.value || ''
                });
            });
        }
        
        return { hasForeignProperty, foreignProperties };
    },
    
    // Collect Moving Expenses
    collectMovingExpenses() {
        const hasMovingExpenses = this.getRadioValue('movingExpenses');
        if (!hasMovingExpenses) {
            return { hasMovingExpenses: false };
        }
        
        const dateOfMove = this.getValue('#dateOfMove');
        const movingExpenseData = { hasMovingExpenses, dateOfMove };
        
        // Check if individual moving expenses exist
        const individualCheckbox = document.querySelector('input[name="movingExpenseIndividual"]:checked');
        if (individualCheckbox) {
            movingExpenseData.movingExpenseForIndividual = true;
            movingExpenseData.movingExpenseIndividual = this.collectMovingExpenseDetails('individual');
        }
        
        // Check if spouse moving expenses exist
        const spouseCheckbox = document.querySelector('input[name="movingExpenseSpouse"]:checked');
        if (spouseCheckbox) {
            movingExpenseData.movingExpenseForSpouse = true;
            movingExpenseData.movingExpenseSpouse = this.collectMovingExpenseDetails('spouse');
        }
        
        return movingExpenseData;
    },
    
    collectMovingExpenseDetails(type) {
        const prefix = type === 'individual' ? 'individual' : 'spouse';
        return {
            individual: this.getValue(`#${prefix}MovingName`),
            oldAddress: this.getValue(`#${prefix}OldAddress`),
            newAddress: this.getValue(`#${prefix}NewAddress`),
            distanceFromOldToNew: this.getValue(`#${prefix}DistanceOldNew`),
            distanceFromNewToOffice: this.getValue(`#${prefix}DistanceNewOffice`),
            airTicketCost: parseFloat(this.getValue(`#${prefix}AirTicket`)) || 0,
            moversAndPackers: parseFloat(this.getValue(`#${prefix}Movers`)) || 0,
            mealsAndOtherCost: parseFloat(this.getValue(`#${prefix}Meals`)) || 0,
            anyOtherCost: parseFloat(this.getValue(`#${prefix}OtherCost`)) || 0,
            dateOfTravel: this.getValue(`#${prefix}TravelDate`),
            dateOfJoining: this.getValue(`#${prefix}JoiningDate`),
            companyName: this.getValue(`#${prefix}CompanyName`),
            newEmployerAddress: this.getValue(`#${prefix}EmployerAddress`),
            grossIncomeAfterMoving: parseFloat(this.getValue(`#${prefix}GrossIncome`)) || 0
        };
    },
    
    // Collect Self Employment Details
    collectSelfEmployment() {
        const isSelfEmployed = this.getRadioValue('selfEmployed');
        if (!isSelfEmployed) {
            return { isSelfEmployed: false };
        }
        
        const businessType = document.querySelector('input[name="businessType"]:checked')?.value;
        const selfEmployment = {
            businessTypes: businessType ? [businessType] : []
        };
        
        if (businessType === 'uber') {
            selfEmployment.uberBusiness = this.collectUberBusiness();
        } else if (businessType === 'general') {
            selfEmployment.generalBusiness = this.collectGeneralBusiness();
        } else if (businessType === 'rental') {
            selfEmployment.rentalIncome = this.collectRentalIncome();
        }
        
        return { isSelfEmployed, selfEmployment };
    },
    
    collectUberBusiness() {
        const section = document.querySelector('#uberSkipDoordashSection');
        if (!section) return {};
        
        return {
            uberSkipStatement: section.querySelector('#uberStatement')?.value || '',
            businessHstNumber: section.querySelector('#uberHstNumber')?.value || '',
            hstAccessCode: section.querySelector('#uberHstAccessCode')?.value || '',
            hstFillingPeriod: section.querySelector('#uberHstPeriod')?.value || '',
            income: parseFloat(section.querySelector('#uberIncome')?.value) || 0,
            totalKmForUberSkip: parseFloat(section.querySelector('#uberTotalKm')?.value) || 0,
            totalOfficialKmDriven: parseFloat(section.querySelector('#uberOfficialKm')?.value) || 0,
            totalKmDrivenEntireYear: parseFloat(section.querySelector('#uberYearKm')?.value) || 0,
            businessNumberVehicleRegistration: parseFloat(section.querySelector('#uberVehicleReg')?.value) || 0,
            meals: parseFloat(section.querySelector('#uberMeals')?.value) || 0,
            telephone: parseFloat(section.querySelector('#uberTelephone')?.value) || 0,
            parkingFees: parseFloat(section.querySelector('#uberParking')?.value) || 0,
            cleaningExpenses: parseFloat(section.querySelector('#uberCleaning')?.value) || 0,
            safetyInspection: parseFloat(section.querySelector('#uberSafety')?.value) || 0,
            winterTireChange: parseFloat(section.querySelector('#uberTires')?.value) || 0,
            oilChangeAndMaintenance: parseFloat(section.querySelector('#uberMaintenance')?.value) || 0,
            depreciation: parseFloat(section.querySelector('#uberDepreciation')?.value) || 0,
            insuranceOnVehicle: parseFloat(section.querySelector('#uberInsurance')?.value) || 0,
            gas: parseFloat(section.querySelector('#uberGas')?.value) || 0,
            financingCostInterest: parseFloat(section.querySelector('#uberFinancing')?.value) || 0,
            leaseCost: parseFloat(section.querySelector('#uberLease')?.value) || 0,
            otherExpense: parseFloat(section.querySelector('#uberOther')?.value) || 0
        };
    },
    
    collectGeneralBusiness() {
        const section = document.querySelector('#generalBusinessSection');
        if (!section) return {};
        
        return {
            clientName: section.querySelector('#generalClientName')?.value || '',
            businessName: section.querySelector('#generalBusinessName')?.value || '',
            salesCommissionsFees: parseFloat(section.querySelector('#generalSales')?.value) || 0,
            minusHstCollected: parseFloat(section.querySelector('#generalHst')?.value) || 0,
            grossIncome: parseFloat(section.querySelector('#generalGrossIncome')?.value) || 0,
            advertising: parseFloat(section.querySelector('#generalAdvertising')?.value) || 0,
            mealsEntertainment: parseFloat(section.querySelector('#generalMeals')?.value) || 0,
            insurance: parseFloat(section.querySelector('#generalInsurance')?.value) || 0,
            officeExpenses: parseFloat(section.querySelector('#generalOffice')?.value) || 0,
            supplies: parseFloat(section.querySelector('#generalSupplies')?.value) || 0,
            legalAccountingFees: parseFloat(section.querySelector('#generalLegal')?.value) || 0,
            travel: parseFloat(section.querySelector('#generalTravel')?.value) || 0,
            telephoneUtilities: parseFloat(section.querySelector('#generalTelephone')?.value) || 0,
            // Office in house
            areaOfHomeForBusiness: section.querySelector('#generalHomeArea')?.value || '',
            totalAreaOfHome: section.querySelector('#generalTotalArea')?.value || '',
            heat: parseFloat(section.querySelector('#generalHeat')?.value) || 0,
            electricity: parseFloat(section.querySelector('#generalElectricity')?.value) || 0,
            houseInsurance: parseFloat(section.querySelector('#generalHouseInsurance')?.value) || 0,
            homeMaintenance: parseFloat(section.querySelector('#generalHomeMaintenance')?.value) || 0,
            mortgageInterest: parseFloat(section.querySelector('#generalMortgage')?.value) || 0,
            houseRent: parseFloat(section.querySelector('#generalRent')?.value) || 0,
            // Motor vehicle
            kmDrivenForBusiness: parseFloat(section.querySelector('#generalBusinessKm')?.value) || 0,
            totalKmDrivenInYear: parseFloat(section.querySelector('#generalTotalKm')?.value) || 0,
            vehicleFuel: parseFloat(section.querySelector('#generalFuel')?.value) || 0,
            vehicleInsurance: parseFloat(section.querySelector('#generalVehicleInsurance')?.value) || 0,
            vehicleMaintenance: parseFloat(section.querySelector('#generalVehicleMaintenance')?.value) || 0
        };
    },
    
    collectRentalIncome() {
        const section = document.querySelector('#rentalIncomeSection');
        if (!section) return {};
        
        return {
            propertyAddress: section.querySelector('#rentalAddress')?.value || '',
            coOwnerPartner1: section.querySelector('#rentalCoOwner1')?.value || '',
            coOwnerPartner2: section.querySelector('#rentalCoOwner2')?.value || '',
            coOwnerPartner3: section.querySelector('#rentalCoOwner3')?.value || '',
            numberOfUnits: parseInt(section.querySelector('#rentalUnits')?.value) || 0,
            grossRentalIncome: parseFloat(section.querySelector('#rentalGrossIncome')?.value) || 0,
            anyGovtIncomeRelatingToRental: parseFloat(section.querySelector('#rentalGovtIncome')?.value) || 0,
            personalUsePortion: section.querySelector('#rentalPersonalUse')?.value || '',
            houseInsurance: parseFloat(section.querySelector('#rentalInsurance')?.value) || 0,
            mortgageInterest: parseFloat(section.querySelector('#rentalMortgage')?.value) || 0,
            propertyTaxes: parseFloat(section.querySelector('#rentalPropertyTax')?.value) || 0,
            utilities: parseFloat(section.querySelector('#rentalUtilities')?.value) || 0,
            managementAdminFees: parseFloat(section.querySelector('#rentalManagement')?.value) || 0,
            repairAndMaintenance: parseFloat(section.querySelector('#rentalRepair')?.value) || 0,
            cleaningExpense: parseFloat(section.querySelector('#rentalCleaning')?.value) || 0,
            motorVehicleExpenses: parseFloat(section.querySelector('#rentalVehicle')?.value) || 0,
            legalProfessionalFees: parseFloat(section.querySelector('#rentalLegal')?.value) || 0,
            advertisingPromotion: parseFloat(section.querySelector('#rentalAdvertising')?.value) || 0,
            otherExpense: parseFloat(section.querySelector('#rentalOther')?.value) || 0,
            purchasePrice: parseFloat(section.querySelector('#rentalPurchasePrice')?.value) || 0,
            purchaseDate: section.querySelector('#rentalPurchaseDate')?.value || '',
            additionDeletionAmount: parseFloat(section.querySelector('#rentalAdditionDeletion')?.value) || 0
        };
    },
    
    // Collect all questionnaire responses
    collectQuestionnaireData() {
        return {
            // Q1: Foreign Property (already collected above)
            // Q2: Medical Expenses
            hasMedicalExpenses: this.getRadioValue('medicalExpenses'),
            // Q3: Charitable Donations
            hasCharitableDonations: this.getRadioValue('charitableDonations'),
            // Q4: Moving Expenses (already collected above)
            // Q5: Self Employment (already collected above)
            // Q6: First Home Buyer
            isFirstHomeBuyer: this.getRadioValue('firstHomeBuyer'),
            // Q7: Sold Property Long Term
            soldPropertyLongTerm: this.getRadioValue('soldPropertyLong'),
            // Q8: Sold Property Short Term
            soldPropertyShortTerm: this.getRadioValue('soldPropertyShort'),
            // Q9: Work From Home Expense
            hasWorkFromHomeExpense: this.getRadioValue('wfhExpense'),
            // Q10: Student Last Year
            wasStudentLastYear: this.getRadioValue('studentLastYear'),
            // Q11: Union Member
            isUnionMember: this.getRadioValue('unionMember'),
            // Q12: Daycare Expenses
            hasDaycareExpenses: this.getRadioValue('daycareExpenses'),
            // Q13: First Time Filer
            isFirstTimeFiler: this.getRadioValue('firstTimeFiler'),
            // Q14: Other Income
            hasOtherIncome: this.getRadioValue('otherIncome'),
            otherIncomeDescription: this.getValue('#otherIncomeDescription'),
            // Q15: Professional Dues
            hasProfessionalDues: this.getRadioValue('professionalDues'),
            // Q16: RRSP/FHSA Investment
            hasRrspFhsaInvestment: this.getRadioValue('rrspInvestment'),
            // Q17: Child Art & Sport Credit
            hasChildArtSportCredit: this.getRadioValue('childArtSport'),
            // Q18: Province Filer
            isProvinceFiler: this.getRadioValue('provinceFiler')
        };
    },
    
    // Main function to collect all form data
    collectAllData() {
        const personalInfo = this.collectPersonalInfo();
        const foreignProperty = this.collectForeignProperty();
        const movingExpenses = this.collectMovingExpenses();
        const selfEmployment = this.collectSelfEmployment();
        const questionnaire = this.collectQuestionnaireData();
        
        return {
            status: 'draft', // Can be 'draft', 'submitted', 'approved', 'rejected'
            personalInfo,
            ...foreignProperty,
            ...movingExpenses,
            ...selfEmployment,
            ...questionnaire
        };
    }
};

// Form Submission Handler
const FormHandler = {
    async initialize() {
        // Check if user is authenticated
        if (!TokenManager.isAuthenticated()) {
            this.showAuthModal();
        } else {
            // Optionally setup encryption if not done
            try {
                await API.setupEncryption();
                console.log('Encryption setup confirmed');
            } catch (error) {
                console.log('Encryption may already be set up:', error.message);
            }
        }
        
        // Attach form submit handler
        const form = document.getElementById('multiStepForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    },
    
    showAuthModal() {
        // Show login/register modal
        alert('Please login or register to save your form data.');
        // You can implement a proper modal here
    },
    
    async handleSubmit(event) {
        event.preventDefault();
        
        if (!TokenManager.isAuthenticated()) {
            this.showAuthModal();
            return;
        }
        
        try {
            // Show loading indicator
            this.showLoading(true);
            
            // Collect form data
            const formData = FormDataCollector.collectAllData();
            
            console.log('Submitting form data:', formData);
            
            // Submit to backend
            const response = await API.createT1Form(formData);
            
            console.log('Form submitted successfully:', response);
            
            // Show success message
            this.showSuccess(`Form saved successfully! Form ID: ${response.form_id}`);
            
            // Optionally redirect or clear form
            // window.location.href = '/success.html';
            
        } catch (error) {
            console.error('Form submission error:', error);
            this.showError(`Failed to submit form: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    },
    
    showLoading(show) {
        let loader = document.getElementById('formLoader');
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'formLoader';
            loader.className = 'alert alert-info';
            loader.innerHTML = '<strong>Loading...</strong> Please wait while we save your data.';
            loader.style.display = 'none';
            document.querySelector('.container').prepend(loader);
        }
        loader.style.display = show ? 'block' : 'none';
    },
    
    showSuccess(message) {
        this.showMessage(message, 'success');
    },
    
    showError(message) {
        this.showMessage(message, 'danger');
    },
    
    showMessage(message, type) {
        let messageDiv = document.getElementById('formMessage');
        if (!messageDiv) {
            messageDiv = document.createElement('div');
            messageDiv.id = 'formMessage';
            document.querySelector('.container').prepend(messageDiv);
        }
        messageDiv.className = `alert alert-${type}`;
        messageDiv.textContent = message;
        messageDiv.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
};

// Authentication UI Functions
const AuthUI = {
    showLoginForm() {
        const html = `
            <div class="modal fade" id="authModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Login / Register</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <ul class="nav nav-tabs" role="tablist">
                                <li class="nav-item">
                                    <a class="nav-link active" data-bs-toggle="tab" href="#loginTab">Login</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" data-bs-toggle="tab" href="#registerTab">Register</a>
                                </li>
                            </ul>
                            <div class="tab-content mt-3">
                                <div id="loginTab" class="tab-pane fade show active">
                                    <form id="loginForm">
                                        <div class="mb-3">
                                            <label class="form-label">Email</label>
                                            <input type="email" class="form-control" id="loginEmail" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Password</label>
                                            <input type="password" class="form-control" id="loginPassword" required>
                                        </div>
                                        <button type="submit" class="btn btn-primary">Login</button>
                                    </form>
                                </div>
                                <div id="registerTab" class="tab-pane fade">
                                    <form id="registerForm">
                                        <div class="mb-3">
                                            <label class="form-label">Full Name</label>
                                            <input type="text" class="form-control" id="registerName" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Email</label>
                                            <input type="email" class="form-control" id="registerEmail" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Password</label>
                                            <input type="password" class="form-control" id="registerPassword" required>
                                        </div>
                                        <button type="submit" class="btn btn-primary">Register</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', html);
        
        // Attach event listeners
        document.getElementById('loginForm').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('registerForm').addEventListener('submit', (e) => this.handleRegister(e));
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('authModal'));
        modal.show();
    },
    
    async handleLogin(event) {
        event.preventDefault();
        
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        try {
            await API.login(email, password);
            alert('Login successful!');
            bootstrap.Modal.getInstance(document.getElementById('authModal')).hide();
            
            // Setup encryption
            await API.setupEncryption();
        } catch (error) {
            alert('Login failed: ' + error.message);
        }
    },
    
    async handleRegister(event) {
        event.preventDefault();
        
        const fullName = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        
        // Split name into first and last
        const nameParts = fullName.trim().split(' ');
        const firstName = nameParts[0] || 'User';
        const lastName = nameParts.slice(1).join(' ') || 'Account';
        
        try {
            await API.register(email, password, firstName, lastName);
            alert('Registration successful! Please login.');
            
            // Switch to login tab
            document.querySelector('a[href="#loginTab"]').click();
        } catch (error) {
            alert('Registration failed: ' + error.message);
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    FormHandler.initialize();
    
    // Add login button to navbar if not authenticated
    if (!TokenManager.isAuthenticated()) {
        // You can add a login button to your navbar here
        console.log('User not authenticated. Please login.');
    }
});

// Export for use in other scripts if needed
window.TaxEaseAPI = {
    API,
    TokenManager,
    FormDataCollector,
    FormHandler,
    AuthUI
};
