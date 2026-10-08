"""Conservative spelling suggestions from the active source vocabulary."""

from __future__ import annotations

import re
from collections.abc import Collection


def edit_distance(left: str, right: str) -> int:
    """Restricted Damerau distance, including adjacent transpositions."""
    rows = [list(range(len(right) + 1))]
    for i, a in enumerate(left, 1):
        row = [i]
        for j, b in enumerate(right, 1):
            value = min(rows[-1][j] + 1, row[-1] + 1, rows[-1][j - 1] + (a != b))
            if i > 1 and j > 1 and a == right[j - 2] and left[i - 2] == b:
                value = min(value, rows[i - 2][j - 2] + 1)
            row.append(value)
        rows.append(row)
    return rows[-1][-1]


def suggest_query(
    query: str, vocabulary: Collection[str], protected_words: Collection[str] = (),
) -> str | None:
    """Repair at most two unknown long words, rejecting ambiguous suggestions.

    Known words, numbers, identifiers, URLs and email components are preserved.
    This proposes retrieval text only; it never supplies factual answer evidence.
    Callers must separately validate retrieval confidence and keep original input.
    """
    vocabulary = set(vocabulary)
    repairs = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal repairs
        word = match.group().lower()
        if word in vocabulary or word in protected_words or repairs >= 2:
            return match.group()
        limit = 2 if len(word) >= 9 else 1
        candidates = [(edit_distance(word, candidate), candidate) for candidate in vocabulary
                      if len(candidate) >= 5 and candidate[0] == word[0]
                      and abs(len(candidate) - len(word)) <= limit]
        candidates.sort()
        if not candidates or candidates[0][0] > limit:
            return match.group()
        if len(candidates) > 1 and candidates[1][0] == candidates[0][0]:
            return match.group()
        repairs += 1
        return candidates[0][1]

    corrected = re.sub(r"(?<![\w@./])[A-Za-z]{5,}(?![\w@./])", replace, query)
    return corrected if corrected != query else None


def gains_lexical_support(original: str, corrected: str, before: list[str], after: list[str]) -> bool:
    """A unique one-edit repair must gain canonical support for all repaired terms.

    This is a separate confidence signal from cosine gain. Embeddings can score
    a wrong passage highly despite misspellings. Do not accept a two-edit repair
    using this route, or one whose evidence was already present before repair.
    """
    old = re.findall(r"[a-z]+", original.lower())
    new = re.findall(r"[a-z]+", corrected.lower())
    pairs = [(a, b) for a, b in zip(old, new) if a != b]
    if not pairs or any(edit_distance(a, b) != 1 for a, b in pairs):
        return False
    terms = {b.rstrip("s") for _, b in pairs}

    def supported(texts: list[str]) -> bool:
        return any(terms <= {word.rstrip("s") for word in re.findall(r"[a-z]+", text.lower())}
                   for text in texts)

    return supported(after) and not supported(before)
