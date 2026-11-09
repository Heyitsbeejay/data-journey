from common import *

M = "5 · Risk and regulation"
L = []

L.append(lesson(22, M, "Credit risk analytics: PD, LGD, EAD, vintages and roll rates", "Advanced", ["Metrics", "Regulation"], f"""
## Objectives
- Define PD, LGD and EAD and how they combine into expected loss.
- Build a vintage (cohort) delinquency view.
- Read a roll-rate (transition) table.

## In plain words
**PD** = probability the borrower defaults in a period. **LGD** = share of the exposure lost if they default (after collateral and recoveries). **EAD** = amount owed at default (for cards, includes likely further drawdowns). **Vintage analysis** groups loans by the month/quarter they were booked and tracks each cohort's delinquency by months-on-book. It removes the denominator effect from Lesson 7. **Roll rates** show how balances move between DPD buckets month to month.

## Terms to know
{terms([
 ("Vintage / cohort", "Loans booked in the same period."),
 ("MOB (months on book)", "Age of the loan in months."),
 ("Roll rate", "% of balance in bucket X this month that is in bucket X+1 next month."),
 ("Cure rate", "% of delinquent balance that returns to current."),
 ("Early warning indicator", "A signal (e.g., first-payment default) that a cohort is worse than usual."),
])}

## Hands-on (15 min): find the bad cohort
{sql('''
-- Personal loans: 30+ delinquency by booking half-year and onboarding channel, Sep 2026
SELECT CASE WHEN a.open_date < '2025-01-01' THEN 'Before 2025'
            WHEN a.open_date < '2025-07-01' THEN '2025 H1'
            WHEN a.open_date < '2026-01-01' THEN '2025 H2' ELSE '2026' END AS vintage,
       c.onboard_channel,
       COUNT(*) AS loans,
       ROUND(100.0 * SUM(CASE WHEN m.dpd_bucket IN ('31-60','61-90','90+') THEN 1 ELSE 0 END) / COUNT(*), 1) AS dq30_pct
FROM monthly_account m JOIN accounts a USING (account_id) JOIN customers c USING (customer_id)
WHERE a.product_code = 'PL' AND m.month = '2026-09'
GROUP BY vintage, c.onboard_channel ORDER BY vintage, c.onboard_channel;
''')}
{sql('''
-- Roll-rate matrix for personal loans: bucket last month -> bucket this month (Apr–Sep 2026)
SELECT prev.dpd_bucket AS from_bucket, cur.dpd_bucket AS to_bucket, COUNT(*) AS n
FROM monthly_account cur
JOIN monthly_account prev ON prev.account_id = cur.account_id
 AND prev.month = strftime('%Y-%m', date(cur.month || '-01', '-1 month'))
JOIN accounts a ON a.account_id = cur.account_id
WHERE a.product_code = 'PL' AND cur.month BETWEEN '2026-04' AND '2026-09'
GROUP BY 1, 2 ORDER BY 1, 2;
''')}
Which vintage and channel is the problem? Write the one-line finding as you would for Risk.

## Review questions
1. Why is vintage analysis better than a portfolio delinquency rate for judging new underwriting?
2. A roll rate from 1–30 to 31–60 jumps from 20% to 35%. What does it signal?
3. Give one data-quality issue that would break a vintage report.

{answers('''
1. It compares cohorts at the same age, so fast growth doesn't hide deterioration.
2. Fewer early-stage delinquents are curing; collections effectiveness or borrower stress is worsening; provisions will follow.
3. Wrong or overwritten open dates (e.g., restructured loans getting a new open date), missing onboarding channel, or accounts re-numbered on migration.
''')}
"""))

