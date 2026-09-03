"""Testes automatizados para conexão, schema e integridade do banco de dados SQLite."""

import sqlite3
import pytest
from src.database import get_connection, init_db


@pytest.fixture
def test_db(tmp_path):
    """Fixture que cria um banco de dados temporário isolado para testes."""
    db_file = tmp_path / "test_locadora.db"
    init_db(db_path=db_file, populate_seed=True)
    return db_file


def test_init_db_creates_all_tables(test_db):
    """Verifica se todas as 5 tabelas obrigatórias foram criadas."""
    conn = get_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]
    conn.close()

    expected_tables = ["clientes", "categorias", "veiculos", "locacoes", "manutencoes"]
    for table in expected_tables:
        assert table in tables, f"Tabela '{table}' não foi criada no banco de dados."


def test_init_db_creates_views(test_db):
    """Verifica se todas as views analíticas foram criadas."""
    conn = get_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
    views = [row["name"] for row in cursor.fetchall()]
    conn.close()

    expected_views = [
        "vw_faturamento_por_categoria",
        "vw_desempenho_clientes",
        "vw_historico_locacoes_detalhado",
        "vw_resultado_por_veiculo",
    ]
    for view in expected_views:
        assert view in views, f"View '{view}' não foi criada no banco de dados."


def test_foreign_key_constraint(test_db):
    """Garante que a integridade referencial (FK) está ativa e impede inserções órfãs."""
    conn = get_connection(test_db)
    cursor = conn.cursor()

    # Tentativa de inserir veículo com categoria inexistente (ex: 9999)
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO veiculos (id_categoria, marca, modelo, ano, placa, cor, status, quilometragem)
            VALUES (9999, 'MarcaTeste', 'ModeloTeste', 2024, 'TST9999', 'Preto', 'Disponivel', 0);
            """
        )
        conn.commit()
    conn.close()


def test_unique_constraint_cpf(test_db):
    """Garante que a constraint UNIQUE de CPF impede duplicatas."""
    conn = get_connection(test_db)
    cursor = conn.cursor()

    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO clientes (nome, cpf, cnh, telefone, email, cidade, estado)
            VALUES ('Nome Duplicado', '111.222.333-44', '99999999999', '1199999999', 'teste@email.com', 'SP', 'SP');
            """
        )
        conn.commit()
    conn.close()
