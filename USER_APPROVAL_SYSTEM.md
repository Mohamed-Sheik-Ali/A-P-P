# User Approval System Documentation

## Overview

The payroll system now includes an admin approval workflow where new user registrations must be approved by an administrator before users can access the system.

## How It Works

### 1. User Registration Flow
- Users register normally using `/api/auth/register/`
- New accounts are created as **inactive** with `approval_status = 'pending'`
- Users receive a success message indicating approval is required
- Users cannot login until approved by admin

### 2. Admin Approval Process
- Admins can view pending users via `/api/admin/users/?status=pending`
- Admins can approve users via `/api/admin/users/{user_id}/approve/`
- Admins can reject users via `/api/admin/users/{user_id}/reject/`
- Approved users become active and can login
- Rejected users remain inactive

### 3. Authentication Checks
- Login attempts check approval status
- JWT authentication verifies approval status
- Non-approved users receive appropriate error messages

## API Endpoints

### Admin Endpoints (Requires staff/superuser privileges)

#### List Users for Approval
```
GET /api/admin/users/
GET /api/admin/users/?status=pending
GET /api/admin/users/?status=approved
GET /api/admin/users/?status=rejected
GET /api/admin/users/?status=all
```

#### Approve User
```
POST /api/admin/users/{user_id}/approve/
```

#### Reject User
```
POST /api/admin/users/{user_id}/reject/
Content-Type: application/json

{
    "reason": "Optional rejection reason"
}
```

#### Admin Statistics
```
GET /api/admin/users/stats/
```

## User Status States

- **pending**: User registered but awaiting admin approval
- **approved**: User approved and can access system
- **rejected**: User rejected and cannot access system

## Database Changes

### UserProfile Model Extended
- `approval_status`: Choice field (pending/approved/rejected)
- `approved_by`: ForeignKey to User (admin who approved/rejected)
- `approval_date`: DateTime of approval/rejection
- `rejection_reason`: Text field for rejection reason

## Admin User Creation

Create an admin user who can approve registrations:

```bash
python manage.py create_admin --username admin --email admin@company.com --password secure_password
```

## Response Examples

### Registration Response
```json
{
    "success": true,
    "message": "Registration successful! Your account is pending admin approval. You will be able to login once an administrator approves your account.",
    "data": {
        "user": {...},
        "approval_status": "pending"
    }
}
```

### Login Attempt (Pending)
```json
{
    "success": false,
    "message": "Your account is pending admin approval. Please wait for an administrator to approve your account.",
    "approval_status": "pending"
}
```

### Admin User List
```json
{
    "success": true,
    "count": 5,
    "data": [
        {
            "id": 2,
            "username": "john_doe",
            "email": "john@company.com",
            "first_name": "John",
            "last_name": "Doe",
            "organization_name": "ABC Corp",
            "approval_status": "pending",
            "approved_by": null,
            "approval_date": null,
            "rejection_reason": null,
            "date_joined": "2025-11-20T10:00:00Z",
            "is_active": false
        }
    ]
}
```

## Frontend Integration Notes

1. **Registration**: Show success message with approval notice
2. **Login**: Handle approval-related error responses
3. **Admin Dashboard**: Create interface for user approval management
4. **User Status**: Display approval status in user profile

## Security Features

- Only staff/superuser accounts can access admin endpoints
- JWT authentication includes approval status validation
- Inactive accounts cannot obtain valid tokens
- Approval actions are logged with admin user and timestamp

## Migration

The system includes migration `0002_add_user_approval_system.py` which adds:
- Approval status fields to UserProfile
- Foreign key relationship for approved_by
- Approval date and rejection reason fields

## Testing

Test the approval workflow:

1. Register a new user → Should be pending
2. Try to login → Should be rejected with approval message  
3. Admin approves user → User should be able to login
4. Admin rejects user → User should remain unable to login
