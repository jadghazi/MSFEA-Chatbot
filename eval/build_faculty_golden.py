"""Freeze the faculty workbook's original anonymized questions as evaluation cases.

The reviewed intake record supplies scope and row identity. The original workbook
supplies exact question and approved-answer wording; classification supplies source
locators. This command reads all three and does not alter the KB or vector index.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from openpyxl import load_workbook  # type: ignore[import-untyped]


EXPECTED_WORKBOOK_SHA256 = "2da2b0c75aa15c15da2a808d43f4e07a3369d2f705d3073b49fa008fdee9b07a"
REVIEW = Path("kb/source/faq-review-2026-09-27.json")
CLASSIFICATION = Path("docs/intake/faq-workbook-classification-2026-09-26.md")
OUTPUT = Path("eval/faculty_questions_golden.jsonl")
DEPARTMENTS = ("ece", "mech", "chem", "iem", "cee")
COURSE_DEPARTMENT = {
    "eece 500": "ece", "mech 500": "mech", "chen 500": "chem",
    "inde 500": "iem", "cive 400": "cee",
}
# These shared questions have materially different department rules. Preserve the
# original wording while testing it with every department selected.
CROSS_DEPARTMENT_IDS = {"GEN-04", "GEN-05", "GEN-06", "GEN-07", "GEN-08", "GEN-10", "GEN-11"}

SIX_WEEK_ROUTE = {
    "ece": "Six company weeks alone are insufficient. Two approved faculty research weeks or at least four approved weeks at a second company may complete the route.",
    "iem": "Six company weeks alone are insufficient. Two approved faculty research weeks or at least four approved weeks at a second company may complete the route.",
    "mech": "Six company weeks alone are insufficient. Two approved faculty research weeks can complete the route if the research includes hands-on engineering work.",
    "chem": "Six company weeks alone are insufficient under the ordinary eight-week minimum. A proposed research component requires Chair approval; do not promise eligibility.",
    "cee": "An exceptional six-week company placement may be approved for selected companies. A proposed research component requires Chair approval; neither is automatic.",
}
SPLIT_ROUTE = {
    "ece": "A 4+4 company split is case-specific and needs a formal petition and written approval.",
    "iem": "A 4+4 company split is not automatically accepted; obtain department approval for the full arrangement.",
    "mech": "Two separate four-week company internships are prohibited.",
    "chem": "Do not promise a 4+4 split; obtain written approval and complete components within the same summer.",
    "cee": "A 4+4 split may be approved if at least one period is in civil or construction engineering.",
}
COMBINE_ROUTE = {
    "ece": "Two company placements require prior written approval. After six company weeks, a second placement must last at least four weeks; a 4+4 split is case-specific and needs a petition.",
    "iem": "Two company placements require prior approval. After six company weeks, a second placement must last at least four weeks.",
    "mech": "A 4+4 company split is prohibited. Do not assume another two-company arrangement counts without prior department approval.",
    "chem": "Two placements need prior written approval and must be completed within the same summer.",
    "cee": "Two placements need prior approval; a 4+4 split may be accepted if at least one period is in civil or construction engineering.",
}
DAR_ROUTE = {
    "ece": "Dar is not exclusive. Six company weeks plus two faculty research weeks require approval and documentation for both components, plus a separate research report.",
    "iem": "Dar is not exclusive. Six company weeks plus two faculty research weeks require approval and documentation for both components, plus a separate research report.",
    "mech": "Dar is not exclusive. Six company weeks plus two approved faculty research weeks may count when the research includes hands-on engineering work; document both components and submit a separate research report.",
    "chem": "Dar is not exclusive. The proposed two-week faculty research addition to six company weeks requires Chair approval; if approved, document both components and submit a separate research report.",
    "cee": "Dar is not exclusive. The proposed two-week faculty research addition to six company weeks requires Chair approval; if approved, document both components and submit a separate research report. A separate exceptional six-week approval exists for selected companies.",
}
RESOLVED_EXPECTATIONS = {
    7: "The ordinary internship minimum is eight full approved weeks; department-specific exceptions need approval.",
    13: "The main company internship cannot take place inside AUB. An approved faculty research component at AUB is distinct and may count under department rules.",
    29: "Fully remote internships are ordinarily not accepted; a documented narrow exception needs formal approval.",
    34: "Multiple Moodle quiz attempts depend on the current activity settings; they are not guaranteed.",
    41: "The Progress Report is generally due at the end of Week 4 from the approved internship start unless Moodle sets a common course deadline; the guideline is June 2026.",
    44: "Use the current departmental Moodle template. The general Progress Report guidance is approximately 1,000 words or 3–5 pages.",
    48: "For an approved company-plus-research arrangement, the Progress Report covers the company component; research is reported separately under current Moodle instructions.",
    52: "Yes. The Final Training Report is a required CHEN 500 deliverable and must cover the approved experience activities.",
    53: "Normally submit the Final Training Report within one week of completing the approved internship, unless the current departmental Moodle page announces a different official deadline.",
    54: "For CEE, follow the general 8–15-page Final Training Report template unless the course team specifies otherwise.",
    59: "Describe technical and administrative activities and engineering-related projects. Address the engineering problem-solving and broader-impact reflections required by the applicable report rubric.",
    68: "Two approved company internships use one Final Report with distinct components. Company plus approved faculty research requires a separate research report. Confirm arrangement-specific details on Moodle.",
    91: "The student internship survey or evaluation is required for all departments and is separate from the Summary Sheet and employer letter.",
    92: "The student survey, Summary Sheet, and employer/supervisor letter are separate required deliverables in all departments.",
    93: "The student survey or self-evaluation is a separate required final deliverable in every internship department.",
    95: "The current approved AI-generated-text limit is 25%, subject to the official course instructions.",
    96: "AI use must be disclosed and cited under the current course instructions for all departments.",
    99: "Editing tools may assist with grammar and language, but the submitted report must remain the student's own work and comply with the current departmental AI and academic-integrity requirements.",
    102: "The current approved Turnitin similarity limit is 20% in all internship departments; it differs from the AI-detection measure.",
    114: "Another summer course needs applicable department, course-team and employer approvals and full work hours. Ten internship weeks and class time windows may be required; confirm with the course team/Moodle rather than asserting an unconditional ten-week rule.",
    115: "Ten internship weeks may be required when taking another summer course, but applicability depends on current course-team/Moodle requirements and approvals; do not state that all students unconditionally need ten weeks.",
    116: "Do not assume eight weeks suffice with another summer course. Confirm the applicable ten-week/time-window conditions and approvals with the course team/Moodle.",
    120: "The Progress Report is due under current Moodle instructions, generally Week 4 of training in the June 2026 guideline; do not attribute it to May.",
    125: "Ask what 'this' refers to. A friend's past individual approval does not establish a current policy or automatic exception; explain the applicable rule once the arrangement is identified.",
    145: "Use the CO-OP handbook's proposal and admission process; no universal internship-course Moodle Proposal requirement was approved for CO-OP.",
    148: "Use the CO-OP handbook's required post-placement deliverables. The signed company letter is additional to the employer forms; do not invent a universal Final VOP requirement.",
    149: "A signed official company completion letter is additionally required for CO-OP in every department and does not replace the handbook's employer forms.",
    153: "Ask the course team whether an early letter is accepted. If accepted, it states the actual start, expected end, and completed work, subject to current Moodle requirements; it is not limited to summer graduates.",
    175: "Follow the CO-OP handbook's proposal process and submit the Notice of Arrival after work starts; do not import a universal internship-course Moodle Proposal rule.",
    177: "Follow the CO-OP handbook's final deliverables plus the additional signed company letter. Do not assert a universal CO-OP Final Voice-Over Presentation requirement.",
}


def _resolved_expectation(ordinal: int, source_id: str, department: str,
                          original: str) -> str:
    if source_id in {"GEN-04", "GEN-05"}:
        return SIX_WEEK_ROUTE[department]
    if source_id == "GEN-06":
        return "Two company weeks after six are not a documented standard route. " + SIX_WEEK_ROUTE[department]
    if source_id == "GEN-07":
        return COMBINE_ROUTE[department]
    if source_id == "GEN-08":
        return SPLIT_ROUTE[department]
    if source_id == "GEN-11":
        return DAR_ROUTE[department]
    return RESOLVED_EXPECTATIONS.get(ordinal, original)


def _classification_blocks() -> list[str]:
    text = CLASSIFICATION.read_text(encoding="utf-8")
    pattern = re.compile(r"^#### \d{3}\. .*?(?=^#### \d{3}\. |\Z)", re.M | re.S)
    return [m.group(0) for m in pattern.finditer(text)]


def _clean_words(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _departments(question: str, green: bool, source_id: str, ordinal: int) -> list[str]:
    lower = question.lower()
    for course, department in COURSE_DEPARTMENT.items():
        if course in lower:
            return [department]
    if not green:
        return ["ece"]
    if source_id in CROSS_DEPARTMENT_IDS:
        return list(DEPARTMENTS)
    return [DEPARTMENTS[ordinal % len(DEPARTMENTS)]]


def build(workbook_path: Path, output_path: Path = OUTPUT) -> list[dict[str, object]]:
    digest = hashlib.sha256(workbook_path.read_bytes()).hexdigest()
    if digest != EXPECTED_WORKBOOK_SHA256:
        raise ValueError("Workbook hash differs from the reviewed 2026-09-26 intake")
    reviewed = json.loads(REVIEW.read_text(encoding="utf-8"))["questions"]
    blocks = _classification_blocks()
    if len(reviewed) != 177 or len(blocks) != len(reviewed):
        raise ValueError("Expected 177 reviewed workbook rows and classification blocks")
    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    cases: list[dict[str, object]] = []
    for ordinal, (row, block) in enumerate(zip(reviewed, blocks, strict=True), 1):
        question = workbook[row["sheet"]][row["question_cell"]].value
        answer = workbook[row["sheet"]][row["answer_cell"]].value
        if not isinstance(question, str) or answer is None:
            raise ValueError(f"Missing question/answer at row {ordinal}")
        if question.strip().casefold() != row["question"].strip().casefold().replace("�", "’"):
            # Older JSON extraction lost some punctuation. Compare the stable words.
            if _clean_words(question) != _clean_words(row["question"]):
                raise ValueError(f"Question mismatch at row {ordinal}: {row['id']}")
        classified_question = re.search(r"\*\*Question \([^)]+\):\*\* ([^\n]+)", block)
        if not classified_question or _clean_words(question) != _clean_words(
            classified_question.group(1)
        ):
            raise ValueError(f"Classification mismatch at row {ordinal}: {row['id']}")
        locators = re.findall(r"\[([^\]]+)\]\(<[^>]+/kb/normalized/([^/:>]+):\d+>\)", block)
        expected_docs = sorted({doc for _, doc in locators})
        if not expected_docs:
            raise ValueError(f"Missing source locator at row {ordinal}")
        selected_departments = _departments(question, bool(row["green"]), row["id"], ordinal)
        for variant, department in enumerate(selected_departments):
            cases.append({
                "id": f"faculty-{ordinal:03d}-{department}",
                "workbook_id": row["id"],
                "question": question.strip(),
                "is_synthetic": False,
                "source_type": "faculty_anonymized_question",
                "original_approved_answer": str(answer).strip(),
                "expected_answer_or_behavior": _resolved_expectation(
                    ordinal, row["id"], department, str(answer).strip()
                ),
                "department": department,
                "primary_workbook_case": variant == 0,
                "shared_scope": bool(row["green"]),
                "intake_status": row["status"],
                "source_doc_candidates": expected_docs,
                "source_locators": [label for label, _ in locators],
                "source_sheet": row["sheet"],
                "question_cell": row["question_cell"],
                "answer_cell": row["answer_cell"],
                "source_sha256": digest,
                "should_refuse": ordinal == 125,
                "reference_note": (
                    "The original answer predates the owner's 2026-09-27 conflict decisions; "
                    "grade against the current approved KB and decision record."
                    if row["status"] in {"Hold", "Keep exceptions", "Broaden", "Correct citation"}
                    else ""
                ),
            })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(json.dumps(case, ensure_ascii=False) + "\n" for case in cases), encoding="utf-8"
    )
    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    cases = build(args.workbook, args.output)
    print(f"Wrote {len(cases)} cases from 177 workbook rows to {args.output}")


if __name__ == "__main__":
    main()
