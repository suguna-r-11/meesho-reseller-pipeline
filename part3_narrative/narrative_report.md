# Narrative Report

All figures come from Part 1 (`monthly_category_revenue.csv`, `region_revenue.csv`, `top_resellers.csv`) and Part 2 (`mom_growth`, `is_flagged`).

## 1. Worked narrative: May Ethnic Wear (flagged)

**Context:** This update covers Ethnic Wear revenue for May compared with April, taken from the monthly category revenue report built from the reseller order data.

**Insight (fact):** Ethnic Wear revenue rose from INR 104520.77 in April to INR 185107.61 in May, a Month-on-Month change of 77.1%. This is flagged as a significant change.

**Implication (hypothesis, not proven by this data alone):** The jump may come from a small group of resellers or from a short-term demand event, but the data does not show which. Recommended next step: split May's Ethnic Wear orders by reseller and region to see whether the rise is broad or concentrated, and confirm stock availability and return rates for Ethnic Wear before the next month.

## 2. Worked narrative: June Ethnic Wear (flagged, opposite direction)

**Context:** This update covers Ethnic Wear revenue for June compared with May, taken from the same monthly category revenue report.

**Insight (fact):** Ethnic Wear revenue fell from INR 185107.61 in May to INR 76371.53 in June, a Month-on-Month change of -58.74%. This is flagged as a significant change, in the opposite direction to May.

**Implication (hypothesis, not proven by this data alone):** May may have been a one-off spike that has now reversed, or resellers may have reduced their Ethnic Wear listings; the data alone cannot distinguish the two. Recommended next step: compare Ethnic Wear order counts by reseller and region between May and June, and check whether any resellers stopped listing Ethnic Wear products before adjusting stock plans.

## 3. Self-score against the refinement checklist

**May Ethnic Wear narrative**
- **Specificity:** it names the correct category (Ethnic Wear), the correct months (April and May), and the exact figures 104520.77, 185107.61 and 77.1%.
- **Audience fit:** it is written in plain business language for a regional manager, with no technical terms such as SQL or function names.
- **Completeness:** it contains a Context, an Insight labelled as a fact, and an Implication labelled as a hypothesis.
- **Actionability:** it gives a concrete next step (split May orders by reseller and region, and confirm stock and return rates) rather than a vague suggestion.

**June Ethnic Wear narrative**
- **Specificity:** it names the correct category, the correct months (May and June), and the exact figures 185107.61, 76371.53 and -58.74%.
- **Audience fit:** it uses plain language and states the direction of the change clearly for a regional manager.
- **Completeness:** it contains a Context, an Insight labelled as a fact, and an Implication labelled as a hypothesis.
- **Actionability:** it gives a concrete next step (compare order counts by reseller and region, and check for stopped listings) before stock plans are changed.

## 4. Chart-choice justification (text only, no images)

**Question 1: "Which month had the highest total revenue?"** (April = INR 419417.43, May = INR 444594.25, June = INR 398055.24). I would use a simple vertical bar chart with one bar per month. This is a bivariate view: one categorical variable (month) against one numeric variable (total revenue). A bar chart lets the reader compare heights and see within 10 seconds that May is the tallest. The y-axis must start at zero, because the three totals are close together and a truncated axis would exaggerate the gaps. There is only one series, so no legend is needed, and I would not use 3D because it distorts bar heights.

**Question 2: "What percentage share does Ethnic Wear represent of April's total revenue?"** (INR 104520.77 of INR 419417.43 = 24.92%). I would use a donut chart of April's five categories with the Ethnic Wear slice highlighted and labelled 24.92%. This is a part-to-whole question about one variable (category share of a single total), so a donut fits because there are only five slices and the message is one slice's share. The other slices are muted and labelled directly, so no legend is needed, the message reads within 10 seconds, and I would keep it flat, never 3D. The zero-baseline rule does not apply to a donut, but if there were many categories I would switch to a sorted bar chart instead.

**Question 3: "How do the four regions compare on total revenue?"** (North INR 337125.46, West INR 333106.33, South INR 316736.68, East INR 275098.45). I would use a bar chart with one bar per region, sorted from highest to lowest. This is a bivariate comparison of one categorical variable (region) against one numeric variable (revenue). The y-axis must start at zero so the differences are shown at their true size and East is not made to look far smaller than North. It is a single series so no legend is needed, the sorted order shows the ranking in about 10 seconds, and 3D is avoided.

## 5. Top-reseller narrative (masked for external use)

**Context:** This summary covers total order spend per reseller across April to June, for resellers whose total spend was above INR 50000. Resellers are shown only by region and alias.

**Insight (fact):** Five resellers passed that level. In the West region, ALIAS-19 led with INR 75295.09 and ALIAS-22 followed with INR 73882.33. In the South region, ALIAS-12 recorded INR 69936.46. In the North region, ALIAS-06 recorded INR 64238.97 and ALIAS-05 recorded INR 61825.02. These totals include orders of every status, so they are not limited to delivered orders.

**Implication (hypothesis, not proven by this data alone):** Spend may be concentrated in a small group of resellers, but this data alone cannot show how much of it is delivered revenue. Recommended next step: for each of these aliases, check the share of returned and cancelled orders before treating them as the region's strongest performers.