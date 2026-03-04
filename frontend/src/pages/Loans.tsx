import { useEffect, useState } from 'react';
import { loansAPI } from '../services/loans.service';
import { Plus, Trash2, CreditCard, X, Save, AlertTriangle, Shield } from 'lucide-react';

export default function Loans() {
    const [loans, setLoans] = useState<any[]>([]);
    const [cards, setCards] = useState<any[]>([]);
    const [showLoanForm, setShowLoanForm] = useState(false);
    const [showCardForm, setShowCardForm] = useState(false);
    const [loanForm, setLoanForm] = useState({ loan_name: '', loan_type: 'personal', outstanding: '', emi: '', interest_rate: '', mode: 'personal' });
    const [cardForm, setCardForm] = useState({ card_name: '', credit_limit: '', credit_used: '', emi: '0' });
    const [loading, setLoading] = useState(true);

    const load = () => {
        Promise.all([loansAPI.getLoans(), loansAPI.getCreditCards()]).then(([l, c]) => {
            setLoans(l.data.data);
            setCards(c.data.data);
            setLoading(false);
        });
    };
    useEffect(load, []);

    const addLoan = async (e: React.FormEvent) => {
        e.preventDefault();
        await loansAPI.createLoan({ ...loanForm, outstanding: parseFloat(loanForm.outstanding), emi: parseFloat(loanForm.emi), interest_rate: loanForm.interest_rate ? parseFloat(loanForm.interest_rate) : undefined });
        setShowLoanForm(false);
        load();
    };

    const addCard = async (e: React.FormEvent) => {
        e.preventDefault();
        await loansAPI.createCreditCard({ ...cardForm, credit_limit: parseFloat(cardForm.credit_limit), credit_used: parseFloat(cardForm.credit_used), emi: parseFloat(cardForm.emi) });
        setShowCardForm(false);
        load();
    };

    if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" /></div>;

    const totalEmi = loans.reduce((s, l) => s + l.emi, 0) + cards.reduce((s, c) => s + c.emi, 0);
    const totalOutstanding = loans.reduce((s, l) => s + l.outstanding, 0);
    const totalCreditUsed = cards.reduce((s, c) => s + c.credit_used, 0);
    const totalLimit = cards.reduce((s, c) => s + c.credit_limit, 0);
    const utilization = totalLimit > 0 ? (totalCreditUsed / totalLimit * 100).toFixed(1) : '0';

    return (
        <div className="space-y-6">
            {/* Summary */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="glass-card p-4"><div className="text-xs text-text-muted mb-1">Total EMI</div><div className="text-xl font-bold text-danger">₹{totalEmi.toLocaleString('en-IN')}/mo</div></div>
                <div className="glass-card p-4"><div className="text-xs text-text-muted mb-1">Outstanding</div><div className="text-xl font-bold">₹{totalOutstanding.toLocaleString('en-IN')}</div></div>
                <div className="glass-card p-4"><div className="text-xs text-text-muted mb-1">Credit Used</div><div className="text-xl font-bold">₹{totalCreditUsed.toLocaleString('en-IN')}</div></div>
                <div className="glass-card p-4"><div className="text-xs text-text-muted mb-1">Utilization</div><div className={`text-xl font-bold ${parseFloat(utilization) > 30 ? 'text-warning' : 'text-success'}`}>{utilization}%</div></div>
            </div>

            {/* Loans */}
            <div>
                <div className="flex items-center justify-between mb-3">
                    <h2 className="text-lg font-semibold">Loans ({loans.length})</h2>
                    <button onClick={() => setShowLoanForm(!showLoanForm)} className="flex items-center gap-1.5 text-sm text-primary hover:text-primary-light"><Plus size={16} /> Add Loan</button>
                </div>
                {showLoanForm && (
                    <form onSubmit={addLoan} className="glass-card p-5 mb-4 space-y-3">
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            <input type="text" placeholder="Loan Name" value={loanForm.loan_name} onChange={e => setLoanForm(f => ({ ...f, loan_name: e.target.value }))} required className="px-3 py-2 rounded-lg bg-bg-input border border-border text-sm text-text-primary focus:border-primary outline-none" />
                            <input type="number" placeholder="Outstanding (₹)" value={loanForm.outstanding} onChange={e => setLoanForm(f => ({ ...f, outstanding: e.target.value }))} required className="px-3 py-2 rounded-lg bg-bg-input border border-border text-sm text-text-primary focus:border-primary outline-none" />
                            <input type="number" placeholder="Monthly EMI (₹)" value={loanForm.emi} onChange={e => setLoanForm(f => ({ ...f, emi: e.target.value }))} required className="px-3 py-2 rounded-lg bg-bg-input border border-border text-sm text-text-primary focus:border-primary outline-none" />
                        </div>
                        <div className="flex gap-2">
                            <button type="submit" className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-success text-white text-sm"><Save size={14} /> Save</button>
                            <button type="button" onClick={() => setShowLoanForm(false)} className="px-4 py-2 rounded-lg border border-border text-sm text-text-secondary hover:bg-bg-hover"><X size={14} /></button>
                        </div>
                    </form>
                )}
                <div className="space-y-3">
                    {loans.map(l => (
                        <div key={l.loan_id} className="glass-card-hover p-4 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-warning/10 text-warning"><AlertTriangle size={16} /></div>
                                <div>
                                    <div className="font-medium text-sm">{l.loan_name}</div>
                                    <div className="text-xs text-text-muted capitalize">{l.loan_type} • {l.mode}</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="font-bold">₹{l.outstanding.toLocaleString('en-IN')}</div>
                                <div className="text-xs text-text-muted">EMI: ₹{l.emi.toLocaleString('en-IN')}/mo</div>
                            </div>
                            <button onClick={async () => { await loansAPI.deleteLoan(l.loan_id); load(); }} className="ml-3 text-text-muted hover:text-danger"><Trash2 size={15} /></button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Credit Cards */}
            <div>
                <div className="flex items-center justify-between mb-3">
                    <h2 className="text-lg font-semibold">Credit Cards ({cards.length})</h2>
                    <button onClick={() => setShowCardForm(!showCardForm)} className="flex items-center gap-1.5 text-sm text-primary hover:text-primary-light"><Plus size={16} /> Add Card</button>
                </div>
                {showCardForm && (
                    <form onSubmit={addCard} className="glass-card p-5 mb-4 space-y-3">
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            <input type="text" placeholder="Card Name" value={cardForm.card_name} onChange={e => setCardForm(f => ({ ...f, card_name: e.target.value }))} required className="px-3 py-2 rounded-lg bg-bg-input border border-border text-sm text-text-primary focus:border-primary outline-none" />
                            <input type="number" placeholder="Credit Limit (₹)" value={cardForm.credit_limit} onChange={e => setCardForm(f => ({ ...f, credit_limit: e.target.value }))} required className="px-3 py-2 rounded-lg bg-bg-input border border-border text-sm text-text-primary focus:border-primary outline-none" />
                            <input type="number" placeholder="Credit Used (₹)" value={cardForm.credit_used} onChange={e => setCardForm(f => ({ ...f, credit_used: e.target.value }))} required className="px-3 py-2 rounded-lg bg-bg-input border border-border text-sm text-text-primary focus:border-primary outline-none" />
                        </div>
                        <div className="flex gap-2">
                            <button type="submit" className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-success text-white text-sm"><Save size={14} /> Save</button>
                            <button type="button" onClick={() => setShowCardForm(false)} className="px-4 py-2 rounded-lg border border-border text-sm text-text-secondary hover:bg-bg-hover"><X size={14} /></button>
                        </div>
                    </form>
                )}
                <div className="space-y-3">
                    {cards.map(c => {
                        const util = c.credit_limit > 0 ? (c.credit_used / c.credit_limit * 100) : 0;
                        return (
                            <div key={c.card_id} className="glass-card-hover p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-secondary/10 text-secondary"><CreditCard size={16} /></div>
                                        <span className="font-medium text-sm">{c.card_name}</span>
                                    </div>
                                    <button onClick={async () => { await loansAPI.deleteCreditCard(c.card_id); load(); }} className="text-text-muted hover:text-danger"><Trash2 size={15} /></button>
                                </div>
                                <div className="w-full bg-bg-hover rounded-full h-2 mb-2">
                                    <div className={`h-2 rounded-full transition-all ${util > 50 ? 'bg-danger' : util > 30 ? 'bg-warning' : 'bg-success'}`} style={{ width: `${Math.min(util, 100)}%` }} />
                                </div>
                                <div className="flex justify-between text-xs text-text-secondary">
                                    <span>₹{c.credit_used.toLocaleString('en-IN')} used</span>
                                    <span>₹{c.credit_limit.toLocaleString('en-IN')} limit ({util.toFixed(1)}%)</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
