# T1 Form Frontend-Backend Integration Guide

## 🎯 Overview

Your T1 form is now **connected to the backend API**! This guide explains how the integration works and how to test it.

---

## ✅ What's Been Done

### 1. **Created API Integration Script** (`t1_form_api.js`)
   - Full authentication system (login/register)
   - Automatic data collection from all form fields
   - JWT token management
   - Form submission to FastAPI backend
   - Error handling and user feedback

### 2. **Updated HTML Form** (`t1_form.html`)
   - Added script reference to `t1_form_api.js`
   - Form now submits data to backend database

### 3. **Complete Field Mapping**
   - Personal information (157+ fields)
   - Spouse and children details
   - All 18 questionnaire sections
   - Self-employment (Uber, General Business, Rental Income)
   - Moving expenses (Individual and Spouse)
   - Foreign property details

---

## 🚀 How It Works

### **Step 1: User Authentication**

When the page loads:
1. Script checks if user is logged in (JWT token in localStorage)
2. If not logged in, shows authentication modal
3. User can register a new account or login to existing account

### **Step 2: Form Filling**

User fills out the multi-step form:
- Personal Information (Step 1)
- Questionnaire (Step 2)
- All conditional sections appear based on user responses

### **Step 3: Form Submission**

When user clicks "Submit Form":
1. JavaScript collects all form data
2. Converts it to JSON format matching backend schema
3. Sends POST request to `/api/v1/t1-forms/`
4. Backend validates data with Pydantic schemas
5. Data is encrypted and saved to PostgreSQL database
6. Success/error message shown to user

---

## 🧪 Testing the Integration

### **Option 1: Quick Test (Using Existing Test Account)**

1. **Make sure backend server is running:**
   ```bash
   cd /home/cyberdude/Documents/Projects/taxease_backend
   python main.py
   ```

2. **Open the HTML form in browser:**
   ```bash
   # If you have a local web server:
   python -m http.server 8080
   
   # Then open: http://localhost:8080/t1_form.html
   ```

3. **Login with test credentials:**
   - Email: `test_1763013147@example.com`
   - Password: `SecureTestPass123!`

4. **Fill out the form** (at least required fields):
   - First Name: John
   - Last Name: Doe
   - SIN: 123456789
   - Address: 123 Main St, Toronto
   - Phone: +14165550123
   - Email: john@example.com

5. **Submit the form** and check for success message

### **Option 2: Create New User**

1. **Click "Register" in the authentication modal**

2. **Fill in:**
   - Full Name: Your Name
   - Email: your@email.com
   - Password: YourSecurePassword123!

3. **After registration, login with those credentials**

4. **Fill and submit the form**

---

## 📋 API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/auth/register` | POST | Register new user |
| `/api/v1/auth/login` | POST | Login and get JWT token |
| `/api/v1/encryption/setup` | POST | Setup encryption keys |
| `/api/v1/t1-forms/` | POST | Create T1 form |
| `/api/v1/t1-forms/{id}` | GET | Retrieve T1 form |
| `/api/v1/t1-forms/{id}` | PUT | Update T1 form |

---

## 🔐 Security Features

### **1. JWT Authentication**
- All form submissions require valid JWT token
- Token stored in browser localStorage
- Token expires after 15 minutes
- User must re-authenticate after expiration

### **2. Automatic Encryption**
- All sensitive data encrypted using AES-256-CBC
- Each user has unique encryption keys (RSA-2048)
- Data encrypted before saving to database
- Data automatically decrypted when retrieved

### **3. CORS Protection**
- Backend configured with CORS middleware
- Only allowed origins can access API

---

## 📝 Sample Form Data Structure

When you submit the form, here's what gets sent to the backend:

```json
{
  "status": "draft",
  "personalInfo": {
    "firstName": "John",
    "middleName": "Q",
    "lastName": "Doe",
    "sin": "123456789",
    "dateOfBirth": "1990-05-20",
    "address": "123 Main St, Toronto, ON",
    "phoneNumber": "+14165550123",
    "email": "john@example.com",
    "isCanadianCitizen": true,
    "maritalStatus": "single"
  },
  "hasForeignProperty": false,
  "foreignProperties": [],
  "hasMedicalExpenses": false,
  "hasCharitableDonations": false,
  "hasMovingExpenses": false,
  "isSelfEmployed": false,
  "isFirstHomeBuyer": false,
  "soldPropertyLongTerm": false,
  "soldPropertyShortTerm": false,
  "hasWorkFromHomeExpense": false,
  "wasStudentLastYear": false,
  "isUnionMember": false,
  "hasDaycareExpenses": false,
  "isFirstTimeFiler": false,
  "hasOtherIncome": false,
  "hasProfessionalDues": false,
  "hasRrspFhsaInvestment": false,
  "hasChildArtSportCredit": false,
  "isProvinceFiler": false
}
```

