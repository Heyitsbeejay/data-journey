from common import *

M = "1 · How banks work"
L = []

L.append(lesson(1, M, "How a bank makes money", "Beginner", ["Business"], f"""
## Objectives
- Explain the three ways a bank earns: the interest spread, fees, and trading/treasury gains.
- Describe maturity transformation and why it is both the business model and the main risk.
- Read a simple bank P&L top to bottom.

## In plain words
A bank borrows money from depositors cheaply, lends it out at a higher rate, and keeps the difference. That difference is the **spread**. On top of that it charges **fees** for services (cards, remittances, wealth advice, cash management) and earns from its **treasury** (investing spare cash in government bonds, FX trading). From that revenue it pays **operating expenses** (people, branches, IT), sets aside **provisions** for loans that may not be repaid, pays **tax**, and what remains is **net income**.

The twist: depositors can take money out tomorrow, but a housing loan runs 20 years. Turning short-term money into long-term loans is called **maturity transformation**. It is why banks exist, and it is why they are heavily regulated (liquidity and capital rules, Lesson 23).

## Terms to know
{terms([
 ("Interest income", "What borrowers (and bonds the bank holds) pay the bank."),
 ("Interest expense", "What the bank pays depositors and other lenders."),
 ("Net interest income (NII)", "Interest income − interest expense. The biggest revenue line for most banks."),
 ("Non-interest income", "Everything else: fees and commissions, trading gains, insurance commissions, etc."),
 ("Operating expenses (opex)", "Salaries, rent, technology, marketing, depreciation."),
 ("Provisions / credit losses", "An expense set aside for expected loan losses."),
 ("Pre-provision operating profit (PPOP)", "Revenue − opex, before provisions. Shows the earning engine before credit cost."),
])}

## The bank P&L waterfall
{illustrative('''
| Line | ₱ million |
|---|---|
| Interest income | 1,000 |
| Interest expense | (350) |
| **Net interest income** | **650** |
| Fees and other income | 250 |
| **Total revenue (operating income)** | **900** |
| Operating expenses | (450) |
| **Pre-provision operating profit** | **450** |
| Provisions for credit losses | (90) |
| **Profit before tax** | **360** |
| Tax (~25%) | (90) |
| **Net income** | **270** |

Revenue mix: 72% NII, 28% fees. Cost-to-income = 450 / 900 = 50%.
''')}

{verified(f'''
BPI's full-year 2025: total revenue **₱195.3B** (+14.8%), of which net interest income **₱148.0B** and non-interest income **₱47.2B**; operating expenses **₱92.1B**; provisions **₱17.8B**; net income **₱66.62B**. So about 76% of BPI's revenue came from NII. Source: {SRC['bpi_fy25']}
''')}

## In your reports
A CEDA profitability summary is this same waterfall, just cut by product, segment, channel or account. When a stakeholder asks "why is Segment X less profitable?", you walk down the lines: spread, volume, fees, cost, credit losses.

## How to read it as an analyst
- Revenue up but net income flat → look below the revenue line: opex or provisions grew faster.
- NII up → is it **volume** (bigger balances) or **rate** (better spread)? Lesson 12 shows how to split it.
- A bank that relies mostly on NII is sensitive to interest-rate cuts; fee income diversifies that.

## Hands-on (12 min): your first look at the sample bank
Open the sample database (see the Data kit on the hub page) in DB Browser for SQLite, DBeaver, or Python. Run:

{sql('''
-- Bank-level monthly P&L lines from the general ledger
SELECT month,
       ROUND(SUM(CASE WHEN gl_code IN ('410000','411000') THEN amount END)/1e6, 2) AS interest_income_m,
       ROUND(SUM(CASE WHEN gl_code = '510000' THEN amount END)/1e6, 2)           AS interest_expense_m,
       ROUND(SUM(CASE WHEN gl_code IN ('410000','411000') THEN amount
                      WHEN gl_code = '510000' THEN -amount END)/1e6, 2)          AS nii_m,
       ROUND(SUM(CASE WHEN gl_code = '420000' THEN amount END)/1e6, 2)           AS fees_m
FROM gl_monthly
GROUP BY month
ORDER BY month;
''')}

Then answer: roughly what share of revenue is NII in this bank? Is it closer to BPI's ~76% or lower?

## Review questions
1. Why is NII the largest revenue line for most commercial banks?
2. What is maturity transformation, and what risk does it create?
3. Revenue grew 10% but net income fell. Name two lines you would check first.

{answers('''
1. Because lending funded by deposits is the core activity; the spread on large balances produces most of the revenue.
2. Funding long-term loans with short-term deposits. It creates liquidity risk (depositors withdraw) and interest-rate risk (deposit costs reprice faster than loan yields).
3. Operating expenses and provisions for credit losses (also tax, one-offs).
''')}
"""))

