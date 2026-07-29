# Decisoes tecnicas

## Interpretacao do problema

O objetivo foi interpretado como um MVP de ponta a ponta: formulario simples, API, validacao, calculo deterministico, persistencia no PostgreSQL e apresentacao do resultado. A implementacao evita recursos fora do escopo, como autenticacao, painel administrativo, integracoes externas, deploy e interface sofisticada.

## Premissas adotadas

1. A formula e `preco_base_m2 x metragem x multiplicador_acabamento x fator_localizacao`, com faixa de 10% abaixo e acima do custo-base. Ela e deterministica, consistente e simples de explicar.
2. Precos por m2, multiplicadores e fatores regionais sao valores demonstrativos e nao representam cotacao real de mercado.
3. A localizacao e uma UF brasileira. A migracao inicial cadastra as 27 UFs; uma UF inexistente ou inativa e rejeitada com HTTP 422.
4. O catalogo inicial possui seis servicos e tres niveis de acabamento.
5. Cada estimativa guarda os dados solicitados e o resultado calculado na mesma tabela. O calculo e sincrono e nao ha edicao ou recalculo neste MVP.

## Decisoes tecnicas

- **FastAPI e Pydantic**: definem as rotas, validam o contrato de entrada e geram documentacao interativa em `/docs`.
- **SQLAlchemy**: concentra os modelos e o acesso ao PostgreSQL. A dependencia `get_db` abre uma sessao por requisicao e garante seu fechamento.
- **Catalogos no banco**: `estados`, `servicos` e `niveis_acabamento` armazenam as opcoes e fatores. A API consulta essas tabelas tanto para preencher os selects quanto para validar e calcular a estimativa; assim, valores de negocio nao ficam duplicados no HTML ou na regra de calculo.
- **Migracao SQL com seed idempotente**: `migrations/001_create_estimativas.sql` e a unica fonte de criacao do schema. Ela cria as tabelas, chaves estrangeiras e dados iniciais. A aplicacao nao executa `Base.metadata.create_all` no startup; isso evita um banco parcialmente criado, sem catalogos ou restricoes relacionais.
- **Regra isolada**: `app/calculation.py` recebe somente os fatores validados e nao depende de HTTP, ORM ou PostgreSQL. Isso permite testes unitarios rapidos e repetiveis.
- **HTML, CSS e JavaScript puro**: o frontend e servido pelo FastAPI e carrega os catalogos via API, sem build step ou framework adicional.
- **Valores monetarios com float**: escolha aceitavel para este MVP didatico, pois a faixa e arredondada a duas casas. Em producao, valores monetarios usariam `NUMERIC` no PostgreSQL e `Decimal` no Python.

## Alternativas consideradas

- **Alembic**: seria mais apropriado para uma evolucao com muitas versoes de schema, mas adicionaria configuracao desnecessaria neste MVP. O script SQL versionado atende ao entregavel de migracao.
- **Duas tabelas (solicitacao e resultado)**: nao agregariam valor enquanto o calculo e imediato e imutavel. Seriam consideradas se houvesse processamento assincrono, historico de recalculo ou aprovacao.
- **React ou outro framework frontend**: descartado porque um formulario com `fetch` cobre o fluxo solicitado sem aumentar o escopo.

## Simplificacoes

- A administracao dos catalogos e feita diretamente no banco; nao ha tela administrativa.
- A listagem de estimativas e limitada a 50 registros e nao possui paginacao nem filtros.
- Os testes automatizados cobrem a regra de calculo. Testes de integracao API/PostgreSQL ficaram fora do escopo minimo.
- Nao ha tratamento especializado para indisponibilidade do banco, concorrencia ou retentativas de transacao.

## Melhorias para producao

- Adotar Alembic, testes de integracao e CI.
- Usar `Decimal`/`NUMERIC`, historico de vigencia dos fatores e snapshot dos fatores aplicados a cada estimativa.
- Adicionar tratamento padronizado para falhas de infraestrutura, logs estruturados, metricas e observabilidade.
- Incluir autenticacao, autorizacao, paginacao, filtros e painel para gestao dos catalogos quando esses recursos entrarem no escopo.

## Uso de IA

IA's usadas -> Claude e Codex.
As ferramentas de IA foram usadas como apoio para estruturar a solucao, revisar modelagem e regras, gerar codigo inicial, documentacao e cenarios de teste. O resultado foi revisado manualmente; a regra de calculo, as validacoes, o fluxo da API e a persistencia podem ser explicados durante a apresentacao.
