
import sys
import os
sys.path.append(os.getcwd())

try:
    from sqlalchemy.orm import DeclarativeBase, declared_attr
    from sqlalchemy import Column, String, DateTime
    from datetime import datetime

    class Base(DeclarativeBase):
        @declared_attr.directive
        def __tablename__(cls) -> str:
            name = cls.__name__
            return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_') + 's'

    class TimestampMixin:
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)

    class UUIDMixin:
        id = Column(String, primary_key=True)

    print("Declaring Organization...")
    class Organization(Base, UUIDMixin, TimestampMixin):
        name = Column(String)
        # metadata = Column(String) # This would cause the error
    
    print("Organization declared successfully")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
