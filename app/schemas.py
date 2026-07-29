# Schemas Pydantic que definem os contratos da API.

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class EstimativaRequest(BaseModel):
    # Dados recebidos ao solicitar uma estimativa.
    # Pydantic rejeita metragem nao positiva e UFs com tamanho diferente de dois
    # caracteres. Os validadores permitem entradas como " Pintura " e "sp".
    tipo_servico: str = Field(..., min_length=1)
    metragem: float = Field(..., gt=0)
    localizacao: str = Field(..., min_length=2, max_length=2)
    nivel_acabamento: str = Field(..., min_length=1)

    @field_validator("tipo_servico", "nivel_acabamento")
    @classmethod
    def normalizar_codigo(cls, value: str) -> str:
        # Remove espacos e converte codigos de catalogo em minusculas.
        return value.strip().lower()

    @field_validator("localizacao")
    @classmethod
    def normalizar_uf(cls, value: str) -> str:
        # Remove espacos e converte uma UF para duas letras maiusculas.
        return value.strip().upper()


class EstimativaResponse(BaseModel):
    # Formato de uma estimativa ja persistida e devolvida pela API.
    id: int
    tipo_servico: str
    metragem: float
    localizacao: str
    nivel_acabamento: str
    custo_base: float
    faixa_min: float
    faixa_max: float
    criado_em: datetime

    model_config = {"from_attributes": True}


class OpcaoCatalogo(BaseModel):
    # Opcao enxuta exibida nos campos de selecao do formulario.
    codigo: str
    nome: str
