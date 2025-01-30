##### config.py #####

"""
Arquivo de configuração da aplicação.
Aqui ficam as variáveis de ambiente, como a conexão com o banco de dados.
"""

class Config:
    SECRET_KEY = 'sua_chave_secreta_aqui'  # Usado para segurança (exemplo: sessões)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'  # Caminho do banco SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Evita warnings desnecessários