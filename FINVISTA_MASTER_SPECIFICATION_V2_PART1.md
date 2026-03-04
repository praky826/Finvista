# 🚀 FINVISTA — COMPLETE ZERO-GAP MASTER SPECIFICATION (INDIA)

**Version**: 2.0 PRODUCTION-GRADE  
**Status**: READY FOR IMPLEMENTATION  
**Guarantee**: All gaps filled, all details specified, all formulas defined

This specification is **authoritative and complete**.
No deviation from structure is allowed.
No additional clarification needed.

---

# TABLE OF CONTENTS

1. ARCHITECTURE MODEL
2. COMPLETE BACKEND STRUCTURE
3. COMPLETE FRONTEND STRUCTURE
4. COMPLETE DATABASE SCHEMA WITH ALL COLUMNS
5. COMPLETE 4-ENGINE ARCHITECTURE WITH ALL FUNCTIONS & FORMULAS
6. COMPLETE REGISTRATION FLOW (10-STEP WIZARD WITH INPUTS)
7. COMPLETE INDIAN TAX IMPLEMENTATION
8. COMPLETE BUSINESS MODE SPECIFICATION
9. RECALCULATION TRIGGER RULES WITH DEPENDENCY MAP
10. COMPLETE ALERT ENGINE WITH THRESHOLDS & FORMULAS
11. COMPLETE API CONTRACTS (REQUEST/RESPONSE EXAMPLES)
12. COMPLETE SECURITY SPECIFICATION
13. MOBILE-FIRST PWA SPECIFICATION
14. CORRECTED 10-PHASE DEVELOPMENT ROADMAP
15. TAB-BY-TAB EDITABLE FIELDS SPECIFICATION

---

# ═══════════════════════════════════════════════════════════════════
# 🔴 SECTION 1: ARCHITECTURE MODEL (MANDATORY)
# ═══════════════════════════════════════════════════════════════════

## LAYERED MONOLITHIC ARCHITECTURE (6 LAYERS)

```
┌─────────────────────────────────────────────────────┐
│ 1. UI LAYER (React PWA)                              │
│    - User interface, forms, charts, gauges           │
│    - Mobile-first responsive design                  │
│    - State management (React Context)                │
└────────────────┬────────────────────────────────────┘
                 │ (HTTP requests with JWT token)
┌────────────────▼────────────────────────────────────┐
│ 2. APPLICATION LAYER (Routers / Controllers)        │
│    - REST endpoint handlers                          │
│    - Input validation (Pydantic schemas)             │
│    - Request/response marshaling                     │
│    - Delegate to services (NEVER call engines)       │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ 3. SERVICE LAYER (Business Transaction Logic)       │
│    - Database operations (CRUD)                      │
│    - Transaction management                         │
│    - ORCHESTRATE: DB update → Engine call → Return  │
│    - Coordinate cross-cutting concerns              │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ 4. ENGINE LAYER (Pure Financial Calculations)       │
│    - financial_calculations.py (pure functions)      │
│    - recalculation_engine.py (orchestrator)          │
│    - health_score_engine.py (scoring)                │
│    - alert_engine.py (rule evaluation)               │
│    - NO database access                              │
│    - NO I/O operations                               │
│    - Receives data → Returns computed values         │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ 5. DATA LAYER (PostgreSQL + SQLAlchemy)             │
│    - Database models (ORM objects)                   │
│    - Persistence and retrieval                       │
│    - No business logic                               │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ 6. SECURITY LAYER (Cross-Cutting)                   │
│    - Password hashing (bcrypt)                       │
│    - JWT token generation & verification            │
│    - CORS middleware                                 │
│    - Input sanitization                              │
│    - Rate limiting                                   │
└─────────────────────────────────────────────────────┘
```

## CRITICAL ARCHITECTURAL RULES

### ❌ FORBIDDEN VIOLATIONS (Will Cause System Failure)

1. **Router CANNOT call Engine directly**
   ```
   WRONG: router → financial_calculations() → return
   RIGHT: router → service → engine → return
   ```

2. **Router CANNOT update `derived_metrics` table**
   ```
   WRONG: router → db.update(derived_metrics)
   RIGHT: router → service → engine → service updates derived_metrics
   ```

3. **Router CANNOT insert alerts**
   ```
   WRONG: router → db.insert(alerts)
   RIGHT: router → service → alert_engine → service updates alerts
   ```

4. **Service CANNOT perform financial calculations**
   ```
   WRONG: service → calculate_net_worth()
   RIGHT: service → engine → calculate_net_worth()
   ```

5. **Engine CANNOT access database**
   ```
   WRONG: engine → session.query(...)
   RIGHT: engine receives data as parameters
   ```

6. **Models CANNOT contain business logic**
   ```
   WRONG: user.py → calculate_savings_ratio()
   RIGHT: user.py → column definitions only
   ```

7. **Frontend CANNOT compute financial formulas**
   ```
   WRONG: React component → calculate_dti()
   RIGHT: React calls API → backend calculates → returns result
   ```

### ✅ CORRECT FLOW PATTERN

```python
# CORRECT PATTERN (for any financial update)

# 1. Router receives request
@app.post("/accounts/update-income")
def update_income(request: UpdateIncomeRequest, db=Depends(get_db)):
    
    # 2. Router validates input (Pydantic)
    # 3. Router calls service (delegates business logic)
    result = account_service.update_income(
        user_id=request.user_id,
        new_income=request.new_income,
        db=db
    )
    return result

# 4. Service performs transaction
def update_income(user_id, new_income, db):
    # Update database
    user = db.query(User).filter(User.user_id == user_id).first()
    user.monthly_income = new_income
    db.commit()
    
    # Call recalculation engine
    recalculation_engine.recalculate_all_metrics(user_id, db)
    
    # Call alert engine
    alert_engine.evaluate_alerts(user_id, db)
    
    # Return response
    return {"success": True, "message": "Income updated and metrics recalculated"}

# 5. Engine receives raw data from service
def recalculate_all_metrics(user_id, db):
    # Fetch raw user data
    user_data = db.query(User).filter(...).first()
    bank_data = db.query(BankAccount).filter(...).all()
    loan_data = db.query(Loan).filter(...).all()
    
    # Call pure calculation functions
    net_worth = financial_calculations.calculate_net_worth(
        assets=user_data.total_assets,
        liabilities=user_data.total_liabilities
    )
    dti = financial_calculations.calculate_dti(
        monthly_emi=user_data.total_emi,
        monthly_income=user_data.monthly_income
    )
    
    # Store results in derived_metrics
    derived = DerivedMetrics(
        user_id=user_id,
        net_worth=net_worth,
        dti=dti,
        # ... all other metrics
    )
    db.add(derived)
    db.commit()
```

---

