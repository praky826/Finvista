import sys
from app.database import SessionLocal
from app.engines.recalculation_engine import recalculate_all_metrics
from app.models.user import User

db = SessionLocal()
# Get the most recently created user
u = db.query(User).order_by(User.user_id.desc()).first()

if u:
    try:
        print(f"Testing recalculation for latest user: {u.username} (ID: {u.user_id})")
        recalculate_all_metrics(u.user_id, db)
        print("Success")
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stdout)
else:
    print("No users found.")
