from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario
from extensions import db
from utils import login_required  # Importa db de extensions.py

auth_routes = Blueprint("auth", __name__)

@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Usuario.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Nome de usuário ou senha incorretos!", "error")
            return redirect(url_for("auth.login"))

        session.permanent = True
        session["user_id"] = user.id
        session["username"] = user.username
        flash("Login realizado com sucesso!", "success")
        return redirect(url_for("concursos.listar_concursos"))

    return render_template("auth/login.html")

@auth_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password or not confirm_password:
            flash("Por favor, preencha todos os campos.", "error")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for("auth.register"))

        existing_user = Usuario.query.filter_by(username=username).first()
        if existing_user:
            flash("Usuário já existe.", "error")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)
        novo_usuario = Usuario(username=username, password=hashed_password)
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Registro realizado com sucesso!", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_routes.route("/logout")
@login_required
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("Logout efetuado com sucesso!", "success")
    return redirect(url_for("auth.login"))