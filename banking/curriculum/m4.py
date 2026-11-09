from common import *

M = "4 · Profitability measurement"
L = []

L.append(lesson(16, M, "Funds transfer pricing (FTP): the engine of profitability reporting", "Intermediate", ["Metrics", "Data"], f"""
## Objectives
- Explain why FTP exists and how it splits NII between business units and Treasury.
- Calculate FTP spread for a loan and a deposit.
- Recognise FTP fields in a profitability data mart.

## In plain words
A deposit-gathering branch and a lending team share one balance sheet. Without FTP, the lender looks like it earns the full loan rate and the branch looks like it only costs interest. **FTP** fixes this with an internal "price of money": Treasury **charges** lenders for the funds they use and **credits** deposit-takers for the funds they bring. Each unit then earns its own spread; Treasury keeps the **mismatch** (interest-rate and liquidity) result.

## Formulas, meaning and limitations
- **Loan spread (net interest contribution) = interest income − FTP charge**
- **Deposit spread = FTP credit − interest expense**
- **Treasury/ALM result = FTP charges collected − FTP credits paid + securities income − wholesale funding cost**
- Sum of all units' NII = bank NII (FTP nets to zero internally).

*Limitations:* the FTP curve is a management choice (matched-maturity, pooled, behavioural tenor for CASA, liquidity premiums). Change the curve and profitability shifts between units without the bank earning a peso more. Always state which FTP methodology a report uses.

{illustrative('''
| | Customer rate | FTP rate | Spread | On ₱10M ADB/yr |
|---|---|---|---|---|
| Housing loan | 8.0% | 6.2% | +1.8% | ₱180,000 |
| Savings deposit | 0.25% | 4.0% | +3.75% | ₱375,000 |
| Time deposit (1 yr) | 5.0% | 5.0% | 0% | ₱0 |

The savings deposit is worth more than the housing loan of the same size. FTP makes that visible.
''')}

## In your reports
Typical fields: `ftp_rate`, `ftp_charge`, `ftp_credit`, `ftp_curve_id`, `behavioural_tenor`, `liquidity_premium`. A profitability report without FTP is basically a "gross interest" report and will mislead.

## Hands-on (12 min)
{sql('''
-- Net interest contribution after FTP, by business unit (Jan–Sep 2026) — compare with Lesson 11's raw NII
SELECT p.business_unit,
       ROUND(SUM(m.interest_income - m.interest_expense)/1e6, 2) AS raw_nii_m,
       ROUND(SUM(m.interest_income - m.ftp_charge + m.ftp_credit - m.interest_expense)/1e6, 2) AS nii_after_ftp_m
FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code)
WHERE m.month BETWEEN '2026-01' AND '2026-09'
GROUP BY p.business_unit;
''')}
Then compute the Treasury result: total FTP charge − total FTP credit + treasury securities income for the same months. Does business units' NII after FTP + Treasury result ≈ total bank NII? (It should.)

## Review questions
1. Why does Treasury credit deposits at a rate higher than what customers are paid?
2. Business Banking's profit rose ₱20M because the CASA FTP rate was raised. Is the bank ₱20M better off?
3. Why do banks assign a "behavioural tenor" to savings accounts that are contractually overnight?

{answers('''
1. Deposits replace funding Treasury would otherwise buy in the market; the credit reflects that market value of the funding.
2. No. The bank's total NII is unchanged; profit moved from Treasury to Business Banking.
3. Because most CASA balances stay for years in practice; a longer tenor gets a fairer (usually higher) FTP credit and better reflects their stability.
''')}
"""))

