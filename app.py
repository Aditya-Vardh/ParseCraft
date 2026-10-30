from __future__ import annotations

from flask import Flask, render_template, request

from compiler.first_follow import compute_first, compute_follow
from compiler.grammar import (
    format_grammar,
    left_factor,
    parse_grammar,
    remove_immediate_left_recursion,
)
from compiler.ll1 import build_parsing_table, format_table, parse_input

app = Flask(__name__)


def format_sets(sets: dict[str, set[str]]) -> dict[str, str]:
    return {symbol: "{ " + ", ".join(sorted(values)) + " }" for symbol, values in sets.items()}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    grammar_text = request.form.get("grammar", "")
    test_string = request.form.get("test_string", "")
    result = None
    error = None

    try:
        original_grammar = parse_grammar(grammar_text)
        recursion_free = remove_immediate_left_recursion(original_grammar)
        factored = left_factor(recursion_free)

        first_sets = compute_first(factored)
        follow_sets = compute_follow(factored, first_sets)
        table, conflicts = build_parsing_table(factored, first_sets, follow_sets)
        table_columns, table_rows = format_table(factored, table)
        parse_result = parse_input(factored, table, test_string)
        production_count = sum(
            len(alternatives) for alternatives in factored.productions.values()
        )

        result = {
            "original": format_grammar(original_grammar),
            "left_recursion": format_grammar(recursion_free),
            "left_factoring": format_grammar(factored),
            "stats": {
                "non_terminals": len(factored.non_terminals),
                "terminals": len(factored.terminals),
                "productions": production_count,
                "grammar_type": "LL(1)" if not conflicts else "Not LL(1)",
                "is_ll1": not conflicts,
            },
            "first": format_sets(first_sets),
            "follow": format_sets(follow_sets),
            "table_columns": table_columns,
            "table_rows": table_rows,
            "conflicts": conflicts,
            "simulation": parse_result.steps,
            "accepted": parse_result.accepted,
            "parse_errors": parse_result.errors,
            "tree": parse_result.tree,
        }
    except ValueError as exc:
        error = str(exc)

    return render_template(
        "index.html",
        grammar=grammar_text,
        test_string=test_string,
        result=result,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
