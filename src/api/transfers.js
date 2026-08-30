/** Transfers API stubs — future real wiring */
import client from './client'

export const transfersApi = {
    list: (params) => client.get('/transfers/', { params }),
    get: (id) => client.get(`/transfers/${id}/`),
    create: (data) => client.post('/transfers/', data),
    dispatch: (id) => client.post(`/transfers/${id}/dispatch/`),
    receive: (id) => client.post(`/transfers/${id}/receive/`),
}
