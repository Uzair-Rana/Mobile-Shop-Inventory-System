import client from './client'

export const reportsApi = {
    salesSummary: (params) => client.get('/reports/sales-summary/', { params }),
    profitLoss: (params) => client.get('/reports/profit-loss/', { params }),
    inventoryValuation: (params) => client.get('/reports/inventory-valuation/', { params }),
    stockMovement: (params) => client.get('/reports/stock-movement/', { params }),
    repairsSummary: (params) => client.get('/reports/repairs/', { params }),
    installmentHealth: (params) => client.get('/reports/installments/', { params }),
    customerStatement: (id, params) => client.get(`/reports/customer-statement/${id}/`, { params }),
    supplierStatement: (id, params) => client.get(`/reports/supplier-statement/${id}/`, { params }),
    exportCsv: (report, params) => client.get(`/reports/${report}/export/`, { params, responseType: 'blob' }),
}
