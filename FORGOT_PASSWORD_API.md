# Forgot Password API Documentation

## Overview

This document describes the **Forgot Password** flow implementation for the Payroll Processor system. Since there's no email service available, this implementation uses a **secure token-based approach** where users receive a reset token directly in the API response.

## Features

 **Two-API Flow**: Request token � Reset password
 **User Validation**: Checks if user is approved and active
 **Secure Tokens**: 256-bit cryptographically secure random tokens
 **Time-Limited**: Tokens expire after 15 minutes
 **One-Time Use**: Tokens are invalidated after use
 **Automatic Login**: Returns JWT token after successful reset
 **Token Reuse Prevention**: Old tokens are invalidated when new ones are created

---

## API Endpoints

### 1. Request Password Reset

**Endpoint:** `POST /api/auth/forgot-password/`
**Authentication:** None (Public)
**Description:** Validates email, checks user approval status, and generates a secure reset token.

#### Request Body

```json
{
  "email": "user@example.com"
}
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Password reset token generated successfully. Use this token to reset your password within 15 minutes.",
  "data": {
    "token": "aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890abcdefghijk",
    "expires_at": "2025-11-21T15:00:00Z",
    "username": "johndoe"
  }
}
```

#### Error Responses

**400 Bad Request** - Invalid email format
```json
{
  "success": false,
  "message": "Password reset request failed",
  "errors": {
    "email": ["Enter a valid email address."]
  }
}
```

**400 Bad Request** - Email not found
```json
{
  "success": false,
  "message": "Password reset request failed",
  "errors": {
    "email": ["No account found with this email address."]
  }
}
```

**400 Bad Request** - User not approved
```json
{
  "success": false,
  "message": "Password reset request failed",
  "errors": {
    "email": ["Your account is pending admin approval. Please wait for approval before resetting password."]
  }
}
```

**400 Bad Request** - User not active
```json
{
  "success": false,
  "message": "Password reset request failed",
  "errors": {
    "email": ["Your account is not active. Please contact support."]
  }
}
```

---

### 2. Reset Password

**Endpoint:** `POST /api/auth/reset-password/`
**Authentication:** None (Public)
**Description:** Validates the reset token and updates the user's password.

#### Request Body

```json
{
  "token": "aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890abcdefghijk",
  "new_password": "NewSecurePassword123!",
  "new_password2": "NewSecurePassword123!"
}
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Password has been reset successfully. You can now login with your new password.",
  "data": {
    "username": "johndoe",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### Error Responses

**400 Bad Request** - Token already used
```json
{
  "success": false,
  "message": "This reset token has already been used. Please request a new password reset."
}
```

**400 Bad Request** - Token expired
```json
{
  "success": false,
  "message": "This reset token has expired. Please request a new password reset."
}
```

**400 Bad Request** - Invalid token
```json
{
  "success": false,
  "message": "Invalid reset token. Please request a new password reset."
}
```

**400 Bad Request** - Password mismatch
```json
{
  "success": false,
  "message": "Password reset failed",
  "errors": {
    "new_password": ["Password fields didn't match."]
  }
}
```

**400 Bad Request** - Weak password
```json
{
  "success": false,
  "message": "Password reset failed",
  "errors": {
    "new_password": ["This password is too short. It must contain at least 8 characters."]
  }
}
```

---

## Usage Flow

### Complete Workflow

```
1. User clicks "Forgot Password" on frontend
   �
2. Frontend sends POST to /api/auth/forgot-password/ with email
   �
3. API validates:
   - Email exists
   - User is active
   - User is approved (for non-superusers)
   �
4. API generates secure reset token (15-minute expiry)
   �
5. API returns token in response
   �
6. Frontend displays token to user OR sends it via alternative method
   �
7. User enters token and new password on frontend
   �
8. Frontend sends POST to /api/auth/reset-password/ with token and passwords
   �
9. API validates token and updates password
   �
10. API returns JWT token for automatic login
    �
11. Frontend stores JWT and redirects to dashboard
```

---

## Frontend Integration Examples

### Example 1: Using Fetch API

```javascript
// Step 1: Request Password Reset
async function requestPasswordReset(email) {
  try {
    const response = await fetch('http://localhost:8000/api/auth/forgot-password/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email })
    });

    const data = await response.json();

    if (data.success) {
      // Display the token to the user
      alert(`Your reset token is: ${data.data.token}\nThis token expires at: ${data.data.expires_at}`);
      return data.data.token;
    } else {
      alert(data.errors.email[0]);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Step 2: Reset Password
async function resetPassword(token, newPassword, confirmPassword) {
  try {
    const response = await fetch('http://localhost:8000/api/auth/reset-password/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token,
        new_password: newPassword,
        new_password2: confirmPassword
      })
    });

    const data = await response.json();

    if (data.success) {
      // Store JWT token and redirect
      localStorage.setItem('authToken', data.data.token);
      window.location.href = '/dashboard';
    } else {
      alert(data.message);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
const email = 'user@example.com';
const token = await requestPasswordReset(email);
// User enters new password
await resetPassword(token, 'NewPassword123!', 'NewPassword123!');
```

### Example 2: Using Axios

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Request Password Reset
const requestPasswordReset = async (email) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/forgot-password/`, {
      email
    });

    if (response.data.success) {
      return response.data.data;
    }
  } catch (error) {
    throw error.response.data;
  }
};