# ═══════════════════════════════════════════════════════════════════
# 🔴 SECTION 2: COMPLETE BACKEND STRUCTURE (STRICT)
# ═══════════════════════════════════════════════════════════════════

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                          ← FastAPI app initialization only
│   ├── config.py                        ← Environment variables & settings
│   ├── database.py                      ← SQLAlchemy engine, session, Base
│   │
│   ├── models/                          ← SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── bank_account.py
│   │   ├── loan.py
│   │   ├── credit_card.py
│   │   ├── investment.py
│   │   ├── goal.py
│   │   ├── tax.py
│   │   ├── derived_metrics.py
│   │   └── alert.py
│   │
│   ├── schemas/                         ← Pydantic validation models
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── account_schema.py
│   │   ├── loan_schema.py
│   │   ├── credit_schema.py
│   │   ├── investment_schema.py
│   │   ├── goal_schema.py
│   │   ├── tax_schema.py
│   │   ├── dashboard_schema.py
│   │   └── alert_schema.py
│   │
│   ├── routers/                         ← API endpoints (application layer)
│   │   ├── __init__.py
│   │   ├── auth.py                      ← POST /auth/register, /auth/login
│   │   ├── accounts.py                  ← CRUD: bank accounts, income
│   │   ├── loans.py                     ← CRUD: loans, EMI, credit cards
│   │   ├── investments.py               ← CRUD: FDs, stocks, etc.
│   │   ├── tax.py                       ← CRUD: tax regime, deductions
│   │   ├── goals.py                     ← CRUD: financial goals
│   │   ├── alerts.py                    ← GET: active alerts
│   │   └── dashboard.py                 ← GET: aggregated metrics
│   │
│   ├── services/                        ← Business logic & orchestration
│   │   ├── __init__.py
│   │   ├── account_service.py           ← Bank account operations
│   │   ├── loan_service.py              ← Loan & credit operations
│   │   ├── investment_service.py        ← Investment operations
│   │   ├── tax_service.py               ← Tax calculations
│   │   ├── goal_service.py              ← Goal operations
│   │   ├── dashboard_service.py         ← Dashboard aggregation
│   │   └── __init__.py
│   │
│   ├── engines/                         ← CORE CALCULATION ENGINES (pure logic)
│   │   ├── __init__.py
│   │   ├── financial_calculations.py    ← 30+ pure functions
│   │   ├── recalculation_engine.py      ← Orchestrates recalculation
│   │   ├── health_score_engine.py       ← Weighted health scoring
│   │   └── alert_engine.py              ← Rule-based alert evaluation
│   │
│   ├── security/                        ← Authentication & authorization
│   │   ├── __init__.py
│   │   ├── hashing.py                   ← bcrypt password hashing
│   │   ├── jwt_handler.py               ← JWT token operations
│   │   └── auth_dependencies.py         ← FastAPI Depends() functions
│   │
│   └── utils/                           ← Helper functions
│       ├── __init__.py
│       ├── formatter.py                 ← Currency formatting, rounding
│       └── date_utils.py                ← Date calculations
│
├── requirements.txt                     ← Python dependencies
├── .env.example                         ← Environment template
└── README.md
```

### KEY FILE PURPOSES

**main.py** (50-70 lines):
- Import FastAPI
- Create app instance
- Add CORS middleware
- Include all routers
- Define startup event (create tables)
- Start uvicorn

**config.py** (30-50 lines):
- Load .env variables
- Validate required variables
- Create Settings class
- Export settings instance

**database.py** (30-50 lines):
- Create SQLAlchemy engine
- Create SessionLocal
- Define Base = declarative_base()
- Define get_db() function

**models/** (8-10 files, 20-40 lines each):
- One file per table
- Column definitions
- Foreign key relationships
- __tablename__ attribute

**schemas/** (9 files, 30-60 lines each):
- Pydantic BaseModel classes
- Validation rules (constraints)
- Request/response shapes

**routers/** (8 files, 50-150 lines each):
- APIRouter instances
- Endpoint decorators (@app.get, @app.post)
- Use Depends(get_db)
- Call services
- Return schemas

**services/** (6 files, 100-300 lines each):
- Database queries
- Update operations
- Call engines
- Transaction management

**engines/** (4 files):
- **financial_calculations.py** (500+ lines): 30 pure functions
- **recalculation_engine.py** (100-150 lines): Main orchestrator
- **health_score_engine.py** (50-80 lines): Scoring formula
- **alert_engine.py** (100-150 lines): Alert rules

---

# ═══════════════════════════════════════════════════════════════════
# 🔴 SECTION 3: COMPLETE FRONTEND STRUCTURE (STRICT)
# ═══════════════════════════════════════════════════════════════════

```
frontend/
│
├── src/
│   ├── main.tsx                         ← React entry point
│   ├── App.tsx                          ← Root router setup
│   │
│   ├── pages/                           ← Each tab = one page
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx                ← Summary view (read-only)
│   │   ├── Accounts.tsx                 ← Bank accounts, income/expenses
│   │   ├── Loans.tsx                    ← Loans, EMI, credit cards
│   │   ├── Investments.tsx              ← FDs, stocks, property
│   │   ├── Tax.tsx                      ← Tax regime, deductions, calculation
│   │   ├── Goals.tsx                    ← Financial goals, tracking
│   │   └── Alerts.tsx                   ← Risk alerts, notifications
│   │
│   ├── components/
│   │   ├── cards/                       ← Card components (metric display)
│   │   │   ├── MetricCard.tsx           ← Generic metric with color & icon
│   │   │   ├── NetWorthCard.tsx
│   │   │   ├── HealthScoreCard.tsx
│   │   │   └── TaxEstimateCard.tsx
│   │   │
│   │   ├── charts/                      ← Chart components
│   │   │   ├── BarChart.tsx
│   │   │   ├── PieChart.tsx
│   │   │   ├── LineChart.tsx
│   │   │   └── GaugeChart.tsx
│   │   │
│   │   ├── gauges/                      ← Gauge visualizations
│   │   │   ├── HealthScoreGauge.tsx
│   │   │   ├── CreditGauge.tsx
│   │   │   └── RatioGauge.tsx
│   │   │
│   │   ├── forms/                       ← Input forms
│   │   │   ├── BankAccountForm.tsx
│   │   │   ├── LoanForm.tsx
│   │   │   ├── InvestmentForm.tsx
│   │   │   ├── GoalForm.tsx
│   │   │   └── TaxForm.tsx
│   │   │
│   │   ├── layout/
│   │   │   ├── MobileNav.tsx            ← Bottom navigation (mobile only)
│   │   │   ├── DesktopSidebar.tsx       ← Left sidebar (desktop only)
│   │   │   ├── Header.tsx               ← Top header
│   │   │   └── Layout.tsx               ← Responsive wrapper
│   │   │
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Modal.tsx
│   │       ├── Loading.tsx
│   │       └── ErrorBoundary.tsx
│   │
│   ├── services/
│   │   ├── api.ts                       ← Axios instance + interceptor
│   │   ├── authService.ts               ← Auth API calls
│   │   └── financeService.ts            ← All financial API calls
│   │
│   ├── context/
│   │   ├── AuthContext.tsx              ← Authentication state
│   │   └── FinanceContext.tsx           ← Financial data state (optional)
│   │
│   ├── hooks/
│   │   ├── useFetch.ts                  ← Generic data fetching
│   │   ├── useAuth.ts                   ← Auth context hook
│   │   └── useFinance.ts                ← Finance context hook
│   │
│   ├── utils/
│   │   ├── formatCurrency.ts            ← ₹ formatting
│   │   ├── formatPercent.ts             ← % formatting
│   │   ├── dateUtils.ts                 ← Date calculations
│   │   └── validation.ts                ← Input validation
│   │
│   ├── styles/
│   │   ├── globals.css                  ← Global Tailwind setup
│   │   ├── variables.css                ← CSS variables
│   │   └── responsive.css               ← Mobile-first media queries
│   │
│   └── pwa/
│       ├── manifest.json                ← PWA manifest
│       └── serviceWorker.ts             ← Service worker
│
├── public/
│   ├── icons/                           ← App icons (128x128, 192x192, 512x512)
│   └── index.html                       ← Base HTML
│
├── vite.config.ts                       ← Vite configuration
├── tsconfig.json                        ← TypeScript configuration
├── tailwind.config.js                   ← Tailwind CSS configuration
└── package.json
```

### RESPONSIVE DESIGN SPECIFICATION

**Mobile-First Breakpoints (Tailwind):**
```
sm: 360px–430px   (primary)
md: 768px
lg: 1024px
xl: 1280px
```

**Layout Rules:**
```
Mobile (sm):
- Single column
- Full-width forms
- Bottom navigation fixed to bottom
- Touch-friendly (48px+ tap targets)
- No sidebar

