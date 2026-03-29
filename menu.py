"""
menu.py - Handles survey, main menu, performance statistics, and account management.
"""

import getpass

import account
from quiz import get_categories, run_quiz


# ── Survey ─────────────────────────────────────────────────────────────────────

def run_survey(questions):
    """Walk the user through the setup survey and return a preferences dict."""
    print(f"\n{'─' * 50}")
    print("  Setup Survey — Let's personalise your quiz!")
    print(f"{'─' * 50}")

    categories = get_categories(questions)
    options = ["All"] + categories

    print("\n  Available categories:")
    for i, cat in enumerate(options, 1):
        print(f"    {i}. {cat}")

    while True:
        raw = input(f"\n  Choose a category (1-{len(options)}): ").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                category = options[idx]
                break
            print(f"  Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("  Invalid input. Please enter a number.")

    # Count how many questions exist for this category
    max_q = len(questions) if category == "All" else sum(
        1 for q in questions if q["category"] == category
    )

    while True:
        raw = input(f"\n  How many questions per quiz? (1–{max_q}): ").strip()
        try:
            num = int(raw)
            if num < 1:
                print("  Please enter at least 1.")
            elif num > max_q:
                print(
                    f"  That's more than the {max_q} questions available. "
                    f"Setting it to the maximum: {max_q}."
                )
                num = max_q
                break
            else:
                break
        except ValueError:
            print("  Invalid input. Please enter a number.")

    while True:
        raw = input(
            "\n  How confident are you in Python?\n"
            "  (1 = Complete beginner, 5 = Very experienced): "
        ).strip()
        try:
            conf = int(raw)
            if 1 <= conf <= 5:
                break
            print("  Please enter a number between 1 and 5.")
        except ValueError:
            print("  Invalid input. Please enter a number.")

    preferences = {"category": category, "num_questions": num, "confidence": conf}
    print(
        f"\n  Preferences saved!  Category: {category} | "
        f"Questions: {num} | Confidence: {conf}/5"
    )
    return preferences


# ── Statistics ─────────────────────────────────────────────────────────────────

def show_stats(username):
    stats = account.get_user_stats(username)

    print(f"\n{'=' * 55}")
    print(f"  Performance Statistics  —  {username}")
    print(f"{'=' * 55}")
    print(f"  Total quizzes taken   : {stats['total_quizzes']}")
    print(f"  Total questions seen  : {stats['total_questions']}")
    print(f"  Total correct answers : {stats['total_correct']}")

    if stats["total_questions"] > 0:
        acc = stats["total_correct"] / stats["total_questions"] * 100
        print(f"  Overall accuracy      : {acc:.1f}%")
    else:
        print("  Overall accuracy      : N/A (no quizzes taken yet)")

    print(f"  Cumulative score      : {stats['total_score']}")
    print(f"  Best single score     : {stats['best_score']}")
    print(f"  Best answer streak    : {stats['best_streak']}")

    history = stats.get("quiz_history", [])
    if history:
        print(f"\n  Recent quiz results (last 5):")
        for entry in history[-5:]:
            pct = (entry["correct"] / entry["total"] * 100) if entry["total"] else 0
            print(
                f"    Score {entry['score']:>4}  |  "
                f"{entry['correct']}/{entry['total']} correct ({pct:.0f}%)  |  "
                f"Category: {entry['category']}"
            )
    else:
        print("\n  No quiz history yet. Take a quiz to see results here!")

    print(f"{'=' * 55}")
    input("\n  Press Enter to return to the menu...")


# ── Account management ─────────────────────────────────────────────────────────

def show_account(username):
    """
    Display account info and provide options to change credentials.
    Returns the (possibly updated) username, or None if re-login is needed.
    """
    users = account.load_users()
    user = users.get(username, {})
    prefs = user.get("preferences", {})

    while True:
        print(f"\n{'─' * 50}")
        print("  Account Information")
        print(f"{'─' * 50}")
        print(f"  Username : {username}")
        print(f"  Password : {'*' * 10}")
        if prefs:
            print(f"\n  Quiz Preferences:")
            print(f"    Category   : {prefs.get('category', 'Not set')}")
            print(f"    Questions  : {prefs.get('num_questions', 'Not set')}")
            print(f"    Confidence : {prefs.get('confidence', 'Not set')}/5")
        print(f"\n{'─' * 50}")
        print("  1. Change password")
        print("  2. Change username  (requires re-login)")
        print("  3. Back to menu")
        print(f"{'─' * 50}")

        choice = input("\n  Choice: ").strip()

        if choice == "1":
            _change_password(username)
        elif choice == "2":
            success = _change_username(username)
            if success:
                return None  # caller must prompt re-login
        elif choice == "3":
            return username
        else:
            print("  Invalid choice. Please enter 1, 2, or 3.")


def _change_password(username):
    current = getpass.getpass("\n  Current password: ")
    ok, _ = account.login(username, current)
    if not ok:
        print("  Incorrect current password.")
        return

    new_pw = getpass.getpass("  New password: ")
    if len(new_pw) < 4:
        print("  Password must be at least 4 characters.")
        return
    confirm = getpass.getpass("  Confirm new password: ")
    if new_pw != confirm:
        print("  Passwords do not match.")
        return

    account.update_password(username, new_pw)
    print("  Password updated successfully.")


def _change_username(username):
    """Returns True if username was changed (caller should force re-login)."""
    new_name = input("\n  New username: ").strip()
    if not new_name:
        print("  Username cannot be empty.")
        return False
    if len(new_name) < 3:
        print("  Username must be at least 3 characters.")
        return False

    ok, msg = account.change_username(username, new_name)
    print(f"  {msg}")
    if ok:
        print("  Please log in again with your new username.")
    return ok


# ── Main menu loop ─────────────────────────────────────────────────────────────

def main_menu(username, preferences, questions):
    """
    Run the main menu loop.
    Returns the current username (may differ if user changed it).
    Exits when the user chooses 'Exit' or when re-login is needed.
    """
    while True:
        print(f"\n{'=' * 55}")
        print(f"  MAIN MENU   |   Logged in as: {username}")
        print(f"{'=' * 55}")
        print("  1. Start Quiz")
        print("  2. Performance Statistics")
        print("  3. Retake Survey")
        print("  4. Account")
        print("  5. Exit")
        print(f"{'=' * 55}")

        choice = input("\n  Choose an option (1–5): ").strip()

        if choice == "1":
            result = run_quiz(username, preferences, questions)
            if result:
                account.update_user_stats(username, result)
            input("\n  Press Enter to return to the menu...")

        elif choice == "2":
            show_stats(username)

        elif choice == "3":
            preferences = run_survey(questions)
            account.update_preferences(username, preferences)

        elif choice == "4":
            updated_username = show_account(username)
            if updated_username is None:
                # Username was changed; force re-login
                return username
            username = updated_username

        elif choice == "5":
            return username

        else:
            print("  Invalid choice. Please enter a number between 1 and 5.")
