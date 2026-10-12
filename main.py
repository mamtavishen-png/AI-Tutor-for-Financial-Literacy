import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError
from openai import APIConnectionError, APIStatusError

load_dotenv()

MODEL = "gpt-5.4-mini"

INSTRUCTIONS = """
You are a friendly financial-literacy tutor for learners in India.
Explain financial concepts in simple language with practical INR examples.
Adapt explanations to the learner's level.
Teach budgeting, saving, banking, interest, loans, inflation, insurance,
investing fundamentals, and financial safety.
Never promise profits or guaranteed outcomes.
Never ask for passwords, PINs, OTPs, or bank account details.
Provide financial education, not personalized investment advice.
"""

TOPICS = [
    "Budgeting and money management",
    "Saving and emergency funds",
    "Banking and digital payments",
    "Interest, loans and credit",
    "Inflation and purchasing power",
    "Insurance fundamentals",
    "Investing fundamentals",
    "Fraud prevention and financial safety",
]

st.set_page_config(
    page_title="AI Tutor for Financial Literacy",
    page_icon="📘",
    layout="wide",
)

st.title("📘 AI Tutor for Financial Literacy")
st.caption(
    "Learn practical money skills through lessons, conversation, "
    "quizzes, and a monthly budget planner."
)

with st.sidebar:
    st.header("Your learning profile")
    level = st.selectbox(
        "Choose your level",
        ["Beginner", "Intermediate", "Advanced"],
    )
    topic = st.selectbox("Choose a topic", TOPICS)
    st.caption("Currency: Indian rupees (₹)")

LOCAL_LESSONS = {
    "Budgeting and money management": """
## Understanding a budget

A budget is a plan for how you will use your money.

**Example:** If your monthly take-home income is ₹30,000 and your
expenses total ₹20,000, you have ₹10,000 remaining.

**Try these steps:**
1. Record your monthly income.
2. List essential expenses, debt payments and other spending.
3. Set a realistic savings goal.
4. Review your spending regularly.

**Key takeaways**
- A budget helps you understand where your money goes.
- Include irregular expenses as well as monthly bills.
- Adjust your plan when your circumstances change.

**Reflection:** Which expense could you review this month?
""",
    "Saving and emergency funds": """
## Building a savings habit

Saving means setting aside part of your income for future needs.

An emergency fund can help cover unexpected essential costs, such as
urgent repairs or a temporary loss of income.

**Example:** Saving ₹1,000 per month adds up to ₹12,000 over a year,
before any interest.

Start with an achievable amount, keep emergency savings accessible,
and build your fund gradually according to your circumstances.

**Reflection:** What is one realistic amount you could set aside?
""",
    "Banking and digital payments": """
## Banking and digital payments

Banks provide services such as deposits, transfers and account
statements. Digital payments can make transactions convenient, but
you must protect your credentials.

**Remember:**
- Never share your OTP, PIN or password.
- Verify the recipient before confirming a payment.
- Check transaction alerts and account statements.
- Contact your bank through an independently verified channel if
  you suspect fraud.

A person sending you money does not need your UPI PIN to complete
the receipt of that money.

**Reflection:** How would you verify an unexpected payment request?
""",
    "Interest, loans and credit": """
## Understanding interest and borrowing

Interest is the cost of borrowing money or the return earned on
certain savings.

**Example:** If you borrow ₹1,000 and repay ₹1,100 in total, the
extra amount paid is ₹100. Actual loan costs may also include fees.

Before borrowing, compare the interest rate, total repayment,
repayment schedule, fees and consequences of missed payments.

**Key takeaway:** A smaller monthly instalment does not always mean
a loan is cheaper overall.

**Reflection:** What would you check before accepting a loan?
""",
    "Inflation and purchasing power": """
## What is inflation?

Inflation is a general rise in prices over time. When prices rise,
the same amount of money may buy fewer goods and services.

**Example:** If an item costs ₹100 and its price rises by 5%, it
will cost ₹105.

If your income does not keep pace with rising prices, your
purchasing power may fall. Actual price changes differ across items.

**Reflection:** Which household expenses have you noticed changing?
""",
    "Insurance fundamentals": """
## Why insurance matters

Insurance can help protect against specified financial risks in
exchange for a premium, subject to the policy's terms.

Different policies cover different risks. For example, health
insurance may cover eligible medical expenses, while motor insurance
addresses specified vehicle-related risks.

Before buying a policy, review its coverage, exclusions, waiting
periods, deductibles, premium and claim requirements.

Insurance does not eliminate every risk or guarantee a payout for
every event.

**Reflection:** What risk would you want to understand better?
""",
    "Investing fundamentals": """
## Introduction to investing

Investing involves putting money into assets with the aim of
achieving future financial goals. Investments can rise or fall in
value, and returns are not guaranteed.

Important concepts include:
- **Risk:** The possibility of losing money or receiving uncertain
  returns.
- **Diversification:** Spreading investments across different
  assets to reduce reliance on a single holding.
- **Time horizon:** How long you expect to invest.
- **Costs:** Fees and charges that can affect your outcome.

Understand an investment before committing money. Past performance
does not guarantee future results.

**Reflection:** What financial goal and time horizon are you
planning to learn about?
""",
    "Fraud prevention and financial safety": """
## Protect yourself from financial fraud

Fraudsters may impersonate banks, government agencies, employers
or people you know.

**Protect yourself:**
- Never disclose your OTP, UPI PIN or banking password.
- Do not install unknown apps at a caller's request.
- Do not approve payment requests you do not understand.
- Verify suspicious messages using an official channel.
- Act promptly through your bank if you suspect fraud.

Do not rely on caller ID or a familiar-looking message alone.

**Reflection:** What would you do if someone urgently requested
your banking OTP?
""",
}


