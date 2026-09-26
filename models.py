from datetime import datetime, date
from extensions import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(30), default="Salaried")  # Student/Salaried/Freelancer/Household
    monthly_income_estimate = db.Column(db.Float, default=0.0)  # useful for variable-income users
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship(
        "Transaction", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    budgets = db.relationship(
        "Budget", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    goals = db.relationship(
        "SavingsGoal", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    emergency_fund = db.relationship(
        "EmergencyFund", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    chat_messages = db.relationship(
        "ChatMessage", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "category": self.category,
            "amount": self.amount,
            "description": self.description or "",
            "date": self.date.isoformat(),
        }


class Budget(db.Model):
    __tablename__ = "budgets"
    __table_args__ = (
        db.UniqueConstraint("user_id", "category", "month", "year", name="uq_budget_period"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False, default=0.0)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "monthly_limit": self.monthly_limit,
            "month": self.month,
            "year": self.year,
        }


class SavingsGoal(db.Model):
    __tablename__ = "savings_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def progress_pct(self):
        if not self.target_amount:
            return 0
        return min(100, round((self.current_amount / self.target_amount) * 100, 1))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "progress_pct": self.progress_pct(),
        }


class EmergencyFund(db.Model):
    __tablename__ = "emergency_funds"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    target_months = db.Column(db.Integer, default=6)  # months of expenses to cover
    current_amount = db.Column(db.Float, default=0.0)

    def to_dict(self, avg_monthly_expense=0.0):
        target_amount = round(avg_monthly_expense * self.target_months, 2)
        progress = min(100, round((self.current_amount / target_amount) * 100, 1)) if target_amount else 0
        return {
            "target_months": self.target_months,
            "current_amount": self.current_amount,
            "target_amount": target_amount,
            "progress_pct": progress,
        }


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
