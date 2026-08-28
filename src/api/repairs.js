import client from './client'

export const repairsApi = {
    listJobs: (params) => client.get('/repairs/jobs/', { params }),
    getJob: (id) => client.get(`/repairs/jobs/${id}/`),
    createJob: (data) => client.post('/repairs/jobs/', data),
    updateJob: (id, data) => client.patch(`/repairs/jobs/${id}/`, data),
    updateStatus: (id, data) => client.post(`/repairs/jobs/${id}/update_status/`, data),
    addPart: (id, data) => client.post(`/repairs/jobs/${id}/parts/`, data),
    removePart: (jobId, partId) => client.delete(`/repairs/jobs/${jobId}/parts/${partId}/`),
    collectPayment: (id, data) => client.post(`/repairs/jobs/${id}/collect_payment/`, data),
    deliver: (id, data) => client.post(`/repairs/jobs/${id}/deliver/`, data),
    printJobCard: (id) => client.get(`/repairs/jobs/${id}/jobcard/`, { responseType: 'blob' }),

    // Technicians
    listTechnicians: (params) => client.get('/repairs/technicians/', { params }),
}
