#!/usr/bin/env python3
"""
Ponto de entrada principal para Qodo PDV
"""

from src.Main import Server


def main():
    """Função principal para executar o servidor"""
    print('🚀 Iniciando Qodo PDV Server...')
    server = Server()
    server.run()


if __name__ == '__main__':
    main()
