import { useEffect, useState } from 'react';
import { investmentsAPI } from '../services/investments.service';
import { Plus, Trash2, Target, X, Save, Clock, Flag } from 'lucide-react';

const PRIORITY_COLORS: Record<string, string> = { high: 'text-danger bg-danger/10', medium: 'text-warning bg-warning/10', low: 'text-success bg-success/10' };

export default function Goals() {
    const [goals, setGoals] = useState<any[]>([]);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ goal_name: '', target: '', deadline: '', current_savings: '0', mode: 'personal', priority: 'medium' });
    const [loading, setLoading] = useState(true);

    const load = () => { investmentsAPI.getGoals().then(res => { setGoals(res.data.data); setLoading(false); }); };
    useEffect(load, []);

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        await investmentsAPI.createGoal({ ...form, target: parseFloat(form.target), current_savings: parseFloat(form.current_savings) });
        setShowForm(false);
        setForm({ goal_name: '', target: '', deadline: '', current_savings: '0', mode: 'personal', priority: 'medium' });
        load();
    };

    if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" /></div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Financial Goals</h1>
                <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-medium">
                    {showForm ? <X size={16} /> : <Plus size={16} />} {showForm ? 'Cancel' : 'New Goal'}
                </button>
            </div>

            {showForm && (
                <form onSubmit={handleAdd} className="glass-card p-6 space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Goal Name</label>
                            <input type="text" value={form.goal_name} onChange={e => setForm(f => ({ ...f, goal_name: e.target.value }))} required className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none" placeholder="e.g., Emergency Fund" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Target Amount (₹)</label>
                            <input type="number" value={form.target} onChange={e => setForm(f => ({ ...f, target: e.target.value }))} required className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Deadline</label>
                            <input type="date" value={form.deadline} onChange={e => setForm(f => ({ ...f, deadline: e.target.value }))} required className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Current Savings (₹)</label>
                            <input type="number" value={form.current_savings} onChange={e => setForm(f => ({ ...f, current_savings: e.target.value }))} className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Priority</label>
                            <select value={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.value }))} className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none">
                                <option value="high">High</option>
                                <option value="medium">Medium</option>
                                <option value="low">Low</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Mode</label>
                            <select value={form.mode} onChange={e => setForm(f => ({ ...f, mode: e.target.value }))} className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none">
                                <option value="personal">Personal</option>
                                <option value="business">Business</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-success text-white text-sm font-medium"><Save size={16} /> Create Goal</button>
                </form>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {goals.map((g: any) => {
                    const progress = g.target > 0 ? (g.current_savings / g.target * 100) : 0;
                    const today = new Date();
                    const deadline = new Date(g.deadline);
                    const daysLeft = Math.max(Math.ceil((deadline.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)), 0);
                    const monthsLeft = Math.max(Math.ceil(daysLeft / 30), 0);
                    return (
                        <div key={g.goal_id} className="glass-card-hover p-5">
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <Target size={18} className="text-primary" />
                                    <h3 className="font-semibold text-sm">{g.goal_name}</h3>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${PRIORITY_COLORS[g.priority] || PRIORITY_COLORS.medium}`}>
                                        {g.priority}
                                    </span>
                                    <button onClick={async () => { await investmentsAPI.deleteGoal(g.goal_id); load(); }} className="text-text-muted hover:text-danger"><Trash2 size={14} /></button>
                                </div>
                            </div>
                            <div className="w-full bg-bg-hover rounded-full h-3 mb-3">
                                <div className={`h-3 rounded-full transition-all duration-700 ${progress >= 100 ? 'bg-success' : progress >= 50 ? 'bg-primary' : 'bg-warning'}`} style={{ width: `${Math.min(progress, 100)}%` }} />
                            </div>
                            <div className="flex justify-between text-xs text-text-secondary mb-1">
                                <span>₹{Number(g.current_savings).toLocaleString('en-IN')}</span>
                                <span className="font-medium">{progress.toFixed(1)}%</span>
                                <span>₹{Number(g.target).toLocaleString('en-IN')}</span>
                            </div>
                            <div className="flex items-center gap-3 text-xs text-text-muted mt-3">
                                <span className="flex items-center gap-1"><Clock size={12} /> {monthsLeft} months left</span>
                                <span className="flex items-center gap-1"><Flag size={12} /> {g.mode}</span>
                            </div>
                        </div>
                    );
                })}
                {goals.length === 0 && <div className="col-span-full text-center text-text-secondary py-10">No goals yet. Set a financial target!</div>}
            </div>
        </div>
    );
}
