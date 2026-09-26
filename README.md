# 💰 Personal Finance Advisor Bot

An AI-powered personal finance management platform for students, salaried
professionals, freelancers, and households. Track income and expenses, set
category budgets, manage savings goals and an emergency fund, view monthly
reports, and chat with an AI advisor (Google Gemini) that gives personalized
budgeting and saving suggestions based on your **real recorded data**.

Currency: **₹ (INR)** by default.

---

## Tech Stack

| Layer      | Technology                                   |
|------------|-----------------------------------------------|
| Frontend   | HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js |
| Backend    | Python, Flask, Flask-Login, Flask-Bcrypt       |
| ORM / DB   | SQLAlchemy + SQLite (Postgres-ready)           |
| AI         | Google Gemini API (`google-generativeai`)      |
| Deployment | Render (Gunicorn) + GitHub                     |

---

## 1. Project Structure

```
personal-finance-advisor-bot/
├── app.py                     # Flask application factory & entry point
├── config.py                  # Configuration (reads from environment variables)
├── extensions.py              # Shared extension instances (db, bcrypt, login_manager)
├── models.py                  # SQLAlchemy models (User, Transaction, Budget, etc.)
├── auth.py                    # Auth blueprint: register / login / logout
├── main.py                    # Main blueprint: dashboard, transactions, budgets,
│                               #   goals, reports, chatbot, profile, JSON APIs
├── ai_advisor.py               # Gemini API integration + rule-based fallback
├── requirements.txt            # Python dependencies
├── .env.example                 # Template for environment variables (copy to .env)
├── .gitignore
├── Procfile                     # Alternative start command reference
├── render.yaml                  # Render Blueprint (Infrastructure as Code)
├── README.md
├── templates/
│   ├── base.html                # Base layout with sidebar + topbar
│   ├── _flash.html              # Flash message partial
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── transactions.html
│   ├── budgets.html
│   ├── goals.html
│   ├── reports.html
│   ├── chatbot.html
│   ├── profile.html
│   ├── 404.html
│   └── 500.html
├── static/
│   ├── css/
│   │   └── style.css            # Blue & white financial dashboard theme
│   └── js/
│       ├── main.js              # Sidebar toggle, flash auto-dismiss
│       ├── dashboard.js         # Chart.js charts
│       ├── transactions.js      # Dynamic category dropdown
│       └── chatbot.js           # AJAX chat requests
└── instance/                    # SQLite DB is created here at runtime (gitignored)
```

---

## 2. Core Features

1. **Authentication** — registration, login, logout, hashed passwords (bcrypt),
   Flask-Login session management, per-user data isolation.
2. **Interactive dashboard** — income, expenses, balance, savings rate cards,
   6-month income vs. expense trend chart, category spend doughnut chart,
   recent transactions, emergency fund progress, overspending alerts.
3. **Transactions** — add / edit / delete / list income & expenses with date,
   amount, category, description; filter by month, year and type.
4. **AI chatbot (Gemini)** — analyzes your real data (income, expenses,
   budgets, goals) and answers free-text questions with personalized advice.
   Falls back to a deterministic rule-based advisor if the Gemini API key is
   missing or the request fails, so the feature never breaks.
5. **Custom monthly budgets** — Rent, Food, Transport, Entertainment,
   Education, Healthcare, Utilities, Other — with progress bars and
   over-budget / near-limit badges.
6. **Savings goals & emergency fund** — create goals with target amount and
   deadline, contribute toward them, track progress %, and plan an emergency
   fund sized in "months of expenses."
7. **Monthly reports** — income vs. expenses, category breakdown, budget
   performance table, and generated recommendations. Printable to PDF via the
   browser's print dialog.
8. **Variable income support** — user "type" (Student / Salaried / Freelancer
   / Household) and an optional "typical monthly income" field tailor the AI
   advice (e.g. emergency-fund emphasis for freelancers, allowance-based tips
   for students).
9. **Responsive & accessible** — collapsible sidebar on mobile, Bootstrap
   grid, semantic HTML, keyboard-accessible forms and modals.

---

## 3. Local Setup on Windows (Step by Step)

### Step 1 — Install Python
1. Download Python 3.11+ from https://www.python.org/downloads/
2. During install, **check "Add python.exe to PATH"**.
3. Verify in Command Prompt:
   ```
   python --version
   ```

