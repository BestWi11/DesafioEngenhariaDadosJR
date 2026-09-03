"""Módulo de conexão e gerenciamento do banco de dados SQLite."""

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
from typing import Generator, Optional, Tuple

# Caminhos padrão do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "locadora.db"
SQL_DIR = BASE_DIR / "sql"


def get_connection(db_path: Optional[os.PathLike | str] = None) -> sqlite3.Connection:
    """Cria e retorna uma conexão configurada com o banco de dados SQLite.

    Args:
        db_path: Caminho opcional para o arquivo do banco de dados.

    Returns:
        sqlite3.Connection: Conexão ativa com o banco.

    Raises:
        sqlite3.Error: Se ocorrer erro ao conectar ou configurar o banco.
    """
    path = str(db_path) if db_path is not None else str(DEFAULT_DB_PATH)

    # Garante que a pasta pai exista se for arquivo físico
    if path != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        # Habilita suporte a chaves estrangeiras no SQLite
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as err:
        print(f"[ERRO DE CONEXAO] Falha ao conectar ao banco de dados '{path}': {err}")
        raise


@contextmanager
def get_db_cursor(
    db_path: Optional[os.PathLike | str] = None,
) -> Generator[Tuple[sqlite3.Connection, sqlite3.Cursor], None, None]:
    """Gerenciador de contexto para execução segura de operações com commit e rollback automáticos.

    Yields:
        Tuple[sqlite3.Connection, sqlite3.Cursor]: Par de conexão e cursor.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        yield conn, cursor
        conn.commit()
    except Exception as err:
        conn.rollback()
        print(f"[ERRO DE TRANSACAO] Operacao cancelada. Rollback executado: {err}")
        raise
    finally:
        cursor.close()
        conn.close()


def execute_sql_file(
    file_path: Path, conn: Optional[sqlite3.Connection] = None, db_path: Optional[str] = None
) -> None:
    """Executa um arquivo de script SQL completo.

    Args:
        file_path: Caminho do arquivo .sql a ser executado.
        conn: Conexão opcional existente.
        db_path: Caminho opcional do banco para criar nova conexão.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo SQL nao encontrado: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        script = file.read()

    if conn is not None:
        conn.executescript(script)
    else:
        with get_db_cursor(db_path) as (connection, _):
            connection.executescript(script)


def init_db(
    db_path: Optional[os.PathLike | str] = None,
    populate_seed: bool = True,
    reset: bool = False,
) -> None:
    """Inicializa o banco de dados criando o esquema, views e dados iniciais.

    Args:
        db_path: Caminho do banco.
        populate_seed: Se True, insere os dados de exemplo do seed.sql.
        reset: Se True, remove o arquivo existente antes de recriar.
    """
    target_path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH

    if reset and target_path != Path(":memory:") and target_path.exists():
        try:
            target_path.unlink()
            print(f"[INFO] Banco de dados anterior removido em: {target_path}")
        except OSError as e:
            print(f"[AVISO] Nao foi possivel remover banco anterior: {e}")

    try:
        conn = get_connection(target_path)
        try:
            schema_file = SQL_DIR / "schema.sql"
            views_file = SQL_DIR / "views.sql"
            seed_file = SQL_DIR / "seed.sql"

            execute_sql_file(schema_file, conn=conn)
            execute_sql_file(views_file, conn=conn)

            if populate_seed:
                execute_sql_file(seed_file, conn=conn)

            conn.commit()
            print("[SUCESSO] Banco de dados inicializado com sucesso!")
        finally:
            conn.close()
    except Exception as err:
        print(f"[ERRO NA INICIALIZACAO] Falha ao inicializar o banco: {err}")
        raise
