"""
feedback.py - Handles OpenRouter API calls to provide AI feedback on quiz answers.
Uses openai/gpt-4o-mini via OpenRouter.
"""

import os
import json
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed; rely on environment variable being set manually

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"
TIMEOUT_SECONDS = 15


def _api_configured():
    return bool(OPENROUTER_API_KEY) and OPENROUTER_API_KEY != "your_api_key_here"


def get_answer_feedback(question_text, correct_answer, user_answer, is_correct):
    """
    Call the OpenRouter API and return a short feedback string.
    Falls back to a descriptive message if the API is unavailable or not configured.
    """
    if not _api_configured():
        return (
            "[AI feedback disabled — set OPENROUTER_API_KEY in your .env file "
            "to enable explanations.]"
        )

    if is_correct:
        prompt = (
            f"A student answered a Python quiz question correctly.\n"
            f"Question: {question_text}\n"
            f"Correct answer: {correct_answer}\n\n"
            f"Give a brief, encouraging explanation (2-3 sentences) of why this answer is correct."
        )
    else:
        prompt = (
            f"A student answered a Python quiz question incorrectly.\n"
            f"Question: {question_text}\n"
            f"Student's answer: {user_answer}\n"
            f"Correct answer: {correct_answer}\n\n"
            f"In 2-3 sentences, explain why the student's answer is wrong "
            f"and why the correct answer is right."
        )

    try:
        response = requests.post(
            url=API_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://python-quiz-app",
                "X-OpenRouter-Title": "Amazing Python Quiz",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
            }),
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:
        return "[AI feedback timed out. Please check your internet connection.]"
    except requests.exceptions.ConnectionError:
        return "[Could not reach the AI service. Please check your internet connection.]"
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        if status == 401:
            return "[Invalid API key. Please update OPENROUTER_API_KEY in your .env file.]"
        if status == 429:
            return "[AI service rate limit reached. Try again in a moment.]"
        return f"[AI service returned an error (HTTP {status}).]"
    except (KeyError, ValueError):
        return "[Received an unexpected response from the AI service.]"
    except Exception as exc:
        return f"[AI feedback unavailable: {exc}]"