L.append(lesson(23, M, "Liquidity and capital: CAR, CET1, LCR, NSFR and reserves", "Advanced", ["Regulation", "Metrics"], f"""
## Objectives
- Explain capital adequacy (Basel III as applied by BSP) and risk-weighted assets.
- Explain LCR and NSFR in plain words.
- Connect these ratios to analyst work (RWA data, deposit run-off assumptions).

## In plain words
**Capital** absorbs losses. Regulators require capital in proportion to **risk-weighted assets (RWA)**: a government bond has a low risk weight, an unsecured loan a high one. **CAR = total qualifying capital ÷ RWA**; **CET1 ratio** uses the highest-quality capital only. **Liquidity** rules make sure a bank survives a run: **LCR** = high-quality liquid assets ÷ net cash outflows over a 30-day stress; **NSFR** = available stable funding ÷ required stable funding over one year. The **reserve requirement** is cash held at the BSP against deposits.

## Terms to know
{terms([
 ("RWA", "Assets weighted by riskiness (credit, market and operational risk)."),
 ("CET1", "Common equity tier 1: common shares + retained earnings, minus deductions."),
 ("HQLA", "High-quality liquid assets: cash, reserves, government securities."),
 ("Run-off rate", "Assumed share of a deposit type that leaves in stress (retail stable deposits lower, corporate higher)."),
 ("Buffers", "Capital conservation buffer, countercyclical buffer, D-SIB surcharge on top of minimums."),
])}

{verified(f'''
- BPI end-2025: CET1 ratio **13.9%** (indicative), CAR **14.7%**. Source: {SRC['bpi_fy25']}
- Reserve requirement for universal/commercial banks cut to **5%** effective late March 2025. Source: {SRC['rrr']}
''')}

{tip(f'''
**Not re-verified for this lesson (check before quoting):** BSP's Basel III rules are commonly summarised as minimum CAR 10% and CET1 6% plus a 2.5% capital conservation buffer, with LCR and NSFR of at least 100%, and D-SIB surcharges for systemically important banks. Confirm current figures in the MORB on {SRC['bsp']}.
''')}

## Why an analyst cares
- RWA by product drives capital allocation in RAROC (Lesson 21).
- LCR depends on deposit classification (retail vs corporate, insured vs not, operational vs non-operational). Wrong customer-type tagging in data changes the bank's reported liquidity.
- Treasury will ask for deposit behaviour (stickiness, concentration of top depositors) to calibrate run-off assumptions.

## Hands-on (12 min)
{sql('''
-- Deposit concentration: share of total deposits held by the top 20 depositors (Sep 2026)
WITH d AS (
  SELECT a.customer_id, SUM(m.eop_balance) AS bal
  FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code)
  WHERE m.month = '2026-09' AND p.balance_side = 'liability'
  GROUP BY a.customer_id)
SELECT ROUND(100.0 * (SELECT SUM(bal) FROM (SELECT bal FROM d ORDER BY bal DESC LIMIT 20)) / SUM(bal), 1) AS top20_share_pct,
       ROUND(100.0 * SUM(CASE WHEN bal <= 1000000 THEN bal ELSE 1000000 END) / SUM(bal), 1) AS approx_insured_share_pct
FROM d;
''')}
Note: "insured share" here caps each customer at ₱1M, a simplification (PDIC coverage is per depositor per bank, with rules on joint and business accounts). Why does a high top-20 share worry Treasury?

## Review questions
1. Why do two banks with the same assets need different capital?
2. In plain words, what does an LCR of 180% mean?
3. Which data attribute errors can change LCR?

{answers('''
1. Their assets have different risk weights (e.g., government bonds vs unsecured loans), so RWA differs.
2. The bank holds 1.8× the liquid assets needed to cover its stressed 30-day net outflows.
3. Customer type (retail/corporate/financial institution), insured vs uninsured, operational account flags, maturity dates, and HQLA classification of securities.
''')}
"""))

