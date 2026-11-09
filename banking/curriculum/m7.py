from common import *

M = "7 · Stakeholders and analyst craft"
L = []

L.append(lesson(32, M, "Stakeholders I: Finance, Treasury, Risk and Compliance", "Intermediate", ["Stakeholders"], f"""
## Objectives
- Know what control functions ask, which metrics they watch, and the data they need.
- Anticipate their objections to your numbers.

## Stakeholder cards
| | Finance (FP&A, Controllership) | Treasury / ALM | Risk Management | Compliance |
|---|---|---|---|---|
| **Typical questions** | Are we on budget? Why did NIM move? Does MIS tie to the GL? | What is our funding mix and cost? Liquidity under stress? Rate sensitivity? | Where is credit quality deteriorating? Are we within risk appetite? | Are KYC records complete? Any AML alerts unresolved? Are we meeting BSP deadlines? |
| **Metrics** | NII, NIM, CIR, ROE, budget variance | Cost of funds, CASA ratio, LCR, NSFR, gap | NPL, DQ, roll rates, ECL, RWA, concentration | KYC completeness, alert ageing, STR counts, complaints |
| **Data needs** | GL, account-level profitability, FTP | Deposit behaviour, maturities, rates | Loan-level DPD, collateral, ratings, vintages | Customer master, transaction monitoring, case data |
| **Pet peeves** | Numbers that don't reconcile | EOP vs ADB confusion | Growth hiding risk (denominator effect) | Personal data in spreadsheets |

## How a Data Analyst supports them
- **Finance:** publish a reconciliation pack with every profitability release (Lesson 29).
- **Treasury:** deposit stickiness and concentration data products (Lesson 23).
- **Risk:** vintage and roll-rate marts with stable definitions (Lesson 22).
- **Compliance:** DQ dashboards on KYC fields and masked data access (Lesson 24).

{illustrative('''
Finance challenges your segment report: total NII is ₱3M below the GL. You reply with a reconciliation: ₱1.25M manual accrual (GL only), ₱1.4M treasury securities income (not in customer segments by design), ₱0.35M unmapped products under investigation. Finance is satisfied because every peso is explained.
''')}

## Hands-on (12 min)
For each of the four functions, write one question they could ask about the sample bank and the SQL table(s) you would use to answer it. Answer one of them with a query.

## Review questions
1. Why does Finance care most about reconciliation?
2. Which Treasury metric would a CASA decline affect first?
3. What is Risk's typical objection to a growth-focused dashboard?

{answers('''
1. They own the official numbers; unreconciled MIS creates two versions of the truth in front of management.
2. Cost of funds (and the CASA ratio itself); in stress, also LCR via run-off assumptions.
3. Growth flatters delinquency ratios (denominator effect); they want vintage views and credit cost alongside growth.
''')}
"""))

L.append(lesson(33, M, "Stakeholders II: business units, product, marketing, operations and senior management", "Intermediate", ["Stakeholders"], f"""
## Objectives
- Know what revenue-generating and support units ask and need.
- Tailor the same data to different audiences.

## Stakeholder cards
| Unit | Typical questions | Key metrics | Data needs |
|---|---|---|---|
| **Retail / Consumer Banking** | Which branches/regions grow deposits? Where are we losing customers? | ADB growth, new-to-bank, attrition, products per customer | Customer, account, branch, channel |
| **Corporate / Business Banking** | Which relationships are most profitable? What is wallet share? | Relationship RAROC, fee income, deposit balances | Relationship hierarchies, FTP, fees, limits |
| **Product Management** | Is the product profitable? Who uses it? | CM1–CM3, take-up, activation, churn | Account-level profitability, usage |
| **Marketing** | Did the campaign work? Who should we target? | Response rate, incremental balances, CAC, CLV | Campaign lists, control groups, outcomes |
| **Sales** | Am I hitting target? Which leads convert? | Sales vs target, conversion, pipeline | CRM, product opening data |
| **Operations** | Where are bottlenecks? | Turnaround time, error rates, cost per transaction | Process logs, transaction volumes |
| **Senior management** | Are we on plan? Where do we invest? What are the risks? | Net income, ROE, NIM, CIR, NPL, market share | Certified KPIs, short narrative |

## Tailoring the message
Same fact: "Mass segment savings balances fell 3% in Q3."
- **Retail head:** which regions and branches, how many customers, which competitor offers.
- **Treasury:** impact on cost of funds and LCR.
- **Senior management:** one line – size, cause, action, owner.

{illustrative('''
Marketing claims a campaign drove ₱500M of new deposits. Your analysis: the target group grew ₱500M, but a random control group (not contacted) grew ₱380M over the same period. **Incremental** effect = ₱120M. Always ask for a control group.
''')}

## Hands-on (12 min)
{sql('''
-- Retail view: savings balance growth by region, Mar -> Sep 2026
SELECT c.region,
       ROUND(SUM(CASE WHEN m.month = '2026-03' THEN m.eop_balance END)/1e6, 1) AS mar_m,
       ROUND(SUM(CASE WHEN m.month = '2026-09' THEN m.eop_balance END)/1e6, 1) AS sep_m,
       ROUND(100.0 * (SUM(CASE WHEN m.month = '2026-09' THEN m.eop_balance END)
                    / SUM(CASE WHEN m.month = '2026-03' THEN m.eop_balance END) - 1), 1) AS growth_pct
FROM monthly_account m JOIN accounts a USING (account_id) JOIN customers c USING (customer_id)
WHERE a.product_code = 'SA'
GROUP BY c.region ORDER BY growth_pct DESC;
''')}
Write the finding three ways: for the Retail head, for Treasury, and for the CEO (one line each).

## Review questions
1. What is the difference between gross and incremental campaign impact?
2. Why does senior management want fewer metrics, not more?
3. What does Product Management need that Finance does not?

{answers('''
1. Gross is total change in the targeted group; incremental is the change above what a comparable untreated (control) group did.
2. Their job is decisions across the whole bank; a short certified set with a narrative is actionable, a long list is noise.
3. Account-level usage and behaviour (activation, churn, utilisation) and product-level contribution layers, not just GL totals.
''')}
"""))

