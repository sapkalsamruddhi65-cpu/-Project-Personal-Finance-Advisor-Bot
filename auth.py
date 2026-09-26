import re
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, bcrypt
from models import User, EmergencyFund

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        user_type = request.form.get("user_type", "Salaried")

        errors = []
        if not name or len(name) < 2:
            errors.append("Please enter your full name.")
        if not EMAIL_RE.match(email):
            errors.append("Please enter a valid email address.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if user_type not in current_app.config["USER_TYPES"]:
            user_type = "Salaried"
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists. Please log in instead.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "register.html", user_types=current_app.config["USER_TYPES"], form=request.form
            )

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(name=name, email=email, password_hash=password_hash, user_type=user_type)
        db.session.add(user)
        db.session.commit()

        # Every new user gets a default emergency fund tracker.
        db.session.add(EmergencyFund(user_id=user.id, target_months=6, current_amount=0.0))
        db.session.commit()

        login_user(user)
        flash(f"Welcome to Personal Finance Advisor Bot, {user.name}!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("register.html", user_types=current_app.config["USER_TYPES"], form={})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
