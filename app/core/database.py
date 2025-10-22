from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Criar engine do SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexão antes de usar
    echo=settings.DEBUG,  # Log de queries SQL em desenvolvimento
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class para os models
Base = declarative_base()


def get_db():
    """
    Dependency para obter sessão do banco de dados.
    Usado em endpoints FastAPI com Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
