# Cenários de teste

Este documento separa testes funcionais (o que o sistema faz) de testes não funcionais (qualidade, segurança e comportamento sob condições adversas). Os cenários manuais podem ser executados pela interface, Swagger (`/docs`) ou ferramenta HTTP.

## Dados de referência

Use, quando aplicável: serviço `pintura` (R$ 45/m²), UF `SP` (fator 1,15), acabamento `medio` (fator 1,0) e metragem `50`. Resultado esperado: custo-base **R$ 2.587,50**, faixa **R$ 2.328,75 a R$ 2.846,25**.

## Testes funcionais

| ID | Cenário | Passos | Resultado esperado |
|---|---|---|---|
| F01 | Carregar formulário | Iniciar API e abrir `/`. | Página é exibida e os três selects são preenchidos com dados do banco. |
| F02 | Listar catálogo de serviços | Acessar `GET /api/catalogo/servicos`. | Retorna HTTP 200, somente serviços ativos, com `codigo` e `nome`. |
| F03 | Listar UFs | Acessar `GET /api/catalogo/estados`. | Retorna HTTP 200 e as 27 UFs cadastradas. |
| F04 | Criar estimativa válida | Enviar `POST /api/estimativas` com os dados de referência. | HTTP 201, valores iguais aos dados de referência e ID gerado. |
| F05 | Persistir estimativa | Executar F04 e consultar `SELECT * FROM estimativas ORDER BY id DESC;` no pgAdmin. | Existe registro com os quatro dados enviados e os três valores calculados. |
| F06 | Consultar por ID | Usar o ID retornado em `GET /api/estimativas/{id}`. | HTTP 200 e o mesmo registro criado. |
| F07 | Listar estimativas | Acessar `GET /api/estimativas`. | HTTP 200, lista ordenada da mais recente para a mais antiga e limitada a 50 itens. |
| F08 | Metragem inválida | Enviar metragem `0` ou `-10`. | HTTP 422; nenhum registro novo é gravado. |
| F09 | Serviço inexistente | Enviar `tipo_servico: "demolicao"`. | HTTP 422 com mensagem de serviço inválido/inativo. |
| F10 | UF inexistente | Enviar `localizacao: "XX"`. | HTTP 422 com mensagem de UF inválida/inativa. |
| F11 | Acabamento inexistente | Enviar `nivel_acabamento: "luxo"`. | HTTP 422 com mensagem de acabamento inválido/inativo. |
| F12 | Normalização | Enviar `" Pintura "`, `" sp "` e `" MEDIO "`. | HTTP 201; API normaliza para `pintura`, `SP` e `medio`. |
| F13 | Catálogo inativo | No banco, definir `ativo = false` para um serviço e tentar usá-lo. | Item não aparece no select e a API retorna HTTP 422 se o código for enviado manualmente. |
| F14 | ID inexistente | Acessar `GET /api/estimativas/999999`. | HTTP 404 com “Estimativa nao encontrada.” |

## Testes não funcionais

| ID | Cenário | Como executar | Critério de aprovação |
|---|---|---|---|
| NF01 | Tempo de resposta | Executar F04 dez vezes em ambiente local. | Cada resposta deve levar menos de 1 segundo, sem erro. |
| NF02 | Concorrência básica | Enviar 10 requisições válidas em paralelo com Postman/Bruno ou `curl`. | Todas retornam 201 e cada uma cria um ID distinto. |
| NF03 | Integridade referencial | Tentar inserir diretamente uma estimativa com UF inexistente via SQL. | PostgreSQL rejeita a inserção pela chave estrangeira. |
| NF04 | Validação de entrada | Enviar JSON sem `metragem`, com texto no lugar de número e UF com três letras. | API retorna HTTP 422, sem erro 500 e sem gravar dados. |
| NF05 | Erro de banco | Parar o serviço PostgreSQL e acessar um endpoint de catálogo. | Falha é visível e a aplicação não grava dados incompletos; ao restaurar o banco, volta a operar. |
| NF06 | Segurança de erro | Enviar campos inválidos pela API. | A resposta não deve expor senha, URL do banco ou stack trace. |
| NF07 | Usabilidade | Preencher todos os campos pela página inicial usando teclado e mouse. | Rótulos são claros, campos obrigatórios impedem envio vazio e resultado/erro é compreensível. |
| NF08 | Compatibilidade básica | Abrir a página em Chrome e Edge atuais. | Formulário, selects, cálculo e formatação em reais funcionam nos dois navegadores. |
| NF09 | Repetibilidade da regra | Executar `python -m pytest` três vezes. | Todos os testes passam nas três execuções, com o mesmo resultado. |
| NF10 | Carga de dados | Criar mais de 50 estimativas válidas e chamar `GET /api/estimativas`. | Endpoint devolve no máximo 50 registros, em ordem decrescente de ID. |

## Evidências sugeridas

Para apresentação, registre capturas do formulário com o resultado de F04, da tabela `estimativas` após F05, do Swagger para F08/F09 e do terminal mostrando `python -m pytest` para NF09.
