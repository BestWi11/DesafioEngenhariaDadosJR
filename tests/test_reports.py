"""Testes automatizados para o módulo de relatórios e consultas analíticas SQL."""

import pytest
from src.database import init_db
from src.reports import (
    format_table,
    get_faturamento_por_categoria,
    get_historico_locacoes,
    get_ranking_clientes,
    get_resultado_operacional,
    get_veiculos_mais_alugados,
)


@pytest.fixture
def test_db(tmp_path):
    """Cria e popula um banco de dados temporário para testes."""
    db_file = tmp_path / "test_reports.db"
    init_db(db_path=db_file, populate_seed=True)
    return db_file


def test_get_faturamento_por_categoria(test_db):
    """Testa se o relatório de faturamento por categoria retorna dados consolidados."""
    report = get_faturamento_por_categoria(db_path=test_db)
    assert "headers" in report
    assert "data" in report
    assert len(report["data"]) == 5  # 5 categorias cadastradas
    assert len(report["raw_rows"]) == 5

    # Verifica se os cálculos de faturamento são números válidos
    for row in report["raw_rows"]:
        assert float(row["faturamento_total"]) >= 0
        assert int(row["total_locacoes"]) >= 0


def test_get_ranking_clientes(test_db):
    """Testa se o ranking de clientes ordena corretamente por volume gasto."""
    report = get_ranking_clientes(db_path=test_db, limit=5)
    assert len(report["data"]) <= 5
    raw = report["raw_rows"]
    if len(raw) > 1:
        # Garante ordenação decrescente por total_gasto
        for i in range(len(raw) - 1):
            assert float(raw[i]["total_gasto"]) >= float(raw[i + 1]["total_gasto"])


def test_get_veiculos_mais_alugados(test_db):
    """Testa a consulta de veículos mais alugados."""
    report = get_veiculos_mais_alugados(db_path=test_db)
    assert len(report["data"]) > 0
    raw = report["raw_rows"]
    for r in raw:
        assert int(r["total_vezes_alugado"]) > 0


def test_get_historico_locacoes(test_db):
    """Testa o histórico geral e o filtro por status de locação."""
    report_geral = get_historico_locacoes(db_path=test_db)
    assert len(report_geral["data"]) > 0

    report_ativas = get_historico_locacoes(db_path=test_db, status_filter="Ativa")
    for row in report_ativas["raw_rows"]:
        assert row["status_locacao"] == "Ativa"


def test_get_resultado_operacional(test_db):
    """Testa a consulta de resultado operacional (receita vs manutenção)."""
    report = get_resultado_operacional(db_path=test_db)
    assert len(report["data"]) > 0
    raw = report["raw_rows"]
    for r in raw:
        assert "resultado_liquido" in r


def test_format_table_formatting():
    """Testa a formatação textual de tabelas."""
    headers = ["ID", "Nome", "Valor"]
    rows = [[1, "Sedã", "R$ 100,00"], [2, "SUV", "R$ 200,00"]]
    table_str = format_table(headers, rows)

    assert "ID" in table_str
    assert "Sedã" in table_str
    assert "SUV" in table_str
    assert "+-" in table_str

    empty_table = format_table(headers, [])
    assert empty_table == "Nenhum registro encontrado."
