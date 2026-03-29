"""
account.py - Handles user account creation, login, and data persistence.
Passwords are hashed with PBKDF2-HMAC-SHA256 + salt (not human-readable).
Performance stats are Base64-encoded so they are not easily human-readable.
"""

import json
import os
import hashlib
import secrets
import base64

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
STATS_FILE = os.path.join(DATA_DIR, "stats.dat")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


# ── User file helpers ──────────────────────────────────────────────────────────

def load_users():
    _ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_users(users):
    _ensure_data_dir()
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ── Password helpers ───────────────────────────────────────────────────────────

def _hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000
    )
    return salt, hashed.hex()


def _verify_password(password, salt, stored_hash):
    _, new_hash = _hash_password(password, salt)
    return new_hash == stored_hash


# ── Account actions ────────────────────────────────────────────────────────────

def create_account(username, password):
    """Return (success: bool, message: str)."""
    users = load_users()
    if username in users:
        return False, "Username already exists."
    salt, hashed = _hash_password(password)
    users[username] = {
        "salt": salt,
        "password": hashed,
        "survey_completed": False,
        "preferences": {},
    }
    save_users(users)
    return True, "Account created successfully."


def login(username, password):
    """Return (success: bool, user_dict or error_message)."""
    users = load_users()
    if username not in users:
        return False, "Username not found."
    user = users[username]
    if not _verify_password(password, user["salt"], user["password"]):
        return False, "Incorrect password."
    return True, user


def update_preferences(username, preferences):
    users = load_users()
    if username not in users:
        return False
    users[username]["preferences"] = preferences
    users[username]["survey_completed"] = True
    save_users(users)
    return True


def update_password(username, new_password):
    users = load_users()
    if username not in users:
        return False
    salt, hashed = _hash_password(new_password)
    users[username]["salt"] = salt
    users[username]["password"] = hashed
    save_users(users)
    return True


def change_username(old_username, new_username):
    """Rename a user entry. Returns (success, message)."""
    users = load_users()
    if old_username not in users:
        return False, "Original username not found."
    if new_username in users:
        return False, "That username is already taken."
    users[new_username] = users.pop(old_username)
    save_users(users)
    # Also migrate stats
    stats = _load_stats()
    if old_username in stats:
        stats[new_username] = stats.pop(old_username)
        _save_stats(stats)
    return True, f"Username changed to '{new_username}'."


# ── Stats helpers (Base64-encoded JSON — not easily human-readable) ────────────

def _load_stats():
    _ensure_data_dir()
    if not os.path.exists(STATS_FILE):
        return {}
    try:
        with open(STATS_FILE, "r") as f:
            encoded = f.read().strip()
        if not encoded:
            return {}
        decoded = base64.b64decode(encoded).decode("utf-8")
        return json.loads(decoded)
    except Exception:
        return {}


def _save_stats(stats):
    _ensure_data_dir()
    encoded = base64.b64encode(json.dumps(stats).encode("utf-8")).decode("utf-8")
    with open(STATS_FILE, "w") as f:
        f.write(encoded)


def _blank_stats():
    return {
        "total_quizzes": 0,
        "total_questions": 0,
        "total_correct": 0,
        "total_score": 0,
        "best_score": 0,
        "best_streak": 0,
        "quiz_history": [],
    }


def get_user_stats(username):
    stats = _load_stats()
    return stats.get(username, _blank_stats())


def update_user_stats(username, quiz_result):
    """Merge a quiz result into the user's lifetime stats."""
    stats = _load_stats()
    if username not in stats:
        stats[username] = _blank_stats()
    s = stats[username]
    s["total_quizzes"] += 1
    s["total_questions"] += quiz_result["questions_asked"]
    s["total_correct"] += quiz_result["correct"]
    s["total_score"] += quiz_result["score"]
    if quiz_result["score"] > s["best_score"]:
        s["best_score"] = quiz_result["score"]
    if quiz_result["best_streak"] > s["best_streak"]:
        s["best_streak"] = quiz_result["best_streak"]
    s["quiz_history"].append({
        "score": quiz_result["score"],
        "correct": quiz_result["correct"],
        "total": quiz_result["questions_asked"],
        "category": quiz_result["category"],
    })
    _save_stats(stats)
