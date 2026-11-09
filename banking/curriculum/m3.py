from common import *

M = "3 · Financial performance metrics"
L = []

L.append(lesson(11, M, "Interest income, interest expense, NII and average balances", "Intermediate", ["Metrics"], f"""
## Objectives
- Compute NII from account-level data.
- Explain ADB vs EOP and accrual vs cash.
- Annualise monthly figures correctly.

## In plain words
Interest is earned **daily** on whatever balance is outstanding that day and is **accrued** (recorded as earned) even before cash is received. So: interest ≈ average balance × rate × days/365. That is why profitability reporting uses average balances.

## Terms to know
{terms([
 ("Accrual", "Recording income/expense when earned or incurred, not when cash moves."),
 ("Day-count convention", "How days are counted (actual/365, 30/360…). Small differences show up in reconciliations."),
 ("Annualise", "Scale a period figure to a year: monthly × 12, or × 365/days for exactness."),
 ("Earning assets", "Assets that earn interest: loans, securities, interbank placements."),
])}

## Formula, meaning and limitations
**NII = interest income − interest expense**
- *Meaning:* the bank's earnings from the spread business.
- *Interpretation:* change = volume effect + rate effect + mix effect (+ day-count: February has fewer days!).
- *Limitations:* NII alone ignores how much capital and risk it took to earn it, and the fees and costs of the same products.

{illustrative('''
An account starts the month at ₱100,000 and receives ₱300,000 on day 25 (30-day month). EOP = ₱400,000. ADB = (100,000×24 + 400,000×6) ÷ 30 = ₱160,000. At 4% a year, interest ≈ 160,000 × 4% × 30/365 = ₱526. Using EOP would overstate it at ₱1,315.
''')}

## In your reports
Columns you will see: `adb`, `eop_bal`, `int_inc_mtd`, `int_inc_ytd`, `accrued_int`. Always check whether a figure is MTD, QTD or YTD before annualising.

## Hands-on (12 min)
{sql('''
-- NII by business unit, annualised, Jan–Sep 2026 (customer-level spread only; treasury book excluded)
SELECT p.business_unit,
       ROUND(SUM(m.interest_income)/1e6, 2) AS int_income_m,
       ROUND(SUM(m.interest_expense)/1e6, 2) AS int_expense_m,
       ROUND(SUM(m.interest_income - m.interest_expense)/1e6, 2) AS nii_m,
       ROUND(SUM(m.interest_income - m.interest_expense) * 12.0 / 9 / 1e6, 2) AS nii_annualised_m
FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code)
WHERE m.month BETWEEN '2026-01' AND '2026-09'
GROUP BY p.business_unit;
''')}
Notice that Consumer Banking, which gathers most of the bank's deposits, shows tiny NII while Corporate Banking looks like the star. Why is that misleading, and what fixes it? (Answer: FTP. In Lesson 16 you will see the ranking flip.)

## Review questions
1. Why is ADB better than EOP for profitability?
2. NII fell 3% in February vs January with no balance or rate change. Why?
3. YTD NII after 9 months is ₱90M. What is the annualised figure?

{answers('''
1. Interest accrues on daily balances; ADB reflects the balance actually earning or costing interest during the period.
2. February has 28 days vs 31 (≈ −9.7% days); in an actual-day accrual NII falls even if nothing else changed. (In the sample data accruals are monthly, so you won't see this effect there.)
3. 90 × 12/9 = ₱120M.
''')}
"""))

