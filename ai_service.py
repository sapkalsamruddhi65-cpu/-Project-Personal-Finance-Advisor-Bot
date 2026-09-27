import os
import re
from config import Config
from utils import get_user_financial_summary

class AIFinanceAdvisor:
    """
    AI Financial Advisor service powered by Google Gemini AI,
    with an intelligent contextual fallback engine for Demo Mode.
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        """Initializes the Gemini AI client if an API key is available."""
        if self.api_key and self.api_key != 'your_gemini_api_key_here':
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(Config.GEMINI_MODEL)
            except Exception as e:
                print(f"[AIFinanceAdvisor] Warning: Failed to initialize Google Gemini client: {e}")
                self.client = None

    def get_financial_context_prompt(self, user, summary):
        """Constructs structured financial context from real database records."""
        top_cats = ", ".join([f"{k}: ${v:,.2f}" for k, v in summary['top_categories']]) or "None recorded"
        
        budget_alerts = []
        for b in summary['budgets']:
            if b['is_over']:
                budget_alerts.append(f"OVER BUDGET in {b['category']} (Spent: ${b['spent']:,.2f}, Limit: ${b['limit']:,.2f})")
            elif b['percentage'] >= 80:
                budget_alerts.append(f"Near Limit in {b['category']} ({b['percentage']}% used)")
        budget_str = "; ".join(budget_alerts) if budget_alerts else "All budgets within limits"

        goals = user.savings_goals.all()
        goals_str = "; ".join([f"{g.name}: ${g.current_amount:,.2f} of ${g.target_amount:,.2f} ({g.progress_percentage}%)" for g in goals]) if goals else "No active savings goals"

        return f"""
You are the "Personal Finance Advisor Bot", a friendly, certified, expert personal financial planner.
You provide clear, practical, beginner-friendly, and actionable financial advice.

USER PROFILE:
- Name: {user.full_name or user.username}
- Current Month Financial Summary:
  * Total Monthly Income: ${summary['monthly_income']:,.2f}
  * Total Monthly Expenses: ${summary['monthly_expense']:,.2f}
  * Available Monthly Balance: ${summary['available_balance']:,.2f}
  * Monthly Savings Rate: {summary['savings_rate']}%
  * All-Time Net Balance: ${summary['all_time_balance']:,.2f}
- Top Spending Categories: {top_cats}
- Budget Status: {budget_str}
- Active Savings Goals: {goals_str}

