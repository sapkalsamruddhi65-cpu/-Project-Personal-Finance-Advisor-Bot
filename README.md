# 💰 Personal Finance Advisor Bot

A complete, modern, responsive full-stack web application designed for personal finance tracking, category budgeting, savings milestone planning, and AI-powered financial advisory powered by **Google Gemini AI**.

Built with **Python Flask**, **SQLite**, **SQLAlchemy ORM**, **HTML5/CSS3/JavaScript**, and **Chart.js**.

---

## 🌟 Features Overview

### 1. 🏠 Landing & Home Page
- Clean, professional landing page highlighting key value propositions.
- Quick navigation with **Login**, **Sign Up**, and **Get Started** buttons.
- Showcase of features, security assurances, and modern design.

### 2. 🔐 Secure User Authentication
- Individual user registration and login with encrypted passwords (`Werkzeug` PBKDF2/scrypt hashing).
- Session security using `Flask-Login` with route protection.
- Complete data privacy: every user's income, expenses, budgets, savings goals, and chats are isolated by `user_id`.

### 3. 📊 Interactive Financial Dashboard
- **Monthly Income**, **Total Expenses**, **Available Net Balance**, and **Total Savings**.
- **Savings Rate Percentage** calculated in real time.
- **Spending by Category Doughnut Chart** (Chart.js) with interactive hover tooltips.
- **6-Month Income vs Expense Trend Bar Chart** showing historical cashflow performance.
- Chronological list of recent income and expense transactions.
- Quick progress indicators for active savings goals.

### 4. 💵 Income Management
- Add, view, edit, and delete income records.
- Track amount, source (*Salary*, *Freelancing*, *Investments*, *Business*, *Rental Income*, *Gift & Bonus*, *Other*), date, and notes.

### 5. 💳 Expense Tracking & Categorization
- Add, view, edit, and delete expenses.
- Standard financial categories: *Food & Dining*, *Rent & Housing*, *Transportation*, *Education*, *Healthcare*, *Entertainment*, *Utilities & Bills*, *Shopping*, *Personal Care*, and *Other*.
- Instant category-based filtering.

### 6. 🤖 Interactive Gemini AI Financial Chatbot
- Integrates with the **Google Gemini AI API** (`gemini-1.5-flash`).
- **Dynamic Context Injection:** Automatically injects the user's current month income, expenses, top spending categories, budget overruns, and active savings goals into the AI prompt.
- Answers personal finance questions, analyzes spending habits, identifies unnecessary spending, suggests 50/30/20 budget allocations, and provides tailored savings tips.
- **Quick Prompt Chips:** One-click pre-built queries (*"Analyze my spending"*, *"Suggest a 50/30/20 budget"*, *"Where can I cut expenses?"*).
- **Intelligent Demo Mode Fallback:** If the Gemini API key is missing or invalid, the bot automatically switches to a clearly labeled **Demo Mode** simulation that calculates recommendations using your actual database records!

### 7. 🎯 Category Budget Planner
- Set monthly spending limits per category.
- Visual progress bars with adaptive color indicators:
  - 🟢 **Green (< 70%):** On track
  - 🟡 **Yellow (70% - 99%):** Approaching limit warning
  - 🔴 **Red (≥ 100%):** Over-budget alert with exact overrun amount
- Real-time calculation of overall remaining safe spending.

### 8. 🏦 Savings Goals Tracker
- Create customized savings milestones (e.g. *Emergency Fund*, *New Laptop*, *Vacation*).
- Define target amounts and target dates.
- Quick **"Deposit Funds"** contribution button to allocate money directly toward a goal.
- Real-time percentage progress bar and remaining amount indicator.

### 9. 📈 Monthly Analytics & Downloadable CSV Reports
- Comprehensive financial statement breakdown by month and year.
- Category spending distribution with percentage share.
- Actual spending vs budgeted limits comparison table.
- **Downloadable CSV Export:** Click one button to download a formatted `.csv` file containing summary totals, itemized incomes, expenses, and category distributions.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Python Flask 3.x |
| **Database & ORM** | SQLite & SQLAlchemy ORM |
| **Authentication** | Flask-Login & Werkzeug Security |
| **AI Advisory Engine** | Google Gemini API (`google-generativeai`) |
| **Frontend UI** | HTML5, CSS3 (Custom Design System), JavaScript (ES6) |
| **Data Visualizations** | Chart.js |
| **Configuration** | Python-Dotenv |

---

## 📂 Project Structure

