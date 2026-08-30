/** Admin API stubs — future real wiring */
import client from './client'

export const adminApi = {
    listAuditLogs: (params) => client.get('/admin/audit/', { params }),
    getAuditLog: (id) => client.get(`/admin/audit/${id}/`),
}
