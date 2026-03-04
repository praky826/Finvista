"""
One-time migration: Drop old derived_metrics table.
New tables (personal_metrics, business_metrics) will be auto-created by main.py on startup.
"""
import sys
sys.path.insert(0, ".")

from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS derived_metrics CASCADE"))
    conn.commit()
    print("✅ Dropped old 'derived_metrics' table")

    # Verify
    result = conn.execute(text(
        "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
    ))
    print("\nCurrent tables:")
    for row in result:
        print(f"  • {row[0]}")

print("\n🚀 Now start the backend with: python -m uvicorn app.main:app --reload")
