"""
quiz.py - Handles question loading, question selection (weighted by user feedback),
quiz flow, scoring, and per-question user feedback recording.
"""

import json
import os
import random

from feedback import get_answer_feedback

QUESTIONS_FILE = "questions.json"
QUESTION_FEEDBACK_FILE = os.path.join("data", "question_feedback.json")

BASE_POINTS = 10
WRONG_PENALTY = 5
STREAK_BONUS = 5   # extra points per consecutive correct answer beyond the first


# ── Question loading ───────────────────────────────────────────────────────────

def load_questions():
    try:
        with open(QUESTIONS_FILE, "r") as f:
            data = json.load(f)
        raw = data.get("questions", [])
        if not raw:
            print("  Warning: questions.json contains no questions.")
            return []
        questions = []
        required = {"question", "type", "answer", "category"}
        for i, q in enumerate(raw):
            missing = required - q.keys()
            if missing:
                print(f"  Warning: question #{i + 1} skipped — missing fields: {', '.join(sorted(missing))}.")
                continue
            if q["type"] == "multiple_choice" and "options" not in q:
                print(f"  Warning: question #{i + 1} skipped — multiple_choice question missing 'options'.")
                continue
            questions.append(q)
        if not questions:
            print("  Warning: no valid questions found after validation.")
        return questions
    except FileNotFoundError:
        print("  Error: questions.json not found.")
        return []
    except json.JSONDecodeError:
        print("  Error: questions.json is malformed and could not be parsed.")
        return []


def get_categories(questions):
    return sorted({q["category"] for q in questions})


# ── Question feedback (like / dislike) ─────────────────────────────────────────

