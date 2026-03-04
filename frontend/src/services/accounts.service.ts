import api from './api';

export const accountsAPI = {
    // Accounts
    getAccounts: () => api.get('/accounts'),
    createAccount: (data: any) => api.post('/accounts', data),
    updateAccount: (id: number, data: any) => api.put(`/accounts/${id}`, data),
    deleteAccount: (id: number) => api.delete(`/accounts/${id}`),

    // Cash
    getCash: () => api.get('/cash'),
    upsertCash: (data: any) => api.post('/cash', data),
};
