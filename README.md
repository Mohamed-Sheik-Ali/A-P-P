# Automated Payroll Processor

A comprehensive Django REST API application for automating payroll processing from Excel files. This system allows HR teams to upload employee salary data in Excel format, automatically calculates salary components, taxes, and deductions, and generates detailed payroll reports.

## 🚀 Features

### Core Functionality
- **Excel File Upload & Processing**: Upload `.xlsx` or `.xls` files with employee salary data
- **Automatic Salary Calculations**: Computes gross salary, deductions (PF, income tax, professional tax), and net salary
- **Data Validation**: Validates file format, required fields, and data integrity
- **Report Generation**: Generate payroll reports in Excel and PDF formats
- **User Management**: Secure authentication and user profile management

### Key Capabilities
- ✅ **Batch Processing**: Process hundreds of employees simultaneously
- ✅ **Progressive Tax Calculation**: Implements tax slabs for accurate income tax computation
- ✅ **Provident Fund Calculation**: Automatic PF calculation at 12% of basic pay
- ✅ **Professional Tax**: Configurable professional tax based on salary ranges
- ✅ **File Validation**: Pre-upload validation to ensure data quality
- ✅ **Error Handling**: Comprehensive error reporting and warnings
- ✅ **Dashboard Analytics**: Real-time statistics and insights
- ✅ **RESTful API**: Complete REST API with detailed documentation
- ✅ **Password Recovery**: Secure token-based password reset without email service

## 🛠️ Technology Stack

- **Backend**: Django 5.2.8, Django REST Framework 3.16.1
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **File Processing**: openpyxl for Excel file handling
- **Authentication**: JWT tokens with PyJWT
- **Report Generation**: ReportLab for PDF reports
- **Server**: Gunicorn with WhiteNoise for static files
- **CORS**: django-cors-headers for frontend integration

## 📋 Prerequisites

- Python 3.11.6 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd payroll_processor
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
python manage.py migrate
```

### 5. Create Sample Excel Template
```bash
python manage.py create_sample_excel
```

### 6. Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

### Admin Access (development only)

For local development and testing the admin interface a convenience admin account has been added to the README.

- Username: `AdminPay`
- Password: `Admin123@`

Warning: These credentials are intended for local/dev testing only. Do NOT use these credentials in production, and rotate or remove them before deploying to any public environment.

Admin dashboard changes

- The Django admin index includes a new "User Approval Management" panel with a prominent "Review Pending Users" button and live counts for pending/approved/rejected users.
- The admin template was updated to extend `admin/base_site.html` and the client-side stats fetch to `/api/admin/users/stats/` now sends session credentials so the admin UI uses Django session authentication.

Quick verification

1. Restart the Django development server:
   ```bash
   python manage.py runserver
   ```
2. Open `http://127.0.0.1:8000/admin/` and sign in with the admin credentials above.
3. If the panel doesn't appear, clear browser cache or open an incognito window and reload the admin page. Check DevTools → Network for a GET to `/api/admin/users/stats/` returning 200 and JSON containing `pending_users`, `approved_users`, and `rejected_users`.

## 📊 Excel File Format

Your Excel file should contain the following columns:

### Required Columns
- **Employee ID**: Unique identifier for each employee
- **Name**: Full name of the employee
- **Basic Pay**: Base salary amount

### Optional Columns
- **Email**: Employee email address
- **Department**: Department name
- **Designation**: Job title/position
- **HRA**: House Rent Allowance
- **Variable Pay**: Performance-based pay
- **Special Allowance**: Additional allowances
- **Other Allowances**: Miscellaneous allowances
- **Other Deductions**: Additional deductions

### Example Excel Structure
```
Employee ID | Name          | Email              | Department  | Basic Pay | HRA    | Variable Pay
EMP001      | John Doe      | john@company.com   | Engineering | 50000     | 20000  | 10000
EMP002      | Jane Smith    | jane@company.com   | Marketing   | 45000     | 18000  | 8000
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/check/` - Check authentication status
- `POST /api/auth/forgot-password/` - Request password reset token
- `POST /api/auth/reset-password/` - Reset password with token

### User Profile
- `GET /api/user/profile/` - Get user profile
- `PUT /api/user/profile/` - Update user profile
- `POST /api/user/change-password/` - Change password

### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics

### File Upload & Processing
- `GET /api/uploads/` - List all uploads
- `POST /api/uploads/` - Upload and process Excel file
- `GET /api/uploads/{id}/` - Get upload details
- `DELETE /api/uploads/{id}/` - Delete upload
- `POST /api/uploads/validate/` - Validate file without processing

### Employee Data
- `GET /api/uploads/{upload_id}/employees/` - List employees for upload
- `GET /api/employees/{id}/` - Get employee details
- `POST /api/employees/{id}/export/` - Export individual employee data (Excel/PDF)

