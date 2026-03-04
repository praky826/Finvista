import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { dashboardAPI } from '../services/dashboard.service';
import { TrendingUp, TrendingDown, Shield, Wallet, Heart, AlertTriangle, Target, ArrowUpRight, ArrowDownRight, Briefcase, User } from 'lucide-react';

interface PersonalDashboardData {
    full_name: string;
    account_type: string;
    monthly_income: number;
    monthly_expenses: number;
    total_bank_balance: number;
    summary: any;
    alerts: any[];
    goals: any[];
}

interface BusinessDashboardData {
    full_name: string;
    account_type: string;
    total_bank_balance: number;
    summary: any;
    alerts: any[];
    goals: any[];
}

function MetricCard({ title, value, meaning, icon: Icon, color, prefix = '₹' }: any) {
    const isPercentage = typeof value === 'number' && (title.includes('Ratio') || title.includes('%') || title.includes('Score') || title.includes('Rate') || title.includes('Fund') || title.includes('Margin'));
    const display = typeof value === 'number' ? (isPercentage ? `${value.toFixed(1)}${title.includes('Fund') ? ' mo' : '%'}` : `${prefix}${value.toLocaleString('en-IN')}`) : value;
    return (
        <div className="glass-card-hover p-5">
            <div className="flex items-center justify-between mb-3">
                <span className="metric-label">{title}</span>
                <div className={`p-2 rounded-lg ${color}`}>
                    <Icon size={18} />
                </div>
            </div>
            <div className="metric-value">{display}</div>
            {meaning && <p className="text-xs text-text-muted mt-1.5">{meaning}</p>}
        </div>
    );
}

function HealthGauge({ score }: { score: number }) {
    const getColor = (s: number) => s >= 80 ? '#10b981' : s >= 60 ? '#6366f1' : s >= 40 ? '#f59e0b' : '#ef4444';
    const getLabel = (s: number) => s >= 80 ? 'Excellent' : s >= 60 ? 'Good' : s >= 40 ? 'Average' : 'Poor';
    return (
        <div className="glass-card p-6 flex flex-col items-center">
            <h3 className="metric-label mb-4">Financial Health</h3>
            <div className="relative w-36 h-36">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                    <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" strokeWidth="6" className="text-border" />
                    <circle cx="50" cy="50" r="42" fill="none" stroke={getColor(score)} strokeWidth="6" strokeDasharray={`${score * 2.64} 264`} strokeLinecap="round" className="transition-all duration-1000" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-bold" style={{ color: getColor(score) }}>{score.toFixed(0)}</span>
                    <span className="text-xs text-text-muted">{getLabel(score)}</span>
                </div>
            </div>
        </div>
    );
}

function ViewToggle({ activeView, onToggle, accountType }: { activeView: 'personal' | 'business'; onToggle: (v: 'personal' | 'business') => void; accountType: string }) {
    if (accountType !== 'both') return null;
    return (
        <div className="flex gap-1 p-1 rounded-xl bg-bg-hover border border-border">
            <button
                onClick={() => onToggle('personal')}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeView === 'personal' ? 'bg-primary text-white shadow-sm' : 'text-text-secondary hover:text-text-primary'}`}
            >
                <User size={14} /> Personal
            </button>
            <button
                onClick={() => onToggle('business')}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeView === 'business' ? 'bg-primary text-white shadow-sm' : 'text-text-secondary hover:text-text-primary'}`}
            >
                <Briefcase size={14} /> Business
            </button>
        </div>
    );
}

