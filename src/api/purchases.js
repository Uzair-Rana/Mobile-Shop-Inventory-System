import client from './client'

export const purchasesApi = {
    // Purchase orders
    listOrders: (params) => client.get('/purchases/orders/', { params }),
    getOrder: (id) => client.get(`/purchases/orders/${id}/`),
    createOrder: (data) => client.post('/purchases/orders/', data),
    updateOrder: (id, data) => client.patch(`/purchases/orders/${id}/`, data),
    receiveOrder: (id, data) => client.post(`/purchases/orders/${id}/receive/`, data),

    // Acquisitions (used-phone intake)
    listAcquisitions: (params) => client.get('/purchases/acquisitions/', { params }),
    createAcquisition: (data) => client.post('/purchases/acquisitions/', data),
    getAcquisition: (id) => client.get(`/purchases/acquisitions/${id}/`),
    updateAcquisition: (id, data) => client.patch(`/purchases/acquisitions/${id}/`, data),
}
