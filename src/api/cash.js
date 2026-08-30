/** Cash API stubs — future real wiring */
import client from './client'

export const cashApi = {
    listSessions: (params) => client.get('/cash/sessions/', { params }),
    getSession: (id) => client.get(`/cash/sessions/${id}/`),
    openSession: (data) => client.post('/cash/sessions/', data),
    closeSession: (id, data) => client.post(`/cash/sessions/${id}/close/`, data),
    listExpenses: (params) => client.get('/cash/expenses/', { params }),
    createExpense: (data) => client.post('/cash/expenses/', data),
    updateExpense: (id, data) => client.patch(`/cash/expenses/${id}/`, data),
}
