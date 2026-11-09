from common import *

M = "8 · Case studies and capstone"
L = []

L.append(lesson(37, M, "Case: Consumer Banking segment profitability review", "Advanced", ["Metrics", "Stakeholders"], f"""
## The brief
The Head of Consumer Banking asks: *"Which customer segments make us money after costs, and where should we focus next year?"* You have 30 minutes to produce the core numbers and a 3-line answer.

## Step 1 (10 min): CM1 by segment, with balances and customers
{sql('''
WITH cust AS (
  SELECT a.customer_id,
         SUM(m.interest_income - m.ftp_charge + m.ftp_credit - m.interest_expense + m.fee_income) AS cm1,
         SUM(m.avg_balance) / 9.0 AS adb
  FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code)
  WHERE m.month BETWEEN '2026-01' AND '2026-09' AND p.business_unit = 'Consumer Banking'
  GROUP BY a.customer_id)
SELECT c.segment, COUNT(*) AS customers, ROUND(SUM(cu.cm1)/1e6, 2) AS cm1_m,
       ROUND(AVG(cu.cm1), 0) AS cm1_per_customer
FROM cust cu JOIN customers c USING (customer_id)
WHERE c.segment IN ('Mass','Mass Affluent','Affluent')
GROUP BY c.segment ORDER BY cm1_m DESC;
''')}

## Step 2 (8 min): cost to serve and credit cost
Add cost-to-serve from `channel_txn` × `channel_costs` (Lesson 20) for the same customers and months, and the change in ECL allowance (Lesson 14) as a credit-cost proxy. Compute **CM after cost-to-serve and credit cost per customer** by segment.

## Step 3 (7 min): answer the question
Fill in: "Mass Affluent generates __% of Consumer CM with __% of customers. Mass customers are __ (profitable / marginal / loss-making) after cost to serve, mainly because __. Next year: focus on __ (e.g., moving Mass to digital servicing, deepening Mass Affluent with cards/TDs) and watch __ (credit cost in personal loans)."

## Step 4 (5 min): self-review
- Did you state the period and balance type?
- Did you exclude Business/Corporate products on purpose and say so?
- Would Finance be able to reconcile your total?
"""))

L.append(lesson(38, M, "Case: Personal loan quality and the provisions question", "Advanced", ["Metrics", "Regulation"], f"""
## The brief
Echoing BPI's real 2026 pattern (provisions up 69.2% in 9M 2026 while NII grew 11% – {SRC['bpi_9m26']}), the CFO of the sample bank asks: *"Why are personal-loan provisions rising, and is the product still worth growing?"* The sample bank is illustrative; the BPI figures are public and only provide context.

## Step 1 (8 min): ECL trend and NPL ratio for PL
{sql('''
SELECT m.month, COUNT(*) AS loans, ROUND(SUM(m.eop_balance)/1e6, 2) AS bal_m,
       ROUND(SUM(m.ecl_allowance)/1e6, 3) AS ecl_m,
       ROUND(100.0 * SUM(m.ecl_allowance) / SUM(m.eop_balance), 2) AS ecl_pct_of_bal,
       ROUND(100.0 * SUM(CASE WHEN m.dpd_bucket = '90+' THEN m.eop_balance ELSE 0 END) / SUM(m.eop_balance), 2) AS npl_pct
FROM monthly_account m JOIN accounts a USING (account_id)
WHERE a.product_code = 'PL' GROUP BY m.month ORDER BY m.month;
''')}

## Step 2 (8 min): isolate the driver
Reuse Lesson 22's vintage × channel query. Then compute the share of September ECL that sits in the 2025 H2 digital cohort.

## Step 3 (8 min): is it still worth growing? (risk-adjusted)
For PL, Jan–Sep 2026: NII after FTP + fees (Lesson 16), minus the ECL increase over the period, minus an assumed ₱150 per account-month servicing cost. Compute an annualised RAROC with capital = 12% × average balance (100% risk weight). Compare with a 13% hurdle. Then recompute excluding the bad cohort.

## Step 4 (6 min): recommendation
Three sentences for the CFO: what is happening, how big, what to do (e.g., keep growing through branch/existing-customer channels, fix digital underwriting, add early-warning tracking).
"""))

