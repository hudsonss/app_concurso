from flask import flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from fucntools import wraps
from app import Usuario

@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    # Validação
    if not username or not password or not confirm_password:
      flash("Por favor, preencha todos os campos.", "error")
      return redirect(url_for("register"))

    if password != confirm_password:
      flash("As senhas não coincidem.", "error")
      return redirect(url_for("register"))

    if len(password) < 8:
      flash("A senha deve ter pelo menos 8 caracteres.", "error")
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

# Proteger rotas
def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if "user_id" not in session:
      flash("Faça login para acessar esta página!", "error")
      return redirect(url_for("login"))
    return f(*args, **kwargs)
  return decorated_function

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
    pass

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