function PersonalView({ data }: { data: PersonalDashboardData }) {
    const s = data.summary;
    const alertColors: Record<string, string> = { critical: 'border-danger bg-danger/5', warning: 'border-warning bg-warning/5', info: 'border-info bg-info/5' };

    return (
        <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard title="Net Worth" value={s.net_worth || 0} icon={Wallet} color="bg-primary/10 text-primary" meaning="Assets minus liabilities" />
                <MetricCard title="Monthly Income" value={data.monthly_income} icon={TrendingUp} color="bg-success/10 text-success" meaning="Your monthly earnings" />
                <MetricCard title="Monthly Expenses" value={data.monthly_expenses} icon={TrendingDown} color="bg-danger/10 text-danger" meaning="Your monthly spending" />
                <MetricCard title="Bank Balance" value={data.total_bank_balance} icon={Shield} color="bg-secondary/10 text-secondary" meaning="Total across all accounts" />
            </div>

            {/* Health Score + Financial Ratios */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <HealthGauge score={s.health_score || 0} />
                <div className="lg:col-span-2 grid grid-cols-2 gap-4">
                    <MetricCard title="DTI Ratio" value={s.dti || 0} icon={s.dti > 40 ? AlertTriangle : Shield} color={s.dti > 40 ? 'bg-danger/10 text-danger' : 'bg-success/10 text-success'} meaning={s.dti > 40 ? '⚠ High debt load' : '✓ Healthy debt level'} prefix="" />
                    <MetricCard title="Emergency Fund" value={s.emergency_fund || 0} icon={Heart} color={s.emergency_fund < 3 ? 'bg-danger/10 text-danger' : 'bg-success/10 text-success'} meaning={s.emergency_fund < 3 ? '⚠ Build reserves' : '✓ Well protected'} prefix="" />
                    <MetricCard title="Credit Utilization" value={s.credit_utilization || 0} icon={s.credit_utilization > 30 ? AlertTriangle : Shield} color={s.credit_utilization > 30 ? 'bg-warning/10 text-warning' : 'bg-success/10 text-success'} meaning={s.credit_utilization > 30 ? '⚠ Keep below 30%' : '✓ Good utilization'} prefix="" />
                    <MetricCard title="Savings Ratio" value={s.savings_ratio || 0} icon={TrendingUp} color={s.savings_ratio > 20 ? 'bg-success/10 text-success' : 'bg-warning/10 text-warning'} meaning={s.savings_ratio > 20 ? '✓ Saving well' : '⚠ Aim for 20%+'} prefix="" />
                </div>
            </div>

            {/* Tax + Cash Flow */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <MetricCard title="Tax Estimate" value={s.tax_estimate || 0} icon={ArrowDownRight} color="bg-warning/10 text-warning" meaning={`${(s.effective_tax_rate || 0).toFixed(1)}% effective rate`} />
                <MetricCard title="Cash Flow" value={s.cash_flow_monthly || 0} icon={s.cash_flow_monthly >= 0 ? TrendingUp : TrendingDown} color={s.cash_flow_monthly >= 0 ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'} meaning={s.cash_flow_monthly >= 0 ? 'Monthly surplus' : 'Monthly deficit'} />
                <MetricCard title="Credit Score" value={`${s.credit_score_simulation || 0}`} icon={Shield} color="bg-primary/10 text-primary" meaning="Simulated score (600-900)" prefix="" />
            </div>

            {/* Personal Alerts */}
            {data.alerts?.length > 0 && (
                <div>
                    <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <AlertTriangle size={18} className="text-warning" /> Personal Alerts ({data.alerts.length})
                    </h2>
                    <div className="space-y-2">
                        {data.alerts.slice(0, 5).map(a => (
                            <div key={a.alert_id} className={`p-4 rounded-xl border-l-4 ${alertColors[a.severity] || alertColors.info}`}>
                                <div className="flex items-center gap-2 mb-1">
                                    <span className={`text-xs font-bold uppercase ${a.severity === 'critical' ? 'text-danger' : a.severity === 'warning' ? 'text-warning' : 'text-info'}`}>{a.severity}</span>
                                    <span className="text-xs text-text-muted">• {a.alert_type.replace(/_/g, ' ')}</span>
                                </div>
                                <p className="text-sm">{a.message}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Personal Goals */}
            {data.goals?.length > 0 && (
                <div>
                    <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <Target size={18} className="text-primary" /> Goals ({data.goals.length})
                    </h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {data.goals.map((g: any) => (
                            <div key={g.goal_id} className="glass-card p-5">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-medium text-sm">{g.goal_name}</span>
                                    <span className="text-xs text-text-muted">{g.months_remaining} mo left</span>
                                </div>
                                <div className="w-full bg-bg-hover rounded-full h-2.5 mb-2">
                                    <div className="h-2.5 rounded-full bg-gradient-to-r from-primary to-secondary transition-all duration-500" style={{ width: `${Math.min(g.progress_percent, 100)}%` }} />
                                </div>
                                <div className="flex justify-between text-xs text-text-secondary">
                                    <span>₹{g.current_savings.toLocaleString('en-IN')}</span>
                                    <span>₹{g.target.toLocaleString('en-IN')}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

function BusinessView({ data }: { data: BusinessDashboardData }) {
    const s = data.summary;
    const alertColors: Record<string, string> = { critical: 'border-danger bg-danger/5', warning: 'border-warning bg-warning/5', info: 'border-info bg-info/5' };

    return (
        <div className="space-y-6">
            {/* Business Key Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard title="Business Net Worth" value={s.business_net_worth || 0} icon={Wallet} color="bg-primary/10 text-primary" meaning="Business assets minus liabilities" />
                <MetricCard title="Net Profit" value={s.net_profit || 0} icon={TrendingUp} color="bg-success/10 text-success" meaning="Revenue minus all costs" />
                <MetricCard title="Working Capital" value={s.working_capital || 0} icon={Shield} color="bg-secondary/10 text-secondary" meaning="Current assets minus liabilities" />
                <MetricCard title="Business Cash Flow" value={s.cash_flow || 0} icon={s.cash_flow >= 0 ? TrendingUp : TrendingDown} color={s.cash_flow >= 0 ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'} meaning={s.cash_flow >= 0 ? 'Positive flow' : 'Negative flow'} />
            </div>

            {/* Business Health Ratios */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard title="Gross Margin" value={s.gross_profit_margin || 0} icon={ArrowUpRight} color="bg-primary/10 text-primary" prefix="" />
                <MetricCard title="Net Margin" value={s.net_profit_margin || 0} icon={ArrowUpRight} color="bg-secondary/10 text-secondary" prefix="" />
                <MetricCard title="Debt Ratio" value={s.debt_ratio || 0} icon={s.debt_ratio > 60 ? AlertTriangle : Shield} color={s.debt_ratio > 60 ? 'bg-danger/10 text-danger' : 'bg-success/10 text-success'} meaning={s.debt_ratio > 60 ? '⚠ Over-leveraged' : '✓ Healthy leverage'} prefix="" />
                <MetricCard title="Liquidity Ratio" value={s.liquidity_ratio || 0} icon={Shield} color={s.liquidity_ratio < 1 ? 'bg-danger/10 text-danger' : 'bg-success/10 text-success'} meaning={s.liquidity_ratio < 1 ? '⚠ Low liquidity' : '✓ Good liquidity'} prefix="" />
            </div>

            {/* Inventory, Receivables, Payables */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <MetricCard title="Inventory Value" value={s.total_inventory_value || 0} icon={Briefcase} color="bg-primary/10 text-primary" meaning="Total stock value" />
                <MetricCard title="Receivables" value={s.total_receivables || 0} icon={ArrowUpRight} color="bg-success/10 text-success" meaning="Pending from customers" />
                <MetricCard title="Payables" value={s.total_payables || 0} icon={ArrowDownRight} color="bg-warning/10 text-warning" meaning="Owed to vendors" />
            </div>

            {/* Business Alerts */}
            {data.alerts?.length > 0 && (
                <div>
                    <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <AlertTriangle size={18} className="text-warning" /> Business Alerts ({data.alerts.length})
                    </h2>
                    <div className="space-y-2">
                        {data.alerts.slice(0, 5).map(a => (
                            <div key={a.alert_id} className={`p-4 rounded-xl border-l-4 ${alertColors[a.severity] || alertColors.info}`}>
                                <div className="flex items-center gap-2 mb-1">
                                    <span className={`text-xs font-bold uppercase ${a.severity === 'critical' ? 'text-danger' : a.severity === 'warning' ? 'text-warning' : 'text-info'}`}>{a.severity}</span>
                                    <span className="text-xs text-text-muted">• {a.alert_type.replace(/_/g, ' ')}</span>
                                </div>
                                <p className="text-sm">{a.message}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Business Goals */}
            {data.goals?.length > 0 && (
                <div>
                    <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <Target size={18} className="text-primary" /> Business Goals ({data.goals.length})
                    </h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {data.goals.map((g: any) => (
                            <div key={g.goal_id} className="glass-card p-5">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-medium text-sm">{g.goal_name}</span>
                                    <span className="text-xs text-text-muted">{g.months_remaining} mo left</span>
                                </div>
                                <div className="w-full bg-bg-hover rounded-full h-2.5 mb-2">
                                    <div className="h-2.5 rounded-full bg-gradient-to-r from-primary to-secondary transition-all duration-500" style={{ width: `${Math.min(g.progress_percent, 100)}%` }} />
                                </div>
                                <div className="flex justify-between text-xs text-text-secondary">
                                    <span>₹{g.current_savings.toLocaleString('en-IN')}</span>
                                    <span>₹{g.target.toLocaleString('en-IN')}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default function Dashboard() {
    const { user } = useAuth();
    const [personalData, setPersonalData] = useState<PersonalDashboardData | null>(null);
    const [businessData, setBusinessData] = useState<BusinessDashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeView, setActiveView] = useState<'personal' | 'business'>(
        user?.account_type === 'business' ? 'business' : 'personal'
    );

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                const accountType = user?.account_type || 'personal';

                // Fetch personal data if applicable
                if (accountType === 'personal' || accountType === 'both') {
                    const res = await dashboardAPI.getPersonalDashboard();
                    setPersonalData(res.data.data);
                }

                // Fetch business data if applicable
                if (accountType === 'business' || accountType === 'both') {
                    const res = await dashboardAPI.getBusinessDashboard();
                    setBusinessData(res.data.data);
                }
            } catch (err) {
                console.error('Dashboard fetch error:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchDashboard();
    }, [user?.account_type]);

    if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" /></div>;

    const currentData = activeView === 'personal' ? personalData : businessData;
    if (!currentData) return <div className="text-center text-text-secondary py-20">Unable to load dashboard.</div>;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-2xl font-bold">Welcome, {(personalData || businessData)?.full_name?.split(' ')[0]}!</h1>
                    <p className="text-text-secondary text-sm mt-1">
                        {activeView === 'personal' ? "Here's your personal financial overview" : "Here's your business performance overview"}
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <ViewToggle activeView={activeView} onToggle={setActiveView} accountType={user?.account_type || 'personal'} />
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20 capitalize">{user?.account_type}</span>
                </div>
            </div>

            {/* Render the active view */}
            {activeView === 'personal' && personalData && <PersonalView data={personalData} />}
            {activeView === 'business' && businessData && <BusinessView data={businessData} />}
        </div>
    );
}
