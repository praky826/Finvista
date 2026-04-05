import api from './api';

export const assetsAPI = {
    getAssets: () => api.get('/assets/'),
    createAsset: (data: { name: string; asset_type: string; value: number }) => api.post('/assets/', data),
    deleteAsset: (id: number) => api.delete(`/assets/${id}`),
};
