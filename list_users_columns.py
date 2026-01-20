from sqlalchemy import create_engine, inspect
import sys

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
        col_names = sorted([c['name'] for c in columns])
        
        print(f"Found {len(col_names)} columns in 'users' table:")
        for name in col_names:
            print(f"- {name}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_columns()
