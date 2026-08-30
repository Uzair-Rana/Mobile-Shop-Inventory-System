/** Branches API stubs — future real wiring */
import client from './client'

export const branchesApi = {
    list: () => client.get('/branches/'),
    get: (id) => client.get(`/branches/${id}/`),
    create: (data) => client.post('/branches/', data),
    update: (id, data) => client.patch(`/branches/${id}/`, data),
}