L.append(lesson(2, M, "Reading a bank's balance sheet and income statement", "Beginner", ["Business", "Metrics"], f"""
## Objectives
- Name the main assets, liabilities and equity lines of a bank.
- Connect balance sheet lines to the income they generate.
- Read BPI's headline numbers and compute two ratios yourself.

## In plain words
For a normal company, loans are a liability. For a bank it is reversed: **loans are assets** (money owed to the bank) and **deposits are liabilities** (money the bank owes customers). Every peso of income on the P&L comes from a balance-sheet line: loans earn interest income, deposits cost interest expense, securities earn yield.

## Terms to know
{terms([
 ("Loans and receivables", "Money lent to customers; the main earning asset. Shown net of the loss allowance."),
 ("Investment securities", "Mostly government bonds held for liquidity and yield."),
 ("Due from BSP / cash", "Reserves and cash. Low or zero yield, needed for liquidity."),
 ("Deposit liabilities", "CASA (current and savings) plus time deposits."),
 ("Bills and bonds payable", "Wholesale funding the bank borrowed in markets."),
 ("Equity (capital)", "Shareholders' money plus retained earnings. The loss-absorbing buffer."),
 ("Loan-to-deposit ratio (LDR)", "Loans ÷ deposits. How much of deposit funding is lent out."),
 ("CASA ratio", "(Current + savings deposits) ÷ total deposits. Higher usually means cheaper funding."),
])}

## How the two statements link
| Balance sheet line | Produces on the P&L |
|---|---|
| Loans | Interest income, loan fees, provisions |
| Securities | Interest income, trading gains/losses |
| Deposits | Interest expense, service fees |
| Equity | No interest cost, but shareholders expect a return (ROE) |

{verified(f'''
BPI, end-2025: total assets **₱3.7T**; total loans **₱2.6T**; total deposits **₱2.8T**, of which CASA **₱1.7T** (CASA ratio **60.7%**); loan-to-deposit ratio **92.4%**; total equity **₱476.6B**. Source: {SRC['bpi_fy25']}
''')}

## Try the ratios yourself
- Equity ÷ assets = 476.6 ÷ 3,700 ≈ **12.9%**. So roughly ₱1 of equity supports ₱7.8 of assets (leverage).
- Loans ÷ assets = 2.6 ÷ 3.7 ≈ **70%** of the balance sheet is lending.

## In your reports
Balances are usually reported two ways: **end-of-period (EOP)** and **average daily balance (ADB)**. Income is earned on average balances, so profitability reports use ADB, while regulatory and position reports often use EOP. Mixing the two is one of the most common causes of "your number doesn't match mine" (Lesson 11).

## How to read it as an analyst
- LDR rising toward 100% → lending growing faster than deposits; funding may get more expensive.
- CASA ratio falling → customers moving to time deposits (often when rates are high); cost of funds rises.
- Equity growing slower than assets → leverage rising; watch capital ratios.

## Hands-on (12 min)
{sql('''
-- Deposits vs loans and LDR by month (end-of-period balances)
SELECT m.month,
       ROUND(SUM(CASE WHEN p.balance_side = 'liability' THEN m.eop_balance END)/1e6, 1) AS deposits_m,
       ROUND(SUM(CASE WHEN p.balance_side = 'asset'     THEN m.eop_balance END)/1e6, 1) AS loans_m,
       ROUND(100.0 * SUM(CASE WHEN p.balance_side = 'asset' THEN m.eop_balance END)
                   / SUM(CASE WHEN p.balance_side = 'liability' THEN m.eop_balance END), 1) AS ldr_pct
FROM monthly_account m
JOIN accounts a USING (account_id)
JOIN products p USING (product_code)
GROUP BY m.month
ORDER BY m.month;
''')}
Excel option: load `monthly_account.csv` and `accounts.csv`, add product_code with XLOOKUP, then a PivotTable with month in rows and SUM of eop_balance by balance side.

Compare the sample bank's LDR with BPI's 92.4%. What does the gap tell you about how the sample bank funds itself and where its spare deposits go? (Hint: look at `treasury_monthly`.)

## Review questions
1. Why are deposits a liability for a bank?
2. A bank's CASA ratio drops from 65% to 58% in a year. What happens to its cost of funds, and why?
3. Why do profitability reports usually use average balances rather than end-of-period balances?

{answers('''
1. The bank owes that money back to the depositor on demand or at maturity.
2. It usually rises: time deposits pay more interest than current/savings accounts, so the funding mix gets more expensive.
3. Interest accrues every day on the balance outstanding that day, so the average over the period matches how income and expense were actually earned. EOP can be distorted by a single large movement on the last day.
''')}
"""))

