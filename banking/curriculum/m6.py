from common import *

M = "6 · Banking data architecture"
L = []

L.append(lesson(26, M, "The bank's systems landscape", "Intermediate", ["Data"], f"""
## Objectives
- Name the main source systems in a bank and what data each produces.
- Explain how they connect (customer ID, account ID, GL mapping).
- Extend your Lesson 5 map with real system types.

## In plain words
A bank runs dozens of systems. Each is the **system of record** for something:
| System | System of record for | Typical data |
|---|---|---|
| Core banking | Deposit and loan accounts | Balances, rates, accruals, transactions, status |
| CIF / customer master | Customer identity | Names, IDs, addresses, KYC, segment |
| Loan origination (LOS) | Applications and approvals | Application data, scores, decisions |
| Card management | Card accounts | Limits, spend, statements, rewards |
| Payments / switch | Transfers | InstaPay/PESONet, bills payment, QR |
| Treasury system | Securities, FX, funding | Positions, trades, valuations |
| General ledger (GL) | Official accounting | Account balances by GL code, cost centre |
| CRM | Interactions and sales | Leads, campaigns, complaints |
| Channels (mobile, internet, ATM) | Usage | Logins, sessions, transactions by channel |
| HR / procurement / cost systems | Costs | Opex by cost centre |

## How they connect
- **Customer ID (CIF number)** links accounts to customers.
- **Account ID** links transactions, balances and fees.
- **Product code** links accounts to the product hierarchy.
- **GL mapping** links account-level amounts to the ledger (e.g., product HL interest → GL 410000).
- **Cost centre / branch code** links to organisation and costs.

Every broken link becomes a reporting problem: an account without a CIF can't be put in a segment; a product without a GL mapping won't reconcile.

## Hands-on (12 min)
In the sample database, list the tables and their keys, and draw the joins (an ERD on paper is fine):
{sql('''
SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name;
''')}
Then check for orphan records:
{sql('''
SELECT 'accounts without a customer' AS check_name, COUNT(*) AS n
FROM accounts a LEFT JOIN customers c USING (customer_id) WHERE c.customer_id IS NULL
UNION ALL
SELECT 'monthly rows without an account', COUNT(*)
FROM monthly_account m LEFT JOIN accounts a USING (account_id) WHERE a.account_id IS NULL;
''')}

## Review questions
1. What is a "system of record"?
2. Which key links an account to a segment?
3. Why might the card system and core banking disagree on a customer's address?

{answers('''
1. The authoritative system for a given piece of data; other systems copy from it.
2. account → customer_id (CIF) → customer segment.
3. Each keeps its own copy and updates at different times; without master data management, the copies drift.
''')}
"""))

L.append(lesson(27, M, "From source to report: warehouse, lake, marts and semantic layer", "Intermediate", ["Data"], f"""
## Objectives
- Describe the data flow: extract → land → standardise → integrate → serve.
- Distinguish data lake, warehouse, data mart and semantic layer.
- Understand the end-of-day (EOD) batch cycle and why reports are "as of" a date.

## In plain words
Source systems close their day (**EOD batch**): interest is accrued, balances are final. Data is **extracted** and **landed** raw (often in a **data lake**), then **standardised** (types, codes, currencies), **integrated** in the **enterprise data warehouse** (customers, accounts, products conformed across systems), and published as **data marts** for specific uses (profitability mart, risk mart, regulatory mart). A **semantic layer** (e.g., a Power BI dataset or a metrics layer) defines measures once – "NII", "Active customer" – so every report computes them the same way.

## Terms to know
{terms([
 ("Data lake", "Cheap storage of raw and semi-structured data; schema applied when read."),
 ("Data warehouse", "Integrated, modelled, historised data; schema applied on write."),
 ("Data mart", "Subject-specific subset optimised for a business area."),
 ("Semantic layer", "Business definitions of metrics and dimensions on top of the data."),
 ("SCD (slowly changing dimension)", "How history of attributes (e.g., segment changes) is kept."),
 ("As-of date / snapshot", "The business date the data represents."),
 ("Data product", "A certified, documented, owned dataset or report built for reuse."),
])}

{illustrative('''
A customer moves from Mass to Mass Affluent in June. Should January–May profit be reported under Mass (as it was then) or Mass Affluent (as it is now)? With an SCD Type 2 customer dimension you can do either. The choice must be written into the metric definition – otherwise two reports will disagree.
''')}

## Hands-on (12 min)
Power BI scenario: you are building a semantic model on the sample bank. Sketch a star schema:
- Fact: `monthly_account` (grain: account × month).
- Dimensions: `accounts`, `customers`, `products`, `branches`, a calendar table.
Write two DAX measures:
{code('''
// DAX – type into Power BI
NII After FTP = SUM(monthly_account[interest_income]) - SUM(monthly_account[ftp_charge])
              + SUM(monthly_account[ftp_credit]) - SUM(monthly_account[interest_expense])
Avg Balance = AVERAGEX(VALUES('Calendar'[Month]), CALCULATE(SUM(monthly_account[avg_balance])))
''')}
Why does `Avg Balance` average over months instead of summing balances?

## Review questions
1. What is the difference between a lake and a warehouse?
2. Why define measures in a semantic layer instead of in each report?
3. Why might a report run on the 2nd working day differ from one run on the 5th for the same month?

{answers('''
1. A lake stores raw data in native form for flexible later use; a warehouse stores cleaned, integrated, modelled data for consistent reporting.
2. One definition, one calculation: avoids reports silently computing the same metric differently.
3. Late adjustments: back-dated transactions, GL month-end adjustments, reclassifications, late source feeds.
''')}
"""))

