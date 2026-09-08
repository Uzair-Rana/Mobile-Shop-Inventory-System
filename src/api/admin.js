import client from './client'

export const adminApi = {
    // Users
    listUsers: (params) => client.get('/admin/users/', { params }),
    getUser: (id) => client.get(`/admin/users/${id}/`),
    createUser: (data) => client.post('/admin/users/', data),
    updateUser: (id, data) => client.patch(`/admin/users/${id}/`, data),
    deactivateUser: (id) => client.post(`/admin/users/${id}/deactivate/`),

    // Roles
    listRoles: (params) => client.get('/admin/roles/', { params }),
    getRole: (id) => client.get(`/admin/roles/${id}/`),
    createRole: (data) => client.post('/admin/roles/', data),
    updateRole: (id, data) => client.patch(`/admin/roles/${id}/`, data),

    // Audit log
    listAuditLogs: (params) => client.get('/admin/audit-log/', { params }),
}
