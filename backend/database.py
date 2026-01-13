from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
DATABASE_URL = "postgresql://super:your_password@sackson-5021.postgres.pythonanywhere-services.com:15021/sackson$aipi_db"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:secret@localhost:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()