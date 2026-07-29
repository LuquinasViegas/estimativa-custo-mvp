// Controla o formulario: carrega catalogos, envia a solicitacao e apresenta o retorno da API.
const form = document.getElementById("form-estimativa");
const resultadoDiv = document.getElementById("resultado");
const erroDiv = document.getElementById("erro");

/** Converte um numero em moeda brasileira para exibicao na tela. */
function formatarMoeda(valor) {
    return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

/** Oculta o resultado e o erro da tentativa anterior antes de um novo envio. */
function esconderMensagens() {
    resultadoDiv.classList.add("oculto");
    erroDiv.classList.add("oculto");
}

/**
 * Busca um catalogo ativo na API e preenche o select correspondente.
 *
 * @param {string} idSelect Identificador do elemento HTML select.
 * @param {string} rota Endpoint que retorna uma lista de codigo e nome.
 * @returns {Promise<void>} Rejeita quando a API nao responde com sucesso.
 */
async function carregarOpcoes(idSelect, rota) {
    const select = document.getElementById(idSelect);
    const resposta = await fetch(rota);
    if (!resposta.ok) throw new Error("Nao foi possivel carregar o catalogo do banco de dados.");
    const opcoes = await resposta.json();
    select.innerHTML = '<option value="">Selecione...</option>';
    for (const opcao of opcoes) {
        const item = document.createElement("option");
        item.value = opcao.codigo;
        item.textContent = opcao.nome;
        select.appendChild(item);
    }
}

// Carrega os tres selects em paralelo ao abrir a pagina e mostra eventual falha.
Promise.all([
    carregarOpcoes("tipo_servico", "/api/catalogo/servicos"),
    carregarOpcoes("localizacao", "/api/catalogo/estados"),
    carregarOpcoes("nivel_acabamento", "/api/catalogo/acabamentos"),
]).catch((erro) => {
    erroDiv.textContent = erro.message;
    erroDiv.classList.remove("oculto");
});

// Intercepta o submit para chamar a API sem recarregar a pagina.
form.addEventListener("submit", async (event) => {
    event.preventDefault();
    esconderMensagens();
    const dados = {
        tipo_servico: document.getElementById("tipo_servico").value,
        metragem: parseFloat(document.getElementById("metragem").value),
        localizacao: document.getElementById("localizacao").value,
        nivel_acabamento: document.getElementById("nivel_acabamento").value,
    };
    try {
        const resposta = await fetch("/api/estimativas", {
            method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(dados),
        });
        const corpo = await resposta.json();
        if (!resposta.ok) {
            const mensagem = Array.isArray(corpo.detail) ? corpo.detail.map((d) => d.msg).join(" ") : corpo.detail;
            throw new Error(mensagem || "Erro ao calcular a estimativa.");
        }
        resultadoDiv.innerHTML = `<h2>Estimativa #${corpo.id}</h2><p><strong>Faixa estimada:</strong> ${formatarMoeda(corpo.faixa_min)} - ${formatarMoeda(corpo.faixa_max)}</p><p><strong>Valor base:</strong> ${formatarMoeda(corpo.custo_base)}</p>`;
        resultadoDiv.classList.remove("oculto");
    } catch (erro) {
        erroDiv.textContent = erro.message;
        erroDiv.classList.remove("oculto");
    }
});
