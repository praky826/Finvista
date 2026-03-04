import api from './api';

export const businessAPI = {
    // Inventory
    getInventory: () => api.get('/business/inventory'),
    createInventory: (data: any) => api.post('/business/inventory', data),

    // Receivables
    getReceivables: () => api.get('/business/receivables'),
    createReceivable: (data: any) => api.post('/business/receivables', data),

    // Payables
    getPayables: () => api.get('/business/payables'),
    createPayable: (data: any) => api.post('/business/payables', data),
};
