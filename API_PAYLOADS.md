# Payroll Processor API - Request & Response Payloads

## Table of Contents
- [Authentication APIs](#authentication-apis)
- [User Profile APIs](#user-profile-apis)
- [Dashboard APIs](#dashboard-apis)
- [Upload APIs](#upload-apis)
- [Employee APIs](#employee-apis)
- [Report APIs](#report-apis)
- [Utility APIs](#utility-apis)

---

## Authentication APIs

### 1. User Registration
**Endpoint:** `POST /api/auth/register/`  
**Authentication:** Not required

**Request Payload:**
```json
{
    "username": "hruser123",
    "email": "hr@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
}
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "User registered successfully. Please login to continue.",
    "data": {
        "user": {
            "id": 1,
            "username": "hruser123",
            "email": "hr@company.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_joined": "2024-11-18T10:30:00Z",
            "last_login": null
        }
    }
}
```

**Error Response (400):**
```json
{
    "success": false,
    "message": "Registration failed",
    "errors": {
        "username": ["A user with this username already exists."],
        "password": ["Password fields didn't match."]
    }
}
```

### 2. User Login
**Endpoint:** `POST /api/auth/login/`  
**Authentication:** Not required

**Request Payload:**
```json
{
    "username": "hruser123",
    "password": "SecurePass123!"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user": {
            "id": 1,
            "username": "hruser123",
            "email": "hr@company.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_joined": "2024-11-18T10:30:00Z",
            "last_login": "2024-11-18T11:45:00Z"
        },
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

**Error Response (401):**
```json
{
    "success": false,
    "message": "Login failed",
    "errors": {
        "non_field_errors": ["Unable to log in with provided credentials."]
    }
}
```

### 3. User Logout
**Endpoint:** `POST /api/auth/logout/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "message": "Logout successful"
}
```

### 4. Check Authentication
**Endpoint:** `GET /api/auth/check/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "authenticated": true,
    "user": {
        "id": 1,
        "username": "hruser123",
        "email": "hr@company.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2024-11-18T10:30:00Z",
        "last_login": "2024-11-18T11:45:00Z"
    }
}
```

---

## User Profile APIs

### 1. Get User Profile
**Endpoint:** `GET /api/user/profile/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "hruser123",
        "email": "hr@company.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2024-11-18T10:30:00Z",
        "last_login": "2024-11-18T11:45:00Z"
    }
}
```

### 2. Update User Profile
**Endpoint:** `PUT /api/user/profile/`  
**Authentication:** Required

**Request Payload:**
```json
{
    "first_name": "John",
    "last_name": "Smith",
    "email": "johnsmith@company.com"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Profile updated successfully",
    "data": {
        "id": 1,
        "username": "hruser123",
        "email": "johnsmith@company.com",
        "first_name": "John",
        "last_name": "Smith",
        "date_joined": "2024-11-18T10:30:00Z",
        "last_login": "2024-11-18T11:45:00Z"
    }
}
```

**Error Response (400):**
```json
{
    "success": false,
    "message": "Profile update failed",
    "errors": {
        "email": ["Enter a valid email address."]
    }
}
```

### 3. Change Password
**Endpoint:** `POST /api/user/change-password/`  
**Authentication:** Required

**Request Payload:**
```json
{
    "old_password": "SecurePass123!",
    "new_password": "NewSecurePass456!",
    "new_password2": "NewSecurePass456!"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Password changed successfully",
    "data": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

**Error Response (400):**
```json
{
    "success": false,
    "message": "Password change failed",
    "errors": {
        "old_password": ["Old password is incorrect."],
        "new_password": ["New password fields didn't match."]
    }
}
```

---

## Dashboard APIs

### 1. Dashboard Statistics
**Endpoint:** `GET /api/dashboard/stats/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "uploads": {
            "total": 15,
            "completed": 12,
            "failed": 2,
            "processing": 1
        },
        "employees": {
            "total": 1250
        },
        "reports": {
            "total": 18
        },
        "disbursement": {
            "total": 85750000.00
        },
        "recent_uploads": [
            {
                "id": 15,
                "user": {
                    "id": 1,
                    "username": "hruser123",
                    "email": "hr@company.com",
                    "first_name": "John",
                    "last_name": "Doe"
                },
                "file": "/media/uploads/2024/11/18/payroll_nov_2024.xlsx",
                "filename": "payroll_nov_2024.xlsx",
                "status": "completed",
                "total_employees": 100,
                "employees_count": 100,
                "upload_date": "2024-11-18T09:30:00Z",
                "processed_date": "2024-11-18T09:35:00Z",
                "error_message": null
            }
        ]
    }
}
```

---

## Upload APIs

### 1. List All Uploads
**Endpoint:** `GET /api/uploads/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "count": 15,
    "data": [
        {
            "id": 15,
            "user": {
                "id": 1,
                "username": "hruser123",
                "email": "hr@company.com",
                "first_name": "John",
                "last_name": "Doe"
            },
            "file": "/media/uploads/2024/11/18/payroll_nov_2024.xlsx",
            "filename": "payroll_nov_2024.xlsx",
            "status": "completed",
            "total_employees": 100,
            "employees_count": 100,
            "upload_date": "2024-11-18T09:30:00Z",
            "processed_date": "2024-11-18T09:35:00Z",
            "error_message": null
        }
    ]
}
```

### 2. Upload Excel File
**Endpoint:** `POST /api/uploads/`  
**Authentication:** Required  
**Content-Type:** `multipart/form-data`

**Request Payload:**
```
file: [Excel file binary data]
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "File processed successfully. 100 employees loaded.",
    "data": {
        "id": 16,
        "user": {
            "id": 1,
            "username": "hruser123",
            "email": "hr@company.com",
            "first_name": "John",
            "last_name": "Doe"
        },
        "file": "/media/uploads/2024/11/18/new_payroll.xlsx",
        "filename": "new_payroll.xlsx",
        "status": "completed",
        "total_employees": 100,
        "employees_count": 100,
        "upload_date": "2024-11-18T12:00:00Z",
        "processed_date": "2024-11-18T12:02:00Z",
        "error_message": null
    },
    "warnings": [
        "Row 25: Email format is invalid for employee EMP001",
        "Row 45: Department field is empty for employee EMP002"
    ]
}
```

**Error Response (400):**
```json
{
    "success": false,
    "message": "File validation failed",
    "errors": [
        "Missing required column: Employee ID",
        "Invalid data format in row 10",
        "File contains no data rows"
    ]
}
```

### 3. Get Upload Details
**Endpoint:** `GET /api/uploads/{upload_id}/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "id": 15,
        "user": {
            "id": 1,
            "username": "hruser123",
            "email": "hr@company.com",
            "first_name": "John",
            "last_name": "Doe"
        },
        "file": "/media/uploads/2024/11/18/payroll_nov_2024.xlsx",
        "filename": "payroll_nov_2024.xlsx",
        "status": "completed",
        "total_employees": 100,
        "upload_date": "2024-11-18T09:30:00Z",
        "processed_date": "2024-11-18T09:35:00Z",
        "error_message": null,
        "employees": [
            {
                "id": 1,
                "employee_id": "EMP001",
                "name": "Alice Johnson",
                "email": "alice@company.com",
                "department": "Engineering",
                "designation": "Senior Developer",
                "salary": {
                    "basic_pay": "50000.00",
                    "hra": "20000.00",
                    "variable_pay": "15000.00",
                    "special_allowance": "5000.00",
                    "other_allowances": "2000.00",
                    "gross_salary": "92000.00",
                    "provident_fund": "6000.00",
                    "professional_tax": "200.00",
                    "income_tax": "8500.00",
                    "other_deductions": "1000.00",
                    "total_deductions": "15700.00",
                    "net_salary": "76300.00",
                    "take_home_pay": "76300.00"
                }
            }
        ]
    }
}
```

**Error Response (404):**
```json
{
    "success": false,
    "message": "Upload not found"
}
```

### 4. Delete Upload
**Endpoint:** `DELETE /api/uploads/{upload_id}/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "message": "Upload deleted successfully"
}
```

**Error Response (404):**
```json
{
    "success": false,
    "message": "Upload not found"
}
```

### 5. Validate Excel File
**Endpoint:** `POST /api/uploads/validate/`  
**Authentication:** Required  
**Content-Type:** `multipart/form-data`

**Request Payload:**
```
file: [Excel file binary data]
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "File validation successful",
    "warnings": [
        "Row 15: Optional field 'Department' is missing",
        "Row 23: Email format could be improved"
    ]
}
```

**Error Response (400):**
```json
{
    "success": false,
    "message": "File validation failed",
    "errors": [
        "Missing required column: Employee ID",
        "Invalid file format. Expected .xlsx or .xls",
        "File contains duplicate employee IDs"
    ]
}
```

---

## Employee APIs

### 1. List Employees for Upload
**Endpoint:** `GET /api/uploads/{upload_id}/employees/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "count": 100,
    "data": [
        {
            "id": 1,
            "employee_id": "EMP001",
            "name": "Alice Johnson",
            "email": "alice@company.com",
            "department": "Engineering",
            "designation": "Senior Developer",
            "salary": {
                "basic_pay": "50000.00",
                "hra": "20000.00",
                "variable_pay": "15000.00",
                "special_allowance": "5000.00",
                "other_allowances": "2000.00",
                "gross_salary": "92000.00",
                "provident_fund": "6000.00",
                "professional_tax": "200.00",
                "income_tax": "8500.00",
                "other_deductions": "1000.00",
                "total_deductions": "15700.00",
                "net_salary": "76300.00",
                "take_home_pay": "76300.00"
            }
        },
        {
            "id": 2,
            "employee_id": "EMP002",
            "name": "Bob Smith",
            "email": "bob@company.com",
            "department": "Marketing",
            "designation": "Marketing Manager",
            "salary": {
                "basic_pay": "45000.00",
                "hra": "18000.00",
                "variable_pay": "10000.00",
                "special_allowance": "3000.00",
                "other_allowances": "1500.00",
                "gross_salary": "77500.00",
                "provident_fund": "5400.00",
                "professional_tax": "200.00",
                "income_tax": "6250.00",
                "other_deductions": "800.00",
                "total_deductions": "12650.00",
                "net_salary": "64850.00",
                "take_home_pay": "64850.00"
            }
        }
    ]
}
```

**Error Response (404):**
```json
{
    "success": false,
    "message": "Upload not found"
}
```

### 2. Get Employee Details
**Endpoint:** `GET /api/employees/{employee_id}/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "employee_id": "EMP001",
        "name": "Alice Johnson",
        "email": "alice@company.com",
        "department": "Engineering",
        "designation": "Senior Developer",
        "salary": {
            "basic_pay": "50000.00",
            "hra": "20000.00",
            "variable_pay": "15000.00",
            "special_allowance": "5000.00",
            "other_allowances": "2000.00",
            "gross_salary": "92000.00",
            "provident_fund": "6000.00",
            "professional_tax": "200.00",
            "income_tax": "8500.00",
            "other_deductions": "1000.00",
            "total_deductions": "15700.00",
            "net_salary": "76300.00",
            "take_home_pay": "76300.00"
        }
    }
}
```

**Error Response (404):**
```json
{
    "success": false,
    "message": "Employee not found"
}
```

---

## Report APIs

### 1. Generate Report
**Endpoint:** `POST /api/uploads/{upload_id}/reports/generate/`  
**Authentication:** Required

**Request Payload:**
```json
{
    "report_type": "excel"
}
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "EXCEL report generated successfully",
    "data": {
        "id": 5,
        "upload": {
            "id": 15,
            "user": {
                "id": 1,
                "username": "hruser123",
                "email": "hr@company.com",
                "first_name": "John",
                "last_name": "Doe"
            },
            "file": "/media/uploads/2024/11/18/payroll_nov_2024.xlsx",
            "filename": "payroll_nov_2024.xlsx",
            "status": "completed",
            "total_employees": 100,
            "employees_count": 100,
            "upload_date": "2024-11-18T09:30:00Z",
            "processed_date": "2024-11-18T09:35:00Z",
            "error_message": null
        },
        "report_type": "excel",
        "file": "/media/reports/2024/11/18/payroll_report_15_excel_20241118_143000.xlsx",
        "generated_date": "2024-11-18T14:30:00Z",
        "file_size": 52480,
        "file_size_kb": 51.25
    }
}
```

**Error Response (400):**
```json
{
    "success": false,
    "message": "Cannot generate report. Upload is not completed yet."
}
```

### 2. List All Reports
**Endpoint:** `GET /api/reports/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "count": 18,
    "data": [
        {
            "id": 5,
            "upload": {
                "id": 15,
                "user": {
                    "id": 1,
                    "username": "hruser123",
                    "email": "hr@company.com",
                    "first_name": "John",
                    "last_name": "Doe"
                },
                "file": "/media/uploads/2024/11/18/payroll_nov_2024.xlsx",
                "filename": "payroll_nov_2024.xlsx",
                "status": "completed",
                "total_employees": 100,
                "employees_count": 100,
                "upload_date": "2024-11-18T09:30:00Z",
                "processed_date": "2024-11-18T09:35:00Z",
                "error_message": null
            },
            "report_type": "excel",
            "file": "/media/reports/2024/11/18/payroll_report_15_excel_20241118_143000.xlsx",
            "generated_date": "2024-11-18T14:30:00Z",
            "file_size": 52480,
            "file_size_kb": 51.25
        },
        {
            "id": 4,
            "upload": {
                "id": 15,
                "user": {
                    "id": 1,
                    "username": "hruser123",
                    "email": "hr@company.com",
                    "first_name": "John",
                    "last_name": "Doe"
                },
                "file": "/media/uploads/2024/11/18/payroll_nov_2024.xlsx",
                "filename": "payroll_nov_2024.xlsx",
                "status": "completed",
                "total_employees": 100,
                "employees_count": 100,
                "upload_date": "2024-11-18T09:30:00Z",
                "processed_date": "2024-11-18T09:35:00Z",
                "error_message": null
            },
            "report_type": "pdf",
            "file": "/media/reports/2024/11/18/payroll_report_15_pdf_20241118_142500.pdf",
            "generated_date": "2024-11-18T14:25:00Z",
            "file_size": 89632,
            "file_size_kb": 87.53
        }
    ]
}
```

### 3. Get Report Details
**Endpoint:** `GET /api/reports/{report_id}/`  
**Authentication:** Required

**Request Payload:** None

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "id": 5,
        "upload": {
            "id": 15,
            "user": {
                "id": 1,
                "username": "hruser123",
                "email": "hr@company.com",
                "first_name": "John",
                "last_name": "Doe"
            },
            "file": "/media/uploads/2024/11/18/payroll_nov_2024.xlsx",
            "filename": "payroll_nov_2024.xlsx",
            "status": "completed",
            "total_employees": 100,
            "employees_count": 100,
            "upload_date": "2024-11-18T09:30:00Z",
            "processed_date": "2024-11-18T09:35:00Z",
            "error_message": null
        },
        "report_type": "excel",
        "file": "/media/reports/2024/11/18/payroll_report_15_excel_20241118_143000.xlsx",
        "generated_date": "2024-11-18T14:30:00Z",
        "file_size": 52480,
        "file_size_kb": 51.25
    }
}
```

**Error Response (404):**
```json
{
    "success": false,
    "message": "Report not found"
}
```

---

## Utility APIs

### 1. API Documentation
**Endpoint:** `GET /api/docs/`  
**Authentication:** Not required

**Request Payload:** None

**Success Response (200):**
```json
{
    "version": "1.0",
    "title": "Payroll Processor API",
    "description": "API for automated payroll processing system",
    "endpoints": {
        "authentication": {
            "register": {
                "url": "/api/auth/register/",
                "method": "POST",
                "description": "Register new HR user",
                "auth_required": false
            },
            "login": {
                "url": "/api/auth/login/",
                "method": "POST",
                "description": "Login HR user",
                "auth_required": false
            }
        },
        "profile": {
            "get_profile": {
                "url": "/api/user/profile/",
                "method": "GET",
                "description": "Get user profile",
                "auth_required": true
            }
        }
    }
}
```

---

## Common Error Responses

### Authentication Error (401)
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Forbidden Error (403)
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### Method Not Allowed (405)
```json
{
    "detail": "Method \"GET\" not allowed."
}
```

### Server Error (500)
```json
{
    "success": false,
    "message": "Internal server error occurred"
}
```

---

## Notes

1. **Authentication**: Most endpoints require JWT token in the Authorization header: `Bearer <token>`
2. **File Uploads**: Use `multipart/form-data` content type for file uploads
3. **Pagination**: Large lists may be paginated in future versions
4. **Rate Limiting**: API may implement rate limiting for production use
5. **File Formats**: Only `.xlsx` and `.xls` files are accepted for uploads
6. **File Size**: Maximum upload size is 10MB
7. **Status Codes**: 
   - 200: Success
   - 201: Created
   - 400: Bad Request
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not Found
   - 500: Internal Server Error

---

## Excel File Format Requirements

The uploaded Excel file should contain the following columns:
- **Employee ID** (required)
- **Name** (required)
- **Email** (optional)
- **Department** (optional)
- **Designation** (optional)
- **Basic Pay** (required)
- **HRA** (optional, defaults to 0)
- **Variable Pay** (optional, defaults to 0)
- **Special Allowance** (optional, defaults to 0)
- **Other Allowances** (optional, defaults to 0)
- **Other Deductions** (optional, defaults to 0)

All salary calculations (gross salary, deductions, net salary) are automatically computed by the system.
