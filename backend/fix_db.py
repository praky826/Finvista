from app.database import engine
from sqlalchemy import text

with engine.connect() as con:
    try:
        con.execute(text("ALTER TABLE users ADD COLUMN monthly_savings NUMERIC(15, 2);"))
        con.commit()
        print("Column monthly_savings added successfully.")
    except Exception as e:
        print(f"Error adding column: {e}")
