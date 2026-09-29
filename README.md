# Meesho Reseller Growth & Alert Intelligence Pipeline

An end-to-end, offline pipeline that turns reseller order data into verified numbers, a rule for "significant change", guarded narrative drafts, and a human-reviewed agent run. Everything runs with the Python standard library only.

## Requirements

- Python 3.8 or newer (on Windows use `py` in place of `python` if needed)
- The `sqlite3` command-line shell, only if you want to re-run the Part 1 exports
- **No API keys, no accounts and no paid services are needed. The whole pipeline (every acceptance criterion) works with zero API keys set, using only the offline template-fill path.**

## Repository layout

    data/             generate_dataset.py, resellers.csv, orders.csv, meesho_reseller.db
    part1_sql/        queries.sql, output/*.csv, output/README.md
    part2_engine/     growth_engine.py, test_growth_engine.py, fixtures/*.csv
    part3_narrative/  prompt_pack.md, narrative_report.md, masking.py,
                      narrative_template.py, test_masking.py
    part4_agent/      agent_spec.md, mock_agent_runner.py,
                      test_mock_agent_runner.py, fixtures/*.csv, output_*.json

## How to run each stage, in order (from the repository root)

### 0. Regenerate the dataset

    python data/generate_dataset.py

Expected output: `Wrote 24 resellers and 900 orders. Zero-order reseller: RS024`.
The seed is fixed, so the output is identical on every run.

### Part 1: SQL Business Query Engine

The five business queries (plus the RS024 `COUNT(*)` vs `COUNT(order_id)` demonstration) are in `part1_sql/queries.sql`. Each query is preceded by a `-- name:` line giving its output file name. To re-run one, open the database in the sqlite3 shell and export its result:

    sqlite3 data/meesho_reseller.db
    .headers on
    .mode csv
    .output part1_sql/output/monthly_category_revenue.csv
    (paste the query for that name from queries.sql, ending with ;)
    .output stdout
    .quit

The exported results are already committed in `part1_sql/output/`. The explanation of why `COUNT(*)` cannot detect a zero-match LEFT JOIN row is in `part1_sql/output/README.md` and in the SQL comments.

### Part 2: Guardrail and growth-detection engine

    python part2_engine/test_growth_engine.py

Runs 7 tests (the four required Given-When-Then cases, a clean-feed check, and the full May-vs-April and June-vs-May MoM tables). Expected: `OK`.

### Part 3: Narrative and prompt pack

    python part3_narrative/narrative_template.py
    python part3_narrative/test_masking.py

The first prints two example drafted messages. The second runs the masking tests, including the negative case where a leaky version fails. Expected: `OK`. The written deliverables are `prompt_pack.md` and `narrative_report.md`.

### Part 4: Agent spec and mock runner

    python part4_agent/test_mock_agent_runner.py
    python part4_agent/mock_agent_runner.py may
    python part4_agent/mock_agent_runner.py june
    python part4_agent/mock_agent_runner.py corrupted

The first command runs 5 agent-level tests (expected `OK`). The other three print one JSON object each. Sample outputs are saved as `part4_agent/output_may.json`, `output_june.json` and `output_corrupted.json`. The specification is `part4_agent/agent_spec.md`.

## How the Parts connect

1. Part 1's query 1 produces `part1_sql/output/monthly_category_revenue.csv` with columns `month,category,revenue,n_orders`.
2. Part 2 reads that exact file format. A copy of the Part 1 output is stored in `part2_engine/fixtures/`, and `validate_feed` runs on it and returns `(True, [])`.
3. Part 3 turns Part 1 and Part 2 numbers into narrative text using a fixed template (`fill_template`), with reseller names masked by alias.
4. Part 4 splits the same Part 1 output into one file per month (`part4_agent/fixtures/april.csv`, `may.csv`, `june.csv`), then the runner imports Part 2's functions unmodified and Part 3's `fill_template` to run one guarded, human-reviewed workflow.

## Workflow patterns

- **Part 1 to Part 2** follows the "compute real numbers via SQL first, then hand off" order of operations: the numbers are computed by queries, never typed or estimated.
- **Part 2** turns a vague phrase ("significant change") into a numeric, testable rule with three explicit outcomes and an input guardrail, tested Given-When-Then.
- **Part 3** uses a reusable prompt pack (Trigger, Input list, Prompt, Checklist) with a Context, Insight, Implication structure, fact and hypothesis labels, and a masking policy for external text.
- **Part 4** mirrors an Intake, Summary, Report Draft, Validate reporting flow: load and validate the feeds (intake), compute changes (summary), draft capped messages (report draft), and hold everything for human approval with every number traceable (validate).

## Documentation referenced

Official Python standard-library documentation for: `random`, `csv`, `os`, `sqlite3`, `json`, `re`, `tempfile` and `unittest`; and the SQLite command-line shell documentation (`.headers`, `.mode`, `.output`).
