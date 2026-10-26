"""Evaluation scenarios matching the five original acceptance criteria."""

from utils.data_loader import load_listings


SCENARIOS = [
    {
        "name": "matching query completes all tools",
        "query": "vintage graphic tee under $30, size M",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        "name": "impossible query stops before outfit",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        "name": "selected item reaches both tools unchanged",
        "query": "vintage graphic tee under $30, size M",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "fit card has accurate details and sentence count",
        "query": "vintage graphic tee under $30, size M",
        "wardrobe": "example",
        "criterion": 4,
    },
]

# Five different searches with known matches.
# Each source listing must match its own title keywords, and its price
# is exactly the inclusive budget boundary.
for listing in load_listings()[:5]:
    SCENARIOS.append({
        "name": f"budget search for {listing['id']}",
        "query": (
            f"{listing['title']} "
            f"under ${listing['price']:.2f}"
        ),
        "description": listing["title"],
        "max_price": float(listing["price"]),
        "known_match_id": listing["id"],
        "test_kind": "search_only",
        "wardrobe": "example",
        "criterion": 5,
    })


WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Check the scenario definitions before evaluation."""
    problems = []

    for index, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"Scenario {index} has no query.")

        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(f"Scenario {index} has an invalid wardrobe.")

        if scenario.get("criterion") not in range(1, 6):
            problems.append(f"Scenario {index} has an invalid criterion.")

        if scenario.get("test_kind") == "search_only":
            if not scenario.get("description"):
                problems.append(
                    f"Scenario {index} has no search description."
                )
            if not isinstance(scenario.get("max_price"), (int, float)):
                problems.append(
                    f"Scenario {index} has no numeric price ceiling."
                )

    return problems