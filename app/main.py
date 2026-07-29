# Rotas HTTP, consulta de catalogos e persistencia de estimativas.

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.calculation import calcular_estimativa
from app.database import get_db
from app.models import Estado, Estimativa, NivelAcabamento, Servico
from app.schemas import EstimativaRequest, EstimativaResponse, OpcaoCatalogo

app = FastAPI(title="Estimativa de Custo - MVP")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def form_page(request: Request):
    # Entrega o HTML do formulario na rota raiz.
    # request e usado pelo Jinja para renderizar o template.
    # Retorna a pagina inicial; o JavaScript carrega os selects depois.
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/catalogo/servicos", response_model=list[OpcaoCatalogo])
def listar_servicos(db: Session = Depends(get_db)):
    # Lista servicos ativos em ordem alfabetica para o formulario.
    # Expoe apenas codigo e nome; o preco-base permanece somente no backend.
    return [OpcaoCatalogo(codigo=item.codigo, nome=item.nome) for item in db.query(Servico).filter_by(ativo=True).order_by(Servico.nome).all()]


@app.get("/api/catalogo/estados", response_model=list[OpcaoCatalogo])
def listar_estados(db: Session = Depends(get_db)):
    # Lista UFs ativas, ordenadas pelo nome do estado, para o formulario.
    return [OpcaoCatalogo(codigo=item.uf, nome=f"{item.nome} ({item.uf})") for item in db.query(Estado).filter_by(ativo=True).order_by(Estado.nome).all()]


@app.get("/api/catalogo/acabamentos", response_model=list[OpcaoCatalogo])
def listar_acabamentos(db: Session = Depends(get_db)):
    # Lista acabamentos ativos seguindo a ordem definida no catalogo.
    return [OpcaoCatalogo(codigo=item.codigo, nome=item.nome) for item in db.query(NivelAcabamento).filter_by(ativo=True).order_by(NivelAcabamento.id).all()]


@app.post("/api/estimativas", response_model=EstimativaResponse, status_code=201)
def criar_estimativa(payload: EstimativaRequest, db: Session = Depends(get_db)):
    # Valida os tres catalogos, calcula a faixa e persiste uma estimativa.
    # Se algum codigo estiver ausente/inativo, retorna HTTP 422. Caso contrario,
    # usa seus fatores, grava entrada e resultado e confirma a transacao.
    # payload contem servico, metragem, UF e acabamento enviados pelo cliente.
    # db e a sessao SQLAlchemy injetada por get_db; retorna o registro gravado.
    servico = db.query(Servico).filter_by(codigo=payload.tipo_servico, ativo=True).first()
    estado = db.query(Estado).filter_by(uf=payload.localizacao, ativo=True).first()
    acabamento = db.query(NivelAcabamento).filter_by(codigo=payload.nivel_acabamento, ativo=True).first()
    if servico is None:
        raise HTTPException(422, "Tipo de servico invalido ou inativo.")
    if estado is None:
        raise HTTPException(422, "UF invalida ou inativa.")
    if acabamento is None:
        raise HTTPException(422, "Nivel de acabamento invalido ou inativo.")

    resultado = calcular_estimativa(payload.metragem, servico.preco_base_m2, acabamento.multiplicador, estado.fator_custo)
    registro = Estimativa(tipo_servico=servico.codigo, metragem=payload.metragem, localizacao=estado.uf, nivel_acabamento=acabamento.codigo, custo_base=resultado.custo_base, faixa_min=resultado.faixa_min, faixa_max=resultado.faixa_max)
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@app.get("/api/estimativas/{estimativa_id}", response_model=EstimativaResponse)
def obter_estimativa(estimativa_id: int, db: Session = Depends(get_db)):
    # Busca uma estimativa pelo ID e devolve HTTP 404 se ela nao existir.
    registro = db.get(Estimativa, estimativa_id)
    if registro is None:
        raise HTTPException(404, "Estimativa nao encontrada.")
    return registro


@app.get("/api/estimativas", response_model=list[EstimativaResponse])
def listar_estimativas(db: Session = Depends(get_db)):
    # Retorna no maximo 50 estimativas, da mais recente para a mais antiga.
    return db.query(Estimativa).order_by(Estimativa.id.desc()).limit(50).all()