def _load_question_feedback():
    if not os.path.exists(QUESTION_FEEDBACK_FILE):
        return {}
    try:
        with open(QUESTION_FEEDBACK_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_question_feedback(feedback):
    os.makedirs("data", exist_ok=True)
    with open(QUESTION_FEEDBACK_FILE, "w") as f:
        json.dump(feedback, f, indent=2)


def record_question_feedback(username, question_text, liked):
    feedback = _load_question_feedback()
    if username not in feedback:
        feedback[username] = {}
    feedback[username][question_text] = "liked" if liked else "disliked"
    _save_question_feedback(feedback)


# ── Question selection ─────────────────────────────────────────────────────────

def select_questions(questions, category, num_questions, username):
    """
    Filter by category, then do weighted random sampling without replacement.
    Liked questions have a higher chance; disliked questions have a lower chance.
    """
    if category == "All":
        pool = questions[:]
    else:
        pool = [q for q in questions if q["category"] == category]

    if not pool:
        return []

    # Cap to what's available
    num_questions = min(num_questions, len(pool))

    feedback = _load_question_feedback()
    user_fb = feedback.get(username, {})

    def weight(q):
        fb = user_fb.get(q["question"], "neutral")
        if fb == "liked":
            return 1.8
        if fb == "disliked":
            return 0.3
        return 1.0

    selected = []
    remaining = [(q, weight(q)) for q in pool]

    for _ in range(num_questions):
        if not remaining:
            break
        total_weight = sum(w for _, w in remaining)
        pick = random.uniform(0, total_weight)
        cumulative = 0.0
        chosen_idx = len(remaining) - 1
        for i, (_, w) in enumerate(remaining):
            cumulative += w
            if pick <= cumulative:
                chosen_idx = i
                break
        selected.append(remaining[chosen_idx][0])
        remaining.pop(chosen_idx)

    return selected


# ── Answer helpers ─────────────────────────────────────────────────────────────

def _normalize(text):
    """Lowercase and remove all whitespace for flexible comparison."""
    return "".join(text.lower().split())


def check_answer(question, user_answer):
    correct = question["answer"]
    if question["type"] == "multiple_choice":
        return user_answer == correct
    # true_false and short_answer: case-insensitive, whitespace-insensitive
    return _normalize(user_answer) == _normalize(correct)


# ── Question prompt functions ──────────────────────────────────────────────────

def _ask_multiple_choice(question):
    options = question["options"]
    print(f"\n  {question['question']}")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        raw = input(f"\n  Your answer (1-{len(options)}): ").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print(f"  Invalid choice. Enter a number between 1 and {len(options)}.")
        except ValueError:
            print("  Invalid input. Please enter a number.")


def _ask_true_false(question):
    print(f"\n  {question['question']}")
    print("    1. True")
    print("    2. False")
    while True:
        raw = input("\n  Your answer (1 or 2): ").strip()
        if raw == "1":
            return "true"
        if raw == "2":
            return "false"
        print("  Invalid input. Please enter 1 for True or 2 for False.")


def _ask_short_answer(question):
    print(f"\n  {question['question']}")
    while True:
        raw = input("\n  Your answer: ").strip()
        if raw:
            return raw
        print("  Answer cannot be empty. Please type your answer.")


# ── Scoring ────────────────────────────────────────────────────────────────────

def _update_score(score, is_correct, streak):
    """Return (new_score, points_delta)."""
    if is_correct:
        streak_bonus = (streak - 1) * STREAK_BONUS if streak > 1 else 0
        delta = BASE_POINTS + streak_bonus
        return score + delta, delta
    else:
        new_score = max(0, score - WRONG_PENALTY)
        delta = new_score - score  # negative or zero
        return new_score, delta


# ── Main quiz runner ───────────────────────────────────────────────────────────

def run_quiz(username, preferences, questions):
    """
    Run a full quiz session.
    Returns a result dict, or None if the quiz could not start.
    """
    if not questions:
        print("\n  No questions available. Please check questions.json.")
        return None

    category = preferences.get("category", "All")
    num_questions = preferences.get("num_questions", 5)

    selected = select_questions(questions, category, num_questions, username)
    if not selected:
        print(f"\n  No questions found for category '{category}'.")
        return None

    actual_count = len(selected)
    if actual_count < num_questions:
        print(
            f"\n  Note: Only {actual_count} question(s) available for "
            f"'{category}'. That's all we've got!"
        )

    score = 0
    streak = 0
    best_streak = 0
    correct_count = 0

    print(f"\n{'=' * 55}")
    print(f"  Quiz Start  |  Category: {category}  |  Questions: {actual_count}")
    print(f"{'=' * 55}")

    for i, question in enumerate(selected, 1):
        q_type = question["type"]
        print(f"\n  ── Question {i}/{actual_count} ──  Score: {score}  Streak: {streak}")

        if q_type == "multiple_choice":
            user_answer = _ask_multiple_choice(question)
        elif q_type == "true_false":
            user_answer = _ask_true_false(question)
        else:
            user_answer = _ask_short_answer(question)

        is_correct = check_answer(question, user_answer)

        if is_correct:
            streak += 1
            best_streak = max(best_streak, streak)
            correct_count += 1
        else:
            streak = 0

        score, delta = _update_score(score, is_correct, streak)

        if is_correct:
            streak_msg = (
                f"  ({(streak - 1) * STREAK_BONUS} streak bonus!)" if streak > 1 else ""
            )
            print(f"\n  CORRECT! +{BASE_POINTS} points{streak_msg}  |  Score: {score}")
        else:
            print(f"\n  WRONG. -{abs(delta)} points  |  Score: {score}")
            print(f"  Correct answer: {question['answer']}")

        # AI feedback
        print("\n  Fetching AI explanation...")
        explanation = get_answer_feedback(
            question["question"],
            question["answer"],
            user_answer,
            is_correct,
        )
        print(f"\n  AI: {explanation}")

        # Question rating
        while True:
            rating = input(
                "\n  Rate this question — L=Like, D=Dislike, S=Skip: "
            ).strip().upper()
            if rating in ("L", "D", "S", ""):
                break
            print("  Please enter L, D, or S.")

        if rating == "L":
            record_question_feedback(username, question["question"], liked=True)
            print("  Saved: Liked")
        elif rating == "D":
            record_question_feedback(username, question["question"], liked=False)
            print("  Saved: Disliked")

    # ── Results ────────────────────────────────────────────────────────────────
    accuracy = (correct_count / actual_count * 100) if actual_count else 0.0

    print(f"\n{'=' * 55}")
    print("  QUIZ COMPLETE!")
    print(f"{'=' * 55}")
    print(f"  Final Score   : {score}")
    print(f"  Correct       : {correct_count} / {actual_count}")
    print(f"  Accuracy      : {accuracy:.1f}%")
    print(f"  Best Streak   : {best_streak}")
    print(f"{'=' * 55}")

    return {
        "score": score,
        "correct": correct_count,
        "questions_asked": actual_count,
        "best_streak": best_streak,
        "accuracy": accuracy,
        "category": category,
    }
