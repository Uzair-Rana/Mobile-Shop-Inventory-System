import client from './client'

export const inventoryApi = {
    // Products / Model catalog
    listProducts: (params) => client.get('/inventory/products/', { params }),
    getProduct: (id) => client.get(`/inventory/products/${id}/`),
    createProduct: (data) => client.post('/inventory/products/', data),
    updateProduct: (id, data) => client.patch(`/inventory/products/${id}/`, data),
    deleteProduct: (id) => client.delete(`/inventory/products/${id}/`),

    // IMEI / Serial stock items (individual units)
    listUnits: (params) => client.get('/inventory/units/', { params }),
    getUnit: (id) => client.get(`/inventory/units/${id}/`),
    getUnitByIMEI: (imei) => client.get('/inventory/units/by_imei/', { params: { imei } }),
    createUnit: (data) => client.post('/inventory/units/', data),
    updateUnit: (id, data) => client.patch(`/inventory/units/${id}/`, data),

    // Accessories / non-serialised stock
    listAccessories: (params) => client.get('/inventory/accessories/', { params }),
    getAccessory: (id) => client.get(`/inventory/accessories/${id}/`),
    createAccessory: (data) => client.post('/inventory/accessories/', data),
    updateAccessory: (id, data) => client.patch(`/inventory/accessories/${id}/`, data),
    adjustStock: (id, data) => client.post(`/inventory/accessories/${id}/adjust_stock/`, data),

    // Categories & Brands
    listCategories: (params) => client.get('/inventory/categories/', { params }),
    listBrands: (params) => client.get('/inventory/brands/', { params }),

    // Barcode/IMEI search (unified scanner endpoint)
    scanLookup: (query) => client.get('/inventory/scan/', { params: { q: query } }),

    // Stock alerts
    listLowStock: (params) => client.get('/inventory/low-stock/', { params }),
}
