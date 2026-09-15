# Role-Based Access Control (RBAC) System

## Overview

The system implements three distinct user roles with granular permission boundaries enforced at the API layer, not just the UI. This ensures secure access control regardless of how the API is accessed.

## Three Defined Roles

### 1. Shop Owner / Super Admin
**Role ID:** `owner` | **Superuser:** `true`

Unrestricted access across all modules with full administrative capabilities.

#### Permissions (All)
- **Inventory Management**: Full CRUD, view costs, manage categories/brands
- **POS & Sales**: Create, view, void, export sales
- **Purchases**: Full management of supplier orders
- **Repairs**: Complete repair job management
- **Customers**: Full customer management
- **Installments**: Create and manage installment plans
- **Reports**: View all reports including profit, cost, and audit logs
- **Approvals**: Approve voids, reversals, and discounts
- **Administration**: User management, role configuration, audit logs, settings
- **Settings**: Company settings, tax configuration, payment methods

#### Visible Data
- Wholesale/cost prices
- Profit reports and margins
- Audit trails of all user actions
- All sensitive business metrics

#### Test Credentials
- Username: `owner`
- Password: `owner123`

---

### 2. Salesperson / Cashier
**Role ID:** `cashier` | **Superuser:** `false`

Restricted to POS operations and daily cash management. Cannot access wholesale costs or profit data.

#### Permissions (Limited)
- **Inventory**: View only (no costs, no create/edit/delete)
- **POS**: View and create sales (no void/edit after creation)
- **Sales**: View sales (no void, export, or cost viewing)
- **Customers**: View and create (for walk-in customers)
- **Cash Management**: 
  - `cash.session.view` - View cash drawer
  - `cash.session.reconcile` - Daily reconciliation
  - `cash.expense.view` - View expenses
  - `cash.expense.create` - Create daily expenses
- **WhatsApp Integration**: 
  - Broadcast stock updates to customers
  - Send invoices via WhatsApp
- **Customer Inquiry**:
  - Check customer balance
  - Inquire about stock availability

#### Hidden Data
- Wholesale/cost prices (API automatically removes)
- Profit reports and margins
- Audit trails
- User management features
- Repair jobs
- Purchase orders

#### Workflow
1. Log in to POS
2. Search and add products to cart (prices shown, costs hidden)
3. Complete sale
4. Process payment
5. At end of day: Reconcile cash drawer
6. View daily sales summary (total only, no profit data)

#### Test Credentials
- Username: `cashier`
- Password: `cashier123`

---

### 3. Technician / Repair Desk
**Role ID:** `technician` | **Superuser:** `false`

Restricted to repair operations only. No access to sales, inventory management, or financial data.

#### Permissions (Repair-Only)
- **Repair Management**: Full access
  - `repair.view` - View repair jobs
  - `repair.create` - Create new repair jobs
  - `repair.edit` - Edit repair details
  - `repair.update_status` - Update job status
  - `repair.print_slip` - Print service slips
  - `repair.view_diagnostics` - View device diagnostics
  - `repair.parts.allocate` - Allocate parts
  - `repair.parts.track` - Track parts usage
  - `repair.mark_complete` - Mark jobs as complete
  - `repair.mark_delivered` - Mark jobs as delivered
- **Inventory**: View only (for checking available parts)

#### Available Modules
- Repair Job Desk
- Device Diagnostics Form
- Parts Allocation
- Service Slip Printing
- Repair Status Tracking

#### Hidden Data
- POS sales data
- Customer balance and history
- Product costs
- Profit data
- Audit trails
- User management

#### Workflow
1. Log in to Repair Desk
2. View assigned repair jobs
3. Update device diagnostics
4. Allocate parts from inventory
5. Print service slip
6. Update job status
7. Mark as delivered

#### Test Credentials
- Username: `technician`
- Password: `tech123`

---

## API-Level Permission Enforcement

### How It Works

1. **Authentication**: User logs in, receives token
2. **Token Validation**: Every API request validates token and retrieves user record
3. **Permission Check**: Before processing request, API checks if user has required permission
4. **Forbidden Response**: If unauthorized, API returns 403 Forbidden with reason

### Example: Creating a Sale

```javascript
// Frontend requests
POST /sales/invoices/
Authorization: Token mock-token-2-1
Content-Type: application/json

{
  "customer": "John Doe",
  "items": [...],
  "grand_total": 5000
}

// API handler checks:
1. Is user authenticated? ✓
2. Does user have 'pos.create' permission?
   - Owner: ✓ (always allowed)
   - Cashier: ✓ (has 'pos.create')
   - Technician: ✗ (denied)

// If allowed, create invoice
// If denied, return 403 Forbidden
```

### Sensitive Data Filtering

The API automatically removes sensitive fields from responses based on user permissions:

```javascript
// Field removal based on permission
if (!user.permissions.includes('inventory.view_cost')) {
  delete response.cost_price
  delete response.wholesale_cost
  delete response.purchase_cost
}

if (!user.permissions.includes('reports.view_profit')) {
  delete response.gross_profit
  delete response.gross_margin
}
```

---

## Frontend Implementation

### Using Permissions in Components

```vue
<script setup>
import { usePermissions } from '@/composables/usePermissions'

const { canCreateSale, canVoidSale, canViewProfit, isCashier } = usePermissions()
</script>

<template>
  <div>
    <!-- Only show to users with permission -->
    <button v-if="canCreateSale" @click="createSale">
      Create Sale
    </button>

    <!-- Hide void button from cashiers -->
    <button v-if="canVoidSale && !isCashier" @click="voidSale">
      Void Sale
    </button>

    <!-- Show profit only if allowed -->
    <p v-if="canViewProfit">
      Gross Profit: {{ profit }}
    </p>

    <!-- Show repair desk only to technicians -->
    <RepairDesk v-if="isTechnician" />
  </div>
</template>
```

