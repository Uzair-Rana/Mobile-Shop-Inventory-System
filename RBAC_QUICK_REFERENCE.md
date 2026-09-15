# RBAC Quick Reference Guide

## Test Users

| Role | Username | Password | Use Case |
|------|----------|----------|----------|
| **Owner** | `owner` | `owner123` | Test full access, admin features |
| **Cashier** | `cashier` | `cashier123` | Test POS, cash management |
| **Technician** | `technician` | `tech123` | Test repair desk only |

## Permission Strings

### Inventory
- `inventory.view` - Read products
- `inventory.create` - Add new products
- `inventory.edit` - Modify products
- `inventory.delete` - Remove products
- `inventory.view_cost` - See wholesale/cost prices ⚠️ **Hidden from cashiers**

### POS & Sales
- `pos.view` - Access POS interface
- `pos.create` - Create sales (finalize transactions)
- `pos.edit` - Modify draft sales
- `sales.view` - View invoices
- `sales.void` - Void/cancel invoices ⚠️ **Requires approval**
- `sales.export` - Export sales data
- `sales.view_cost` - See product costs in sales

### Repairs
- `repair.view` - View repair jobs
- `repair.create` - Create new repair job
- `repair.edit` - Edit repair details
- `repair.update_status` - Change job status
- `repair.print_slip` - Print service slip
- `repair.view_diagnostics` - View device diagnostics
- `repair.parts.allocate` - Assign parts
- `repair.parts.track` - Track part usage

### Reports & Analytics
- `reports.view` - Access reports module
- `reports.view_profit` - See profit/margin data ⚠️ **Hidden from cashiers**
- `reports.view_cost` - See cost analysis
- `reports.export` - Export reports

### Admin
- `admin.view` - Access admin panel
- `admin.configure` - Change settings
- `admin.manage_users` - Create/edit users
- `admin.manage_roles` - Manage roles/permissions
- `admin.view_audit_log` - View audit trail ⚠️ **Hidden from non-owners**

### Cash Management
- `cash.session.view` - View cash drawer
- `cash.session.reconcile` - Daily reconciliation
- `cash.expense.view` - View expenses
- `cash.expense.create` - Record expenses

### Customer
- `customer.view` - View customer list
- `customer.create` - Add customers
- `customer.edit` - Modify customer info
- `customer.inquire_balance` - Check payment status
- `customer.inquire_stock` - Check availability

### Approvals ⚠️ **Owner-only**
- `approve_void` - Approve invoice voids
- `approve_reversal` - Approve reversals
- `approve_discount` - Approve discounts

### WhatsApp
- `whatsapp.broadcast_stock` - Send stock updates
- `whatsapp.send_invoice` - Send invoice links

⚠️ = Sensitive permission, restricted to specific roles

## Frontend Usage

### Check Single Permission
```javascript
const { canCreateSale } = usePermissions()

if (canCreateSale.value) {
  // Show create sale button
}
```

### Check Multiple Permissions
```javascript
const { canVoidSale, canApproveVoid } = usePermissions()

if (canVoidSale.value && canApproveVoid.value) {
  // Show void + approve workflow
}
```

### Check Role
```javascript
const { isOwner, isCashier, isTechnician } = usePermissions()

if (isCashier.value) {
  // Cashier-specific UI
}
```

### Available Modules
```javascript
const { accessibleModules } = usePermissions()

// Shows boolean for each module
accessibleModules.value.pos        // true/false
accessibleModules.value.repairs    // true/false
accessibleModules.value.showCost   // true/false
accessibleModules.value.showProfit // true/false
```

## API-Level Enforcement

All endpoints check permissions. Examples:

### Create Sale (requires: `pos.create`)
```javascript
POST /sales/invoices/
Authorization: Token xxx

// Owner ✅ | Cashier ✅ | Technician ❌ (403 Forbidden)
```

### View Profit (requires: `reports.view_profit`)
```javascript
GET /reports/daily-summary/?date=2024-01-01
Authorization: Token xxx

// Owner ✅ | Cashier ❌ (data filtered) | Technician ❌ (403 Forbidden)
```

