"""Módulo de exportação de dados para CSV e geração de gráficos com matplotlib."""

import csv
import os
from pathlib import Path
from typing import Any, List, Optional
from src.database import BASE_DIR

EXPORTS_DIR = BASE_DIR / "exports"


def export_to_csv(headers: List[str], data: List[List[Any]], filename: str) -> Path:
    """Exporta uma lista de cabeçalhos e linhas para um arquivo CSV no diretório exports/."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    if not filename.endswith(".csv"):
        filename += ".csv"

    filepath = EXPORTS_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(headers)
        writer.writerows(data)

    print(f"[EXPORTAÇÃO] Arquivo CSV salvo com sucesso em: {filepath}")
    return filepath


def gerar_grafico_faturamento_por_categoria(
    db_path: Optional[os.PathLike | str] = None,
    output_filename: str = "grafico_faturamento_categoria.png",
) -> Optional[Path]:
    """Gera um gráfico de barras comparativo do faturamento por categoria de veículo."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # Backend não interativo
        import matplotlib.pyplot as plt
    except ImportError:
        print("[AVISO] matplotlib não está instalado. Instale com 'pip install matplotlib'.")
        return None

    from src.reports import get_faturamento_por_categoria

    report = get_faturamento_por_categoria(db_path)
    raw = report["raw_rows"]

    if not raw:
        print("[AVISO] Não há dados para gerar o gráfico.")
        return None

    categorias = [r["categoria"] for r in raw]
    faturamentos = [float(r["faturamento_total"]) for r in raw]
    locacoes = [int(r["total_locacoes"]) for r in raw]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    cores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    bars = ax1.bar(categorias, faturamentos, color=cores[:len(categorias)], alpha=0.85, edgecolor="black")

    ax1.set_title("Faturamento e Volume de Locações por Categoria de Veículo", fontsize=14, fontweight="bold", pad=15)
    ax1.set_xlabel("Categoria de Veículo", fontsize=12, labelpad=10)
    ax1.set_ylabel("Faturamento Total (R$)", fontsize=12, color="#1f77b4")
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # Rótulos nas barras
    for bar, loc in zip(bars, locacoes):
        height = bar.get_height()
        ax1.annotate(
            f"R$ {height:,.2f}\n({loc} locações)",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="semibold",
        )

    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()

    os.makedirs(EXPORTS_DIR, exist_ok=True)
    out_path = EXPORTS_DIR / output_filename
    plt.savefig(out_path, dpi=300)
    plt.close()

    print(f"[GRÁFICO] Gráfico gerado e salvo com sucesso em: {out_path}")
    return out_path


def gerar_grafico_resultado_operacional(
    db_path: Optional[os.PathLike | str] = None,
    output_filename: str = "grafico_resultado_operacional.png",
) -> Optional[Path]:
    """Gera um gráfico comparativo de Receita vs Custo de Manutenção por veículo."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[AVISO] matplotlib não está instalado. Instale com 'pip install matplotlib'.")
        return None

    from src.reports import get_resultado_operacional

    report = get_resultado_operacional(db_path)
    raw = [r for r in report["raw_rows"] if float(r["faturamento_gerado"]) > 0 or float(r["custo_manutencao"]) > 0]

    if not raw:
        print("[AVISO] Não há dados suficientes para gerar o gráfico operacional.")
        return None

    veiculos = [f"{r['veiculo']} ({r['placa']})" for r in raw]
    receitas = [float(r["faturamento_gerado"]) for r in raw]
    custos = [float(r["custo_manutencao"]) for r in raw]

    import numpy as np
    x = np.arange(len(veiculos))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, receitas, width, label="Receita Gerada (R$)", color="#2ca02c", alpha=0.85)
    ax.bar(x + width/2, custos, width, label="Custo Manutenção (R$)", color="#d62728", alpha=0.85)

    ax.set_title("Resultado Operacional por Veículo: Receita vs Custo de Manutenção", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Veículo", fontsize=12, labelpad=10)
    ax.set_ylabel("Valor (R$)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(veiculos, rotation=30, ha="right", fontsize=9)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    out_path = EXPORTS_DIR / output_filename
    plt.savefig(out_path, dpi=300)
    plt.close()

    print(f"[GRÁFICO] Gráfico operacional gerado com sucesso em: {out_path}")
    return out_path
