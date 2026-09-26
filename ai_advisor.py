"""AI financial advisor module.

Wraps the Google Gemini API to produce personalized budgeting / saving
suggestions based on a user's real transaction data. If the API key is
missing, invalid, or the request fails for any reason (network issue,
quota, etc.), a deterministic rule-based fallback is used instead so the
chatbot never breaks for the end user.
"""
import os
import logging

logger = logging.getLogger(__name__)

CURRENCY = "\u20b9"


def _build_financial_context(summary: dict) -> str:
    """Turns a numeric summary dict into a compact text block for the LLM prompt."""
    lines = [
        f"User type: {summary.get('user_type', 'Unknown')}",
        f"Monthly income (this month): {CURRENCY}{summary.get('monthly_income', 0):,.2f}",
        f"Monthly expenses (this month): {CURRENCY}{summary.get('monthly_expense', 0):,.2f}",
        f"Balance (this month): {CURRENCY}{summary.get('balance', 0):,.2f}",
        f"Savings rate: {summary.get('savings_rate', 0)}%",
    ]
    cat = summary.get("category_breakdown", {})
    if cat:
        lines.append("Spending by category this month:")
        for k, v in cat.items():
            lines.append(f"  - {k}: {CURRENCY}{v:,.2f}")
    budgets = summary.get("budget_status", [])
    if budgets:
        lines.append("Budget status this month:")
        for b in budgets:
            lines.append(
                f"  - {b['category']}: spent {CURRENCY}{b['spent']:,.2f} of "
                f"{CURRENCY}{b['limit']:,.2f} limit ({b['pct']}%)"
            )
    goals = summary.get("goals", [])
    if goals:
        lines.append("Savings goals:")
        for g in goals:
            lines.append(
                f"  - {g['name']}: {CURRENCY}{g['current_amount']:,.2f} / "
                f"{CURRENCY}{g['target_amount']:,.2f} ({g['progress_pct']}%)"
            )
    return "\n".join(lines)


def _rule_based_fallback(summary: dict, question: str = "") -> str:
    """Deterministic, useful advice generator used when Gemini is unavailable."""
    income = summary.get("monthly_income", 0)
    expense = summary.get("monthly_expense", 0)
    balance = income - expense
    savings_rate = summary.get("savings_rate", 0)
    cat = summary.get("category_breakdown", {})
    budgets = summary.get("budget_status", [])

    tips = []

    if income == 0 and expense == 0:
        return (
            "I don't see any transactions recorded yet. Start by adding your income and "
            "expenses on the Transactions page so I can analyze your spending and give you "
            "personalized budgeting advice. As a general rule of thumb, try to save at least "
            "20% of your income and keep essential expenses (rent, food, transport) under 50%."
        )

    if balance < 0:
        tips.append(
            f"You're currently spending more than you earn this month "
            f"(deficit of {CURRENCY}{abs(balance):,.2f}). Review your largest expense "
            f"categories below and look for cuts you can make immediately."
        )
    elif savings_rate < 20:
        tips.append(
            f"Your current savings rate is about {savings_rate}%. Financial experts often "
            f"recommend saving at least 20% of your income — try trimming discretionary "
            f"categories like entertainment to close the gap."
        )
    else:
        tips.append(
            f"Great job — you're saving roughly {savings_rate}% of your income this month. "
            f"Consider directing part of this surplus toward your savings goals or an "
            f"emergency fund."
        )

    if cat:
        top_cat = max(cat.items(), key=lambda x: x[1])
        tips.append(
            f"Your biggest expense category is {top_cat[0]} at {CURRENCY}{top_cat[1]:,.2f}. "
            f"Setting a monthly budget for this category could help control it."
        )

    overspent = [b for b in budgets if b["pct"] >= 100]
    nearing = [b for b in budgets if 80 <= b["pct"] < 100]
    if overspent:
        names = ", ".join(b["category"] for b in overspent)
        tips.append(f"You have exceeded your budget in: {names}. Consider reducing spending here next month.")
    if nearing:
        names = ", ".join(b["category"] for b in nearing)
        tips.append(f"You're close to your limit (80%+) in: {names}. Keep an eye on these categories.")

    user_type = summary.get("user_type", "")
    if user_type == "Student":
        tips.append(
            "As a student with a limited allowance, try the 50/30/20 approach adapted for "
            "smaller budgets: prioritize essentials, allow a small amount for fun, and save "
            "whatever you can, even if it's a small fixed amount each month."
        )
    elif user_type == "Freelancer":
        tips.append(
            "Since your income varies month to month, base your fixed expenses on your "
            "lowest expected monthly income, and save a larger share of high-income months "
            "to smooth out the low-income ones. Building a 6-month emergency fund is "
            "especially important for freelancers."
        )

    tips.append(
        "Note: I'm currently running on offline rule-based analysis because the AI service "
        "is temporarily unavailable. This is still based on your real recorded data."
    )

    return "\n\n".join(tips)


def get_financial_advice(summary: dict, question: str = "") -> str:
    """Main entry point. Attempts a Gemini API call; falls back gracefully on any failure.

    Args:
        summary: dict produced by main.build_financial_summary()
        question: optional free-text question from the user (chatbot mode)
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        logger.info("GEMINI_API_KEY not set — using rule-based fallback advisor.")
        return _rule_based_fallback(summary, question)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)

        context = _build_financial_context(summary)
        system_instructions = (
            "You are a friendly, professional personal finance advisor embedded inside a "
            "budgeting app called 'Personal Finance Advisor Bot'. All amounts are in Indian "
            "Rupees (\u20b9). Use the user's real financial data below to give specific, "
            "actionable, encouraging advice. Keep responses concise (under 200 words), use "
            "short paragraphs or bullet points, and never invent numbers that were not "
            "provided. If the user asked a specific question, answer it directly first."
        )
        user_question = question.strip() if question else (
            "Give me a personalized budgeting and saving analysis based on my current data."
        )
        prompt = (
            f"{system_instructions}\n\n"
            f"--- USER FINANCIAL DATA ---\n{context}\n--- END DATA ---\n\n"
            f"User's question: {user_question}"
        )

        response = model.generate_content(prompt)
        text = getattr(response, "text", None)
        if not text:
            raise ValueError("Empty response from Gemini API")
        return text.strip()

    except Exception as exc:  # noqa: BLE001 - any failure must safely fall back
        logger.warning("Gemini API call failed, using fallback advisor: %s", exc)
        return _rule_based_fallback(summary, question)