L.append(lesson(17, M, "Cost allocation and contribution margin layers", "Intermediate", ["Metrics"], f"""
## Objectives
- Distinguish direct, indirect and overhead costs.
- Allocate costs with drivers (activity-based costing).
- Build contribution margin layers CM1 → CM3 → net profit.

## In plain words
Revenue is easy to assign to an account. Costs are not: who "owns" the head-office IT budget? Banks allocate costs in layers using **drivers**: branch costs by number of branch transactions, card operations by number of cards, head-office by share of revenue. Each layer gives a different view of profit.

## Contribution margin layers
| Layer | = | Answers |
|---|---|---|
| **CM1** | NII after FTP + fees | Is the product priced right? |
| **CM2** | CM1 − direct costs (processing, rewards, product team) | Does it cover its own direct costs? |
| **CM3** | CM2 − allocated indirect costs (branches, IT, ops) | Does it cover a fair share of shared costs? |
| **Pre-tax profit** | CM3 − provisions − overhead allocation | Is it profitable overall? |
| **Risk-adjusted** | after capital charge (Lesson 21) | Does it beat the cost of capital? |

*Limitations:* allocations are judgement calls; a product can look unprofitable at CM3 only because of how overhead was spread. For decisions (e.g., "should we drop this product?") the relevant number is usually CM2: overhead won't disappear if the product does.

## Hands-on (12 min): allocate one month's opex to products
{sql('''
-- Driver volumes for Sep 2026
SELECT 'Card accounts' AS driver, COUNT(*) AS volume FROM monthly_account m JOIN accounts a USING (account_id)
  WHERE m.month = '2026-09' AND a.product_code = 'CC'
UNION ALL
SELECT 'Loan accounts', COUNT(*) FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code)
  WHERE m.month = '2026-09' AND p.balance_side = 'asset' AND a.product_code <> 'CC'
UNION ALL
SELECT 'Branch transactions', SUM(txn_count) FROM channel_txn WHERE month = '2026-09' AND channel = 'Branch'
UNION ALL
SELECT 'Digital transactions', SUM(txn_count) FROM channel_txn WHERE month = '2026-09' AND channel IN ('Mobile','Online');
''')}
Excel exercise: put the cost centres for 2026-09 from `opex_monthly.csv` in rows. Allocate "Card operations" 100% to Credit Card, "Credit & collections" to loans by number of loan accounts, and "Head office & support" by each product's share of CM1. Compute CM2 and CM3 for Credit Card. Keep the workbook; you'll reuse it in Lesson 18.

## Review questions
1. Why is CM2 often better than CM3 for a "keep or drop the product" decision?
2. Give a sensible driver for allocating contact-centre costs.
3. Product A looks unprofitable at CM3 but strongly positive at CM2. What do you tell the product manager?

{answers('''
1. Allocated overhead mostly stays even if the product is dropped; CM2 shows what the bank actually loses.
2. Number of calls (or call minutes) by product or segment.
3. It covers its direct costs and contributes to shared costs; dropping it would make other products carry those costs. Look at pricing or cost-to-serve, not closure.
''')}
"""))

