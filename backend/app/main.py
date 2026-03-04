"""
FINVISTA — FastAPI Application Entry Point
main.py: ~50 lines, imports routers, configures middleware, creates tables on startup.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import (
    auth, accounts, loans, investments, tax, business, dashboard
)

# Import all models so they register with Base.metadata
from app.models import (  # noqa: F401
    User, BankAccount, Loan, CreditCard, Investment,
    Goal, Tax, PersonalMetrics, BusinessMetrics, Alert, Cash,
    BusinessInventory, BusinessReceivable, BusinessPayable, ScheduledAlert,
)

# ── Create FastAPI app ──
app = FastAPI(
    title="FINVISTA API",
    description="Modular financial analytics platform for Indian users",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ──
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(loans.router)
app.include_router(investments.router)
app.include_router(tax.router)
app.include_router(business.router)
app.include_router(dashboard.router)


# ── Startup Event: Create Tables ──
@app.on_event("startup")
def on_startup():
    """Create all database tables on startup (idempotent)."""
    Base.metadata.create_all(bind=engine)
    print("✅ FINVISTA database tables created / verified.")


# ── Health Check ──
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": "FINVISTA",
        "version": "1.0.0",
        "docs": "/docs",
    }


# ── Run with uvicorn ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