Tablet (md):
- Two columns possible
- Side sheet optional
- Bottom nav or top nav

Desktop (lg):
- Sidebar + content layout
- Left sidebar (fixed or collapsible)
- Top header with breadcrumbs
- Bottom nav hidden
- Multiple columns for dashboards
```

---

# ═══════════════════════════════════════════════════════════════════
# 🔴 SECTION 4: COMPLETE DATABASE SCHEMA
# ═══════════════════════════════════════════════════════════════════

All money columns use `NUMERIC(15,2)` (never FLOAT).

## TABLE 1: users

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('personal', 'business', 'both')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

## TABLE 2: bank_accounts

```sql
CREATE TABLE bank_accounts (
    account_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    bank_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(50) CHECK (account_type IN ('savings', 'current', 'salary')),
    balance NUMERIC(15,2) NOT NULL DEFAULT 0,
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('personal', 'business')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

## TABLE 3: loans

```sql
CREATE TABLE loans (
    loan_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    loan_name VARCHAR(100) NOT NULL,
    loan_type VARCHAR(50) CHECK (loan_type IN ('home', 'personal', 'business', 'education', 'other')),
    outstanding NUMERIC(15,2) NOT NULL DEFAULT 0,
    emi NUMERIC(15,2) NOT NULL DEFAULT 0,
    interest_rate NUMERIC(5,2),
    tenure_months INTEGER,
    start_date DATE,
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('personal', 'business')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

## TABLE 4: credit_cards

```sql
CREATE TABLE credit_cards (
    card_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    card_name VARCHAR(100) NOT NULL,
    credit_limit NUMERIC(15,2) NOT NULL DEFAULT 0,
    credit_used NUMERIC(15,2) NOT NULL DEFAULT 0,
    emi NUMERIC(15,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

## TABLE 5: investments

```sql
CREATE TABLE investments (
    investment_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('fd', 'stock', 'mf', 'gold', 'property')),
    value NUMERIC(15,2) NOT NULL DEFAULT 0,
    interest_rate NUMERIC(5,2),
    tenure_months INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

## TABLE 6: goals

```sql
CREATE TABLE goals (
    goal_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    goal_name VARCHAR(150) NOT NULL,
    target NUMERIC(15,2) NOT NULL,
    deadline DATE NOT NULL,
    current_savings NUMERIC(15,2) NOT NULL DEFAULT 0,
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('personal', 'business')),
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

## TABLE 7: tax

```sql
CREATE TABLE tax (
    tax_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    -- Personal Income Tax
    annual_income NUMERIC(15,2),
    monthly_income NUMERIC(15,2),
    deductions_80c NUMERIC(15,2) DEFAULT 0,
    deductions_80d NUMERIC(15,2) DEFAULT 0,
    deductions_80tta NUMERIC(15,2) DEFAULT 0,
    other_deductions NUMERIC(15,2) DEFAULT 0,
    regime VARCHAR(20) CHECK (regime IN ('old', 'new')),
    -- Business Tax
    business_revenue NUMERIC(15,2),
    business_expenses NUMERIC(15,2),
    cogs NUMERIC(15,2),
    business_deductions NUMERIC(15,2) DEFAULT 0,
    corporate_tax_percent NUMERIC(5,2) DEFAULT 0,
    -- Common
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

## TABLE 8: derived_metrics (CRITICAL - PRE-CALCULATED)

```sql
CREATE TABLE derived_metrics (
    metric_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- PERSONAL METRICS
    net_worth NUMERIC(15,2),
    savings_ratio NUMERIC(6,2),                    -- %
    dti NUMERIC(6,2),                              -- % (debt-to-income)
    emergency_fund NUMERIC(6,2),                   -- months
    credit_utilization NUMERIC(6,2),               -- %
    liquid_asset_percentage NUMERIC(6,2),          -- %
    loan_to_asset NUMERIC(6,2),                    -- %
    tax_estimate NUMERIC(15,2),
    effective_tax_rate NUMERIC(6,2),               -- %
    credit_score_simulation INTEGER,               -- 600-900
    health_score NUMERIC(6,2),                     -- 0-100
    
    -- BUSINESS METRICS
    business_net_worth NUMERIC(15,2),
    net_profit NUMERIC(15,2),
    working_capital NUMERIC(15,2),
    cash_flow NUMERIC(15,2),
    debt_ratio NUMERIC(6,2),                       -- %
    liquidity_ratio NUMERIC(6,2),
    gross_profit_margin NUMERIC(6,2),              -- %
    net_profit_margin NUMERIC(6,2),                -- %
    emi_burden_ratio NUMERIC(6,2),                 -- %
    
    -- COMMON
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id)
);
```

## TABLE 9: alerts

```sql
CREATE TABLE alerts (
    alert_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('info', 'warning', 'critical')),
    message TEXT NOT NULL,
    metric_value NUMERIC(15,2),                    -- Current value that triggered alert
    threshold NUMERIC(15,2),                       -- Threshold that was crossed
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'ignored')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    
    -- Prevent duplicates: unique alert per user per type
    UNIQUE(user_id, alert_type, status),
    
    INDEX idx_user_id (user_id),
    INDEX idx_severity (severity)
);
```

---

# ═══════════════════════════════════════════════════════════════════
# 🔴 SECTION 5: COMPLETE 4-ENGINE ARCHITECTURE WITH ALL FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

## ENGINE 1: financial_calculations.py

**Purpose**: Pure mathematical functions. NO database access. NO I/O.

### PERSONAL FINANCE FUNCTIONS

```python
# NET WORTH & ASSETS
def calculate_net_worth(
    total_assets: Decimal,
    total_liabilities: Decimal
) -> Decimal:
    """
    Net Worth = Total Assets - Total Liabilities
    
    Total Assets = Bank Balance + Cash + FD + Investments + Property
    Total Liabilities = Loan Outstanding + Credit Card Dues
    """
    return total_assets - total_liabilities

