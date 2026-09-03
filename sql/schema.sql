-- ====================================================================
-- Script DDL: Criação do Esquema do Banco de Dados para Locadora de Veículos
-- Banco de Dados: SQLite 3
-- ====================================================================

PRAGMA foreign_keys = ON;

-- 1. Tabela: clientes
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL UNIQUE,
    cnh TEXT NOT NULL UNIQUE,
    telefone TEXT,
    email TEXT NOT NULL UNIQUE,
    cidade TEXT NOT NULL,
    estado TEXT NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela: categorias
CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    valor_diaria_base REAL NOT NULL CHECK(valor_diaria_base > 0)
);

-- 3. Tabela: veiculos
CREATE TABLE IF NOT EXISTS veiculos (
    id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_categoria INTEGER NOT NULL,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    ano INTEGER NOT NULL,
    placa TEXT NOT NULL UNIQUE,
    cor TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Disponivel' CHECK(status IN ('Disponivel', 'Alugado', 'Manutencao')),
    quilometragem INTEGER NOT NULL DEFAULT 0 CHECK(quilometragem >= 0),
    FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria) ON DELETE RESTRICT
);

-- 4. Tabela: locacoes
CREATE TABLE IF NOT EXISTS locacoes (
    id_locacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    id_veiculo INTEGER NOT NULL,
    data_locacao DATE NOT NULL,
    data_devolucao_prevista DATE NOT NULL,
    data_devolucao_real DATE,
    valor_diaria REAL NOT NULL CHECK(valor_diaria > 0),
    valor_total REAL CHECK(valor_total >= 0),
    status TEXT NOT NULL DEFAULT 'Ativa' CHECK(status IN ('Ativa', 'Finalizada', 'Cancelada')),
    FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente) ON DELETE RESTRICT,
    FOREIGN KEY (id_veiculo) REFERENCES veiculos (id_veiculo) ON DELETE RESTRICT
);

-- 5. Tabela: manutencoes
CREATE TABLE IF NOT EXISTS manutencoes (
    id_manutencao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_veiculo INTEGER NOT NULL,
    data_manutencao DATE NOT NULL,
    tipo_servico TEXT NOT NULL,
    custo REAL NOT NULL CHECK(custo >= 0),
    descricao TEXT,
    FOREIGN KEY (id_veiculo) REFERENCES veiculos (id_veiculo) ON DELETE CASCADE
);

-- Índices para otimização de consultas e joins
CREATE INDEX IF NOT EXISTS idx_veiculos_categoria ON veiculos (id_categoria);
CREATE INDEX IF NOT EXISTS idx_locacoes_cliente ON locacoes (id_cliente);
CREATE INDEX IF NOT EXISTS idx_locacoes_veiculo ON locacoes (id_veiculo);
CREATE INDEX IF NOT EXISTS idx_locacoes_status ON locacoes (status);
CREATE INDEX IF NOT EXISTS idx_manutencoes_veiculo ON manutencoes (id_veiculo);
