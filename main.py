import calendar
from datetime import datetime, date

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import extract, func

from extensions import db
from models import Transaction, Budget, SavingsGoal, EmergencyFund, ChatMessage
from ai_advisor import get_financial_advice

main_bp = Blueprint("main", __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _month_year_from_request():
    try:
        month = int(request.args.get("month", datetime.utcnow().month))
        year = int(request.args.get("year", datetime.utcnow().year))
        if month < 1 or month > 12:
            month = datetime.utcnow().month
    except (TypeError, ValueError):
        month, year = datetime.utcnow().month, datetime.utcnow().year
    return month, year


def build_financial_summary(user, month=None, year=None):
    """Aggregates a user's transactions/budgets/goals for a given month into
    a plain dict used both by the dashboard/report views and the AI advisor."""
    today = datetime.utcnow()
    month = month or today.month
    year = year or today.year

    tx_query = Transaction.query.filter_by(user_id=user.id).filter(
        extract("month", Transaction.date) == month,
        extract("year", Transaction.date) == year,
    )

    income_total = (
        tx_query.filter_by(type="income").with_entities(func.sum(Transaction.amount)).scalar() or 0.0
    )
    expense_total = (
        tx_query.filter_by(type="expense").with_entities(func.sum(Transaction.amount)).scalar() or 0.0
    )
    balance = income_total - expense_total
    savings_rate = round((balance / income_total) * 100, 1) if income_total > 0 else 0.0

    category_rows = (
        tx_query.filter_by(type="expense")
        .with_entities(Transaction.category, func.sum(Transaction.amount))
        .group_by(Transaction.category)
        .all()
    )
    category_breakdown = {cat: round(total, 2) for cat, total in category_rows}

    budgets = Budget.query.filter_by(user_id=user.id, month=month, year=year).all()
    budget_status = []
    for b in budgets:
        spent = category_breakdown.get(b.category, 0.0)
        pct = round((spent / b.monthly_limit) * 100, 1) if b.monthly_limit else 0.0
        budget_status.append(
            {"category": b.category, "limit": b.monthly_limit, "spent": spent, "pct": pct}
        )

    goals = SavingsGoal.query.filter_by(user_id=user.id).all()
    goals_data = [g.to_dict() for g in goals]

    return {
        "user_type": user.user_type,
        "month": month,
        "year": year,
        "monthly_income": round(income_total, 2),
        "monthly_expense": round(expense_total, 2),
        "balance": round(balance, 2),
        "savings_rate": savings_rate,
        "category_breakdown": category_breakdown,
        "budget_status": budget_status,
        "goals": goals_data,
    }


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    month, year = _month_year_from_request()
    summary = build_financial_summary(current_user, month, year)

    # last 6 months trend for the line chart
    trend = []
    m, y = month, year
    for _ in range(6):
        s = build_financial_summary(current_user, m, y)
        trend.append(
            {
                "label": f"{calendar.month_abbr[m]} {y}",
                "income": s["monthly_income"],
                "expense": s["monthly_expense"],
            }
        )
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    trend.reverse()

    recent_tx = (
        Transaction.query.filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(6)
        .all()
    )

    overspent_categories = [b for b in summary["budget_status"] if b["pct"] >= 100]

    ef = EmergencyFund.query.filter_by(user_id=current_user.id).first()
    avg_expense = summary["monthly_expense"] or 1.0
    ef_data = ef.to_dict(avg_monthly_expense=avg_expense) if ef else None

    return render_template(
        "dashboard.html",
        summary=summary,
        trend=trend,
        recent_tx=recent_tx,
        overspent=overspent_categories,
        ef=ef_data,
        currency=current_app.config["CURRENCY_SYMBOL"],
        month=month,
        year=year,
        month_name=calendar.month_name[month],
    )


# ---------------------------------------------------------------------------
# Transactions (CRUD)
# ---------------------------------------------------------------------------
@main_bp.route("/transactions", methods=["GET"])
@login_required
def transactions():
    month, year = _month_year_from_request()
    tx_type = request.args.get("type", "all")

    query = Transaction.query.filter_by(user_id=current_user.id).filter(
        extract("month", Transaction.date) == month,
        extract("year", Transaction.date) == year,
    )
    if tx_type in ("income", "expense"):
        query = query.filter_by(type=tx_type)

    tx_list = query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()

    return render_template(
        "transactions.html",
        transactions=tx_list,
        currency=current_app.config["CURRENCY_SYMBOL"],
        income_categories=current_app.config["INCOME_CATEGORIES"],
        expense_categories=current_app.config["EXPENSE_CATEGORIES"],
        month=month,
        year=year,
        tx_type=tx_type,
        today=date.today().isoformat(),
    )


@main_bp.route("/transactions/add", methods=["POST"])
@login_required
def add_transaction():
    tx_type = request.form.get("type")
    category = (request.form.get("category") or "").strip()
    amount_raw = request.form.get("amount", "")
    description = (request.form.get("description") or "").strip()
    date_raw = request.form.get("date")

    errors = []
    if tx_type not in ("income", "expense"):
        errors.append("Invalid transaction type.")
    if not category:
        errors.append("Category is required.")
    try:
        amount = float(amount_raw)
        if amount <= 0:
            errors.append("Amount must be greater than zero.")
    except ValueError:
        errors.append("Amount must be a valid number.")
        amount = 0

    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("main.transactions"))

    tx = Transaction(
        user_id=current_user.id,
        type=tx_type,
        category=category,
        amount=amount,
        description=description,
        date=_parse_date(date_raw),
    )
    db.session.add(tx)
    db.session.commit()
    flash("Transaction added successfully.", "success")
    return redirect(url_for("main.transactions"))