L.append(lesson(34, M, "Requirements, metric definitions and challenging inconsistent numbers", "Advanced", ["Stakeholders", "Data"], f"""
## Objectives
- Run a requirements conversation that produces a clear specification.
- Clarify metric definitions before building.
- Challenge inconsistent figures politely and with evidence.

## The requirements checklist
1. **Decision:** what decision will this report support? (If none, push back.)
2. **Audience and frequency.**
3. **Metrics:** for each – definition, formula, balance type (ADB/EOP), period (MTD/YTD), currency, inclusions/exclusions.
4. **Dimensions and grain:** product, segment, channel, branch, customer, account; as-of logic for changing attributes.
5. **Source of truth:** certified data product? GL reconciliation needed?
6. **Comparisons:** vs last month, last year, budget.
7. **Access and privacy:** who may see account- or customer-level detail.
8. **Acceptance test:** "the report is right if total NII ties to GL ±0.5%".

## Challenging numbers: a script
> "Thanks – before we use this, can we align on definitions? Your deposits figure is ₱12.1B; the certified mart shows ₱11.9B as of the same date. The ₱0.2B difference matches the balance of accounts closed on the 30th; your extract seems to be from the 29th. Could we re-run on the month-end snapshot?"

Notice the pattern: **acknowledge → compare like-for-like → quantify → hypothesise → propose a fix.** Never "your number is wrong".

## Common causes of mismatches
EOP vs ADB · different as-of dates · different scope (incl./excl. closed, dormant, staff, internal accounts) · old vs new segment assignment · FX conversion date · duplicates · GL adjustments · gross vs net of allowance.

## Hands-on (12 min)
Two "reports" for Sep 2026 personal loans:
{sql('''
SELECT 'Report A (EOP, all accounts)' AS report, ROUND(SUM(m.eop_balance)/1e6, 2) AS pl_balance_m
FROM monthly_account m JOIN accounts a USING (account_id) WHERE a.product_code = 'PL' AND m.month = '2026-09'
UNION ALL
SELECT 'Report B (ADB, excl. 90+)', ROUND(SUM(m.avg_balance)/1e6, 2)
FROM monthly_account m JOIN accounts a USING (account_id) WHERE a.product_code = 'PL' AND m.month = '2026-09' AND m.dpd_bucket <> '90+';
''')}
Write the reconciliation: start from A, show each step to B with amounts (two steps: EOP→ADB, exclude 90+). Then write a 3-sentence message to the requester using the script above.

## Review questions
1. Why ask "what decision will this support?" first?
2. List four common causes of two numbers disagreeing.
3. What makes a challenge land well with a senior stakeholder?

{answers('''
1. It sets scope and priority, avoids building unused reports, and drives the right metric definitions.
2. Any four: balance type, as-of date, scope, segment logic, FX, duplicates, GL adjustments, gross vs net.
3. Evidence and a like-for-like comparison, a quantified difference with a likely cause, and a constructive next step – no blame.
''')}
"""))

