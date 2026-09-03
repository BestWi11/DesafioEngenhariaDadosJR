"""Módulo de serviços de negócio e operações de cadastro (INSERT / UPDATE)."""

from datetime import datetime
import os
from typing import Any, Dict, List, Optional
from src.database import get_db_cursor


def cadastrar_cliente(
    nome: str,
    cpf: str,
    cnh: str,
    telefone: str,
    email: str,
    cidade: str,
    estado: str,
    db_path: Optional[os.PathLike | str] = None,
) -> int:
    """Cadastra um novo cliente no banco de dados."""
    sql = """
        INSERT INTO clientes (nome, cpf, cnh, telefone, email, cidade, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    with get_db_cursor(db_path) as (_, cursor):
        cursor.execute(sql, (nome.strip(), cpf.strip(), cnh.strip(), telefone.strip(), email.strip(), cidade.strip(), estado.strip().upper()))
        cliente_id = cursor.lastrowid
    return cliente_id


def cadastrar_veiculo(
    id_categoria: int,
    marca: str,
    modelo: str,
    ano: int,
    placa: str,
    cor: str,
    quilometragem: int = 0,
    db_path: Optional[os.PathLike | str] = None,
) -> int:
    """Cadastra um novo veículo no banco de dados."""
    sql = """
        INSERT INTO veiculos (id_categoria, marca, modelo, ano, placa, cor, status, quilometragem)
        VALUES (?, ?, ?, ?, ?, ?, 'Disponivel', ?);
    """
    with get_db_cursor(db_path) as (_, cursor):
        cursor.execute(
            sql,
            (
                id_categoria,
                marca.strip(),
                modelo.strip(),
                ano,
                placa.strip().upper(),
                cor.strip(),
                quilometragem,
            ),
        )
        veiculo_id = cursor.lastrowid
    return veiculo_id


def registrar_locacao(
    id_cliente: int,
    id_veiculo: int,
    data_locacao_str: str,
    data_devolucao_prevista_str: str,
    db_path: Optional[os.PathLike | str] = None,
) -> int:
    """Registra uma nova locação com transação atômica.

    Valida a existência do cliente, disponibilidade do veículo e atualiza seu status para 'Alugado'.
    """
    d_loc = datetime.strptime(data_locacao_str, "%Y-%m-%d")
    d_prev = datetime.strptime(data_devolucao_prevista_str, "%Y-%m-%d")
    dias = (d_prev - d_loc).days
    if dias <= 0:
        raise ValueError("A data de devolução prevista deve ser posterior à data de locação.")

    with get_db_cursor(db_path) as (_, cursor):
        # 1. Verifica cliente
        cursor.execute("SELECT id_cliente, nome FROM clientes WHERE id_cliente = ?", (id_cliente,))
        cliente = cursor.fetchone()
        if not cliente:
            raise ValueError(f"Cliente com ID {id_cliente} não encontrado.")

        # 2. Verifica veículo e obtém diária da categoria
        cursor.execute(
            """
            SELECT v.id_veiculo, v.status, c.valor_diaria_base
            FROM veiculos v
            INNER JOIN categorias c ON v.id_categoria = c.id_categoria
            WHERE v.id_veiculo = ?
            """,
            (id_veiculo,),
        )
        veiculo = cursor.fetchone()
        if not veiculo:
            raise ValueError(f"Veículo com ID {id_veiculo} não encontrado.")

        if veiculo["status"] != "Disponivel":
            raise ValueError(f"Veículo ID {id_veiculo} não está disponível (Status atual: {veiculo['status']}).")

        valor_diaria = float(veiculo["valor_diaria_base"])
        valor_total = valor_diaria * dias

        # 3. Insere a locação
        insert_sql = """
            INSERT INTO locacoes (id_cliente, id_veiculo, data_locacao, data_devolucao_prevista, valor_diaria, valor_total, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Ativa');
        """
        cursor.execute(
            insert_sql,
            (
                id_cliente,
                id_veiculo,
                data_locacao_str,
                data_devolucao_prevista_str,
                valor_diaria,
                valor_total,
            ),
        )
        locacao_id = cursor.lastrowid

        # 4. Atualiza o status do veículo para 'Alugado'
        cursor.execute("UPDATE veiculos SET status = 'Alugado' WHERE id_veiculo = ?", (id_veiculo,))

    return locacao_id


def finalizar_locacao(
    id_locacao: int,
    data_devolucao_real_str: Optional[str] = None,
    nova_quilometragem: Optional[int] = None,
    db_path: Optional[os.PathLike | str] = None,
) -> None:
    """Finaliza uma locação ativa e libera o veículo de volta para 'Disponivel'."""
    data_real = data_devolucao_real_str or datetime.now().strftime("%Y-%m-%d")

    with get_db_cursor(db_path) as (_, cursor):
        cursor.execute("SELECT id_locacao, id_veiculo, status FROM locacoes WHERE id_locacao = ?", (id_locacao,))
        locacao = cursor.fetchone()
        if not locacao:
            raise ValueError(f"Locação com ID {id_locacao} não encontrada.")
        if locacao["status"] != "Ativa":
            raise ValueError(f"Locação ID {id_locacao} já está {locacao['status']}.")

        id_veiculo = locacao["id_veiculo"]

        # Atualiza a locação
        cursor.execute(
            "UPDATE locacoes SET data_devolucao_real = ?, status = 'Finalizada' WHERE id_locacao = ?",
            (data_real, id_locacao),
        )

        # Libera o veículo
        if nova_quilometragem is not None:
            cursor.execute(
                "UPDATE veiculos SET status = 'Disponivel', quilometragem = ? WHERE id_veiculo = ?",
                (nova_quilometragem, id_veiculo),
            )
        else:
            cursor.execute("UPDATE veiculos SET status = 'Disponivel' WHERE id_veiculo = ?", (id_veiculo,))


def listar_categorias(db_path: Optional[os.PathLike | str] = None) -> List[Dict[str, Any]]:
    """Retorna a lista de categorias cadastradas."""
    with get_db_cursor(db_path) as (_, cursor):
        cursor.execute("SELECT id_categoria, nome, valor_diaria_base FROM categorias ORDER BY id_categoria")
        return [dict(row) for row in cursor.fetchall()]


def listar_veiculos_disponiveis(db_path: Optional[os.PathLike | str] = None) -> List[Dict[str, Any]]:
    """Retorna os veículos que estão disponíveis para locação."""
    with get_db_cursor(db_path) as (_, cursor):
        cursor.execute(
            """
            SELECT v.id_veiculo, v.marca, v.modelo, v.placa, c.nome AS categoria, c.valor_diaria_base
            FROM veiculos v
            INNER JOIN categorias c ON v.id_categoria = c.id_categoria
            WHERE v.status = 'Disponivel'
            ORDER BY c.valor_diaria_base, v.marca;
            """
        )
        return [dict(row) for row in cursor.fetchall()]


def listar_clientes(db_path: Optional[os.PathLike | str] = None) -> List[Dict[str, Any]]:
    """Retorna os clientes cadastrados."""
    with get_db_cursor(db_path) as (_, cursor):
        cursor.execute("SELECT id_cliente, nome, cpf, email, cidade, estado FROM clientes ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]
