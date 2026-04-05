import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Wallet, CreditCard, TrendingUp, Calculator, Target, Bell, LogOut, Menu, X, Archive } from 'lucide-react';
import { useState } from 'react';

const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/accounts', label: 'Accounts', icon: Wallet },
    { path: '/loans', label: 'Loans & Credit', icon: CreditCard },
    { path: '/investments', label: 'Investments', icon: TrendingUp },
    { path: '/tax', label: 'Tax', icon: Calculator },
    { path: '/goals', label: 'Goals', icon: Target },
    { path: '/alerts', label: 'Alerts', icon: Bell },
    { path: '/assets', label: 'Assets', icon: Archive },
];

export default function Layout() {
    const { user, logout } = useAuth();
    const location = useLocation();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="flex h-screen bg-bg-primary overflow-hidden">
            {/* ── Desktop Sidebar ── */}
            <aside className={`hidden lg:flex flex-col w-64 bg-bg-secondary border-r border-border`}>
                <div className="p-6 border-b border-border">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">FINVISTA</h1>
                    <p className="text-xs text-text-muted mt-1">Financial Analytics</p>
                </div>
                <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
                    {navItems.map(({ path, label, icon: Icon }) => (
                        <NavLink key={path} to={path}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${isActive ? 'bg-primary/15 text-primary border border-primary/20' : 'text-text-secondary hover:bg-bg-hover hover:text-text-primary'
                                }`
                            }>
                            <Icon size={18} />
                            {label}
                        </NavLink>
                    ))}
                </nav>
                <div className="p-4 border-t border-border">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm">
                            {user?.full_name?.charAt(0) || 'U'}
                        </div>
                        <div className="min-w-0">
                            <div className="text-sm font-medium truncate">{user?.full_name || 'User'}</div>
                            <div className="text-xs text-text-muted truncate">{user?.account_type || 'personal'}</div>
                        </div>
                    </div>
                    <button onClick={logout} className="flex items-center gap-2 w-full px-4 py-2 rounded-lg text-sm text-text-secondary hover:bg-danger/10 hover:text-danger transition-colors">
                        <LogOut size={16} /> Logout
                    </button>
                </div>
            </aside>

            {/* ── Mobile Sidebar Overlay ── */}
            {sidebarOpen && (
                <div className="lg:hidden fixed inset-0 z-50">
                    <div className="absolute inset-0 bg-black/60" onClick={() => setSidebarOpen(false)} />
                    <aside className="absolute left-0 top-0 bottom-0 w-72 bg-bg-secondary border-r border-border flex flex-col">
                        <div className="p-5 flex items-center justify-between border-b border-border">
                            <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">FINVISTA</h1>
                            <button onClick={() => setSidebarOpen(false)} className="text-text-secondary"><X size={20} /></button>
                        </div>
                        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
                            {navItems.map(({ path, label, icon: Icon }) => (
                                <NavLink key={path} to={path} onClick={() => setSidebarOpen(false)}
                                    className={({ isActive }) =>
                                        `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${isActive ? 'bg-primary/15 text-primary' : 'text-text-secondary hover:bg-bg-hover'
                                        }`
                                    }>
                                    <Icon size={18} />
                                    {label}
                                </NavLink>
                            ))}
                        </nav>
                        <div className="p-4 border-t border-border">
                            <button onClick={logout} className="flex items-center gap-2 w-full px-4 py-2 rounded-lg text-sm text-text-secondary hover:bg-danger/10 hover:text-danger">
                                <LogOut size={16} /> Logout
                            </button>
                        </div>
                    </aside>
                </div>
            )}

            {/* ── Main Content ── */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Top Bar */}
                <header className="h-16 bg-bg-secondary/80 backdrop-blur-lg border-b border-border flex items-center px-4 lg:px-6 shrink-0">
                    <button className="lg:hidden mr-3 text-text-secondary" onClick={() => setSidebarOpen(true)}>
                        <Menu size={22} />
                    </button>
                    <div className="flex-1">
                        <h2 className="text-lg font-semibold capitalize">{location.pathname.split('/').pop() || 'Dashboard'}</h2>
                    </div>
                    <div className="lg:hidden flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-xs">
                            {user?.full_name?.charAt(0) || 'U'}
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <main className="flex-1 overflow-y-auto p-4 lg:p-6 pb-20 lg:pb-6">
                    <div className="page-enter">
                        <Outlet />
                    </div>
                </main>

                {/* ── Mobile Bottom Nav ── */}
                <nav className="bottom-nav lg:hidden flex items-center justify-around py-2 z-40">
                    {navItems.slice(0, 5).map(({ path, label, icon: Icon }) => (
                        <NavLink key={path} to={path}
                            className={({ isActive }) =>
                                `flex flex-col items-center gap-0.5 py-1 px-2 text-xs transition-colors ${isActive ? 'text-primary' : 'text-text-muted'
                                }`
                            }>
                            <Icon size={20} />
                            <span className="truncate">{label.split(' ')[0]}</span>
                        </NavLink>
                    ))}
                </nav>
            </div>
        </div>
    );
}