def calculate_liquid_asset_percentage(
    liquid_assets: Decimal,
    total_assets: Decimal
) -> Decimal:
    """
    Liquid Assets % = Liquid Assets / Total Assets × 100
    
    Liquid Assets = Bank + Cash + FD (only within 1 month maturity)
    Total Assets = All assets
    """
    if total_assets == 0:
        return Decimal(0)
    return (liquid_assets / total_assets) * 100

# INCOME & SAVINGS
def calculate_savings_ratio(
    monthly_income: Decimal,
    monthly_expenses: Decimal
) -> Decimal:
    """
    Savings Ratio = (Income - Expenses) / Income × 100
    
    Interpretation:
    - >30% = Excellent
    - 20-30% = Good
    - 10-20% = Average
    - <10% = Poor
    """
    if monthly_income == 0:
        return Decimal(0)
    return ((monthly_income - monthly_expenses) / monthly_income) * 100

def calculate_emergency_fund(
    liquid_savings: Decimal,
    monthly_expenses: Decimal
) -> Decimal:
    """
    Emergency Fund Coverage (months) = Liquid Savings / Monthly Expenses
    
    Interpretation:
    - <3 months = CRITICAL (alert)
    - 3-6 months = At Risk
    - 6+ months = Healthy
    """
    if monthly_expenses == 0:
        return Decimal(0)
    return liquid_savings / monthly_expenses

# DEBT METRICS
def calculate_dti(
    total_monthly_emi: Decimal,
    monthly_income: Decimal
) -> Decimal:
    """
    Debt-to-Income Ratio = Total Monthly EMI / Monthly Income × 100
    
    Interpretation:
    - <30% = Healthy
    - 30-40% = Caution
    - >40% = CRITICAL (alert)
    """
    if monthly_income == 0:
        return Decimal(0)
    return (total_monthly_emi / monthly_income) * 100

def calculate_emi_burden_ratio(
    total_monthly_emi: Decimal,
    monthly_income: Decimal
) -> Decimal:
    """
    EMI Burden = Total EMI / Monthly Income × 100
    Same as DTI but named for clarity in EMI context
    """
    return calculate_dti(total_monthly_emi, monthly_income)

def calculate_loan_to_asset(
    total_loan_outstanding: Decimal,
    total_assets: Decimal
) -> Decimal:
    """
    Loan-to-Asset Ratio = Total Loan Outstanding / Total Assets
    
    Interpretation:
    - <0.3 = Good (30% leveraged)
    - 0.3-0.6 = Moderate (30-60%)
    - >0.6 = High risk (>60%)
    """
    if total_assets == 0:
        return Decimal(0)
    return total_loan_outstanding / total_assets

# CREDIT METRICS
def calculate_credit_utilization(
    credit_used: Decimal,
    credit_limit: Decimal
) -> Decimal:
    """
    Credit Utilization = Credit Used / Credit Limit × 100
    
    Interpretation:
    - <30% = Good
    - 30-50% = Caution (alert at 30%)
    - >50% = High risk
    """
    if credit_limit == 0:
        return Decimal(0)
    return (credit_used / credit_limit) * 100

def calculate_credit_score_simulation(
    credit_utilization: Decimal,
    dti: Decimal,
    payment_history_score: Decimal = 100  # 0-100, default good
) -> int:
    """
    Simulated Credit Score = Base 750
    - Deduct for high credit utilization (>30%)
    - Deduct for high DTI (>40%)
    - Bonus for low EMI burden
    
    Formula:
    Score = 750
            - (credit_util > 30 ? 50 : 0)
            - (dti > 40 ? 100 : 0)
            + (payment_history_score)
    
    Range: 600-850 (rough simulation)
    """
    score = 750
    
    if credit_utilization > 30:
        score -= min(50, int(credit_utilization / 2))
    
    if dti > 40:
        score -= min(100, int((dti - 40) * 2))
    
    score += int((payment_history_score - 100) / 2)  # -50 to +50
    
    return max(600, min(900, score))  # Clamp to 600-900

# INVESTMENT & FD METRICS
def calculate_fd_maturity(
    principal: Decimal,
    annual_interest_rate: Decimal,
    tenure_years: Decimal
) -> Decimal:
    """
    FD Maturity = Principal × (1 + (Rate/100))^Years
    
    Assumes annual compounding (simplification)
    """
    rate = annual_interest_rate / 100
    return principal * ((1 + rate) ** tenure_years)

def calculate_diversification_ratio(
    asset_value: Decimal,
    total_investment: Decimal
) -> Decimal:
    """
    Diversification % for one asset = Asset Value / Total Investment × 100
    
    Called for each asset type separately.
    Interpretation:
    - Ideal: No single asset >25%
    - Safe: No single asset >40%
    - Risk: Any asset >50% is concentration risk
    """
    if total_investment == 0:
        return Decimal(0)
    return (asset_value / total_investment) * 100

def calculate_expected_annual_return(
    investment_value: Decimal,
    expected_return_rate: Decimal  # User's estimated % return
) -> Decimal:
    """
    Expected Annual Return = Investment Value × (Expected Rate / 100)
    
    User provides expected return rate (e.g., 7% for FD, 12% for equity)
    """
    return investment_value * (expected_return_rate / 100)

# TAX FUNCTIONS (Personal)

def calculate_tax_old_regime(
    annual_income: Decimal,
    deductions_80c: Decimal = 0,
    deductions_80d: Decimal = 0,
    deductions_80tta: Decimal = 0,
    other_deductions: Decimal = 0
) -> dict:
    """
    OLD REGIME (Pre-2023) - Still available for FY 2023-24
    
    Calculation:
    1. Gross Income = Annual Income
    2. Standard Deduction = ₹50,000
    3. Total Deductions = 80C (₹1.5L max) + 80D + 80TTA + others
    4. Taxable Income = Gross - Standard Deduction - Deductions
    5. Apply slab logic
    6. Add 4% health education cess
    
    SLAB LOGIC (FY 2023-24):
    - ₹0 to ₹2.5L: 0%
    - ₹2.5L to ₹5L: 5%
    - ₹5L to ₹10L: 10%
    - ₹10L to ₹15L: 20%
    - ₹15L and above: 30%
    
    DEDUCTIONS:
    - Section 80C: LIC, PPF, ELSS, etc. (up to ₹1.5L)
    - Section 80D: Medical insurance (up to ₹25,000 individual)
    - Section 80TTA: Savings account interest (up to ₹10,000)
    """
    gross_income = annual_income
    standard_deduction = Decimal(50000)
    
    # Cap deductions
    deductions_80c_capped = min(deductions_80c, Decimal(150000))
    deductions_80d_capped = min(deductions_80d, Decimal(25000))
    deductions_80tta_capped = min(deductions_80tta, Decimal(10000))
    
    total_deductions = (
        deductions_80c_capped +
        deductions_80d_capped +
        deductions_80tta_capped +
        other_deductions
    )
    
    taxable_income = gross_income - standard_deduction - total_deductions
    taxable_income = max(taxable_income, Decimal(0))  # Cannot be negative
    
    # Calculate tax on slabs
    if taxable_income <= 250000:
        tax_before_cess = Decimal(0)
    elif taxable_income <= 500000:
        tax_before_cess = (taxable_income - 250000) * Decimal('0.05')
    elif taxable_income <= 1000000:
        tax_before_cess = (250000 * Decimal('0.05')) + (taxable_income - 500000) * Decimal('0.10')
    elif taxable_income <= 1500000:
        tax_before_cess = (
            (250000 * Decimal('0.05')) +
            (500000 * Decimal('0.10')) +
            (taxable_income - 1000000) * Decimal('0.20')
        )
    else:
        tax_before_cess = (
            (250000 * Decimal('0.05')) +
            (500000 * Decimal('0.10')) +
            (500000 * Decimal('0.20')) +
            (taxable_income - 1500000) * Decimal('0.30')
        )
    
    # Add 4% cess
    cess = tax_before_cess * Decimal('0.04')
    total_tax = tax_before_cess + cess
    
    # Section 87A Rebate: NOT applicable in old regime above ₹5L
    
    effective_tax_rate = (total_tax / gross_income * 100) if gross_income > 0 else Decimal(0)
    
    return {
        "gross_income": gross_income,
        "standard_deduction": standard_deduction,
        "total_deductions": total_deductions,
        "taxable_income": taxable_income,
        "tax_before_cess": tax_before_cess,
        "cess": cess,
        "total_tax": total_tax,
        "effective_tax_rate": effective_tax_rate,
        "net_income": gross_income - total_tax
    }

