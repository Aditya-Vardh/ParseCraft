"""Grammar parsing and grammar transformations for the studio."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

EPSILON = "ε"
EPSILON_ALIASES = {"ε", "ϵ", "Îµ", "epsilon", "EPSILON", "eps", "EPS", "e"}
END_MARKER = "$"


@dataclass
class Grammar:
    """Context-free grammar represented as tokenized productions."""

    productions: dict[str, list[list[str]]] = field(default_factory=dict)
    start_symbol: str | None = None

    @property
    def non_terminals(self) -> set[str]:
        return set(self.productions)

    @property
    def terminals(self) -> set[str]:
        terminals: set[str] = set()
        for alternatives in self.productions.values():
            for production in alternatives:
                for symbol in production:
                    if symbol != EPSILON and symbol not in self.productions:
                        terminals.add(symbol)
        return terminals

    def add_rule(self, lhs: str, rhs: list[str]) -> None:
        if self.start_symbol is None:
            self.start_symbol = lhs
        self.productions.setdefault(lhs, []).append(rhs or [EPSILON])

    def clone(self) -> "Grammar":
        return Grammar(deepcopy(self.productions), self.start_symbol)


def normalize_epsilon(symbol: str) -> str:
    return EPSILON if symbol.strip() in EPSILON_ALIASES else symbol.strip()


def tokenize(production: str, known_non_terminals: set[str] | None = None) -> list[str]:
    """Tokenize one production alternative.

    Supports compact grammar notation such as ``TE'`` as well as spaced
    notation such as ``T E'``. Multi-character terminals like ``id`` are kept
    intact.
    """

    production = production.strip()
    if not production:
        return [EPSILON]

    normalized = normalize_epsilon(production)
    if normalized == EPSILON:
        return [EPSILON]

    if " " in production:
        return [normalize_epsilon(part) for part in production.split() if part.strip()]

    symbols: list[str] = []
    non_terminals = sorted(known_non_terminals or set(), key=len, reverse=True)
    i = 0

    while i < len(production):
        if production[i].isspace():
            i += 1
            continue

        match = next(
            (nt for nt in non_terminals if production.startswith(nt, i)),
            None,
        )
        if match:
            symbols.append(match)
            i += len(match)
            continue

        if production.startswith("id", i):
            symbols.append("id")
            i += 2
            continue

        ch = production[i]
        if ch.isupper():
            symbol = ch
            i += 1
            while i < len(production) and production[i] == "'":
                symbol += "'"
                i += 1
            symbols.append(symbol)
            continue

        if ch.isalpha():
            symbols.append(ch)
            i += 1
            continue

        symbols.append(ch)
        i += 1

    return symbols or [EPSILON]


def parse_grammar(text: str) -> Grammar:
    """Parse textarea grammar input into a ``Grammar`` object."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Enter at least one grammar production.")

    lhs_order: list[str] = []
    raw_rules: list[tuple[str, str]] = []

    for line in lines:
        if "->" not in line:
            raise ValueError(f"Invalid production '{line}'. Use A->alpha|beta.")
        lhs, rhs = line.split("->", 1)
        lhs = lhs.strip()
        if not lhs:
            raise ValueError(f"Invalid production '{line}'. Missing left-hand side.")
        if lhs not in lhs_order:
            lhs_order.append(lhs)
        raw_rules.append((lhs, rhs))

    grammar = Grammar()
    known_non_terminals = set(lhs_order)

    for lhs, rhs in raw_rules:
        for alternative in rhs.split("|"):
            grammar.add_rule(lhs, tokenize(alternative, known_non_terminals))

    return grammar


def format_production(rhs: list[str]) -> str:
    return EPSILON if rhs == [EPSILON] else " ".join(rhs)


def format_grammar(grammar: Grammar) -> list[str]:
    return [
        f"{lhs} -> {' | '.join(format_production(rhs) for rhs in alternatives)}"
        for lhs, alternatives in grammar.productions.items()
    ]


def _fresh_non_terminal(base: str, existing: set[str]) -> str:
    candidate = f"{base}'"
    while candidate in existing:
        candidate += "'"
    return candidate


def remove_immediate_left_recursion(grammar: Grammar) -> Grammar:
    """Remove immediate left recursion from each non-terminal."""

    result = Grammar(start_symbol=grammar.start_symbol)
    existing = set(grammar.productions)

    for lhs, alternatives in grammar.productions.items():
        recursive: list[list[str]] = []
        non_recursive: list[list[str]] = []

        for rhs in alternatives:
            if rhs and rhs[0] == lhs:
                suffix = rhs[1:] or [EPSILON]
                recursive.append(suffix)
            else:
                non_recursive.append(rhs)

        if not recursive:
            result.productions[lhs] = deepcopy(alternatives)
            continue

        new_lhs = _fresh_non_terminal(lhs, existing | set(result.productions))
        existing.add(new_lhs)
        result.productions[lhs] = []
        result.productions[new_lhs] = []

        for rhs in non_recursive or [[EPSILON]]:
            prefix = [] if rhs == [EPSILON] else rhs
            result.productions[lhs].append(prefix + [new_lhs])

        for rhs in recursive:
            prefix = [] if rhs == [EPSILON] else rhs
            result.productions[new_lhs].append(prefix + [new_lhs])
        result.productions[new_lhs].append([EPSILON])

    return result


def _longest_common_prefix(items: list[list[str]]) -> list[str]:
    if len(items) < 2:
        return []

    prefix: list[str] = []
    for column in zip(*items):
        if len(set(column)) != 1 or column[0] == EPSILON:
            break
        prefix.append(column[0])
    return prefix


def left_factor(grammar: Grammar) -> Grammar:
    """Apply common-prefix left factoring until no factorable group remains."""

    result = grammar.clone()
    changed = True

    while changed:
        changed = False
        for lhs in list(result.productions):
            alternatives = result.productions[lhs]
            groups: dict[str, list[list[str]]] = {}
            for rhs in alternatives:
                key = rhs[0] if rhs and rhs[0] != EPSILON else EPSILON
                groups.setdefault(key, []).append(rhs)

            factorable = next(
                (group for group in groups.values() if _longest_common_prefix(group)),
                None,
            )
            if not factorable:
                continue

            prefix = _longest_common_prefix(factorable)
            new_lhs = _fresh_non_terminal(lhs, set(result.productions))
            remaining = [rhs for rhs in alternatives if rhs not in factorable]
            remaining.append(prefix + [new_lhs])

            result.productions[lhs] = remaining
            result.productions[new_lhs] = [
                rhs[len(prefix) :] or [EPSILON] for rhs in factorable
            ]
            changed = True
            break

    return result
