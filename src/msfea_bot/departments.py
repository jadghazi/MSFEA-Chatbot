"""The MSFEA department registry (backlog B-1 / B-2).

Two things depend on knowing a student's department:

1. **Escalation routing (B-1).** When the bot can't answer, sending the student to
   the coordinator who actually owns their department is a better deflection than a
   generic address — it still keeps the email off the wrong professor's desk.
2. **Department-conditional rules (B-2).** Several internship rules differ by
   department (MECH forbids splitting an internship; CEE allows it when at least
   one period is civil/construction). Answering with another department's rule is
   exactly the confidently-wrong answer CLAUDE.md §1 forbids.

**The source of truth is the knowledge base, not this file.** Contacts come from the
"Department Contacts" table and the abbreviations from the "Department-Specific
Rules" headings in `kb/normalized/summer-training-guidelines-2026.md`. This table
exists because routing needs a lookup that cannot depend on a retrieval hit, and
because B-1 asks for contacts as *data* rather than a hard-coded constant.
`tests/test_departments.py` asserts every address here still appears in that
document, so the two cannot drift apart silently.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Department:
    """One MSFEA department: how to name it, and who owns its questions."""

    code: str  # stable identifier used on the wire and in chunk metadata
    abbr: str  # as written in the KB headings, e.g. "MECH"
    label: str  # human-readable name shown to the student
    contact_name: str
    contact_email: str


DEPARTMENTS: tuple[Department, ...] = (
    Department("mech", "MECH", "Mechanical Engineering", "Elie Kfoury", "ek15@aub.edu.lb"),
    Department(
        "ece", "ECE", "Electrical and Computer Engineering", "Rafika Dinnawi", "rd39@aub.edu.lb"
    ),
    Department("chem", "CHEM", "Chemical Engineering", "Adnan Itani", "ai34@aub.edu.lb"),
    Department(
        "iem", "IEM", "Industrial Engineering and Management", "Maysaa Jaafar", "mj73@aub.edu.lb"
    ),
    Department(
        "cee", "CEE", "Civil and Environmental Engineering", "Hiam Khoury", "hk50@aub.edu.lb"
    ),
)

_BY_CODE = {d.code: d for d in DEPARTMENTS}

# Shown when the student hasn't told us their department, or picked "not sure".
GENERAL_CONTACT = "fcareer@aub.edu.lb"


def from_code(code: str | None) -> Department | None:
    """Look up a department by its wire code. Unknown/absent -> None.

    The code arrives from the browser, so it is untrusted: anything not on the
    known list is treated as "no department given" rather than passed along.
    """
    if not code:
        return None
    return _BY_CODE.get(code.strip().lower())


def from_heading(heading: str) -> Department | None:
    """Identify the department a KB section belongs to, from its heading.

    Matches the parenthesised abbreviation the KB uses ("### Civil and Environmental
    Engineering (CEE)"). Matching the abbreviation rather than the full name avoids
    tagging general sections that merely mention a department in passing.
    """
    found = re.findall(r"\(([A-Za-z]+)\)", heading)
    for token in found:
        for dept in DEPARTMENTS:
            if token.upper() == dept.abbr:
                return dept
    return None


def contact_for(code: str | None) -> str:
    """The best escalation address for this student: their coordinator, else the CDC."""
    dept = from_code(code)
    return dept.contact_email if dept else GENERAL_CONTACT


def describe(code: str | None) -> str | None:
    """"Mechanical Engineering (MECH)" for prompts/UI, or None if unknown."""
    dept = from_code(code)
    return f"{dept.label} ({dept.abbr})" if dept else None
