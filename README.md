# Meesho Reseller Growth & Alert Intelligence Pipeline

A small monitoring pipeline for Meesho's reseller-ops team. Instead of someone eyeballing last month's spreadsheet and typing up an update by hand, the pipeline does the repetitive work the same way every time: it pulls real numbers out of a database, decides what counts as a "significant" change, drafts a short message about it, and then stops and waits for a person to approve it.

It is four parts that feed into each other, and everything runs on the Python standard library only.

## Contents

1. [Requirements](#requirements)
2. [Repository layout](#repository-layout)
3. [Quick start](#quick-start)
4. [Running each part in detail](#running-each-part-in-detail)
5. [How the parts connect](#how-the-parts-connect)
6. [Workflow patterns](#workflow-patterns)
7. [Documentation referenced](#documentation-referenced)

## Requirements

- Python 3.8 or newer (on Windows, use `py` instead of `python` if the first one doesn't work)
- The `sqlite3` command-line shell, only if you want to re-run the Part 1 exports yourself. The results are already saved in the repo.

**No API keys, no accounts, nothing paid.** The "AI narrative" step is a plain template-fill function that works offline, so the whole pipeline (every acceptance criterion in the brief) runs correctly with zero API keys set. I did not wire in a real LLM.

## Repository layout

```
data/             generate_dataset.py, resellers.csv, orders.csv, meesho_reseller.db
part1_sql/        queries.sql, output/*.csv, output/README.md
part2_engine/     growth_engine.py, test_growth_engine.py, fixtures/*.csv
part3_narrative/  prompt_pack.md, narrative_report.md, masking.py,
                  narrative_template.py, test_masking.py
part4_agent/      agent_spec.md, mock_agent_runner.py,
                  test_mock_agent_runner.py, fixtures/*.csv, output_*.json
```

## Quick start

Run every command from the repository root, in this order.

| Step | What it does | Command | Expected result |
|------|--------------|---------|-----------------|
| 0 | Regenerate the dataset | `python data/generate_dataset.py` | `Wrote 24 resellers and 900 orders. Zero-order reseller: RS024` |
| 1 | Part 1: SQL queries | `sqlite3` shell (see below) | CSVs in `part1_sql/output/` (already committed) |
| 2 | Part 2: engine tests | `python part2_engine/test_growth_engine.py` | `OK` (7 tests) |
| 3a | Part 3: example messages | `python part3_narrative/narrative_template.py` | Two drafted messages printed |
| 3b | Part 3: masking tests | `python part3_narrative/test_masking.py` | `OK` |
| 4a | Part 4: agent tests | `python part4_agent/test_mock_agent_runner.py` | `OK` (5 tests) |
| 4b | Part 4: May run | `python part4_agent/mock_agent_runner.py may` | One JSON object |
| 4c | Part 4: June run | `python part4_agent/mock_agent_runner.py june` | One JSON object |
| 4d | Part 4: corrupted feed | `python part4_agent/mock_agent_runner.py corrupted` | One JSON object (hard stop) |

## Running each part in detail

### Step 0: Generate the dataset

```
python data/generate_dataset.py
```

Expected output:

```
Wrote 24 resellers and 900 orders. Zero-order reseller: RS024
```

This creates `data/resellers.csv`, `data/orders.csv` and `data/meesho_reseller.db`. The random seed is fixed (42), so the output is identical every time.

### Part 1: SQL business queries

- **Where:** `part1_sql/queries.sql`
- **What:** the five business queries, plus the RS024 `COUNT(*)` vs `COUNT(order_id)` demo
- **Output:** `part1_sql/output/*.csv`, already committed, so re-running is optional

Each query has a `-- name:` line above it that says which output file it belongs to. To re-run one, open the database and export its result:

```
sqlite3 data/meesho_reseller.db
.headers on
.mode csv
.output part1_sql/output/monthly_category_revenue.csv
# paste the matching query from queries.sql here, ending with ;
.output stdout
.quit
```

The query 1 export, `monthly_category_revenue.csv`, is the file Parts 2 and 4 consume directly.

**Why the RS024 demo matters:** a LEFT JOIN gives an unmatched reseller one row full of NULLs, and `COUNT(*)` counts that row as 1. `COUNT(order_id)` skips NULLs, so it correctly gives 0. That is why `COUNT(*)` can't be used to detect a reseller with no orders. The full explanation is in `part1_sql/output/README.md` and in the SQL comments.

### Part 2: Growth engine and input guardrail

- **Where:** `part2_engine/growth_engine.py`
- **Tests:** `part2_engine/test_growth_engine.py`

```
python part2_engine/test_growth_engine.py
```

Expected output: `OK`

The 7 tests are the four required Given-When-Then cases, a check that the clean feed passes validation, and the full May-vs-April and June-vs-May month-on-month tables.

### Part 3: Narrative and masking

- **Where:** `part3_narrative/`
- **Written deliverables:** `prompt_pack.md` and `narrative_report.md`

```
python part3_narrative/narrative_template.py
python part3_narrative/test_masking.py
```

The first command prints two example drafted messages. The second runs the masking tests, including the negative case where a version of the text that leaks a real reseller name is supposed to fail. Expected output for the tests: `OK`

### Part 4: Agent spec and mock runner

- **Where:** `part4_agent/`
- **Specification:** `agent_spec.md`
- **Saved sample runs:** `output_may.json`, `output_june.json`, `output_corrupted.json`

```
python part4_agent/test_mock_agent_runner.py
python part4_agent/mock_agent_runner.py may
python part4_agent/mock_agent_runner.py june
python part4_agent/mock_agent_runner.py corrupted
```

The first command runs 5 agent-level tests (expected output: `OK`). The other three each print one JSON object.

## How the parts connect

| From | To | What is passed |
|------|----|----------------|
| Part 1 | Part 2 | `part1_sql/output/monthly_category_revenue.csv` with columns `month,category,revenue,n_orders`. A copy sits in `part2_engine/fixtures/`, and `validate_feed` returns `(True, [])` on it. |
| Parts 1 and 2 | Part 3 | Verified numbers go into a fixed template (`fill_template`). Reseller names are always replaced with an alias. |
| Part 1 | Part 4 | The same CSV is split into `april.csv`, `may.csv` and `june.csv` in `part4_agent/fixtures/`. |
| Parts 2 and 3 | Part 4 | The runner imports Part 2's functions unmodified and Part 3's `fill_template`, then runs one guarded, human-reviewed workflow. |

## Workflow patterns

| Part | Pattern it follows | In practice |
|------|--------------------|-------------|
| Part 1 to Part 2 | Compute real numbers via SQL first, then hand off | Numbers come from queries and are never typed or estimated by hand. |
| Part 2 | Turn a vague phrase into a testable rule | "Significant change" becomes a number: flagged, not flagged, or held for a person if it lands exactly on the 8% boundary. An input check runs first. Tested in Given-When-Then style. |
| Part 3 | Reusable prompt pack | Trigger, Input list, Prompt, Checklist. Writes in a Context, Insight, Implication shape, labels claims as fact or hypothesis, and masks reseller names in external text. |
| Part 4 | Intake, Summary, Report Draft, Validate | Load and validate the feeds, work out the changes, draft a capped number of messages, then hold everything for human approval with every number traceable. Invalid input causes a hard stop, not a quiet skip. |

## Documentation referenced

- Official Python standard-library documentation: `random`, `csv`, `os`, `sqlite3`, `json`, `re`, `tempfile`, `unittest`
- SQLite command-line shell documentation: `.headers`, `.mode`, `.output`
