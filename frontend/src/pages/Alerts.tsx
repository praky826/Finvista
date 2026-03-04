import { useEffect, useState } from 'react';
import { dashboardAPI } from '../services/dashboard.service';
import { Bell, AlertTriangle, Info, AlertCircle, X, CheckCircle } from 'lucide-react';

const SEVERITY_CONFIG: Record<string, { icon: any; bg: string; border: string; text: string }> = {
    critical: { icon: AlertTriangle, bg: 'bg-danger/5', border: 'border-danger/30', text: 'text-danger' },
    warning: { icon: AlertCircle, bg: 'bg-warning/5', border: 'border-warning/30', text: 'text-warning' },
    info: { icon: Info, bg: 'bg-info/5', border: 'border-info/30', text: 'text-info' },
};

export default function Alerts() {
    const [alerts, setAlerts] = useState<any[]>([]);
    const [filter, setFilter] = useState('active');
    const [stats, setStats] = useState({ total_active: 0, critical_count: 0 });
    const [loading, setLoading] = useState(true);

    const load = () => {
        dashboardAPI.getAlerts(filter === 'all' ? undefined : filter).then(res => {
            setAlerts(res.data.data.alerts);
            setStats({ total_active: res.data.data.total_active, critical_count: res.data.data.critical_count });
            setLoading(false);
        });
    };
    useEffect(load, [filter]);

    const handleDismiss = async (id: number) => {
        await dashboardAPI.dismissAlert(id);
        load();
    };

    if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" /></div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2"><Bell size={24} /> Alerts</h1>
                    <p className="text-text-secondary text-sm">{stats.total_active} active • {stats.critical_count} critical</p>
                </div>
            </div>

            {/* Filter Tabs */}
            <div className="flex gap-2">
                {['active', 'resolved', 'ignored', 'all'].map(f => (
                    <button key={f} onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize ${filter === f ? 'bg-primary text-white' : 'bg-bg-secondary text-text-secondary hover:bg-bg-hover border border-border'}`}>
                        {f}
                    </button>
                ))}
            </div>

            {/* Alert List */}
            <div className="space-y-3">
                {alerts.map(a => {
                    const config = SEVERITY_CONFIG[a.severity] || SEVERITY_CONFIG.info;
                    const Icon = config.icon;
                    return (
                        <div key={a.alert_id} className={`${config.bg} border ${config.border} rounded-xl p-5 transition-all duration-200`}>
                            <div className="flex items-start gap-3">
                                <div className={`p-2 rounded-lg ${config.text} ${config.bg}`}><Icon size={20} /></div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`text-xs font-bold uppercase ${config.text}`}>{a.severity}</span>
                                        <span className="text-xs text-text-muted">• {a.alert_type.replace(/_/g, ' ')}</span>
                                        {a.status === 'resolved' && <span className="text-xs text-success flex items-center gap-1"><CheckCircle size={12} /> Resolved</span>}
                                    </div>
                                    <p className="text-sm">{a.message}</p>
                                    {a.metric_value !== null && (
                                        <div className="flex gap-4 mt-2 text-xs text-text-muted">
                                            <span>Value: <span className="font-medium text-text-secondary">{a.metric_value}</span></span>
                                            {a.threshold !== null && <span>Threshold: <span className="font-medium text-text-secondary">{a.threshold}</span></span>}
                                        </div>
                                    )}
                                    {a.created_at && <div className="text-xs text-text-muted mt-2">{new Date(a.created_at).toLocaleString()}</div>}
                                </div>
                                {a.status === 'active' && (
                                    <button onClick={() => handleDismiss(a.alert_id)} className="text-text-muted hover:text-text-secondary transition-colors" title="Dismiss">
                                        <X size={18} />
                                    </button>
                                )}
                            </div>
                        </div>
                    );
                })}
                {alerts.length === 0 && (
                    <div className="text-center text-text-secondary py-16">
                        <Bell size={40} className="mx-auto mb-3 opacity-30" />
                        <p>No {filter} alerts</p>
                    </div>
                )}
            </div>
        </div>
    );
}
