/**
 * T1 Form API Integration
 * Connects the T1 tax form to the TaxEase backend API
 */

// API Configuration
const API_CONFIG = {
    baseURL: 'http://localhost:8000',
    endpoints: {
        register: '/api/v1/auth/register',
        login: '/api/v1/auth/login',
        me: '/api/v1/auth/me',
        health: '/health',
        t1Forms: '/api/v1/t1-forms',
        createT1Form: '/api/v1/t1-forms/',
        listT1Forms: '/api/v1/t1-forms/',
        getT1Form: '/api/v1/t1-forms/',
        updateT1Form: '/api/v1/t1-forms/',
        deleteT1Form: '/api/v1/t1-forms/'
    }
};

// Token Manager
const TokenManager = {
    getToken() {
        return localStorage.getItem('taxease_token');
    },
    
    setToken(token) {
        localStorage.setItem('taxease_token', token);
    },
    
    clearToken() {
        localStorage.removeItem('taxease_token');
    },
    
    isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;
        
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp * 1000 > Date.now();
        } catch {
            return false;
        }
    }
};

// API Helper
const API = {
    async request(endpoint, options = {}) {
        const url = API_CONFIG.baseURL + endpoint;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        const token = TokenManager.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    },
    
    async login(email, password) {
        const result = await this.request(API_CONFIG.endpoints.login, {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (result.access_token) {
            TokenManager.setToken(result.access_token);
        }
        
        return result;
    },
    
    async register(userData) {
        return await this.request(API_CONFIG.endpoints.register, {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },
    
    async getCurrentUser() {
        return await this.request(API_CONFIG.endpoints.me);
    },
    
    async createT1Form(formData) {
        return await this.request(API_CONFIG.endpoints.createT1Form, {
            method: 'POST',
            body: JSON.stringify(formData)
        });
    },
    
    async listT1Forms() {
        return await this.request(API_CONFIG.endpoints.listT1Forms);
    },
    
    async getT1Form(formId) {
        return await this.request(API_CONFIG.endpoints.getT1Form + formId);
    },
    
    async updateT1Form(formId, formData) {
        return await this.request(API_CONFIG.endpoints.updateT1Form + formId, {
            method: 'PUT',
            body: JSON.stringify(formData)
        });
    },
    
    async deleteT1Form(formId) {
        return await this.request(API_CONFIG.endpoints.deleteT1Form + formId, {
            method: 'DELETE'
        });
    }
};

// Form Data Collector
const FormDataCollector = {
    collectPersonalInfo() {
        const form = document.getElementById('multiStepForm');
        
        // Personal Information
        const personalInfo = {
            firstName: form.querySelector('input[placeholder="First Name (Individual)"]')?.value || '',
            middleName: form.querySelector('input[placeholder="Middle Name (Individual)"]')?.value || '',
            lastName: form.querySelector('input[placeholder="Last Name (Individual)"]')?.value || '',
            sin: form.querySelector('input[placeholder="Individual SIN"]')?.value || '',
            dateOfBirth: form.querySelector('input[type="date"]')?.value || null,
            address: form.querySelector('input[placeholder="Individual Address"]')?.value || '',
            phoneNumber: form.querySelector('input[placeholder="Individual Phone"]')?.value || '',
            email: form.querySelector('input[placeholder="Individual Email"]')?.value || '',
            isCanadianCitizen: form.querySelector('input[name="canadianCitizen"]:checked')?.value === 'yes',
            maritalStatus: form.querySelector('#maritalStatus')?.value || ''
        };
        
        // Spouse Information (if married/common-law)
        const spouseDetails = document.getElementById('spouseDetails');
        if (spouseDetails && spouseDetails.style.display !== 'none') {
            personalInfo.spouseInfo = {
                firstName: form.querySelector('input[placeholder="First Name (Spouse)"]')?.value || '',
                middleName: form.querySelector('input[placeholder="Middle Name (Spouse)"]')?.value || '',
                lastName: form.querySelector('input[placeholder="Last Name (Spouse)"]')?.value || '',
                sin: form.querySelector('input[placeholder="Spouse SIN"]')?.value || '',
                dateOfBirth: spouseDetails.querySelector('input[type="date"]')?.value || null
            };
        }
        
        // Children Information
        const childrenContainer = document.getElementById('childrenContainer');
        const children = [];
        if (childrenContainer) {
            const childEntries = childrenContainer.querySelectorAll('.child-entry');
            childEntries.forEach(entry => {
                children.push({
                    firstName: entry.querySelector('input[placeholder*="First Name (Child"]')?.value || '',
                    middleName: entry.querySelector('input[placeholder*="Middle Name (Child"]')?.value || '',
                    lastName: entry.querySelector('input[placeholder*="Last Name (Child"]')?.value || '',
                    sin: entry.querySelector('input[placeholder*="Child"][placeholder*="SIN"]')?.value || '',
                    dateOfBirth: entry.querySelector('input[type="date"]')?.value || null
                });
            });
        }
        personalInfo.children = children;
        
        return personalInfo;
    },
    
    collectQuestionnaire() {
        const form = document.getElementById('multiStepForm');
        const questionnaire = {};
        
        // Question responses
        questionnaire.hasForeignProperty = form.querySelector('input[name="foreignProperty"]:checked')?.value === 'yes';
        questionnaire.hasMedicalExpenses = form.querySelector('input[name="medicalExpenses"]:checked')?.value === 'yes';
        questionnaire.hasCharitableDonations = form.querySelector('input[name="charitableDonations"]:checked')?.value === 'yes';
        questionnaire.hasMovingExpenses = form.querySelector('input[name="movingExpenses"]:checked')?.value === 'yes';
        questionnaire.isSelfEmployed = form.querySelector('input[name="selfEmployed"]:checked')?.value === 'yes';
        questionnaire.isFirstHomeBuyer = form.querySelector('input[name="firstHomeBuyer"]:checked')?.value === 'yes';
        questionnaire.soldPropertyLongTerm = form.querySelector('input[name="soldPropertyLong"]:checked')?.value === 'yes';
        questionnaire.soldPropertyShortTerm = form.querySelector('input[name="soldPropertyShort"]:checked')?.value === 'yes';
        questionnaire.hasWorkFromHomeExpense = form.querySelector('input[name="wfhExpense"]:checked')?.value === 'yes';
        questionnaire.wasStudentLastYear = form.querySelector('input[name="studentLastYear"]:checked')?.value === 'yes';
        questionnaire.isUnionMember = form.querySelector('input[name="unionMember"]:checked')?.value === 'yes';
        questionnaire.hasDaycareExpenses = form.querySelector('input[name="daycareExpenses"]:checked')?.value === 'yes';
        questionnaire.isFirstTimeFiler = form.querySelector('input[name="firstTimeFiler"]:checked')?.value === 'yes';
        questionnaire.hasOtherIncome = form.querySelector('input[name="otherIncome"]:checked')?.value === 'yes';
        questionnaire.hasProfessionalDues = form.querySelector('input[name="professionalDues"]:checked')?.value === 'yes';
        questionnaire.hasRrspFhsaInvestment = form.querySelector('input[name="rrspFhsaInvestment"]:checked')?.value === 'yes';
        questionnaire.hasChildArtSportCredit = form.querySelector('input[name="childArtSportCredit"]:checked')?.value === 'yes';
        questionnaire.isProvinceFiler = form.querySelector('input[name="provinceFiler"]:checked')?.value === 'yes';
        
        // Collect detailed data for conditional sections
        if (questionnaire.hasOtherIncome) {
            const otherIncomeDetails = document.getElementById('otherIncomeDetails');
            if (otherIncomeDetails && otherIncomeDetails.style.display !== 'none') {
                questionnaire.otherIncomeDescription = otherIncomeDetails.querySelector('textarea')?.value || '';
            }
        }
        
        // Collect moving expenses details
        if (questionnaire.hasMovingExpenses) {
            questionnaire.dateOfMove = form.querySelector('#dateOfMove')?.value || null;
            const movingDetails = document.getElementById('movingExpenseDetails');
            if (movingDetails && movingDetails.style.display !== 'none') {
                questionnaire.movingExpenseDetails = this.collectMovingExpenseDetails(movingDetails);
            }
        }
        
        // Collect self-employment details
        if (questionnaire.isSelfEmployed) {
            const selfEmployedDetails = document.getElementById('selfEmployedDetails');
            if (selfEmployedDetails && selfEmployedDetails.style.display !== 'none') {
                questionnaire.selfEmploymentDetails = this.collectSelfEmploymentDetails(selfEmployedDetails);
            }
        }
        
        // Collect property sale details
        if (questionnaire.soldPropertyLongTerm) {
            const propertyDetails = document.getElementById('soldPropertyLongDetails');
            if (propertyDetails && propertyDetails.style.display !== 'none') {
                questionnaire.soldPropertyLongDetails = this.collectPropertySaleDetails(propertyDetails);
            }
        }
        
        if (questionnaire.soldPropertyShortTerm) {
            const propertyDetails = document.getElementById('soldPropertyShortDetails');
            if (propertyDetails && propertyDetails.style.display !== 'none') {
                questionnaire.soldPropertyShortDetails = this.collectPropertySaleDetails(propertyDetails);
            }
        }
        
        // Collect work from home details
        if (questionnaire.hasWorkFromHomeExpense) {
            const wfhDetails = document.getElementById('wfhExpenseDetails');
            if (wfhDetails && wfhDetails.style.display !== 'none') {
                questionnaire.workFromHomeDetails = this.collectWorkFromHomeDetails(wfhDetails);
            }
        }
        
        // Collect first time filer details
        if (questionnaire.isFirstTimeFiler) {
            const firstTimeFilerDetails = document.getElementById('firstTimeFilerDetails');
            if (firstTimeFilerDetails && firstTimeFilerDetails.style.display !== 'none') {
                questionnaire.firstTimeFilerDetails = this.collectFirstTimeFilerDetails(firstTimeFilerDetails);
            }
        }
        
        return questionnaire;
    },
    
    collectMovingExpenseDetails(container) {
        return {
            oldAddressIndividual: container.querySelector('input[placeholder="Individual Old Address"]')?.value || '',
            oldAddressSpouse: container.querySelector('input[placeholder="Spouse Old Address"]')?.value || '',
            newAddressIndividual: container.querySelector('input[placeholder="Individual New Address"]')?.value || '',
            newAddressSpouse: container.querySelector('input[placeholder="Spouse New Address"]')?.value || '',
            distanceOldToNewOfficeIndividual: parseFloat(container.querySelector('input[placeholder*="Distance from old address to New office"][placeholder*="Individual"]')?.value) || 0,
            distanceOldToNewOfficeSpouse: parseFloat(container.querySelector('input[placeholder*="Distance from old address to New office"][placeholder*="Spouse"]')?.value) || 0,
            distanceNewToNewOfficeIndividual: parseFloat(container.querySelector('input[placeholder*="Distance from new address to New office"][placeholder*="Individual"]')?.value) || 0,
            distanceNewToNewOfficeSpouse: parseFloat(container.querySelector('input[placeholder*="Distance from new address to New office"][placeholder*="Spouse"]')?.value) || 0,
            airTicketCost: parseFloat(container.querySelector('input[placeholder*="Air ticket cost"]')?.value) || 0,
            moversPackersCost: parseFloat(container.querySelector('input[placeholder*="Movers and packers cost"]')?.value) || 0,
            mealsOtherCost: parseFloat(container.querySelector('input[placeholder*="Meals and other cost"]')?.value) || 0,
            anyOtherCost: parseFloat(container.querySelector('input[placeholder*="Any other cost"]')?.value) || 0,
            dateOfTravel: container.querySelector('input[placeholder*="Date of Travel"]')?.value || null,
            dateOfJoining: container.querySelector('input[placeholder*="Date of joining"]')?.value || null,
            companyName: container.querySelector('input[placeholder*="Name of the company"]')?.value || '',
            newEmployerAddress: container.querySelector('input[placeholder*="Address of New Employer"]')?.value || '',
            grossIncomeAfterMoving: parseFloat(container.querySelector('input[placeholder*="Gross income earned"]')?.value) || 0
        };
    },
    
    collectSelfEmploymentDetails(container) {
        const businessType = container.querySelector('input[name="businessType"]:checked')?.value || '';
        const details = { businessType };
        
        if (businessType === 'uber') {
            const uberSection = document.getElementById('uberSkipDoordashSection');
            if (uberSection && uberSection.style.display !== 'none') {
                details.uberDetails = this.collectUberDetails(uberSection);
            }
        } else if (businessType === 'general') {
            const generalSection = document.getElementById('generalBusinessSection');
            if (generalSection && generalSection.style.display !== 'none') {
                details.generalBusinessDetails = this.collectGeneralBusinessDetails(generalSection);
            }
        } else if (businessType === 'rental') {
            const rentalSection = document.getElementById('rentalIncomeSection');
            if (rentalSection && rentalSection.style.display !== 'none') {
                details.rentalDetails = this.collectRentalDetails(rentalSection);
            }
        }
        
        return details;
    },
    
    collectUberDetails(container) {
        return {
            uberSkipStatement: container.querySelector('input[placeholder*="provide a link"]')?.value || '',
            businessHstNumber: container.querySelector('input[placeholder*="Business"][placeholder*="HST"]')?.value || '',
            hstAccessCode: container.querySelector('input[placeholder*="HST Access Code"]')?.value || '',
            hstFillingPeriod: container.querySelector('input[placeholder*="HST Filling Period"]')?.value || '',
            basicIncome: parseFloat(container.querySelector('label:contains("Basic Income") + input')?.value) || 0,
            hst: parseFloat(container.querySelector('label:contains("HST") + input')?.value) || 0,
            totalKmForUber: parseFloat(container.querySelector('input[placeholder*="Total KM Travelled for Uber"]')?.value) || 0,
            totalOfficialKm: parseFloat(container.querySelector('input[placeholder*="Total Official KM driven"]')?.value) || 0,
            totalKmEntireYear: parseFloat(container.querySelector('input[placeholder*="Total KM driven for Entire Year"]')?.value) || 0
        };
    },
    
    collectGeneralBusinessDetails(container) {
        return {
            clientName: container.querySelector('input[placeholder*="Client Name"]')?.value || '',
            businessName: container.querySelector('input[placeholder*="Business Name"]')?.value || '',
            salesCommissionsFees: parseFloat(container.querySelector('input[placeholder*="Sales, Commissions"]')?.value) || 0,
            minusHstCollected: parseFloat(container.querySelector('input[placeholder*="Minus: HST collected"]')?.value) || 0,
            areaOfHomeForBusiness: parseFloat(container.querySelector('input[placeholder*="Area of home used for business"]')?.value) || 0,
            totalAreaOfHome: parseFloat(container.querySelector('input[placeholder*="Total area of the home"]')?.value) || 0,
            kmDrivenForBusiness: parseFloat(container.querySelector('input[placeholder*="Kilometers driven to earn business"]')?.value) || 0,
            totalKmDrivenInYear: parseFloat(container.querySelector('input[placeholder*="Total Kilometers driven in the tax year"]')?.value) || 0
        };
    },
    
    collectRentalDetails(container) {
        return {
            propertyAddress: container.querySelector('input[placeholder*="Property Address"]')?.value || '',
            coOwnerPartner1: container.querySelector('input[placeholder*="Co-owner / Partner 1"]')?.value || '',
            coOwnerPartner2: container.querySelector('input[placeholder*="Co-owner / Partner 2"]')?.value || '',
            coOwnerPartner3: container.querySelector('input[placeholder*="Co-owner / Partner 3"]')?.value || '',
            numberOfUnits: parseInt(container.querySelector('input[placeholder*="Number of Units"]')?.value) || 0,
            grossRentalIncome: parseFloat(container.querySelector('input[placeholder*="Gross Rental Income"]')?.value) || 0,
            govtIncomeRelatingToRental: parseFloat(container.querySelector('input[placeholder*="Any Govt. Income"]')?.value) || 0,
            personalUsePortion: parseFloat(container.querySelector('input[placeholder*="Personal Use Portion"]')?.value) || 0,
            purchasePrice: parseFloat(container.querySelector('input[placeholder*="Purchase Price"]')?.value) || 0,
            purchaseDate: container.querySelector('input[placeholder*="Purchase date"]')?.value || null,
            additionDeletionAmount: parseFloat(container.querySelector('input[placeholder*="Addition / deletion"]')?.value) || 0,
            additionDeletionYear: parseInt(container.querySelector('input[placeholder*="Addition / deletion Year"]')?.value) || 0,
            lastYearUccValue: parseFloat(container.querySelector('input[placeholder*="Last Year UCC Value"]')?.value) || 0
        };
    },
    
    collectPropertySaleDetails(container) {
        return {
            propertyAddress: container.querySelector('input[placeholder*="Address of the Property"]')?.value || '',
            purchaseDate: container.querySelector('input[placeholder*="Purchase Date"]')?.value || null,
            sellDate: container.querySelector('input[placeholder*="Sell Date"]')?.value || null,
            expensesRelatedToPurchaseAndSell: parseFloat(container.querySelector('input[placeholder*="Expenses related"]')?.value) || 0,
            capitalGainEarned: parseFloat(container.querySelector('input[placeholder*="Capital Gain Earned"]')?.value) || 0
        };
    },
    
    collectWorkFromHomeDetails(container) {
        return {
            totalSqFtHouseIndividual: parseFloat(container.querySelector('input[placeholder*="Total Sq.Ft. area of your House (Individual)"]')?.value) || 0,
            totalSqFtHouseSpouse: parseFloat(container.querySelector('input[placeholder*="Total Sq.Ft. area of your House (Spouse)"]')?.value) || 0,
            totalSqFtUsedForWorkIndividual: parseFloat(container.querySelector('input[placeholder*="Total Sq.Ft. area used for work (Individual)"]')?.value) || 0,
            totalSqFtUsedForWorkSpouse: parseFloat(container.querySelector('input[placeholder*="Total Sq.Ft. area used for work (Spouse)"]')?.value) || 0,
            totalRentMortgageInterest: parseFloat(container.querySelector('input[placeholder*="Total Rent/Mortgage Interest"]')?.value) || 0,
            totalWifiElectricity: parseFloat(container.querySelector('input[placeholder*="Total Wifi and Electricity"]')?.value) || 0,
            totalHeatWater: parseFloat(container.querySelector('input[placeholder*="Total Heat and Water"]')?.value) || 0,
            totalInsurance: parseFloat(container.querySelector('input[placeholder*="Total Insurance Expense"]')?.value) || 0
        };
    },
    
    collectFirstTimeFilerDetails(container) {
        return {
            dateOfLandingIndividual: container.querySelector('input[placeholder*="Date of landing"][placeholder*="Individual"]')?.value || null,
            dateOfLandingSpouse: container.querySelector('input[placeholder*="Date of landing"][placeholder*="Spouse"]')?.value || null,
            approxIncomeOutsideCanadaIndividual: parseFloat(container.querySelector('input[placeholder*="Approximate income earned outside Canada"][placeholder*="Individual"]')?.value) || 0,
            approxIncomeOutsideCanadaSpouse: parseFloat(container.querySelector('input[placeholder*="Approximate income earned outside Canada"][placeholder*="Spouse"]')?.value) || 0,
            backHomeIncome2022Individual: parseFloat(container.querySelector('input[placeholder*="Back Home/working country Income 2022"][placeholder*="Individual"]')?.value) || 0,
            backHomeIncome2022Spouse: parseFloat(container.querySelector('input[placeholder*="Back Home/working country Income 2022"][placeholder*="Spouse"]')?.value) || 0,
            backHomeIncome2021Individual: parseFloat(container.querySelector('input[placeholder*="Back Home/working country Income 2021"][placeholder*="Individual"]')?.value) || 0,
            backHomeIncome2021Spouse: parseFloat(container.querySelector('input[placeholder*="Back Home/working country Income 2021"][placeholder*="Spouse"]')?.value) || 0
        };
    },
    
    collectTableData(tableId) {
        const table = document.querySelector(`#${tableId} table tbody`);
        if (!table) return [];
        
        const rows = table.querySelectorAll('tr');
        const data = [];
        
        rows.forEach(row => {
            const inputs = row.querySelectorAll('input');
            const rowData = {};
            inputs.forEach((input, index) => {
                if (input.type === 'number') {
                    rowData[`field_${index}`] = parseFloat(input.value) || 0;
                } else if (input.type === 'date') {
                    rowData[`field_${index}`] = input.value || null;
                } else {
                    rowData[`field_${index}`] = input.value || '';
                }
            });
            if (Object.keys(rowData).length > 0) {
                data.push(rowData);
            }
        });
        
        return data;
    },
    
    collectAllData() {
        const formData = {
            tax_year: 2023,
            status: 'draft',
            personalInfo: this.collectPersonalInfo(),
            questionnaire: this.collectQuestionnaire()
        };
        
        // Map form data to database fields
        const dbData = {
            tax_year: formData.tax_year,
            status: formData.status,
            first_name: formData.personalInfo.firstName,
            last_name: formData.personalInfo.lastName,
            email: formData.personalInfo.email,
            
            // Boolean flags
            has_foreign_property: formData.questionnaire.hasForeignProperty || false,
            has_medical_expenses: formData.questionnaire.hasMedicalExpenses || false,
            has_charitable_donations: formData.questionnaire.hasCharitableDonations || false,
            has_moving_expenses: formData.questionnaire.hasMovingExpenses || false,
            is_self_employed: formData.questionnaire.isSelfEmployed || false,
            is_first_home_buyer: formData.questionnaire.isFirstHomeBuyer || false,
            is_first_time_filer: formData.questionnaire.isFirstTimeFiler || false,
            
            // Store complete form data as JSON
            form_data: formData,
            
            // Income calculations (you can add logic here)
            employment_income: 0,
            self_employment_income: 0,
            investment_income: 0,
            other_income: 0,
            total_income: 0,
            rrsp_contributions: 0,
            charitable_donations: 0,
            federal_tax: 0,
            provincial_tax: 0,
            total_tax: 0,
            refund_or_owing: 0
        };
        
        return dbData;
    }
};

// Authentication UI
const AuthUI = {
    showLoginModal() {
        const modalHtml = `
        <div class="modal fade" id="loginModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Login to TaxEase</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div id="loginError" class="alert alert-danger d-none"></div>
                        <form id="loginForm">
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" id="loginEmail" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" class="form-control" id="loginPassword" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="loginBtn">Login</button>
                        <button type="button" class="btn btn-link" id="showRegisterBtn">Need an account?</button>
                    </div>
                </div>
            </div>
        </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('loginModal'));
        modal.show();
        
        // Event listeners
        document.getElementById('loginBtn').addEventListener('click', this.handleLogin.bind(this));
        document.getElementById('showRegisterBtn').addEventListener('click', () => {
            modal.hide();
            this.showRegisterModal();
        });
    },
    
    showRegisterModal() {
        const modalHtml = `
        <div class="modal fade" id="registerModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Register for TaxEase</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div id="registerError" class="alert alert-danger d-none"></div>
                        <form id="registerForm">
                            <div class="mb-3">
                                <label class="form-label">First Name</label>
                                <input type="text" class="form-control" id="registerFirstName" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Last Name</label>
                                <input type="text" class="form-control" id="registerLastName" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" id="registerEmail" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" class="form-control" id="registerPassword" required>
                                <div class="form-text">Minimum 8 characters</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="registerBtn">Register</button>
                        <button type="button" class="btn btn-link" id="showLoginBtn">Have an account?</button>
                    </div>
                </div>
            </div>
        </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('registerModal'));
        modal.show();
        
        // Event listeners
        document.getElementById('registerBtn').addEventListener('click', this.handleRegister.bind(this));
        document.getElementById('showLoginBtn').addEventListener('click', () => {
            modal.hide();
            this.showLoginModal();
        });
    },
    
    async handleLogin() {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const errorDiv = document.getElementById('loginError');
        const loginBtn = document.getElementById('loginBtn');
        
        try {
            loginBtn.disabled = true;
            loginBtn.textContent = 'Logging in...';
            
            await API.login(email, password);
            
            // Close modal and show success
            const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            modal.hide();
            
            this.showSuccessMessage('Login successful! You can now submit your T1 form.');
            
        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('d-none');
        } finally {
            loginBtn.disabled = false;
            loginBtn.textContent = 'Login';
        }
    },
    
    async handleRegister() {
        const firstName = document.getElementById('registerFirstName').value;
        const lastName = document.getElementById('registerLastName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const errorDiv = document.getElementById('registerError');
        const registerBtn = document.getElementById('registerBtn');
        
        try {
            registerBtn.disabled = true;
            registerBtn.textContent = 'Registering...';
            
            await API.register({
                first_name: firstName,
                last_name: lastName,
                email,
                password
            });
            
            // Close modal and show login
            const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            modal.hide();
            
            this.showSuccessMessage('Registration successful! Please login to continue.');
            this.showLoginModal();
            
        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('d-none');
        } finally {
            registerBtn.disabled = false;
            registerBtn.textContent = 'Register';
        }
    },
    
    showSuccessMessage(message) {
        const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        `;
        
        document.querySelector('.container').insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            const alert = document.querySelector('.alert-success');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    },
    
    showErrorMessage(message) {
        const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        `;
        
        document.querySelector('.container').insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            const alert = document.querySelector('.alert-danger');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
};

// Form Handler
const FormHandler = {
    async handleSubmit(event) {
        event.preventDefault();
        
        // Check authentication
        if (!TokenManager.isAuthenticated()) {
            AuthUI.showLoginModal();
            return;
        }
        
        const submitButton = event.target.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        try {
            submitButton.disabled = true;
            submitButton.textContent = 'Submitting...';
            
            // Collect form data
            const formData = FormDataCollector.collectAllData();
            
            // Submit to backend
            const result = await API.createT1Form(formData);
            
            AuthUI.showSuccessMessage(`T1 Form submitted successfully! Form ID: ${result.form_id}`);
            
            // Optionally reset form or redirect
            console.log('Form submission result:', result);
            
        } catch (error) {
            console.error('Form submission failed:', error);
            AuthUI.showErrorMessage(`Failed to submit T1 form: ${error.message}`);
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    },
    
    initializeForm() {
        const form = document.getElementById('multiStepForm');
        if (form) {
            // Check if enhanced handler is already installed
            if (!form.hasAttribute('data-enhanced-handler')) {
                console.log('📋 Installing default API form handler...');
                form.addEventListener('submit', this.handleSubmit.bind(this));
                form.setAttribute('data-api-handler', 'true');
            } else {
                console.log('📋 Enhanced form handler detected, skipping default handler...');
            }
            
            // Add authentication status indicator
            this.addAuthStatusIndicator();
        } else {
            console.warn('❌ Form with id "multiStepForm" not found!');
        }
    },
    
    addAuthStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'authStatus';
        indicator.className = 'auth-status';
        indicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            z-index: 1000;
        `;
        
        this.updateAuthStatusIndicator(indicator);
        document.body.appendChild(indicator);
        
        // Update every 5 seconds
        setInterval(() => this.updateAuthStatusIndicator(indicator), 5000);
    },
    
    updateAuthStatusIndicator(indicator) {
        if (TokenManager.isAuthenticated()) {
            indicator.textContent = '✓ Authenticated';
            indicator.style.backgroundColor = '#d4edda';
            indicator.style.color = '#155724';
            indicator.style.border = '1px solid #c3e6cb';
        } else {
            indicator.textContent = '⚠ Not Authenticated';
            indicator.style.backgroundColor = '#f8d7da';
            indicator.style.color = '#721c24';
            indicator.style.border = '1px solid #f5c6cb';
            indicator.style.cursor = 'pointer';
            indicator.onclick = () => AuthUI.showLoginModal();
        }
    }
};

// Auto-save functionality
const AutoSave = {
    intervalId: null,
    
    start() {
        this.stop(); // Clear any existing interval
        
        this.intervalId = setInterval(async () => {
            if (TokenManager.isAuthenticated()) {
                try {
                    const formData = FormDataCollector.collectAllData();
                    formData.status = 'draft';
                    
                    // Save as draft (you might want to implement this endpoint)
                    console.log('Auto-saving form data:', formData);
                    
                } catch (error) {
                    console.warn('Auto-save failed:', error);
                }
            }
        }, 30000); // Save every 30 seconds
    },
    
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('T1 Form API integration script starting...');
    
    FormHandler.initializeForm();
    
    // Start auto-save if user is authenticated
    if (TokenManager.isAuthenticated()) {
        AutoSave.start();
    }
    
    console.log('T1 Form API integration loaded successfully!');
    console.log('Form element found:', document.getElementById('multiStepForm') !== null);
});

// Export for global access
window.T1FormAPI = {
    API,
    FormDataCollector,
    TokenManager,
    AuthUI,
    FormHandler,
    AutoSave
};
