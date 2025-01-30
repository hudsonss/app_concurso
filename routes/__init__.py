##### routes/__init__.py #####
"""
Inicializa e registra as rotas da aplicação.
E implementa o @login_required para garantir proteção das rotas.
"""
from .auth import auth_routes
from .concursos import concursos_routes
from .users import users_routes


# Importa e registra as rotas
def init_routes(app):
    app.register_blueprint(auth_routes)
    app.register_blueprint(concursos_routes)
    app.register_blueprint(users_routes)
