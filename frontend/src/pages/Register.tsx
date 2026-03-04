import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/auth.service';
import { taxAPI } from '../services/tax.service';
import { accountsAPI } from '../services/accounts.service';
import { loansAPI } from '../services/loans.service';
import { investmentsAPI } from '../services/investments.service';
import { businessAPI } from '../services/business.service';
import {
    Eye, EyeOff, UserPlus, ChevronRight, ChevronLeft, Check,
    Plus, Trash2, Building2, User, Users, Briefcase
} from 'lucide-react';

/* ─── Types ─── */
interface BankEntry { bank_name: string; account_type: string; balance: string; mode: string }
interface CreditCardEntry { card_name: string; credit_limit: string; credit_used: string; mode: string }
interface LoanEntry { loan_name: string; loan_type: string; outstanding: string; emi: string; interest_rate: string; mode: string }
interface InvestmentEntry { type: string; value: string; interest_rate: string; mode: string }
interface GoalEntry { goal_name: string; target: string; deadline: string; current_savings: string; mode: string }

/* Step defs */
const PERSONAL_STEPS = ['Account Type', 'Authentication', 'Income', 'Bank Accounts', 'Credit Cards', 'Loans', 'Investments', 'Tax', 'Goals', 'Review'];
const BUSINESS_STEPS = ['Account Type', 'Authentication', 'Income', 'Bank Accounts', 'Credit Cards', 'Loans', 'Investments', 'Working Capital', 'Tax', 'Goals', 'Review'];

