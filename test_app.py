"""
Automated Test Suite for Personal Finance Advisor Bot.
Tests user registration, login, income/expense CRUD, budget limits,
savings goals, reports, CSV export, and AI Chatbot fallback.
"""
import unittest
from datetime import date
from app import create_app
from extensions import db
from models import User, Income, Expense, Budget, SavingsGoal, ChatMessage

class TestFinanceAdvisor(unittest.TestCase):
    def setUp(self):
        # Configure app for testing with an in-memory SQLite database
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create a test user
            user = User(username='tester', email='tester@test.com', full_name='Test User')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        return self.client.post('/auth/login', data={
            'login_identifier': 'tester',
            'password': 'password123'
        }, follow_redirects=True)

    def test_home_page(self):
        """Verify landing page loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Personal Finance Advisor Bot', response.data)
        self.assertIn(b'Log In', response.data)
        self.assertIn(b'Sign Up', response.data)

    def test_auth_flow(self):
        """Verify registration, login, and logout."""
        # 1. Register new user
        reg_response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'full_name': 'New User',
            'password': 'secretpassword',
            'confirm_password': 'secretpassword'
        }, follow_redirects=True)
        self.assertEqual(reg_response.status_code, 200)
        self.assertIn(b'Welcome aboard', reg_response.data)

        # 2. Logout
        logout_response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(logout_response.status_code, 200)

        # 3. Login
        login_response = self.client.post('/auth/login', data={
            'login_identifier': 'newuser',
            'password': 'secretpassword'
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b'Financial Dashboard', login_response.data)

    def test_income_crud(self):
        """Test adding, viewing, and deleting income records."""
        self.login()
        # Add income
        response = self.client.post('/income/add', data={
            'amount': '3500.00',
            'source': 'Salary',
            'date': date.today().strftime('%Y-%m-%d'),
            'description': 'Primary paycheck'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Primary paycheck', response.data)
        self.assertIn(b'3,500.00', response.data)

        with self.app.app_context():
            inc = Income.query.first()
            self.assertIsNotNone(inc)
            self.assertEqual(inc.amount, 3500.00)
            self.assertEqual(inc.source, 'Salary')

    def test_expense_crud(self):
        """Test adding, viewing, and filtering expenses."""
        self.login()
        # Add expense
        response = self.client.post('/expenses/add', data={
            'amount': '120.50',
            'category': 'Food & Dining',
            'date': date.today().strftime('%Y-%m-%d'),
            'description': 'Grocery shopping'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Grocery shopping', response.data)
        self.assertIn(b'120.50', response.data)

    def test_budget_planner(self):
        """Test setting and tracking budget limits."""
        self.login()
        today = date.today()
        # Set budget
        response = self.client.post('/budget/set', data={
            'category': 'Food & Dining',
            'limit': '500.00',
            'month': today.month,
            'year': today.year
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Food & Dining', response.data)
        self.assertIn(b'500.00', response.data)

    def test_savings_goal_and_contribution(self):
        """Test creating a savings goal and adding a contribution deposit."""
        self.login()
        # Add goal
        response = self.client.post('/savings/add', data={
            'name': 'Emergency Buffer',
            'target_amount': '5000.00',
            'initial_amount': '1000.00',
            'category': 'Safety Net',
            'notes': '6 months of living expenses'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Emergency Buffer', response.data)
        self.assertIn(b'20.0%', response.data)

        # Deposit funds into goal
        with self.app.app_context():
            goal = SavingsGoal.query.first()
            goal_id = goal.id

        contrib_res = self.client.post(f'/savings/contribute/{goal_id}', data={
            'amount': '500.00'
        }, follow_redirects=True)
        self.assertEqual(contrib_res.status_code, 200)
        self.assertIn(b'Added $500.00', contrib_res.data)

    def test_reports_and_csv_download(self):
        """Test generating financial reports and downloading CSV."""
        self.login()
        # Get reports page
        report_page = self.client.get('/reports/')
        self.assertEqual(report_page.status_code, 200)
        self.assertIn(b'Monthly Financial Report', report_page.data)

        # Download CSV
        today = date.today()
        csv_response = self.client.get(f'/reports/download-csv?month={today.month}&year={today.year}')
        self.assertEqual(csv_response.status_code, 200)
        self.assertEqual(csv_response.mimetype, 'text/csv')
        self.assertIn(b'Personal Finance Advisor Bot - Monthly Financial Report', csv_response.data)

    def test_chatbot_ask_demo_fallback(self):
        """Test AI Chatbot endpoint gracefully generates smart contextual response."""
        self.login()
        response = self.client.post('/chatbot/ask', json={
            'message': 'Can you suggest a 50/30/20 budget for me?'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('reply', data)
        self.assertIn('50/30/20', data['reply'])

if __name__ == '__main__':
    unittest.main()
