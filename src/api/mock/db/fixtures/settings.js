export const companyFixture = {
    id: 1,
    name: 'DEVNEST Mobile Shop',
    address: 'Main Boulevard, Lahore, Pakistan',
    phone: '042-111-222-333',
    email: 'info@devnest.pk',
    ntn: '1234567-8',
    website: 'www.devnest.pk',
    currency: 'PKR',
    logo: '',
}

export const taxFixtures = [
    { id: 1, name: 'GST', rate: 17.0, is_active: true, applies_to: 'sales' },
    { id: 2, name: 'No Tax', rate: 0.0, is_active: true, applies_to: 'sales' },
]

export const receiptConfigFixture = {
    id: 1,
    header_text: 'DEVNEST Mobile Shop',
    footer_text: 'Thank you for shopping with us!',
    show_logo: true,
    show_tax_breakdown: true,
    paper_size: '80mm',
}
