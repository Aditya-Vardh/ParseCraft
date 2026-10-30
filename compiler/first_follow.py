"""FIRST and FOLLOW set computation."""

from __future__ import annotations

from compiler.grammar import END_MARKER, EPSILON, Grammar


def first_of_sequence(
    sequence: list[str],
    first_sets: dict[str, set[str]],
    grammar: Grammar,
) -> set[str]:
    """Return FIRST for a sequence of grammar symbols."""

    if not sequence or sequence == [EPSILON]:
        return {EPSILON}

    result: set[str] = set()

    for symbol in sequence:
        if symbol == EPSILON:
            result.add(EPSILON)
            break

        if symbol not in grammar.non_terminals:
            result.add(symbol)
            break

        result.update(first_sets[symbol] - {EPSILON})
        if EPSILON not in first_sets[symbol]:
            break
    else:
        result.add(EPSILON)

    return result


def compute_first(grammar: Grammar) -> dict[str, set[str]]:
    """Compute complete textbook FIRST sets for all non-terminals."""

    first_sets = {non_terminal: set() for non_terminal in grammar.productions}
    changed = True

    while changed:
        changed = False
        for lhs, alternatives in grammar.productions.items():
            for rhs in alternatives:
                before = len(first_sets[lhs])
                first_sets[lhs].update(first_of_sequence(rhs, first_sets, grammar))
                changed = changed or len(first_sets[lhs]) > before

    return first_sets


def compute_follow(
    grammar: Grammar,
    first_sets: dict[str, set[str]] | None = None,
) -> dict[str, set[str]]:
    """Compute complete FOLLOW sets for all non-terminals."""

    first_sets = first_sets or compute_first(grammar)
    follow_sets = {non_terminal: set() for non_terminal in grammar.productions}

    if grammar.start_symbol:
        follow_sets[grammar.start_symbol].add(END_MARKER)

    changed = True
    while changed:
        changed = False
        for lhs, alternatives in grammar.productions.items():
            for rhs in alternatives:
                for index, symbol in enumerate(rhs):
                    if symbol not in grammar.non_terminals:
                        continue

                    trailer = rhs[index + 1 :]
                    first_trailer = first_of_sequence(trailer, first_sets, grammar)

                    before = len(follow_sets[symbol])
                    follow_sets[symbol].update(first_trailer - {EPSILON})
                    if not trailer or EPSILON in first_trailer:
                        follow_sets[symbol].update(follow_sets[lhs])
                    changed = changed or len(follow_sets[symbol]) > before

    return follow_sets
