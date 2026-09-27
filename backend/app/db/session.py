import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Local peer-auth PostgreSQL is the only fallback; container deployments must
# provide DATABASE_URL through their environment rather than source control.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://riskradar@localhost:5432/riskradar")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
