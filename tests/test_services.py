"""Testes automatizados para operações de negócio, cadastro e exportação CSV."""

import os
import pytest
from src.database import init_db
from src.export import export_to_csv
from src.services import (
    cadastrar_cliente,
    cadastrar_veiculo,
    finalizar_locacao,
    listar_categorias,
    listar_veiculos_disponiveis,
    registrar_locacao,
)


@pytest.fixture
def test_db(tmp_path):
    """Cria banco de dados temporário para testes de serviços."""
    db_file = tmp_path / "test_services.db"
    init_db(db_path=db_file, populate_seed=True)
    return db_file


def test_cadastrar_cliente(test_db):
    """Testa o cadastro de um novo cliente."""
    cliente_id = cadastrar_cliente(
        nome="Novo Cliente de Teste",
        cpf="999.888.777-66",
        cnh="98765432100",
        telefone="(11) 91234-5678",
        email="novo.teste@email.com",
        cidade="Campinas",
        estado="SP",
        db_path=test_db,
    )
    assert cliente_id > 0


def test_cadastrar_veiculo(test_db):
    """Testa o cadastro de um novo veículo na frota."""
    veiculo_id = cadastrar_veiculo(
        id_categoria=1,
        marca="Renault",
        modelo="Kwid Zen",
        ano=2024,
        placa="KWD9X99",
        cor="Branco",
        quilometragem=500,
        db_path=test_db,
    )
    assert veiculo_id > 0


def test_registrar_e_finalizar_locacao(test_db):
    """Testa fluxo completo de locação: reserva, alteração de status do veículo e devolução."""
    # 1. Pega um veículo disponível
    disponiveis = listar_veiculos_disponiveis(db_path=test_db)
    assert len(disponiveis) > 0
    veiculo_alvo = disponiveis[0]
    id_veiculo = veiculo_alvo["id_veiculo"]

    # 2. Registra locação para o cliente 1
    locacao_id = registrar_locacao(
        id_cliente=1,
        id_veiculo=id_veiculo,
        data_locacao_str="2024-07-01",
        data_devolucao_prevista_str="2024-07-05",
        db_path=test_db,
    )
    assert locacao_id > 0

    # 3. Tentar alugar novamente o mesmo veículo deve falhar (status 'Alugado')
    with pytest.raises(ValueError, match="não está disponível"):
        registrar_locacao(
            id_cliente=2,
            id_veiculo=id_veiculo,
            data_locacao_str="2024-07-02",
            data_devolucao_prevista_str="2024-07-06",
            db_path=test_db,
        )

    # 4. Finaliza a locação com devolução
    finalizar_locacao(
        id_locacao=locacao_id,
        data_devolucao_real_str="2024-07-05",
        nova_quilometragem=20000,
        db_path=test_db,
    )

    # 5. Veículo deve estar disponível novamente
    disponiveis_depois = [v["id_veiculo"] for v in listar_veiculos_disponiveis(db_path=test_db)]
    assert id_veiculo in disponiveis_depois


def test_registrar_locacao_data_invalida(test_db):
    """Testa erro de validação quando data de devolução é anterior ou igual à data de início."""
    with pytest.raises(ValueError, match="deve ser posterior"):
        registrar_locacao(
            id_cliente=1,
            id_veiculo=1,
            data_locacao_str="2024-07-10",
            data_devolucao_prevista_str="2024-07-05",
            db_path=test_db,
        )


def test_export_to_csv(tmp_path):
    """Testa a exportação de dados para arquivo CSV."""
    headers = ["ID", "Nome", "Total"]
    data = [[1, "Sedã", 1500.0], [2, "SUV", 2300.0]]
    csv_file = export_to_csv(headers, data, "teste_export")

    assert os.path.exists(csv_file)
    with open(csv_file, "r", encoding="utf-8-sig") as f:
        content = f.read()
    assert "ID;Nome;Total" in content
    assert "Sedã;1500.0" in content
