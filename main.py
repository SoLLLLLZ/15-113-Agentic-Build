"""
main.py - Entry point for the Amazing Python Quiz application.
"""

import getpass
import sys

import account
from menu import main_menu, run_survey
from quiz import load_questions

# ── ASCII Art ──────────────────────────────────────────────────────────────────

WELCOME_ART = r"""
         ~~~  ~~~  ~~~  ~~~
        ~                 ~
    /\^/\                /\^/\
   ( o  o )   AXOLOTL   ( o  o )
    \ == /    WELCOMES   \ == /
     \  /      YOU!       \  /
      \/~~~~~~~~~~~~~~~~~~\/
          \_____________/
               |   |
"""

GOODBYE_ART = r"""
          ~~~  ~~~  ~~~
         ~             ~
     /\^/\
    ( ^  ^ )   See you
     \ ~~ /    soon!
      \  /
       \/~~~~
        | |
        o o
"""


def _print_banner():
    print(WELCOME_ART)
    print("=" * 55)
    print("      Welcome to the Amazing Python Quiz!")
    print("=" * 55)


def _print_goodbye(username):
    print(GOODBYE_ART)
    print(f"  Goodbye, {username}!  Keep coding!")
    print("=" * 55)


# ── Auth flow ──────────────────────────────────────────────────────────────────

def _prompt_login():
    """Prompt for credentials and return (username, user_dict) or (None, None)."""
    attempts = 0
    while True:
        username = input("\n  Username: ").strip()
        if not username:
            print("  Username cannot be empty.")
            continue

        password = getpass.getpass("  Password: ")
        ok, result = account.login(username, password)

        if ok:
            print(f"\n  Welcome back, {username}!")
            return username, result

        print(f"\n  Error: {result}")
        attempts += 1
        retry = input("  Try again? (y/n): ").strip().lower()
        if retry != "y":
            return None, None


def _prompt_register():
    """Walk through account creation and return (username, user_dict) or (None, None)."""
    print("\n  ── Create a New Account ──")

    while True:
        username = input("  Choose a username (min 3 chars): ").strip()
        if len(username) < 3:
            print("  Username must be at least 3 characters.")
            continue

        # Check availability before asking for a password
        existing = account.load_users()
        if username in existing:
            print("  That username is already taken. Please choose another.")
            continue
        break

    while True:
        password = getpass.getpass("  Choose a password (min 4 chars): ")
        if len(password) < 4:
            print("  Password must be at least 4 characters.")
            continue
        confirm = getpass.getpass("  Confirm password: ")
        if password != confirm:
            print("  Passwords do not match. Try again.")
            continue
        break

    ok, message = account.create_account(username, password)
    if ok:
        print(f"\n  {message}  You're all set, {username}!")
        return username, {"survey_completed": False, "preferences": {}}

    print(f"\n  Error: {message}")
    return None, None


def _auth_gate():
    """Show login/register prompt and return (username, user_dict) or (None, None)."""
    while True:
        print(f"\n{'─' * 40}")
        print("  1. Log in")
        print("  2. Create account")
        print("  3. Exit")
        print(f"{'─' * 40}")

        choice = input("  Choice: ").strip()

        if choice == "1":
            return _prompt_login()
        elif choice == "2":
            return _prompt_register()
        elif choice == "3":
            return None, None
        else:
            print("  Invalid choice. Please enter 1, 2, or 3.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    _print_banner()

    questions = load_questions()
    if not questions:
        print(
            "\n  Critical error: Could not load questions.json.\n"
            "  Please ensure the file exists and is valid JSON.\n"
            "  Exiting."
        )
        sys.exit(1)

    while True:
        username, user_data = _auth_gate()

        if username is None:
            # User chose Exit from the auth gate
            print("\n  Thanks for visiting the Amazing Python Quiz!")
            break

        preferences = user_data.get("preferences", {})

        # First-time users see the survey automatically
        if not user_data.get("survey_completed", False):
            print("\n  First time here? Let's set up your quiz preferences.")
            preferences = run_survey(questions)
            account.update_preferences(username, preferences)

        # Run the main menu (loops until the user exits or changes username)
        username = main_menu(username, preferences, questions)

        # After the menu exits, show goodbye and ask if another user wants to play
        _print_goodbye(username)

        again = input("\n  Another user? (y/n): ").strip().lower()
        if again != "y":
            print("\n  Thanks for using the Amazing Python Quiz!\n")
            break


if __name__ == "__main__":
    main()