L.append(lesson(39, M, "Case: Channel migration business case", "Advanced", ["Metrics", "Business"], f"""
## The brief
The Head of Operations wants to close or reformat two low-traffic branches and push Mass customers to mobile. You must quantify the opportunity and the risks.

## Step 1 (8 min): branch traffic and cost
{sql('''
SELECT b.branch_code, b.region, b.monthly_opex_php,
       SUM(t.txn_count) AS branch_txns_sep,
       ROUND(1.0 * b.monthly_opex_php / SUM(t.txn_count), 0) AS cost_per_branch_txn
FROM channel_txn t JOIN customers c USING (customer_id) JOIN branches b ON b.branch_code = c.home_branch
WHERE t.month = '2026-09' AND t.channel = 'Branch'
GROUP BY b.branch_code ORDER BY cost_per_branch_txn DESC LIMIT 5;
''')}

## Step 2 (8 min): what is at stake
For the two most expensive branches per transaction: how many customers, how much in deposits (Sep 2026 EOP) and CM1 (Jan–Sep) do they hold? Which segments? Are they already digital (digital share)?

## Step 3 (8 min): the business case
- Savings: branch opex avoided (assume 70% of opex saved after 12 months) minus extra mobile/agency transaction cost.
- Risk: deposit attrition. Scenario: 5%, 10% and 20% of those branches' deposits leave. Value the lost deposit spread using FTP (Lesson 16).
- Break-even attrition: at what % attrition do savings equal lost CM1?

## Step 4 (6 min): recommendation
Write 4 sentences: options (close / reformat to a smaller digital-assisted branch / partner agency), the numbers, the break-even, and what you would monitor after the change.
"""))

L.append(lesson(40, M, "Capstone: monthly performance pack, final assessment and keeping it sharp", "Advanced", ["Metrics", "Data", "Stakeholders"], f"""
## Part A (12 min): the monthly performance pack
Produce the September 2026 pack for the sample bank, one line per item with the number and a one-sentence comment:
1. Net interest income (incl. treasury) and NIM vs August.
2. Fee income and CIR.
3. Deposits, CASA ratio, cost of deposits.
4. Loans, NPL ratio, ECL allowance change.
5. Top 3 movers (product or segment) in CM1 vs August.
6. Data quality status: GL reconciliation result and DQ scorecard (Lessons 29, 31).
Then write a 4-line executive summary (Lesson 36).

## Part B (10 min): final assessment
Answer without notes, then check against the lessons.
1. Walk down the bank P&L from interest income to net income.
2. BPI FY2025 NIM, CIR, ROE and NPL ratio (with source).
3. Explain FTP and why a 0.25% savings account can be very profitable.
4. Write the formulas for NIM, CIR, ROA, ROE, credit cost, RAROC, CLV.
5. CM1 vs CM2 vs CM3 – which one for a "drop the product?" decision, and why?
6. Name five source systems and what each is the system of record for.
7. Two reports disagree on deposits. List five likely causes.
8. Define SSOT and the role of owner, steward and custodian.
9. Give the investigation method in 7 steps.
10. One sentence on how your CEDA work supports each of: Finance, Risk, Retail, senior management.

## Part C (5 min): keep it sharp after the course
- **Weekly (15 min, Fridays):** re-answer the review questions of one module, rotating 1→8.
- **Quarterly:** when BPI publishes results, update your notes with NII, NIM, CIR, ROE, NPL, CASA and explain each change in one line (practise Lesson 15's driver tree on real numbers).
- **Monthly at work:** pick one report you publish and write its metric definitions using the Lesson 30 template.
- **Glossary:** add every new term you meet at work to the Notion glossary with its formula and limitation.

## Part D (3 min): reflect
Rate your confidence 1–5 on each module in the lesson database. Anything ≤ 3 goes into the weekly review rotation first.
"""))