def calculate_tax_new_regime(
    annual_income: Decimal,
    standard_deduction: Decimal = 50000
) -> dict:
    """
    NEW REGIME (FY 2023-24 onwards)
    
    Features:
    - Standard deduction only (₹50,000)
    - NO Section 80C, 80D, 80TTA deductions
    - Simpler slab logic
    - Section 87A rebate for income ≤ ₹5L
    
    SLAB LOGIC (FY 2023-24):
    - ₹0 to ₹2.5L: 0%
    - ₹2.5L to ₹5L: 5%
    - ₹5L to ₹7.5L: 10%
    - ₹7.5L to ₹10L: 15%
    - ₹10L to ₹12.5L: 20%
    - ₹12.5L to ₹15L: 25%
    - ₹15L and above: 30%
    
    SECTION 87A REBATE:
    If income ≤ ₹5L: Tax = ₹0 (100% rebate)
    """
    gross_income = annual_income
    taxable_income = gross_income - standard_deduction
    taxable_income = max(taxable_income, Decimal(0))
    
    # Calculate tax on new regime slabs
    if taxable_income <= 250000:
        tax_before_cess = Decimal(0)
    elif taxable_income <= 500000:
        tax_before_cess = (taxable_income - 250000) * Decimal('0.05')
    elif taxable_income <= 750000:
        tax_before_cess = (250000 * Decimal('0.05')) + (taxable_income - 500000) * Decimal('0.10')
    elif taxable_income <= 1000000:
        tax_before_cess = (
            (250000 * Decimal('0.05')) +
            (250000 * Decimal('0.10')) +
            (taxable_income - 750000) * Decimal('0.15')
        )
    elif taxable_income <= 1250000:
        tax_before_cess = (
            (250000 * Decimal('0.05')) +
            (250000 * Decimal('0.10')) +
            (250000 * Decimal('0.15')) +
            (taxable_income - 1000000) * Decimal('0.20')
        )
    elif taxable_income <= 1500000:
        tax_before_cess = (
            (250000 * Decimal('0.05')) +
            (250000 * Decimal('0.10')) +
            (250000 * Decimal('0.15')) +
            (250000 * Decimal('0.20')) +
            (taxable_income - 1250000) * Decimal('0.25')
        )
    else:
        tax_before_cess = (
            (250000 * Decimal('0.05')) +
            (250000 * Decimal('0.10')) +
            (250000 * Decimal('0.15')) +
            (250000 * Decimal('0.20')) +
            (250000 * Decimal('0.25')) +
            (taxable_income - 1500000) * Decimal('0.30')
        )
    
    # Add 4% cess
    cess = tax_before_cess * Decimal('0.04')
    total_tax_before_rebate = tax_before_cess + cess
    
    # Section 87A Rebate: If gross income ≤ ₹5L, tax = ₹0
    if gross_income <= 500000:
        total_tax = Decimal(0)
        rebate = total_tax_before_rebate
    else:
        total_tax = total_tax_before_rebate
        rebate = Decimal(0)
    
    effective_tax_rate = (total_tax / gross_income * 100) if gross_income > 0 else Decimal(0)
    
    return {
        "gross_income": gross_income,
        "standard_deduction": standard_deduction,
        "taxable_income": taxable_income,
        "tax_before_cess": tax_before_cess,
        "cess": cess,
        "total_tax_before_rebate": total_tax_before_rebate,
        "section_87a_rebate": rebate,
        "total_tax": total_tax,
        "effective_tax_rate": effective_tax_rate,
        "net_income": gross_income - total_tax
    }

# GOAL TRACKING
def calculate_goal_feasibility(
    target_amount: Decimal,
    current_savings: Decimal,
    available_monthly_savings: Decimal,  # Surplus income after expenses
    months_remaining: int
) -> dict:
    """
    Goal Feasibility Calculation (Personal)
    
    Required Monthly Saving = (Target - Current Savings) / Months Remaining
    Feasibility Ratio = Available Monthly Savings / Required Monthly Saving
    
    Interpretation:
    - ≥1.0 = On Track (green)
    - 0.5-1.0 = Behind (yellow)
    - <0.5 = Far Behind (red)
    """
    if months_remaining <= 0:
        return {
            "status": "overdue",
            "feasibility_ratio": Decimal(0),
            "required_monthly": Decimal(0)
        }
    
    remaining_needed = target_amount - current_savings
    required_monthly = remaining_needed / months_remaining if remaining_needed > 0 else Decimal(0)
    
    if required_monthly == 0:
        feasibility_ratio = Decimal(1)  # Already saved
    else:
        feasibility_ratio = available_monthly_savings / required_monthly
    
    if feasibility_ratio >= 1:
        status = "on_track"
    elif feasibility_ratio >= 0.5:
        status = "behind"
    else:
        status = "far_behind"
    
    return {
        "target_amount": target_amount,
        "current_savings": current_savings,
        "required_monthly": required_monthly,
        "available_monthly": available_monthly_savings,
        "feasibility_ratio": feasibility_ratio,
        "status": status,
        "months_remaining": months_remaining,
        "total_needed": remaining_needed
    }
```

### BUSINESS FINANCE FUNCTIONS

```python
def calculate_net_profit(
    revenue: Decimal,
    operating_expenses: Decimal,
    cogs: Decimal = 0,  # Cost of Goods Sold
    interest_paid: Decimal = 0,  # EMI interest
    tax_paid: Decimal = 0
) -> Decimal:
    """
    Net Profit = Revenue - COGS - Operating Expenses - Interest - Taxes
    
    For service business: COGS = 0
    For product business: Include COGS
    """
    return revenue - cogs - operating_expenses - interest_paid - tax_paid

def calculate_working_capital(
    current_assets: Decimal,  # Bank + Inventory + Receivables
    current_liabilities: Decimal  # Payables + Short-term debt
) -> Decimal:
    """
    Working Capital = Current Assets - Current Liabilities
    
    Interpretation:
    - Positive and growing = Healthy
    - Negative = Liquidity crisis
    - Alert if < 1 month of expenses
    """
    return current_assets - current_liabilities

