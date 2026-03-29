# Code Review — Amazing Python Quiz

Reviewed against `SPEC.md` acceptance criteria, user workflow, error-handling requirements, and general code quality.

---

## Acceptance Criteria

1. **[PASS] App runs smoothly without errors** — Normal flow executes cleanly. No unguarded `sys.exit` calls except the intentional one in `main.py:147` when `questions.json` is missing.

2. **[PASS] All errors result in the user getting warned** — Invalid menu inputs, wrong passwords, empty usernames, and out-of-range question counts all produce user-facing messages rather than crashes. `feedback.py` never raises to the caller; it returns a descriptive fallback string.

3. **[PASS] Has memory for username and password** — `account.py` persists accounts to `data/users.json`. Passwords are hashed with PBKDF2-HMAC-SHA256 + a 16-byte hex salt (`account.py:43-49`). Usernames survive across sessions.

4. **[PASS] Supports local login and logout** — Login (`account.py:75-83`), logout (returning to the auth gate in `main.py:149-174`), and "Another user?" flow all work correctly.

5. **[PASS] API is connected and provides feedback** — `feedback.py` calls `openai/gpt-4o-mini` via OpenRouter after every answered question (`quiz.py:256-262`). Graceful fallback messages are returned for all error conditions.

---

## User Workflow (SPEC steps 1–9)

6. **[PASS] Step 2 — Axolotl art + title on launch** — `WELCOME_ART` ASCII art and "Welcome to the Amazing Python Quiz!" banner are printed in `main.py:39-43`.

7. **[PASS] Step 3 — Username/password prompt** — `_prompt_login()` and `_prompt_register()` in `main.py` handle both cases. `getpass` is used so the password is not echoed.

8. **[PASS] Step 4/5 — First-time survey; retakeable from menu** — Survey runs automatically for new users (`main.py:160-163`). "Retake Survey" is option 3 in `main_menu` (`menu.py:227-229`). Survey collects category, number of questions, and confidence level as specified.

9. **[PASS] Step 5 — Menu options** — All five options present: Start Quiz, Performance Statistics, Retake Survey, Account, Exit (`menu.py:209-214`).

10. **[PASS] Step 6 — Quiz uses survey preferences** — `run_quiz` reads `category` and `num_questions` from `preferences` (`quiz.py:199-200`).

11. **[PASS] Step 7 — AI feedback after each answer** — Called immediately after each answer in `quiz.py:256-262` with context for both correct and incorrect answers.

12. **[PASS] Step 8 — Score displayed at quiz end; stats updated** — Results summary printed in `quiz.py:283-290`. `account.update_user_stats` called in `menu.py:221`.

13. **[PASS] Step 9 — Goodbye message with axolotl art** — `_print_goodbye(username)` in `main.py:169` shows `GOODBYE_ART` and a personalised farewell.

---

## Error Handling (SPEC requirements)

14. **[PASS] Invalid input → warn and redisplay** — All input prompts loop on invalid input: menus (`menu.py:241-242`), multiple choice (`quiz.py:146-148`), true/false (`quiz.py:160-161`), short answer (`quiz.py:168-170`), survey (`menu.py:33-35`, `57-58`, `69-70`).

15. **[PASS] Incorrect password → warn and retry** — `_prompt_login` (`main.py:70-73`) prints the error and offers a retry prompt.

16. **[PASS] Score cannot go below zero** — `_update_score` in `quiz.py:182` uses `max(0, score - WRONG_PENALTY)`.

17. **[FAIL] Wrong-penalty message is inaccurate near score = 0** — `quiz.py:251` always prints `"-5 points"` regardless of whether the full penalty was applied. If `score` was 3, the player only loses 3 points (floor at 0), but the message still says "-5 points". Same issue if score is already 0. The `delta` variable returned from `_update_score` is never used in the display. **File:** `quiz.py:182-184, 251`.

18. **[PASS] Large question count → cap to max and notify** — `menu.py:49-54` prints a message and sets `num = max_q` when the user enters a number exceeding available questions.

---

## Feature Requirements

19. **[PASS] Three question types** — `multiple_choice`, `true_false`, and `short_answer` are all handled in `quiz.py:227-232`.

20. **[PASS] Questions in human-readable JSON** — `questions.json` is plain, well-structured JSON at the project root.

