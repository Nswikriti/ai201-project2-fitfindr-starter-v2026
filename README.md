# FitFindr

Swikriti Neupane

See [RUNNING.md](RUNNING.md) for environment setup and commands.

> 

## What This Does

FitFindr helps users explore a local dataset of 40 mock secondhand
clothing listings. A user enters clothing keywords and optionally a
size and maximum price, and the agent selects the highest-ranked
matching listing. It uses Gemini to suggest outfits using the supplied
wardrobe and create a short caption with the item's price and platform.
If nothing matches, it stops and suggests changes to the search.
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
### One full query

Command:

```powershell
python app.py ask 'vintage graphic tee under $30, size M'
```

Actual output:

```text
Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

Outfit:   Outfit 1:
Pair the Y2K Baby Tee — Butterfly Print with the Baggy straight-leg jeans, dark wash, and finish with the Chunky white sneakersfor a classic Y2K streetwear look.

Outfit 2:
Combine the Y2K Baby Tee — Butterfly Print with the Wide-leg khaki trousers, layered under the Vintage black denim jacket, and complete the outfit with the Chunky white sneakers.

Fit card: Channel classic Y2K streetwear by styling this graphic tee with baggy straight-leg jeans and chunky white sneakers.Grab the Y2K Baby Tee — Butterfly Print on Depop for $18.00 to complete your vintage rotation.

2 model calls this session, 1104 prompt + 135 output tokens
```

### Empty-search branch

Command:

```powershell
python app.py ask 'designer ballgown size XXS under $5'
```

Actual output:

```text
No matching listings. Try broader description keywords, a different size, or a higher maximum price.

0 model calls this session
```

### Individual tool tests

#### search_listings

Command:

```powershell
python -c "from tools import search_listings; from pprint import pprint; pprint(search_listings('graphic tee', max_price=30))"
```

The actual output contained six listing dictionaries, with IDs
lst_002, lst_006, lst_017, lst_033, lst_011, and lst_015.
Their prices were 18, 24, 15, 19, 27, and 26 respectively.
The full output should be pasted below.

#### suggest_outfit

Command:

```powershell
python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
```

Actual output:

```text
Outfit 1:
Pair the Vintage Levi's 501 Jeans with the White ribbed tank top, layered under the Oversized grey crewneck sweatshirt. Finish the look with the Chunky white sneakers and the Black crossbody bag.

Outfit 2:
Style the Vintage Levi's 501 Jeans with the White ribbed tank top and the Vintage black denim jacket on top. Accessorize with the Brown leather belt, and complete the outfit with the Black combat boots.
```

#### create_fit_card

Command:

```powershell
python -c "from tools import create_fit_card; from utils.data_loader import load_listings; item = load_listings()[0]; print('Listing:', item['title'], item['price'], item['platform']); print(create_fit_card('Pair with a white t-shirt and white sneakers for a casual look.', item))"
```

Actual output:

```text
Listing: Vintage Levi's 501 Jeans — Medium Wash 38.0 depop
Channel casual style by pairing these classic blue Levi's 501 Jeans with a simple white t-shirt and fresh sneakers. These vintage denim bottoms feature a great medium wash and are available on depop for $38.00. Grab this timeless streetwear staple for your everyday wardrobe rotation today!
```
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


## How I Used AI

**Moment 1 — Implementing and checking the tools**

I asked Claude for implementation help based on the starter functions
and my Tool Inventory. It supplied keyword-search code and prompts for
the model-backed tools. My first tests returned empty results because
Python was still loading saved placeholder functions. I used the
suggested inspection commands, replaced the placeholders, saved the
file, and reran the tests. This showed me why checking the code actually
loaded by Python matters.

**Moment 2 — Connecting and checking session state**

I asked Claude to help connect the tools using the session dictionary.
It supplied a staged loop with an empty-search branch and an iteration
guard. I added it to agent.py and tested both a matching query and an
impossible query. I then ran its wrapper-based inspection to check the
actual tool inputs: all three listing IDs were lst_002, and the saved
outfit text matched the input passed to create_fit_card.



---

## Run Log — Before

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all tools | At least 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item stays consistent | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card has accurate details and length | At least 4 of 5 | PASS | FAIL | PASS | PASS | PASS | MET (4/5) |
| 5. Search respects the price ceiling | All 5 searches pass | PASS | PASS | PASS | PASS | PASS | MET |

Evidence: results/run_2026-10-25_2004_before.md, produced by
run_eval.py::main and run_eval.py::run_once.

Caching was disabled. Each scenario ran five times. For criterion 5,
each column represents a complete set of five different budget searches.
All 25 search executions returned nonempty results within their ceilings.

Criterion 4 was manually scored for sentence count, item identification,
correct attribution of price and platform, and absence of invented brands.
Decimal prices such as $18.0 were not counted as sentence boundaries.

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all tools | At least 4 of 5 | MET (5/5) | All five runs searched through MCP, called both model tools, and returned a fit card. |
| 2 | Empty search stops before outfit | 5 of 5 | MET (5/5) | All five runs returned actionable search advice. The recorded tool-call lists were empty for the two downstream tools. |
| 3 | Selected item stays consistent | 5 of 5 | MET (5/5) | In every try, selected_item and the actual inputs to both tools contained listing ID lst_002. |
| 4 | Fit card has accurate details and length | At least 4 of 5 | MET (4/5) | Try 2 attributed the price to a wardrobe accessory. The other four captions met the stated requirements. |
| 5 | Search respects the price ceiling | All 5 searches pass | MET | Every budget search returned results, and every returned price was within its ceiling in all five repetitions. |

**Diagnoses**



---

## Loop Trace

<### Model-unavailable check

I disabled caching and set an invalid API key only inside a temporary
Python process. The real key in .env was unchanged.

The trace reached search_listings through MCP, selected lst_002, and
stopped when suggest_outfit could not reach the model successfully.

Actual final output:

```text
ERROR: Outfit suggestions could not be generated. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
FIT CARD: None
1 model calls this session
```

The handler in agent.py::run_agent caught ModelUnavailable and returned
the session with an actionable error rather than a stack trace.

### Failure-mode summary

| Condition | Observed behavior |
|---|---|
| Empty search | Stopped before outfit and fit-card generation, suggested changes to the search, and made zero model calls. |
| Empty wardrobe | Returned general styling suggestions and completed the fit card. The check reused cached model responses. |
| Model unavailable | Returned API-key troubleshooting advice and stopped with fit_card set to None. |

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** I registered search_listings in mcp_server.py
with typed description, size, and max_price inputs. In
agent.py::run_agent, I replaced the direct search call with
mcp_client.call_tool("search_listings", session["parsed"]).

The server listed the expected tool and inputs. The matching query
still selected lst_002, the $18 Y2K Baby Tee, and completed the outfit
and fit card using cached model responses. The impossible query still
returned helpful advice and made zero model calls.


---

## The Improvement

**What I changed:**

I strengthened the system prompt in tools.py::create_fit_card.
It now requires the selected item's name, price, and platform in
the same sentence and explicitly distinguishes other outfit pieces
from the item being sold. No other agent behavior was changed.

**Which failure it was meant to fix:**

In criterion 4, baseline try 2, the caption attached the tee's $18
price to a crossbody bag. The change aims to make price attribution
explicit while preserving the original acceptance criteria.

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
