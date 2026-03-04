import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../services/auth.service';

interface User {
    user_id: number;
    full_name: string;
    email: string;
    username: string;
    account_type: string;
    monthly_income: number;
    monthly_expenses: number;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (username: string, password: string) => Promise<any>;
    registerAndLogin: (data: any) => Promise<any>;
    logout: () => void;
    isAuthenticated: boolean;
    loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem('finvista_token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadUser = async () => {
            if (token) {
                try {
                    const res = await authAPI.me();
                    setUser(res.data.data);
                } catch {
                    localStorage.removeItem('finvista_token');
                    setToken(null);
                }
            }
            setLoading(false);
        };
        loadUser();
    }, [token]);

    const setSession = (data: any, username: string) => {
        localStorage.setItem('finvista_token', data.token);
        localStorage.setItem('finvista_user', JSON.stringify(data));
        setToken(data.token);
        setUser({
            user_id: data.user_id,
            full_name: data.full_name || '',
            email: data.email || '',
            username: username,
            account_type: data.account_type || 'personal',
            monthly_income: 0,
            monthly_expenses: 0,
        });
    };

    const login = async (username: string, password: string) => {
        const res = await authAPI.login({ username, password });
        const data = res.data.data;
        setSession(data, username);
        return data;
    };

    const registerAndLogin = async (regData: any) => {
        const res = await authAPI.register(regData);
        const data = res.data.data;
        // Register now returns a token — auto-login
        setSession(data, regData.username);
        return data;
    };

    const logout = () => {
        localStorage.removeItem('finvista_token');
        localStorage.removeItem('finvista_user');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, registerAndLogin, logout, isAuthenticated: !!token, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
}