L.append(lesson(3, M, "The Philippine banking landscape and the BSP", "Beginner", ["Business", "Regulation"], f"""
## Objectives
- Describe the BSP's role and the main bank categories in the Philippines.
- Know the other key institutions: PDIC, AMLC, SEC, Insurance Commission.
- Understand the policy levers (policy rate, reserve requirement) that move bank profitability.

## In plain words
The **Bangko Sentral ng Pilipinas (BSP)** is the central bank. It sets monetary policy (the policy rate), supervises banks, licenses them, and runs or oversees the payment system. Banks follow BSP rules collected in the **Manual of Regulations for Banks (MORB)** and issued as **BSP Circulars**. The **PDIC** insures deposits. The **AMLC** enforces the anti-money-laundering law.

## Bank categories you will hear
| Category | Typical scope |
|---|---|
| Universal banks | Full commercial banking plus investment-house powers (underwriting, equity investments). Large banks such as BPI are in this group. |
| Commercial banks | Full commercial banking without the wider investment powers. |
| Thrift banks | Savings, consumer and SME lending, often regional or specialised. |
| Rural and cooperative banks | Countryside and agricultural communities. |
| Digital banks | Branchless banks licensed under a separate BSP framework. |

{verified(f'''
- BSP announced six licensed digital banks in Aug 2022: UnionDigital, GoTyme, Tonik, Maya Bank, Overseas Filipino Bank and UNObank. Source: {SRC['digital']}. BSP has since accepted new applications, so check BSP's list for the current count.
- **Reserve requirement:** BSP cut the ratio for universal and commercial banks by 200 bps to **5%**, effective the week of 28 March 2025 (digital banks −150 bps, thrift banks −100 bps). Source: {SRC['rrr']}
- **Deposit insurance:** PDIC's maximum coverage rose from ₱500,000 to **₱1 million per depositor, per bank**, effective **15 March 2025**. Source: {SRC['pdic']}
- Primary source for rules and circulars: {SRC['bsp']}
''')}

## Why these levers matter for profitability
- **Policy rate cuts** → loan yields reprice down, deposit rates fall more slowly for CASA (already near zero) → NIM can compress.
- **Reserve requirement cuts** → money that sat at the BSP earning nothing can be lent or invested → NII up.
- **Deposit insurance** → affects depositor confidence and the bank's insurance premium cost.

## In your reports
You will see regulatory segments in data (e.g., BSP loan classifications, MSME lending categories, reserve-eligible deposits). Regulatory reports to BSP (the Financial Reporting Package, FRP) use BSP definitions that can differ from internal MIS definitions. Always ask "which definition is this?"

## How to read it as an analyst
When NIM moves, check the macro first: did BSP change the policy rate in the period? Did the reserve requirement change? A margin change that lines up with a policy move is not a business-unit issue.

## Hands-on (12 min)
1. Open {SRC['bsp']} and find (a) the current policy rate and the date of the last change, (b) the latest "Status Report on the Philippine Financial System" or banking statistics page. Write both in your notes with the date you checked.
2. In the sample data, products carry an FTP (transfer) rate that steps up by 0.20% from Feb 2026 to mimic a market-rate move. Find it:
{sql('''
SELECT month, ROUND(AVG(1200.0 * ftp_charge / avg_balance), 3) AS implied_ftp_pct
FROM monthly_account m JOIN accounts a USING (account_id)
WHERE a.product_code = 'HL' AND avg_balance > 0
GROUP BY month ORDER BY month;
''')}

## Review questions
1. What is the difference between a universal bank and a commercial bank?
2. Why would a lower reserve requirement increase a bank's net interest income?
3. A colleague's NIM report uses BSP definitions and yours uses internal MIS definitions. What should you do before comparing them?

{answers('''
1. A universal bank has commercial banking powers plus investment-house powers (underwriting, equity investments in non-allied businesses); a commercial bank does not have the extended investment powers.
2. Reserves held at the BSP earn little or nothing; freed-up reserves can be lent out or invested in earning assets.
3. Agree on the definition (numerator, denominator, balance type, scope) and document the reconciling items between the two.
''')}
"""))

