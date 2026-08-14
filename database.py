import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración automática para desarrollo y producción
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Producción (Render) - PostgreSQL
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
else:
    # Desarrollo local - SQLite
    DATABASE_URL = "sqlite:///./blog.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: abre una sesion y la cierra al terminar la request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
