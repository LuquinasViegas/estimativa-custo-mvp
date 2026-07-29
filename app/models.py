# Modelos SQLAlchemy que representam as tabelas do PostgreSQL.

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


class Estado(Base):
    # UF, nome e fator regional usados no calculo de novas estimativas.
    __tablename__ = "estados"
    id = Column(Integer, primary_key=True)
    uf = Column(String(2), unique=True, nullable=False, index=True)
    nome = Column(String(50), nullable=False)
    fator_custo = Column(Float, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)


class Servico(Base):
    # Servico disponivel e seu preco-base por metro quadrado.
    __tablename__ = "servicos"
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False)
    preco_base_m2 = Column(Float, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)


class NivelAcabamento(Base):
    # Nivel de acabamento e multiplicador aplicado ao preco-base.
    __tablename__ = "niveis_acabamento"
    id = Column(Integer, primary_key=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    nome = Column(String(50), nullable=False)
    multiplicador = Column(Float, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)


class Estimativa(Base):
    # Solicitacao recebida e valores calculados, armazenados de forma imutavel.
    __tablename__ = "estimativas"
    id = Column(Integer, primary_key=True, index=True)
    tipo_servico = Column(String(50), ForeignKey("servicos.codigo"), nullable=False)
    metragem = Column(Float, nullable=False)
    localizacao = Column(String(2), ForeignKey("estados.uf"), nullable=False)
    nivel_acabamento = Column(String(20), ForeignKey("niveis_acabamento.codigo"), nullable=False)
    custo_base = Column(Float, nullable=False)
    faixa_min = Column(Float, nullable=False)
    faixa_max = Column(Float, nullable=False)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
