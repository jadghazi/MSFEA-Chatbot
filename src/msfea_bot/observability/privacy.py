"""Best-effort anonymization of student-identifying data (CLAUDE.md §7).

Applied to the question BEFORE it is sent to the LLM or stored in logs. Strips
the identifiers we can detect reliably: email addresses and long digit sequences
(student IDs, phone numbers).

Known limitation: this does NOT reliably strip personal names (that needs NER).
Documented in ADR-0007. Domain numbers that are not identifiers ("8 weeks",
"3.3", "75%", "FEAA 500", "2-3 weeks") are deliberately preserved.
"""

from __future__ import annotations

import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# A digit, then >=5 digit/space/punct chars, then a digit: catches IDs and
# phone numbers (>=7 chars) without matching short domain numbers.
_LONG_NUMBER = re.compile(r"\b\d[\d\s().-]{5,}\d\b")


def anonymize(text: str) -> str:
    """Return the text with emails and long numbers redacted."""
    text = _EMAIL.sub("[redacted-email]", text)
    text = _LONG_NUMBER.sub("[redacted-number]", text)
    return text
