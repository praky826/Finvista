import api from './api';

export const investmentsAPI = {
    // Investments
    getInvestments: () => api.get('/investments'),
    createInvestment: (data: any) => api.post('/investments', data),
    updateInvestment: (id: number, data: any) => api.put(`/investments/${id}`, data),
    deleteInvestment: (id: number) => api.delete(`/investments/${id}`),

    // Goals
    getGoals: () => api.get('/goals'),
    createGoal: (data: any) => api.post('/goals', data),
    updateGoal: (id: number, data: any) => api.put(`/goals/${id}`, data),
    deleteGoal: (id: number) => api.delete(`/goals/${id}`),
};
