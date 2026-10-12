# AI Tutor for Financial Literacy

## Project Overview

AI Tutor for Financial Literacy is a Streamlit-based educational
application designed to help learners understand practical personal
finance concepts through simple explanations and interactive tools.

The application uses Indian rupee (INR) examples and is designed for
beginner, intermediate and advanced learners.

## Features

### 1. Learn
Provides prepared lessons on eight financial-literacy topics:
- Budgeting and money management
- Saving and emergency funds
- Banking and digital payments
- Interest, loans and credit
- Inflation and purchasing power
- Insurance fundamentals
- Investing fundamentals
- Fraud prevention and financial safety

### 2. Ask the Tutor
Provides local, rule-based responses to recognized financial-literacy
keywords and questions. It does not currently use a live AI model to
generate answers.

### 3. Quiz
Offers topic-based financial-literacy questions, answer options and
explanations.

### 4. Budget Planner
Helps users explore income, expenses and savings through local
calculations.

## Technology Stack
- Python
- Streamlit
- python-dotenv
- OpenAI Python SDK (currently not used for live tutor responses)

## Requirements
- Python 3.13 or a compatible Python version
- pip
- The packages listed in requirements.txt

## Run on Windows

1. Extract the project folder.
2. Open PowerShell in that folder.
3. Create a virtual environment:

   python -m venv .venv

4. Activate it:

   .\.venv\Scripts\Activate.ps1

5. Install the dependencies:

   python -m pip install -r requirements.txt

6. Start the application:

   python -m streamlit run main.py

7. Open the local URL shown in the terminal, usually:

   http://localhost:8501

## Internet and API Usage

The current lesson content, rule-based tutor and budget calculations
are designed to run locally without OpenAI API calls. Internet access
is needed to install packages unless they are already available.

No OpenAI API key is required for the current local-mode functionality.

## Limitations

The tutor uses prepared lesson content and keyword-based responses.
It may not understand every question or provide a relevant answer to
unrecognized wording. It is an educational prototype, not a substitute
for qualified financial advice.

## Project Status

The four main application tabs have been tested locally:
Learn, Ask the Tutor, Quiz and Budget Planner.

Online deployment and testing on a separate computer must be verified
separately.
