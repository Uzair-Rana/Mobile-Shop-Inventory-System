import client from './client'

export const suppliersApi = {
    listSuppliers: (params) => client.get('/suppliers/', { params }),
    getSupplier: (id) => client.get(`/suppliers/${id}/`),
    createSupplier: (data) => client.post('/suppliers/', data),
    updateSupplier: (id, data) => client.patch(`/suppliers/${id}/`, data),
    getLedger: (id) => client.get(`/suppliers/${id}/ledger/`),
}
