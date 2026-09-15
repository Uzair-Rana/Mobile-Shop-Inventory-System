# Role Switcher - Visual Location Guide

## 🗺️ Where to Find It

### Step 1: Open Settings
```
Sidebar (Left)
├── Dashboard
├── POS
├── Inventory
├── Sales
├── Repairs
├── Customers
├── Installments
├── Cash
├── Reports
├── ...
└── Settings ⚙️  ← CLICK HERE
```

### Step 2: Settings Page Opens
```
┌─────────────────────────────────────┐
│       DEVNEST Settings              │
├─────────────────────────────────────┤
│ Company    Users    Roles    Tax     │
│ Audit Log                           │
├─────────────────────────────────────┤
│ Company Settings Section:           │
│                                     │
│ [Company Name Input Field]          │
│ [Address Input Field]               │
│ [Phone Input Field]                 │
│ [Email Input Field]                 │
│ [NTN/Tax ID Input Field]           │
│ [Website Input Field]               │
│                                     │
│ [Save Changes Button] →             │
│                                     │
│                                     │
│ ROLE SWITCHER (Below) ↓             │
│ ┌──────────────────────────────────┐│
│ │ Quick Role Switch                 ││
│ │ Testing & Development Only        ││
│ │                                   ││
│ │ Current Role: Shop Owner          ││
│ │                                   ││
│ │ [ 👑 Shop Owner     ] [Active]   ││
│ │ [ 💳 Salesperson    ]            ││
│ │ [ 🔧 Technician     ]            ││
│ │                                   ││
│ │ ▸ Test Credentials               ││
│ │   owner / owner123               ││
│ │   cashier / cashier123           ││
│ │   technician / tech123           ││
│ └──────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

---

## 🎨 Role Switcher Component

```
┌────────────────────────────────────────────────────┐
│                                                    │
│  Quick Role Switch                                 │
│  Testing & Development Only                        │
│                                                    │
│  Current Role: 👤 Shop Owner / Super Admin        │
│                                                    │
│  ┌─────────────────────────────────────────────┐ │
│  │ 👑 Shop Owner / Super Admin    [ACTIVE]     │ │
│  │ Full unrestricted access to all modules     │ │
│  └─────────────────────────────────────────────┘ │
│                                                    │
│  ┌─────────────────────────────────────────────┐ │
│  │ 💳 Salesperson / Cashier                    │ │
│  │ POS operations and cash management only     │ │
│  └─────────────────────────────────────────────┘ │
│                                                    │
│  ┌─────────────────────────────────────────────┐ │
│  │ 🔧 Technician / Repair Desk                │ │
│  │ Repair jobs and related functions only      │ │
│  └─────────────────────────────────────────────┘ │
│                                                    │
│  ▸ Test Credentials                               │
│      owner           owner123                     │
│      cashier         cashier123                   │
│      technician      tech123                      │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 📱 How It Looks in the App

### Full Page View
```
┌──────────────────────────────────────────────┐
│  DEVNEST · Mobile Shop ERP                   │
├──────────────────────────────────────────────┤
│                                              │
│  Settings Tab Selected                       │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Company Settings Form                  │ │
│  ├────────────────────────────────────────┤ │
│  │ Company Name: [DEVNEST Electronics  ] │ │
│  │ Address:      [123 Main St, City    ] │ │
│  │ Phone:        [+92-300-1234567      ] │ │
│  │ Email:        [info@devnest.local   ] │ │
│  │ NTN/Tax ID:   [1234567-8            ] │ │
│  │ Website:      [www.devnest.local    ] │ │
│  │                      [Save Changes] │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 🎭 Quick Role Switch 🎭                │ │
│  │ Testing & Development Only             │ │
│  │                                        │ │
│  │ Current: Shop Owner                    │ │
│  │                                        │ │
│  │ [👑 Owner] [💳 Cashier] [🔧 Tech]    │ │
│  │                                        │ │
│  │ ▸ Test Credentials                     │ │
│  └────────────────────────────────────────┘ │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 🔄 Role Switching Flow

```
User in Settings
    │
    └─ Sees Role Switcher Card
         │
         ├─ Click [👑 Shop Owner]
         │  │
         │  └─ Current role already, nothing changes
         │
         ├─ Click [💳 Cashier]
         │  │
         │  └─ Loading... (shows spinner)
         │     │
         │     ├─ 1. Logs out Shop Owner
         │     ├─ 2. Logs in as Cashier (cashier123)
         │     ├─ 3. Gets new authorization token
         │     ├─ 4. Updates user permissions
         │     ├─ 5. Refreshes sidebar (shows/hides modules)
         │     ├─ 6. Redirects to Dashboard
         │     │
         │     └─ Toast: "Switched to Salesperson role"
         │
         └─ Click [🔧 Technician]
            │
            └─ Same flow, switches to Technician role
