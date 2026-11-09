from common import *

M = "2 · Products and business lines"
L = []

L.append(lesson(6, M, "Deposits: CASA, time deposits and why funding mix matters", "Beginner", ["Business", "Metrics"], f"""
## Objectives
- Distinguish current, savings and time deposits, and their cost and stability.
- Calculate average daily balance (ADB), CASA ratio and cost of deposits.
- Explain why deposits can be profitable even though they pay interest.

## In plain words
Deposits are the bank's raw material. **CASA** (current and savings accounts) pays little or no interest and is used for daily transactions, so it is cheap and "sticky". **Time deposits (TDs)** pay more and are locked for a term (30 days to years), so they are expensive and can leave at maturity. A bank with lots of CASA has a cost advantage.

How can a deposit be profitable? Through **funds transfer pricing (FTP)**: Treasury "buys" the deposit from the deposit business at a market rate. If the bank pays the customer 0.25% and Treasury credits 4.00%, the deposit unit earns a 3.75% spread (Lesson 16).

## Terms to know
{terms([
 ("ADB (average daily balance)", "Sum of daily balances ÷ days in period."),
 ("CASA ratio", "(Current + savings) ÷ total deposits."),
 ("Cost of deposits", "Annualised interest expense on deposits ÷ average deposits."),
 ("Deposit run-off / attrition", "Balances or accounts leaving the bank."),
 ("Dormant account", "No customer-initiated transaction for a defined period (rules set by BSP and the bank)."),
 ("Rollover rate", "Share of maturing TDs that are renewed."),
])}

## Formula, meaning and limitations
**Cost of deposits = (interest expense on deposits × 12 / months in period) ÷ average deposits**
- *Meaning:* the average annual rate paid to depositors.
- *Interpretation:* rising cost with a stable policy rate often means mix shift toward TDs or promotional rates.
- *Limitations:* excludes non-interest costs of gathering deposits (branches, deposit insurance premiums), so a "cheap" CASA book can still be costly to serve.

{verified(f'''BPI end-2025: CASA **₱1.7T** of **₱2.8T** total deposits; CASA ratio **60.7%**. Source: {SRC['bpi_fy25']}''')}

## In your reports
Deposit dashboards usually show EOP and ADB balances, CASA ratio, number of accounts, new-to-bank vs existing, and cost of deposits, cut by product, segment, branch/region and channel.

## Hands-on (12 min)
{sql('''
-- CASA ratio and annualised cost of deposits by month
SELECT m.month,
       ROUND(SUM(m.eop_balance)/1e6, 1) AS deposits_m,
       ROUND(SUM(CASE WHEN a.product_code IN ('TD','CTD') THEN m.eop_balance END)/1e6, 1) AS time_deposits_m,
       ROUND(100.0 * SUM(CASE WHEN a.product_code IN ('SA','CA','BCA') THEN m.eop_balance END) / SUM(m.eop_balance), 1) AS casa_ratio_pct,
       ROUND(100.0 * 12 * SUM(m.interest_expense) / SUM(m.avg_balance), 2) AS cost_of_deposits_pct
FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code)
WHERE p.balance_side = 'liability'
GROUP BY m.month ORDER BY m.month;
''')}
Total deposits grow every month, but in one month time deposits fall while the CASA ratio jumps. Which month? Note it: a healthy total can hide a problem underneath, and you will find the root cause in Lesson 35.

## Review questions
1. Why is CASA called "sticky" funding?
2. Cost of deposits rose from 1.4% to 1.7% while the policy rate was unchanged. Give two likely causes.
3. Why can a savings account paying 0.25% still be one of the bank's most profitable products?

{answers('''
1. Customers use it for salaries and payments, so balances stay even when rates elsewhere change; switching banks is a hassle.
2. Mix shift from CASA to TDs; promotional/special TD rates; loss of large CASA balances.
3. Because FTP credits the deposit at a market funding rate far above 0.25%, and the large, stable balances generate a wide spread.
''')}
"""))