L.append(lesson(12, M, "NIM, yields, cost of funds and rate/volume analysis", "Intermediate", ["Metrics"], f"""
## Objectives
- Calculate NIM, asset yield, cost of funds and spread.
- Explain what moves NIM.
- Split a change in NII into rate and volume effects.

## Formulas, meaning and limitations
- **NIM = annualised NII ÷ average earning assets.** The margin earned on every peso of earning assets.
- **Asset yield = annualised interest income ÷ average earning assets.**
- **Cost of funds = annualised interest expense ÷ average interest-bearing liabilities.**
- **Spread = asset yield − cost of funds.**

*Interpretation:* NIM widens when asset yields rise faster than funding costs (e.g., shift toward higher-yield consumer loans, or more CASA). It compresses after rate cuts if loans reprice faster than deposits.
*Limitations:* NIM ignores credit risk (high-yield loans also lose more) and fee income; comparing NIMs across banks needs the same denominator definition.

{verified(f'''BPI FY2025 NIM **4.6%**, up 28 bps, with NII +16.0%; 9M 2026 NIM **4.6%**. 4Q25 risk-adjusted cost of funds **2.37%**. Sources: {SRC['bpi_fy25']}; {SRC['bpi_deck']}; {SRC['bpi_9m26']}''')}

## Rate/volume analysis
ΔNII from one product = **volume effect** (Δbalance × old rate) + **rate effect** (Δrate × new balance).

{illustrative('''
Personal loans: last year ADB ₱1.0B at 22% → ₱220M. This year ADB ₱1.3B at 21% → ₱273M. ΔII = +₱53M.
Volume effect = 0.3B × 22% = +₱66M. Rate effect = −1% × 1.3B = −₱13M. Check: 66 − 13 = 53. ✓
Story: growth drove income; pricing pressure took some back.
''')}

## Hands-on (12 min)
{sql('''
-- Simple bank NIM by quarter: loans + treasury securities as earning assets
WITH q AS (
  SELECT CASE WHEN month <= '2025-12' THEN '2025Q4' WHEN month <= '2026-03' THEN '2026Q1'
              WHEN month <= '2026-06' THEN '2026Q2' ELSE '2026Q3' END AS qtr, month FROM gl_monthly GROUP BY month),
loans AS (
  SELECT m.month, SUM(m.avg_balance) AS loan_adb, SUM(m.interest_income) AS ii, 0 AS ie
  FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code)
  WHERE p.balance_side = 'asset' GROUP BY m.month),
deps AS (
  SELECT m.month, SUM(m.interest_expense) AS ie
  FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code)
  WHERE p.balance_side = 'liability' GROUP BY m.month)
SELECT q.qtr,
       ROUND(100.0 * 4 * SUM(l.ii + t.interest_income - d.ie) / (SUM(l.loan_adb + t.avg_securities_balance) / 3), 2) AS nim_pct,
       ROUND(100.0 * 4 * SUM(l.ii + t.interest_income) / (SUM(l.loan_adb + t.avg_securities_balance) / 3), 2) AS asset_yield_pct
FROM q JOIN loans l USING (month) JOIN deps d USING (month) JOIN treasury_monthly t USING (month)
GROUP BY q.qtr ORDER BY q.qtr;
''')}
Power BI: write the measure `NIM % = DIVIDE([NII] * 12 / [Months in Context], [Avg Earning Assets])`. Why must the annualisation factor depend on the filter context?

## Review questions
1. Two banks: A has NIM 4.6%, B has 3.2%. Is A necessarily more profitable?
2. BSP cuts rates by 50 bps. Which bank's NIM falls more: one with mostly floating-rate corporate loans and TDs, or one with fixed-rate housing loans and CASA?
3. Do the rate/volume split for: last year ₱500M at 6%, this year ₱600M at 5.5%.

{answers('''
1. No. A may take more credit risk (higher provisions), have higher costs, or hold more capital.
2. The first bank (floating-rate loans, TD funding): its loan yields fall immediately while TD costs only fall as deposits mature. The second bank's fixed-rate loans don't reprice yet and its CASA costs barely move, so its NIM changes little in the short run (it feels the cut later as loans reprice).
3. Old income ₱30M, new ₱33M, Δ +₱3M. Volume = 100M × 6% = +₱6M. Rate = −0.5% × 600M = −₱3M.
''')}
"""))

