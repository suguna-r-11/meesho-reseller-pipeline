# Agent Specification: Category Growth Monitoring Agent

## 1. Goal

Keep Meesho category managers informed of any category whose month-on-month revenue moves beyond the 8% threshold, with a human approving every message before it goes out.

## 2. Tools

The agent only calls these existing functions. It does not re-implement them.

- validate_feed(csv_path) (Part 2, growth_engine.py): input check on a month,category,revenue,n_orders CSV.
- mom_growth(previous, current) (Part 2): Month-on-Month growth percentage, rounded to 2 decimals.
- is_flagged(mom_pct, threshold=8.0) (Part 2): returns "flagged", "not_flagged" or "escalate_exact_boundary".
- fill_template(category, previous_revenue, current_revenue, mom_pct, month, prev_month) (Part 3, narrative_template.py): the offline prompt-pack template fill that drafts a Context, Insight, Implication message.
- Input data: part1_sql/output/monthly_category_revenue.csv (Part 1), split into one CSV per month.

## 3. Memory / State

The agent must remember between runs:

- The previous month's revenue per category, so the next run can compute Month-on-Month growth.
- The month name of the previous feed, so messages can say for example "May versus April".
- The list of categories suppressed in the last run, so a person can review them manually.

In this mock runner the previous month's state is supplied as a CSV file, so nothing is stored inside the program itself.

## 4. Planner (ordered subtasks)

1. Load the monthly revenue feeds (previous and current month) and run validate_feed on them.
2. If either feed is invalid, Hard Stop and report the validation errors.
3. If valid, compute mom_growth for every category against the previous month.
4. Run is_flagged on every category.
5. Sort the flagged categories by abs(mom_pct), largest first.
6. Draft a message (via Part 3's template) for at most the top 3 flagged categories. This cap prevents the notification-flooding failure mode of drafting, and eventually sending, one message per flagged item with no limit.
7. Log any remaining flagged categories beyond the cap as "suppressed, review manually", without drafting a message for them.
7b. Separately, log any category whose is_flagged result is "escalate_exact_boundary" into escalated_categories, without drafting a message for it. An exact-boundary category is neither flagged nor not_flagged, so it must never be silently dropped from both lists or mistaken for either one.
8. Emit one structured JSON object for the run.

## 5. Feedback Loop

Human approval is the checkpoint before any drafted message counts as sent. The runner never sends anything. It drafts messages and marks the run as drafted_and_held_for_approval, and a person reviews each draft (and the suppressed and escalated lists) before anything is released. This is simulated as the action_taken flag in the JSON output. No email or SMTP integration is used.

## 6. Guardrails

- Input guardrail: validate_feed must pass on both feeds before anything else runs. If it does not, nothing is computed.
- Action guardrail: no message is ever auto-sent. Messages are only drafted and held for human approval. At most 3 messages are drafted per run.
- Output guardrail: every number in a drafted message must trace back to a Part 1 or Part 2 value (previous revenue, current revenue, or mom_pct). No invented figures, and no reseller is named.

## 7. Stopping Conditions

- Success: drafts are produced (or correctly zero drafts, if nothing crossed the threshold) with every number traceable to Part 1 or Part 2. The run ends with action_taken = "drafted_and_held_for_approval".
- Error: validate_feed returns False. The run is a Hard Stop with the validation errors surfaced in validation_errors and action_taken = "hard_stop". It is never a silent skip.

## 8. Output Schema

Every run, success or Hard Stop, emits one JSON object with exactly these top-level keys:

- run_month: the month being reported.
- validation_status: "valid" or "invalid".
- validation_errors: list of error strings (empty on success).
- flagged_categories: list of objects with category, mom_pct, previous_revenue, current_revenue, drafted (true), and message.
- suppressed_categories: list of category names flagged beyond the cap of 3 (empty if none).
- escalated_categories: list of category names whose result was "escalate_exact_boundary" (empty in the real May and June scenarios).
- action_taken: "drafted_and_held_for_approval" or "hard_stop".

## 9. Given-When-Then Specs

1. GIVEN the April and May feeds are valid and Ethnic Wear revenue moves from 104520.77 to 185107.61, WHEN the agent runs, THEN it computes a Month-on-Month change of 77.1%, classifies it as "flagged", and lists Ethnic Wear first in flagged_categories with a drafted message.

2. GIVEN the May and June feeds are valid and Beauty & Personal Care revenue moves from 35542.11 to 37559.07, WHEN the agent runs, THEN it computes 5.67%, classifies it as "not_flagged", and Beauty & Personal Care appears in neither flagged_categories nor suppressed_categories.

3. GIVEN a synthetic pair with previous revenue 100000 and current revenue 108000, WHEN the agent runs, THEN it computes exactly 8.0%, classifies it as "escalate_exact_boundary", places the category in escalated_categories, and drafts no message for it. It is neither flagged nor dropped.

4. GIVEN the corrupted feed (part2_engine/fixtures/corrupted_feed.csv) as the current month, WHEN the agent runs, THEN validation_status is "invalid", action_taken is "hard_stop", validation_errors contains exactly the negative-revenue error (line 3), the missing-category error (line 4) and the missing-revenue error (line 6) in that order, and flagged_categories and suppressed_categories are both empty.