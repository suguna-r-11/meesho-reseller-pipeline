# Prompt Pack: Flagged-Category Stakeholder Update

## Trigger

Run this prompt when a category's `is_flagged(mom_pct)` result (Part 2) is `"flagged"`.
It is not run for `"not_flagged"`. For `"escalate_exact_boundary"` no message is drafted;
the category is held for human review.

## Input list

| Placeholder | Meaning | Source |
|---|---|---|
| `{category}` | Category name, e.g. Ethnic Wear | Part 1 `monthly_category_revenue.csv` |
| `{prev_month}` | Earlier month, e.g. April | Part 1 |
| `{month}` | Later month, e.g. May | Part 1 |
| `{previous_revenue}` | Revenue in `{prev_month}`, INR | Part 1 |
| `{current_revenue}` | Revenue in `{month}`, INR | Part 1 |
| `{mom_pct}` | Month-on-Month growth percentage | Part 2 `mom_growth` |

## Prompt

```
You are writing a short update for a Meesho regional category manager.

Category: {category}
Period: {month} versus {prev_month}
Revenue in {prev_month}: INR {previous_revenue}
Revenue in {month}: INR {current_revenue}
Month-on-Month change: {mom_pct}%

Write the update in exactly three parts:
1. Context: what is measured (revenue for {category}) and over which months.
2. Insight: state the change of {mom_pct}% and label it "fact".
3. Implication: give one specific next step naming what to check or do. If the
   step assumes a cause the data does not prove, label it "hypothesis".

Rules:
- Use only the numbers supplied above. Never state any other number.
- Do not mention any reseller by name. If a reseller is referenced, use only its
  region and its alias (for example ALIAS-19).
- Write for a regional manager, not a data engineer. Avoid technical jargon.
- Do not overstate: describe what the numbers show, not what they prove.
```

The offline implementation of this prompt is `fill_template` in `narrative_template.py`.
It fills the same Context, Insight, Implication structure from the same six inputs.

## Checklist (run on every draft before use)

- [ ] Every number in the draft matches a supplied placeholder value exactly
      (`{previous_revenue}`, `{current_revenue}`, `{mom_pct}`); no invented figures.
- [ ] The category name and both month names are correct.
- [ ] The insight is labelled as a fact, and any proposed cause is labelled as a hypothesis.
- [ ] The recommendation is specific and actionable (it names what to check or do),
      not vague like "look into it".
- [ ] No reseller is referenced by raw name; only region and alias are used
      (verified with `assert_no_raw_names_leak`).
- [ ] The draft is written for a regional manager and follows Context → Insight → Implication.
- [ ] The draft is held for human approval and is never auto-sent.