```
personal-finance-advisor-bot/
├── app.py                      # Application factory and entry point
├── config.py                   # Configuration & environment variable loader
├── extensions.py               # Database and LoginManager instances
├── models.py                   # SQLAlchemy models (User, Income, Expense, Budget, SavingsGoal, ChatMessage)
├── ai_service.py               # Gemini AI integration & contextual demo simulation engine
├── utils.py                    # Calculation helpers, financial summary, CSV generator
├── seed_demo_data.py           # Demo dataset seeder for instant testing
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
├── .gitignore                  # Prevents committing secrets, databases, or venv
├── README.md                   # Complete documentation and setup guide
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Registration, login, logout routes
│   ├── main.py                 # Landing / homepage route
│   ├── dashboard.py            # Dashboard metrics & Chart.js API
│   ├── income.py               # Income CRUD operations
│   ├── expense.py              # Expense CRUD operations
│   ├── budget.py               # Budget planner CRUD & limit checks
│   ├── savings.py              # Savings goals & contribution deposits
│   ├── reports.py              # Monthly reports & CSV export
│   └── chatbot.py              # AI Chatbot endpoint & chat history
├── static/
│   ├── css/
│   │   ├── style.css           # Clean modern design system (navy blue & emerald green)
│   │   └── chatbot.css         # Chat interface, prompt chips, typing bubbles
│   └── js/
│       ├── main.js             # Mobile sidebar, modal controls, alerts
│       ├── dashboard.js        # Doughnut & Bar Chart.js scripts
│       └── chatbot.js          # Chat client, optimistic UI, markdown parser
└── templates/
    ├── base.html               # Master layout with responsive sidebar & topbar
    ├── index.html              # Landing page
    ├── dashboard.html          # Main financial dashboard
    ├── income.html             # Income records management
    ├── expenses.html           # Expense records management
    ├── budget.html             # Monthly budget planner
    ├── savings.html            # Savings goals tracker
    ├── reports.html            # Monthly reports & CSV download
    ├── chatbot.html            # Dedicated AI Advisor chatbot page
    └── auth/
        ├── login.html          # User login
        └── register.html       # User registration
```

---

## 🚀 Local Installation & Setup

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12 installed on your computer.

### Step 1: Clone or Navigate to the Project Directory
```bash
cd personal-finance-advisor-bot
```

### Step 2: Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the `.env.example` file to create your own `.env` file:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and configure your settings:
```env
SECRET_KEY=replace-with-a-random-secret-key-for-session-signing
DATABASE_URL=sqlite:///finance_advisor.db
GEMINI_API_KEY=your_gemini_api_key_here
```

> **Note:** If you do not have a Gemini API key yet, you can leave it blank or as `your_gemini_api_key_here`. The application will seamlessly run in **Demo Mode**, providing realistic financial insights using your actual database records!

### Step 5: (Optional) Seed Realistic Demo Data
To test the website immediately with populated transactions, budgets, goals, and charts:
```bash
python seed_demo_data.py
```
This generates a test user:
- **Username:** `demo_user`
- **Password:** `demo1234`

### Step 6: Start the Flask Development Server
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 🔑 How to Get a Free Google Gemini AI API Key

1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click on **"Get API Key"** in the top navigation.
4. Click **"Create API Key in new project"** (or select an existing project).
5. Copy your generated API key.
6. Open your `.env` file in the project folder and paste it:
   ```env
   GEMINI_API_KEY=AIzaSyYourGeneratedGeminiKeyHere
   ```
7. Restart your Flask server. The chatbot page will now display **"Gemini AI Active"** with a green status indicator.

---

## 📤 How to Upload This Project to GitHub

Follow these steps to publish this repository cleanly without leaking secrets or database files:

### Step 1: Initialize Git
```bash
cd personal-finance-advisor-bot
git init
```

### Step 2: Check Status and Verify Ignored Files
```bash
git status
```
> Verify that `.env`, `instance/`, `finance_advisor.db`, and `venv/` are ignored by `.gitignore`.

### Step 3: Add and Commit Files
```bash
git add .
git commit -m "Initial commit: Complete Personal Finance Advisor Bot website"
```

### Step 4: Link to Your GitHub Repository
1. Go to [GitHub](https://github.com/) and click **"New Repository"**.
2. Give it a name (e.g. `personal-finance-advisor-bot`).
3. Leave "Initialize with README" **unchecked** (we already have a complete README).
4. Run the following commands in your terminal:
```bash
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/personal-finance-advisor-bot.git
git push -u origin main
```

---

## 🌐 Deployment & Public Demo Link

You can deploy this application for free on several hosting platforms:

### Option A: Render.com (Recommended Free Hosting)
1. Push your code to GitHub.
2. Sign up at [Render.com](https://render.com/).
3. Click **"New +"** and choose **"Web Service"**.
4. Connect your GitHub repository.
5. Configure the deployment settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (or `python app.py`)
6. In **Environment Variables**, add:
   - `SECRET_KEY`: A random secret string
   - `GEMINI_API_KEY`: Your Google Gemini API key
7. Click **"Create Web Service"**.
8. Render will build and deploy the app, providing a public URL (e.g. `https://personal-finance-advisor-bot.onrender.com`).

### Option B: PythonAnywhere (Free & Beginner-Friendly)
1. Create a free account on [PythonAnywhere](https://www.pythonanywhere.com/).
2. Open a Bash console and clone your repository:
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/personal-finance-advisor-bot.git
   ```
3. Set up a virtualenv and install dependencies:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 finance-env
   pip install -r requirements.txt
   ```
4. In the **Web** tab, create a new manual Flask app pointing to `app.py`.
5. Your public site will be accessible at `<yourusername>.pythonanywhere.com`.

---

## 🔒 Security & Privacy Highlights

- **Password Hashing:** Passwords are never stored in plaintext. They are hashed using industry-standard salt and cryptographic hashes via Werkzeug.
- **Zero Secret Leakage:** `.gitignore` excludes `.env`, `instance/`, and local SQLite files so credentials are never pushed to GitHub.
- **User Isolation:** All database queries are strictly scoped to the logged-in user (`user_id == current_user.id`).
- **Input Sanitization:** Form inputs are validated and sanitized before database insertion or AI prompt construction.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
