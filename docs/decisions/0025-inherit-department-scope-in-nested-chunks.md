# ADR-0025: Inherit department scope in nested chunks

**Status:** Accepted

**Date:** 2026-09-12

## Context

Department filtering relies on each indexed chunk's `department` metadata. An ECE
section was split into smaller level-3 sections to improve follow-up answers, but
the chunker inferred scope from only the current heading. Headings such as `6+2
arrangement definition` do not repeat `(ECE)`, so those child chunks fell back to
the document default `all` and became retrievable for MECH students.

The same defect could affect any department section with nested headings. Prompt
wording cannot reliably repair it because the incorrect chunks have already passed
the retrieval boundary as generally applicable evidence.

## Decision

- Track department scope through the Markdown heading hierarchy. A nested heading
  inherits the nearest scoped ancestor unless it names a department itself.
- Reset inherited scope when the parser reaches a sibling or higher-level heading.
- Keep the SQL department filter unchanged; correctly tagged chunks are sufficient.
- Treat proposed combinations as valid only when the retrieved sources explicitly
  document that arrangement for the selected department.
- Keep general second-internship forms separate from the ECE two-week research form.

## Measurement

The regression set asks the identical six-week-plus-two-week question for MECH and
ECE. The selected pilot model must reject it for MECH and accept it for ECE, with
the correct evidence and without unrelated forms, reports, or 4+4 rules. Unit tests
also cover department inheritance through more than one nested heading level. The
nine-case answer suite passes 9/9 checks with 15/15 required evidence hits, and the
combined synthesis retrieval gate passes 19/19.

## Consequences

Re-ingestion is required because the fix changes stored chunk metadata. This is a
general ingestion correction: future department sections can be subdivided without
silently widening their applicability. The LLM model and request count do not change.