L.append(lesson(18, M, "Account and product profitability", "Intermediate", ["Metrics", "Data"], f"""
## Objectives
- Build an account-level profitability calculation.
- Roll it up to product level and read the distribution.
- Recognise the classic "few accounts make all the money" pattern.

## In plain words
Account profitability is the most granular view: for each account and month, revenue (NII after FTP + fees) minus costs (direct + allocated) minus expected credit loss. Product profitability is the sum over that product's accounts. The data mart behind it usually has one row per account per month.

## The account profit formula
**Account profit = (interest income − FTP charge) + (FTP credit − interest expense) + fees − direct costs − allocated costs − provision**

{illustrative('''
Savings account, one month: ADB ₱80,000; interest paid 0.25%/yr = ₱17; FTP credit 4.0%/yr = ₱267; fees ₱20; allocated servicing cost ₱60. Profit = 267 − 17 + 20 − 60 = **₱210**.
Savings account with ADB ₱3,000: FTP credit ₱10, interest ₱1, fee ₱0, cost ₱60 → **−₱51**. Low-balance accounts are often loss-making.
''')}

## Hands-on (15 min)
{sql('''
-- Account profitability before allocated costs (CM1 + provision) for savings accounts, Jan–Sep 2026
WITH acct AS (
  SELECT m.account_id,
         AVG(m.avg_balance) AS adb,
         SUM(m.ftp_credit - m.interest_expense + m.interest_income - m.ftp_charge + m.fee_income) AS cm1
  FROM monthly_account m JOIN accounts a USING (account_id)
  WHERE a.product_code = 'SA' AND m.month BETWEEN '2026-01' AND '2026-09'
  GROUP BY m.account_id)
SELECT CASE WHEN adb < 10000 THEN '1: < 10k' WHEN adb < 50000 THEN '2: 10k-50k'
            WHEN adb < 250000 THEN '3: 50k-250k' ELSE '4: 250k+' END AS balance_band,
       COUNT(*) AS accounts,
       ROUND(AVG(cm1), 0) AS avg_cm1_per_account,
       ROUND(SUM(cm1)/1e6, 2) AS total_cm1_m
FROM acct GROUP BY balance_band ORDER BY balance_band;
''')}
Now assume a servicing cost of ₱60 per account per month (₱540 for 9 months). Which balance bands are loss-making after this cost? What share of accounts is that?

Python stretch: plot a cumulative profit curve ("whale curve") – sort accounts by profit descending and plot cumulative profit vs % of accounts.
{py('''
import sqlite3, pandas as pd
con = sqlite3.connect("sample_bank.db")
q = """SELECT account_id, SUM(ftp_credit - interest_expense + interest_income - ftp_charge + fee_income) - 540 AS profit
       FROM monthly_account WHERE month BETWEEN '2026-01' AND '2026-09' GROUP BY account_id"""
d = pd.read_sql(q, con).sort_values("profit", ascending=False)
d["cum_share_profit"] = d.profit.cumsum() / d.profit.sum()
d["pct_accounts"] = range(1, len(d) + 1); d.pct_accounts /= len(d)
print(d[["pct_accounts", "cum_share_profit"]].iloc[[int(len(d)*x) for x in (0.05, 0.2, 0.5, 0.8)] + [-1]])
''')}

## Review questions
1. Why are low-balance CASA accounts often loss-making, and what can a bank do about it?
2. Why should product profitability be measured on ADB rather than EOP?
3. What is the "whale curve" and why does it often peak above 100%?

{answers('''
1. FTP credit on a small balance is less than the fixed cost to service the account. Options: minimum balance / maintaining fees, digital-only servicing, cross-sell.
2. Interest and FTP accrue on daily balances; EOP misstates them.
3. Cumulative profit plotted against accounts sorted by profit. It rises above 100% because the most profitable accounts earn more than the total; loss-making accounts then pull it back down.
''')}
"""))

