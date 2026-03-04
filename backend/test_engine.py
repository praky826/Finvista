import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.engines.recalculation_engine import recalculate_all_metrics
from app.database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print("Testing recalculation for user 22...")
    recalculate_all_metrics(22, db)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc(file=sys.stdout)