L.append(lesson(7, M, "Consumer lending: housing, auto and personal loans", "Beginner", ["Business", "Metrics"], f"""
## Objectives
- Describe the main consumer loan products and how they differ in yield, term and risk.
- Understand amortisation, days past due (DPD) and the delinquency buckets.
- Calculate portfolio yield and a simple delinquency rate.

## In plain words
Consumer loans are sold to individuals. **Housing loans** are large, long (up to 20+ years), secured by the property, low rate. **Auto loans** are medium-sized, 3–5 years, secured by the car. **Personal / salary loans** are small, unsecured and short, so they carry high rates to compensate for higher default risk. Most are **amortising**: each monthly payment covers interest plus part of the principal, so balances fall over time.

## Terms to know
{terms([
 ("Yield", "Annualised interest income ÷ average loan balance."),
 ("DPD (days past due)", "How late a payment is. Buckets: Current, 1–30, 31–60, 61–90, 90+."),
 ("Past due / delinquency rate", "Balance in a late bucket ÷ total balance (define which bucket!)."),
 ("NPL (non-performing loan)", "Generally 90+ DPD or otherwise impaired; definitions follow BSP rules."),
 ("Collateral / LTV", "Security for the loan; loan-to-value = loan ÷ collateral value."),
 ("Prepayment", "Paying early; reduces future interest income."),
])}

## Formula, meaning and limitations
**Delinquency rate (30+) = balance in 31–60, 61–90 and 90+ buckets ÷ total balance**
- *Meaning:* how much of the book is behind on payments.
- *Limitations:* a fast-growing book looks healthier than it is because new loans haven't had time to go bad (the "denominator effect"). Vintage analysis (Lesson 22) fixes this.

{illustrative('''
| Product | Typical rate | Term | Loss if default | Monthly payment on ₱500k |
|---|---|---|---|---|
| Housing | 7–8.5% | 15–20 yrs | low (secured) | ≈ ₱4,180 (20 yrs @ 8%) |
| Auto | 9–12% | 5 yrs | medium | ≈ ₱10,600 (5 yrs @ 10%) |
| Personal | 20–28% | 3 yrs | high (unsecured) | ≈ ₱19,620 (3 yrs @ 24%) |
''')}

## Hands-on (12 min)
{sql('''
-- Yield and 30+ delinquency by consumer loan product, September 2026
SELECT a.product_code,
       COUNT(*) AS accounts,
       ROUND(SUM(m.eop_balance)/1e6, 1) AS balance_m,
       ROUND(100.0 * 12 * SUM(m.interest_income) / SUM(m.avg_balance), 2) AS yield_pct,
       ROUND(100.0 * SUM(CASE WHEN m.dpd_bucket IN ('31-60','61-90','90+') THEN m.eop_balance ELSE 0 END) / SUM(m.eop_balance), 2) AS dq30_pct
FROM monthly_account m JOIN accounts a USING (account_id)
WHERE m.month = '2026-09' AND a.product_code IN ('HL','AL','PL')
GROUP BY a.product_code;
''')}
Python option:
{py('''
import sqlite3, pandas as pd
con = sqlite3.connect("sample_bank.db")
df = pd.read_sql("SELECT m.*, a.product_code FROM monthly_account m JOIN accounts a USING (account_id)", con)
pl = df[df.product_code == "PL"]
print(pl.pivot_table(index="month", columns="dpd_bucket", values="eop_balance", aggfunc="sum").fillna(0).round(0))
''')}
Which product has the highest yield and the worst delinquency? Is the extra yield worth it? (You'll answer properly in Lesson 21.)

## Review questions
1. Why do personal loans carry higher rates than housing loans?
2. What is the "denominator effect" in delinquency rates?
3. A loan moves from 61–90 to 90+. What happens to its interest accrual in many banks' systems?

{answers('''
1. They are unsecured and have higher default rates and loss severity; the rate prices in expected loss and capital.
2. Rapid new lending increases the total balance (denominator) before those loans can become delinquent, temporarily lowering the ratio.
3. It typically stops accruing interest income (non-accrual/non-performing), so yield falls; the sample data does the same.
''')}
"""))

