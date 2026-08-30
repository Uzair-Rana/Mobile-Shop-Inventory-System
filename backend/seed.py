"""
Quick seed script — creates a superuser, a default branch,
and the built-in permission set.

Usage:
    python manage.py shell < seed.py
    OR
    python seed.py  (if DJANGO_SETTINGS_MODULE is set)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devnest.settings')
django.setup()

from apps.users.models import User, Role, Permission
from apps.branches.models import Branch
from rest_framework.authtoken.models import Token

# ── Permissions ──────────────────────────────────────────────────────────────
PERMISSIONS = [
    # Inventory
    ('view_inventory',      'View Inventory'),
    ('add_inventory',       'Add Inventory'),
    ('edit_inventory',      'Edit Inventory'),
    ('view_cost',           'View Cost Price'),
    ('adjust_cost',         'Adjust Cost Price'),
    # Sales / POS
    ('view_sales',          'View Sales'),
    ('create_sale',         'Create Sale'),
    ('void_invoices',       'Void Invoices'),
    ('apply_discount',      'Apply Discount'),
    ('discount_override',   'Override Discount Threshold'),
    ('view_profit',         'View Profit/Margin'),
    # Repairs
    ('view_repairs',        'View Repairs'),
    ('manage_repairs',      'Manage Repairs'),
    # Purchases
    ('view_purchases',      'View Purchases'),
    ('manage_purchases',    'Manage Purchases'),
    # Installments
    ('view_installments',   'View Installments'),
    ('manage_installments', 'Manage Installments'),
    # Cash
    ('view_cash',           'View Cash Sessions'),
    ('manage_cash',         'Manage Cash Sessions'),
    # Customers
    ('view_customers',      'View Customers'),
    ('manage_customers',    'Manage Customers'),
    # Reports
    ('view_reports',        'View Reports'),
    ('export_reports',      'Export Reports'),
    # Transfers
    ('view_transfers',      'View Transfers'),
    ('manage_transfers',    'Manage Transfers'),
    # Admin
    ('manage_users',        'Manage Users & Roles'),
    ('view_audit_log',      'View Audit Log'),
    ('manage_settings',     'Manage Settings'),
]

created_count = 0
for codename, name in PERMISSIONS:
    _, created = Permission.objects.get_or_create(codename=codename, defaults={'name': name})
    if created:
        created_count += 1

print(f'✓ Permissions: {created_count} created, {len(PERMISSIONS) - created_count} already existed')

# ── Roles ────────────────────────────────────────────────────────────────────
all_perms = Permission.objects.all()

admin_role, _ = Role.objects.get_or_create(
    name='Admin',
    defaults={'description': 'Full access'}
)
admin_role.permissions.set(all_perms)

cashier_perms = Permission.objects.filter(codename__in=[
    'view_inventory', 'view_sales', 'create_sale', 'apply_discount',
    'view_customers', 'manage_customers', 'view_repairs',
    'view_installments', 'view_cash',
])
cashier_role, _ = Role.objects.get_or_create(
    name='Cashier',
    defaults={'description': 'POS and basic operations'}
)
cashier_role.permissions.set(cashier_perms)

technician_perms = Permission.objects.filter(codename__in=[
    'view_inventory', 'view_repairs', 'manage_repairs', 'view_customers',
])
tech_role, _ = Role.objects.get_or_create(
    name='Technician',
    defaults={'description': 'Repair jobs only'}
)
tech_role.permissions.set(technician_perms)

print('✓ Roles: Admin, Cashier, Technician ready')

# ── Default Branch ───────────────────────────────────────────────────────────
branch, created = Branch.objects.get_or_create(
    name='Main Branch',
    defaults={
        'address': '123 Main Street',
        'phone': '0300-0000000',
        'is_default': True,
    }
)
print(f'✓ Branch: {"created" if created else "already exists"} → {branch.name} (id={branch.id})')

# ── Superuser ────────────────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@devnest.local',
        full_name='System Admin',
        role=admin_role,
        branches=[branch.id],
    )
    Token.objects.get_or_create(user=user)
    print('✓ Superuser created → username: admin | password: admin123')
else:
    print('✓ Superuser "admin" already exists')

print('\n🚀 Seed complete. Run: python manage.py runserver')
