import sys
from app.database import SessionLocal
from app.engines.recalculation_engine import recalculate_all_metrics
from app.models.user import User

db = SessionLocal()
u = db.query(User).filter_by(username='busera_ps').first()

if u:
    try:
        print(f"Testing recalculation for user {u.user_id}...")
        recalculate_all_metrics(u.user_id, db)
        print("Success")
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stdout)
else:
    print("User not found.")
