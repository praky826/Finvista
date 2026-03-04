import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff, LogIn } from 'lucide-react';

export default function Login() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPwd, setShowPwd] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(username, password);
            navigate('/dashboard');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-bg-primary flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-primary-light to-secondary bg-clip-text text-transparent mb-2">FINVISTA</h1>
                    <p className="text-text-secondary">Financial Analytics Platform</p>
                </div>
                <div className="glass-card p-8">
                    <h2 className="text-xl font-semibold mb-6">Log In</h2>
                    {error && <div className="mb-4 p-3 rounded-lg bg-danger/10 border border-danger/20 text-danger text-sm">{error}</div>}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm text-text-secondary mb-1.5">Username</label>
                            <input type="text" value={username} onChange={e => setUsername(e.target.value)} required autoComplete="username"
                                className="w-full px-4 py-3 rounded-xl bg-bg-input border border-border text-text-primary placeholder-text-muted focus:border-primary focus:ring-1 focus:ring-primary/30 outline-none transition-all" placeholder="Enter username" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1.5">Password</label>
                            <div className="relative">
                                <input type={showPwd ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} required autoComplete="current-password"
                                    className="w-full px-4 py-3 rounded-xl bg-bg-input border border-border text-text-primary placeholder-text-muted focus:border-primary focus:ring-1 focus:ring-primary/30 outline-none transition-all pr-12" placeholder="Enter password" />
                                <button type="button" onClick={() => setShowPwd(!showPwd)} className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary">
                                    {showPwd ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </div>
                        <button type="submit" disabled={loading}
                            className="w-full py-3 rounded-xl bg-primary hover:bg-primary-hover text-white font-medium transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50">
                            {loading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" /> : <><LogIn size={18} /> Log In</>}
                        </button>
                    </form>
                    <p className="text-center text-sm text-text-secondary mt-6">
                        Don't have an account? <Link to="/register" className="text-primary hover:text-primary-light transition-colors">Create one</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
