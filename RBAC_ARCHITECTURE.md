# RBAC System Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  (Vue Components with usePermissions composable)                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─ Route Guards ─┐
             │                │ Checks route.meta.requiresPermission
             │                └─→ Redirects unauthorized users
             │
    ┌────────┴──────────┐
    │                   │
    ▼                   ▼
┌─────────────────┐ ┌──────────────────┐
│ Show UI Element │ │ Hide UI Element  │
│ (has perm)      │ │ (no perm)        │
└─────────────────┘ └──────────────────┘
    │                   │
    │ API Request       │ (button disabled/hidden)
    │ (with token)      │
    │                   │
    └───────────┬───────┘
                │
                ▼
    ┌─────────────────────────────┐
    │   API REQUEST TO SERVER     │
    │   Authorization: Token xxx  │
    └───────────┬─────────────────┘
                │
                ▼
    ┌───────────────────────────────────────────┐
    │         MSW HANDLER / API ENDPOINT        │
    │                                           │
    │ 1. Get user from token                    │
    │ 2. Call checkPermission(user, 'perm.id') │
    │ 3. If denied: return 403                  │
    │ 4. If allowed: process request           │
    │ 5. Filter sensitive data from response   │
    └───────────┬─────────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
    ┌────────────┐  ┌──────────────┐
    │ 403 Error  │  │ 200 Success  │
    │ Permission │  │ Filtered     │
    │ Denied     │  │ Response     │
    └────────────┘  └──────────────┘
```

## Role Permission Flow

```
                    ┌──────────────────────┐
                    │   USER LOGS IN       │
                    │ username/password    │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ POST /auth/login/    │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Valid credentials?   │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
            ┌────────┐                   ┌────────┐
            │  YES   │                   │   NO   │
            └────┬───┘                   └────┬───┘
                 │                            │
     ┌───────────▼────────────┐      ┌────────▼──────────┐
     │ Get User from DB       │      │ Return 400 Error  │
     │ with permissions array │      │ "Invalid creds"   │
     └───────────┬────────────┘      └───────────────────┘
                 │
     ┌───────────▼────────────┐
     │ Generate token         │
     │ Return user + token    │
     └───────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │ Frontend stores token   │
    │ (in auth store)         │
    └────────────┬────────────┘
                 │
    ┌────────────▼──────────────────────┐
    │ Future API requests include token │
    │ Authorization: Token xxx          │
    └────────────┬──────────────────────┘
                 │
    ┌────────────▼──────────────────────┐
    │ API validates token & gets user   │
    │ User has permissions array        │
    └────────────┬──────────────────────┘
                 │
    ┌────────────▼──────────────────────┐
    │ Check if user has permission      │
    │ for this action                   │
    └────────────┬──────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
         ▼               ▼
     ┌────────┐      ┌─────────┐
     │ ALLOW  │      │  DENY   │
     └────┬───┘      └────┬────┘
          │               │
    ┌─────▼──────┐  ┌─────▼──────────┐
    │ Process    │  │ Return 403     │
    │ request    │  │ "Permission    │
    │ Filter data│  │  denied"       │
    │ Return 200 │  └────────────────┘
    └────────────┘
```

## Three Role Separation

```
                       ALL USERS
                          │
                    ┌─────┼─────┐
                    │     │     │
                    ▼     ▼     ▼
              ┌────────┐ ┌────────┐ ┌──────────┐
              │ OWNER  │ │CASHIER │ │TECHNICIAN│
              └────┬───┘ └────┬───┘ └────┬─────┘
                   │          │          │
    ┌──────────────┼──────────┼──────────┼──────────┐
    │              │          │          │          │
    ▼              ▼          ▼          ▼          ▼
┌────────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ ┌─────────────┐
│ Inventory  │ │  POS   │ │ Repairs│ │  Reports │ │Admin Panel  │
│ ✅ Full    │ │✅ Full │ │✅ Full │ │✅ Full   │ │✅ Full      │
└────────────┘ └────────┘ └────────┘ └──────────┘ └─────────────┘
                │          │          │               │
    ┌───────────▼──┐   ┌───▼───────┐  ├─ View POS    │
    │ View/Create/ │   │ View/Full  │  │ Create Sale │ ✅ Manage
    │ Edit/Delete  │   │ Operations │  │ ❌ Void     │    Users
    │ View Costs   │   │ No Void    │  │ ❌ Export   │ ✅ Approve
    │ View Profit  │   │ View Costs │  │ ❌ View     │    Voids
    │ Audit Logs   │   │ ❌ Profit  │  │    Costs    │ ✅ Audit
    │ Approvals    │   │ ❌ Reports │  │            │    Logs
    │ Settings     │   │ ❌ Admin   │  │            │
    └───────────────┘   └────────────┘  └──────────┘ └─────────────┘
         55+ perms       12 perms         10 perms      15+ perms