L.append(lesson(24, M, "Compliance: AML/KYC, data privacy and consumer protection", "Intermediate", ["Regulation", "Data"], f"""
## Objectives
- Explain KYC/CDD and AML monitoring and the data they need.
- Know the main Philippine laws: AMLA, Data Privacy Act, Financial Products and Services Consumer Protection Act.
- Apply privacy rules to analytics work (minimisation, masking, purpose).

## In plain words
Banks must know who their customers are (**KYC / customer due diligence**), monitor transactions for money laundering and terrorist financing, and report suspicious and covered transactions to the **Anti-Money Laundering Council (AMLC)**. They must protect personal data under the **Data Privacy Act of 2012 (RA 10173)**, overseen by the National Privacy Commission, and treat customers fairly under the **Financial Products and Services Consumer Protection Act (RA 11765)**, which BSP enforces for its supervised institutions.

## Terms to know
{terms([
 ("AMLA", "Anti-Money Laundering Act of 2001 (RA 9160), as amended."),
 ("CDD / EDD", "Customer due diligence; enhanced due diligence for higher-risk customers (e.g., PEPs)."),
 ("PEP", "Politically exposed person."),
 ("STR / CTR", "Suspicious transaction report / covered transaction report filed with AMLC."),
 ("Data minimisation", "Use only the personal data you need for the purpose."),
 ("Pseudonymisation / masking", "Replacing identifiers so analysts can work without seeing personal data."),
])}

{tip(f'''
These are laws and regulator frameworks; details change through amendments and circulars. Check the AMLC, NPC and BSP sites ({SRC['bsp']}) for current thresholds and rules before quoting them in a report.
''')}

## Why an analyst cares
- KYC completeness and risk-rating fields are data products Compliance consumes; missing or stale values are compliance findings.
- Your reports must not expose personal data beyond the need: aggregate, mask names/account numbers, restrict row-level access.
- A data request "send me all customers with balances above X with names" should trigger a purpose and access check.

## Hands-on (12 min)
{sql('''
-- KYC-style completeness check on the sample customer master
SELECT segment,
       COUNT(*) AS customers,
       SUM(CASE WHEN birth_year = '' OR birth_year IS NULL THEN 1 ELSE 0 END) AS missing_birth_year,
       SUM(CASE WHEN cif_no IS NULL OR LENGTH(cif_no) <> 10 THEN 1 ELSE 0 END) AS bad_cif
FROM customers GROUP BY segment;
''')}
Missing birth year for SME/Corporate is expected (they are companies). What field should a business customer have instead? Write a rule that only flags *individuals* without a birth year.

Privacy exercise: rewrite the query in Lesson 9 (top corporate relationships) so it shows a masked name (first 3 letters + "***") instead of the full name.

## Review questions
1. Why does a data quality issue in KYC fields become a compliance issue?
2. A marketing analyst wants customer-level data with names for a campaign model. What do you check first?
3. What is the difference between CDD and EDD?

{answers('''
1. Regulations require complete and current customer information; gaps mean the bank can't evidence due diligence or risk-rate customers.
2. Purpose and lawful basis/consent, whether names are needed at all (use IDs), access approvals, and secure handling.
3. CDD is standard identification and verification; EDD adds deeper checks (source of funds, senior approval, more monitoring) for high-risk customers.
''')}
"""))

L.append(lesson(25, M, "Market, interest-rate and operational risk basics", "Intermediate", ["Regulation"], f"""
## Objectives
- Explain interest-rate risk in the banking book (IRRBB): repricing gaps, NII sensitivity.
- Explain market risk in trading (FX, bonds) and operational risk.
- Pass the Module 5 check.

## In plain words
- **Interest-rate risk (banking book):** if loans reprice slower than deposits (or vice versa), a rate move changes NII. Banks measure **repricing gaps** and **NII sensitivity** (e.g., NII impact of +/−100 bps).
- **Market risk:** losses on trading positions from price moves (bonds, FX). Measured with sensitivities and value-at-risk.
- **Operational risk:** losses from failed processes, people, systems or external events (fraud, outages, errors). Data errors in regulatory reports are operational risk too.

{illustrative('''
Repricing gap, next 12 months: assets repricing ₱1.2B, liabilities repricing ₱1.6B → gap −₱0.4B. If rates rise 100 bps, NII falls by about ₱0.4B × 1% = ₱4M over the year (liabilities cost more before assets earn more). If rates fall, NII rises by about the same.
''')}

## Hands-on (10 min)
Classify the sample products as "reprices within 12 months" or "later": SA/CA/BCA (administered rates, treat as reprices quickly but only partially), TD/CTD (at maturity, mostly < 12 months), CC/PL (fixed for term), HL/AL (fixed periods of years), SBL/CL (often floating). Use Sep 2026 balances to estimate a rough gap.
{sql('''
SELECT a.product_code, ROUND(SUM(m.eop_balance)/1e6, 1) AS bal_m
FROM monthly_account m JOIN accounts a USING (account_id)
WHERE m.month = '2026-09' GROUP BY a.product_code ORDER BY bal_m DESC;
''')}

## Module 5 check (8 min)
1. Define PD, LGD, EAD and write the EL formula.
2. What is a vintage curve and what does it fix?
3. What does CET1 measure and why is BPI's 13.9% meaningful?
4. Name two laws an analyst must respect when using customer data.
5. Your bank has a negative 12-month repricing gap. What happens to NII if rates rise?

{answers('''
1. PD probability of default, LGD loss given default, EAD exposure at default; EL = PD × LGD × EAD.
2. Delinquency by months on book per booking cohort; it fixes the denominator effect and shows whether new underwriting is worse.
3. Highest-quality capital as % of RWA; 13.9% is well above BSP minimum + buffers, leaving room to grow lending or absorb losses.
4. Data Privacy Act (RA 10173), AMLA (RA 9160 as amended); also RA 11765 for consumer protection.
5. NII falls in the short term because more liabilities than assets reprice upward.
''')}
"""))
