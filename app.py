from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "secret"

db = SQLAlchemy(app)

# Modelo da tabela
class Concurso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(10), nullable=False)
    banca = db.Column(db.String(100), nullable=False)


# Criar o banco de dados
with app.app_context():
    db.create_all()


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
@app.route("/concursos", methods= ["GET"])
def listar_concursos():
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    if search:
        concursos = Concurso.query.filter(
            (Concurso.nome.like(f"%{search}%")) |
            (Concurso.banca.like(f"%{search}%"))
        ).paginate(page=page, per_page=5)
    else:
        concursos = Concurso.query.paginate(page=page, per_page=5)

    return render_template("concursos.html", concursos=concursos)

#Rota para exclusão de concursos
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
            flash("Todos os campos são obrigatórios.", "error")
            return redirect(url_for("editar_concurso", id=id))

        concurso.nome = nome
        concurso.data = data
        concurso.banca = banca
        db.session.commit()
        flash(f"Concurso '{nome}' atualizado com sucesso!", "success")
        return redirect(url_for("listar_concursos"))

if __name__ == "__main__":
    app.run(debug=True)
