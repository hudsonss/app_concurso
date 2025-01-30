from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Concurso
from extensions import db  # Importa db de extensions.py
from functools import wraps
from utils import login_required

concursos_routes = Blueprint("concursos", __name__)

@concursos_routes.route("/")
def home():
    return render_template("index.html")

@concursos_routes.route("/cadastrar_concurso", methods=["GET", "POST"])
@login_required
def cadastro():
    if request.method == "POST":
        nome = request.form.get("concurso_name")
        data = request.form.get("concurso_date")
        banca = request.form.get("concurso_banca")
        user_id = session.get("user_id")

        if not nome or not data or not banca:
            flash("Todos os campos são obrigatórios.", "error")
            return redirect(url_for("concursos.cadastro"))

        novo_concurso = Concurso(nome=nome, data=data, banca=banca, user_id=user_id)
        db.session.add(novo_concurso)
        db.session.commit()
        flash(f"Concurso '{nome}' cadastrado com sucesso!", "success")
        return redirect(url_for("concursos.listar_concursos"))

    return render_template("cadastrar_concurso.html")

@concursos_routes.route("/concursos")
@login_required
def listar_concursos():
    user_id = session.get("user_id")
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)

    if search:
        concursos = Concurso.query.filter(
            (Concurso.user_id == user_id) &
            (Concurso.nome.like(f"%{search}%")) | (Concurso.banca.like(f"%{search}%"))).paginate(
                page=page, per_page=5)
    else:
        concursos = Concurso.query.filter_by(user_id=user_id).paginate(page=page, per_page=5)

    return render_template("concursos.html", concursos=concursos)

@concursos_routes.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def excluir_concurso(id):
    concurso = Concurso.query.get_or_404(id)
    db.session.delete(concurso)
    db.session.commit()
    flash(f"Concurso '{concurso.nome}' excluído com sucesso!", "success")
    return redirect(url_for("concursos.listar_concursos"))

@concursos_routes.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_concurso(id):
    concurso = Concurso.query.get_or_404(id)

    if request.method == "POST":
        nome = request.form.get("concurso_name")
        data = request.form.get("concurso_date")
        banca = request.form.get("concurso_banca")

        if not nome or not data or not banca:
            flash("Todos os campos são obrigatórios!", "danger")
            return redirect(url_for("concursos.editar_concurso", id=id))

        concurso.nome = nome
        concurso.data = data
        concurso.banca = banca
        db.session.commit()
        flash(f"Concurso '{nome}' atualizado com sucesso!", "success")
        return redirect(url_for("concursos.listar_concursos"))

    return render_template("editar.html", concurso=concurso)