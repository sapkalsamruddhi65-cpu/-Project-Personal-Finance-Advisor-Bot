import csv
import io
from datetime import datetime, date
from sqlalchemy import func, extract
from extensions import db
from models import Income, Expense, Budget, SavingsGoal

EXPENSE_CATEGORIES = [
    'Food & Dining',
    'Rent & Housing',
    'Transportation',
    'Education',
    'Healthcare',
    'Entertainment',
    'Utilities & Bills',
    'Shopping',
    'Personal Care',
    'Other'
]

INCOME_SOURCES = [
    'Salary',
    'Freelancing',
    'Investments',
    'Business',
    'Rental Income',
    'Gift & Bonus',
    'Other'
]

def get_current_month_year():
    today = date.today()
    return today.month, today.year

def get_user_financial_summary(user_id, month=None, year=None):
    """
    Computes real-time financial metrics for a user.
    If month/year are omitted, defaults to the current month/year.
    """
    if month is None or year is None:
        curr_m, curr_y = get_current_month_year()
        month = month or curr_m
        year = year or curr_y

    # Monthly Incomes
    monthly_incomes = Income.query.filter(
        Income.user_id == user_id,
        extract('month', Income.date) == month,
        extract('year', Income.date) == year
    ).all()
    monthly_income_total = sum(i.amount for i in monthly_incomes)

    # Monthly Expenses
    monthly_expenses = Expense.query.filter(
        Expense.user_id == user_id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).all()
    monthly_expense_total = sum(e.amount for e in monthly_expenses)

    # Available Balance for the month
    monthly_balance = monthly_income_total - monthly_expense_total

    # All-time metrics
    all_time_income = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(Income.user_id == user_id).scalar()
    all_time_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(Expense.user_id == user_id).scalar()
    all_time_balance = all_time_income - all_time_expense

    # Total savings in active goals
    total_savings_in_goals = db.session.query(func.coalesce(func.sum(SavingsGoal.current_amount), 0.0)).filter(SavingsGoal.user_id == user_id).scalar()
    total_savings_target = db.session.query(func.coalesce(func.sum(SavingsGoal.target_amount), 0.0)).filter(SavingsGoal.user_id == user_id).scalar()

    # Category breakdown for the month
    category_totals = {}
    for exp in monthly_expenses:
        category_totals[exp.category] = category_totals.get(exp.category, 0.0) + exp.amount

    # Sort categories by spending descending
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

    # Budgets for this month
    budgets = Budget.query.filter(
        Budget.user_id == user_id,
        Budget.month == month,
        Budget.year == year
    ).all()

    budget_status = []
    total_budget_limit = 0.0
    for b in budgets:
        spent = category_totals.get(b.category, 0.0)
        remaining = b.monthly_limit - spent
        pct = round((spent / b.monthly_limit * 100), 1) if b.monthly_limit > 0 else 0
        total_budget_limit += b.monthly_limit
        budget_status.append({
            'id': b.id,
            'category': b.category,
            'limit': b.monthly_limit,
            'spent': round(spent, 2),
            'remaining': round(remaining, 2),
            'percentage': pct,
            'is_over': spent > b.monthly_limit
        })

    # Savings rate
    savings_rate = 0.0
    if monthly_income_total > 0:
        savings_rate = round(max(0.0, (monthly_balance / monthly_income_total) * 100), 1)

    return {
        'month': month,
        'year': year,
        'monthly_income': round(monthly_income_total, 2),
        'monthly_expense': round(monthly_expense_total, 2),
        'available_balance': round(monthly_balance, 2),
        'all_time_balance': round(all_time_balance, 2),
        'total_savings_goals': round(total_savings_in_goals, 2),
        'total_savings_target': round(total_savings_target, 2),
        'savings_rate': savings_rate,
        'category_breakdown': dict(sorted_categories),
        'top_categories': sorted_categories[:5],
        'budgets': budget_status,
        'total_budget_limit': round(total_budget_limit, 2),
        'expense_count': len(monthly_expenses),
        'income_count': len(monthly_incomes)
    }


def generate_monthly_csv(user_id, month=None, year=None):
    """Generates an exportable CSV buffer for financial records."""
    curr_m, curr_y = get_current_month_year()
    month = int(month) if month else curr_m
    year = int(year) if year else curr_y

    incomes = Income.query.filter(
        Income.user_id == user_id,
        extract('month', Income.date) == month,
        extract('year', Income.date) == year
    ).order_by(Income.date.asc()).all()

    expenses = Expense.query.filter(
        Expense.user_id == user_id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).order_by(Expense.date.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header / Summary Section
    writer.writerow(["Personal Finance Advisor Bot - Monthly Financial Report"])
    writer.writerow(["Month", f"{month:02d}/{year}"])
    writer.writerow(["Generated At", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
    writer.writerow([])

    total_inc = sum(i.amount for i in incomes)
    total_exp = sum(e.amount for e in expenses)
    net_bal = total_inc - total_exp

    writer.writerow(["FINANCIAL SUMMARY"])
    writer.writerow(["Total Income", f"${total_inc:,.2f}"])
    writer.writerow(["Total Expenses", f"${total_exp:,.2f}"])
    writer.writerow(["Net Savings", f"${net_bal:,.2f}"])
    writer.writerow([])

    # Income Section
    writer.writerow(["INCOME RECORDS"])
    writer.writerow(["Date", "Source", "Amount ($)", "Description"])
    for inc in incomes:
        writer.writerow([inc.date.strftime("%Y-%m-%d"), inc.source, f"{inc.amount:.2f}", inc.description or ''])
    writer.writerow([])

    # Expense Section
    writer.writerow(["EXPENSE RECORDS"])
    writer.writerow(["Date", "Category", "Amount ($)", "Description"])
    for exp in expenses:
        writer.writerow([exp.date.strftime("%Y-%m-%d"), exp.category, f"{exp.amount:.2f}", exp.description or ''])
    writer.writerow([])

    # Category Breakdown
    category_map = {}
    for exp in expenses:
        category_map[exp.category] = category_map.get(exp.category, 0.0) + exp.amount

    writer.writerow(["CATEGORY BREAKDOWN"])
    writer.writerow(["Category", "Total Spent ($)", "Share of Expenses (%)"])
    for cat, val in sorted(category_map.items(), key=lambda x: x[1], reverse=True):
        share = (val / total_exp * 100) if total_exp > 0 else 0
        writer.writerow([cat, f"{val:.2f}", f"{share:.1f}%"])

    output.seek(0)
    return output.getvalue()