L.append(lesson(8, M, "Credit cards and payments", "Beginner", ["Business"], f"""
## Objectives
- Explain how a credit card makes money (interest, interchange, fees) and what it costs.
- Distinguish revolvers from transactors.
- Know the Philippine payment rails: InstaPay, PESONet, QR Ph.

## In plain words
A credit card earns in three ways: **interest** when cardholders carry a balance ("revolve"), **interchange** (a small % of each purchase paid by the merchant's bank to the card issuer), and **fees** (annual, late, cash advance, FX). It costs **rewards**, **fraud losses**, **processing**, **acquisition** (marketing, sign-up gifts) and **credit losses**. **Transactors** pay in full every month: they generate interchange but no interest. **Revolvers** generate interest but also more credit risk.

Payments: the BSP's **National Retail Payment System** framework includes **InstaPay** (real-time, lower-value transfers) and **PESONet** (batch, higher-value transfers), and **QR Ph**, the national QR standard. Payment volumes drive fee income and are a rich behavioural data source.

## Terms to know
{terms([
 ("Revolve rate", "Share of balances (or cardholders) carrying debt past the due date."),
 ("Interchange", "Fee per card transaction earned by the issuer."),
 ("Activation / active rate", "Share of cards with at least one transaction in the period."),
 ("Spend per active card", "Purchase volume ÷ active cards."),
 ("Charge-off", "Balance written off as uncollectable."),
])}

{verified(f'''Cards were **32.1%** of BPI's FY2025 fee income, and BPI's credit card loans grew **31.9%** in 2025. Sources: {SRC['bpi_deck']}; {SRC['bpi_fy25']}''')}

{illustrative('''
One card account, one month: purchases ₱20,000 → interchange at 1.5% = ₱300. Revolving balance ₱30,000 at 3% per month = ₱900 interest. Annual fee amortised = ₱150. Costs: rewards ₱100, processing ₱60, FTP charge on ₱30,000 at 5.5%/yr ≈ ₱138, expected loss ≈ ₱250. Contribution ≈ ₱802.
''')}

## Hands-on (12 min)
{sql('''
-- Card portfolio by segment: balances, fees, delinquency (Sep 2026)
SELECT c.segment, COUNT(*) AS cards,
       ROUND(AVG(m.eop_balance), 0) AS avg_balance,
       ROUND(SUM(m.fee_income) / COUNT(*), 0) AS fee_per_card,
       ROUND(100.0 * SUM(CASE WHEN m.dpd_bucket <> 'Current' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_late
FROM monthly_account m JOIN accounts a USING (account_id) JOIN customers c USING (customer_id)
WHERE a.product_code = 'CC' AND m.month = '2026-09'
GROUP BY c.segment ORDER BY cards DESC;
''')}
Power BI scenario: you are asked for a card KPI page. Sketch 4 cards (KPIs) and 2 visuals you would show. Suggested: Active cards, Spend per active, Revolve rate, 30+ DQ; visuals: spend trend by month, delinquency by segment.

## Review questions
1. Why might a bank still like transactors even though they pay no interest?
2. Which payment rail would you expect for a ₱5,000 real-time transfer between friends?
3. Card fee income is up 20% but card contribution is flat. Name two cost lines to check.

{answers('''
1. They generate interchange and fees with low credit risk, and are often affluent customers with other products.
2. InstaPay (real-time, lower value). PESONet is batch, used for larger or payroll-type transfers.
3. Rewards cost, credit losses/provisions, acquisition/marketing cost, FTP charge on revolving balances, fraud.
''')}
"""))

L.append(lesson(9, M, "Corporate, SME, treasury, wealth and investment banking", "Intermediate", ["Business"], f"""
## Objectives
- Describe how corporate and SME banking earn money beyond the loan spread.
- Explain treasury's two roles: managing the balance sheet and earning trading income.
- Describe wealth, trust and investment banking revenue models (fees on AUM and deals).

## In plain words
**Corporate banking** serves large companies: term loans, working-capital lines, trade finance, and **cash management** (payroll, collections, payments). Big loans earn thin spreads, so profitability depends on the whole relationship: deposits (operating accounts), fees, FX and cross-sell. **SME / business banking** serves smaller firms with higher spreads and higher risk.

**Treasury** manages the bank's liquidity, funding and interest-rate risk (ALM), runs the FTP curve, invests surplus funds in securities, and trades FX and bonds. **Wealth management and trust** earn fees on **assets under management (AUM)**. **Investment banking** earns deal fees for underwriting bonds and equities and advising on M&A.

## Terms to know
{terms([
 ("Relationship profitability", "Profit across all products held by one corporate client group."),
 ("Trade finance", "Letters of credit, import/export financing; fee-heavy."),
 ("Cash management / transaction banking", "Payment and collection services; drives operating deposits and fees."),
 ("ALM (asset-liability management)", "Managing the mismatch in maturity and repricing between assets and liabilities."),
 ("AUM", "Assets under management; fees are usually a % of AUM."),
 ("Underwriting", "Helping issuers sell securities; earns a fee."),
])}

{verified(f'''BPI FY2025: wealth management AUM **₱1.9T**; fee mix includes Wealth Management 15.5%, Transaction Banking 5.8%, Corporate clients & business banking 3.8%, Securities brokerage & investment banking 2.9%. Institutional loans ₱1,825B (+10.4%), Business Banking loans +79.7%. Sources: {SRC['bpi_deck']}; {SRC['bpi_fy25']}''')}

{illustrative('''
Corporate client "Lim Logistics": ₱100M term loan at 6.5%, FTP 5.6% → spread income ₱0.9M/yr. Operating account averages ₱40M at 0% with FTP credit 4.0% → ₱1.6M/yr. Cash management and FX fees ₱0.8M/yr. The deposit side earns more than the loan! This is why corporate bankers talk about "the relationship", not the loan.
''')}

## Hands-on (12 min)
{sql('''
-- Top 10 corporate relationships by net interest contribution + fees, Jan–Sep 2026
SELECT c.customer_id, c.customer_name,
       ROUND(SUM(m.interest_income - m.ftp_charge)/1e6, 2) AS loan_spread_m,
       ROUND(SUM(m.ftp_credit - m.interest_expense)/1e6, 2) AS deposit_spread_m,
       ROUND(SUM(m.fee_income)/1e6, 2) AS fees_m,
       ROUND(SUM(m.interest_income - m.ftp_charge + m.ftp_credit - m.interest_expense + m.fee_income)/1e6, 2) AS total_m
FROM monthly_account m JOIN accounts a USING (account_id) JOIN customers c USING (customer_id)
WHERE c.segment = 'Corporate' AND m.month BETWEEN '2026-01' AND '2026-09'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_m DESC LIMIT 10;
''')}
For how many of the top 10 is the deposit spread bigger than the loan spread?

## Review questions
1. Why do corporate loans usually have thinner spreads than SME loans?
2. What are treasury's two roles in a bank?
3. Why is AUM, not balance sheet size, the key driver for wealth management revenue?

{answers('''
1. Large corporates have strong credit and bargaining power, so competition pushes rates down; SMEs are riskier and less served.
2. Balance sheet management (liquidity, funding, interest-rate risk, FTP) and generating income from investments and trading.
3. Wealth fees are charged as a percentage of assets managed for clients, which mostly sit off the bank's balance sheet.
''')}
"""))