L.append(lesson(4, M, "BPI in the ecosystem", "Beginner", ["Business"], f"""
## Objectives
- Describe how BPI is organised and where its revenue comes from, using public disclosures only.
- Read BPI's fee-income mix and connect it to products.
- Practise separating verified facts from assumptions.

## In plain words
BPI is one of the largest universal banks in the Philippines. Its public reports split the business into lending to **institutions** (large corporates and other big borrowers) and **non-institutions** (SME, consumer, microfinance), with fee businesses (cards, wealth, insurance) on top. It also runs subsidiaries such as **BanKo** (microfinance-focused) and serves customers through branches, agency partners and digital channels.

{verified(f'''
From BPI's FY2025 investor presentation ({SRC['bpi_deck']}):
- **18.2 million** clients (16.0 million in 2024).
- **1,277** branches in total: BPI 823, BanKo 412, LSB 42. Plus **7,032** agency banking partner stores.
- Gross loans ₱2,623B: institutional ₱1,825B, non-institutional ₱798B (about 70/30 – this split is my arithmetic from the two figures).
- Wealth management AUM: **₱1.9 trillion**.
- Fee income ₱39.0B, by source: Cards 32.1%, Wealth Management 15.5%, Insurance 12.8%, Branch service charges 9.4%, ATM & digital channels 8.2%, Transaction banking 5.8%, Remittance 4.7%, Corporate clients & business banking 3.8%, Retail loans 3.5%, Securities brokerage & investment banking 2.9%, Asset sales 1.2%, Rental 0.2%.
- Risk-adjusted cost of funds: 2.37% in 4Q25 (2.44% in 4Q24).

From the FY2025 press release ({SRC['bpi_fy25']}): loan growth in 2025 was led by non-institutional loans (+25.8%), Business Banking (+79.7%), credit cards (+31.9%) and personal loans (+28.3%), against institutional loans +10.4%.
''')}

{tip('''
**What is not public:** product-level, segment-level and channel-level profitability, internal FTP rates and cost allocations. That is exactly what CEDA produces internally. In these lessons, anything at that level is illustrative and uses the sample bank, not BPI data.
''')}

## How to read it as an analyst
- Cards are a third of fee income, and card loans grew 31.9% → card data products (spend, revolve rate, delinquency) matter to management.
- Fast growth in higher-yield consumer and SME loans raises NIM, but also raises credit cost later. Keep that link in mind for Lesson 14 and the Module 3 quiz.

## Hands-on (12 min)
1. Open {SRC['bpi_ir']} and download the latest quarterly presentation. Note three numbers that changed since FY2025 and the date of the report.
2. Map BPI's fee categories to the products in the sample bank (`products` table). Which fee categories have no matching product in the sample? (Answer: wealth, insurance, remittance, brokerage — the sample bank is deliberately simple.)
3. Sample bank fee mix:
{sql('''
SELECT p.product_name, ROUND(SUM(m.fee_income)/1e6, 2) AS fees_m,
       ROUND(100.0 * SUM(m.fee_income) / (SELECT SUM(fee_income) FROM monthly_account WHERE month LIKE '2026%'), 1) AS share_pct
FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code)
WHERE m.month LIKE '2026%'
GROUP BY p.product_name ORDER BY fees_m DESC;
''')}

## Review questions
1. Which single category drives the largest share of BPI's fee income?
2. Why might fast growth in personal and credit card loans raise both NIM and provisions?
3. Where would you look to confirm a BPI figure before putting it in a presentation?

{answers('''
1. Cards (32.1% of FY2025 fee income).
2. These loans carry high interest rates (raising yield and NIM) but also higher default rates, so expected credit losses and provisions rise as the book grows and seasons.
3. BPI's investor relations pages: the quarterly press release, presentation, annual/integrated report and audited financial statements; note the report date.
''')}
"""))