def calculate_liquidity_ratio(
    current_assets: Decimal,
    current_liabilities: Decimal
) -> Decimal:
    """
    Liquidity Ratio = Current Assets / Current Liabilities
    
    Interpretation:
    - >1.5 = Excellent liquidity
    - 1.0-1.5 = Healthy
    - <1.0 = CRITICAL (alert) - can't cover short-term obligations
    """
    if current_liabilities == 0:
        return Decimal(0)
    return current_assets / current_liabilities

def calculate_debt_ratio(
    total_debt: Decimal,
    total_assets: Decimal
) -> Decimal:
    """
    Debt Ratio = Total Debt / Total Assets × 100
    
    Interpretation:
    - <40% = Conservative
    - 40-60% = Moderate
    - >60% = CRITICAL (alert) - over-leveraged
    """
    if total_assets == 0:
        return Decimal(0)
    return (total_debt / total_assets) * 100

def calculate_profit_margins(
    revenue: Decimal,
    cogs: Decimal,
    net_profit: Decimal
) -> dict:
    """
    Gross Profit Margin = (Revenue - COGS) / Revenue × 100
    Net Profit Margin = Net Profit / Revenue × 100
    
    Interpretation:
    Gross Margin:
    - >50% = Excellent pricing
    - 30-50% = Good
    - <30% = Price/cost pressure
    
    Net Margin:
    - >20% = Excellent profitability
    - 10-20% = Good
    - 5-10% = Average
    - <5% = Low profitability (alert)
    """
    if revenue == 0:
        return {
            "gross_margin": Decimal(0),
            "net_margin": Decimal(0)
        }
    
    gross_profit = revenue - cogs
    gross_margin = (gross_profit / revenue) * 100
    net_margin = (net_profit / revenue) * 100
    
    return {
        "gross_margin": gross_margin,
        "net_margin": net_margin,
        "gross_profit": gross_profit
    }

def calculate_business_goal_feasibility(
    target_amount: Decimal,
    current_savings: Decimal,
    monthly_net_profit: Decimal,
    months_remaining: int
) -> dict:
    """
    Business Goal Feasibility (Different from personal)
    
    Required Monthly Allocation = (Target - Current) / Months Remaining
    Feasibility Ratio = Monthly Net Profit / Required Monthly Allocation
    
    Interpretation:
    - ≥1.0 = Can allocate without impacting operations
    - 0.5-1.0 = Can allocate but tight
    - <0.5 = Unrealistic given profit
    """
    if months_remaining <= 0:
        return {
            "status": "overdue",
            "feasibility_ratio": Decimal(0),
            "required_monthly": Decimal(0)
        }
    
    remaining_needed = target_amount - current_savings
    required_monthly = remaining_needed / months_remaining if remaining_needed > 0 else Decimal(0)
    
    # For business: Compare with net profit, not just savings
    if required_monthly == 0:
        feasibility_ratio = Decimal(1)
    else:
        # Can we allocate this from profit without hurting operations?
        feasibility_ratio = monthly_net_profit / required_monthly
    
    if feasibility_ratio >= 1:
        status = "feasible"
    elif feasibility_ratio >= 0.5:
        status = "tight"
    else:
        status = "unrealistic"
    
    return {
        "target_amount": target_amount,
        "current_savings": current_savings,
        "required_monthly": required_monthly,
        "monthly_net_profit": monthly_net_profit,
        "feasibility_ratio": feasibility_ratio,
        "status": status,
        "months_remaining": months_remaining,
        "total_needed": remaining_needed
    }

def calculate_business_tax(
    revenue: Decimal,
    business_expenses: Decimal,
    cogs: Decimal = 0,
    business_deductions: Decimal = 0,
    corporate_tax_rate: Decimal = Decimal('30')  # Default 30% for companies
) -> dict:
    """
    Business Tax Calculation
    
    Taxable Profit = Revenue - COGS - Expenses - Deductions
    Tax = Taxable Profit × Corporate Tax Rate
    Quarterly Advance Tax = Annual Tax / 4
    
    Note: GST is separate (user handles invoicing)
    """
    taxable_profit = revenue - cogs - business_expenses - business_deductions
    taxable_profit = max(taxable_profit, Decimal(0))  # Cannot be negative
    
    annual_tax = taxable_profit * (corporate_tax_rate / 100)
    quarterly_advance_tax = annual_tax / 4
    
    effective_tax_rate = (annual_tax / revenue * 100) if revenue > 0 else Decimal(0)
    
    return {
        "revenue": revenue,
        "expenses": business_expenses,
        "cogs": cogs,
        "deductions": business_deductions,
        "taxable_profit": taxable_profit,
        "corporate_tax_rate": corporate_tax_rate,
        "annual_tax": annual_tax,
        "quarterly_advance_tax": quarterly_advance_tax,
        "effective_tax_rate": effective_tax_rate,
        "net_profit_after_tax": taxable_profit - annual_tax
    }
