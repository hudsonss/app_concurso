from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Usuario
from extensions import db  # Importa db de extensions.py
from werkzeug.security import generate_password_hash, check_password_hash
from utils import login_required

users_routes = Blueprint("users", __name__)

@users_routes.route("/perfil")
@login_required
def perfil():
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id)
    return render_template("perfil.html", usuario=usuario)

@users_routes.route("/alterar_senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id)

    if request.method == "POST":
        senha_atual = request.form.get("senha_atual")
        nova_senha = request.form.get("nova_senha")
        confirmar_senha = request.form.get("confirmar_senha")

        if not check_password_hash(usuario.password, senha_atual):
            flash("Senha atual incorreta!", "error")
            return redirect(url_for("users.perfil"))

        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem!", "error")
            return redirect(url_for("users.perfil"))

        usuario.password = generate_password_hash(nova_senha)
        db.session.commit()
        flash("Senha alterada com sucesso!", "success")
        return redirect(url_for("users.perfil"))

    return render_template("perfil.html")