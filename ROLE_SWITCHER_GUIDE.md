# Role Switcher - Quick Guide

## 📍 Where to Find It

The **Role Switcher** is located in the **Settings → Company Settings** page.

### Steps to Access:
1. Click the **⚙️ Settings** icon in the sidebar (bottom of navigation)
2. The **Company Settings** page will open
3. Scroll down to see the **"Quick Role Switch"** purple card

---

## 🎭 How to Use It

### Visual Layout
```
┌─────────────────────────────────────────┐
│  Quick Role Switch                      │
│  Testing & Development Only             │
│                                         │
│  Current Role: [Shop Owner]             │
│                                         │
│  [ 👑 Shop Owner    ]                   │
│  [ 💳 Salesperson   ]                   │
│  [ 🔧 Technician    ]                   │
│                                         │
│  ▸ Test Credentials                     │
│    owner      owner123                  │
│    cashier    cashier123                │
│    technician tech123                   │
└─────────────────────────────────────────┘
```

### To Switch Roles:
1. Find the **Role Switcher** card in Settings
2. Click one of the three role buttons:
   - 👑 **Shop Owner** - Full access
   - 💳 **Salesperson** - POS only
   - 🔧 **Technician** - Repair only
3. Wait for the role to switch (shows loading state)
4. You'll see a success toast: "Switched to [Role] role"
5. **Automatic redirect** to dashboard
6. **All your permissions update immediately**

---

## 🧪 Testing Different Roles

### Test 1: Shop Owner (Full Access)
1. Switch to **👑 Shop Owner**
2. Navigate to:
   - ✅ Inventory → See product costs
   - ✅ POS → Create and void sales
   - ✅ Reports → View profit data
   - ✅ Admin → Manage users

### Test 2: Salesperson (POS Only)
1. Switch to **💳 Salesperson**
2. Navigate to:
   - ✅ POS → Create sales (void button hidden)
   - ❌ Inventory → Try to view products (should redirect)
   - ❌ Reports → Access denied
   - ❌ Admin → Access denied
3. Create a sale:
   - ✅ Price shown
   - ❌ Cost price **NOT shown** (filtered by API)
   - ✅ Finalize sale works
   - ❌ Void button missing

### Test 3: Technician (Repair Only)
1. Switch to **🔧 Technician**
2. Navigate to:
   - ✅ Repairs → View repair jobs
   - ❌ POS → Try to create sale (should redirect)
   - ❌ Inventory → Access denied
   - ❌ Reports → Access denied
   - ❌ Admin → Access denied

---

## 🔐 What Gets Updated When You Switch

When you click a role button:

| What Changes | Details |
|---|---|
| **User Account** | Logs out current user, logs in as new user |
| **Permissions** | User's full permission array is loaded |
| **UI Elements** | All buttons/menus update based on new permissions |
| **API Requests** | Authorization token changes for new user |
| **Data Visibility** | Cost/profit data filtering updates |
| **Route Access** | New user can only access permitted routes |
| **Sidebar** | Menu items show/hide based on new role |

---

## ✅ Features of the Role Switcher

- **One-Click Switching** - No need to logout/login manually
- **Shows Current Role** - See which role you're logged in as
- **Test Credentials Display** - Expandable section shows username/password
- **Loading Indicator** - Shows when role switch is in progress
- **Toast Notifications** - Confirms role switch or shows errors
- **Responsive Design** - Works on mobile and desktop
- **Active State** - Current role button is highlighted

---

## 📊 Test Credentials (Expanded View)

Click **▸ Test Credentials** to expand and see:

```
owner       | owner123
cashier     | cashier123
technician  | tech123
```

---

## 🔍 Verify Permissions Are Working

After switching roles, verify permissions work:

### Check 1: UI Elements Update
- Look at sidebar menu - modules should show/hide
- Look at buttons - should be enabled/disabled based on role
- Look for cost fields - should disappear for cashier

### Check 2: Try Forbidden Action
- As **Cashier**: Try to access `/admin` → Should redirect to dashboard
- As **Technician**: Try to access `/pos` → Should redirect with error
- As **Owner**: All modules accessible ✅

### Check 3: API Data Filtering
As **Cashier**:
1. Create a sale
2. Open browser DevTools (F12)
3. Go to Network tab
4. Look at POST /sales/invoices/ response
5. Should **NOT see**: `cost_price`, `wholesale_cost`, `profit`
6. Should **see**: `invoice_id`, `customer`, `items`, `total`

---

## 🎯 Common Testing Scenarios

### Scenario 1: Cashier Can't Void Sales
```
1. Switch to Cashier (💳)
2. Go to POS → Create a sale
3. View invoice → Void button should be hidden
4. Try API directly: POST /sales/invoices/1/void/
5. Should get 403 Forbidden error
```

### Scenario 2: Technician Can't Access POS
```
1. Switch to Technician (🔧)
2. Try to navigate to /pos
3. Should be redirected to /dashboard
4. Should see toast: "You do not have permission to access this page"
```

### Scenario 3: Cost Data Filtering
```
1. Switch to Technician (🔧)
2. Go to Repairs → Create repair job
3. API response should NOT include:
   - cost_price
   - wholesale_cost
   - profit_margin
4. Switch to Owner (👑)
5. Same action → API response INCLUDES all cost fields
```

---

## 🚀 Quick Test Checklist

After switching roles, verify:

- [ ] Sidebar menu updated (modules show/hide)
- [ ] Buttons enabled/disabled correctly
- [ ] Forbidden pages redirect to dashboard
- [ ] Toast messages appear
- [ ] Cost data hidden from non-authorized users
- [ ] API returns 403 for unauthorized actions
- [ ] Current role badge updated
- [ ] Browser console shows no errors

---

## ❓ Troubleshooting

### Role Didn't Switch
- Check console (F12) for errors
- Make sure internet is working
- Try refreshing the page
- Check if MSW (Mock API) is active

### Permissions Not Updating
- Clear browser cache
- Close and reopen Settings page
- Verify you're actually logged in as new user
- Check current role badge in switcher

### Can't Find Role Switcher
- Go to Settings (⚙️ icon in sidebar)
- Make sure you're on "Company Settings" tab
- Scroll down - it's below the company form

### API Still Returns Unauthorized
- Check Authorization header includes correct token
- Verify user has the required permission
- Check permission string matches exactly (case-sensitive)
- Look at `/api/mock/db/fixtures/users.js` to verify permission exists

---

## 📝 Notes

- **Testing/Development Only**: The Role Switcher is meant for testing RBAC system
- **Not for Production**: In production, proper authentication UI is used
- **Mock API**: Works with MSW (Mock Service Worker)
- **Real Backend**: When connected to real backend, use normal login/logout
- **Permissions Enforcement**: API layer always enforces permissions, regardless of how you authenticate

---

## 🔗 Related Documentation

- `RBAC.md` - Complete RBAC documentation
- `RBAC_QUICK_REFERENCE.md` - Permission strings reference
- `RBAC_ARCHITECTURE.md` - System architecture
- `IMPLEMENTATION_SUMMARY.md` - Implementation overview

---

## 💡 Pro Tips

1. **Quick Testing**: Use Role Switcher to test permission boundaries quickly
2. **API Testing**: Open DevTools Network tab while switching to see token changes
3. **Permission List**: Click "Test Credentials" to see all test users in one place
4. **Compare Behavior**: Switch between roles and do the same action to see differences
5. **Check Audit Trail**: As Owner, view audit logs to see actions by other users

---

**Status**: ✅ Role Switcher is ready for use in Settings page!