def ask_tutor(prompt):
    # Accept either a lesson prompt or the chat's message history.
    if isinstance(prompt, list):
        user_messages = [
            message["content"]
            for message in prompt
            if message.get("role") == "user"
        ]
        question = str(user_messages[-1]) if user_messages else ""
    else:
        question = str(prompt)

    # Guided lessons use prepared content and require no API call.
    if question.startswith("Teach a short lesson on"):
        return LOCAL_LESSONS.get(
            topic,
            "Please select a financial-literacy topic."
        )

    # Provide simple, topic-relevant explanations locally.
    text = question.casefold()

    answers = {
        "budget": (
            "A budget compares your income with your expenses. "
            "List essential costs, debt payments and other spending, "
            "then plan a realistic savings amount."
        ),
        "sav": (
            "Start by choosing a realistic savings amount and setting "
            "it aside regularly. An emergency fund can help with "
            "unexpected essential expenses."
        ),
        "interest": (
            "Interest is the cost of borrowing or the return earned "
            "on certain savings. Compare rates, fees and the total "
            "amount payable before making a decision."
        ),
        "loan": (
            "Before taking a loan, compare the interest rate, fees, "
            "total repayment, schedule and consequences of missed "
            "payments. Borrow only after understanding the terms."
        ),
        "inflation": (
            "Inflation is a general rise in prices. If prices rise "
            "while your income stays unchanged, your money may buy "
            "fewer goods and services."
        ),
        "insurance": (
            "Insurance helps manage specified financial risks. "
            "Read the coverage, exclusions, premium and claim terms "
            "carefully; not every event is covered."
        ),
        "invest": (
            "Investments involve risk, and returns are not guaranteed. "
            "Learn about risk, diversification, costs and your time "
            "horizon before making investment decisions."
        ),
        "upi": (
            "Never share your UPI PIN or OTP. Verify payment requests "
            "and contact your bank through an official channel if "
            "you suspect fraud."
        ),
        "fraud": (
            "Never share an OTP, PIN or password. Verify suspicious "
            "requests independently, avoid unknown apps, and contact "
            "your bank promptly if you suspect fraud."
        ),
        "bank": (
            "Use official banking channels, check transaction alerts, "
            "and protect your PIN, password and OTP. Never disclose "
            "these credentials to someone contacting you."
        ),
        "credit": (
            "Credit allows you to borrow money that must be repaid "
            "under agreed terms. Compare interest, fees, repayment "
            "obligations and your ability to repay."
        ),
    }

    for keyword, answer in answers.items():
        if keyword in text:
            return (
                f"**Local financial-literacy tutor**\n\n{answer}\n\n"
                "This is general education, not personalized "
                "financial advice. Would you like an example?"
            )

    return (
        "**Local financial-literacy tutor**\n\n"
        f"Let's explore **{topic}**.\n\n"
        f"{LOCAL_LESSONS.get(topic, 'Choose a topic to get started.')}"
        "\n\nYou can ask about budgeting, saving, interest, loans, "
        "inflation, insurance, investing, banking or fraud prevention."
    )

