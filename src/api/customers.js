import client from './client'

export const customersApi = {
    listCustomers: (params) => client.get('/customers/', { params }),
    getCustomer: (id) => client.get(`/customers/${id}/`),
    createCustomer: (data) => client.post('/customers/', data),
    updateCustomer: (id, data) => client.patch(`/customers/${id}/`, data),
    getHistory: (id) => client.get(`/customers/${id}/history/`),
    getLedger: (id) => client.get(`/customers/${id}/ledger/`),
    search: (q) => client.get('/customers/search/', { params: { q } }),
}
