import client from './client'

export const installmentsApi = {
    listPlans: (params) => client.get('/installments/plans/', { params }),
    getPlan: (id) => client.get(`/installments/plans/${id}/`),
    createPlan: (data) => client.post('/installments/plans/', data),
    getSchedule: (id) => client.get(`/installments/plans/${id}/schedule/`),
    collectPayment: (id, data) => client.post(`/installments/plans/${id}/collect/`, data),
    listOverdue: (params) => client.get('/installments/overdue/', { params }),
    getAging: () => client.get('/installments/aging/'),
}
