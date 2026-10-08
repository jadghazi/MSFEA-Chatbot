"""Spelling recovery must preserve intent and reject uncertain corrections."""

from msfea_bot.retrieval.repair import edit_distance, suggest_query, gains_lexical_support


def test_transpositions_and_single_character_errors_generalize() -> None:
    vocabulary = {"workshops", "bursaries", "mentorship"}
    assert edit_distance("wrokshops", "workshops") == 1
    assert suggest_query("what are wrokshops", vocabulary) == "what are workshops"
    assert suggest_query("can i apply for bursraies", vocabulary) == "can i apply for bursaries"


def test_known_words_and_ambiguous_candidates_are_preserved() -> None:
    assert suggest_query("plants", {"plants", "plans"}) is None
    assert suggest_query("plane", {"plans", "plant"}) is None
    assert suggest_query("weather tomorrow", {"whether", "training"}) is None


def test_identifiers_urls_and_email_components_are_never_repaired() -> None:
    assert suggest_query("wrokshops500 https://wrokshops.org wrokshops@aub.edu.lb",
                         {"workshops"}) is None


def test_repair_is_bounded_and_does_not_insert_policy_facts() -> None:
    vocabulary = {"workshops"}
    assert suggest_query("wrokshops wrokshops wrokshops", vocabulary) == "workshops workshops wrokshops"


def test_known_whole_words_and_existing_evidence_prevent_weak_repairs() -> None:
    assert suggest_query("employed", {"employer"}, {"employed"}) is None
    assert gains_lexical_support("wrokshops aborad", "workshops abroad",
                                ["Workshop instructions"], ["Workshops abroad"])
    assert not gains_lexical_support("wrokshops", "workshops",
                                    ["Workshop instructions"], ["Workshops abroad"])
    assert not gains_lexical_support("worxxhops", "workshops", [], ["Workshops abroad"])
