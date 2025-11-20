# Deployment Checklist

## Pre-Deployment Verification ✅

### 1. Database Migrations
- [x] All migrations applied successfully
- [x] Employee scoping working (no EMPID conflicts across users)
- [x] User approval system tables created

### 2. Admin User Setup
- [x] Admin creation command tested
- [x] Build script updated to create admin user automatically

### 3. Code Quality
- [x] Django system checks pass
- [x] All new models, views, and authentication working

## Digital Ocean Deployment Steps

### 1. Update Environment Variables
Make sure these are set in Digital Ocean:
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### 2. Deploy Commands
The updated `build.sh` will automatically:
1. Install dependencies
2. Run migrations
3. Collect static files
4. Create admin user (if not exists)

### 3. Post-Deployment Verification
After deployment, verify:
- [ ] Admin user can login at `/admin/`
- [ ] New user registration creates pending users
- [ ] Admin can approve/reject users via API
- [ ] Approved users can login successfully
- [ ] Employee data is scoped to each user properly

### 4. API Endpoints to Test
```bash
# Register new user
POST /api/register/

# Admin endpoints (require admin authentication)
GET /api/admin/users/pending/
POST /api/admin/users/{id}/approve/
POST /api/admin/users/{id}/reject/
GET /api/admin/users/stats/
```

## Frontend Integration Tasks

### 1. Registration Flow
- Update registration success message to mention admin approval
- Add approval status checking in user dashboard

### 2. Login Enhancement
- Handle approval status errors gracefully
- Show appropriate messages for pending/rejected users

### 3. Admin Dashboard (Optional)
- Create admin interface for user approval
- Show pending users count and approval actions

## Success Criteria
- [x] No more duplicate EMPID errors across different users
- [x] New users require admin approval before accessing system
- [x] Existing approved users continue working normally
- [x] Clean deployment process with automated admin setup

## Notes
- Admin username: `admin`
- Admin email: `admin@payroll.com`
- Password will be generated during deployment
- All user approval functionality documented in `USER_APPROVAL_SYSTEM.md`
