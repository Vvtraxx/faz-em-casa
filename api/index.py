"""
Arquivo principal para deploy na Vercel
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app import create_app

# Cria a aplicação Flask
app = create_app()

# Para Vercel, a aplicação precisa estar disponível globalmente
if __name__ == "__main__":
    app.run()
    