```

---

## ENGINE 2: recalculation_engine.py

**Purpose**: Orchestrates recalculation. Fetches data → Calls calculations → Updates derived_metrics → Triggers alerts.

```python
def recalculate_all_metrics(user_id: int, db: Session):
    """
    MASTER ORCHESTRATOR
    
    Called whenever ANY core financial data updates.
    Recalculates ALL dependent metrics in correct order.
    Updates derived_metrics table.
    """
    
    # STEP 1: FETCH ALL RAW USER DATA
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"error": "User not found"}
    
    bank_accounts = db.query(BankAccount).filter(BankAccount.user_id == user_id).all()
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    credit_cards = db.query(CreditCard).filter(CreditCard.user_id == user_id).all()
    investments = db.query(Investment).filter(Investment.user_id == user_id).all()
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    tax_info = db.query(Tax).filter(Tax.user_id == user_id).first()
    
    # STEP 2: AGGREGATE TOTALS
    total_bank_balance = sum(acc.balance for acc in bank_accounts) if bank_accounts else Decimal(0)
    total_cash = Decimal(0)  # Usually 0 unless user manually adds
    total_fd = sum(inv.value for inv in investments if inv.type == 'fd') if investments else Decimal(0)
    total_investments = sum(inv.value for inv in investments) if investments else Decimal(0)
    total_property = Decimal(0)  # User-estimated property value (not in investments table)
    
    total_assets = total_bank_balance + total_cash + total_fd + total_investments + total_property
    
    total_loan_outstanding = sum(loan.outstanding for loan in loans) if loans else Decimal(0)
    total_credit_used = sum(cc.credit_used for cc in credit_cards) if credit_cards else Decimal(0)
    total_liabilities = total_loan_outstanding + total_credit_used
    
    total_emi = sum(loan.emi for loan in loans) if loans else Decimal(0)
    total_emi += sum(cc.emi for cc in credit_cards) if credit_cards else Decimal(0)
    
    total_credit_limit = sum(cc.credit_limit for cc in credit_cards) if credit_cards else Decimal(0)
    
    # STEP 3: CALL FINANCIAL CALCULATION FUNCTIONS
    
    # Basic metrics
    net_worth = financial_calculations.calculate_net_worth(total_assets, total_liabilities)
    savings_ratio = financial_calculations.calculate_savings_ratio(user.monthly_income, user.monthly_expenses)
    dti = financial_calculations.calculate_dti(total_emi, user.monthly_income)
    emergency_fund = financial_calculations.calculate_emergency_fund(total_bank_balance, user.monthly_expenses)
    credit_utilization = financial_calculations.calculate_credit_utilization(total_credit_used, total_credit_limit)
    liquid_asset_percentage = financial_calculations.calculate_liquid_asset_percentage(total_bank_balance, total_assets)
    loan_to_asset = financial_calculations.calculate_loan_to_asset(total_loan_outstanding, total_assets)
    
    # Credit score
    credit_score = financial_calculations.calculate_credit_score_simulation(credit_utilization, dti)
    
    # Tax (use selected regime)
    if tax_info.regime == 'old':
        tax_calc = financial_calculations.calculate_tax_old_regime(
            annual_income=tax_info.annual_income or (user.monthly_income * 12),
            deductions_80c=tax_info.deductions_80c or 0,
            deductions_80d=tax_info.deductions_80d or 0,
            deductions_80tta=tax_info.deductions_80tta or 0,
            other_deductions=tax_info.other_deductions or 0
        )
    else:
        tax_calc = financial_calculations.calculate_tax_new_regime(
            annual_income=tax_info.annual_income or (user.monthly_income * 12)
        )
    
    tax_estimate = tax_calc['total_tax']
    effective_tax_rate = tax_calc['effective_tax_rate']
    
    # Diversification
    diversification = {}  # Calculate for each investment type
    if total_investments > 0:
        for inv in investments:
            diversification[inv.type] = financial_calculations.calculate_diversification_ratio(inv.value, total_investments)
    
    # Expected return
    expected_return = Decimal(0)
    for inv in investments:
        if inv.interest_rate:
            expected_return += financial_calculations.calculate_expected_annual_return(inv.value, inv.interest_rate)
    
    # STEP 4: CALL HEALTH SCORE ENGINE
    health_score = health_score_engine.calculate_health_score(
        savings_ratio=savings_ratio,
        dti=dti,
        emergency_fund=emergency_fund,
        credit_utilization=credit_utilization,
        diversification_avg=sum(diversification.values()) / len(diversification) if diversification else Decimal(0)
    )
    
    # STEP 5: CALCULATE BUSINESS METRICS (if business mode)
    business_metrics = {}
    if user.account_type in ('business', 'both'):
        if tax_info.business_revenue:
            net_profit = financial_calculations.calculate_net_profit(
                revenue=tax_info.business_revenue,
                operating_expenses=tax_info.business_expenses or 0,
                cogs=tax_info.cogs or 0
            )
            business_metrics['net_profit'] = net_profit
            
            working_capital = financial_calculations.calculate_working_capital(
                current_assets=total_bank_balance,
                current_liabilities=total_credit_used
            )
            business_metrics['working_capital'] = working_capital
            
            liquidity_ratio = financial_calculations.calculate_liquidity_ratio(
                current_assets=total_bank_balance,
                current_liabilities=total_credit_used or 1  # Avoid division by zero
            )
            business_metrics['liquidity_ratio'] = liquidity_ratio
            
            debt_ratio = financial_calculations.calculate_debt_ratio(total_loan_outstanding, total_assets)
            business_metrics['debt_ratio'] = debt_ratio
            
            margins = financial_calculations.calculate_profit_margins(
                revenue=tax_info.business_revenue,
                cogs=tax_info.cogs or 0,
                net_profit=net_profit
            )
            business_metrics['gross_profit_margin'] = margins['gross_margin']
            business_metrics['net_profit_margin'] = margins['net_margin']
            
            business_emi_burden = financial_calculations.calculate_emi_burden_ratio(total_emi, tax_info.monthly_business_revenue or Decimal(1))
            business_metrics['emi_burden_ratio'] = business_emi_burden
    
    # STEP 6: UPDATE derived_metrics TABLE
    derived = db.query(DerivedMetrics).filter(DerivedMetrics.user_id == user_id).first()
    
    if not derived:
        derived = DerivedMetrics(user_id=user_id)
        db.add(derived)
    
    # Personal metrics
    derived.net_worth = net_worth
    derived.savings_ratio = savings_ratio
    derived.dti = dti
    derived.emergency_fund = emergency_fund
    derived.credit_utilization = credit_utilization
    derived.liquid_asset_percentage = liquid_asset_percentage
    derived.loan_to_asset = loan_to_asset
    derived.tax_estimate = tax_estimate
    derived.effective_tax_rate = effective_tax_rate
    derived.credit_score_simulation = credit_score
    derived.health_score = health_score
    
    # Business metrics
    if business_metrics:
        derived.net_profit = business_metrics.get('net_profit')
        derived.working_capital = business_metrics.get('working_capital')
        derived.liquidity_ratio = business_metrics.get('liquidity_ratio')
        derived.debt_ratio = business_metrics.get('debt_ratio')
        derived.gross_profit_margin = business_metrics.get('gross_profit_margin')
        derived.net_profit_margin = business_metrics.get('net_profit_margin')
        derived.emi_burden_ratio = business_metrics.get('emi_burden_ratio')
    
    derived.updated_at = datetime.now()
    db.commit()
    
    # STEP 7: TRIGGER ALERT ENGINE
    alert_engine.evaluate_alerts(user_id, derived, db)
    
    return {
        "success": True,
        "message": "All metrics recalculated",
        "health_score": float(health_score)
    }
```

---

## ENGINE 3: health_score_engine.py

```python
def calculate_health_score(
    savings_ratio: Decimal,
    dti: Decimal,
    emergency_fund: Decimal,
    credit_utilization: Decimal,
    diversification_avg: Decimal
) -> Decimal:
    """
    HEALTH SCORE ALGORITHM
    
    Normalized weighted score (0-100).
    
    Weights:
    - Savings Ratio: 20% (how much you save)
    - DTI: 20% (debt burden)
    - Emergency Fund: 20% (safety net)
    - Credit Utilization: 20% (credit discipline)
    - Diversification: 20% (investment spread)
    
    Score Interpretation:
    - 80-100: Excellent
    - 60-80: Good
    - 40-60: Average
    - 20-40: Poor
    - 0-20: Critical
    """
    
    # NORMALIZE each metric to 0-100 scale
    
    # Savings Ratio: Ideal is 30%+
    # 30%+ = 100, 0% = 0
    normalized_savings = min((savings_ratio / 30) * 100, Decimal(100))
    
    # DTI: Ideal is <30%
    # 0% = 100, 40%+ = 0
    dti_inverted = max(Decimal(100) - (dti * Decimal('2.5')), Decimal(0))  # 40% dti = 0 score
    normalized_dti = min(dti_inverted, Decimal(100))
    
    # Emergency Fund: Ideal is 6+ months
    # 6+ = 100, 0 = 0
    normalized_emergency = min((emergency_fund / 6) * 100, Decimal(100))
    
    # Credit Utilization: Ideal is <30%
    # 0% = 100, 100% = 0
    credit_inverted = max(Decimal(100) - credit_utilization, Decimal(0))
    normalized_credit = credit_inverted
    
    # Diversification: Ideal is no asset >25%
    # If avg is 25%, score is high; if >50%, score is low
    if diversification_avg <= Decimal(25):
        normalized_diversification = Decimal(100)
    elif diversification_avg <= Decimal(50):
        normalized_diversification = max(Decimal(100) - ((diversification_avg - 25) * 2), Decimal(0))
    else:
        normalized_diversification = Decimal(0)
    
    # APPLY WEIGHTS
    health_score = (
        (normalized_savings * Decimal('0.20')) +
        (normalized_dti * Decimal('0.20')) +
        (normalized_emergency * Decimal('0.20')) +
        (normalized_credit * Decimal('0.20')) +
        (normalized_diversification * Decimal('0.20'))
    )
    
    # Round to 2 decimals
    return health_score.quantize(Decimal('0.01'))
