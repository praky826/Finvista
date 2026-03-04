# 📊 FINVISTA

**FINVISTA** is a comprehensive, modular financial analytics platform tailored for granular tracking of both **Personal** and **Business** finances. Designed with a modern tech stack and decoupled architecture, FINVISTA provides automated metric recaluation, intelligent alerts, and dynamic dashboards to give users complete control over their financial health.

---

## ✨ Key Features

- **Dual-Domain Tracking**: Seamlessly switch between Personal and Business financial profiles depending on your account type (Personal, Business, or Both).
- **Automated Recalculation Engine**: Whenever an asset, liability, or income stream updates, Finvista's decoupled recalculation engines immediately compute updated KPIs (Net Worth, Debt-to-Income, Savings Ratios, Net Margins, etc.).
- **Smart Alert System**: Proactive notifications regarding high credit utilization, low emergency funds, pending receivables, and upcoming EMI deadlines.
- **Taxation Engine**: Integrated scenario-based tax calculations comparing Old vs. New tax regimes based on Indian taxation standards.
- **Deep Financial Granularity**: Native tracking for Bank Accounts, Cash flow, Credit Cards, Loans (with EMI scheduling), Investments (FDs, MFs, Gold, Real Estate), and Financial Goals.
- **Business Modules**: Dedicated tracking for Working Capital, Inventory Valuation, Accounts Receivable, and Accounts Payable.

---

## 🛠️ Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: PostgreSQL with [SQLAlchemy](https://www.sqlalchemy.org/) ORM
- **Authentication**: JWT (JSON Web Tokens) with Argon2/Bcrypt password hashing
- **Architecture**: Service-Oriented Architecture (Decoupled Routers, Services, and Evaluation Engines)

### Frontend
- **Framework**: [React](https://reactjs.org/) + [TypeScript](https://www.typescriptlang.org/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Charting**: [Recharts](https://recharts.org/)
- **Icons**: [Lucide React](https://lucide.dev/)

---

## 📐 Architecture & Domain Decoupling

FINVISTA implements a strict separation of concerns between personal banking and business operations:

1. **Database Decoupling**: Separate `personal_metrics` and `business_metrics` tables prevent data bleeding and ensure modular scalability.
2. **Engine Decoupling**: Independent Recalculation Engines (`personal_recalculation_engine.py` & `business_recalculation_engine.py`) isolate business KPIs (like Working Capital and Net Profit Margins) from personal KPIs (like Emergency Funds and Health Scores).
3. **Frontend Views**: The UI utilizes granular API fetching to distinct `/dashboard/personal` and `/dashboard/business` endpoints, allowing dual-account users to easily toggle their financial contexts without reloading.

---

## 📂 Project Structure

```text
FINVISTA/
│
├── backend/                       # FastAPI Backend
│   ├── app/
│   │   ├── engines/               # Financial logic & metric recalculation
│   │   ├── models/                # SQLAlchemy DB models 
│   │   ├── routers/               # API endpoints
│   │   ├── schemas/               # Pydantic validation schemas
│   │   ├── security/              # Auth & JWT handling
│   │   └── services/              # Business logic & DB transactions
│   ├── main.py                    # Application entry point
│   └── requirements.txt           # Python dependencies
│
└── frontend/                      # React Frontend
    ├── src/
    │   ├── components/            # Reusable UI elements (Charts, Widgets)
    │   ├── context/               # React Context (Auth State)
    │   ├── pages/                 # Full screen views (Dashboard, Register)
    │   └── services/              # API interceptors and fetch logic
    ├── tailwind.config.js         # Tailwind styling tokens
    └── package.json               # Node dependencies
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- PostgreSQL (v14+)

### 1. Setting up the Backend
Navigate to the backend directory and set up your Python environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Configuration**: 
Create a `.env` file in the `backend/` directory referencing your local PostgreSQL instance and JWT secret:
```env
# backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/finvista
JWT_SECRET_KEY=your_super_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Run the Server**:
The backend utilizes `Base.metadata.create_all()` to auto-generate database tables on startup.
```bash
python -m uvicorn app.main:app --reload --port 8000
```
*API Documentation will be available at: http://localhost:8000/docs*

### 2. Setting up the Frontend
Open a new terminal, navigate to the frontend directory, and install dependencies:

```bash
cd frontend
npm install
```

**Run the Application**:
```bash
npm run dev
```
*The React app will be available at: http://localhost:5173*

---

## 🤝 Contributing

1. BBG fork me bbg.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