L.append(lesson(13, M, "Non-interest income, operating expenses and cost-to-income", "Intermediate", ["Metrics"], f"""
## Objectives
- Classify non-interest income lines.
- Classify operating expenses (people, premises, technology, other).
- Calculate and interpret the cost-to-income ratio (CIR) and jaws.

## Formulas, meaning and limitations
- **Cost-to-income ratio = operating expenses ÷ total operating income (NII + non-interest income).** Lower = more efficient.
- **Jaws = revenue growth % − expense growth %.** Positive jaws = efficiency improving.

*Limitations:* CIR improves when revenue spikes (e.g., rate cycle) even if nothing about efficiency changed. It excludes provisions, so a bank lending to riskier borrowers can show a great CIR and still earn less. One-off items (trading gains, asset sales, restructuring costs) distort it.

{verified(f'''BPI FY2025: opex **₱92.1B** (+9.9%), revenue **₱195.3B** (+14.8%), **CIR 47.2%** (down 209 bps). Jaws ≈ 14.8 − 9.9 = **+4.9 pts** (my arithmetic). 9M 2026 CIR **47.1%** vs 46% a year earlier. Sources: {SRC['bpi_fy25']}; {SRC['bpi_9m26']}''')}

## Terms to know
{terms([
 ("Fee and commission income", "Service charges, card fees, trust fees, remittance fees."),
 ("Trading / securities gains", "Profit from selling bonds or FX trading; volatile."),
 ("Recurring vs non-recurring", "Separate one-offs to see the underlying trend."),
 ("Fixed vs variable cost", "Branch rent is fixed; card processing per transaction is variable."),
])}

## Hands-on (12 min)
{sql('''
-- Sample bank cost-to-income by month (GL revenue, opex table)
WITH rev AS (
  SELECT month,
         SUM(CASE WHEN gl_code IN ('410000','411000','420000') THEN amount WHEN gl_code = '510000' THEN -amount ELSE 0 END) AS revenue
  FROM gl_monthly GROUP BY month),
ox AS (SELECT month, SUM(amount_php) AS opex FROM opex_monthly GROUP BY month)
SELECT month, ROUND(revenue/1e6, 2) AS revenue_m, ROUND(opex/1e6, 2) AS opex_m,
       ROUND(100.0 * opex / revenue, 1) AS cir_pct
FROM rev JOIN ox USING (month) ORDER BY month;
''')}
The sample bank's CIR (55–60%) is well above BPI's 47%. Name two structural reasons a smaller bank has a higher CIR. One month also looks odd – which, and why? (Hint: compare with Lesson 29.)

## Review questions
1. CIR improved from 52% to 48%. Give one "good" and one "not really good" explanation.
2. Revenue +8%, opex +11%. Are the jaws positive or negative?
3. Why are provisions excluded from CIR?

{answers('''
1. Good: digital migration cut cost per transaction. Not really: a rate cycle temporarily inflated NII, or a one-off gain boosted revenue.
2. Negative (−3 pts): costs growing faster than revenue.
3. CIR measures operating efficiency; credit cost is a separate risk outcome tracked with credit cost and NPL ratios.
''')}
"""))

L.append(lesson(14, M, "Asset quality: NPLs, provisions and credit cost", "Intermediate", ["Metrics", "Regulation"], f"""
## Objectives
- Define NPL ratio, NPL coverage and credit cost.
- Explain expected credit loss (ECL) under PFRS 9 at a high level (stages 1–3).
- Connect provisions to net income using BPI's 2026 results.

## In plain words
Not every loan gets repaid. Under **PFRS 9** (the Philippine adoption of IFRS 9), banks set aside an **allowance** for **expected credit losses**, not only losses that already happened. Loans move through **Stage 1** (performing, 12-month ECL), **Stage 2** (significant increase in credit risk, lifetime ECL) and **Stage 3** (credit-impaired, lifetime ECL). The P&L expense that builds the allowance is the **provision**.

## Formulas, meaning and limitations
- **NPL ratio = NPLs ÷ gross loans.** Share of the book that is non-performing.
- **NPL coverage = loss allowance ÷ NPLs.** How much of the bad book is already reserved.
- **Credit cost = annualised provisions ÷ average loans.** Credit losses as a "rate" you can compare with yield.

*Limitations:* NPL ratio lags (loans take months to reach 90+) and suffers the denominator effect; coverage can look fine if NPLs are collateralised; provisions include model changes and management overlays, not just defaults.

{verified(f'''
- BPI FY2025: NPL ratio **2.18%**, NPL coverage **94.9%** (122.9% under BSP Circular 941 definitions), provisions **₱17.8B**, up **168.9%**. Source: {SRC['bpi_fy25']}
- BPI 9M 2026: provisions **₱19.9B**, up **69.2%** from ₱11.8B; NPL ratio **2.50%** vs 2.3%; net income **₱48.9B**, **down 3.2%** even though NII grew 11% and loans grew 13.6%. Source: {SRC['bpi_9m26']}
''')}

{tip('''
Notice the two coverage numbers for BPI. Same bank, same date, different definitions (PFRS vs BSP Circular 941). This is the everyday reality of a Data Platforms team: always label which definition a metric follows.
''')}

## Hands-on (12 min)
{sql('''
-- Sample bank: NPL ratio (90+ DPD), allowance, and coverage by month
SELECT m.month,
       ROUND(SUM(m.eop_balance)/1e6, 1) AS gross_loans_m,
       ROUND(100.0 * SUM(CASE WHEN m.dpd_bucket = '90+' THEN m.eop_balance ELSE 0 END) / SUM(m.eop_balance), 2) AS npl_ratio_pct,
       ROUND(SUM(m.ecl_allowance)/1e6, 2) AS allowance_m,
       ROUND(100.0 * SUM(m.ecl_allowance) / NULLIF(SUM(CASE WHEN m.dpd_bucket = '90+' THEN m.eop_balance ELSE 0 END), 0), 0) AS coverage_pct
FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code)
WHERE p.balance_side = 'asset'
GROUP BY m.month ORDER BY m.month;
''')}
Early months show a blank or huge coverage figure because NPLs are close to zero: a ratio with a tiny denominator is meaningless, and a good report says so instead of showing 1,932%. Monthly provision expense ≈ change in allowance + write-offs. Compute the month-on-month change in `allowance_m`. In which month did it jump most?

## Review questions
1. Why can net income fall while NII grows (as at BPI in 9M 2026)?
2. A loan moves from Stage 1 to Stage 2 without missing a payment. What changes?
3. Coverage is 95% under one definition and 123% under another. What do you tell a stakeholder?

{answers('''
1. Provisions rose faster than revenue (₱19.9B vs ₱11.8B), absorbing the NII growth.
2. Its allowance switches from 12-month to lifetime expected loss, so the allowance (and provision expense) rises.
3. Both are right under their own definitions; name the definition, show both if needed, and explain the reconciling items.
''')}
"""))

