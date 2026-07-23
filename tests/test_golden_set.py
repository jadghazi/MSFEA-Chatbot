"""The golden set loads, validates, and stays consistent with the KB."""

from pathlib import Path

from eval.loader import load_golden_set

NORMALIZED = Path(__file__).parent.parent / "kb" / "normalized"


def test_golden_set_loads_and_ids_unique() -> None:
    items = load_golden_set()
    assert len(items) >= 20
    ids = [i.id for i in items]
    assert len(ids) == len(set(ids)), "duplicate ids in golden set"


def test_has_both_answerable_and_refusal_cases() -> None:
    items = load_golden_set()
    assert any(i.should_refuse for i in items), "no should_refuse cases"
    assert any(not i.should_refuse for i in items), "no answerable cases"


def test_answerable_items_reference_existing_kb_files() -> None:
    for item in load_golden_set():
        if not item.should_refuse:
            assert item.source_doc is not None
            assert (NORMALIZED / item.source_doc).exists(), (
                f"{item.id}: source_doc '{item.source_doc}' not found in kb/normalized/"
            )


def test_answerable_items_have_evidence() -> None:
    for item in load_golden_set():
        if not item.should_refuse:
            assert item.evidence, f"{item.id}: answerable item is missing an evidence string"


def test_evidence_actually_exists_in_the_source_doc() -> None:
    # Guards against a mistyped evidence annotation: the string the retrieval
    # metric looks for must really be present in the KB it points at.
    for item in load_golden_set():
        if item.should_refuse or not item.evidence or not item.source_doc:
            continue
        doc_text = (NORMALIZED / item.source_doc).read_text(encoding="utf-8").lower()
        assert item.evidence.lower() in doc_text, (
            f"{item.id}: evidence '{item.evidence}' not found in {item.source_doc}"
        )
