"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import trace
from generate import ModelUnavailable
from mcp_client import call_tool
from tools import suggest_outfit, create_fit_card


def new_session(query: str, wardrobe: dict) -> dict:
    """Create the saved state for one interaction."""
    return {
        "query": query,
        "parsed": {},
        "search_results": [],
        "selected_item": None,
        "wardrobe": wardrobe,
        "outfit_suggestion": None,
        "fit_card": None,
        "error": None,
    }


def run_agent(query: str, wardrobe: dict) -> dict:
    """Choose the next stage using results saved in the session."""
    session = new_session(query, wardrobe)
    trace.start_trace()

    stage = "parse"
    iterations = 0

    while True:
        iterations += 1
        trace.check_iterations(iterations)

        if stage == "parse":
            description = query.strip()

            price_match = re.search(
                r"\b(?:under|below|up to|max(?:imum)?(?: price)?)"
                r"\s*\$?\s*(\d+(?:\.\d{1,2})?)\b",
                description,
                flags=re.IGNORECASE,
            )

            max_price = None
            if price_match:
                max_price = float(price_match.group(1))
                description = (
                    description[:price_match.start()]
                    + " "
                    + description[price_match.end():]
                )

            size_match = re.search(
                r"\b(?:in\s+)?size\s+"
                r"(W\d+(?:\s+L\d+)?|US\s*\d+(?:\.\d+)?"
                r"|[A-Za-z0-9]+(?:/[A-Za-z0-9]+)?)"
                r"(?:\s*\([^)]*\))?",
                description,
                flags=re.IGNORECASE,
            )

            size = None
            if size_match:
                size = size_match.group(1).strip()
                description = (
                    description[:size_match.start()]
                    + " "
                    + description[size_match.end():]
                )

            description = re.sub(
                r"^\s*(?:looking for|searching for|find me|find|"
                r"show me|I want|I need)\s+",
                "",
                description,
                flags=re.IGNORECASE,
            )
            description = " ".join(description.strip(" ,.;").split())

            session["parsed"] = {
                "description": description,
                "size": size,
                "max_price": max_price,
            }

            trace.step(
                "parse_query",
                inputs=query,
                returned=session["parsed"],
            )
            stage = "search"

        elif stage == "search":
            session["search_results"] = call_tool(
                "search_listings",
                session["parsed"],
            )

            trace.step(
                "search_listings (via MCP)",
                inputs=session["parsed"],
                returned=session["search_results"],
            )

            if not session["search_results"]:
                session["error"] = (
                    "No matching listings. Try broader description "
                    "keywords, a different size, or a higher maximum price."
                )
                trace.step(
                    "empty_search",
                    returned=session["error"],
                    note="No matches: stopping before outfit and fit card.",
                )
                return session

            session["selected_item"] = session["search_results"][0]

            trace.step(
                "select_item",
                returned=session["selected_item"],
            )
            stage = "outfit"

        elif stage == "outfit":
            inputs = {
                "new_item": session["selected_item"],
                "wardrobe": session["wardrobe"],
            }

            try:
                session["outfit_suggestion"] = suggest_outfit(**inputs)
            except ModelUnavailable as exc:
                session["error"] = (
                    "Outfit suggestions could not be generated. "
                    f"{exc}"
                )
                trace.step(
                    "suggest_outfit",
                    inputs=inputs,
                    returned=session["error"],
                    note="Model unavailable: stopping.",
                )
                return session

            trace.step(
                "suggest_outfit",
                inputs=inputs,
                returned=session["outfit_suggestion"],
                note=(
                    "Empty wardrobe: general styling advice."
                    if not session["wardrobe"].get("items")
                    else "Using supplied wardrobe."
                ),
            )
            stage = "fit_card"

        elif stage == "fit_card":
            inputs = {
                "outfit": session["outfit_suggestion"],
                "new_item": session["selected_item"],
            }

            try:
                session["fit_card"] = create_fit_card(**inputs)
            except ModelUnavailable as exc:
                session["error"] = (
                    "The fit card could not be generated. "
                    f"{exc}"
                )
                trace.step(
                    "create_fit_card",
                    inputs=inputs,
                    returned=session["error"],
                    note="Model unavailable: stopping.",
                )
                return session

            trace.step(
                "create_fit_card",
                inputs=inputs,
                returned=session["fit_card"],
            )
            return session


def _show(session: dict) -> None:
    """Print the final result or the reason the agent stopped."""
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r}")
        return

    item = session["selected_item"] or {}
    print(
        f"  found: {item.get('title')} "
        f"— ${item.get('price')} on {item.get('platform')}"
    )
    print(f"  outfit: {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(
        run_agent(
            query="looking for a vintage graphic tee under $30",
            wardrobe=get_example_wardrobe(),
        )
    )

    print("\n=== A query it cannot match ===")
    _show(
        run_agent(
            query="designer ballgown size XXS under $5",
            wardrobe=get_example_wardrobe(),
        )
    )