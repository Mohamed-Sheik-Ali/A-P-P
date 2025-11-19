# 🧪 Payroll API Testing Guide

This guide provides comprehensive steps to test the Payroll Processor API and verify how data is stored in the database.

## 📋 Prerequisites

1. **Server Running**: Ensure the Django development server is running
   ```bash
   python manage.py runserver
   ```

2. **Database Setup**: Ensure migrations are applied
   ```bash
   python manage.py migrate
   ```

3. **Sample File**: Ensure `sample_payroll_template.xlsx` exists in the project root

## 🚀 Quick Testing (Automated)

### Option 1: Run Automated Test Suite

```bash
python test_api.py
```

This will:
- Register a test user
- Login and get authentication token
- Test all API endpoints
- Upload the sample Excel file
- Verify data processing
- Generate reports
- Show detailed response logs

### Option 2: Inspect Database After Testing

```bash
python inspect_database.py
```

Available inspection commands:
```bash
python inspect_database.py summary      # Show summary statistics
python inspect_database.py users        # Show all users
python inspect_database.py uploads      # Show all uploads
python inspect_database.py employees    # Show all employees
python inspect_database.py salary       # Show salary components
python inspect_database.py reports      # Show generated reports
python inspect_database.py latest       # Show latest upload details
python inspect_database.py upload=1     # Show specific upload details
```

## 🛠 Manual Testing (Step by Step)

### Step 1: Test User Registration

**Endpoint**: `POST /api/auth/register/`

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Expected Response**: Status 201 with user details

### Step 2: Test User Login

**Endpoint**: `POST /api/auth/login/`

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

**Expected Response**: Status 200 with access token
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

**Important**: Save the `access` token for subsequent requests!

### Step 3: Test File Upload

**Endpoint**: `POST /api/uploads/`

```bash
curl -X POST http://127.0.0.1:8000/api/uploads/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sample_payroll_template.xlsx"
```

**Expected Response**: Status 201 with upload details
```json
{
  "id": 1,
  "filename": "sample_payroll_template.xlsx",
  "status": "completed",
  "total_employees": 5,
  "upload_date": "2025-11-19T02:56:45Z",
  "processed_date": "2025-11-19T02:56:46Z"
}
```

### Step 4: Get Upload Details

**Endpoint**: `GET /api/uploads/{upload_id}/`

```bash
curl -X GET http://127.0.0.1:8000/api/uploads/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Step 5: Get Employees List

**Endpoint**: `GET /api/uploads/{upload_id}/employees/`

```bash
curl -X GET http://127.0.0.1:8000/api/uploads/1/employees/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response**: List of employees with salary calculations
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "employee_id": "EMP001",
      "name": "John Doe",
      "email": "john.doe@company.com",
      "department": "Engineering",
      "designation": "Software Engineer",
      "salary": {
        "basic_pay": "50000.00",
        "hra": "20000.00",
        "variable_pay": "10000.00",
        "gross_salary": "80000.00",
        "provident_fund": "6000.00",
        "professional_tax": "200.00",
        "income_tax": "1000.00",
        "total_deductions": "7200.00",
        "net_salary": "72800.00"
      }
    }
  ]
}
```

### Step 6: Generate Report

**Endpoint**: `POST /api/uploads/{upload_id}/reports/generate/`

```bash
curl -X POST http://127.0.0.1:8000/api/uploads/1/reports/generate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"report_type": "excel"}'
```

### Step 7: Get Dashboard Statistics

**Endpoint**: `GET /api/dashboard/stats/`

```bash
curl -X GET http://127.0.0.1:8000/api/dashboard/stats/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔍 Database Verification

After testing, verify the data stored in the database:

### Check Users Table
```bash
python inspect_database.py users
```

### Check Uploaded Files
```bash
python inspect_database.py uploads
```

### Check Employee Data
```bash
python inspect_database.py employees
```

### Check Salary Calculations
```bash
python inspect_database.py salary
```

### Check Generated Reports
```bash
python inspect_database.py reports
```

## 📊 What Data is Stored

### 1. PayrollUpload Table
- File upload metadata
- Processing status
- User association
- Upload timestamps
- Error messages (if any)

### 2. Employee Table
- Employee personal information
- Department and designation
- Linked to specific upload

### 3. SalaryComponent Table
- **Earnings**: Basic Pay, HRA, Variable Pay, Allowances
- **Deductions**: PF, Professional Tax, Income Tax
- **Calculated Values**: Gross Salary, Net Salary, Take Home Pay
- Automatic calculations based on tax rules

### 4. PayrollReport Table
- Generated report metadata
- File paths and sizes
- Report types (Excel/PDF)

### 5. User Table (Django's built-in)
- User authentication data
- Profile information

## 🧮 Salary Calculation Verification

The system automatically calculates:

### Gross Salary
```
Gross = Basic Pay + HRA + Variable Pay + Special Allowance + Other Allowances
```

### Provident Fund (12% of Basic Pay)
```
PF = Basic Pay × 0.12
```

### Professional Tax
```
Professional Tax = ₹200 (if Gross > ₹15,000, else ₹0)
```

### Income Tax (Progressive)
```
Annual Gross:
- Up to ₹2,50,000: 0%
- ₹2,50,001 to ₹5,00,000: 5%
- ₹5,00,001 to ₹10,00,000: 20%
- Above ₹10,00,000: 30%
```

### Net Salary
```
Net = Gross - (PF + Professional Tax + Income Tax + Other Deductions)
```

## 🔧 Testing Different Scenarios

### Test File Validation
```bash
curl -X POST http://127.0.0.1:8000/api/uploads/validate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sample_payroll_template.xlsx"
```

### Test Error Handling
Upload an invalid file (e.g., a text file) to test error responses.

### Test Large Files
Create a larger Excel file with more employees to test performance.

### Test Authentication
Try accessing protected endpoints without a token to verify security.

## 📁 File Locations

After successful upload and processing:

- **Uploaded Files**: `media/uploads/YYYY/MM/DD/`
- **Generated Reports**: `media/reports/YYYY/MM/DD/`
- **Database**: `db.sqlite3` (SQLite file)

## 🔍 Troubleshooting

### Common Issues:

1. **401 Unauthorized**: Check if you're including the Bearer token correctly
2. **400 Bad Request**: Verify the request payload format
3. **500 Server Error**: Check the Django server logs
4. **File Upload Fails**: Ensure the file is a valid Excel format

### Debug Commands:

```bash
# Check server logs
tail -f server_logs.log

# Inspect specific upload
python inspect_database.py upload=1

# Check latest upload
python inspect_database.py latest
```

## 🎯 Expected Test Results

After successful testing, you should see:

1. ✅ User registered and authenticated
2. ✅ File uploaded and processed
3. ✅ Employee data extracted and stored
4. ✅ Salary calculations completed automatically
5. ✅ Reports generated successfully
6. ✅ All data accessible via API endpoints

## 📈 Performance Monitoring

Monitor:
- Upload processing time
- Database query performance
- File size limitations
- Memory usage during processing

Run the automated test suite multiple times to ensure consistency and performance.