### Step 2 — Get the project files
Unzip `personal-finance-advisor-bot.zip` to a folder, e.g. `C:\Projects\personal-finance-advisor-bot`.

Open Command Prompt (or PowerShell) in that folder:
```
cd C:\Projects\personal-finance-advisor-bot
```

### Step 3 — Create and activate a virtual environment
```
python -m venv venv
venv\Scripts\activate
```
Your prompt should now start with `(venv)`.

### Step 4 — Install dependencies
```
pip install -r requirements.txt
```

### Step 5 — Configure environment variables
```
copy .env.example .env
```
Open `.env` in Notepad and fill in:
```
SECRET_KEY=<a long random string>
FLASK_ENV=development
GEMINI_API_KEY=<your Gemini API key>
```
To generate a secure `SECRET_KEY`, run:
```
python -c "import secrets; print(secrets.token_hex(32))"
```
Paste the output as the value of `SECRET_KEY`.

**Getting a Gemini API key (free tier available):**
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with a Google account.
3. Click "Create API key" and copy it.
4. Paste it into `.env` as `GEMINI_API_KEY=...`.
5. If you skip this step, the AI Advisor chat will still work using a
   built-in rule-based fallback advisor — it just won't use Gemini.

`python-dotenv` is included, but Flask's `app.py` reads variables via
`os.environ`. To have `.env` auto-load locally, either:
- Install and rely on an IDE that loads `.env` automatically, **or**
- Load it manually before running, in Command Prompt:
  ```
  for /f "usebackq tokens=1,2 delims==" %A in (".env") do set %A=%B
  ```
- Or simply set the variables directly in the terminal session:
  ```
  set SECRET_KEY=your-secret-key
  set GEMINI_API_KEY=your-gemini-key
  set FLASK_ENV=development
  ```

### Step 6 — Run the application
```
python app.py
```
You should see output like:
```
 * Running on http://0.0.0.0:5000
```
Open your browser at: **http://localhost:5000**

The SQLite database file is created automatically at
`instance/finance.db` the first time you run the app.

### Step 7 — Test all features
1. **Register** a new account (try each user type: Student, Salaried,
   Freelancer, Household).
2. **Login / Logout** — confirm you're redirected correctly and that
   protected pages redirect to login when logged out.
3. **Transactions** — add a few income and expense entries with different
   categories and dates; edit one; delete one; filter by month/type.
4. **Dashboard** — confirm the income/expense/balance/savings cards and both
   charts update correctly after adding transactions.
5. **Budgets** — set a monthly limit for a category (e.g. Food), add
   expenses in that category, and watch the progress bar / badge change
   (On Track → Near Limit → Over Budget).
6. **Goals & Savings** — create a savings goal, contribute to it, watch the
   progress bar update; set up the emergency fund target and current amount.
7. **Reports** — switch months/years and confirm the report, category table,
   budget table and recommendations reflect the selected period. Try
   "Print / Save PDF".
8. **AI Advisor (chatbot)** — ask a question like *"How can I save more this
   month?"*. With a valid `GEMINI_API_KEY` you'll get a Gemini-generated
   answer; without one (or if the API call fails) you'll get the rule-based
   fallback — either way, the response is based on your real data.
9. **Profile** — update your name, account type, and income estimate.
10. **Responsive design** — resize your browser window / use DevTools device
    toolbar to confirm the sidebar collapses into a toggle-able menu on
    mobile widths.

---

## 4. Preparing for GitHub

1. Create a new, empty repository on GitHub (do **not** initialize it with a
   README, since you already have one) — e.g. name it
   `personal-finance-advisor-bot`.
2. In your project folder (with `venv` still deactivated is fine), run:
   ```
   git init
   git add .
   git commit -m "Initial commit: Personal Finance Advisor Bot"
   git branch -M main
   git remote add origin https://github.com/<your-username>/personal-finance-advisor-bot.git
   git push -u origin main
   ```
3. **Important:** `.env` is listed in `.gitignore` and will never be pushed.
   Never commit real API keys or secrets — only `.env.example` should be in
   the repository.
4. After pushing, refresh your GitHub repository page and confirm all files
   (app.py, templates/, static/, requirements.txt, etc.) are present.

> I cannot create or push a GitHub repository on your behalf — I don't have
> access to your GitHub account. The steps above are exactly what you need
> to run. Once pushed, your repository's real URL will be:
> `https://github.com/<your-username>/personal-finance-advisor-bot`

