# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
Finding an item alone does not complete the user's request. The agent
must also suggest an outfit and produce a caption. I chose 4 of 5
because this path depends on two model calls, which may occasionally
fail or return unusable output. The target requires the full process
to succeed in most attempts.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**

Without a matching item, the remaining tools have no valid listing
to work with. Continuing could produce invented recommendations and
unnecessary model calls. I chose 5 of 5 because checking an empty list
is controlled by code. The message must suggest changing the keywords,
size, or maximum price so the user knows what to try next.

---

## 3. Something about state


In 5 of 5 successful-search runs, the listing ID saved in
session["selected_item"] matches the listing ID passed to both
suggest_outfit and create_fit_card.


**Why this target:**
The outfit suggestion and fit card must refer to the item selected
from the search results. Passing a different item would make the final
result misleading, even if each tool worked individually. I chose
5 of 5 because transferring the selected item between functions is
controlled by code and should not depend on model response variation.



---

## 4. Something about the fit card

In at least 4 of 5 successful-search runs, the fit card contains
two to four sentences, identifies the selected item, and includes
its correct price and platform without inventing a brand.
A missing fit card counts as a failure.


**Why this target:**

The caption should be short enough for a social post while giving
accurate information about the find. Its price and platform must match
the selected listing, and an unknown brand should remain unknown.
I chose 4 of 5 because model-generated text can vary in format.
A run passes only when it satisfies every requirement, so this target
still demands consistent factual and formatting quality.


---

## 5. Your choice

For 5 different searches with a specified maximum price and at least
one known matching listing within budget, search_listings returns
at least one result, and every returned listing has a price less
than or equal to that maximum. All 5 searches must pass.



**Why this target:**
The maximum price represents the user's budget. Returning a listing
above it would violate the request, even if the item matched the
description and size. I chose 5 of 5 because numeric price filtering
is deterministic. Requiring a result when a known match exists also
prevents an empty list from counting as a successful budget check.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
