import client from './client'

export const settingsApi = {
    getCompany: () => client.get('/settings/company/'),
    updateCompany: (data) => client.patch('/settings/company/', data),

    listUsers: (params) => client.get('/settings/users/', { params }),
    getUser: (id) => client.get(`/settings/users/${id}/`),
    createUser: (data) => client.post('/settings/users/', data),
    updateUser: (id, data) => client.patch(`/settings/users/${id}/`, data),
    deactivateUser: (id) => client.post(`/settings/users/${id}/deactivate/`),

    listRoles: () => client.get('/settings/roles/'),
    getRole: (id) => client.get(`/settings/roles/${id}/`),
    createRole: (data) => client.post('/settings/roles/', data),
    updateRole: (id, data) => client.patch(`/settings/roles/${id}/`, data),

    listTaxes: () => client.get('/settings/taxes/'),
    updateTax: (id, data) => client.patch(`/settings/taxes/${id}/`, data),

    getReceiptConfig: () => client.get('/settings/receipt/'),
    updateReceiptConfig: (data) => client.patch('/settings/receipt/', data),
}