```

---

## ENGINE 4: alert_engine.py

```python
def evaluate_alerts(user_id: int, metrics: DerivedMetrics, db: Session):
    """
    ALERT EVALUATION ENGINE
    
    Checks all conditions and creates/updates/resolves alerts.
    Never creates duplicates.
    """
    
    alerts_to_create = []
    
    # ========== PERSONAL ALERTS ==========
    
    # ALERT 1: High DTI (>40%)
    if metrics.dti and metrics.dti > 40:
        alerts_to_create.append({
            "alert_type": "HIGH_DTI",
            "severity": "critical",
            "message": f"Your debt-to-income ratio is {metrics.dti:.1f}%, indicating high financial stress. Consider reducing EMI load.",
            "metric_value": metrics.dti,
            "threshold": 40
        })
    
    # ALERT 2: High Credit Utilization (>30%)
    if metrics.credit_utilization and metrics.credit_utilization > 30:
        severity = "critical" if metrics.credit_utilization > 50 else "warning"
        alerts_to_create.append({
            "alert_type": "HIGH_CREDIT_UTILIZATION",
            "severity": severity,
            "message": f"Credit utilization is {metrics.credit_utilization:.1f}%. Keep it below 30% for better credit score.",
            "metric_value": metrics.credit_utilization,
            "threshold": 30
        })
    
    # ALERT 3: Low Emergency Fund (<3 months)
    if metrics.emergency_fund and metrics.emergency_fund < 3:
        severity = "critical" if metrics.emergency_fund < 1 else "warning"
        alerts_to_create.append({
            "alert_type": "LOW_EMERGENCY_FUND",
            "severity": severity,
            "message": f"Emergency fund covers only {metrics.emergency_fund:.1f} months of expenses. Target: 6 months.",
            "metric_value": metrics.emergency_fund,
            "threshold": 3
        })
    
    # ALERT 4: Goal Feasibility (<1.0)
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    for goal in goals:
        months_remaining = calculate_months_remaining(goal.deadline)
        if months_remaining > 0:
            goal_feasibility = financial_calculations.calculate_goal_feasibility(
                target_amount=goal.target,
                current_savings=goal.current_savings,
                available_monthly_savings=...,  # Calculate from metrics
                months_remaining=months_remaining
            )
            
            if goal_feasibility['feasibility_ratio'] < 1:
                alerts_to_create.append({
                    "alert_type": "GOAL_BEHIND_SCHEDULE",
                    "severity": "warning",
                    "message": f"Goal '{goal.goal_name}' is behind schedule. Required: ₹{goal_feasibility['required_monthly']:,.0f}/month, Available: ...",
                    "metric_value": goal_feasibility['feasibility_ratio'],
                    "threshold": 1.0
                })
    
    # ========== BUSINESS ALERTS ==========
    
    # ALERT 5: Negative Cash Flow
    if metrics.cash_flow is not None and metrics.cash_flow < 0:
        alerts_to_create.append({
            "alert_type": "NEGATIVE_CASH_FLOW",
            "severity": "critical",
            "message": f"Cash flow is negative (₹{metrics.cash_flow:,.0f}). Business is spending more than earning.",
            "metric_value": metrics.cash_flow,
            "threshold": 0
        })
    
    # ALERT 6: Low Working Capital
    if metrics.working_capital is not None:
        # Assume monthly expenses ~ 5% of annual revenue
        estimated_monthly_expenses = metrics.business_revenue / 12 * Decimal('0.4') if metrics.business_revenue else Decimal(0)
        if metrics.working_capital < estimated_monthly_expenses:
            alerts_to_create.append({
                "alert_type": "LOW_WORKING_CAPITAL",
                "severity": "warning",
                "message": f"Working capital is ₹{metrics.working_capital:,.0f}. Maintain at least 1 month of expenses.",
                "metric_value": metrics.working_capital,
                "threshold": estimated_monthly_expenses
            })
    
    # ALERT 7: High Debt Ratio (>60%)
    if metrics.debt_ratio and metrics.debt_ratio > 60:
        alerts_to_create.append({
            "alert_type": "HIGH_DEBT_RATIO",
            "severity": "critical",
            "message": f"Debt ratio is {metrics.debt_ratio:.1f}%. You're over-leveraged. Target: <60%.",
            "metric_value": metrics.debt_ratio,
            "threshold": 60
        })
    
    # ALERT 8: High EMI Burden (>30% of revenue)
    if metrics.emi_burden_ratio and metrics.emi_burden_ratio > 30:
        alerts_to_create.append({
            "alert_type": "HIGH_EMI_BURDEN",
            "severity": "warning",
            "message": f"EMI burden is {metrics.emi_burden_ratio:.1f}% of revenue. Keep below 30%.",
            "metric_value": metrics.emi_burden_ratio,
            "threshold": 30
        })
    
    # ALERT 9: Low Profit Margin (<5%)
    if metrics.net_profit_margin is not None and metrics.net_profit_margin < 5:
        alerts_to_create.append({
            "alert_type": "LOW_PROFIT_MARGIN",
            "severity": "warning",
            "message": f"Net profit margin is {metrics.net_profit_margin:.1f}%. Improve pricing or cut costs.",
            "metric_value": metrics.net_profit_margin,
            "threshold": 5
        })
    
    # ========== UPDATE ALERTS TABLE ==========
    
    for alert_data in alerts_to_create:
        # Check if alert already exists
        existing_alert = db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.alert_type == alert_data['alert_type'],
            Alert.status == 'active'
        ).first()
        
        if existing_alert:
            # Update existing
            existing_alert.message = alert_data['message']
            existing_alert.metric_value = alert_data['metric_value']
            existing_alert.updated_at = datetime.now()
        else:
            # Create new
            new_alert = Alert(
                user_id=user_id,
                alert_type=alert_data['alert_type'],
                severity=alert_data['severity'],
                message=alert_data['message'],
                metric_value=alert_data['metric_value'],
                threshold=alert_data['threshold'],
                status='active'
            )
            db.add(new_alert)
    
    # RESOLVE alerts that no longer apply
    existing_alerts = db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.status == 'active'
    ).all()
    
    for alert in existing_alerts:
        # If alert not in alerts_to_create and condition no longer met, resolve it
        if not any(a['alert_type'] == alert.alert_type for a in alerts_to_create):
            alert.status = 'resolved'
            alert.resolved_at = datetime.now()
    
    db.commit()
```

---

[Continues in next part due to length...]

