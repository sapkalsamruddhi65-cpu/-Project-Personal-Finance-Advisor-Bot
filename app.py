import os
from flask import Flask, render_template

from config import Config
from extensions import db, bcrypt, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure the instance folder exists for the SQLite file.
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import models so SQLAlchemy is aware of them before create_all()
    from models import User, Transaction, Budget, SavingsGoal, EmergencyFund, ChatMessage  # noqa: F401

    # Register blueprints
    from auth import auth_bp
    from main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Make currency symbol available in every template
    @app.context_processor
    def inject_globals():
        return {
            "currency_symbol": app.config["CURRENCY_SYMBOL"],
            "app_name": "Personal Finance Advisor Bot",
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_ENV") != "production"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
