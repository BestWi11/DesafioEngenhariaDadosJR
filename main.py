#!/usr/bin/env python3
"""Ponto de entrada principal da aplicação Locadora de Veículos Analytics."""

import sys
from src.menu import main_menu

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[INFO] Execução interrompida pelo usuário (Ctrl+C). Saindo...")
        sys.exit(0)
