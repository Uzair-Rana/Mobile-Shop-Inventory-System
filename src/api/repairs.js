import client from './client'

export const repairsApi = {
    listJobs: (params) => client.get('/repairs/jobs/', { params }),
    getJob: (id) => client.get(`/repairs/jobs/${id}/`),
    createJob: (data) => client.post('/repairs/jobs/', data),
    updateJob: (id, data) => client.patch(`/repairs/jobs/${id}/`, data),
    updateStatus: (id, data) => client.post(`/repairs/jobs/${id}/update_status/`, data),
    deliver: (id, data) => client.post(`/repairs/jobs/${id}/deliver/`, data),
    getBoard: () => client.get('/repairs/jobs/board/'),
}
