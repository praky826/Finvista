import { useEffect, useState } from 'react';
import { taxAPI } from '../services/tax.service';
import { Calculator, ArrowRight, Save, CheckCircle } from 'lucide-react';

export default function Tax() {
    const [taxData, setTaxData] = useState<any>(null);
    const [comparison, setComparison] = useState<any>(null);
    const [editing, setEditing] = useState(false);
    const [form, setForm] = useState({ regime: 'new', annual_income: '', deductions_80c: '', deductions_80d: '', deductions_80tta: '', other_deductions: '' });
    const [loading, setLoading] = useState(true);

    const load = () => {
        Promise.all([taxAPI.getTax().catch(() => ({ data: { data: null } })), taxAPI.getTaxComparison().catch(() => ({ data: { data: null } }))])
            .then(([t, c]) => {
                if (t.data.data) {
                    setTaxData(t.data.data);
                    setForm({
                        regime: t.data.data.regime || 'new',
                        annual_income: String(t.data.data.annual_income || ''),
                        deductions_80c: String(t.data.data.deductions_80c || ''),
                        deductions_80d: String(t.data.data.deductions_80d || ''),
                        deductions_80tta: String(t.data.data.deductions_80tta || ''),
                        other_deductions: String(t.data.data.other_deductions || ''),
                    });
                }
                if (c.data.data) setComparison(c.data.data);
                setLoading(false);
            });
    };
    useEffect(load, []);

    const handleSave = async () => {
        const data: any = { regime: form.regime };
        if (form.annual_income) data.annual_income = parseFloat(form.annual_income);
        if (form.deductions_80c) data.deductions_80c = parseFloat(form.deductions_80c);
        if (form.deductions_80d) data.deductions_80d = parseFloat(form.deductions_80d);
        if (form.deductions_80tta) data.deductions_80tta = parseFloat(form.deductions_80tta);
        if (form.other_deductions) data.other_deductions = parseFloat(form.other_deductions);
        await taxAPI.updateTax(data);
        setEditing(false);
        load();
    };

    if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" /></div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Tax Planning</h1>
                <button onClick={() => setEditing(!editing)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-medium">
                    {editing ? 'Cancel' : 'Edit Tax Info'}
                </button>
            </div>

            {/* Edit Form */}
            {editing && (
                <div className="glass-card p-6 space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Regime</label>
                            <select value={form.regime} onChange={e => setForm(f => ({ ...f, regime: e.target.value }))} className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none">
                                <option value="old">Old Regime</option>
                                <option value="new">New Regime</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Annual Income (₹)</label>
                            <input type="number" value={form.annual_income} onChange={e => setForm(f => ({ ...f, annual_income: e.target.value }))} className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">80C Deductions (max ₹1.5L)</label>
                            <input type="number" max="150000" value={form.deductions_80c} onChange={e => setForm(f => ({ ...f, deductions_80c: e.target.value }))} className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">80D Health Insurance (max ₹25K)</label>
                            <input type="number" max="25000" value={form.deductions_80d} onChange={e => setForm(f => ({ ...f, deductions_80d: e.target.value }))} className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">80TTA Savings Interest (max ₹10K)</label>
                            <input type="number" max="10000" value={form.deductions_80tta} onChange={e => setForm(f => ({ ...f, deductions_80tta: e.target.value }))} className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Other Deductions (₹)</label>
                            <input type="number" value={form.other_deductions} onChange={e => setForm(f => ({ ...f, other_deductions: e.target.value }))} className="w-full px-3 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary outline-none" />
                        </div>
                    </div>
                    <button onClick={handleSave} className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-success text-white text-sm font-medium"><Save size={16} /> Save Tax Info</button>
                </div>
            )}

            {/* Comparison Cards */}
            {comparison && (
                <div>
                    <h2 className="text-lg font-semibold mb-3">Old vs New Regime Comparison</h2>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                        {/* Old Regime */}
                        <div className={`glass-card p-5 ${comparison.recommended === 'old' ? 'border-success/50' : ''}`}>
                            {comparison.recommended === 'old' && <div className="flex items-center gap-1.5 text-success text-xs font-medium mb-2"><CheckCircle size={14} /> Recommended</div>}
                            <h3 className="font-semibold mb-3">Old Regime</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between"><span className="text-text-secondary">Gross Income</span><span>₹{comparison.old_regime.gross_income?.toLocaleString('en-IN')}</span></div>
                                <div className="flex justify-between"><span className="text-text-secondary">Deductions</span><span className="text-success">-₹{comparison.old_regime.total_deductions?.toLocaleString('en-IN')}</span></div>
                                <div className="flex justify-between"><span className="text-text-secondary">Taxable</span><span>₹{comparison.old_regime.taxable_income?.toLocaleString('en-IN')}</span></div>
                                <div className="border-t border-border pt-2 flex justify-between font-bold"><span>Total Tax</span><span className="text-danger">₹{comparison.old_regime.total_tax?.toLocaleString('en-IN')}</span></div>
                                <div className="flex justify-between text-xs"><span className="text-text-muted">Effective Rate</span><span>{comparison.old_regime.effective_tax_rate}%</span></div>
                            </div>
                        </div>

                        {/* Arrow */}
                        <div className="hidden lg:flex items-center justify-center">
                            <div className="glass-card p-6 text-center">
                                <div className="text-2xl font-bold text-success mb-1">₹{comparison.savings_with_recommended?.toLocaleString('en-IN')}</div>
                                <div className="text-xs text-text-muted">Savings with {comparison.recommended} regime</div>
                            </div>
                        </div>

                        {/* New Regime */}
                        <div className={`glass-card p-5 ${comparison.recommended === 'new' ? 'border-success/50' : ''}`}>
                            {comparison.recommended === 'new' && <div className="flex items-center gap-1.5 text-success text-xs font-medium mb-2"><CheckCircle size={14} /> Recommended</div>}
                            <h3 className="font-semibold mb-3">New Regime</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between"><span className="text-text-secondary">Gross Income</span><span>₹{comparison.new_regime.gross_income?.toLocaleString('en-IN')}</span></div>
                                <div className="flex justify-between"><span className="text-text-secondary">Std. Deduction</span><span className="text-success">-₹{comparison.new_regime.standard_deduction?.toLocaleString('en-IN')}</span></div>
                                <div className="flex justify-between"><span className="text-text-secondary">Taxable</span><span>₹{comparison.new_regime.taxable_income?.toLocaleString('en-IN')}</span></div>
                                {comparison.new_regime.section_87a_rebate > 0 && <div className="flex justify-between"><span className="text-text-secondary">87A Rebate</span><span className="text-success">-₹{comparison.new_regime.section_87a_rebate?.toLocaleString('en-IN')}</span></div>}
                                <div className="border-t border-border pt-2 flex justify-between font-bold"><span>Total Tax</span><span className="text-danger">₹{comparison.new_regime.total_tax?.toLocaleString('en-IN')}</span></div>
                                <div className="flex justify-between text-xs"><span className="text-text-muted">Effective Rate</span><span>{comparison.new_regime.effective_tax_rate}%</span></div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
