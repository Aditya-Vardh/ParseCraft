"""LL(1) parsing table and predictive parser."""

from __future__ import annotations

from dataclasses import dataclass

from compiler.first_follow import compute_first, compute_follow, first_of_sequence
from compiler.grammar import END_MARKER, EPSILON, Grammar, format_production, tokenize


@dataclass
class ParseResult:
    accepted: bool
    steps: list[dict[str, str]]
    tree: dict[str, object] | None
    errors: list[str]


def build_parsing_table(
    grammar: Grammar,
    first_sets: dict[str, set[str]] | None = None,
    follow_sets: dict[str, set[str]] | None = None,
) -> tuple[dict[str, dict[str, list[str]]], list[str]]:
    """Build the predictive parsing table and report LL(1) conflicts."""

    first_sets = first_sets or compute_first(grammar)
    follow_sets = follow_sets or compute_follow(grammar, first_sets)
    table: dict[str, dict[str, list[str]]] = {
        non_terminal: {} for non_terminal in grammar.productions
    }
    conflicts: list[str] = []

    for lhs, alternatives in grammar.productions.items():
        for rhs in alternatives:
            first_rhs = first_of_sequence(rhs, first_sets, grammar)
            targets = set(first_rhs - {EPSILON})
            if EPSILON in first_rhs:
                targets.update(follow_sets[lhs])

            for terminal in targets:
                existing = table[lhs].get(terminal)
                if existing is not None and existing != rhs:
                    conflicts.append(
                        f"Conflict at M[{lhs}, {terminal}]: "
                        f"{format_production(existing)} vs {format_production(rhs)}"
                    )
                table[lhs][terminal] = rhs

    return table, conflicts


def format_table(
    grammar: Grammar,
    table: dict[str, dict[str, list[str]]],
) -> tuple[list[str], list[dict[str, str]]]:
    """Format a parsing table for template rendering."""

    columns = sorted(grammar.terminals) + [END_MARKER]
    rows: list[dict[str, str]] = []
    for non_terminal in grammar.productions:
        row = {"non_terminal": non_terminal}
        for terminal in columns:
            production = table.get(non_terminal, {}).get(terminal)
            row[terminal] = (
                f"{non_terminal} -> {format_production(production)}"
                if production
                else ""
            )
        rows.append(row)
    return columns, rows


def tokenize_input(text: str, grammar: Grammar) -> list[str]:
    """Tokenize the test string with the same scanner used for productions."""

    if not text.strip():
        return []
    if " " in text:
        return [part for part in text.split() if part.strip()]
    return tokenize(text, grammar.non_terminals)


def parse_input(
    grammar: Grammar,
    table: dict[str, dict[str, list[str]]],
    text: str,
) -> ParseResult:
    """Run the LL(1) predictive parser and return a detailed trace."""

    if not grammar.start_symbol:
        return ParseResult(False, [], None, ["Grammar has no start symbol."])

    tokens = tokenize_input(text, grammar) + [END_MARKER]
    root: dict[str, object] = {"symbol": grammar.start_symbol, "children": []}
    stack: list[tuple[str, dict[str, object] | None]] = [
        (END_MARKER, None),
        (grammar.start_symbol, root),
    ]
    index = 0
    steps: list[dict[str, str]] = []
    errors: list[str] = []

    while stack:
        stack_view = " ".join(symbol for symbol, _ in reversed(stack))
        remaining = " ".join(tokens[index:])
        top, node = stack.pop()
        current = tokens[index] if index < len(tokens) else END_MARKER

        if top == EPSILON:
            steps.append(
                {"stack": stack_view, "input": remaining, "action": "Output ε"}
            )
            continue

        if top == END_MARKER and current == END_MARKER:
            steps.append({"stack": stack_view, "input": remaining, "action": "Accept"})
            return ParseResult(True, steps, root, errors)

        if top not in grammar.non_terminals:
            if top == current:
                steps.append(
                    {"stack": stack_view, "input": remaining, "action": f"Match {top}"}
                )
                index += 1
                continue

            message = f"Expected {top}, found {current}."
            errors.append(message)
            steps.append({"stack": stack_view, "input": remaining, "action": message})
            return ParseResult(False, steps, root, errors)

        production = table.get(top, {}).get(current)
        if production is None:
            message = f"No rule for M[{top}, {current}]."
            errors.append(message)
            steps.append({"stack": stack_view, "input": remaining, "action": message})
            return ParseResult(False, steps, root, errors)

        steps.append(
            {
                "stack": stack_view,
                "input": remaining,
                "action": f"Use {top} -> {format_production(production)}",
            }
        )

        children = [{"symbol": symbol, "children": []} for symbol in production]
        if node is not None:
            node["children"] = children

        for symbol, child in reversed(list(zip(production, children))):
            if symbol != EPSILON:
                stack.append((symbol, child))

    errors.append("Input was not fully consumed.")
    return ParseResult(False, steps, root, errors)