L.append(lesson(5, M, "Inside the bank: who does what (and where CEDA fits)", "Beginner", ["Business", "Stakeholders"], f"""
## Objectives
- Describe front, middle and back office.
- List the main business units and support functions and what each needs from data.
- Place a Data Platforms / CEDA team in the flow from source systems to decisions.
- Pass the Module 1 check.

## In plain words
- **Front office** earns revenue and faces customers: retail branches, relationship managers, corporate bankers, treasury traders, wealth advisers.
- **Middle office** controls risk and performance: risk management, compliance, finance/controllership, strategy.
- **Back office** processes and settles: operations, loan servicing, cards processing, payments, IT.

A Data Platforms team sits across all three. It does not own the business, but it owns **trusted, standardised data**, so that the CFO, the head of retail and the chief risk officer see the same number for "deposits in NCR last month".

## Who asks what (preview of Module 7)
| Group | Typical question |
|---|---|
| Finance | Does MIS profit reconcile to the GL? Why did NIM move? |
| Treasury | What is our funding mix and cost of funds by tenor? |
| Retail / Consumer | Which segments and branches are growing deposits? |
| Corporate | Which clients are most profitable after cost of funds and capital? |
| Product | Is the new card variant profitable after acquisition cost? |
| Risk | How are vintages and delinquency rolling? |
| Compliance | Are KYC fields complete? Which accounts were flagged? |
| Senior management | Are we on budget? Where should we invest? |

{illustrative('''
A "single source of truth" in practice: Retail reports 1.20M active savings accounts; Marketing reports 1.35M. The difference turns out to be dormant accounts (no customer-initiated transaction in 12 months) that Marketing counts as active. CEDA publishes one certified definition of "active account" and both reports switch to it.
''')}

## Hands-on (10 min)
Draw (paper is fine) a one-page map: source systems → data platform → data products → consumers. Put at least 5 consumers from the table above on it. Keep this; you will extend it in Lesson 26.

## Module 1 check (5 min)
1. Write the bank P&L waterfall from interest income down to net income from memory.
2. Using BPI FY2025: NII ₱148.0B, total revenue ₱195.3B. What share of revenue is NII?
3. Name one BSP policy lever and how it affects NII.
4. Name the three "offices" and one function in each.
5. What is BPI's CASA ratio at end-2025 and why does it matter?

{answers('''
1. Interest income − interest expense = NII; + non-interest income = total revenue; − opex = PPOP; − provisions = profit before tax; − tax = net income.
2. 148.0 ÷ 195.3 ≈ 75.8%.
3. Policy rate (changes asset yields and deposit costs) or reserve requirement (frees or locks up non-earning reserves).
4. Front: relationship managers/branches; middle: risk/finance/compliance; back: operations/IT/loan servicing.
5. 60.7%. CASA is cheap funding; a higher CASA ratio lowers cost of funds and supports NIM.
''')}
"""))
