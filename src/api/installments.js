import client from './client'

export const installmentsApi = {
    listPlans: (params) => client.get('/installments/plans/', { params }),
    getPlan: (id) => client.get(`/installments/plans/${id}/`),
    createPlan: (data) => client.post('/installments/plans/', data),
    collectPayment: (id, data) => client.post(`/installments/plans/${id}/collect/`, data),
    markDefaulted: (id, data) => client.post(`/installments/plans/${id}/default/`, data),
    cancelPlan: (id, data) => client.post(`/installments/plans/${id}/cancel/`, data),
    listOverdue: (params) => client.get('/installments/overdue/', { params }),
    getSchedule: (id) => client.get(`/installments/plans/${id}/schedule/`),
}
