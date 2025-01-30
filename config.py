##### config.py #####

"""
Arquivo de configuração da aplicação.
Aqui ficam as variáveis de ambiente, como a conexão com o banco de dados.
"""
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "uma_chave_secreta_muito_segura"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 86400  # 1 dia em segundos