L.append(lesson(19, M, "Customer and segment profitability, and customer lifetime value", "Advanced", ["Metrics", "Business"], f"""
## Objectives
- Roll account profit up to customers and segments.
- Explain why customer view ≠ sum of product views (cross-sell, shared costs, duplicates).
- Calculate a simple customer lifetime value (CLV).

## In plain words
Customers hold several products. A Mass Affluent customer might have a loss-making checking account but a highly profitable credit card and time deposit. **Customer profitability** sums all accounts per customer (which needs a clean customer ID, Lesson 28). **Segment profitability** sums customers by segment (Mass, Mass Affluent, Affluent, SME, Corporate).

## CLV formula, meaning and limitations
**CLV = Σ (annual profit in year t × retention^t) ÷ (1 + discount rate)^t − acquisition cost**
Simple version with constant profit m, retention r and discount d: **CLV ≈ m × r ÷ (1 + d − r) − acquisition cost.**
- *Meaning:* what a customer is worth over the relationship, today.
- *Limitations:* very sensitive to the retention assumption; ignores how profit changes as customers age; segment averages hide variation.

{illustrative('''
Mass Affluent customer: profit ₱6,000/yr, retention 85%, discount 10%, acquisition ₱3,000.
CLV ≈ 6,000 × 0.85 ÷ (1.10 − 0.85) − 3,000 = 6,000 × 3.4 − 3,000 = **₱17,400**.
If retention falls to 75%: 6,000 × 0.75 ÷ 0.35 − 3,000 = **₱9,857**. Retention is worth more than price.
''')}

## Hands-on (12 min)
{sql('''
-- Segment profitability (CM1) per customer, Jan–Sep 2026
WITH cust AS (
  SELECT a.customer_id,
         SUM(m.interest_income - m.ftp_charge + m.ftp_credit - m.interest_expense + m.fee_income) AS cm1,
         COUNT(DISTINCT a.product_code) AS products
  FROM monthly_account m JOIN accounts a USING (account_id)
  WHERE m.month BETWEEN '2026-01' AND '2026-09'
  GROUP BY a.customer_id)
SELECT c.segment, COUNT(*) AS customers,
       ROUND(AVG(cu.products), 2) AS products_per_customer,
       ROUND(AVG(cu.cm1), 0) AS cm1_per_customer,
       ROUND(SUM(cu.cm1)/1e6, 2) AS total_cm1_m,
       ROUND(100.0 * SUM(cu.cm1) / (SELECT SUM(cm1) FROM cust), 1) AS share_pct
FROM cust cu JOIN customers c USING (customer_id)
GROUP BY c.segment ORDER BY total_cm1_m DESC;
''')}
Then: does CM1 per customer rise with products per customer? Group by `products` instead of segment to see.

## Review questions
1. Why can't you get segment profitability by summing product profitability reports?
2. Which assumption in CLV matters most, and why?
3. A segment has high revenue per customer but low CLV. Give two possible reasons.

{answers('''
1. Products reports don't carry the customer/segment key consistently, customers hold multiple products, and duplicates or unlinked accounts distort counts. You need account → customer → segment mapping.
2. Retention: it compounds over every future year.
3. Low retention (high churn), high acquisition cost, high credit losses, or high cost to serve.
''')}
"""))

L.append(lesson(20, M, "Channel profitability and cost-to-serve", "Advanced", ["Metrics", "Business"], f"""
## Objectives
- Measure channel cost-to-serve and channel-attributed revenue.
- Understand attribution choices (acquisition channel vs servicing channel).
- Build a simple digital-migration savings estimate.

## In plain words
Channel profitability asks: what does each channel cost, and what revenue does it bring or protect? Costs are fairly measurable (branch opex, IT, agent commissions). Revenue is harder: a customer opens an account in a branch, transacts on mobile, and gets a loan via a relationship manager. Banks use **attribution rules**: by acquisition channel, by sales channel of the product, or split by usage.

## Formulas, meaning and limitations
- **Cost per transaction = channel cost ÷ channel transactions**
- **Cost-to-serve per customer = Σ (transactions by channel × unit cost)**
- **Migration savings = transactions moved × (old unit cost − new unit cost)**

*Limitations:* unit costs are averages, and most branch cost is fixed in the short run, so moving transactions saves less than the arithmetic says until branches are resized.

## Hands-on (12 min)
{sql('''
-- Cost-to-serve per customer by onboarding channel and segment (Sep 2026)
SELECT c.onboard_channel, c.segment,
       COUNT(DISTINCT c.customer_id) AS customers,
       ROUND(SUM(t.txn_count * k.cost_per_txn_php) / COUNT(DISTINCT c.customer_id), 0) AS cost_to_serve_per_customer,
       ROUND(100.0 * SUM(CASE WHEN t.channel IN ('Mobile','Online') THEN t.txn_count END) / SUM(t.txn_count), 1) AS digital_share_pct
FROM channel_txn t JOIN channel_costs k USING (channel) JOIN customers c USING (customer_id)
WHERE t.month = '2026-09' AND c.segment IN ('Mass','Mass Affluent')
GROUP BY c.onboard_channel, c.segment ORDER BY c.segment, cost_to_serve_per_customer DESC;
''')}
Migration estimate: if 20% of Mass segment branch transactions in Sep 2026 moved to mobile, what is the monthly saving at the illustrative unit costs (Branch ₱95, Mobile ₱1.80)? Why would the real P&L saving be smaller in year 1?

## Review questions
1. Why is it hard to attribute revenue to a channel?
2. Branch transactions fell 15% but branch costs fell 2%. Why?
3. What metric would you add to make channel profitability fair to branches?

{answers('''
1. A customer's journey spans channels; acquisition, sale and servicing happen in different places.
2. Branch costs are mostly fixed (rent, staff) in the short run; they only fall when branches are resized, reformatted or closed.
3. Sales/acquisition credit (new accounts and products sold), or advice-driven revenue such as wealth and loans originated at branches.
''')}
"""))

