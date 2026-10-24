import os
from sqlalchemy import create_engine
from fastapi import HTTPException
from sqlalchemy.orm import declarative_base, sessionmaker

raw_url = os.getenv("DATABASE_URL", "").strip()
DATABASE_CONFIGURED = bool(raw_url)

if raw_url:
    if raw_url.startswith("postgres://"):
        raw_url = "postgresql://" + raw_url[len("postgres://"):]
    if raw_url.startswith("postgresql://"):
        raw_url = raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    DATABASE_URL = raw_url
else:
    # Do not use a local SQLite file on Vercel/serverless.
    # Database-dependent routes will report a clear error until DATABASE_URL is set.
    DATABASE_URL = None

engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
Base = declarative_base()

def get_db():
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not configured. Add a hosted PostgreSQL URL in Vercel Environment Variables.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
