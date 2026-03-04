/**
 * Axios API instance with JWT interceptor.
 * All API calls go through this instance.
 */
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE,
    headers: { 'Content-Type': 'application/json' },
});

// Request interceptor: attach JWT token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('finvista_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor: handle 401 (token expired)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Don't redirect if we're on the register page (wizard is saving data)
            const isRegisterPage = window.location.pathname.includes('/register');
            if (!isRegisterPage) {
                localStorage.removeItem('finvista_token');
                localStorage.removeItem('finvista_user');
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default api;
