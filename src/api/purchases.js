import client from './client'

export const purchasesApi = {
    listOrders: (params) => client.get('/purchases/orders/', { params }),
    getOrder: (id) => client.get(`/purchases/orders/${id}/`),
    createOrder: (data) => client.post('/purchases/orders/', data),
    updateOrder: (id, data) => client.patch(`/purchases/orders/${id}/`, data),
    receiveOrder: (id, data) => client.post(`/purchases/orders/${id}/receive/`, data),
    cancelOrder: (id, data) => client.post(`/purchases/orders/${id}/cancel/`, data),

    // Purchase payments to supplier
    addPayment: (id, data) => client.post(`/purchases/orders/${id}/payments/`, data),
}
