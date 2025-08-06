"""
Configuração para desenvolvimento local
Este arquivo carrega o .env apenas quando executando localmente
"""
import os
from dotenv import load_dotenv

def load_local_env():
    """Carrega variáveis de ambiente do .env para desenvolvimento local"""
    if os.path.exists('.env'):
        load_dotenv()
        print("Variáveis de ambiente carregadas do arquivo .env (desenvolvimento local)")
    else:
        print("Arquivo .env não encontrado - usando variáveis de ambiente do sistema")