L.append(lesson(15, M, "ROA, ROE and the bank DuPont tree", "Intermediate", ["Metrics"], f"""
## Objectives
- Calculate ROA and ROE and explain how leverage links them.
- Build a DuPont-style driver tree for a bank.
- Pass the Module 3 check with a BPI case.

## Formulas, meaning and limitations
- **ROA = net income ÷ average total assets.** How well the whole balance sheet earns.
- **ROE = net income ÷ average equity.** Return to shareholders.
- **ROE = ROA × (average assets ÷ average equity)** — the equity multiplier (leverage).

*Limitations:* ROE can be boosted by leverage (riskier); one-off gains distort both; ROA ignores off-balance-sheet businesses like wealth management.

## The driver tree
ROA ≈ (NII/Assets) + (Non-II/Assets) − (Opex/Assets) − (Provisions/Assets) − (Tax/Assets).
Every CEDA report that explains profitability is some branch of this tree.

{verified(f'''BPI FY2025: ROE **14.5%**, ROA **2.0%**, net income ₱66.62B, total equity ₱476.6B, total assets ₱3.7T. 9M 2026: ROE **13.6%** vs 15.0%. Sources: {SRC['bpi_fy25']}; {SRC['bpi_9m26']}''')}

Check: ROE ÷ ROA = 14.5 ÷ 2.0 ≈ 7.3× leverage, consistent with assets/equity ≈ 3.7T ÷ 0.48T ≈ 7.8× (end-period vs average balances explain the gap).

## Hands-on (10 min)
Fill in the tree for BPI FY2025 using ~₱3.5T as average assets (illustrative assumption; use the annual report average for the real figure):
| Line | ₱B | % of avg assets |
|---|---|---|
| NII | 148.0 | ? |
| Non-interest income | 47.2 | ? |
| Opex | (92.1) | ? |
| Provisions | (17.8) | ? |
| Net income | 66.6 | ? |

## Module 3 check (8 min): the BPI 9M 2026 case
Facts: NII +11%, NIM 4.6%, loans +13.6%, deposits +11%, fee income +15.5%, provisions +69.2%, CIR 47.1% (vs 46%), net income −3.2%, ROE 13.6% (vs 15%). Source: {SRC['bpi_9m26']}
1. Write a 3-sentence explanation of why profit fell for a senior manager.
2. Which metric would you add to the report to show whether the higher provisions are concentrated in specific products?
3. Draft one follow-up question you would ask Risk.

{answers('''
NII ≈ 4.2%, non-II ≈ 1.3%, opex ≈ −2.6%, provisions ≈ −0.5%; before tax ≈ 2.4%, after tax/other ≈ 1.9% ≈ reported 2.0%.
1. "Core revenue grew solidly: NII +11% on 13.6% loan growth with a stable 4.6% margin, and fees +15.5%. But provisions for credit losses rose 69% to ₱19.9B, and costs grew slightly faster than revenue, so net income fell 3.2% and ROE slipped to 13.6%. The question for management is whether the provisions reflect growth in higher-risk consumer lending (expected) or deterioration beyond plan."
2. Credit cost and NPL ratio by product/segment, ideally by vintage.
3. "How much of the provision increase is from Stage 1/2 growth on new loans versus Stage 3 migration on older loans, and which products drive it?"
''')}
"""))