L.append(lesson(28, M, "Customer data and master data management (MDM)", "Intermediate", ["Data"], f"""
## Objectives
- Explain MDM, the golden record and survivorship rules.
- Detect probable duplicate customers.
- Explain householding and relationship groups.

## In plain words
The same person can exist twice: once from a branch account in 2018 and once from a mobile-app onboarding in 2025, with two CIF numbers. **MDM** matches records that belong to the same real-world entity, decides which attribute values "survive" (the **golden record**), and gives every system the same master ID. Without it, customer counts are inflated, segment profitability is split, and KYC is inconsistent.

## Terms to know
{terms([
 ("Golden record", "The single best version of a customer, assembled from sources."),
 ("Match rules", "Deterministic (exact keys) or probabilistic (fuzzy scores) matching."),
 ("Survivorship", "Rules for which source wins per attribute (e.g., latest verified address)."),
 ("Householding", "Grouping individuals in the same household."),
 ("Relationship group", "Grouping related companies (parent and subsidiaries) for corporate banking."),
])}

## Hands-on (15 min)
Step 1 – naive matching (name + birth year):
{sql('''
SELECT COUNT(*) AS name_birthyear_pairs
FROM (SELECT customer_name, birth_year FROM customers
      WHERE birth_year <> '' GROUP BY customer_name, birth_year HAVING COUNT(*) > 1);
''')}
That number is far too high: common Filipino names plus the same birth year collide. Step 2 – add a second attribute:
{sql('''
SELECT c1.customer_id AS id_1, c2.customer_id AS id_2, c1.customer_name, c1.birth_year, c1.home_branch,
       c1.onboard_date AS onboard_1, c2.onboard_date AS onboard_2, c2.onboard_channel AS channel_2
FROM customers c1 JOIN customers c2
  ON c1.customer_name = c2.customer_name AND c1.birth_year = c2.birth_year
 AND c1.home_branch = c2.home_branch AND c1.customer_id < c2.customer_id
WHERE c1.birth_year <> ''
ORDER BY c1.customer_name;
''')}
How many probable duplicates are there now, and what onboarding channel do the second records share? What would you recommend to the digital onboarding team? (In a real bank you would also match on government ID, mobile number and full birth date.)

## Review questions
1. Why are naive name matches dangerous in the Philippines?
2. How do duplicates distort segment profitability?
3. What is a survivorship rule? Give an example.

{answers('''
1. Many common names and surnames; false matches would merge different people (a privacy and KYC problem).
2. One customer's products are split across two IDs, so each looks smaller/less profitable, customer counts are inflated and products-per-customer understated.
3. A rule that decides which source's value wins per attribute; e.g., "mobile number: most recently verified via OTP wins".
''')}
"""))

