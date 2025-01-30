from flask import Flask
from config import Config
from extensions import db  # Importa db de extensions.py
from routes import init_routes

app = Flask(__name__)
app.config.from_object(Config)  # Carrega as configurações

# Inicializa o banco de dados
db.init_app(app)

# Registra as rotas
init_routes(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)
