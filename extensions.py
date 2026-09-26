"""Shared extension instances.

Kept in their own module (rather than inside app.py) to avoid circular
imports between app.py, models.py and the blueprints.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access your financial dashboard."
login_manager.login_message_category = "warning"
