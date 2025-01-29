from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "secret"

db = SQLAlchemy(app)


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


# Criar o banco de dados
with app.app_context():
    print("Banco de dados!")
    db.create_all()
    print("Banco de dados inicializado!")


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

        print(f"Tentativa de login: {username}"
              )  # Debug 1: Verificar se o formulário está enviando os dados

        # Verificar se o usuário existe
        user = Usuario.query.filter_by(username=username).first()
        if not user:
            flash("Nome de usuário ou senha incorretos!", "error")
            print("Usuário não encontrado."
                  )  # Debug 2: O usuário não foi encontrado no banco
            return redirect(url_for("login"))

        # Verificar a senha
        if not check_password_hash(user.password, password):
            flash("Nome de usuário ou senha incorretos!", "error")
            print("Senha incorreta."
                  )  # Debug 3: A senha não corresponde ao hash armazenado
            return redirect(url_for("login"))

        # Configurar a sessão
        session["user_id"] = user.id
        session["username"] = user.username
        flash("Login realizado com sucesso!", "success")
        print(f"Usuário logado com ID: {user.id} e username: {user.username}"
              )  # Debug 4: Verificar se a sessão foi configurada
        return redirect(url_for("listar_concursos"))

    return render_template("login.html")


# Rota para logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("Logout efetuado com sucesso!", "success")
    print("logout com sucesso")
    return redirect(url_for("login"))


# Proteger rotas
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login para acessar esta página!", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# Rota para Cadastro de Concursos
@app.route("/", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("concurso_name")
        data = request.form.get("concurso_date")
        banca = request.form.get("concurso_banca")

        if not nome or not data or not banca:
            flash("Todos os campos são obrigatórios.", "error")
            return redirect(url_for("cadastro"))

        # Salvar no banco de dados
        novo_concurso = Concurso(nome=nome, data=data, banca=banca)
        db.session.add(novo_concurso)
        db.session.commit()
        flash(f"Concurso '{nome}' cadastrado com sucesso!", "success")
        return redirect(url_for("listar_concursos"))

    return render_template("index.html")


#Rota para listagem dos concursos
@app.route("/concursos", methods=["GET"])
@login_required
def listar_concursos():
    search = request.args.get('search')  # Captura o termo de pesquisa
    page = request.args.get('page', 1, type=int)  # Captura o número da página (default é 1)

    if search:
        # Realiza o filtro de busca
        concursos = Concurso.query.filter(
            (Concurso.nome.like(f"%{search}%")) | 
            (Concurso.banca.like(f"%{search}%"))
        ).paginate(page=page, per_page=5)  # Exibe 5 concursos por página
    else:
        concursos = Concurso.query.paginate(page=page, per_page=5)  # Exibe 5 concursos por página

    return render_template("concursos.html", concursos=concursos)
    

@app.route("/delete/<int:id>", methods=["GET", "POST"])
def excluir_concurso(id):
    concurso = Concurso.query.get_or_404(id)
    db.session.delete(concurso)
    db.session.commit()
    flash(f"Concurso '{concurso.nome}' excluído com sucesso!", "success")
    return redirect(url_for("listar_concursos"))


#Rota para edição de concursos
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_concurso(id):
    concurso = Concurso.query.get_or_404(id)

    if request.method == "POST":
        nome = request.form.get("concurso_name")
        data = request.form.get("concurso_date")
        banca = request.form.get("concurso_banca")

        if not nome or not data or not banca:
            flash("Todos os campos são obrigatórios!", "danger")  # Usando "danger" para erro
            return redirect(url_for("editar_concurso", id=id))

        concurso.nome = nome
        concurso.data = data
        concurso.banca = banca
        db.session.commit()
        flash(f"Concurso '{nome}' atualizado com sucesso!", "success")  # Usando "success" para sucesso
        return redirect(url_for("listar_concursos"))

    return render_template("editar.html", concurso=concurso)

if __name__ == "__main__":
    app.run(debug=True)