L.append(lesson(29, M, "Finance vs MIS: GL, sub-ledgers and reconciliation", "Advanced", ["Data", "Metrics"], f"""
## Objectives
- Explain the GL, sub-ledgers and how MIS (management information) relates to them.
- Perform a reconciliation between account-level data and the GL.
- Document and explain reconciling items.

## In plain words
The **general ledger** is the official book: audited, used for financial statements and BSP reports. Product systems are **sub-ledgers** with account-level detail. MIS/profitability reports are built bottom-up from account data, so they must **reconcile** to the GL within a tolerance. Differences come from manual journal entries, accrual adjustments, timing, mapping errors and items that exist only in the GL (e.g., head-office adjustments).

## Terms to know
{terms([
 ("Reconciliation", "Comparing two sources and explaining every difference."),
 ("Reconciling item", "A known, explained difference (e.g., manual accrual)."),
 ("Tolerance / materiality", "Size of difference that is acceptable without action."),
 ("Manual journal entry (MJE)", "An entry booked directly in the GL, not from a source system."),
 ("Month-end close", "The process of finalising the GL for a month."),
])}

## Hands-on (15 min): find the break
{sql('''
-- Account-level deposit interest expense vs GL 510000
WITH src AS (
  SELECT month, SUM(interest_expense) AS src_amt FROM monthly_account GROUP BY month),
gl AS (
  SELECT month, amount AS gl_amt FROM gl_monthly WHERE gl_code = '510000')
SELECT month, ROUND(src_amt, 2) AS source_total, ROUND(gl_amt, 2) AS gl_total,
       ROUND(gl_amt - src_amt, 2) AS difference,
       CASE WHEN ABS(gl_amt - src_amt) > 1000 THEN 'INVESTIGATE' ELSE 'OK' END AS status
FROM src JOIN gl USING (month) ORDER BY month;
''')}
Repeat for interest income (GL 410000) and fees (GL 420000). Then write a reconciliation note: month, amount, likely cause, owner, and whether MIS should be adjusted.
(Spoiler for checking yourself: the sample bank's GL has a ₱1.25M manual accrual in June 2026 that has no account-level detail.)

## Review questions
1. Why does MIS need to reconcile to the GL?
2. GL is higher than the source by a round ₱1,250,000 in one month. What is the likely cause, and who do you ask?
3. Should CEDA "plug" the difference into the profitability mart? What are the options?

{answers('''
1. So management reports and financial statements tell the same story; unreconciled MIS loses credibility with Finance.
2. A manual journal entry (accrual/adjustment) booked only in the GL; ask Financial Controllership for the journal reference and its allocation.
3. Not silently. Options: allocate it to products via an agreed rule, show it as an "unallocated / GL adjustment" line, or leave MIS as-is with a documented reconciling item. Agree the treatment with Finance and document it.
''')}
"""))

L.append(lesson(30, M, "Data governance: ownership, lineage, metadata and BCBS 239", "Advanced", ["Data", "Regulation"], f"""
## Objectives
- Explain data ownership vs stewardship vs custodianship.
- Explain lineage and metadata and why regulators care.
- Write a proper metric definition (business glossary entry).

## In plain words
**Governance** answers: who decides what a field means, who fixes it when it's wrong, and how do we prove where a number came from? **Data owners** (business) are accountable for a domain; **data stewards** manage definitions and quality day to day; **custodians** (IT/data platforms) run the systems. **Metadata** is data about data (definitions, owners, refresh times). **Lineage** traces a reported number back through every transformation to the source.

{verified(f'''The Basel Committee's **BCBS 239** principles (2013) set expectations for banks' risk data aggregation and reporting: governance, architecture, accuracy, completeness, timeliness and adaptability. Source: {SRC['bcbs239']}. It was written for globally systemically important banks, but supervisors widely use it as a benchmark for good practice.''')}

## Writing a metric definition (template)
| Field | Example: Active savings account |
|---|---|
| Business definition | A savings account with at least one customer-initiated transaction in the last 90 days, status not closed or dormant. |
| Calculation | COUNT(DISTINCT account_id) WHERE product_family = 'Savings' AND last_cust_txn_date >= as_of_date − 90 |
| Grain | Account |
| Source / lineage | Core banking accounts + transaction history → EDW → retail mart |
| Owner / steward | Head of Retail Deposits / Retail data steward |
| Refresh | Daily, as of previous business day |
| Exclusions | Staff accounts? Internal accounts? (state explicitly) |
| Known differences | Marketing used 180 days until 2026 |

## Hands-on (12 min)
Write definitions using the template for: (1) **NIM** for the sample bank, (2) **Active customer**, (3) **NPL ratio**. Be explicit about balance type (ADB/EOP), scope and exclusions. Store them on the hub's Glossary page in Notion.

## Review questions
1. Who should decide the definition of "active customer": the data team or the business? Why?
2. What is lineage and when do you need it urgently?
3. Name three BCBS 239 themes.

{answers('''
1. The business owner decides (it's a business concept); the data team facilitates, documents and implements it consistently.
2. The traceable path from report back to source. You need it when a regulator, auditor or executive challenges a number, or when a source change may break reports.
3. Governance and infrastructure, accuracy and integrity, completeness, timeliness, adaptability, and reporting accuracy/clarity.
''')}
"""))