@main_bp.route("/transactions/<int:tx_id>/edit", methods=["POST"])
@login_required
def edit_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()

    tx_type = request.form.get("type")
    category = (request.form.get("category") or "").strip()
    amount_raw = request.form.get("amount", "")
    description = (request.form.get("description") or "").strip()
    date_raw = request.form.get("date")

    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        flash("Amount must be a valid positive number.", "danger")
        return redirect(url_for("main.transactions"))

    if tx_type not in ("income", "expense") or not category:
        flash("Invalid transaction data.", "danger")
        return redirect(url_for("main.transactions"))

    tx.type = tx_type
    tx.category = category
    tx.amount = amount
    tx.description = description
    tx.date = _parse_date(date_raw)
    db.session.commit()
    flash("Transaction updated successfully.", "success")
    return redirect(url_for("main.transactions"))


@main_bp.route("/transactions/<int:tx_id>/delete", methods=["POST"])
@login_required
def delete_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    db.session.delete(tx)
    db.session.commit()
    flash("Transaction deleted.", "info")
    return redirect(url_for("main.transactions"))


# ---------------------------------------------------------------------------
# Budgets
# ---------------------------------------------------------------------------
@main_bp.route("/budgets", methods=["GET"])
@login_required
def budgets():
    month, year = _month_year_from_request()
    summary = build_financial_summary(current_user, month, year)
    existing = {b.category: b for b in Budget.query.filter_by(
        user_id=current_user.id, month=month, year=year
    ).all()}

    rows = []
    for cat in current_app.config["EXPENSE_CATEGORIES"]:
        b = existing.get(cat)
        spent = summary["category_breakdown"].get(cat, 0.0)
        limit = b.monthly_limit if b else 0.0
        pct = round((spent / limit) * 100, 1) if limit else 0
        rows.append({
            "category": cat,
            "budget_id": b.id if b else None,
            "limit": limit,
            "spent": spent,
            "pct": pct,
        })

    return render_template(
        "budgets.html",
        rows=rows,
        currency=current_app.config["CURRENCY_SYMBOL"],
        month=month,
        year=year,
    )


@main_bp.route("/budgets/save", methods=["POST"])
@login_required
def save_budget():
    month = int(request.form.get("month"))
    year = int(request.form.get("year"))
    category = request.form.get("category")
    limit_raw = request.form.get("limit", "0")

    try:
        limit = float(limit_raw)
        if limit < 0:
            raise ValueError()
    except ValueError:
        flash("Budget limit must be a valid non-negative number.", "danger")
        return redirect(url_for("main.budgets", month=month, year=year))

    if category not in current_app.config["EXPENSE_CATEGORIES"]:
        flash("Invalid budget category.", "danger")
        return redirect(url_for("main.budgets", month=month, year=year))

    budget = Budget.query.filter_by(
        user_id=current_user.id, category=category, month=month, year=year
    ).first()
    if budget:
        budget.monthly_limit = limit
    else:
        budget = Budget(
            user_id=current_user.id, category=category, monthly_limit=limit, month=month, year=year
        )
        db.session.add(budget)
    db.session.commit()
    flash(f"Budget for {category} saved.", "success")
    return redirect(url_for("main.budgets", month=month, year=year))


# ---------------------------------------------------------------------------
# Savings Goals & Emergency Fund
# ---------------------------------------------------------------------------
@main_bp.route("/goals", methods=["GET"])
@login_required
def goals():
    goal_list = SavingsGoal.query.filter_by(user_id=current_user.id).order_by(
        SavingsGoal.created_at.desc()
    ).all()
    ef = EmergencyFund.query.filter_by(user_id=current_user.id).first()
    summary = build_financial_summary(current_user)
    avg_expense = summary["monthly_expense"] or 1.0
    ef_data = ef.to_dict(avg_monthly_expense=avg_expense) if ef else None

    return render_template(
        "goals.html",
        goals=goal_list,
        ef=ef_data,
        currency=current_app.config["CURRENCY_SYMBOL"],
    )


