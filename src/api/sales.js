import client from './client'

export const salesApi = {
    // Invoices
    listInvoices: (params) => client.get('/sales/invoices/', { params }),
    getInvoice: (id) => client.get(`/sales/invoices/${id}/`),
    createInvoice: (data) => client.post('/sales/invoices/', data),
    updateInvoice: (id, data) => client.patch(`/sales/invoices/${id}/`, data),
    finalizeInvoice: (id) => client.post(`/sales/invoices/${id}/finalize/`),
    voidInvoice: (id, data) => client.post(`/sales/invoices/${id}/void/`, data),
    returnInvoice: (id, data) => client.post(`/sales/invoices/${id}/return/`, data),
    printInvoice: (id) => client.get(`/sales/invoices/${id}/print/`, { responseType: 'blob' }),

    // Payments
    listPayments: (params) => client.get('/sales/payments/', { params }),
    addPayment: (invoiceId, data) => client.post(`/sales/invoices/${invoiceId}/payments/`, data),

    // Daily summary
    getDailySummary: (date) => client.get('/sales/daily-summary/', { params: { date } }),
}