```

## Permission Check Sequence

```
REQUEST ARRIVES
    │
    ▼
┌─────────────────────────────┐
│ 1. Extract Authorization    │
│    Header: "Token xxx"      │
└────────────┬────────────────┘
             │
    ┌────────▼────────┐
    │ 2. Validate     │
    │    Token       │
    └────────┬────────┘
             │
    ┌────────▼────────────────────┐
    │ 3. Get User from Database    │
    │    - id                      │
    │    - role                    │
    │    - permissions array       │
    │    - is_superuser flag       │
    └────────┬────────────────────┘
             │
    ┌────────▼────────────────────┐
    │ 4. Check Permission          │
    │                              │
    │    if (user.is_superuser)    │
    │      return ALLOWED          │
    │                              │
    │    if (permissions.includes  │
    │        (required))           │
    │      return ALLOWED          │
    │                              │
    │    else                      │
    │      return DENIED           │
    └────────┬────────────────────┘
             │
     ┌───────┴────────┐
     │                │
     ▼                ▼
  ALLOWED          DENIED
     │                │
     ▼                ▼
┌────────────┐    ┌──────────────┐
│ 5. Process │    │ 6. Return    │
│    Request │    │    403 Error │
│            │    │              │
│ 6. Filter  │    │ "Permission  │
│    Data    │    │  Denied"     │
│            │    │              │
│ 7. Return  │    │ Stop         │
│    200 OK  │    │              │
└────────────┘    └──────────────┘
```

## Frontend vs Backend Permission Check

```
┌─────────────────────────────────────┐
│        FRONTEND (Client-Side)       │
│                                     │
│  usePermissions() Composable        │
│  ├─ canCreateSale                   │
│  ├─ canVoidSale                     │
│  ├─ canViewProfit                   │
│  └─ ... 60+ permissions             │
│                                     │
│  Used for:                          │
│  ✅ Show/hide UI elements           │
│  ✅ Enable/disable buttons          │
│  ✅ Route navigation                │
│                                     │
│  BUT: User can bypass with          │
│  ❌ Browser dev tools               │
│  ❌ Direct API calls                │
└────────────┬────────────────────────┘
             │
      [NOT SECURE ALONE]
             │
             ▼
┌─────────────────────────────────────┐
│       BACKEND (Server-Side)         │
│                                     │
│  Permission Middleware              │
│  ├─ checkPermission()               │
│  ├─ filterSensitiveData()           │
│  ├─ forbiddenResponse()             │
│  └─ ... validation logic            │
│                                     │
│  Used for:                          │
│  ✅ Validate every API request      │
│  ✅ Filter response data            │
│  ✅ Enforce business rules          │
│  ✅ Log access attempts             │
│                                     │
│  User CANNOT bypass:                │
│  🔒 Token validation                │
│  🔒 Permission checking             │
│  🔒 Data filtering                  │
│  🔒 API enforcement                 │
└─────────────────────────────────────┘

RESULT: Double-layer security
├─ Frontend: Good UX (hide forbidden options)
└─ Backend: Real security (enforce rules)
```

## Data Flow: Creating a Sale

```
CASHIER (Limited User)
   │
   ├─ Sees "Create Sale" button (frontend check passed)
   │
   └─ Clicks button
       │
       ▼
   Frontend calls:
   POST /sales/invoices/
   Authorization: Token cashier-token
   Body: {customer, items, total}
       │
       ▼
   API Handler receives request
       │
       ├─ Validate token ✓
       ├─ Get user (cashier)
       │
       ├─ Check: has permission 'pos.create'?
       │  ├─ is_superuser? NO
       │  └─ permissions.includes('pos.create')? YES ✓
       │
       ├─ ALLOWED: Process request
       │
       ├─ Create invoice in database
       │
       └─ Prepare response:
           {
             invoice_id: 123,
             customer: "John Doe",
             items: [...],
             total: 5000,
             cost_price: REMOVED ← Filtered
             wholesale_cost: REMOVED ← Filtered
             profit: REMOVED ← Filtered
           }
           │
           ▼
       Return 200 OK (filtered response)
           │
           ▼
       Frontend displays success
       Cashier can see invoice (without costs)
