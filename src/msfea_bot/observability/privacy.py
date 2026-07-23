"""Best-effort anonymization of student-identifying data (CLAUDE.md §7).

Applied to the question BEFORE it is sent to the LLM or stored in logs. Removes:
- email addresses and long digit sequences (student IDs, phone numbers) via regex,
- personal names via local NER (spaCy `en_core_web_sm`, ADR-0009).

All local/offline, no per-use cost. Domain numbers that are not identifiers
("8 weeks", "3.3", "75%", "FEAA 500", "2-3 weeks") are deliberately preserved.

Fail-safe: if the NER model is unavailable, name redaction is skipped (with a
warning) and the regex redactions still apply — the app never crashes over it.
NER is not perfect (may miss unusual names or over-redact); see ADR-0009.
"""

from __future__ import annotations

import re
import warnings
from functools import lru_cache
from typing import Any

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# A digit, then >=5 digit/space/punct chars, then a digit: catches IDs and
# phone numbers (>=7 chars) without matching short domain numbers.
_LONG_NUMBER = re.compile(r"\b\d[\d\s().-]{5,}\d\b")


@lru_cache(maxsize=1)
def _ner() -> Any:
    """Load (and cache) the spaCy NER model, or None if it isn't installed."""
    try:
        import spacy

        return spacy.load("en_core_web_sm")
    except Exception as exc:  # noqa: BLE001 - degrade gracefully, never crash
        warnings.warn(
            f"NER model unavailable ({exc}); names will NOT be redacted. "
            "Install with: python -m spacy download en_core_web_sm",
            stacklevel=2,
        )
        return None


def _redact_names(text: str) -> str:
    nlp = _ner()
    if nlp is None:
        return text
    persons = [ent for ent in nlp(text).ents if ent.label_ == "PERSON"]
    # Replace back-to-front so earlier offsets stay valid.
    for ent in sorted(persons, key=lambda e: e.start_char, reverse=True):
        text = text[: ent.start_char] + "[redacted-name]" + text[ent.end_char :]
    return text


def anonymize(text: str) -> str:
    """Return the text with emails, long numbers, and personal names redacted."""
    text = _EMAIL.sub("[redacted-email]", text)
    text = _LONG_NUMBER.sub("[redacted-number]", text)
    text = _redact_names(text)
    return text
