from sqlalchemy import create_engine, inspect
import os

# Use the postgresql:// URL (sync)
DATABASE_URL = "postgresql://horizon:horizon_secret@localhost:5432/horizon_erp"

def check_columns():
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        if 'users' not in inspector.get_table_names():
            print("Table 'users' does not exist!")
            return

        columns = inspector.get_columns('users')
        print(f"Found {len(columns)} columns in 'users' table:")
        for column in columns:
            print(f"- {column['name']} ({column['type']})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_columns()
