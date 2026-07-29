# Regra deterministica de calculo da faixa de custo.

from dataclasses import dataclass


class MetragemInvalidaError(ValueError):
    # Indica que a metragem informada nao e um numero maior que zero.
    pass


MARGEM_FAIXA = 0.10


@dataclass(frozen=True)
class ResultadoEstimativa:
    # Resultado imutavel do calculo antes de sua persistencia.
    # custo_base: valor central calculado para o servico.
    # faixa_min: limite inferior, 10% abaixo do valor central.
    # faixa_max: limite superior, 10% acima do valor central.
    custo_base: float
    faixa_min: float
    faixa_max: float


def calcular_estimativa(metragem: float, preco_base_m2: float, multiplicador_acabamento: float, fator_localizacao: float) -> ResultadoEstimativa:
    # Calcula a faixa de custo usando fatores ja validados pela API.
    # Nao acessa banco ou HTTP, portanto a regra pode ser testada isoladamente.
    # Formula: preco_base_m2 * metragem * multiplicador_acabamento * fator_localizacao.
    # A faixa corresponde a mais ou menos 10% do valor central e todos os
    # valores sao arredondados para duas casas decimais.
    #
    # Parametros:
    # - metragem: area em m2; deve ser maior que zero.
    # - preco_base_m2: preco de referencia do servico escolhido.
    # - multiplicador_acabamento: fator do acabamento escolhido.
    # - fator_localizacao: fator regional da UF escolhida.
    #
    # Retorna: ResultadoEstimativa com custo central, faixa minima e maxima.
    # Levanta MetragemInvalidaError se a metragem for nula, zero ou negativa.
    if metragem is None or metragem <= 0:
        raise MetragemInvalidaError("A metragem deve ser um numero maior que zero.")

    custo_base = preco_base_m2 * metragem * multiplicador_acabamento * fator_localizacao
    return ResultadoEstimativa(round(custo_base, 2), round(custo_base * (1 - MARGEM_FAIXA), 2), round(custo_base * (1 + MARGEM_FAIXA), 2))
