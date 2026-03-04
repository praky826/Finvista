import api from './api';

export const taxAPI = {
    // Income
    updateIncome: (data: any) => api.put('/income', data),

    // Tax
    getTax: () => api.get('/tax'),
    updateTax: (data: any) => api.put('/tax', data),
    getTaxComparison: () => api.get('/tax/comparison'),
};