L.append(lesson(31, M, "Data quality and the Single Source of Truth", "Advanced", ["Data"], f"""
## Objectives
- Apply the six data quality dimensions with concrete checks.
- Design DQ controls for a data product.
- Explain what "Single Source of Truth" really means in practice.
- Pass the Module 6 check.

## Data quality dimensions
| Dimension | Question | Example check |
|---|---|---|
| Completeness | Is it there? | % of accounts with segment populated |
| Validity | Is it allowed? | dpd_bucket in the allowed list |
| Accuracy | Is it right? | balances match source / GL |
| Consistency | Does it agree across systems? | same customer count in CRM and EDW |
| Timeliness | Is it on time? | mart loaded by 7 AM |
| Uniqueness | Is it once only? | one golden ID per customer |

**SSOT** does not mean "one giant table". It means: for each metric there is **one certified definition, one certified dataset, one owner**, and everyone uses it. Other numbers may exist, but they are labelled and reconciled to the certified one.

## Hands-on (12 min): build a mini DQ scorecard
{sql('''
SELECT 'Completeness: accounts with branch' AS rule,
       ROUND(100.0 * SUM(CASE WHEN branch_code IS NOT NULL AND branch_code <> '' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pass_pct FROM accounts
UNION ALL
SELECT 'Validity: dpd_bucket values (assets)',
       ROUND(100.0 * SUM(CASE WHEN m.dpd_bucket IN ('Current','1-30','31-60','61-90','90+') THEN 1 ELSE 0 END) / COUNT(*), 2)
  FROM monthly_account m JOIN accounts a USING (account_id) JOIN products p USING (product_code) WHERE p.balance_side = 'asset'
UNION ALL
SELECT 'Validity: no negative balances',
       ROUND(100.0 * SUM(CASE WHEN eop_balance >= 0 THEN 1 ELSE 0 END) / COUNT(*), 2) FROM monthly_account
UNION ALL
SELECT 'Uniqueness: one row per account-month',
       ROUND(100.0 * COUNT(DISTINCT account_id || month) / COUNT(*), 2) FROM monthly_account
UNION ALL
SELECT 'Consistency: closed accounts have close_date',
       ROUND(100.0 * SUM(CASE WHEN status <> 'Closed' OR close_date <> '' THEN 1 ELSE 0 END) / COUNT(*), 2) FROM accounts;
''')}
Add two rules of your own (e.g., accuracy vs GL from Lesson 29, uniqueness of customers from Lesson 28).

## Module 6 check (8 min)
1. Draw source → lake → warehouse → mart → semantic layer → report and label one control at each step.
2. What is the golden record?
3. Why must MIS reconcile to the GL, and what do you do with a difference?
4. Owner vs steward vs custodian: one line each.
5. Define SSOT in one sentence a business head would accept.

{answers('''
1. E.g., source: record counts vs extract; lake: file arrival/timeliness; warehouse: key uniqueness and referential integrity; mart: reconciliation to GL; semantic: certified measures; report: sign-off and version.
2. The single best, consolidated version of an entity (customer) built from multiple sources via matching and survivorship.
3. To keep management and official numbers consistent; investigate, document as reconciling item, agree treatment with Finance.
4. Owner: accountable business leader; steward: manages definitions and quality day to day; custodian: runs the technical platform.
5. "For every key metric there is one agreed definition and one certified dataset, so every report gives the same answer."
''')}
"""))
