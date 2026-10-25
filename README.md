# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory


### `search_listings`

- **What it does:** Loads listings with `load_listings()`, applies any size and price filters, and ranks matches by the number of distinct query keywords found in the title, description, and style tags, ignoring capitalization. Listings with no keyword matches are excluded.
- **Inputs:** `description` (str): clothing keywords; `size` (str or None, default None): optional size filter; `max_price` (float or None, default None): inclusive maximum price. Size matching ignores capitalization and compares complete size labels or slash-separated alternatives, so M matches S/M, but L does not match XL and S does not match US 9. Parenthetical fit notes are ignored, so XL matches XL (oversized). Numeric sizes otherwise require the full label, such as W30 L30. None skips the corresponding filter.
- **Returns:** A `list[dict]` containing at most `config.SEARCH_RESULT_LIMIT` matching listings, ranked by keyword score from highest to lowest, with ties kept in data-file order. Each dictionary contains `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`. The `brand` value may be None.
- **When it has nothing:** Returns an empty list `[]` when nothing matches, including when the description has no searchable keywords.

### `suggest_outfit`

- **What it does:** Calls the model through `generate()` to suggest one or two outfits combining the selected listing with pieces in the user's wardrobe.
- **Inputs:** `new_item` (dict): a selected listing returned by `search_listings`; `wardrobe` (dict): an `items` list containing wardrobe dictionaries with `id`, `name`, `category`, `colors`, `style_tags`, and optional `notes`.
- **Returns:** A non-empty string describing one or two outfit ideas using the selected item and naming relevant pieces from the supplied wardrobe.
- **When it has nothing:** If the wardrobe has an empty `items` list, returns general styling advice for the selected item without claiming the user owns the suggested pieces.

### `create_fit_card`

- **What it does:** Calls the model through `generate()` to turn an outfit suggestion and listing details into a short social-media caption.
- **Inputs:** `outfit` (str): the suggestion returned by `suggest_outfit`; `new_item` (dict): the same selected listing used for the outfit suggestion.
- **Returns:** A string containing a two-to-four-sentence caption that mentions the item, its price, and its platform once each and describes the outfit's style. A missing brand is omitted rather than invented.
- **When it has nothing:** If `outfit` is empty or contains only whitespace, returns "Cannot create a fit card without an outfit suggestion." without calling the model.


## Planning Loop

**Where it lives:** `agent.py::run_agent`.

The implemented loop moves through parsing, search, outfit suggestion,
and fit-card generation. Each iteration checks the maximum iteration
limit. An empty search returns the session immediately with a helpful
error message and no outfit or fit card.

**How the query is parsed:** Use regular expressions to extract the
description, optional size, and optional maximum price. Save these
values in session["parsed"].

**Branch rule:** Call search_listings and save its results in
session["search_results"].

If the results are empty, set session["error"] to:
"No matching listings. Try broader description keywords, a different
size, or a higher maximum price."

Stop immediately without calling suggest_outfit or create_fit_card.
Leave session["fit_card"] as None.

Otherwise, save the first matching listing in session["selected_item"].
Read that item and session["wardrobe"] to call suggest_outfit, then
save its response in session["outfit_suggestion"].

Read the saved outfit suggestion and selected item to call
create_fit_card. Save its response in session["fit_card"] and return
the session.

**Loop limit:** Check each iteration with trace.check_iterations
to enforce the starter's maximum iteration limit.

## Sample Run
### Session-state verification

I used temporary wrappers around the real tools to inspect their inputs.
The selected listing ID matched the item passed to both tools, and
create_fit_card received the outfit text saved in the session.

```text
{'create_fit_card_item_id': 'lst_002',
 'error': None,
 'parsed': {'description': 'vintage graphic tee',
            'max_price': 30.0,
            'size': 'M'},
 'same_item': True,
 'saved_outfit_passed_to_card': True,
 'selected_item_id': 'lst_002',
 'suggest_outfit_item_id': 'lst_002'}
```

This verifies one successful run. Repeated evaluation against the
five acceptance criteria will take place in Unit 4.
### Fit-card variation check

Function: tools.py::create_fit_card.

I generated three captions using the same listing and outfit suggestion,
with caching disabled for this command only.

```powershell
python -c "import config; config.CACHE_ENABLED = False; from tools import create_fit_card; from utils.data_loader import load_listings; item = load_listings()[0]; outfit = 'Pair with a white t-shirt and white sneakers for a casual look.'; print('Listing:', item['title'], item['price'], item['platform']); [print('\nRUN', i + 1, '\n', create_fit_card(outfit, item)) for i in range(3)]"
```

```text
Listing: Vintage Levi's 501 Jeans — Medium Wash 38.0 depop

RUN 1
Complete your casual everyday look by pairing these Vintage Levi's 501 Jeans — Medium Wash with a crisp white t-shirt and white sneakers. Grab these classic denim bottoms on depop for $38.00before they're gone!

RUN 2
Level up your casual everyday rotation with these classic Levi's 501 Jeans featuring a timeless medium wash and effortless streetwear appeal. Pair them with a simple white t-shirt and fresh white sneakers for an effortless weekend aesthetic. Score this vintage piece for $38.00 on depop before it's gone!

RUN 3
Achieve an effortless, casual look by pairing these vintage Levi's 501 Jeans with a simple white t-shirt and white sneakers. Grab this classic denim staple for $38.00 on depop.
```

The captions differed and contained two, three, and two sentences.
Each included the correct price and platform. However, the first two
added urgency that was not supported by the listing. Variation alone
does not guarantee that every statement is grounded.



**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```

```
$ python -c "from tools import suggest_outfit; ..."

```

```
$ python -c "from tools import create_fit_card; ..."

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
