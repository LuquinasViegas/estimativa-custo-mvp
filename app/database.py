# Configuracao da conexao e das sessoes do PostgreSQL.

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/estimativa_custo")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    # Fornece uma sessao SQLAlchemy para uma requisicao HTTP.
    # Usada pelo FastAPI com Depends(get_db). Cria a sessao antes da rota,
    # entrega-a para a rota e garante seu fechamento, inclusive em erros.
    # Retorna por yield uma sessao transacional para consultas e gravacoes.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
