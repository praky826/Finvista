import api from './api';

export const dashboardAPI = {
    // Backward-compatible combined dashboard
    getDashboard: () => api.get('/dashboard'),

    // Decoupled dashboards
    getPersonalDashboard: () => api.get('/dashboard/personal'),
    getBusinessDashboard: () => api.get('/dashboard/business'),

    // Alerts
    getAlerts: (status?: string) => api.get('/alerts', { params: { status } }),
    dismissAlert: (id: number) => api.patch(`/alerts/${id}/dismiss`),
};
