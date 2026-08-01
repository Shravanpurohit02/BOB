from __future__ import annotations

from enum import Enum


class Intent(str, Enum):
    IMPLEMENT = "implement"
    ANALYZE = "analyze"
    AUDIT = "audit"
    QUESTION = "question"


QUESTION_WORDS = {
    "what",
    "which",
    "who",
    "where",
    "when",
    "why",
    "how",
}


IMPLEMENT_WORDS = {
    "create",
    "implement",
    "generate",
    "build",
    "write",
    "modify",
    "fix",
    "repair",
    "refactor",
}


class IntentClassifier:

    def classify(
        self,
        objective: str,
    ) -> Intent:

        text = objective.lower().strip()

        if "audit" in text:
            return Intent.AUDIT

        if "analyze" in text or "analyse" in text:
            return Intent.ANALYZE

        first = text.split()[0] if text.split() else ""

        if first in QUESTION_WORDS or text.endswith("?"):
            return Intent.QUESTION

        if any(word in text for word in IMPLEMENT_WORDS):
            return Intent.IMPLEMENT

        return Intent.IMPLEMENT


classifier = IntentClassifier()
