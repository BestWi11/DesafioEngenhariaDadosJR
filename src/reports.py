"""Módulo de relatórios e consultas analíticas SQL."""

import os
from typing import Any, Dict, List, Optional
from src.database import get_connection


def format_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Formata dados em uma tabela textual elegante para exibição no terminal."""
    if not rows:
        return "Nenhum registro encontrado."

    # Converte todos os valores para string
    str_rows = [[str(cell) for cell in row] for row in rows]

    # Calcula a largura máxima para cada coluna
    col_widths = [len(h) for h in headers]
    for row in str_rows:
        for idx, cell in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(cell))

    # Cria linhas de separação e cabeçalho
    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_line = "| " + " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths)) + " |"

    body_lines = []
    for row in str_rows:
        line = "| " + " | ".join(f"{c:<{w}}" for c, w in zip(row, col_widths)) + " |"
        body_lines.append(line)

    return "\n".join([sep, header_line, sep] + body_lines + [sep])


def get_faturamento_por_categoria(
    db_path: Optional[os.PathLike | str] = None,
) -> Dict[str, Any]:
    """Consulta analítica: Faturamento, volume de locações e diária média por categoria.

    Utiliza: VIEW vw_faturamento_por_categoria (com JOIN, GROUP BY, SUM, COUNT, AVG).
    """
    sql = """
        SELECT 
            categoria,
            valor_diaria_base,
            total_locacoes,
            faturamento_total,
            ticket_medio_locacao,
            valor_diaria_media
        FROM vw_faturamento_por_categoria;
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        headers = [
            "Categoria",
            "Diária Base (R$)",
            "Total Locações",
            "Faturamento (R$)",
            "Ticket Médio (R$)",
            "Diária Média (R$)",
        ]
        data = [
            [
                r["categoria"],
                f"R$ {r['valor_diaria_base']:.2f}",
                r["total_locacoes"],
                f"R$ {r['faturamento_total']:.2f}",
                f"R$ {r['ticket_medio_locacao']:.2f}",
                f"R$ {r['valor_diaria_media']:.2f}",
            ]
            for r in records
        ]
        raw_rows = [dict(r) for r in records]
        return {
            "title": "Relatório de Faturamento por Categoria de Veículo",
            "headers": headers,
            "data": data,
            "raw_rows": raw_rows,
        }
    finally:
        conn.close()


def get_ranking_clientes(
    db_path: Optional[os.PathLike | str] = None, limit: int = 10
) -> Dict[str, Any]:
    """Consulta analítica: Ranking de clientes por valor total investido.

    Utiliza: VIEW vw_desempenho_clientes (com JOIN, GROUP BY, SUM, COUNT, AVG, ORDER BY).
    """
    sql = """
        SELECT 
            cliente,
            cpf,
            cidade || '/' || estado AS localizacao,
            total_locacoes,
            total_gasto,
            ticket_medio,
            COALESCE(ultima_locacao, 'Nenhuma') AS ultima_locacao
        FROM vw_desempenho_clientes
        LIMIT ?;
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (limit,))
        records = cursor.fetchall()
        headers = [
            "Cliente",
            "CPF",
            "Localização",
            "Locações",
            "Total Gasto (R$)",
            "Ticket Médio (R$)",
            "Última Locação",
        ]
        data = [
            [
                r["cliente"],
                r["cpf"],
                r["localizacao"],
                r["total_locacoes"],
                f"R$ {r['total_gasto']:.2f}",
                f"R$ {r['ticket_medio']:.2f}",
                r["ultima_locacao"],
            ]
            for r in records
        ]
        raw_rows = [dict(r) for r in records]
        return {
            "title": f"Top {limit} Clientes com Maior Volume de Locações",
            "headers": headers,
            "data": data,
            "raw_rows": raw_rows,
        }
    finally:
        conn.close()


def get_veiculos_mais_alugados(
    db_path: Optional[os.PathLike | str] = None,
) -> Dict[str, Any]:
    """Consulta analítica SQL direta com JOIN, WHERE, GROUP BY e SUM/COUNT."""
    sql = """
        SELECT 
            v.id_veiculo,
            v.marca || ' ' || v.modelo AS veiculo,
            v.placa,
            cat.nome AS categoria,
            v.status AS status_atual,
            COUNT(l.id_locacao) AS total_vezes_alugado,
            ROUND(COALESCE(SUM(l.valor_total), 0), 2) AS receita_total_gerada
        FROM veiculos v
        INNER JOIN categorias cat ON v.id_categoria = cat.id_categoria
        LEFT JOIN locacoes l ON v.id_veiculo = l.id_veiculo
        GROUP BY v.id_veiculo, v.marca, v.modelo, v.placa, cat.nome, v.status
        HAVING total_vezes_alugado > 0
        ORDER BY total_vezes_alugado DESC, receita_total_gerada DESC;
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        headers = [
            "ID",
            "Veículo",
            "Placa",
            "Categoria",
            "Status Atual",
            "Qtd. Locações",
            "Receita Gerada (R$)",
        ]
        data = [
            [
                r["id_veiculo"],
                r["veiculo"],
                r["placa"],
                r["categoria"],
                r["status_atual"],
                r["total_vezes_alugado"],
                f"R$ {r['receita_total_gerada']:.2f}",
            ]
            for r in records
        ]
        raw_rows = [dict(r) for r in records]
        return {
            "title": "Desempenho da Frota - Veículos Mais Alugados",
            "headers": headers,
            "data": data,
            "raw_rows": raw_rows,
        }
    finally:
        conn.close()


