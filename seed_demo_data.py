"""
Demo Data Seeder for Personal Finance Advisor Bot.
Populates realistic financial data (income, categorized expenses, budgets, savings goals)
for testing and demonstration.
"""
from datetime import date, timedelta
from app import create_app
from extensions import db
from models import User, Income, Expense, Budget, SavingsGoal, ChatMessage

def seed():
    app = create_app()
    with app.app_context():
        # Check if demo user already exists
        demo_user = User.query.filter_by(username='demo_user').first()
        if demo_user:
            print("Demo user 'demo_user' already exists. Re-seeding data...")
            # Clean up old data for clean state
            Income.query.filter_by(user_id=demo_user.id).delete()
            Expense.query.filter_by(user_id=demo_user.id).delete()
            Budget.query.filter_by(user_id=demo_user.id).delete()
            SavingsGoal.query.filter_by(user_id=demo_user.id).delete()
            ChatMessage.query.filter_by(user_id=demo_user.id).delete()
        else:
            demo_user = User(
                username='demo_user',
                email='demo@financeadvisor.local',
                full_name='Alex Morgan',
                currency='$'
            )
            demo_user.set_password('demo1234')
            db.session.add(demo_user)
            db.session.commit()
            print("Created demo user: username='demo_user', password='demo1234'")

        today = date.today()
        curr_m = today.month
        curr_y = today.year

        # 1. Add Realistic Incomes
        incomes = [
            Income(user_id=demo_user.id, amount=4500.0, source='Salary', date=date(curr_y, curr_m, 1), description='Monthly Primary Salary'),
            Income(user_id=demo_user.id, amount=850.0, source='Freelancing', date=date(curr_y, curr_m, 10), description='UI/UX Consultation project'),
            Income(user_id=demo_user.id, amount=220.0, source='Investments', date=date(curr_y, curr_m, 15), description='Dividend payouts'),
        ]
        db.session.add_all(incomes)

        # 2. Add Categorized Expenses
        expenses = [
            # Rent & Housing
            Expense(user_id=demo_user.id, amount=1450.0, category='Rent & Housing', date=date(curr_y, curr_m, 2), description='Apartment monthly rent'),
            # Utilities
            Expense(user_id=demo_user.id, amount=165.0, category='Utilities & Bills', date=date(curr_y, curr_m, 5), description='Electricity and high-speed internet'),
            # Food & Dining
            Expense(user_id=demo_user.id, amount=240.0, category='Food & Dining', date=date(curr_y, curr_m, 3), description='Weekly supermarket groceries'),
            Expense(user_id=demo_user.id, amount=185.0, category='Food & Dining', date=date(curr_y, curr_m, 11), description='Trader Joe\'s grocery run'),
            Expense(user_id=demo_user.id, amount=95.0, category='Food & Dining', date=date(curr_y, curr_m, 14), description='Dinner with colleagues'),
            # Transportation
            Expense(user_id=demo_user.id, amount=120.0, category='Transportation', date=date(curr_y, curr_m, 6), description='Monthly transit pass'),
            Expense(user_id=demo_user.id, amount=65.0, category='Transportation', date=date(curr_y, curr_m, 18), description='Gas station fill-up'),
            # Healthcare
            Expense(user_id=demo_user.id, amount=75.0, category='Healthcare', date=date(curr_y, curr_m, 8), description='Prescription medicines & vitamins'),
            # Entertainment
            Expense(user_id=demo_user.id, amount=45.0, category='Entertainment', date=date(curr_y, curr_m, 9), description='Streaming subscriptions (Netflix, Spotify)'),
            Expense(user_id=demo_user.id, amount=80.0, category='Entertainment', date=date(curr_y, curr_m, 16), description='Concert tickets'),
            # Education
            Expense(user_id=demo_user.id, amount=120.0, category='Education', date=date(curr_y, curr_m, 12), description='Online Python & Data Science course'),
            # Shopping
            Expense(user_id=demo_user.id, amount=110.0, category='Shopping', date=date(curr_y, curr_m, 17), description='Ergonomic desk accessories'),
        ]
        db.session.add_all(expenses)

        # 3. Add Monthly Budgets
        budgets = [
            Budget(user_id=demo_user.id, category='Rent & Housing', monthly_limit=1500.0, month=curr_m, year=curr_y),
            Budget(user_id=demo_user.id, category='Food & Dining', monthly_limit=600.0, month=curr_m, year=curr_y),
            Budget(user_id=demo_user.id, category='Transportation', monthly_limit=250.0, month=curr_m, year=curr_y),
            Budget(user_id=demo_user.id, category='Utilities & Bills', monthly_limit=200.0, month=curr_m, year=curr_y),
            Budget(user_id=demo_user.id, category='Entertainment', monthly_limit=150.0, month=curr_m, year=curr_y),
            Budget(user_id=demo_user.id, category='Healthcare', monthly_limit=150.0, month=curr_m, year=curr_y),
            Budget(user_id=demo_user.id, category='Education', monthly_limit=150.0, month=curr_m, year=curr_y),
            Budget(user_id=demo_user.id, category='Shopping', monthly_limit=150.0, month=curr_m, year=curr_y),
        ]
        db.session.add_all(budgets)

        # 4. Add Savings Goals
        goals = [
            SavingsGoal(
                user_id=demo_user.id,
                name='Emergency Fund (6 Months)',
                target_amount=12000.0,
                current_amount=7800.0,
                target_date=today + timedelta(days=180),
                category='Safety Net',
                notes='Keep in high-yield savings account (HYSA).'
            ),
            SavingsGoal(
                user_id=demo_user.id,
                name='Trip to Japan',
                target_amount=3500.0,
                current_amount=1950.0,
                target_date=today + timedelta(days=240),
                category='Travel',
                notes='Flights and accommodation in Tokyo and Kyoto.'
            ),
            SavingsGoal(
                user_id=demo_user.id,
                name='New MacBook Pro M-series',
                target_amount=2200.0,
                current_amount=1500.0,
                target_date=today + timedelta(days=90),
                category='Gadgets',
                notes='For software development and freelance work.'
            )
        ]
        db.session.add_all(goals)

        # 5. Add initial welcome chat message
        welcome_chat = ChatMessage(
            user_id=demo_user.id,
            sender='bot',
            message=(
                "Hello Alex! 👋 I am your **Personal Finance Advisor Bot**.\n\n"
                "I have analyzed your current finances:\n"
                "- Total Income: **$5,570.00**\n"
                "- Total Expenses: **$2,645.00**\n"
                "- Available Balance: **$2,925.00** (52.5% savings rate!)\n\n"
                "Ask me anything like *\"Suggest a 50/30/20 budget\"*, *\"Where can I cut expenses?\"*, or *\"How to reach my Japan savings goal?\"*!"
            ),
            is_demo_mode=True
        )
        db.session.add(welcome_chat)

        db.session.commit()
        print("Demo data seeded successfully! You can login with:")
        print("   Username: demo_user")
        print("   Password: demo1234")

if __name__ == '__main__':
    seed()
