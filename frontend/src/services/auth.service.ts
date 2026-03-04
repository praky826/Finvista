import api from './api';

export const authAPI = {
    register: (data: any) => api.post('/auth/register', data),
    login: (data: any) => api.post('/auth/login', data),
    me: () => api.get('/auth/me'),
    completeSetup: () => api.post('/auth/complete-setup'),
};