21. **[WARN] Stats file is not meaningfully secure** — `data/stats.dat` is Base64-encoded JSON (`account.py:141-145`). Base64 is trivially reversible (`base64 -d stats.dat`) and provides no real protection. The SPEC requires stats to be "not human-readable" and "relatively secure." Usernames are also visible after decoding. Consider encryption (e.g., `cryptography` library with a key derived from a secret) if real security is intended.

22. **[PASS] Passwords not easily discoverable** — PBKDF2-HMAC-SHA256 with 200,000 iterations and a per-user random salt (`account.py:43-49`). This is a strong, correct approach.

23. **[PASS] Question feedback influences selection** — Like/Dislike recorded in `data/question_feedback.json` (`quiz.py:60-65`). Liked questions get weight 1.8×, disliked 0.3×, neutral 1.0× in weighted sampling (`quiz.py:89-95`).

24. **[PASS] Account management screen** — Shows username + masked password + preferences. Allows password change (with current-password verification) and username change (`menu.py:122-193`).

---

## Bugs & Logic Errors

25. **[WARN] Streak bonus display is split from base points** — `quiz.py:246-249` prints "+10 points" and then "(5 streak bonus!)" separately. The actual score increase is their sum (e.g., 15), but there is no combined total shown. A player must add them mentally. Not a calculation bug, but a confusing UX.

26. **[FAIL] No minimum length enforced on username change** — `menu.py:184-193` (`_change_username`) does not enforce the 3-character minimum required in `_prompt_register` (`main.py:83-85`). A user can change their username to 1 or 2 characters.

27. **[WARN] Goodbye message uses old username after username change** — When a user changes their username, `show_account` returns `None`, `main_menu` returns, and `main.py:169` calls `_print_goodbye(username)` with the pre-change username. The goodbye says the old name. Minor UX issue.

28. **[WARN] `questions.json` fields are not validated** — `load_questions()` (`quiz.py:22-35`) checks that the file parses as JSON and is non-empty, but does not validate individual question structure. A question missing `"type"`, `"question"`, `"answer"`, or `"options"` (for multiple choice) will raise an unhandled `KeyError` mid-quiz. Example crash sites: `quiz.py:127, 136-137, 229`.

---

## Code Quality

29. **[WARN] `load_questions()` called redundantly** — Questions are loaded in `main.py:140` (for the survey), again in `menu.py:204` on every menu iteration, and again inside `run_quiz()` at `quiz.py:194`. Each quiz start triggers at least two file reads. `run_quiz` could accept a `questions` parameter instead.

30. **[PASS] File structure matches spec** — `account.py`, `quiz.py`, `menu.py`, `feedback.py`, and `main.py` map directly to the modules described in the spec notes.

31. **[WARN] No atomic file writes** — `account.py:37-38` and `account.py:142-145` write directly to the target file. If the process is killed mid-write, `users.json` or `stats.dat` will be corrupted. A safer pattern is to write to a `.tmp` file and then `os.replace()` it atomically.

32. **[PASS] `requirements.txt` present** — Lists `requests` and `python-dotenv`, covering all third-party dependencies.

---

## Security

33. **[WARN] Real API key stored in `.env`** — `.env` contains a live `OPENROUTER_API_KEY`. The file is correctly listed in `.gitignore` and will not be committed, but the key is present on disk in plaintext. This is standard practice for local dev; just ensure `.gitignore` is never bypassed and the key is rotated if the repo is ever made public.

34. **[PASS] `.env` is in `.gitignore`** — Confirmed: `.gitignore` contains `.env`. The clean git status confirms it is not tracked.

35. **[WARN] `data/users.json` written without directory check at call site** — `save_users` calls `_ensure_data_dir()` before writing (`account.py:36-37`), which is correct. However, `save_users` is public and if called from outside `account.py` before the dir exists it would fail — low risk since it is only used internally, but the guard should ideally be inside `save_users` itself (it isn't — it is only in `load_users`). Actually on re-read: `save_users` at line 35 does NOT call `_ensure_data_dir()` itself, only `load_users` does. If `save_users` is ever called without `load_users` having been called first, it will crash with `FileNotFoundError`. Currently all call paths go through `load_users` first, so this is not a live bug, but it is fragile. **File:** `account.py:35-38`.

---

## Summary

| Severity | Count |
|----------|-------|
| FAIL     | 2     |
| WARN     | 9     |
| PASS     | 24    |

**Critical fixes recommended:**
- `quiz.py:251` — Display the actual points lost (delta), not a hardcoded `-5`, when the score floor clips the penalty.
- `menu.py:184` — Enforce a minimum length (≥ 3 chars) on the new username in `_change_username`.