---

## 🐛 Troubleshooting

### **Issue 1: "Failed to fetch" error**

**Cause:** Backend server not running

**Solution:**
```bash
cd /home/cyberdude/Documents/Projects/taxease_backend
python main.py
```

---

### **Issue 2: "Unauthenticated" error**

**Cause:** JWT token expired or missing

**Solution:**
1. Clear localStorage: `localStorage.clear()` in browser console
2. Refresh page
3. Login again

---

### **Issue 3: CORS error**

**Cause:** Frontend and backend on different domains

**Solution:**
Update `main.py` to allow your frontend origin:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### **Issue 4: "Form data missing" error**

**Cause:** Required fields not filled

**Solution:**
Make sure these required fields are filled:
- First Name
- Last Name
- SIN (9 digits)
- Address
- Phone Number
- Email
- Marital Status

---

## 🔧 Advanced Features

### **Save as Draft**

To save form without submitting:
```javascript
// Modify the status field
const formData = FormDataCollector.collectAllData();
formData.status = 'draft'; // Can be: 'draft', 'submitted', 'approved', 'rejected'
await API.createT1Form(formData);
```

### **Update Existing Form**

To update a previously saved form:
```javascript
const formId = 'T1_1234567890';
const formData = FormDataCollector.collectAllData();
await API.updateT1Form(formId, formData);
```

### **Retrieve Saved Form**

To load a previously saved form:
```javascript
const formId = 'T1_1234567890';
const savedForm = await API.getT1Form(formId);
console.log(savedForm);
```

---

## 📊 Viewing Saved Data

### **Option 1: Using API Directly**

```bash
# Get your auth token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test_1763013147@example.com&password=SecureTestPass123!"

# List all your forms
curl -X GET http://localhost:8000/api/v1/t1-forms/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### **Option 2: Using PostgreSQL**

```bash
psql -U postgres -d taxease_db

# View all T1 forms
SELECT form_id, user_id, status, created_at FROM t1_personal_forms;

# View specific form (encrypted data)
SELECT * FROM t1_personal_forms WHERE form_id = 'T1_1234567890';
```

### **Option 3: Using API Documentation**

1. Open: http://localhost:8000/docs
2. Click "Authorize" button
3. Enter your JWT token
4. Test all endpoints interactively

---

## 🎨 Customization

### **Change API URL**

Edit `t1_form_api.js`:
```javascript
const API_CONFIG = {
    BASE_URL: 'https://your-production-domain.com', // Change this
    // ... rest of config
};
```

### **Add Form Validation**

Add validation before submission:
```javascript
// In FormHandler.handleSubmit()
if (!this.validateForm()) {
    this.showError('Please fill all required fields');
    return;
}
```

### **Add Auto-Save**

Save draft every 2 minutes:
```javascript
setInterval(async () => {
    if (TokenManager.isAuthenticated()) {
        const formData = FormDataCollector.collectAllData();
        formData.status = 'draft';
        await API.createT1Form(formData);
        console.log('Auto-saved!');
    }
}, 120000); // 2 minutes
```

---

## ✅ Next Steps

1. **Test the integration** with the test account
2. **Fill out a complete form** and verify data saves to database
3. **Customize the UI** for better user experience (add loading spinners, better error messages)
4. **Add form validation** before submission
5. **Implement auto-save** feature
6. **Add file upload** functionality for supporting documents
7. **Create a dashboard** to view all submitted forms
8. **Deploy to production** server

---

## 📞 Support

If you encounter any issues:

1. Check browser console for errors (F12)
2. Check backend logs: `tail -f server.log`
3. Verify backend is running: `curl http://localhost:8000/health`
4. Check database connection: `psql -U postgres -d taxease_db -c "SELECT 1;"`

---

## 🎉 Success Checklist

- ✅ Backend API running on port 8000
- ✅ Database connected and migrations applied
- ✅ Frontend form loads without errors
- ✅ User can register/login
- ✅ Form submission works
- ✅ Data appears in database
- ✅ Data can be retrieved via API

**Your T1 form is now fully integrated with the backend!** 🚀
