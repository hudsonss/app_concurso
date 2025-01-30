from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Disciplina
from extensions import db  # Importa db de extensions.py
from utils import login_required

disciplinas_routes = Blueprint("disciplinas", __name__)


@disciplinas_routes.route("/cadastro_disciplina", methods=["GET", "POST"])
@login_required
def cadastro():
  if request.method == "POST":
    nome = request.form.get("nome")
    if not nome:
      flash("Todos os campos são obrigatórios.", "error")
      return redirect(url_for("disciplinas.cadastro"))

    nova_disciplina = Disciplina(nome=nome)
    db.session.add(nova_disciplina)
    db.session.commit()
    flash(f"Disciplina '{nome}' cadastrada com sucesso")
    return redirect(url_for("disciplinas.listar_disciplinas"))
  return render_template("disciplinas/cadastro_disciplina.html")


@disciplinas_routes.route("/disciplinas")
@login_required
def listar_disciplinas():
  search = request.args.get('search')  # Captura o termo de pesquisa
  page = request.args.get('page', 1,
                          type=int)  # Captura o número da página (default é 1)

  if search:
    # Filtra as disciplinas pelo nome (usando LIKE para busca parcial)
    disciplinas = Disciplina.query.filter(
        Disciplina.nome.like(f"%{search}%")).paginate(
            page=page, per_page=10)  # Exibe 10 disciplinas por página
  else:
    # Lista todas as disciplinas com paginação
    disciplinas = Disciplina.query.paginate(page=page, per_page=10)

  return render_template("disciplinas/disciplinas.html", disciplinas=disciplinas)


@disciplinas_routes.route("/delete/<int:id>", methods=["GET", "POS"])
@login_required
def excluir_disciplina(id):
  disciplina = Disciplina.query.get_or_404(id)
  db.session.delete(disciplina)
  db.session.commit()
  flash(f"Disciplina '{disciplina.nome}' excluída com sucesso")
  return redirect(url_for("listar_disciplinas"))


@disciplinas_routes.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_disciplina(id):
  disciplina = Disciplina.query.get_or_404(id)
  if request.method == "POST":
    nome = request.form.get("nome")
    carga_horaria = request.form.get("carga_horaria")
    if not nome or not carga_horaria:
      flash("Todos os campos são obrigatórios!", "danger")
      return redirect(url_for("editar_disciplina", id=id))
    disciplina.nome = nome
    disciplina.carga_horaria = carga_horaria
    db.session.commit()
    flash(f"Disciplina '{nome}' atualizada com sucesso", "success")
    return redirect(url_for("listar_disciplinas"))

  return render_template("disciplinas/editar.html", disciplina=disciplina)
