"""Interface de linha de comando (CLI) com menus interativos para a Locadora de Veículos."""

import os
import sys
from typing import Optional
from src.database import DEFAULT_DB_PATH, init_db
from src.export import (
    export_to_csv,
    gerar_grafico_faturamento_por_categoria,
    gerar_grafico_resultado_operacional,
)
from src.reports import (
    format_table,
    get_faturamento_por_categoria,
    get_historico_locacoes,
    get_ranking_clientes,
    get_resultado_operacional,
    get_veiculos_mais_alugados,
)
from src.services import (
    cadastrar_cliente,
    cadastrar_veiculo,
    finalizar_locacao,
    listar_categorias,
    listar_clientes,
    listar_veiculos_disponiveis,
    registrar_locacao,
)


def clear_screen() -> None:
    """Limpa a tela do terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title: str) -> None:
    """Exibe um cabeçalho estilizado."""
    line = "=" * 70
    print(f"\n{line}")
    print(f"  🚗 LOCADORA DE VEÍCULOS ANALYTICS - {title.upper()}")
    print(f"{line}\n")


def menu_relatorios(db_path: Optional[os.PathLike | str] = None) -> None:
    """Submenu de Relatórios Analíticos."""
    while True:
        print_header("Relatórios Analíticos e Indicadores")
        print(" [1] 📊 Faturamento e Diárias por Categoria")
        print(" [2] 🏆 Ranking de Clientes (Top Clientes)")
        print(" [3] 🚘 Desempenho da Frota (Veículos Mais Alugados)")
        print(" [4] 📋 Histórico Geral de Locações (Últimas 20)")
        print(" [5] 🟢 Locações Ativas no Momento")
        print(" [6] 💰 Resultado Operacional por Veículo (Receita vs Manutenção)")
        print(" [0] ⬅️  Voltar ao Menu Principal")

        opcao = input("\n👉 Escolha uma opção de relatório: ").strip()

        if opcao == "0":
            break

        try:
            report_data = None
            if opcao == "1":
                report_data = get_faturamento_por_categoria(db_path)
            elif opcao == "2":
                limite = input("Quantidade de clientes a exibir (padrão 10): ").strip()
                n = int(limite) if limite.isdigit() else 10
                report_data = get_ranking_clientes(db_path, limit=n)
            elif opcao == "3":
                report_data = get_veiculos_mais_alugados(db_path)
            elif opcao == "4":
                report_data = get_historico_locacoes(db_path)
            elif opcao == "5":
                report_data = get_historico_locacoes(db_path, status_filter="Ativa")
            elif opcao == "6":
                report_data = get_resultado_operacional(db_path)
            else:
                print("\n❌ Opção inválida! Tente novamente.")
                input("\nPressione [Enter] para continuar...")
                continue

            if report_data:
                print(f"\n=== {report_data['title']} ===")
                print(format_table(report_data["headers"], report_data["data"]))

                salvar = input("\nDeseja exportar este relatório para CSV? (s/N): ").strip().lower()
                if salvar in ("s", "sim", "y", "yes"):
                    nome_arquivo = input("Nome do arquivo (ex: relatorio.csv): ").strip() or "relatorio.csv"
                    export_to_csv(report_data["headers"], report_data["data"], nome_arquivo)

        except Exception as err:
            print(f"\n❌ Ocorreu um erro ao gerar o relatório: {err}")

        input("\nPressione [Enter] para continuar...")


def menu_cadastros(db_path: Optional[os.PathLike | str] = None) -> None:
    """Submenu de Operações e Cadastros (INSERT / UPDATE)."""
    while True:
        print_header("Operações e Cadastros")
        print(" [1] 👤 Cadastrar Novo Cliente")
        print(" [2] 🚙 Cadastrar Novo Veículo na Frota")
        print(" [3] 📝 Registrar Nova Locação")
        print(" [4] 🏁 Finalizar / Devolver Locação")
        print(" [0] ⬅️  Voltar ao Menu Principal")

        opcao = input("\n👉 Escolha uma opção: ").strip()

        if opcao == "0":
            break

        try:
            if opcao == "1":
                print("\n--- Cadastro de Cliente ---")
                nome = input("Nome Completo: ").strip()
                cpf = input("CPF (ex: 123.456.789-00): ").strip()
                cnh = input("CNH: ").strip()
                telefone = input("Telefone: ").strip()
                email = input("E-mail: ").strip()
                cidade = input("Cidade: ").strip()
                estado = input("Estado (UF, ex: SP): ").strip()

                if not (nome and cpf and cnh and email):
                    print("❌ Campos obrigatórios não preenchidos!")
                else:
                    cid = cadastrar_cliente(nome, cpf, cnh, telefone, email, cidade, estado, db_path)
                    print(f"✅ Cliente cadastrado com sucesso! ID gerado: {cid}")

            elif opcao == "2":
                print("\n--- Cadastro de Veículo ---")
                categorias = listar_categorias(db_path)
                print("\nCategorias disponíveis:")
                for cat in categorias:
                    print(f"  [{cat['id_categoria']}] {cat['nome']} - Diária: R$ {cat['valor_diaria_base']:.2f}")

                id_cat = int(input("\nID da Categoria: ").strip())
                marca = input("Marca (ex: Toyota): ").strip()
                modelo = input("Modelo (ex: Yaris 1.5): ").strip()
                ano = int(input("Ano (ex: 2024): ").strip())
                placa = input("Placa (ex: ABC1D23): ").strip()
                cor = input("Cor: ").strip()
                km = int(input("Quilometragem inicial (ex: 0): ").strip() or 0)

                vid = cadastrar_veiculo(id_cat, marca, modelo, ano, placa, cor, km, db_path)
                print(f"✅ Veículo cadastrado com sucesso! ID gerado: {vid}")

            elif opcao == "3":
                print("\n--- Nova Locação ---")
                veiculos_disp = listar_veiculos_disponiveis(db_path)
                if not veiculos_disp:
                    print("⚠️ Nenhum veículo disponível para locação no momento.")
                else:
                    print("\nVeículos disponíveis:")
                    for v in veiculos_disp:
                        print(f"  [{v['id_veiculo']}] {v['marca']} {v['modelo']} ({v['placa']}) - {v['categoria']} (R$ {v['valor_diaria_base']:.2f}/dia)")

                    clientes = listar_clientes(db_path)
                    print("\nClientes recentes:")
                    for c in clientes[:5]:
                        print(f"  [{c['id_cliente']}] {c['nome']} (CPF: {c['cpf']})")

                    id_cli = int(input("\nID do Cliente: ").strip())
                    id_veic = int(input("ID do Veículo: ").strip())
                    dt_loc = input("Data de Início (YYYY-MM-DD): ").strip()
                    dt_prev = input("Data de Devolução Prevista (YYYY-MM-DD): ").strip()

                    lid = registrar_locacao(id_cli, id_veic, dt_loc, dt_prev, db_path)
                    print(f"✅ Locação registrada com sucesso! ID gerado: {lid}")

            elif opcao == "4":
                print("\n--- Devolução de Locação ---")
                ativas = get_historico_locacoes(db_path, status_filter="Ativa")
                if not ativas["data"]:
                    print("⚠️ Nenhuma locação ativa no momento.")
                else:
                    print(format_table(ativas["headers"], ativas["data"]))
                    id_loc = int(input("\nID da Locação a finalizar: ").strip())
                    dt_real = input("Data de Devolução Real (YYYY-MM-DD, vazio para hoje): ").strip() or None
                    km_fim_str = input("Nova quilometragem do veículo (opcional): ").strip()
                    km_fim = int(km_fim_str) if km_fim_str.isdigit() else None

                    finalizar_locacao(id_loc, dt_real, km_fim, db_path)
                    print(f"✅ Locação ID {id_loc} finalizada e veículo liberado!")

            else:
                print("\n❌ Opção inválida!")

        except ValueError as val_err:
            print(f"\n⚠️ Validação de Dados: {val_err}")
        except Exception as err:
            print(f"\n❌ Erro na operação: {err}")

        input("\nPressione [Enter] para continuar...")


def menu_graficos(db_path: Optional[os.PathLike | str] = None) -> None:
    """Submenu para geração de gráficos analíticos."""
    while True:
        print_header("Visualização de Dados e Gráficos (Matplotlib)")
        print(" [1] 📈 Gerar Gráfico de Faturamento por Categoria")
        print(" [2] 📊 Gerar Gráfico de Receita vs Custos de Manutenção")
        print(" [0] ⬅️  Voltar ao Menu Principal")

        opcao = input("\n👉 Escolha um gráfico: ").strip()

        if opcao == "0":
            break

        try:
            if opcao == "1":
                out = gerar_grafico_faturamento_por_categoria(db_path)
                if out:
                    print(f"\n🎉 Gráfico salvo com sucesso em: {out}")
            elif opcao == "2":
                out = gerar_grafico_resultado_operacional(db_path)
                if out:
                    print(f"\n🎉 Gráfico salvo com sucesso em: {out}")
            else:
                print("\n❌ Opção inválida!")

        except Exception as err:
            print(f"\n❌ Erro ao gerar gráfico: {err}")

        input("\nPressione [Enter] para continuar...")


def main_menu(db_path: Optional[os.PathLike | str] = None) -> None:
    """Menu Principal da Aplicação."""
    # Garante que o banco existe antes de iniciar o loop
    try:
        if not (DEFAULT_DB_PATH.exists() if db_path is None else os.path.exists(str(db_path))):
            print("[INFO] Banco de dados não encontrado. Inicializando pela primeira vez...")
            init_db(db_path=db_path, populate_seed=True)
    except Exception as err:
        print(f"[ALERTA] Falha na inicialização inicial do banco: {err}")

    while True:
        clear_screen()
        print_header("Painel Principal de Gestão e Análise")
        print(" [1] 📊 Consultar Relatórios Analíticos (SQL)")
        print(" [2] 📝 Cadastros e Operações (INSERT/UPDATE)")
        print(" [3] 📈 Gerar Gráficos Visuais (Matplotlib)")
        print(" [4] 🔄 Reinicializar / Resetar Banco com Dados de Exemplo")
        print(" [0] ❌ Sair da Aplicação")

        opcao = input("\n👉 Selecione uma opção: ").strip()

        if opcao == "1":
            menu_relatorios(db_path)
        elif opcao == "2":
            menu_cadastros(db_path)
        elif opcao == "3":
            menu_graficos(db_path)
        elif opcao == "4":
            confirma = input("\n⚠️ Deseja resetar o banco e restaurar dados iniciais? (s/N): ").strip().lower()
            if confirma in ("s", "sim", "y", "yes"):
                try:
                    init_db(db_path=db_path, populate_seed=True, reset=True)
                    print("\n✅ Banco de dados reinicializado com sucesso!")
                except Exception as err:
                    print(f"\n❌ Erro ao reinicializar banco: {err}")
                input("\nPressione [Enter] para continuar...")
        elif opcao == "0":
            print("\n👋 Encerrando aplicação Locadora de Veículos Analytics. Até logo!")
            sys.exit(0)
        else:
            print("\n❌ Opção inválida! Escolha um número válido do menu.")
            input("\nPressione [Enter] para continuar...")
