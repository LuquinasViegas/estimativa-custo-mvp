import pytest

from app.calculation import MetragemInvalidaError, calcular_estimativa


def test_calculo_e_deterministico():
    fatores = dict(metragem=50, preco_base_m2=45, multiplicador_acabamento=1, fator_localizacao=1.15)
    assert calcular_estimativa(**fatores) == calcular_estimativa(**fatores)


def test_calculo_aplica_todos_os_fatores_e_a_faixa():
    resultado = calcular_estimativa(50, 45, 1.0, 1.15)
    assert resultado.custo_base == 2587.50
    assert resultado.faixa_min == 2328.75
    assert resultado.faixa_max == 2846.25


def test_acabamento_alto_aumenta_o_custo():
    basico = calcular_estimativa(30, 700, 0.85, 0.95)
    alto = calcular_estimativa(30, 700, 1.40, 0.95)
    assert alto.custo_base > basico.custo_base


@pytest.mark.parametrize("metragem", [0, -5, -0.01])
def test_metragem_invalida_levanta_erro(metragem):
    with pytest.raises(MetragemInvalidaError):
        calcular_estimativa(metragem, 45, 1, 1)
