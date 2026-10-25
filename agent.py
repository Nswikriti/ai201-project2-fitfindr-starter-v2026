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
import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """Run the tools in stages, storing each result in the session."""
    session = new_session(query, wardrobe)
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
            stage = "search"

        elif stage == "search":
            session["search_results"] = search_listings(
                **session["parsed"]
            )

            if not session["search_results"]:
                session["error"] = (
                    "No matching listings. Try broader description "
                    "keywords, a different size, or a higher maximum price."
                )
                return session

            session["selected_item"] = session["search_results"][0]
            stage = "outfit"

        elif stage == "outfit":
            session["outfit_suggestion"] = suggest_outfit(
                session["selected_item"],
                session["wardrobe"],
            )
            stage = "fit_card"

        elif stage == "fit_card":
            session["fit_card"] = create_fit_card(
                session["outfit_suggestion"],
                session["selected_item"],
            )
            return session

# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
