# Role-Based Access Control & Dynamic Permissions

## Overview

The system supports **two roles**: `admin` and `superadmin`, both can access all pages. Permissions are **dynamic** and controlled by the superadmin.

## Key Features

✅ **No Page Blocking** - Both admin and superadmin can access all pages  
✅ **Dynamic Permissions** - Superadmin can assign custom permissions to admins  
✅ **Action-Level Control** - Permissions control what actions users can perform  
✅ **Zero Dummy Data** - Dashboard shows empty state when no data exists  

## Roles

### Superadmin
- **Default**: Has all permissions
- **Access**: All pages and all actions
- **Can**: Manage admin users and their permissions
- **Cannot be blocked**: Always has full access

### Admin
- **Default**: Limited permissions (can be customized by superadmin)
- **Access**: All pages (view access)
- **Actions**: Limited by assigned permissions
- **Customizable**: Superadmin can grant/revoke specific permissions

## Available Permissions

1. `add_edit_client` - Create and edit clients
2. `add_edit_payment` - Record and manage payments
3. `request_documents` - Request documents from clients
4. `assign_clients` - Assign clients to admins
5. `view_analytics` - View analytics and reports
6. `approve_cost_estimate` - Approve cost estimates
7. `update_workflow` - Update client workflow status

## How Permissions Work

### Page Access
- **All pages are accessible** to both roles
- No pages are blocked based on role
- Users can navigate to any page

### Action Permissions
- **Create/Update/Delete** operations check permissions
- If user lacks permission, action is blocked with error message
- UI shows/hides action buttons based on permissions

### Examples

**Admin without `add_edit_client` permission:**
- ✅ Can view Clients page
- ✅ Can view client details
- ❌ Cannot create new client
- ❌ Cannot edit client
- ❌ Cannot delete client

**Admin with `add_edit_payment` permission:**
- ✅ Can view Payments page
- ✅ Can create payments
- ✅ Can view payment history

## Creating Admin Users

### Using Script

```bash
cd tax-hub-dashboard/backend
source venv/bin/activate

# Create admin with default permissions
python create_admin.py admin@taxease.ca "John Admin" "password123" admin

# Create admin with specific permissions
python create_admin.py admin@taxease.ca "John Admin" "password123" admin \
  add_edit_client view_analytics request_documents

# Create superadmin
python create_admin.py super@taxease.ca "Super Admin" "password123" superadmin
```

### Using Dashboard

1. Login as superadmin
2. Go to **Admin Management** page
3. Click **Add Admin**
4. Fill in details and select permissions
5. Save

## Managing Permissions

### Via Dashboard
1. Login as superadmin
2. Go to **Admin Management**
3. Click **Edit** on an admin user
4. Toggle permissions on/off
5. Save changes

### Via API
```bash
# Get admin user
curl -X GET http://localhost:8000/api/v1/admin-users/{id} \
  -H "Authorization: Bearer {token}"

# Update permissions
curl -X PATCH http://localhost:8000/api/v1/admin-users/{id} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "permissions": ["add_edit_client", "view_analytics"]
  }'
```

## Database Schema

Permissions are stored as PostgreSQL array:
```sql
permissions TEXT[] NOT NULL DEFAULT '{}'
```

## Frontend Integration

### Checking Permissions
```typescript
const { hasPermission } = useAuth();

// Check if user can perform action
if (hasPermission('add_edit_client')) {
  // Show create/edit buttons
}
```

### Conditional UI
```tsx
{hasPermission(PERMISSIONS.ADD_EDIT_CLIENT) && (
  <Button onClick={handleCreate}>Create Client</Button>
)}
```

## Empty State

When dashboard has no data:
- Shows welcome message
- Provides "Add Your First Client" button
- No dummy data displayed

## Database Optimization

### Indexes Created
- `admin_users`: email, role, is_active
- `clients`: email, status, filing_year, assigned_admin_id
- `documents`: client_id, status, type
- `payments`: client_id, created_at
- `audit_logs`: entity_type, timestamp, performed_by_id

### Performance Features
- Composite indexes for common queries
- Foreign key constraints for data integrity
- ANALYZE run for query planner optimization

## Setup

1. **Run database setup:**
   ```bash
   python setup_database.py
   ```

2. **Create superadmin:**
   ```bash
   python create_superadmin.py
   ```

3. **Create admin user:**
   ```bash
   python create_admin.py admin@taxease.ca "Admin User" "password" admin
   ```

4. **Clear dummy data:**
   ```bash
   python clear_dummy_data.py
   ```

## Testing

1. Login as superadmin - should have full access
2. Create admin user with limited permissions
3. Login as admin - should see all pages but limited actions
4. Verify action buttons are hidden/shown based on permissions
5. Test creating/updating permissions via superadmin

---

**Status**: ✅ Fully implemented and ready for use!





