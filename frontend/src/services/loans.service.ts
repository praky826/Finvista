import api from './api';

export const loansAPI = {
    // Loans
    getLoans: () => api.get('/loans'),
    createLoan: (data: any) => api.post('/loans', data),
    updateLoan: (id: number, data: any) => api.put(`/loans/${id}`, data),
    deleteLoan: (id: number) => api.delete(`/loans/${id}`),

    // Credit Cards
    getCreditCards: () => api.get('/credit-cards'),
    createCreditCard: (data: any) => api.post('/credit-cards', data),
    updateCreditCard: (id: number, data: any) => api.put(`/credit-cards/${id}`, data),
    deleteCreditCard: (id: number) => api.delete(`/credit-cards/${id}`),
};
