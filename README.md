# Amazing Python Quiz

A command-line Python quiz app that tests your Python knowledge with multiple choice, true/false, and short answer questions. Tracks your scores, streaks, and performance statistics across sessions.

---

## Prerequisites

- Python 3.8 or newer

---

## Installation

1. Download or clone this repository.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the App

```bash
python main.py
```

That's it. The app will guide you through creating an account (or logging in) and walk you through the rest.

---

## AI Feedback (Optional)

After each answer the app can give an AI-generated explanation of why the answer is correct or incorrect. This requires a free API key from [OpenRouter](https://openrouter.ai).

**Without a key:** the app still runs fully — you just see a placeholder message instead of an AI explanation.

**To enable AI feedback:**

1. Create a free account at [openrouter.ai](https://openrouter.ai) and generate an API key.
2. Create a file named `.env` in the project root.
3. Add the following line to it:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```

---

## Question Bank

Questions live in `questions.json` at the project root. The file is plain, human-readable JSON — you can open it in any text editor to add, remove, or edit questions. Each question needs a `type` (`multiple_choice`, `true_false`, or `short_answer`), a `category`, and an `answer`. Multiple choice questions also need an `options` list.

---

## File Overview

| File | Purpose |
|---|---|
| `main.py` | Entry point — handles startup, auth flow, and the top-level loop |
| `account.py` | Account creation, login, password hashing, and stats persistence |
| `quiz.py` | Question loading/validation, quiz flow, scoring, and question feedback |
| `menu.py` | Main menu, survey, performance statistics, and account management screens |
| `feedback.py` | OpenRouter API calls for AI answer explanations |
| `questions.json` | The question bank (human-readable, easy to edit) |
