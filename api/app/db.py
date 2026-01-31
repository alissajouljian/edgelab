import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_URL = os.environ.get("EDGELAB_DB_URL", "sqlite:////data/edgelab.sqlite")

connect_args = {}
if DB_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# start
engine = create_engine(DB_URL, connect_args=connect_args, pool_pre_ping=True)
# connect
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base is the common parent class that tells SQLAlchemy “these classes are database tables”.

#An ORM model is a Python class that represents a database table.
# Mapping:
# Class → Table
# Object (instance) → Row
# Attributes/fields → Columns
# with Base we make  python class to be DB Table
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
