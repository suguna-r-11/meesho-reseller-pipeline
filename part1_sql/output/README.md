# Part 1 output notes

Queries are in `part1_sql/queries.sql`. Each was run in the sqlite3 command-line
shell against `data/meesho_reseller.db` and exported with `.headers on`, `.mode csv`
and `.output <file>`.

| File | Query | Result |
|---|---|---|
| monthly_category_revenue.csv | Q1 | 15 rows; input for Part 2 and Part 4 |
| region_revenue.csv | Q2 | North 337125.46 (231), West 333106.33 (232), South 316736.68 (216), East 275098.45 (221) |
| top_resellers.csv | Q3 | RS019, RS022, RS012, RS006, RS005 |
| never_ordered.csv | Q4a | RS024, Ahmedabad Reseller 6, West |
| count_star_vs_count_col.csv | Q4b | RS024: count_star = 1, count_order_id = 0 |
| june_delivered_aov.csv | Q5 | 1267.69 |

## Why COUNT(*) is the wrong way to test for a zero-match LEFT JOIN row

A LEFT JOIN keeps every row from the left table. A reseller with no orders still
appears as a single row in which all columns from `orders` are NULL. `COUNT(*)` counts
rows, so for RS024 it returns 1. `COUNT(o.order_id)` counts only non-NULL values, so it
returns 0, the true number of orders. `COUNT(*)` can never be 0 for a reseller in a
LEFT JOIN result, so it cannot detect the zero-match case. Use `WHERE o.order_id IS NULL`
or `COUNT(o.order_id) = 0` instead.