import client from './client'

export const authApi = {
    login: (data) => client.post('/auth/login/', data),
    logout: () => client.post('/auth/logout/'),
    me: () => client.get('/auth/me/'),
    changePassword: (data) => client.post('/auth/change-password/', data),
    stepUp: (data) => client.post('/auth/step-up/', data),
}
