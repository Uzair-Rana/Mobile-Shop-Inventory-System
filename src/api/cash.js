import client from './client'

export const cashApi = {
    // Sessions
    currentSession: () => client.get('/cash/sessions/current/'),
    openSession: (data) => client.post('/cash/sessions/open/', data),
    closeSession: (data) => client.post('/cash/sessions/close/', data),
    addInflow: (id, data) => client.post(`/cash/sessions/${id}/inflow/`, data),
    addOutflow: (id, data) => client.post(`/cash/sessions/${id}/outflow/`, data),

    // Expenses
    listExpenses: (params) => client.get('/cash/expenses/', { params }),
    createExpense: (data) => client.post('/cash/expenses/', data),
    updateExpense: (id, data) => client.patch(`/cash/expenses/${id}/`, data),
    deleteExpense: (id) => client.delete(`/cash/expenses/${id}/`),
}