### Permission Composable API

```javascript
const {
  // Inventory
  canViewInventory,
  canCreateInventory,
  canViewCost,

  // POS & Sales
  canAccessPOS,
  canCreateSale,
  canVoidSale,
  canViewSaleCost,

  // Repairs
  canAccessRepairs,
  canCreateRepair,
  canPrintSlip,

  // Reports
  canViewReports,
  canViewProfitReport,
  canViewAuditLog,

  // Admin
  canAccessAdmin,
  canManageUsers,

  // Role checks
  isOwner,
  isCashier,
  isTechnician,

  // Accessible modules (computed object)
  accessibleModules,
} = usePermissions()
```

---

## Route Guards

Routes can enforce permissions at the navigation level:

```javascript
// In route definition
{
  path: '/reports/profit',
  component: ProfitReportView,
  meta: {
    requiresPermission: 'reports.view_profit',
    title: 'Profit Report'
  }
}

// Automatic enforcement via router guard
// If user doesn't have permission:
// - Navigation is blocked
// - User is redirected to /dashboard
// - Toast message shown
```

---

## Files Structure

```
src/
├── api/mock/
│   ├── db/
│   │   ├── permissions.js          # Permission utilities & definitions
│   │   └── fixtures/users.js       # User fixtures with role/permission data
│   ├── middleware/
│   │   └── permissionMiddleware.js # API permission enforcement
│   ├── handlers/
│   │   └── sales.js                # Example: permission checks in handlers
│   └── browser.js
├── router/
│   ├── index.js                    # Route definitions
│   └── guards.js                   # Route-level permission guards
├── composables/
│   └── usePermissions.js          # Frontend permission checking
└── stores/
    └── auth.js                     # User & auth state
```

---

## Permission String Conventions

Permissions are named using dot notation:

```
module.action
inventory.view
inventory.create
inventory.view_cost
sales.void
repair.parts.allocate
admin.manage_users
reports.view_profit
```

### Permission Categories

| Category | Example | Purpose |
|----------|---------|---------|
| **View** | `inventory.view` | Can access/read resource |
| **Create** | `pos.create` | Can create new records |
| **Edit** | `inventory.edit` | Can modify existing records |
| **Delete** | `inventory.delete` | Can delete records |
| **Export** | `sales.export` | Can export data |
| **Approve** | `approve_void` | Can approve sensitive actions |
| **Manage** | `admin.manage_users` | Administrative actions |

---

## Testing Permissions

### Test User Accounts

| Username | Password | Role | Purpose |
|----------|----------|------|---------|
| `owner` | `owner123` | Shop Owner | Full access testing |
| `cashier` | `cashier123` | Salesperson | POS/cash operations |
| `technician` | `tech123` | Technician | Repair operations |

### Manual Testing

1. **Test Cashier accessing POS**:
   - ✅ Can create sales
   - ✅ Can view inventory (without costs)
   - ❌ Cannot void invoices
   - ❌ Cannot see profit reports

2. **Test Technician accessing repairs**:
   - ✅ Can view/create repair jobs
   - ✅ Can print service slips
   - ❌ Cannot access POS
   - ❌ Cannot view sales

3. **Test Owner accessing all modules**:
   - ✅ Can access all modules
   - ✅ Can view all data (costs, profits, audit logs)
   - ✅ Can approve voids
   - ✅ Can manage users

---

## Security Considerations

### API-Level Enforcement (Not UI-Only)

❌ **Don't do this** (UI-only, can be bypassed):
```javascript
// Only hiding button, user can still call API
v-if="isOwner"
```

✅ **Do this** (API enforces):
```javascript
// API checks permission before processing
POST /sales/invoices/:id/void/
→ If not authorized: 403 Forbidden
```

### Data Filtering

All sensitive fields are automatically removed from API responses for unauthorized users:
- Wholesale costs
- Profit margins
- Audit trails
- User activity logs

### Logging & Audit Trail

Every action by every user is logged:
- Who performed the action
- What action was performed
- When it was performed
- Whether it required approval

---

## Future Enhancements

1. **Time-Based Permissions**: Access available only during certain hours
2. **Branch-Level Permissions**: Different access per branch
3. **Dynamic Permission Groups**: Create custom role templates
4. **Approval Workflows**: Multi-level approval for sensitive actions
5. **Audit Events**: Detailed logging of permission checks and denials
6. **Permission Audit**: View who accessed what and when

---

## Troubleshooting

### User Can't Access POS
1. Check user role is `cashier`
2. Verify user has `pos.view` permission
3. Check route guard isn't blocking navigation
4. Review API response for 403 error

### Cost Data Showing When It Shouldn't
1. Verify user doesn't have `inventory.view_cost`
2. Check API response filtering in permission middleware
3. Review permission string in permission definitions

### Permission Denied on Valid Action
1. Check exact permission string matches (case-sensitive)
2. Verify user permissions array includes permission
3. Check if API requires multiple permissions (use hasAll)
4. Review middleware permission check logic

---

## References

- `src/api/mock/db/permissions.js` - Permission definitions and checkers
- `src/api/mock/middleware/permissionMiddleware.js` - API enforcement
- `src/composables/usePermissions.js` - Frontend permission composable
- `src/router/guards.js` - Route-level guards
- `RBAC.md` (this file) - Documentation
