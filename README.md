# Estimativa de Custo - MVP

Aplicacao FastAPI para estimar custos de servicos de reforma. O usuario preenche o formulario, a API calcula uma faixa de custo, grava o resultado no PostgreSQL e o exibe na pagina.

Este guia foi escrito para **Windows com PowerShell e PostgreSQL local**.

## Pre-requisitos

Antes de iniciar, instale:

- Python 3.11 ou 3.12;
- PostgreSQL 13 ou superior, incluindo pgAdmin e SQL Shell (psql).

Para confirmar o Python, abra o **PowerShell** e execute:

```powershell
python --version
```

O resultado deve mostrar Python 3.11.x ou 3.12.x.

## 1. Abrir a pasta do projeto

**Onde executar:** PowerShell.

Abra o PowerShell e entre na pasta que contem `README.md`, `app` e `migrations`:

```powershell
cd "C:\caminho_da_pasta"
```

Para conferir se esta no lugar correto:

```powershell
Get-ChildItem
```

Devem aparecer, entre outros, `app`, `migrations`, `tests`, `requirements.txt` e `README.md`.

## 2. Criar o banco de dados PostgreSQL

O banco usado pela aplicacao se chama `estimativa_custo`.

### Opcao A: pelo PowerShell, usando `createdb`

**Onde executar:** PowerShell. Use esta opcao somente se o comando `createdb` for reconhecido.

```powershell
createdb -U postgres estimativa_custo
```

Digite a senha do usuario `postgres` quando solicitada.

Se aparecer que `createdb` nao e reconhecido, use a Opcao B.

### Opcao B: pelo pgAdmin

**Onde executar:** pgAdmin.

1. Abra o **pgAdmin 4**.
2. No painel da esquerda, abra `Servers` -> seu servidor PostgreSQL -> `Databases`.
3. Clique com o botao direito em `Databases` -> **Create** -> **Database...**.
4. Em **Database**, informe `estimativa_custo`.
5. Mantenha o proprietario como `postgres` e clique em **Save**.

### Opcao C: pelo SQL Shell (psql)

**Onde executar:** aplicativo **SQL Shell (psql)**, aberto pelo menu Iniciar do Windows.

Nas perguntas iniciais, apenas pressione Enter para aceitar `localhost`, `postgres`, porta `5432` e usuario `postgres`. Depois digite a senha quando solicitada. Quando aparecer `postgres=#`, execute:

```sql
CREATE DATABASE estimativa_custo;
```

Se o banco ja existir e voce quiser comecar novamente, conecte-se ao banco `postgres` no pgAdmin/psql e execute:

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'estimativa_custo'
  AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS estimativa_custo;
CREATE DATABASE estimativa_custo;
```

## 3. Criar e ativar o ambiente virtual Python

**Onde executar:** PowerShell, dentro da pasta do projeto aberta no passo 1.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Quando funcionar, o inicio da linha do PowerShell mostrara `(.venv)`.

Se o PowerShell bloquear a ativacao, execute este comando apenas na janela atual e tente ativar novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 4. Instalar as dependencias

**Onde executar:** PowerShell, com `(.venv)` visivel no inicio da linha.

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Esse comando instala FastAPI, SQLAlchemy, Psycopg2, Uvicorn, Pytest e as demais bibliotecas usadas pelo projeto.

## 5. Importar a estrutura e os dados iniciais

Este passo e obrigatorio. A aplicacao nao cria tabelas automaticamente ao iniciar.

A migracao `migrations/001_create_estimativas.sql` cria as tabelas, chaves estrangeiras e dados iniciais:

- 27 UFs em `estados`;
- seis servicos em `servicos`;
- tres niveis em `niveis_acabamento`;
- tabela `estimativas` para as solicitacoes e resultados.

### Forma recomendada: SQL Shell (psql)

**Onde executar:** primeiro no PowerShell, depois no SQL Shell (psql).

O caminho do projeto possui `Área`, que pode causar erro de codificacao no SQL Shell. Por isso, no **PowerShell**, copie temporariamente a migracao para um caminho simples:

```powershell
New-Item -ItemType Directory -Force C:\temp
Copy-Item ".\migrations\001_create_estimativas.sql" "C:\temp\001_create_estimativas.sql"
```

Depois abra o **SQL Shell (psql)**. Aceite os valores padrao das perguntas de conexao e digite a senha do usuario `postgres`. Quando aparecer `postgres=#`, execute os dois comandos abaixo, um de cada vez:

```sql
\c estimativa_custo
\i 'C:/temp/001_create_estimativas.sql'
```

O resultado esperado inclui mensagens como `CREATE TABLE` e `INSERT 0 ...`.

### Conferir a importacao no pgAdmin

**Onde executar:** pgAdmin.

No painel esquerdo, abra:

```text
Servers -> PostgreSQL -> Databases -> estimativa_custo -> Schemas -> public -> Tables
```

Se necessario, clique com o botao direito em `Tables` -> **Refresh**. Devem existir `estados`, `servicos`, `niveis_acabamento` e `estimativas`.

## 6. Configurar a senha do banco para a aplicacao

**Onde executar:** PowerShell, com `(.venv)` ativo. Execute no mesmo terminal em que voce iniciara o servidor.

Defina a variavel `DATABASE_URL`, substituindo `SUA_SENHA` pela senha do usuario PostgreSQL `postgres`:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/estimativa_custo"
```

Exemplo, caso sua senha local seja `Senha123_Projeto`:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://postgres:Senha123_Projeto@localhost:5432/estimativa_custo"
```

Use uma senha com letras, numeros e `_` para evitar problemas na URL. Se sua senha tiver `@`, `#`, `ç`, espacos ou outros caracteres especiais, ela precisa ser codificada para URL.

Essa variavel vale somente para a janela atual do PowerShell. Se fechar a janela, defina-a novamente antes de iniciar o servidor.

## 7. Executar os testes automatizados

**Onde executar:** PowerShell, com `(.venv)` ativo e dentro da pasta do projeto.

```powershell
python -m pytest
```

Resultado esperado:

```text
6 passed
```

Os testes cobrem a regra deterministica: `preco_base_m2 x metragem x multiplicador_acabamento x fator_localizacao`, com faixa de +/- 10%.

Os cenarios manuais funcionais e nao funcionais estao em [TEST_SCENARIOS.md](./TEST_SCENARIOS.md).

## 8. Iniciar a aplicacao

**Onde executar:** PowerShell, com `(.venv)` ativo, dentro da pasta do projeto e apos configurar `DATABASE_URL` no passo 6.

```powershell
python -m uvicorn app.main:app --reload
```

Se tudo estiver correto, aparecera uma mensagem semelhante a:

```text
Uvicorn running on http://127.0.0.1:8000
```

Abra no navegador:

- Aplicacao: [http://localhost:8000](http://localhost:8000)
- Documentacao e testes manuais da API: [http://localhost:8000/docs](http://localhost:8000/docs)

Para parar o servidor, volte ao PowerShell e pressione `Ctrl + C`.

## Endpoints

| Metodo | Rota | Descricao |
|---|---|---|
| GET | `/` | Formulario HTML |
| GET | `/api/catalogo/servicos` | Servicos ativos do banco |
| GET | `/api/catalogo/estados` | UFs ativas do banco |
| GET | `/api/catalogo/acabamentos` | Acabamentos ativos do banco |
| POST | `/api/estimativas` | Calcula e persiste uma estimativa |
| GET | `/api/estimativas/{id}` | Consulta uma estimativa por ID |
| GET | `/api/estimativas` | Lista as ultimas 50 estimativas |
