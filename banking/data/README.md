# Sample Bank PH – practice data

**Everything in this folder is synthetic.** "Sample Bank PH" is a made-up Philippine universal bank. Rates, costs and balances are plausible but are **not BPI figures**. Real, public BPI and BSP numbers live only in the ✅ "Publicly verified" boxes in the Notion lessons, each with its source.

- `sample_bank.db` – SQLite database with every table (open it with DB Browser for SQLite, DBeaver, VS Code SQLite, or Python `sqlite3`).
- `*.csv` – the same tables for Excel and Power BI.
- `build_sample_data.py` – rebuilds everything deterministically (seed 2026): `python3 build_sample_data.py`.

Period: 12 months, **Oct 2025 – Sep 2026** (`month` = `YYYY-MM`). Amounts in PHP.

| Table | Rows | Grain and key columns |
|---|---|---|
| `customers` | 2,015 | one row per customer record: `customer_id`, `cif_no`, `segment` (Mass, Mass Affluent, Affluent, SME, Corporate), `region`, `home_branch`, `onboard_channel`, `onboard_date` |
| `products` | 11 | SA, CA, TD, BCA, CTD, CC, PL, AL, HL, SBL, CL with `business_unit`, `balance_side` (asset/liability) and annual FTP rate |
| `branches` | 20 | `branch_code`, `region`, `monthly_opex_php` |
| `accounts` | 3,885 | `account_id`, `customer_id`, `product_code`, open/close dates, `status`, `contract_rate` |
| `monthly_account` | 44,212 | account × month: `avg_balance`, `eop_balance`, interest income/expense, `ftp_charge`, `ftp_credit`, `fee_income`, `dpd_bucket`, `ecl_allowance` |
| `channel_txn` | 104,547 | customer × month × channel transaction counts |
| `channel_costs` | 5 | cost per transaction: Branch ₱95, ATM ₱12, Agency ₱9, Online ₱3.50, Mobile ₱1.80 |
| `opex_monthly` | 72 | cost centre × month with an allocation driver |
| `treasury_monthly` | 12 | securities balance and income (the bank invests excess deposits) |
| `gl_monthly` | 72 | general-ledger totals per month for 410000, 411000, 420000, 120000, 210000, 510000 |

## Planted stories (spoilers, the lessons ask you to find them)
1. **April 2026 time-deposit run-off in Visayas** – a few large TD/CTD accounts mature and leave; time deposits fall while total deposits still grow (Lessons 6, 35, 36).
2. **Personal-loan cohort problem** – PLs booked through Digital onboarding in Jul–Dec 2025 turn delinquent from Mar 2026 (Lessons 14, 22, 38).
3. **Channel shift** – transactions move from branch to mobile over the year (Lessons 10, 20, 39).
4. **GL break** – a ₱1.25M manual accrual on GL 510000 in Jun 2026 with no account-level detail (Lesson 29).
5. **Duplicate customers** – 15 people onboarded twice through Digital in 2025 (same name, birth year and home branch); naive name + birth-year matching gives many more false matches (Lesson 28).
6. **FTP rate change** – FTP rates rise by 0.20 pp from Feb 2026, which moves product margins without any change in customer behaviour (Lesson 16).