L.append(lesson(10, M, "Channels: branches, ATMs, agency and digital", "Beginner", ["Business", "Metrics"], f"""
## Objectives
- Describe the bank's distribution channels and the role of each.
- Explain cost-to-serve and digital migration.
- Pass the Module 2 check.

## In plain words
A **channel** is how a customer reaches the bank: **branch**, **ATM**, **online (web)**, **mobile app**, **agency banking** (partner stores doing cash-in/cash-out) and **contact centre**. Branches are expensive but good for complex sales and trust; digital is cheap per transaction and always open. Banks try to move routine transactions to cheaper channels (**digital migration**) while keeping branches for advice and acquisition.

{verified(f'''BPI end-2025: **1,277** branches (BPI 823, BanKo 412, LSB 42) and **7,032** agency banking partner stores; ATM & digital channels were 8.2% of fee income. Source: {SRC['bpi_deck']}''')}

## Terms to know
{terms([
 ("Cost per transaction", "Channel cost ÷ number of transactions in that channel."),
 ("Digital adoption", "Share of customers active on digital channels."),
 ("Digital transaction share", "Digital transactions ÷ all transactions."),
 ("Acquisition channel", "Where the customer was onboarded (branch, digital, agency)."),
])}

## Hands-on (10 min)
{sql('''
-- Channel mix and illustrative cost-to-serve by month
SELECT t.month,
       ROUND(100.0 * SUM(CASE WHEN t.channel IN ('Mobile','Online') THEN t.txn_count END) / SUM(t.txn_count), 1) AS digital_share_pct,
       SUM(t.txn_count) AS txns,
       ROUND(SUM(t.txn_count * k.cost_per_txn_php)/1e6, 2) AS cost_to_serve_m
FROM channel_txn t JOIN channel_costs k USING (channel)
GROUP BY t.month ORDER BY t.month;
''')}
Excel option: PivotTable of `channel_txn.csv` with month in rows, channel in columns, SUM txn_count; add a % of row total.

## Module 2 check (5 min)
1. Rank SA, TD and CA by cost to the bank and explain.
2. Why does a growing personal-loan book look less delinquent than it is?
3. Name the three revenue sources of a credit card.
4. A corporate client has a big low-spread loan but large operating deposits. Is it profitable? What do you need to know?
5. What is the risk of moving every customer to digital?

{answers('''
1. TD (pays highest rate) > SA (small rate) > CA (usually zero). Non-interest servicing costs can change the ranking for low-balance CASA.
2. Denominator effect: new loans inflate the balance before they can go delinquent.
3. Interest on revolving balances, interchange, fees.
4. Possibly yes; you need FTP credits on the deposits, fees, cost to serve, credit risk and capital (RAROC).
5. Fewer cross-sell and advice opportunities, excluded customer groups, fraud risk, and branch costs that don't fall as fast as transactions do.
''')}
"""))