### Reports
- `POST /api/uploads/{upload_id}/reports/generate/` - Generate reports
- `GET /api/reports/` - List all reports
- `GET /api/reports/{id}/` - Get report details

### Documentation
- `GET /api/docs/` - API documentation

## 💼 Salary Calculation Logic

### Gross Salary
```
Gross Salary = Basic Pay + HRA + Variable Pay + Special Allowance + Other Allowances
```

### Deductions

#### Provident Fund (PF)
```
PF = Basic Pay × 12%
```

#### Professional Tax
```
Professional Tax = ₹200 (if Gross Salary > ₹15,000, else ₹0)
```

#### Income Tax (Simplified Progressive Tax)
```
Annual Gross Salary:
- Up to ₹2,50,000: 0%
- ₹2,50,001 to ₹5,00,000: 5%
- ₹5,00,001 to ₹10,00,000: 20%
- Above ₹10,00,000: 30%
```

### Net Salary
```
Net Salary = Gross Salary - (PF + Professional Tax + Income Tax + Other Deductions)
```

## 📈 Usage Workflow

1. **Register/Login**: Create an account or login to existing account
2. **Upload Excel File**: Upload payroll data in the specified Excel format
3. **File Validation**: System validates file format and data integrity
4. **Processing**: Automatic calculation of all salary components
5. **Review Data**: Check processed employee data and calculations
6. **Generate Reports**: Create Excel or PDF reports for distribution
7. **Download Reports**: Access generated reports for payroll distribution

## 🔒 Security Features

- JWT-based authentication
- User-specific data isolation
- Secure password reset with cryptographically secure tokens (15-minute expiry)
- Token-based password recovery without email dependency
- File upload validation and size limits
- CORS protection
- SQL injection prevention through Django ORM
- XSS protection via Django's built-in security
- Admin approval system for new user registrations


## 📁 Project Structure

```
payroll_processor/
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── runtime.txt                   # Python version for deployment
├── Procfile                      # Heroku deployment configuration
├── API_PAYLOADS.md              # Detailed API documentation
├── sample_payroll_template.xlsx  # Sample Excel template
├── db.sqlite3                    # SQLite database (development)
├── media/                        # Uploaded files and generated reports
│   ├── uploads/                  # Excel file uploads
│   └── reports/                  # Generated reports
├── payroll_config/               # Django project configuration
│   ├── __init__.py
│   ├── settings.py              # Project settings
│   ├── urls.py                  # Main URL configuration
│   ├── wsgi.py                  # WSGI configuration
│   └── asgi.py                  # ASGI configuration
└── payroll/                     # Main application
    ├── __init__.py
    ├── models.py                # Database models
    ├── serializers.py           # API serializers
    ├── views.py                 # API views
    ├── urls.py                  # App URL configuration
    ├── admin.py                 # Django admin configuration
    ├── apps.py                  # App configuration
    ├── jwt_utils.py             # JWT utility functions
    ├── utils.py                 # Utility functions for file processing
    ├── tests.py                 # Unit tests
    ├── migrations/              # Database migrations
    └── management/              # Custom Django commands
        └── commands/
            └── create_sample_excel.py  # Generate sample Excel template
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📚 API Documentation

### 📖 Available Documentation

1. **Detailed API Payloads**: Request/response examples in [`API_PAYLOADS.md`](API_PAYLOADS.md)

2. **Forgot Password Flow**: Complete password reset implementation guide in [`FORGOT_PASSWORD_API.md`](FORGOT_PASSWORD_API.md)

3. **Interactive API Docs**: Built-in documentation interface
   ```
   GET http://127.0.0.1:8000/api/docs/
   ```

4. **🚀 Postman Collection**: Complete API collection with examples
   ```
   https://documenter.getpostman.com/view/31932375/2sB3WyKH17
   ```
   
   **Features of Postman Collection:**
   - ✅ All endpoints with sample requests
   - ✅ Authentication examples
   - ✅ File upload workflows
   - ✅ Error handling scenarios
   - ✅ Environment variables setup
   - ✅ Test scripts for automation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, email support@example.com or open an issue in the GitHub repository.

## 🚦 Status

- ✅ Core payroll processing functionality
- ✅ Excel file upload and validation
- ✅ Salary calculations with tax computation
- ✅ Report generation (Excel/PDF)
- ✅ User authentication and authorization
- ✅ Secure password reset without email service
- ✅ Admin approval system for new users
- ✅ RESTful API with comprehensive documentation
- ✅ Dashboard with analytics
- ✅ Production-ready deployment configuration

---

**Built with ❤️ for efficient payroll management**
