from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_PERMANENT"] = True
app.permanent_session_lifetime = timedelta(days=1)  # Sessão válida por 1 dia
app.secret_key = "secret"

db = SQLAlchemy(app)

#####################################################################
#                    Modelos
#####################################################################

# Modelo da tabela de Users
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# Modelo da tabela de concursos
class Concurso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(10), nullable=False)
    banca = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)


# Criar o banco de dados
with app.app_context():
    print("Banco de dados!")
    db.create_all()
    print("Banco de dados inicializado!")


# Proteger rotas
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login para acessar esta página!", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function

#####################################################################
#                    Home
#####################################################################
@app.route("/")
def home():
    return render_template("index.html")  # Exibe a nova página inicial

#####################################################################
#                    Usuários
#####################################################################
# Rota para registro de usuarios
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validação simples
        if not username or not password or not confirm_password:
            flash("Por favor, preencha todos os campos.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for("register"))

        # Verificar se o usuário já existe
        existing_user = Usuario.query.filter_by(username=username).first()
        if existing_user:
            flash("Usuário já existe.", "error")
            return redirect(url_for("register"))

        # Criar novo usuário com senha hash
        hashed_password = generate_password_hash(password)
        novo_usuario = Usuario(username=username, password=hashed_password)
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Registro realizado com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# Rota para login de usuarios
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Verificar se o usuário existe
        user = Usuario.query.filter_by(username=username).first()
        if not user:
            flash("Nome de usuário ou senha incorretos!", "error")
            return redirect(url_for("login"))

        # Verificar a senha
        if not check_password_hash(user.password, password):
            flash("Nome de usuário ou senha incorretos!", "error")
            return redirect(url_for("login"))

        # Configurar a sessão
        session.permanent = True  # Define que a sessão deve ser mantida
        session["user_id"] = user.id
        session["username"] = user.username
        flash("Login realizado com sucesso!", "success")
        
        return redirect(url_for("listar_concursos"))

    return render_template("login.html")


# Rota para logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("Logout efetuado com sucesso!", "success")
    print("logout com sucesso")
    return redirect(url_for("home"))


# Perfil de usuário
@app.route("/perfil")
@login_required
def perfil():
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id)

    return render_template("perfil.html", usuario=usuario)


# Rota para alterar senha
@app.route("/alterar_senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id)

    senha_atual = request.form.get("senha_atual")
    nova_senha = request.form.get("nova_senha")
    confirmar_senha = request.form.get("confirmar_senha")

    #verificar se a senha atual está correta
    if not check_password_hash(usuario.password, senha_atual):
        flash("Senha atual incorreta!", "error")
        return redirect(url_for("perfil"))

    #verificar se a nova senha é válida
    if nova_senha != confirmar_senha:
        flash("As senhas não coincidem!", "error")
        return redirect(url_for("perfil"))

    #atualizar a senha do usuário
    usuario.password = generate_password_hash(nova_senha)
    db.session.commit()

    flash("Senha alterada com sucesso!", "success")
    return redirect(url_for("perfil"))



#####################################################################
#                    Concursos
#####################################################################


# Rota para Cadastro de Concursos
@app.route("/cadastrar_concurso", methods=["GET", "POST"])
@login_required
def cadastro():
    if request.method == "POST":
        nome = request.form.get("concurso_name")
        data = request.form.get("concurso_date")
        banca = request.form.get("concurso_banca")
        user_id = session.get("user_id")

        if not nome or not data or not banca:
            flash("Todos os campos são obrigatórios.", "error")
            return redirect(url_for("cadastro"))

        # Salvar no banco de dados
        novo_concurso = Concurso(nome=nome, data=data, banca=banca, user_id=user_id)
        db.session.add(novo_concurso)
        db.session.commit()
        flash(f"Concurso '{nome}' cadastrado com sucesso!", "success")
        return redirect(url_for("listar_concursos"))

    return render_template("cadastrar_concurso.html")

# Rota para listagem dos concursos
@app.route("/concursos", methods=["GET"])
@login_required
def listar_concursos():
    user_id = session.get("user_id")
    search = request.args.get('search')  # Captura o termo de pesquisa
    page = request.args.get(
        'page', 1, type=int)  # Captura o número da página (default é 1)

    if search:
        # Realiza o filtro de busca
        concursos = Concurso.query.filter(
            (Concurso.user_id == user_id) &
            (Concurso.nome.like(f"%{search}%")) | (Concurso.banca.like(f"%{search}%"))).paginate(
                page=page, per_page=5)  # Exibe 5 concursos por página
    else:
        concursos = Concurso.query.filter_by(user_id=user_id).paginate(page=page, per_page=5)  # Exibe 5 concursos por página

    return render_template("concursos.html", concursos=concursos)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def excluir_concurso(id):
    concurso = Concurso.query.get_or_404(id)
    db.session.delete(concurso)
    db.session.commit()
    flash(f"Concurso '{concurso.nome}' excluído com sucesso!", "success")
    return redirect(url_for("listar_concursos"))


# Rota para edição de concursos
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_concurso(id):
    concurso = Concurso.query.get_or_404(id)

    if request.method == "POST":
        nome = request.form.get("concurso_name")
        data = request.form.get("concurso_date")
        banca = request.form.get("concurso_banca")

        if not nome or not data or not banca:
            flash("Todos os campos são obrigatórios!",
                  "danger")  # Usando "danger" para erro
            return redirect(url_for("editar_concurso", id=id))

        concurso.nome = nome
        concurso.data = data
        concurso.banca = banca
        db.session.commit()
        flash(f"Concurso '{nome}' atualizado com sucesso!",
              "success")  # Usando "success" para sucesso
        return redirect(url_for("listar_concursos"))

    return render_template("editar.html", concurso=concurso)


@app.route("/debug_sessao")
def debug_sessao():
    print(f"Sessão atual: {session}")  # Exibir a sessão no terminal
    return f"Sessão: {session}"


if __name__ == "__main__":
    app.run(debug=True)