export default function Register() {
    const { registerAndLogin } = useAuth();
    const navigate = useNavigate();

    /* ─── Step nav ─── */
    const [step, setStep] = useState(0);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    /* Step 1 */
    const [accountType, setAccountType] = useState('personal');
    /* Step 2 */
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPwd, setShowPwd] = useState(false);
    /* Step 3 */
    const [monthlyIncome, setMonthlyIncome] = useState('');
    const [otherIncome, setOtherIncome] = useState('');
    const [bizRevenue, setBizRevenue] = useState('');
    const [bizExpenses, setBizExpenses] = useState('');
    const [bizCogs, setBizCogs] = useState('');
    /* Step 4 */
    const [banks, setBanks] = useState<BankEntry[]>([]);
    /* Step 5 */
    const [cards, setCards] = useState<CreditCardEntry[]>([]);
    /* Step 6 */
    const [loans, setLoans] = useState<LoanEntry[]>([]);
    /* Step 7 */
    const [investments, setInvestments] = useState<InvestmentEntry[]>([]);
    /* Business working capital */
    const [inventory, setInventory] = useState('');
    const [receivables, setReceivables] = useState('');
    const [payables, setPayables] = useState('');
    /* Tax */
    const [deductions80c, setDeductions80c] = useState('');
    const [deductions80d, setDeductions80d] = useState('');
    const [deductions80tta, setDeductions80tta] = useState('');
    const [otherDeductions, setOtherDeductions] = useState('');
    const [taxRegime, setTaxRegime] = useState('new');
    /* Goals */
    const [goals, setGoals] = useState<GoalEntry[]>([]);

    const isBiz = accountType === 'business' || accountType === 'both';
    const steps = isBiz ? BUSINESS_STEPS : PERSONAL_STEPS;
    const defaultMode = accountType === 'business' ? 'business' : 'personal';

    /* ─── Validation helpers ─── */
    const pwdChecks = {
        length: password.length >= 8,
        upper: /[A-Z]/.test(password),
        lower: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };

    const canNext = (): boolean => {
        if (step === 0) return true;
        if (steps[step] === 'Authentication') {
            return fullName.length > 0 && email.includes('@') && username.length >= 6
                && Object.values(pwdChecks).every(Boolean) && password === confirmPassword;
        }
        if (steps[step] === 'Income') {
            if (isBiz) return Number(bizRevenue) > 0;
            return Number(monthlyIncome) > 0;
        }
        return true; // optional steps
    };

    /* ─── Final submit ─── */
    const handleFinish = async () => {
        setError('');
        setLoading(true);
        try {
            // 1. Register + auto-login
            await registerAndLogin({ full_name: fullName, email, username, password, account_type: accountType });

            // 2. Save income via tax update
            const taxData: any = { regime: taxRegime };
            if (accountType !== 'business') {
                taxData.annual_income = Number(monthlyIncome) * 12;
                taxData.monthly_income = Number(monthlyIncome);
                taxData.deductions_80c = Number(deductions80c) || 0;
                taxData.deductions_80d = Number(deductions80d) || 0;
                taxData.deductions_80tta = Number(deductions80tta) || 0;
                taxData.other_deductions = Number(otherDeductions) || 0;
            }
            if (isBiz) {
                if (bizRevenue) taxData.business_revenue = Number(bizRevenue) * 12;
                if (bizExpenses) taxData.business_expenses = Number(bizExpenses) * 12;
                if (bizCogs) taxData.cogs = Number(bizCogs) * 12;
            }
            await taxAPI.updateTax(taxData);

            // 3. Save bank accounts
            for (const b of banks) {
                if (b.bank_name && Number(b.balance) >= 0) {
                    await accountsAPI.createAccount({ bank_name: b.bank_name, account_type: b.account_type, balance: Number(b.balance), mode: b.mode });
                }
            }

            // 4. Save credit cards
            for (const c of cards) {
                if (c.card_name) {
                    await loansAPI.createCreditCard({ card_name: c.card_name, credit_limit: Number(c.credit_limit), credit_used: Number(c.credit_used), emi: 0 });
                }
            }

            // 5. Save loans
            for (const l of loans) {
                if (l.loan_name) {
                    await loansAPI.createLoan({ loan_name: l.loan_name, loan_type: l.loan_type, outstanding: Number(l.outstanding), emi: Number(l.emi), interest_rate: Number(l.interest_rate), mode: l.mode });
                }
            }

            // 6. Save investments
            for (const inv of investments) {
                if (inv.type) {
                    await investmentsAPI.createInvestment({ type: inv.type, value: Number(inv.value), interest_rate: Number(inv.interest_rate), mode: inv.mode });
                }
            }

            // 7. Business working capital
            if (isBiz) {
                if (Number(inventory) > 0) await businessAPI.createInventory({ item_name: 'Total Inventory', quantity: 1, unit_cost: Number(inventory) });
                if (Number(receivables) > 0) await businessAPI.createReceivable({ customer_name: 'Total Receivables', invoice_amount: Number(receivables), due_date: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0] });
                if (Number(payables) > 0) await businessAPI.createPayable({ vendor_name: 'Total Payables', bill_amount: Number(payables), due_date: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0] });
            }

            // 8. Save goals
            for (const g of goals) {
                if (g.goal_name) {
                    await investmentsAPI.createGoal({ goal_name: g.goal_name, target: Number(g.target), deadline: g.deadline, current_savings: Number(g.current_savings), mode: g.mode });
                }
            }

            // 9. Complete setup → triggers recalculation
            await authAPI.completeSetup();

            navigate('/dashboard');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    /* ─── Step renderers ─── */
    const stepContent = () => {
        const current = steps[step];

        if (current === 'Account Type') return (
            <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-2">Select Account Type</h3>
                <p className="text-sm text-text-secondary mb-4">Choose how you'll use FINVISTA</p>
                {[
                    { val: 'personal', icon: <User size={24} />, label: 'Personal', desc: 'Track personal finances, investments, tax' },
                    { val: 'business', icon: <Briefcase size={24} />, label: 'Business', desc: 'Track business revenue, expenses, working capital' },
                    { val: 'both', icon: <Users size={24} />, label: 'Both', desc: 'Personal + Business financial tracking' },
                ].map(opt => (
                    <button key={opt.val} onClick={() => setAccountType(opt.val)}
                        className={`w-full p-4 rounded-xl border text-left flex items-start gap-4 transition-all ${accountType === opt.val ? 'border-primary bg-primary/10' : 'border-border hover:border-text-muted'}`}>
                        <span className={accountType === opt.val ? 'text-primary' : 'text-text-muted'}>{opt.icon}</span>
                        <div>
                            <div className="font-medium">{opt.label}</div>
                            <div className="text-sm text-text-secondary">{opt.desc}</div>
                        </div>
                    </button>
                ))}
            </div>
        );

        if (current === 'Authentication') return (
            <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-2">Create Your Account</h3>
                <InputField label="Full Name" value={fullName} onChange={setFullName} placeholder="e.g. Phani Kumar" required />
                <InputField label="Email" type="email" value={email} onChange={setEmail} placeholder="e.g. phani@example.com" required />
                <InputField label="Username" value={username} onChange={setUsername} placeholder="Min 6 chars, alphanumeric + underscore" required hint={username.length > 0 && username.length < 6 ? 'Username must be at least 6 characters' : undefined} />
                <div>
                    <label className="block text-sm text-text-secondary mb-1.5">Password</label>
                    <div className="relative">
                        <input type={showPwd ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)}
                            className="w-full px-4 py-3 rounded-xl bg-bg-input border border-border text-text-primary placeholder-text-muted focus:border-primary outline-none transition-all pr-12" placeholder="Min 8 chars" />
                        <button type="button" onClick={() => setShowPwd(!showPwd)} className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary">
                            {showPwd ? <EyeOff size={18} /> : <Eye size={18} />}
                        </button>
                    </div>
                    {password.length > 0 && (
                        <div className="mt-2 grid grid-cols-2 gap-1 text-xs">
                            {Object.entries({ '8+ characters': pwdChecks.length, 'Uppercase': pwdChecks.upper, 'Lowercase': pwdChecks.lower, 'Number': pwdChecks.number, 'Special char': pwdChecks.special }).map(([l, ok]) => (
                                <span key={l} className={ok ? 'text-success' : 'text-text-muted'}>
                                    {ok ? '✓' : '○'} {l}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
                <InputField label="Confirm Password" type="password" value={confirmPassword} onChange={setConfirmPassword} placeholder="Re-enter password" required
                    hint={confirmPassword.length > 0 && password !== confirmPassword ? 'Passwords do not match' : undefined} />
            </div>
        );

        if (current === 'Income') return (
            <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-2">Income Setup</h3>
                {accountType !== 'business' && <>
                    <InputField label="Monthly Income (₹)" type="number" value={monthlyIncome} onChange={setMonthlyIncome} placeholder="e.g. 50000" required />
                    {monthlyIncome && <p className="text-sm text-text-secondary">Annual: ₹{(Number(monthlyIncome) * 12).toLocaleString('en-IN')}</p>}
                    <InputField label="Other Monthly Income (₹, optional)" type="number" value={otherIncome} onChange={setOtherIncome} placeholder="Freelance, rent, dividends..." />
                </>}
                {isBiz && <>
                    <InputField label="Monthly Business Revenue (₹)" type="number" value={bizRevenue} onChange={setBizRevenue} placeholder="e.g. 100000" required />
                    {bizRevenue && <p className="text-sm text-text-secondary">Annual: ₹{(Number(bizRevenue) * 12).toLocaleString('en-IN')}</p>}
                    <InputField label="Monthly Operating Expenses (₹)" type="number" value={bizExpenses} onChange={setBizExpenses} placeholder="e.g. 40000" />
                    <InputField label="Cost of Goods Sold (₹, optional)" type="number" value={bizCogs} onChange={setBizCogs} placeholder="Product-based businesses" />
                </>}
            </div>
        );

        if (current === 'Bank Accounts') return (
            <ListStep title="Bank Accounts" subtitle="Add your bank accounts" items={banks} setItems={setBanks}
                defaultItem={{ bank_name: '', account_type: 'savings', balance: '', mode: defaultMode }}
                renderItem={(b, i) => (
                    <div className="space-y-3">
                        <InputField label="Bank Name" value={b.bank_name} onChange={v => updateList(banks, setBanks, i, 'bank_name', v)} placeholder="e.g. SBI" />
                        <div className="grid grid-cols-2 gap-3">
                            <SelectField label="Type" value={b.account_type} onChange={v => updateList(banks, setBanks, i, 'account_type', v)} options={['savings', 'current', 'salary', 'fd']} />
                            <InputField label="Balance (₹)" type="number" value={b.balance} onChange={v => updateList(banks, setBanks, i, 'balance', v)} placeholder="0" />
                        </div>
                        {accountType === 'both' && <SelectField label="Mode" value={b.mode} onChange={v => updateList(banks, setBanks, i, 'mode', v)} options={['personal', 'business']} />}
                    </div>
                )} />
        );

        if (current === 'Credit Cards') return (
            <ListStep title="Credit Cards" subtitle="Add your credit cards" items={cards} setItems={setCards}
                defaultItem={{ card_name: '', credit_limit: '', credit_used: '', mode: defaultMode }}
                renderItem={(c, i) => (
                    <div className="space-y-3">
                        <InputField label="Card Name" value={c.card_name} onChange={v => updateList(cards, setCards, i, 'card_name', v)} placeholder="e.g. HDFC Regalia" />
                        <div className="grid grid-cols-2 gap-3">
                            <InputField label="Credit Limit (₹)" type="number" value={c.credit_limit} onChange={v => updateList(cards, setCards, i, 'credit_limit', v)} placeholder="100000" />
                            <InputField label="Credit Used (₹)" type="number" value={c.credit_used} onChange={v => updateList(cards, setCards, i, 'credit_used', v)} placeholder="25000" />
                        </div>
                    </div>
                )} />
        );

        if (current === 'Loans') return (
            <ListStep title="Loans" subtitle="Add your loans (home loan, car loan, etc.)" items={loans} setItems={setLoans}
                defaultItem={{ loan_name: '', loan_type: 'home_loan', outstanding: '', emi: '', interest_rate: '', mode: defaultMode }}
                renderItem={(l, i) => (
                    <div className="space-y-3">
                        <InputField label="Loan Name" value={l.loan_name} onChange={v => updateList(loans, setLoans, i, 'loan_name', v)} placeholder="e.g. Home Loan SBI" />
                        <SelectField label="Loan Type" value={l.loan_type} onChange={v => updateList(loans, setLoans, i, 'loan_type', v)} options={['home_loan', 'car_loan', 'personal_loan', 'education_loan', 'business_loan', 'other']} />
                        <div className="grid grid-cols-2 gap-3">
                            <InputField label="Outstanding (₹)" type="number" value={l.outstanding} onChange={v => updateList(loans, setLoans, i, 'outstanding', v)} placeholder="4000000" />
                            <InputField label="Monthly EMI (₹)" type="number" value={l.emi} onChange={v => updateList(loans, setLoans, i, 'emi', v)} placeholder="50000" />
                        </div>
                        <InputField label="Interest Rate (%)" type="number" value={l.interest_rate} onChange={v => updateList(loans, setLoans, i, 'interest_rate', v)} placeholder="7.5" />
                    </div>
                )} />
        );

        if (current === 'Investments') return (
            <ListStep title="Investments" subtitle="Add your investments" items={investments} setItems={setInvestments}
                defaultItem={{ type: 'mutual_fund', value: '', interest_rate: '', mode: defaultMode }}
                renderItem={(inv, i) => (
                    <div className="space-y-3">
                        <SelectField label="Type" value={inv.type} onChange={v => updateList(investments, setInvestments, i, 'type', v)}
                            options={['mutual_fund', 'stocks', 'fd', 'ppf', 'gold', 'real_estate', 'crypto', 'bonds', 'other']} />
                        <div className="grid grid-cols-2 gap-3">
                            <InputField label="Value (₹)" type="number" value={inv.value} onChange={v => updateList(investments, setInvestments, i, 'value', v)} placeholder="500000" />
                            <InputField label="Return Rate (%)" type="number" value={inv.interest_rate} onChange={v => updateList(investments, setInvestments, i, 'interest_rate', v)} placeholder="12" />
                        </div>
                    </div>
                )} />
        );

        if (current === 'Working Capital') return (
            <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-2">Business Working Capital</h3>
                <p className="text-sm text-text-secondary mb-4">Enter current values for working capital calculation</p>
                <InputField label="Total Inventory Value (₹)" type="number" value={inventory} onChange={setInventory} placeholder="e.g. 200000" />
                <InputField label="Total Accounts Receivable (₹)" type="number" value={receivables} onChange={setReceivables} placeholder="Amount owed to you" />
                <InputField label="Total Accounts Payable (₹)" type="number" value={payables} onChange={setPayables} placeholder="Amount you owe" />
            </div>
        );

        if (current === 'Tax') return (
            <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-2">Tax Setup</h3>
                {accountType !== 'business' && <>
                    <SelectField label="Preferred Tax Regime" value={taxRegime} onChange={setTaxRegime} options={['old', 'new']} />
                    <InputField label="Section 80C Deductions (₹)" type="number" value={deductions80c} onChange={setDeductions80c} placeholder="LIC, PPF, ELSS (max ₹1.5L)" />
                    <InputField label="Health Insurance 80D (₹)" type="number" value={deductions80d} onChange={setDeductions80d} placeholder="Medical insurance (max ₹25K)" />
                    <InputField label="Savings Interest 80TTA (₹)" type="number" value={deductions80tta} onChange={setDeductions80tta} placeholder="Savings account interest (max ₹10K)" />
                    <InputField label="Other Deductions (₹)" type="number" value={otherDeductions} onChange={setOtherDeductions} placeholder="Any other deductions" />
                </>}
                {isBiz && <p className="text-sm text-text-secondary">Business tax is auto-calculated from revenue, expenses, and COGS you entered earlier.</p>}
            </div>
        );

        if (current === 'Goals') return (
            <ListStep title="Financial Goals" subtitle="Set your targets (optional)" items={goals} setItems={setGoals}
                defaultItem={{ goal_name: '', target: '', deadline: '', current_savings: '', mode: defaultMode }}
                renderItem={(g, i) => (
                    <div className="space-y-3">
                        <InputField label="Goal Name" value={g.goal_name} onChange={v => updateList(goals, setGoals, i, 'goal_name', v)} placeholder="e.g. Buy a house" />
                        <div className="grid grid-cols-2 gap-3">
                            <InputField label="Target Amount (₹)" type="number" value={g.target} onChange={v => updateList(goals, setGoals, i, 'target', v)} placeholder="5000000" />
                            <InputField label="Saved So Far (₹)" type="number" value={g.current_savings} onChange={v => updateList(goals, setGoals, i, 'current_savings', v)} placeholder="500000" />
                        </div>
                        <InputField label="Target Date" type="date" value={g.deadline} onChange={v => updateList(goals, setGoals, i, 'deadline', v)} placeholder="" />
                    </div>
                )} />
        );

        if (current === 'Review') return (
            <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-2">Review & Complete</h3>
                <div className="space-y-3">
                    <ReviewRow label="Account Type" value={accountType} />
                    <ReviewRow label="Name" value={fullName} />
                    <ReviewRow label="Email" value={email} />
                    <ReviewRow label="Username" value={username} />
                    {accountType !== 'business' && <ReviewRow label="Monthly Income" value={`₹${Number(monthlyIncome).toLocaleString('en-IN')}`} />}
                    {isBiz && <ReviewRow label="Business Revenue" value={`₹${Number(bizRevenue).toLocaleString('en-IN')}/mo`} />}
                    <ReviewRow label="Bank Accounts" value={`${banks.length} added`} />
                    <ReviewRow label="Credit Cards" value={`${cards.length} added`} />
                    <ReviewRow label="Loans" value={`${loans.length} added`} />
                    <ReviewRow label="Investments" value={`${investments.length} added`} />
                    <ReviewRow label="Goals" value={`${goals.length} added`} />
                    <ReviewRow label="Tax Regime" value={taxRegime.toUpperCase()} />
                </div>
                <p className="text-sm text-text-secondary mt-4">Click "Complete Registration" to create your account and set up your dashboard.</p>
            </div>
        );

        return null;
    };

    /* ─── UI ─── */
    return (
        <div className="min-h-screen bg-bg-primary flex items-center justify-center p-4">
            <div className="w-full max-w-lg">
                <div className="text-center mb-6">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-primary via-primary-light to-secondary bg-clip-text text-transparent mb-1">FINVISTA</h1>
                    <p className="text-text-secondary text-sm">Financial Analytics Platform</p>
                </div>

                {/* Progress bar */}
                <div className="mb-4">
                    <div className="flex items-center justify-between text-xs text-text-muted mb-1.5">
                        <span>Step {step + 1} of {steps.length}</span>
                        <span>{steps[step]}</span>
                    </div>
                    <div className="w-full bg-bg-input rounded-full h-1.5">
                        <div className="bg-gradient-to-r from-primary to-secondary h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${((step + 1) / steps.length) * 100}%` }} />
                    </div>
                </div>

                <div className="glass-card p-6">
                    {error && <div className="mb-4 p-3 rounded-lg bg-danger/10 border border-danger/20 text-danger text-sm">{error}</div>}

                    {stepContent()}

                    {/* Nav buttons */}
                    <div className="flex items-center justify-between mt-6 pt-4 border-t border-border">
                        {step > 0 ? (
                            <button onClick={() => { setStep(s => s - 1); setError(''); }} className="px-4 py-2 rounded-xl border border-border text-text-secondary hover:text-text-primary hover:border-text-muted transition-all flex items-center gap-1.5 text-sm">
                                <ChevronLeft size={16} /> Back
                            </button>
                        ) : (
                            <Link to="/login" className="text-sm text-text-secondary hover:text-primary transition-colors">Already have an account? Log in</Link>
                        )}

                        {steps[step] === 'Review' ? (
                            <button onClick={handleFinish} disabled={loading}
                                className="px-6 py-2.5 rounded-xl bg-success hover:bg-success/90 text-white font-medium transition-all flex items-center gap-2 text-sm disabled:opacity-50">
                                {loading ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" /> : <><Check size={16} /> Complete Registration</>}
                            </button>
                        ) : (
                            <button onClick={() => { if (canNext()) { setStep(s => s + 1); setError(''); } }}
                                disabled={!canNext()}
                                className="px-5 py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white font-medium transition-all flex items-center gap-1.5 text-sm disabled:opacity-40">
                                Next <ChevronRight size={16} />
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ─── Helper components ─── */
function InputField({ label, type = 'text', value, onChange, placeholder, required, hint }: {
    label: string; type?: string; value: string; onChange: (v: string) => void; placeholder: string; required?: boolean; hint?: string
}) {
    return (
        <div>
            <label className="block text-sm text-text-secondary mb-1.5">{label}{required && <span className="text-danger"> *</span>}</label>
            <input type={type} value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder}
                className="w-full px-4 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary placeholder-text-muted focus:border-primary outline-none transition-all text-sm" />
            {hint && <p className="text-xs text-danger mt-1">{hint}</p>}
        </div>
    );
}

function SelectField({ label, value, onChange, options }: {
    label: string; value: string; onChange: (v: string) => void; options: string[]
}) {
    return (
        <div>
            <label className="block text-sm text-text-secondary mb-1.5">{label}</label>
            <select value={value} onChange={e => onChange(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-bg-input border border-border text-text-primary focus:border-primary outline-none transition-all text-sm capitalize">
                {options.map(o => <option key={o} value={o}>{o.replace(/_/g, ' ')}</option>)}
            </select>
        </div>
    );
}

function ReviewRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-bg-input/50">
            <span className="text-sm text-text-secondary">{label}</span>
            <span className="text-sm font-medium capitalize">{value}</span>
        </div>
    );
}

function ListStep<T>({ title, subtitle, items, setItems, defaultItem, renderItem }: {
    title: string; subtitle: string; items: T[]; setItems: (v: T[]) => void;
    defaultItem: T; renderItem: (item: T, index: number) => JSX.Element;
}) {
    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-semibold">{title}</h3>
                    <p className="text-sm text-text-secondary">{subtitle}</p>
                </div>
                <button onClick={() => setItems([...items, { ...defaultItem }])}
                    className="px-3 py-1.5 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 text-sm flex items-center gap-1 transition-colors">
                    <Plus size={14} /> Add
                </button>
            </div>
            {items.length === 0 && <p className="text-sm text-text-muted text-center py-6">No items added yet. Click "Add" or skip this step.</p>}
            {items.map((item, i) => (
                <div key={i} className="relative p-4 rounded-xl bg-bg-input/30 border border-border space-y-3">
                    <button onClick={() => setItems(items.filter((_, j) => j !== i))}
                        className="absolute top-2 right-2 text-text-muted hover:text-danger transition-colors">
                        <Trash2 size={14} />
                    </button>
                    {renderItem(item, i)}
                </div>
            ))}
        </div>
    );
}

function updateList<T>(list: T[], setList: (v: T[]) => void, index: number, key: keyof T, value: any) {
    const updated = [...list];
    (updated[index] as any)[key] = value;
    setList(updated);
}