def get_historico_locacoes(
    db_path: Optional[os.PathLike | str] = None,
    status_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """Consulta detalhada de locações com filtros e múltiplos JOINs."""
    base_sql = """
        SELECT 
            id_locacao,
            cliente,
            veiculo,
            placa,
            categoria,
            data_locacao,
            data_devolucao_prevista,
            ROUND(valor_total, 2) AS valor_total,
            status_locacao
        FROM vw_historico_locacoes_detalhado
    """
    params = []
    if status_filter:
        base_sql += " WHERE status_locacao = ?"
        params.append(status_filter)

    base_sql += " LIMIT 20;"

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(base_sql, tuple(params))
        records = cursor.fetchall()
        headers = [
            "ID",
            "Cliente",
            "Veículo",
            "Placa",
            "Categoria",
            "Início",
            "Prev. Devolução",
            "Valor Total (R$)",
            "Status",
        ]
        data = [
            [
                r["id_locacao"],
                r["cliente"],
                r["veiculo"],
                r["placa"],
                r["categoria"],
                r["data_locacao"],
                r["data_devolucao_prevista"],
                f"R$ {r['valor_total']:.2f}",
                r["status_locacao"],
            ]
            for r in records
        ]
        raw_rows = [dict(r) for r in records]
        title_suffix = f" (Status: {status_filter})" if status_filter else ""
        return {
            "title": f"Histórico de Locações Recentes{title_suffix}",
            "headers": headers,
            "data": data,
            "raw_rows": raw_rows,
        }
    finally:
        conn.close()


def get_resultado_operacional(
    db_path: Optional[os.PathLike | str] = None,
) -> Dict[str, Any]:
    """Consulta analítica de resultado financeiro líquido por veículo (Receita vs Manutenção).

    Utiliza: VIEW vw_resultado_por_veiculo.
    """
    sql = """
        SELECT 
            veiculo,
            placa,
            categoria,
            status_atual,
            total_locacoes,
            faturamento_gerado,
            custo_manutencao,
            resultado_liquido
        FROM vw_resultado_por_veiculo;
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        headers = [
            "Veículo",
            "Placa",
            "Categoria",
            "Status",
            "Locações",
            "Receita (R$)",
            "Manutenção (R$)",
            "Resultado Líquido (R$)",
        ]
        data = [
            [
                r["veiculo"],
                r["placa"],
                r["categoria"],
                r["status_atual"],
                r["total_locacoes"],
                f"R$ {r['faturamento_gerado']:.2f}",
                f"R$ {r['custo_manutencao']:.2f}",
                f"R$ {r['resultado_liquido']:.2f}",
            ]
            for r in records
        ]
        raw_rows = [dict(r) for r in records]
        return {
            "title": "Resultado Operacional por Veículo (Receita vs Manutenção)",
            "headers": headers,
            "data": data,
            "raw_rows": raw_rows,
        }
    finally:
        conn.close()