@main_bp.route("/goals/add", methods=["POST"])
@login_required
def add_goal():
    name = (request.form.get("name") or "").strip()
    target_raw = request.form.get("target_amount", "")
    deadline_raw = request.form.get("deadline")

    try:
        target = float(target_raw)
        if target <= 0:
            raise ValueError()
    except ValueError:
        flash("Target amount must be a valid positive number.", "danger")
        return redirect(url_for("main.goals"))

    if not name:
        flash("Goal name is required.", "danger")
        return redirect(url_for("main.goals"))

    goal = SavingsGoal(
        user_id=current_user.id,
        name=name,
        target_amount=target,
        current_amount=0.0,
        deadline=_parse_date(deadline_raw) if deadline_raw else None,
    )
    db.session.add(goal)
    db.session.commit()
    flash("Savings goal created.", "success")
    return redirect(url_for("main.goals"))


@main_bp.route("/goals/<int:goal_id>/contribute", methods=["POST"])
@login_required
def contribute_goal(goal_id):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    amount_raw = request.form.get("amount", "0")
    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        flash("Contribution amount must be a valid positive number.", "danger")
        return redirect(url_for("main.goals"))

    goal.current_amount = (goal.current_amount or 0) + amount
    db.session.commit()
    flash(f"Added {current_app.config['CURRENCY_SYMBOL']}{amount:,.2f} to '{goal.name}'.", "success")
    return redirect(url_for("main.goals"))


@main_bp.route("/goals/<int:goal_id>/delete", methods=["POST"])
@login_required
def delete_goal(goal_id):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash("Savings goal removed.", "info")
    return redirect(url_for("main.goals"))


@main_bp.route("/emergency-fund/update", methods=["POST"])
@login_required
def update_emergency_fund():
    ef = EmergencyFund.query.filter_by(user_id=current_user.id).first()
    if not ef:
        ef = EmergencyFund(user_id=current_user.id)
        db.session.add(ef)

    try:
        ef.current_amount = float(request.form.get("current_amount", 0))
        ef.target_months = int(request.form.get("target_months", 6))
    except ValueError:
        flash("Please enter valid numbers.", "danger")
        return redirect(url_for("main.goals"))

    db.session.commit()
    flash("Emergency fund updated.", "success")
    return redirect(url_for("main.goals"))


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
@main_bp.route("/reports")
@login_required
def reports():
    month, year = _month_year_from_request()
    summary = build_financial_summary(current_user, month, year)

    # Basic recommendations (rule-based, instant — no API call needed for the report page)
    recommendations = []
    if summary["monthly_income"] > 0 and summary["savings_rate"] < 20:
        recommendations.append(
            "Your savings rate is below the recommended 20% — review discretionary spending."
        )
    for b in summary["budget_status"]:
        if b["pct"] >= 100:
            recommendations.append(f"You exceeded your {b['category']} budget this month.")
        elif b["pct"] >= 80:
            recommendations.append(f"You're nearing your {b['category']} budget limit.")
    if not recommendations:
        recommendations.append("You're on track this month. Keep up the good financial habits!")

    return render_template(
        "reports.html",
        summary=summary,
        recommendations=recommendations,
        currency=current_app.config["CURRENCY_SYMBOL"],
        month=month,
        year=year,
        month_name=calendar.month_name[month],
    )


# ---------------------------------------------------------------------------
# AI Chatbot
# ---------------------------------------------------------------------------
@main_bp.route("/chatbot")
@login_required
def chatbot():
    history = (
        ChatMessage.query.filter_by(user_id=current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(50)
        .all()
    )
    return render_template("chatbot.html", history=history)


@main_bp.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()

    if not question:
        return jsonify({"error": "Message cannot be empty."}), 400
    if len(question) > 1000:
        return jsonify({"error": "Message is too long (max 1000 characters)."}), 400

    summary = build_financial_summary(current_user)

    try:
        db.session.add(ChatMessage(user_id=current_user.id, role="user", content=question))
        answer = get_financial_advice(summary, question)
        db.session.add(ChatMessage(user_id=current_user.id, role="assistant", content=answer))
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        current_app.logger.error("Chat error: %s", exc)
        return jsonify({"error": "Something went wrong processing your message. Please try again."}), 500

    return jsonify({"reply": answer})


# ---------------------------------------------------------------------------
# JSON API for dashboard charts
# ---------------------------------------------------------------------------
@main_bp.route("/api/dashboard-data")
@login_required
def api_dashboard_data():
    month, year = _month_year_from_request()
    summary = build_financial_summary(current_user, month, year)
    return jsonify(summary)


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------
@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        user_type = request.form.get("user_type")
        income_estimate_raw = request.form.get("monthly_income_estimate", "0")

        if name:
            current_user.name = name
        if user_type in current_app.config["USER_TYPES"]:
            current_user.user_type = user_type
        try:
            current_user.monthly_income_estimate = float(income_estimate_raw)
        except ValueError:
            pass

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("main.profile"))

    return render_template("profile.html", user_types=current_app.config["USER_TYPES"])
