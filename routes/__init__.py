##### routes/__init__.py #####

"""
Inicializa e registra as rotas da aplicação.
"""

from .auth import auth_bp
from .concursos import concursos_bp

def init_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(concursos_bp)    