```

---

## 🎯 What Happens When You Click a Role

### Before Click
```
You are: Shop Owner
├─ Can see: All modules (POS, Inventory, Repairs, Reports, Admin, etc.)
├─ Can see: Cost prices
├─ Can see: Profit data
├─ Can see: Audit logs
└─ Sidebar shows: All menu items
```

### During Click (Loading)
```
Switching...
├─ Button shows spinner
├─ Toast appears at bottom
└─ All interactions disabled (can't click other buttons)
```

### After Click
```
You are: Cashier
├─ Can see: Only POS, Customers, Cash modules
├─ Can NOT see: Cost prices (API filters them)
├─ Can NOT see: Profit data
├─ Can NOT see: Audit logs
├─ Can NOT see: Admin menu
├─ Sidebar updated: Shows only Cashier-accessible modules
├─ Toast: "Switched to Salesperson role"
└─ Redirected to: Dashboard
```

---

## 💾 Test Credentials Reference

Expand the "Test Credentials" section to see:

```
┌─────────────────────────────────┐
│ ▾ Test Credentials              │ ← Click to expand
├─────────────────────────────────┤
│ owner         owner123          │
│ cashier       cashier123        │
│ technician    tech123           │
└─────────────────────────────────┘
```

Each row shows:
- **Left**: Username
- **Right**: Password

---

## 🚀 Quick Start (3 Steps)

### Step 1️⃣: Open Settings
- Click the ⚙️ **Settings** icon in the sidebar

### Step 2️⃣: Find Role Switcher
- Scroll down on the Company Settings page
- Look for the purple **"Quick Role Switch"** card

### Step 3️⃣: Click a Role Button
- 👑 **Shop Owner** → Full access
- 💳 **Salesperson** → POS only
- 🔧 **Technician** → Repair only

---

## ✨ Features at a Glance

| Feature | What It Does |
|---------|-------------|
| **One-Click Switch** | Change roles instantly without logout |
| **Shows Current Role** | Badge displays your current role |
| **Loading State** | Visual feedback while switching |
| **Toast Notification** | Confirms role change with message |
| **Credential Display** | View test user passwords in one place |
| **Mobile Responsive** | Works on phone, tablet, desktop |
| **Active State** | Current role button is highlighted |
| **Auto Redirect** | Goes to dashboard after switching |

---

## 📍 Location Summary

```
App → Settings (⚙️) → Company Settings Tab
                          ↓
                   [Company Form]
                          ↓
                   [Role Switcher] ← YOU ARE HERE
```

---

## 🎓 Educational Purpose

The Role Switcher is designed for:
- ✅ Testing different user roles
- ✅ Verifying permission boundaries
- ✅ Checking API-level enforcement
- ✅ Seeing how UI updates for different roles
- ✅ Confirming data filtering works
- ✅ Learning about RBAC system

---

## 🔐 Security Note

> The Role Switcher is **Testing/Development Only**
> 
> In production, users authenticate normally through login screen.
> This quick switcher only exists to make testing easier!

---

Ready to test roles? Go to **Settings** now! 🎭