L.append(lesson(35, M, "Investigating: trends, anomalies and root cause", "Advanced", ["Metrics", "Stakeholders"], f"""
## Objectives
- Apply a repeatable investigation method.
- Decompose a change by dimension (where), driver (why) and entity (who).
- Find the root cause of the April 2026 time-deposit drop in the sample bank.

## The method
1. **Validate first:** is the data complete and the definition the same as last month? (Rule out data issues before business stories.)
2. **Size it:** how big vs normal variation?
3. **Decompose:** by product → region → segment → customer. Follow the biggest contributor at each level.
4. **Concentration check:** is it a few large accounts or many small ones?
5. **Driver:** balances vs rates vs counts (opened/closed accounts).
6. **Corroborate:** talk to the business (RM, branch, product) – data tells you where, people tell you why.
7. **Conclude:** finding, evidence, impact, recommendation, owner.

## Hands-on (18 min): the April time-deposit drop
Step 1 – where? Product and region:
{sql('''
SELECT a.product_code, c.region,
       ROUND(SUM(CASE WHEN m.month = '2026-03' THEN m.eop_balance ELSE 0 END)/1e6, 1) AS mar_m,
       ROUND(SUM(CASE WHEN m.month = '2026-04' THEN m.eop_balance ELSE 0 END)/1e6, 1) AS apr_m,
       ROUND(SUM(CASE WHEN m.month = '2026-04' THEN m.eop_balance ELSE 0 END - CASE WHEN m.month = '2026-03' THEN m.eop_balance ELSE 0 END)/1e6, 1) AS change_m
FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code) JOIN customers c USING (customer_id)
WHERE p.balance_side = 'liability' AND m.month IN ('2026-03','2026-04')
GROUP BY a.product_code, c.region ORDER BY change_m ASC LIMIT 5;
''')}
Step 2 – who? Accounts behind it:
{sql('''
SELECT a.account_id, c.customer_name, c.segment, a.product_code,
       ROUND(SUM(CASE WHEN m.month = '2026-03' THEN m.eop_balance ELSE 0 END)/1e6, 1) AS mar_m,
       ROUND(SUM(CASE WHEN m.month = '2026-04' THEN m.eop_balance ELSE 0 END)/1e6, 1) AS apr_m
FROM monthly_account m JOIN accounts a USING (account_id) JOIN customers c USING (customer_id)
WHERE c.region = 'Visayas' AND a.product_code IN ('TD','CTD') AND m.month IN ('2026-03','2026-04')
GROUP BY a.account_id ORDER BY (apr_m - mar_m) ASC LIMIT 5;
''')}
Step 3 – write it up: "Time deposits fell ₱__M in April even though total deposits still grew. ₱__M (__%) of the drop came from __ time deposits in Visayas held by __ customers that matured and were not rolled over (accounts later closed). Excluding them, time deposits grew __%. Recommend: RM call to understand where funds went (rate competition?), and a TD maturity early-warning list for large depositors."

## Review questions
1. Why validate the data before investigating the business?
2. What is a concentration check and why does it matter in banking data?
3. Data says where; who tells you why?

{answers('''
1. Many "anomalies" are late feeds, definition changes or duplicates; chasing a fake business story wastes time and credibility.
2. Checking whether a change is driven by a few large accounts; bank balances are highly concentrated (corporates, affluent), so a handful of accounts can move totals.
3. The business: relationship managers, branch staff, product owners – and sometimes the customers.
''')}
"""))

L.append(lesson(36, M, "Communicating findings to management", "Advanced", ["Stakeholders"], f"""
## Objectives
- Write an executive summary using the pyramid principle.
- Design a one-page Power BI management view.
- Pass the Module 7 check.

## The pyramid
1. **Answer first** (the "so what").
2. **3 supporting points** with numbers.
3. **Evidence** in an appendix or drill-through.

{illustrative('''
**Subject: September personal loan performance**
Personal loan profit is under pressure from credit losses concentrated in one cohort. Loans booked through digital onboarding in Jul–Dec 2025 show 30+ delinquency several times higher than other cohorts; they drive most of the ECL increase since March. Recommend: tighten digital underwriting cut-offs, review the scorecard with Risk, and track first-payment default weekly. Owner: Consumer Lending + Credit Risk.
''')}

## Power BI one-pager (management view)
- Top row: 4–6 KPI cards with vs-last-month and vs-budget (Net income, NII, NIM, CIR, NPL ratio, CASA ratio).
- Middle: one trend (12 months) and one driver chart (waterfall: last month → this month by driver).
- Bottom: top movers table (segments/products with largest change) with drill-through to detail.
- Rules: certified measures only, as-of date and definitions visible, no more than ~8 visuals, consistent colours (good/bad).

## Hands-on (8 min)
Write a 4-sentence executive summary of the April time-deposit drop from Lesson 35 using the pyramid. Then list the 4 KPI cards you would put on a deposits management page.

## Module 7 check (7 min)
1. Name the three things Finance will check first in any profitability report.
2. Give the 5-step script for challenging a number.
3. What is the first step of any investigation?
4. Rewrite "Time deposits decreased due to various factors" into a useful finding sentence (use the Lesson 35 result).
5. What belongs on a management one-pager and what doesn't?

{answers('''
1. Reconciliation to GL, definitions (balance type, scope), and period/as-of date.
2. Acknowledge → compare like-for-like → quantify → hypothesise → propose a fix.
3. Validate the data (completeness, definition, timing).
4. E.g., "Time deposits fell about ₱39M (−2%) in April because three large Visayas time deposits (one corporate, two affluent; about ₱65M in March) matured and were not rolled over; excluding them, time deposits grew, and total deposits still rose on CASA growth."
5. Certified KPIs, trend, drivers, top movers, as-of date and definitions. Not: raw tables, uncertified metrics, dozens of visuals, unexplained jargon.
''')}
"""))
