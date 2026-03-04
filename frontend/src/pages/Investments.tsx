import { useEffect, useState } from 'react';
import { investmentsAPI } from '../services/investments.service';
import { Plus, Trash2, X, Save, TrendingUp, PieChart } from 'lucide-react';
import { PieChart as RPieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = ['#6366f1', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
const TYPE_LABELS: Record<string, string> = { fd: 'Fixed Deposit', stock: 'Stocks', mf: 'Mutual Funds', gold: 'Gold', property: 'Property' };

export default function Investments() {
    const [investments, setInvestments] = useState<any[]>([]);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ type: 'fd', value: '', interest_rate: '' });
    const [loading, setLoading] = useState(true);

    const load = () => { investmentsAPI.getInvestments().then(res => { setInvestments(res.data.data); setLoading(false); }); };
    useEffect(load, []);

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        await investmentsAPI.createInvestment({ type: form.type, value: parseFloat(form.value), interest_rate: form.interest_rate ? parseFloat(form.interest_rate) : undefined });
        setShowForm(false);
        setForm({ type: 'fd', value: '', interest_rate: '' });
        load();
    };

    if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" /></div>;

    const total = investments.reduce((s, i) => s + i.value, 0);
    const byType: Record<string, number> = {};
    investments.forEach(i => { byType[i.type] = (byType[i.type] || 0) + i.value; });
    const pieData = Object.entries(byType).map(([name, value]) => ({ name: TYPE_LABELS[name] || name, value }));

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Investments</h1>
                    <p className="text-text-secondary text-sm">Total Portfolio: <span className="text-primary font-semibold">₹{total.toLocaleString('en-IN')}</span></p>
                </div>
                <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-medium">
                    {showForm ? <X size={16} /> : <Plus size={16} />} {showForm ? 'Cancel' : 'Add Investment'}
                </button>
            </div>

            {showForm && (
                <form onSubmit={handleAdd} className="glass-card p-5 space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <select value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))} className="px-3 py-2 rounded-lg bg-bg-input border border-border text-sm text-text-primary outline-none">
                            {Object.entries(TYPE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                        </select>
                        <input type="number" placeholder="Value (₹)" value={form.value} onChange={e => setForm(f => ({ ...f, value: e.target.value }))} required className="px-3 py-2 rounded-lg bg-bg-input border border-border text-sm text-text-primary outline-none" />
                        <input type="number" step="0.01" placeholder="Interest Rate %" value={form.interest_rate} onChange={e => setForm(f => ({ ...f, interest_rate: e.target.value }))} className="px-3 py-2 rounded-lg bg-bg-input border border-border text-sm text-text-primary outline-none" />
                    </div>
                    <button type="submit" className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-success text-white text-sm"><Save size={14} /> Save</button>
                </form>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Pie Chart */}
                {pieData.length > 0 && (
                    <div className="glass-card p-6">
                        <h3 className="text-sm font-medium text-text-secondary mb-4 flex items-center gap-2"><PieChart size={16} /> Asset Allocation</h3>
                        <ResponsiveContainer width="100%" height={200}>
                            <RPieChart>
                                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={3} dataKey="value">
                                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                </Pie>
                                <Tooltip formatter={(v: number) => `₹${v.toLocaleString('en-IN')}`} contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f1f5f9' }} />
                            </RPieChart>
                        </ResponsiveContainer>
                        <div className="flex flex-wrap gap-2 mt-3">
                            {pieData.map((d, i) => (
                                <span key={d.name} className="flex items-center gap-1.5 text-xs text-text-secondary">
                                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                                    {d.name} ({(d.value / total * 100).toFixed(0)}%)
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Investment List */}
                <div className={`${pieData.length > 0 ? 'lg:col-span-2' : 'lg:col-span-3'} space-y-3`}>
                    {investments.map(i => (
                        <div key={i.investment_id} className="glass-card-hover p-4 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-success/10 text-success"><TrendingUp size={16} /></div>
                                <div>
                                    <div className="font-medium text-sm">{TYPE_LABELS[i.type] || i.type}</div>
                                    {i.interest_rate && <div className="text-xs text-text-muted">{i.interest_rate}% p.a.</div>}
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className="font-bold">₹{i.value.toLocaleString('en-IN')}</span>
                                <button onClick={async () => { await investmentsAPI.deleteInvestment(i.investment_id); load(); }} className="text-text-muted hover:text-danger"><Trash2 size={15} /></button>
                            </div>
                        </div>
                    ))}
                    {investments.length === 0 && <div className="text-center text-text-secondary py-10">No investments yet.</div>}
                </div>
            </div>
        </div>
    );
}
