"""Conservative process-stage constraints, independent of university topics."""

import re


def excluded_process_stages(question: str) -> tuple[str, ...]:
    """Entry facts cannot settle explicitly later employment/retention outcomes.

    Require both an employment attribute and an explicit later-time cue. An
    initial application/acceptance question keeps its entry evidence, including
    when the question says 'after applying'. Unknown stages stay unfiltered.
    """
    if not re.search(r"\b(?:hir(?:e[ds]?|ing)|jobs?|employ(?:ees?|ed|ment)|"
                     r"retain(?:s|ed|ing)?|retention|permanent(?:ly)?)\b", question, re.I):
        return ()
    if not re.search(r"\bafter(?:wards)?\b|\b(?:upon|on) completion\b|"
                     r"\bonce (?:I |we |you |they )?(?:finish|complete|graduate)|"
                     r"\b(?:finishing|completing)\s+(?:(?:my|the|a|an)\s+)?"
                     r"(?:[\w-]+\s+){0,3}(?:term|course|program|training|workshop)\b",
                     question, re.I):
        return ()
    if re.search(r"\bafter\s+(?:(?:I am|I'm|we are|we're|you are|you're|"
                 r"they are|they're)\s+)?(?:(?:being|getting|completing|finishing)\s+)?"
                 r"(?:(?:my|the|an|a)\s+)?(?:applying|applications?|accepted|"
                 r"acceptance|admission|registering|registration|joining|enrollment)\b",
                 question, re.I):
        return ()
    if re.search(r"\b(?:can|could|how|where|when|should)\b.{0,30}"
                 r"\b(?:apply|register|enroll|enrol|join)\b", question, re.I):
        return ()
    return ("entry",)


def requires_later_outcome_evidence(question: str) -> bool:
    """Definitive later employment/retention claims need evidence for that stage.

    General career-help and benefit questions can still use documented support.
    This never supplies a policy outcome: missing evidence routes to a human;
    reviewed post-completion evidence permits ordinary grounded generation.
    """
    if not excluded_process_stages(question):
        return False
    if re.search(r"\b(?:guarantee\w*|definitely|promise\w*|retain\w*|retention)\b",
                 question, re.I) or re.search(r"\bkeep (?:me|us|you|them)\b", question, re.I):
        return True
    # Future-tense assistance is a request for support, not a promised hiring
    # outcome. Entry evidence stays excluded, and generation must still match
    # the service/actor in canonical evidence. Explicit guarantees above remain
    # guarded even when the question also asks for help.
    assistance = re.search(r"\b(?:help|support|assist(?:ance)?)\b", question, re.I)
    hiring = re.search(r"\b(?:hir(?:e[sd]?|ing)|employ(?:s|ed|ing))\b", question, re.I)
    if assistance and (not hiring or assistance.start() < hiring.start()):
        return False
    return bool(re.search(r"\bpermanent\b", question, re.I)
                or re.match(r"^will\b", question.strip(), re.I))