### Void Invoice (requires: `sales.void`)
```javascript
POST /sales/invoices/1/void/
Authorization: Token xxx

// Owner ✅ | Cashier ❌ (403 Forbidden) | Technician ❌ (403 Forbidden)
```

## Updating User Permissions

Edit `src/api/mock/db/fixtures/users.js`:

```javascript
{
  id: 2,
  username: 'cashier',
  // ... other fields ...
  permissions: [
    'inventory.view',
    'pos.view',
    'pos.create',
    // Add new permission here
    'new.permission',
  ]
}
```

Changes take effect on next login.

## Route-Level Guards

Routes automatically check permissions:

```javascript
// src/router/index.js
{
  path: '/reports/profit',
  component: ProfitReportView,
  meta: {
    requiresPermission: 'reports.view_profit',
  }
}

// User without permission: redirected to /dashboard
```

## Debugging Permissions

### Check User Permissions
```javascript
const { user } = usePermissions()
console.log(user.value.permissions) // Array of permission strings
```

### Test Permission Check
```javascript
const { has } = usePermissions()
console.log(has('pos.create')) // true/false
```

### View Available Modules
```javascript
const { accessibleModules } = usePermissions()
console.log(accessibleModules.value) // Object with all module access
```

### Check Role
```javascript
const { isOwner, isCashier, isTechnician } = usePermissions()
console.log({
  isOwner: isOwner.value,
  isCashier: isCashier.value,
  isTechnician: isTechnician.value
})
```

## Common Tasks

### Add Permission to Cashier
1. Edit `src/api/mock/db/fixtures/users.js`
2. Add permission string to `permissions` array
3. Restart app (or re-login if already running)

### Create New Role
1. Add user fixture in `users.js` with new `role` value
2. Add permissions array
3. Add permission checks in API handlers
4. Add role helper in `usePermissions()`

### Hide Field for Specific Role
In API handler:
```javascript
const result = {
  ...invoice,
  // Hide cost from non-owners
  cost_price: user.is_superuser ? invoice.cost_price : undefined
}
```

Or use middleware:
```javascript
const filtered = filterSensitiveData(invoice, user)
```

### Require Multiple Permissions
```javascript
// All must have permission
const { hasAll } = usePermissions()
if (hasAll(['sales.void', 'approve_void'])) {
  // Can void AND approve
}

// Any must have permission
const { hasAny } = usePermissions()
if (hasAny(['reports.view_profit', 'admin.view_audit_log'])) {
  // Can view either profit or audit
}
```

## What Each Role CAN'T Do

### Cashier CAN'T
- ❌ See product cost prices
- ❌ View profit/margin reports
- ❌ Void/edit finalized sales
- ❌ Access repair desk
- ❌ Manage inventory
- ❌ Access admin panel
- ❌ View audit logs

### Technician CAN'T
- ❌ Access POS
- ❌ Create sales
- ❌ View customer balances
- ❌ Manage users
- ❌ View reports
- ❌ Access admin panel
- ❌ Manage inventory (except view for parts)

### Owner CAN
✅ Everything (no restrictions)

## Testing Checklist

- [ ] Login as each role
- [ ] Verify accessible modules
- [ ] Try to access forbidden routes (should redirect)
- [ ] Check sensitive data isn't visible
- [ ] Test permission-restricted buttons
- [ ] Verify API returns 403 for unauthorized requests
- [ ] Test permission filtering in API responses
- [ ] Verify audit logging works
- [ ] Test cash reconciliation as cashier
- [ ] Test repair workflow as technician

## Files Modified

- `src/api/mock/db/fixtures/users.js` - User roles & permissions
- `src/api/mock/db/permissions.js` - Permission utilities (new)
- `src/api/mock/middleware/permissionMiddleware.js` - API enforcement (new)
- `src/api/mock/handlers/sales.js` - Permission checks added
- `src/api/mock/handlers/auth.js` - Set current user context
- `src/composables/usePermissions.js` - Frontend permission checking (updated)
- `src/router/guards.js` - Route guards (new)
- `src/main.js` - Setup route guards
- `RBAC.md` - Full documentation (new)

---

📖 For detailed documentation, see **RBAC.md**