---

## 5. Deploying to Render (Free, Public HTTPS URL)

Render can deploy directly from your GitHub repository and gives you a
public `https://<your-app>.onrender.com` URL that anyone can access — no one
needs access to your computer or Google account.

### Option A — One-click Blueprint (uses the included `render.yaml`)
1. Go to https://render.com and sign up / log in (you can use email — a
   Google account is not required).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub account when prompted, then select the
   `personal-finance-advisor-bot` repository.
4. Render will detect `render.yaml` and pre-fill the service configuration
   (Python web service, build command, start command, a 1GB persistent disk
   for the SQLite database).
5. When prompted for the `GEMINI_API_KEY` environment variable, paste your
   real key (it's marked `sync: false` so Render asks you to enter it
   securely rather than storing it in the repo).
6. Click **Apply** / **Create**. Render will build and deploy automatically.

### Option B — Manual Web Service (if you skip render.yaml)
1. On https://render.com, click **New +** → **Web Service**.
2. Connect your GitHub repository.
3. Configure:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Under **Environment Variables**, add:
   - `SECRET_KEY` → a long random string (generate one the same way as
     locally: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `FLASK_ENV` → `production`
   - `GEMINI_API_KEY` → your real Gemini API key
   - `GEMINI_MODEL` → `gemini-1.5-flash` (optional)
   - `DATABASE_URL` → see the persistent storage note below
5. Under **Disks**, add a persistent disk (e.g. name `finance-data`, mount
   path `/opt/render/project/data`, size 1 GB) — **required** so your SQLite
   database survives redeploys (Render's default filesystem is ephemeral).
6. Set `DATABASE_URL` to
   `sqlite:////opt/render/project/data/finance.db` (note the 4 slashes —
   3 for the `sqlite://` scheme + 1 for the absolute path) so the app writes
   the database file to that persistent disk instead of the ephemeral one.
7. Click **Create Web Service**. Render will build and deploy automatically
   on every push to your `main` branch.

### Production database notes
- SQLite works fine for a personal/demo deployment as long as it lives on
  Render's **persistent disk** (step 5–6 above) — without a disk, the
  database resets on every redeploy/restart.
- For heavier multi-user production use, swap in managed Postgres instead:
  1. Create a Render **PostgreSQL** database (free tier available).
  2. Copy its **Internal Database URL**.
  3. Set it as the `DATABASE_URL` environment variable on your web service
     (the app already normalizes `postgres://` → `postgresql://` and no
     other code changes are required — SQLAlchemy handles the rest).

### After deployment
Render will show your live service URL in the dashboard, in the form:
```
https://personal-finance-advisor-bot-XXXX.onrender.com
```
(the exact subdomain is assigned by Render when you create the service).
That link is public — copy it from your Render dashboard and share it with
anyone; no login to your accounts is needed to view it.

> I cannot deploy this for you or invent a real URL — Render deployment
> happens under your own account. Follow the steps above, then copy the
> real URL Render shows you after the build finishes successfully.

---

## 6. Security Notes

- Passwords are hashed with bcrypt (`Flask-Bcrypt`) — plaintext passwords
  are never stored.
- All financial data routes are protected with `@login_required` and always
  filtered by `user_id`, so users can only ever see and modify their own
  records.
- The Gemini API key is read only from the server-side environment
  (`GEMINI_API_KEY`) and is never sent to the browser or exposed in any
  template, JS file, or API response.
- Session cookies are `HttpOnly` and `SameSite=Lax`; `Secure` is enabled
  automatically when `FLASK_ENV=production`.
- Input validation happens on both the amount/category/type fields (server
  side) before anything touches the database.

---

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` on run | Make sure your virtual environment is activated and `pip install -r requirements.txt` completed without errors. |
| Chatbot always shows fallback text | Check that `GEMINI_API_KEY` is set correctly and that your Google AI Studio key is active/has quota. |
| Database resets after redeploying on Render | You need the persistent disk + `DATABASE_URL` pointing at it (see Section 5). |
| `flask: command not found` | You don't need the `flask` CLI here — just run `python app.py`. |
| Styles not loading | Hard-refresh the browser (Ctrl+F5) — stale cached CSS is the usual cause. |

---

## License
This project is provided as-is for personal / educational use.