L.append(lesson(21, M, "Risk-adjusted profitability: capital, expected loss and RAROC", "Advanced", ["Metrics", "Regulation"], f"""
## Objectives
- Explain expected loss (EL), economic/regulatory capital and cost of capital.
- Calculate RAROC and economic profit (EVA-style).
- Pass the Module 4 check.

## In plain words
Two products earn the same profit, but one needs far more capital because it is riskier. **RAROC** puts them on the same footing: profit after expected loss, divided by the capital the product consumes. If RAROC beats the bank's **hurdle rate** (cost of equity), the product creates value.

## Formulas, meaning and limitations
- **Expected loss (EL) = PD × LGD × EAD**
- **RAROC = (revenue − costs − expected loss − tax) ÷ allocated capital**
- **Economic profit = risk-adjusted profit − (capital × hurdle rate)**

*Limitations:* capital allocation methods differ (regulatory risk-weighted assets × target ratio vs internal economic capital models); PD/LGD estimates are uncertain; small segments give unstable results.

{illustrative('''
| | Housing loan book | Personal loan book |
|---|---|---|
| Avg balance | ₱1,000M | ₱300M |
| NII after FTP | ₱18M | ₱54M |
| Fees − costs | −₱4M | −₱9M |
| Expected loss | ₱2.5M (PD 1%, LGD 25%) | ₱18M (PD 8%, LGD 75%) |
| Pre-tax | ₱11.5M | ₱27M |
| After tax (25%) | ₱8.6M | ₱20.3M |
| Capital (RWA × 12%) | ₱1,000M × 50% RW × 12% = ₱60M | ₱300M × 100% RW × 12% = ₱36M |
| **RAROC** | **14.4%** | **56%** |
| Economic profit @ 13% hurdle | ₱0.8M | ₱15.6M |

Personal loans look very attractive – as long as the PD assumption holds. If PD doubles to 16%, EL becomes ₱36M and RAROC drops to ~19%. This is the 2026 provisions story in miniature.
''')}

## Hands-on (8 min)
Use the sample data: for `PL` in Sep 2026, compute the share of accounts in each DPD bucket. Use them to pick a PD (e.g., share that moved to 31+ over the last 6 months, annualised). Re-run the personal-loan column above with your PD.

## Module 4 check (7 min)
1. Explain FTP to a branch manager in two sentences.
2. Name the contribution layers CM1, CM2, CM3 and what each subtracts.
3. Why can customer profitability differ from the sum of product profitability?
4. Why is a channel's cost saving smaller than "transactions × unit cost difference" in year 1?
5. Two products both earn ₱10M. What extra information decides which is better?

{answers('''
1. "Treasury pays your branch for the deposits you bring at the rate it would otherwise pay in the market, and charges lenders for the money they use. So your branch earns a spread on deposits even though customers are paid little interest."
2. CM1 = NII after FTP + fees; CM2 subtracts direct costs; CM3 subtracts allocated indirect costs (then provisions and overhead to get to pre-tax profit).
3. Cross-holdings, shared costs, customer mapping and duplicates; customer view nets losses on some products against profits on others.
4. Most channel costs are fixed in the short term.
5. Risk (expected loss) and capital consumed, i.e., RAROC / economic profit.
''')}
"""))