lesson_tab, chat_tab, quiz_tab, budget_tab = st.tabs(
    ["📖 Learn", "💬 Ask the Tutor", "🧠 Quiz", "💰 Budget Planner"]
)

with lesson_tab:
    st.subheader("Your guided lesson")
    st.write(f"**Topic:** {topic} | **Level:** {level}")

    if st.button("Generate my lesson", type="primary"):
        with st.spinner("Preparing your lesson..."):
            try:
                st.session_state["lesson"] = ask_tutor(
                    f"Teach a short lesson on {topic}. "
                    "Include an Indian rupee example, three takeaways, "
                    "and one reflection question."
                )
            except AuthenticationError:
                st.error("API authentication failed. Check your API key.")
            except RateLimitError:
                st.error("API quota or rate limit issue. Check your account.")
            except APIConnectionError:
                st.error("Connection failed. Check your internet.")
            except APIStatusError as exc:
                st.error(f"OpenAI API error: HTTP {exc.status_code}")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")

    if st.session_state.get("lesson"):
        st.markdown(st.session_state["lesson"])


with chat_tab:
    st.subheader("Ask a financial-literacy question")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "For example: How do I start saving money?"
    )

    if question:
        st.session_state["messages"].append(
            {"role": "user", "content": question}
        )
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_tutor(
                        st.session_state["messages"][-12:]
                    )
                    st.markdown(answer)
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": answer}
                    )
                except AuthenticationError:
                    st.error("API authentication failed. Check your API key.")
                except RateLimitError:
                    st.error("API quota or rate limit issue. Check your account.")
                except APIConnectionError:
                    st.error("Connection failed. Check your internet.")
                except APIStatusError as exc:
                    st.error(f"OpenAI API error: HTTP {exc.status_code}")
                except Exception as exc:
                    st.error(f"Unexpected error: {exc}")

    if st.button("Clear conversation"):
        st.session_state["messages"] = []
        st.rerun()

QUIZZES = {
    "Budgeting and money management": {
        "question": "Your monthly income is ₹20,000 and expenses are ₹17,000. How much remains?",
        "options": ["₹2,000", "₹3,000", "₹4,000", "₹17,000"],
        "answer": "₹3,000",
        "explanation": "₹20,000 minus ₹17,000 equals ₹3,000.",
    },
    "Saving and emergency funds": {
        "question": "What is an emergency fund mainly for?",
        "options": [
            "Routine shopping",
            "Unexpected essential expenses",
            "Luxury purchases",
            "Guaranteed profits",
        ],
        "answer": "Unexpected essential expenses",
        "explanation": "It helps cover unexpected costs, such as urgent repairs.",
    },
    "Banking and digital payments": {
        "question": "Someone asks for your banking OTP to give you a prize. What should you do?",
        "options": [
            "Share it immediately",
            "Post it online",
            "Never share it and verify the claim",
            "Share it if they know your name",
        ],
        "answer": "Never share it and verify the claim",
        "explanation": "Never disclose an OTP, PIN, or password.",
    },
    "Interest, loans and credit": {
        "question": "You borrow ₹1,000 and repay ₹1,100. How much extra did you pay?",
        "options": ["₹10", "₹100", "₹1,000", "₹1,100"],
        "answer": "₹100",
        "explanation": "₹1,100 minus ₹1,000 equals ₹100.",
    },
    "Inflation and purchasing power": {
        "question": "If prices rise but your income stays the same, what generally happens?",
        "options": [
            "Your money buys more",
            "Your money buys less",
            "Nothing changes",
            "Your income automatically rises",
        ],
        "answer": "Your money buys less",
        "explanation": "Inflation reduces purchasing power when income does not keep pace.",
    },
    "Insurance fundamentals": {
        "question": "What is a key purpose of insurance?",
        "options": [
            "Eliminate every risk",
            "Help manage specified financial risks",
            "Guarantee investment profits",
            "Replace all savings",
        ],
        "answer": "Help manage specified financial risks",
        "explanation": "Coverage depends on the policy terms and exclusions.",
    },
    "Investing fundamentals": {
        "question": "Which statement about investments is most accurate?",
        "options": [
            "All investments guarantee profits",
            "Higher returns never involve risk",
            "Investments can rise or fall in value",
            "Past performance guarantees future results",
        ],
        "answer": "Investments can rise or fall in value",
        "explanation": "Investment losses are possible; understand risk before investing.",
    },
    "Fraud prevention and financial safety": {
        "question": "A caller claiming to be your bank asks for your UPI PIN. What is safest?",
        "options": [
            "Tell them the PIN",
            "Install their unknown app",
            "Share your screen",
            "Never share the PIN; contact your bank independently",
        ],
        "answer": "Never share the PIN; contact your bank independently",
        "explanation": "Never disclose your UPI PIN or install unknown remote-access apps at a caller's request.",
    },
}


