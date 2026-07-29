-- Estrutura e dados iniciais do MVP de estimativa de custo.
-- Pode ser executado mais de uma vez com seguranca.

CREATE TABLE IF NOT EXISTS estados (
    id SERIAL PRIMARY KEY,
    uf CHAR(2) NOT NULL UNIQUE,
    nome VARCHAR(50) NOT NULL,
    fator_custo DOUBLE PRECISION NOT NULL CHECK (fator_custo > 0),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS servicos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    preco_base_m2 DOUBLE PRECISION NOT NULL CHECK (preco_base_m2 > 0),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS niveis_acabamento (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(50) NOT NULL,
    multiplicador DOUBLE PRECISION NOT NULL CHECK (multiplicador > 0),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS estimativas (
    id SERIAL PRIMARY KEY,
    tipo_servico VARCHAR(50) NOT NULL REFERENCES servicos(codigo),
    metragem DOUBLE PRECISION NOT NULL CHECK (metragem > 0),
    localizacao CHAR(2) NOT NULL REFERENCES estados(uf),
    nivel_acabamento VARCHAR(20) NOT NULL REFERENCES niveis_acabamento(codigo),
    custo_base DOUBLE PRECISION NOT NULL,
    faixa_min DOUBLE PRECISION NOT NULL,
    faixa_max DOUBLE PRECISION NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_estimativas_criado_em ON estimativas (criado_em DESC);

INSERT INTO estados (uf, nome, fator_custo) VALUES
    ('AC', 'Acre', 0.90), ('AL', 'Alagoas', 0.88), ('AP', 'Amapa', 0.95),
    ('AM', 'Amazonas', 0.98), ('BA', 'Bahia', 0.90), ('CE', 'Ceara', 0.88),
    ('DF', 'Distrito Federal', 1.10), ('ES', 'Espirito Santo', 1.00),
    ('GO', 'Goias', 0.95), ('MA', 'Maranhao', 0.85), ('MT', 'Mato Grosso', 0.98),
    ('MS', 'Mato Grosso do Sul', 0.95), ('MG', 'Minas Gerais', 0.95),
    ('PA', 'Para', 0.92), ('PB', 'Paraiba', 0.87), ('PR', 'Parana', 0.95),
    ('PE', 'Pernambuco', 0.85), ('PI', 'Piaui', 0.84), ('RJ', 'Rio de Janeiro', 1.10),
    ('RN', 'Rio Grande do Norte', 0.87), ('RS', 'Rio Grande do Sul', 1.00),
    ('RO', 'Rondonia', 0.92), ('RR', 'Roraima', 0.95), ('SC', 'Santa Catarina', 1.02),
    ('SP', 'Sao Paulo', 1.15), ('SE', 'Sergipe', 0.88), ('TO', 'Tocantins', 0.90)
ON CONFLICT (uf) DO UPDATE SET nome = EXCLUDED.nome, fator_custo = EXCLUDED.fator_custo;

INSERT INTO servicos (codigo, nome, preco_base_m2) VALUES
    ('pintura', 'Pintura', 45.00),
    ('reforma_banheiro', 'Reforma de banheiro', 950.00),
    ('reforma_cozinha', 'Reforma de cozinha', 1100.00),
    ('eletrica', 'Instalacao eletrica', 180.00),
    ('hidraulica', 'Instalacao hidraulica', 200.00),
    ('reforma_geral', 'Reforma geral', 700.00)
ON CONFLICT (codigo) DO UPDATE SET nome = EXCLUDED.nome, preco_base_m2 = EXCLUDED.preco_base_m2;

INSERT INTO niveis_acabamento (codigo, nome, multiplicador) VALUES
    ('basico', 'Basico', 0.85), ('medio', 'Medio', 1.00), ('alto', 'Alto padrao', 1.40)
ON CONFLICT (codigo) DO UPDATE SET nome = EXCLUDED.nome, multiplicador = EXCLUDED.multiplicador;