GUIDELINES:
1. Base your recommendations on the user's REAL financial numbers provided above.
2. Keep advice constructive, encouraging, structured with bullet points, and easy to read.
3. Suggest practical money-saving tactics, budget adjustments (like 50/30/20 rule), and emergency fund strategies.
4. Keep answers concise (under 250 words) unless in-depth analysis is requested.
"""

    def generate_demo_response(self, user, user_message, summary):
        """
        Smart offline fallback engine that generates dynamic, highly realistic
        financial advice using the user's actual database records.
        """
        msg = user_message.lower().strip()
        income = summary['monthly_income']
        expense = summary['monthly_expense']
        balance = summary['available_balance']
        savings_rate = summary['savings_rate']
        top_cats = summary['top_categories']
        budgets = summary['budgets']

        disclaimer = "*(Demo Mode: Gemini API key not configured or unreachable. Below is an intelligent simulation based on your real data.)*\n\n"

        # 1. Budget suggestion or 50/30/20
        if any(w in msg for w in ['budget', '50/30/20', 'rule', 'plan']):
            needs = income * 0.50
            wants = income * 0.30
            savings = income * 0.20
            return (
                f"{disclaimer}"
                f"### Personalized 50/30/20 Budget Plan for You\n\n"
                f"Based on your recorded monthly income of **${income:,.2f}**, here is your recommended monthly allocation:\n\n"
                f"- **50% Needs (Essential living costs):** **${needs:,.2f}**\n"
                f"  * Rent, utilities, groceries, healthcare, and basic transport.\n"
                f"- **30% Wants (Lifestyle & entertainment):** **${wants:,.2f}**\n"
                f"  * Dining out, shopping, subscriptions, hobbies.\n"
                f"- **20% Savings & Debt Repayment:** **${savings:,.2f}**\n"
                f"  * Emergency fund, high-yield savings, investments.\n\n"
                f"**Current Status:** Your expenses this month are **${expense:,.2f}** "
                f"leaving a balance of **${balance:,.2f}** ({savings_rate}% savings rate). "
                f"Target saving at least **${savings:,.2f}** every month to stay on track!"
            )

        # 2. Where to cut expenses or unnecessary spending
        elif any(w in msg for w in ['cut', 'reduce', 'unnecessary', 'overspend', 'leak', 'spend less', 'where is my money']):
            if top_cats:
                highest_cat, highest_amt = top_cats[0]
                pct_of_exp = (highest_amt / expense * 100) if expense > 0 else 0
                second = f" and **{top_cats[1][0]}** (${top_cats[1][1]:,.2f})" if len(top_cats) > 1 else ""
                
                return (
                    f"{disclaimer}"
                    f"### Spending Analysis & Quick Savings Wins\n\n"
                    f"Looking at your expenses this month (totaling **${expense:,.2f}**), here is where your money is flowing:\n\n"
                    f"1. **Primary Spending Category:** **{highest_cat}** represents **${highest_amt:,.2f}** ({pct_of_exp:.1f}% of total spending){second}.\n"
                    f"2. **Discretionary Trimming:** Aim for a 10%–15% reduction in non-essential categories, which would instantly free up **${highest_amt * 0.12:,.2f}/month**.\n"
                    f"3. **Subscription Audit:** Review recurring monthly debits for services or gym memberships you rarely use.\n"
                    f"4. **Meal Planning:** If dining or takeout is elevated, cooking 2 more meals at home per week can save $150–$300/month."
                )
            else:
                return (
                    f"{disclaimer}"
                    f"### Expense Reduction Tips\n\n"
                    f"You don't have many expense records logged for this month yet. Once you record your daily expenses, "
                    f"I can pinpoint your highest spending categories!\n\n"
                    f"**General Best Practices:**\n"
                    f"- Follow the 24-hour rule before non-essential purchases over $50.\n"
                    f"- Negotiate internet, phone, and insurance rates annually.\n"
                    f"- Automate transfers to your savings right after payday."
                )

        # 3. Savings goals or emergency fund
        elif any(w in msg for w in ['save', 'saving', 'goal', 'emergency fund', 'invest']):
            goals = user.savings_goals.all()
            goals_summary = ""
            if goals:
                goals_summary = "\n**Your Active Goals:**\n" + "\n".join([f"- **{g.name}:** ${g.current_amount:,.2f} / ${g.target_amount:,.2f} ({g.progress_percentage}%)" for g in goals])

            target_emergency = expense * 3 if expense > 0 else 3000.0
            return (
                f"{disclaimer}"
                f"### High-Impact Savings Strategy\n\n"
                f"- **Current Net Balance:** You have **${balance:,.2f}** remaining this month ({savings_rate}% savings rate).\n"
                f"- **3-Month Emergency Fund Target:** Based on your monthly spend of ${expense:,.2f}, aim for an emergency buffer of **${target_emergency:,.2f}** in a high-yield savings account (HYSA).\n"
                f"- **Automate Savings:** Transfer money to your savings on the day your salary is received, not at the end of the month.\n"
                f"{goals_summary}\n\n"
                f"**Tip:** Even an extra $25 or $50 contributed weekly adds up to over $1,300–$2,600 each year!"
            )

        # 4. General / Greeting / Analysis
        else:
            return (
                f"{disclaimer}"
                f"### Financial Health Overview for {user.full_name or user.username}\n\n"
                f"Here is a summary of your financial position:\n\n"
                f"- **Monthly Income:** **${income:,.2f}**\n"
                f"- **Monthly Expenses:** **${expense:,.2f}**\n"
                f"- **Net Balance:** **${balance:,.2f}**\n"
                f"- **Current Savings Rate:** **{savings_rate}%**\n\n"
                f"**What would you like to explore next?**\n"
                f"- Ask *\"How can I cut expenses?\"* for spending optimizations.\n"
                f"- Ask *\"Suggest a 50/30/20 budget\"* for tailored spending caps.\n"
                f"- Ask *\"How to build an emergency fund?\"* for step-by-step guidance."
            )

    def ask(self, user, user_message):
        """
        Sends a query to Gemini AI with full financial context,
        or gracefully falls back to the intelligent demo mode.
        """
        summary = get_user_financial_summary(user.id)
        
        # Check if client is initialized
        if not self.client and self.api_key and self.api_key != 'your_gemini_api_key_here':
            self._init_gemini()

        if self.client:
            try:
                system_context = self.get_financial_context_prompt(user, summary)
                full_prompt = f"{system_context}\n\nUSER QUESTION: {user_message}\n\nADVISOR RESPONSE:"
                response = self.client.generate_content(full_prompt)
                
                if response and hasattr(response, 'text') and response.text:
                    return {
                        'response': response.text.strip(),
                        'is_demo_mode': False,
                        'success': True
                    }
            except Exception as e:
                print(f"[AIFinanceAdvisor] Error during Gemini API call: {e}")
                # Fall through to demo mode

        # Fallback to smart Demo Mode
        demo_text = self.generate_demo_response(user, user_message, summary)
        return {
            'response': demo_text,
            'is_demo_mode': True,
            'success': True
        }
