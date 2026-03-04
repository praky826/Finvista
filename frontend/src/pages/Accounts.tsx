import { useEffect, useState } from 'react';
import { accountsAPI } from '../services/accounts.service';
import { Plus, Pencil, Trash2, Wallet, X, Save } from 'lucide-react';

export default function Accounts() {
    const [accounts, setAccounts] = useState<any[]>([]);
    const [totalBalance, setTotalBalance] = useState(0);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ bank_name: '', account_type: 'savings', balance: '', mode: 'personal' });
    const [loading, setLoading] = useState(true);

    const load = () => {
        accountsAPI.getAccounts().then(res => {
            setAccounts(res.data.data.accounts);
            setTotalBalance(res.data.data.total_balance);
            setLoading(false);
        });
    };

    useEffect(load, []);

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        await accountsAPI.createAccount({ ...form, balance: parseFloat(form.balance) });
        setForm({ bank_name: '', account_type: 'savings', balance: '', mode: 'personal' });
        setShowForm(false);
        load();
    };

    const handleDelete = async (id: number) => {
        if (confirm('Delete this account?')) {
            await accountsAPI.deleteAccount(id);
            load();
        }
    };

    if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" /></div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Bank Accounts</h1>
                    <p className="text-text-secondary text-sm">Total Balance: <span className="text-primary font-semibold">₹{totalBalance.toLocaleString('en-IN')}</span></p>
                </div>
                <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors">
                    {showForm ? <X size={16} /> : <Plus size={16} />} {showForm ? 'Cancel' : 'Add Account'}
                </button>
            </div>

            {showForm && (
                <form onSubmit={handleAdd} className="glass-card p-6 space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Bank Name</label>
                            <input type="text" value={form.bank_name} onChange={e => setForm(f => ({ ...f, bank_name: e.target.value }))} required className="w-full px-4 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary focus:border-primary outline-none" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Type</label>
                            <select value={form.account_type} onChange={e => setForm(f => ({ ...f, account_type: e.target.value }))} className="w-full px-4 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary focus:border-primary outline-none">
                                <option value="savings">Savings</option>
                                <option value="current">Current</option>
                                <option value="salary">Salary</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Balance (₹)</label>
                            <input type="number" step="0.01" min="0" value={form.balance} onChange={e => setForm(f => ({ ...f, balance: e.target.value }))} required className="w-full px-4 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary focus:border-primary outline-none" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Mode</label>
                            <select value={form.mode} onChange={e => setForm(f => ({ ...f, mode: e.target.value }))} className="w-full px-4 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary focus:border-primary outline-none">
                                <option value="personal">Personal</option>
                                <option value="business">Business</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-success hover:bg-success/80 text-white text-sm font-medium transition-colors">
                        <Save size={16} /> Save Account
                    </button>
                </form>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {accounts.map(a => (
                    <div key={a.account_id} className="glass-card-hover p-5">
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-primary/10 text-primary"><Wallet size={18} /></div>
                                <div>
                                    <h3 className="font-medium text-sm">{a.bank_name}</h3>
                                    <span className="text-xs text-text-muted capitalize">{a.account_type} • {a.mode}</span>
                                </div>
                            </div>
                            <button onClick={() => handleDelete(a.account_id)} className="text-text-muted hover:text-danger transition-colors"><Trash2 size={16} /></button>
                        </div>
                        <div className="text-2xl font-bold">₹{a.balance.toLocaleString('en-IN')}</div>
                    </div>
                ))}
                {accounts.length === 0 && <div className="col-span-full text-center text-text-secondary py-10">No accounts yet. Add your first bank account.</div>}
            </div>
        </div>
    );
}
