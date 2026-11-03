"""
Draft final-exam questions from lesson notes with Claude (optional).

Only drafts: nothing is saved here. The instructor sees every draft in the exam
editor, edits or deletes it, and saves the ones they approve. Every draft goes
through the same ExamQuestionWrite validation as a hand-written question, so a
malformed draft is dropped instead of reaching the bank.

Needs ANTHROPIC_API_KEY in the server environment; without it the endpoint
answers 503 with a plain explanation.
"""

from __future__ import annotations

import json
import logging
import re

import httpx

from app.core.config import settings
from app.schemas.exam import ExamQuestionWrite

logger = logging.getLogger(__name__)

API_URL = "https://api.anthropic.com/v1/messages"

PROMPT = """You are an experienced exam writer for WAMUGII TECH SOLUTIONS, an online school in Rwanda.
Write {count} final-exam questions in simple, clear English for the course "{course}", based ONLY on the lesson notes below.

Use a mix of these question types: {kinds}.
Rules:
- SINGLE: 4 options, exactly 1 correct.
- MULTIPLE: 4 or 5 options, 2 or 3 correct.
- TRUE_FALSE: a clear statement that is definitely true or definitely false.
- FILL_BLANK: one sentence with the missing word or number shown as ___ ; give 1-3 accepted answers (short).
- Test understanding, not memory of exact wording. No trick questions. Wrong options must be believable.
- "topic" is the week/module the question comes from.
- "correct" is a list of option numbers starting at 0 (for FILL_BLANK: the accepted answers as strings).

Reply with ONLY a JSON array, no other text. Each item:
{{"kind": "SINGLE|MULTIPLE|TRUE_FALSE|FILL_BLANK", "question": "...", "options": ["..."], "correct": [0], "explanation": "one sentence", "topic": "..."}}

LESSON NOTES:
{notes}
"""


class AiDraftError(Exception):
    pass


def is_available() -> bool:
    return bool(settings.ANTHROPIC_API_KEY)


def draft_questions(course_title: str, lessons: list[tuple[str, str, str]], count: int, kinds: list[str]) -> list[ExamQuestionWrite]:
    """`lessons` is a list of (module_title, lesson_title, content)."""
    if not is_available():
        raise AiDraftError("AI drafting is not set up on this server (ANTHROPIC_API_KEY is missing).")

    notes = []
    budget = 60000  # characters of notes sent, to keep the request small
    for module, title, content in lessons:
        chunk = f"\n### {module or ''} — {title}\n{content}\n"
        if budget - len(chunk) < 0:
            chunk = chunk[: max(0, budget)]
        notes.append(chunk)
        budget -= len(chunk)
        if budget <= 0:
            break

    prompt = PROMPT.format(count=count, course=course_title, kinds=", ".join(kinds), notes="".join(notes))
    try:
        resp = httpx.post(
            API_URL,
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY or "",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.AI_DRAFT_MODEL,
                "max_tokens": 8000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
    except httpx.HTTPError as exc:
        logger.warning("AI draft request failed: %s", exc)
        raise AiDraftError("Could not reach the AI service. Please try again later.") from exc
    if resp.status_code != 200:
        logger.warning("AI draft HTTP %s: %s", resp.status_code, resp.text[:500])
        raise AiDraftError(f"The AI service returned an error ({resp.status_code}).")

    text = "".join(block.get("text", "") for block in resp.json().get("content", []) if block.get("type") == "text")
    match = re.search(r"\[.*\]", text, re.S)
    if not match:
        raise AiDraftError("The AI reply could not be read. Please try again.")
    try:
        raw = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise AiDraftError("The AI reply could not be read. Please try again.") from exc

    drafts: list[ExamQuestionWrite] = []
    for item in raw if isinstance(raw, list) else []:
        try:
            drafts.append(ExamQuestionWrite.model_validate(item))
        except Exception:  # noqa: BLE001 -- a bad draft is skipped, not fatal
            continue
    return drafts
