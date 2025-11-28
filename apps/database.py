from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Connect to the file in the parent directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./urbanplate.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 2. Dependency: Used by endpoints to open/close DB connections
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()