// Reset Password
const resetPassword = async (token, newPassword, confirmPassword) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/reset-password/`, {
      token,
      new_password: newPassword,
      new_password2: confirmPassword
    });

    if (response.data.success) {
      // Store JWT token
      localStorage.setItem('authToken', response.data.data.token);
      return response.data;
    }
  } catch (error) {
    throw error.response.data;
  }
};
```

---

## Security Features

### 1. Token Security
- **Cryptographically Secure**: Uses Python's `secrets.token_urlsafe(32)` for 256-bit entropy
- **URL-Safe**: Tokens are Base64 URL-safe encoded
- **Unpredictable**: Each token is uniquely generated

### 2. Token Expiration
- Tokens expire after **15 minutes**
- Expired tokens are rejected with clear error messages
- Token expiry time is returned in the API response

### 3. One-Time Use
- Tokens are marked as "used" after successful password reset
- Used tokens cannot be reused
- Prevents replay attacks

### 4. Token Invalidation
- When a new reset token is requested, all previous unused tokens for that user are invalidated
- Prevents token accumulation and confusion

### 5. User Validation
- Verifies user exists
- Checks if user is active (`is_active = True`)
- Checks if user is approved (for non-superusers)
- Appropriate error messages for each validation failure

### 6. IP Tracking
- Records IP address when token is created
- Useful for security auditing and abuse detection

### 7. Password Strength
- Uses Django's built-in password validation
- Enforces minimum length, complexity requirements
- Prevents common passwords

---

## Database Schema

### PasswordResetToken Model

```python
class PasswordResetToken(models.Model):
    user = ForeignKey(User)               # User requesting reset
    token = CharField(max_length=100)     # Secure random token
    created_at = DateTimeField()          # When token was created
    expires_at = DateTimeField()          # When token expires (15 min)
    is_used = BooleanField()              # Whether token has been used
    used_at = DateTimeField()             # When token was used
    ip_address = GenericIPAddressField()  # IP of requester
```

---

## Testing

### Run the Test Script

```bash
# Update TEST_EMAIL in test_forgot_password.py to match a valid user
python3 test_forgot_password.py
```

### Manual Testing with cURL

```bash
# Step 1: Request password reset
curl -X POST http://localhost:8000/api/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'

# Response will contain the token

# Step 2: Reset password with token
curl -X POST http://localhost:8000/api/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token":"YOUR_TOKEN_HERE",
    "new_password":"NewPassword123!",
    "new_password2":"NewPassword123!"
  }'
```

---

## Alternative Token Distribution Methods

Since there's no email service, here are alternative ways to deliver the reset token to users:

### Option 1: Display in UI (Current Implementation)
- Show token directly in the frontend
- User copies token and pastes it in reset form
- Simple but requires user to handle token manually

### Option 2: Admin-Assisted Reset
- User requests reset via API
- Admin views pending reset tokens in Django admin panel
- Admin sends token to user via phone/other channel
- User uses token to reset password

### Option 3: SMS Integration (Future Enhancement)
- Integrate with SMS gateway (Twilio, AWS SNS)
- Send token via SMS instead of email
- More secure than displaying in UI

### Option 4: In-Person Reset (High Security)
- User requests reset
- Admin verifies user identity in person
- Admin provides token to user
- Suitable for high-security environments

---

## Admin Panel Access

Admins can view and manage password reset tokens in Django Admin:

1. Login to Django Admin: `http://localhost:8000/admin/`
2. Navigate to: **Payroll � Password Reset Tokens**
3. View all tokens with:
   - Username
   - Token value
   - Creation time
   - Expiration time
   - Used status
   - IP address

---

## Troubleshooting

### "No account found with this email address"
- Email doesn't exist in database
- Check spelling and try again

### "Your account is pending admin approval"
- User account needs to be approved by admin first
- Contact administrator

### "Your account is not active"
- User account has been deactivated
- Contact administrator

### "This reset token has expired"
- Token was created more than 15 minutes ago
- Request a new password reset

### "This reset token has already been used"
- Token can only be used once
- Request a new password reset

### "Invalid reset token"
- Token doesn't exist in database
- Token may have been mistyped
- Request a new password reset

---

## Production Recommendations

### 1. Enable Email Service
For production, integrate a proper email service:
- SendGrid
- Amazon SES
- Mailgun
- SMTP server

### 2. Increase Token Expiry (Optional)
If needed, modify token expiry in [models.py:303](payroll/models.py#L303):
```python
expires_at = timezone.now() + timedelta(minutes=30)  # 30 minutes instead of 15
```

### 3. Add Rate Limiting
Implement rate limiting to prevent abuse:
```python
from django.core.cache import cache

# In ForgotPasswordRequestView
def post(self, request):
    email = request.data.get('email')
    cache_key = f'password_reset_{email}'

    if cache.get(cache_key):
        return Response({
            'success': False,
            'message': 'Please wait before requesting another reset.'
        }, status=429)

    # Set cooldown (e.g., 5 minutes)
    cache.set(cache_key, True, 300)
    # ... rest of the code
```

### 4. Add Logging
Log all password reset attempts for security auditing:
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f'Password reset requested for {email} from IP {ip_address}')
```

### 5. Use HTTPS
Always use HTTPS in production to protect tokens in transit.

---

## Related Documentation

- [API Payloads Guide](API_PAYLOADS.md)
- [Frontend API Guide](FRONTEND_API_GUIDE.md)
- [User Approval System](USER_APPROVAL_SYSTEM.md)

---

## Support

For issues or questions:
1. Check this documentation
2. Review test results in [test_forgot_password.py](test_forgot_password.py)
3. Check Django server logs
4. Contact system administrator
