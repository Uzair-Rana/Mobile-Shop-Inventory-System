import client from './client'

export const reportsApi = {
    salesSummary: (params) => client.get('/reports/sales-summary/', { params }),
    profitLoss: (params) => client.get('/reports/profit-loss/', { params }),
    inventoryValuation: (params) => client.get('/reports/inventory-valuation/', { params }),
    imeiHistory: (params) => client.get('/reports/imei-history/', { params }),
    repairs: (params) => client.get('/reports/repairs/', { params }),
    installments: (params) => client.get('/reports/installments/', { params }),
    customerLedger: (params) => client.get('/reports/customer-ledger/', { params }),
    staffPerformance: (params) => client.get('/reports/staff-performance/', { params }),
    deadStock: (params) => client.get('/reports/dead-stock/', { params }),
    cash: (params) => client.get('/reports/cash/', { params }),
    exportCsv: (slug, params) => client.get(`/reports/${slug}/export/`, {
        params,
        responseType: 'blob',
    }),
}
