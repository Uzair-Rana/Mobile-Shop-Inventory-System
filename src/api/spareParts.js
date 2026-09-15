import client from './client'

const BASE = '/spare-parts/parts'

export const sparePartsApi = {
    // Catalog CRUD
    list: (params) => client.get(`${BASE}/`, { params }),
    get: (id) => client.get(`${BASE}/${id}/`),
    create: (data) => client.post(`${BASE}/`, data),
    update: (id, d) => client.patch(`${BASE}/${id}/`, d),
    remove: (id) => client.delete(`${BASE}/${id}/`),

    // Ledger
    ledger: (id, params) => client.get(`${BASE}/${id}/ledger/`, { params }),
    stockIn: (id, data) => client.post(`${BASE}/${id}/stock-in/`, data),
    stockOut: (id, data) => client.post(`${BASE}/${id}/stock-out/`, data),

    // Meta
    categories: () => client.get(`${BASE}/categories/`),
    lowStock: () => client.get(`${BASE}/low-stock/`),
}
