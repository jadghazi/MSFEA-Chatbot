"""Ingestion pipeline (CLAUDE.md §5.4).

load -> clean/normalize -> chunk -> embed source documents -> store in pgvector,
with metadata (source doc, section, last-updated, and a reserved
`department`/`applies_to` field for department-conditional rules — see
docs/backlog.md B-2). One command rebuilds the index from source; the vector
store is never hand-edited.

PLACEHOLDER: no implementation yet — built in the ingestion phase.
"""
