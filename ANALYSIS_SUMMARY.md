# ANALYSIS_SUMMARY

## Client Fields (from tax_ease_app_client)

### Personal Information
- firstName, middleName, lastName
- sin (SIN)
- dateOfBirth
- address, phoneNumber, email
- isCanadianCitizen
- maritalStatus (single, married, common_law, separated, divorced, widowed)
- spouseInfo: firstName, middleName, lastName, sin, dateOfBirth
- children: List of {firstName, middleName, lastName, sin, dateOfBirth}

### T1 Form Questionnaire Flags
- hasForeignProperty
- hasMedicalExpenses
- hasCharitableDonations
- hasMovingExpenses
- isSelfEmployed
- isFirstHomeBuyer
- soldPropertyLongTerm
- soldPropertyShortTerm
- hasWorkFromHomeExpense
- wasStudentLastYear
- isUnionMember
- hasDaycareExpenses
- isFirstTimeFiler
- hasOtherIncome, otherIncomeDescription
- hasProfessionalDues
- hasRrspFhsaInvestment
- hasChildArtSportCredit
- isProvinceFiler

### T1 Form Sections (JSONB data)
- personalInfo: T1PersonalInfo (full object)
- foreignProperties: List<T1ForeignProperty>
- movingExpense: T1MovingExpense (legacy)
- movingExpenseIndividual: T1MovingExpense
- movingExpenseSpouse: T1MovingExpense
- selfEmployment: T1SelfEmployment containing:
  - businessTypes: ['uber', 'general', 'rental']
  - uberBusiness: T1UberBusiness
  - generalBusiness: T1GeneralBusiness
  - rentalIncome: T1RentalIncome

### Document Sections (from T1DocumentRequirements)
- Disability Approval form (optional)
- Charitable Donation Receipts
- Moving Expense
- Statement of Adjustment issued by lawyer
- T2202 Form
- Union Dues Receipt
- Day Care Expense Receipts
- Professional Fees Receipt
- RRSP/FHSA T-slips
- Receipt for Child's Sport/Fitness & Art

### Status Flags
- status: 'draft' | 'submitted'
- awaitingDocuments: boolean
- uploadedDocuments: Map<String, String> (document label -> filename)

## Admin Fields (from tax-hub-dashboard-admin)

### Client Listing Fields
- id, name, email, phone
- filingYear
- status: 'documents_pending' | 'under_review' | 'cost_estimate_sent' | 'awaiting_payment' | 'in_preparation' | 'awaiting_approval' | 'filed' | 'completed'
- paymentStatus: 'pending' | 'partial' | 'paid' | 'overdue'
- assignedAdminId, assignedAdminName
- totalAmount, paidAmount
- createdAt, updatedAt
- personalInfo: PersonalInfo object

### Document Verification Fields
- id, clientId
- name, type
- status: 'pending' | 'complete' | 'missing' | 'approved' | 'reupload_requested'
- version
- uploadedAt
- notes
- url (file path)

### Admin Actions
- Assign clients to admins
- Request documents (with custom notes)
- Update client status
- Create payment requests
- Upload tax files (T1 Return, T183 Form)
- Send for client approval
- Mark payments as received

### Payment & Filing Status
- Payment: amount, method, note, status ('requested' | 'received' | 'pending'), isRequest
- PaymentRequest: amount, note, status ('pending' | 'received' | 'cancelled')
- TaxFile: t1ReturnUrl, t183FormUrl, refundOrOwing, amount, status ('draft' | 'sent' | 'approved' | 'rejected')

### Role-Based Permissions
- Roles: 'client', 'admin', 'superadmin'
- Permissions:
  - add_edit_payment
  - add_edit_client
  - request_documents
  - assign_clients
  - view_analytics
  - approve_cost_estimate
  - update_workflow

### Admin User Fields
- id, email, name
- role: 'admin' | 'superadmin'
- permissions: List[str]
- avatar, isActive
- createdAt, updatedAt, lastLoginAt

## Document Sections Mapping
Documents are organized by section names:
- 'personal_info'
- 'foreign_property'
- 'medical_expenses'
- 'charitable_donations'
- 'moving_expenses'
- 'self_employment'
- 'uber_business'
- 'general_business'
- 'rental_income'
- 'first_home_buyer'
- 'property_sale'
- 'work_from_home'
- 'student'
- 'union_member'
- 'daycare'
- 'professional_dues'
- 'rrsp_fhsa'
- 'child_art_sport'
- 'other_income'

## API Payload Shapes

### Client APIs
- POST /client/profile: {personalInfo, ...}
- POST /client/tax-return: {formData: T1FormData JSON}
- GET /client/status: Returns {status, paymentStatus, filingYear, ...}

### Document APIs
- POST /documents/upload: multipart/form-data {file, section, clientId}
- GET /documents/client/{id}: Returns list of documents
- GET /documents/section/{name}: Returns documents for section

### Admin APIs
- GET /admin/clients: Returns filtered/paginated client list
- POST /admin/request-documents: {clientId, documentType, note}
- POST /admin/update-status: {clientId, status, paymentStatus}







