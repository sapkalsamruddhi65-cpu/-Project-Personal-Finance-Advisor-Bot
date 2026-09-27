import os
from pathlib import Path
from flask import Flask
from config import Config
from extensions import db, login_manager

def create_app(config_class=Config):
    """Application factory for Personal Finance Advisor Bot."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure the instance directory exists for SQLite database storage
    instance_path = Path(app.root_path) / 'instance'
    instance_path.mkdir(exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.income import income_bp
    from routes.expense import expense_bp
    from routes.budget import budget_bp
    from routes.savings import savings_bp
    from routes.reports import reports_bp
    from routes.chatbot import chatbot_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(savings_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(chatbot_bp)

    # Context processor to inject global variables in all templates
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'Personal Finance Advisor Bot',
            'current_year': 2026,
            'currency': '₹'
        }

    # Automatically create database tables if they do not exist
    with app.app_context():
        import models  # Ensure all models are registered
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    # Run the application locally
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