with quiz_tab:
    st.subheader("Check your understanding")
    quiz = QUIZZES[topic]
    st.write(f"**Question:** {quiz['question']}")

    selected_answer = st.radio(
        "Choose one answer",
        quiz["options"],
        key=f"quiz_{topic}",
    )

    if st.button("Check answer"):
        st.session_state["quiz_result"] = {
            "topic": topic,
            "selected": selected_answer,
            "correct": quiz["answer"],
            "explanation": quiz["explanation"],
        }

    result = st.session_state.get("quiz_result")

    if result and result["topic"] == topic:
        if result["selected"] == result["correct"]:
            st.success("Correct! Well done.")
        else:
            st.warning(f"Correct answer: {result['correct']}")
        st.info(result["explanation"])


with budget_tab:
    st.subheader("Monthly budget planner")
    st.write(
        "Enter monthly amounts in rupees. Calculations happen locally "
        "in the app and are not sent to the AI tutor."
    )

    income = st.number_input(
        "Monthly take-home income (₹)",
        min_value=0,
        value=30000,
        step=1000,
    )

    col1, col2 = st.columns(2)

    with col1:
        housing = st.number_input(
            "Housing and utilities (₹)",
            min_value=0,
            value=8000,
            step=500,
        )
        food = st.number_input(
            "Food and groceries (₹)",
            min_value=0,
            value=5000,
            step=500,
        )
        transport = st.number_input(
            "Transport (₹)",
            min_value=0,
            value=2000,
            step=500,
        )

    with col2:
        debt = st.number_input(
            "Loan and debt payments (₹)",
            min_value=0,
            value=2000,
            step=500,
        )
        other = st.number_input(
            "Other expenses (₹)",
            min_value=0,
            value=3000,
            step=500,
        )
        savings_goal = st.number_input(
            "Desired monthly savings (₹)",
            min_value=0,
            value=5000,
            step=500,
        )

    expenses = housing + food + transport + debt + other
    balance = income - expenses
    remaining_after_goal = balance - savings_goal
    savings_rate = balance / income * 100 if income else 0

    st.divider()
    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Monthly expenses", f"₹{expenses:,.0f}")
    metric2.metric("Money left", f"₹{balance:,.0f}")
    metric3.metric(
        "After savings goal",
        f"₹{remaining_after_goal:,.0f}",
    )

    if balance < 0:
        st.error("Your listed expenses exceed your income.")
    elif remaining_after_goal < 0:
        st.warning(
            "Your current balance is below your savings goal. "
            "Review your expenses or adjust the goal."
        )
    else:
        st.success(
            f"Your budget leaves ₹{balance:,.0f}. "
            f"If you save that full amount, the estimated savings rate "
            f"is {savings_rate:.1f}%."
        )

    st.caption(
        "Planning estimate only. Include irregular expenses and avoid "
        "counting the same expense twice."
    )


st.divider()
st.caption(
    "Educational tool only. It does not guarantee financial outcomes "
    "or provide personalized investment recommendations."
)