```

## Data Flow: Trying to Void (Technician)

```
TECHNICIAN (Repair-Only User)
   │
   └─ Cannot see "Void" button (frontend hides it)
       │
       └─ But tries to call API anyway:
           │
           ▼
       POST /sales/invoices/123/void/
       Authorization: Token technician-token
       Body: {reason: "Wrong item"}
           │
           ▼
       API Handler receives request
           │
           ├─ Validate token ✓
           ├─ Get user (technician)
           │
           ├─ Check: has permission 'sales.void'?
           │  ├─ is_superuser? NO
           │  └─ permissions.includes('sales.void')? NO ✗
           │
           ├─ DENIED: Permission check failed
           │
           └─ Return 403 Forbidden:
              {
                detail: "You do not have permission to perform this action",
                code: "permission_denied"
              }
              │
              ▼
           No invoice voided
           Frontend shows error toast
           Technician sees: "Permission denied"
```

## Files Interaction Map

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
├─────────────────────────────────────────────────────────────┤
│  Components use:                                            │
│  ├─ usePermissions()                                        │
│  │  └─ reads auth.user.permissions                         │
│  └─ Route guards in <RouterView>                           │
└────────┬─────────────────────────────────┬─────────────────┘
         │                                 │
         ▼                                 ▼
    ┌─────────────────────┐    ┌──────────────────────┐
    │ src/composables/    │    │ src/router/          │
    │ usePermissions.js   │    │ guards.js            │
    │                     │    │                      │
    │ ├─ has()            │    │ ├─ setupRouteGuards()│
    │ ├─ hasAny()         │    │ ├─ checkPermission() │
    │ ├─ canCreateSale    │    │ └─ forbiddenResponse │
    │ ├─ canViewProfit    │    │                      │
    │ └─ ... 60+ perms    │    │ Blocks unauthorized  │
    │                     │    │ route navigation     │
    └────────┬────────────┘    └──────────┬───────────┘
             │                           │
             └──────────────┬────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │ src/main.js      │
                    │                  │
                    │ Registers guards │
                    │ on app start     │
                    └──────┬───────────┘
                           │
                           ▼
              ┌────────────────────────────┐
              │   API LAYER / MSW          │
              │   (Mock Service Worker)    │
              └──────────┬─────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐  ┌──────────────┐  ┌──────────────┐
    │auth.js  │  │sales.js      │  │repairs.js    │
    │         │  │              │  │              │
    │├─login()│  │├─listInvoices│  │├─listRepairs │
    │├─logout │  │├─createInvoice│ │├─createRepair│
    │└─me()   │  │├─voidInvoice │ │├─updateStatus│
    │         │  │└─...         │  │└─...         │
    └────┬────┘  └────┬─────────┘  └────┬─────────┘
         │             │                 │
         └─────────────┼─────────────────┘
                       │
                       ▼
         ┌──────────────────────────────┐
         │  permissionMiddleware.js      │
         │                              │
         │  ├─ checkPermission()         │
         │  ├─ filterSensitiveData()     │
         │  ├─ forbiddenResponse()       │
         │  └─ data filtering logic      │
         │                              │
         │  EVERY endpoint uses this    │
         └────────────┬─────────────────┘
                      │
                      ▼
         ┌──────────────────────────────┐
         │ permissions.js               │
         │                              │
         │ ├─ Permission definitions    │
         │ ├─ hasPermission()           │
         │ ├─ roleDefinitions          │
         │ └─ access control helpers    │
         │                              │
         │ Data source for checks       │
         └────────────┬─────────────────┘
                      │
                      ▼
         ┌──────────────────────────────┐
         │ fixtures/users.js            │
         │                              │
         │ ├─ owner role               │
         │ │  └─ 55+ permissions       │
         │ │                            │
         │ ├─ cashier role             │
         │ │  └─ 12 permissions        │
         │ │                            │
         │ └─ technician role          │
         │    └─ 10 permissions        │
         │                              │
         │ User data with permissions   │
         └──────────────────────────────┘
```

---

## Summary

The RBAC system uses a **layered approach**:

1. **Frontend Layer** (Client-side)
   - Route guards prevent navigation
   - Permission composable shows/hides UI
   - Better UX, but can be bypassed

2. **Backend Layer** (Server-side)
   - Every API endpoint checks permissions
   - Returns 403 if unauthorized
   - Filters sensitive data from responses
   - Enforces business rules
   - **Cannot be bypassed**

3. **Data Layer** (Database)
   - Users have permission arrays
   - Roles have distinct permission sets
   - Audit logs track all access

**Result**: Secure, layered permission system where authorization is enforced at the API level, not just the UI.
