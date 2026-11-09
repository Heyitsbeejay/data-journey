"""Build the ILLUSTRATIVE sample bank dataset used in the banking lessons.

Everything here is synthetic. "Sample Bank PH" is a made-up bank; rates, costs and balances are
plausible for a Philippine universal bank but are NOT BPI figures. Several stories are planted on
purpose so the lessons have something to find (see README.md in this folder).

Run:  python3 build_sample_data.py      -> writes *.csv and sample_bank.db next to this file
"""
import csv, os, random, sqlite3, datetime as dt

random.seed(2026)
HERE = os.path.dirname(os.path.abspath(__file__))
MONTHS = [f"{y}-{m:02d}" for y, m in [(2025, 10), (2025, 11), (2025, 12)] + [(2026, k) for k in range(1, 10)]]

REGIONS = {"NCR": 0.45, "North & Central Luzon": 0.2, "South Luzon": 0.12, "Visayas": 0.13, "Mindanao": 0.10}
BRANCHES = []
for region, n in [("NCR", 8), ("North & Central Luzon", 4), ("South Luzon", 3), ("Visayas", 3), ("Mindanao", 2)]:
    for i in range(n):
        code = f"BR{len(BRANCHES)+1:03d}"
        BRANCHES.append(dict(branch_code=code, branch_name=f"{region.split()[0]} Branch {i+1}", region=region,
                             monthly_opex_php=random.randint(250, 450) * 1000))

SEGMENTS = [("Mass", 0.55), ("Mass Affluent", 0.22), ("Affluent", 0.08), ("SME", 0.12), ("Corporate", 0.03)]

# product_code, name, family, business unit, side, annual contract rate range, annual FTP rate, monthly fee per account range
PRODUCTS = [
    ("SA",  "Regular Savings",         "Deposit", "Consumer Banking",  "liability", (0.0025, 0.0025), 0.0400, (0, 50)),
    ("CA",  "Checking Account",        "Deposit", "Consumer Banking",  "liability", (0.0, 0.0),       0.0400, (100, 400)),
    ("TD",  "Time Deposit",            "Deposit", "Consumer Banking",  "liability", (0.040, 0.055),   0.0500, (0, 0)),
    ("BCA", "Business Checking",       "Deposit", "Business Banking",  "liability", (0.0, 0.0),       0.0400, (2000, 15000)),
    ("CTD", "Corporate Time Deposit",  "Deposit", "Corporate Banking", "liability", (0.045, 0.058),   0.0510, (0, 0)),
    ("CC",  "Credit Card",             "Card",    "Consumer Banking",  "asset",     (0.30, 0.36),     0.0550, (300, 1500)),
    ("PL",  "Personal Loan",           "Loan",    "Consumer Banking",  "asset",     (0.20, 0.28),     0.0550, (50, 200)),
    ("AL",  "Auto Loan",               "Loan",    "Consumer Banking",  "asset",     (0.09, 0.12),     0.0580, (50, 150)),
    ("HL",  "Housing Loan",            "Loan",    "Consumer Banking",  "asset",     (0.07, 0.085),    0.0620, (50, 150)),
    ("SBL", "SME Business Loan",       "Loan",    "Business Banking",  "asset",     (0.085, 0.11),    0.0580, (1000, 5000)),
    ("CL",  "Corporate Term Loan",     "Loan",    "Corporate Banking", "asset",     (0.060, 0.072),   0.0560, (20000, 150000)),
]
P = {p[0]: p for p in PRODUCTS}

# products a segment may hold: (code, probability, balance range PHP)
HOLD = {
    "Mass":          [("SA", 0.95, (2e3, 6e4)), ("CC", 0.30, (5e3, 6e4)), ("PL", 0.12, (5e4, 3e5)), ("TD", 0.05, (5e4, 2e5))],
    "Mass Affluent": [("SA", 0.95, (5e4, 8e5)), ("CA", 0.40, (2e4, 3e5)), ("TD", 0.30, (2e5, 2e6)), ("CC", 0.60, (2e4, 1.5e5)),
                      ("PL", 0.10, (1e5, 5e5)), ("AL", 0.12, (4e5, 1.2e6)), ("HL", 0.08, (2e6, 6e6))],
    "Affluent":      [("SA", 0.90, (5e5, 5e6)), ("CA", 0.70, (2e5, 3e6)), ("TD", 0.60, (1e6, 2e7)), ("CC", 0.80, (5e4, 3e5)),
                      ("AL", 0.15, (8e5, 2.5e6)), ("HL", 0.20, (4e6, 1.5e7))],
    "SME":           [("BCA", 0.95, (1e5, 4e6)), ("SBL", 0.45, (5e5, 1e7)), ("CC", 0.30, (3e4, 2e5)), ("TD", 0.15, (5e5, 5e6))],
    "Corporate":     [("BCA", 1.0, (2e6, 4e7)), ("CTD", 0.35, (1e7, 1e8)), ("CL", 0.8, (1e7, 1.2e8))],
}
FIRST = ["Juan", "Maria", "Jose", "Ana", "Mark", "Grace", "Paolo", "Kristine", "Rafael", "Joy", "Miguel", "Liza", "Carlo", "Bea", "Nico"]
LAST = ["Santos", "Reyes", "Cruz", "Bautista", "Garcia", "Mendoza", "Torres", "Villanueva", "Ramos", "Aquino", "Navarro", "Lim", "Tan", "Dela Cruz"]
CO = ["Trading", "Logistics", "Foods", "Builders", "Agri Ventures", "Pharma", "Retail Corp", "Holdings", "Tech Solutions", "Shipping"]

def pick(weights):
    r, acc = random.random(), 0
    for k, w in weights:
        acc += w
        if r <= acc:
            return k
    return weights[-1][0]

def rdate(a, b):
    return a + dt.timedelta(days=random.randint(0, (b - a).days))

customers, accounts = [], []
N = 2000
for i in range(1, N + 1):
    seg = pick(SEGMENTS)
    region = pick(list(REGIONS.items()))
    br = random.choice([b for b in BRANCHES if b["region"] == region])
    onboard = rdate(dt.date(2012, 1, 1), dt.date(2026, 6, 30))
    ch = pick([("Digital", 0.15), ("Branch", 0.85)]) if onboard.year < 2022 else pick([("Digital", 0.6), ("Branch", 0.3), ("Agency", 0.1)])
    if seg in ("SME", "Corporate"):
        name = f"{random.choice(LAST)} {random.choice(CO)}"
        ch = "Branch" if seg == "Corporate" else ch
        by = ""
    else:
        name = f"{random.choice(FIRST)} {random.choice(LAST)}"
        by = random.randint(1955, 2004)
    customers.append(dict(customer_id=f"C{i:05d}", cif_no=f"{random.randint(10**9, 10**10-1)}", customer_name=name,
                          birth_year=by, segment=seg, region=region, home_branch=br["branch_code"],
                          onboard_channel=ch, onboard_date=onboard.isoformat()))

# Story 5 (MDM): 15 customers were onboarded twice (same name + birth year, new CIF, digital channel).
for k, c in enumerate(random.sample([c for c in customers if c["segment"] in ("Mass", "Mass Affluent")], 15)):
    dup = dict(c, customer_id=f"C{N+k+1:05d}", cif_no=f"{random.randint(10**9, 10**10-1)}", onboard_channel="Digital",
               onboard_date=rdate(dt.date(2025, 1, 1), dt.date(2025, 12, 31)).isoformat())
    customers.append(dup)

aid = 0
for c in customers:
    holds = HOLD[c["segment"]]
    got = [h for h in holds if random.random() < h[1]] or [holds[0]]
    for code, _, (lo, hi) in got:
        aid += 1
        lo_r, hi_r = P[code][5]
        od = max(dt.date.fromisoformat(c["onboard_date"]), rdate(dt.date(2015, 1, 1), dt.date(2026, 8, 31)))
        accounts.append(dict(account_id=f"A{aid:06d}", customer_id=c["customer_id"], product_code=code,
                             open_date=od.isoformat(), close_date="", status="Active",
                             branch_code=c["home_branch"], contract_rate=round(random.uniform(lo_r, hi_r), 4),
                             _bal=random.uniform(lo, hi)))

# Story 2: personal loans booked via Digital onboarding in Jul-Dec 2025 turn delinquent from 2026-03.
cust = {c["customer_id"]: c for c in customers}
risky = {a["account_id"] for a in accounts if a["product_code"] == "PL" and cust[a["customer_id"]]["onboard_channel"] == "Digital"
         and "2025-07-01" <= a["open_date"] <= "2025-12-31"}
# make sure there are enough of them
pls = [a for a in accounts if a["product_code"] == "PL" and a["account_id"] not in risky]
for a in random.sample(pls, min(60, len(pls))):
    if cust[a["customer_id"]]["onboard_channel"] == "Digital":
        a["open_date"] = rdate(dt.date(2025, 7, 1), dt.date(2025, 12, 31)).isoformat()
        risky.add(a["account_id"])

# Story 1: three Visayas corporate/affluent TD holders pull out big time deposits in 2026-04.
td_vis = [a for a in accounts if a["product_code"] in ("TD", "CTD") and cust[a["customer_id"]]["region"] == "Visayas"]
td_vis.sort(key=lambda a: -a["_bal"])
runoff = {a["account_id"] for a in td_vis[1:4]}

monthly = []
def mstart(m):
    return dt.date.fromisoformat(m + "-01")

dpd_state = {}
for a in accounts:
    code = a["product_code"]; prod = P[code]; side = prod[4]
    bal = a["_bal"]
    for mi, m in enumerate(MONTHS):
        if a["open_date"] > (mstart(m) + dt.timedelta(days=27)).isoformat():
            continue
        if a["account_id"] in runoff and m >= "2026-04":
            if m == "2026-04":
                avg, eop = bal * 0.45, 0.0
            else:
                a["status"], a["close_date"] = "Closed", "2026-04-20"
                break
        else:
            drift = {"liability": random.uniform(-0.03, 0.045), "asset": random.uniform(-0.025, 0.03)}[side]
            if code in ("HL", "AL", "PL", "SBL", "CL"):
                drift = -random.uniform(0.005, 0.02)  # amortising
            if code == "SA" and m in ("2025-12",):
                drift += 0.06  # 13th month pay
            eop = max(bal * (1 + drift), 0)
            avg = (bal + eop) / 2
            bal = eop
        rate = a["contract_rate"]
        ftp = prod[6] + (0.002 if m >= "2026-02" else 0)  # funding curve moved up in Feb 2026
        fee = random.uniform(*prod[7]) * (12 if code == "BCA" and cust[a["customer_id"]]["segment"] == "Corporate" else 1)
        # delinquency
        dpd = "Current"
        if side == "asset" and code != "CL":
            base = 0.02 if code in ("CC", "PL") else 0.008
            if a["account_id"] in risky and m >= "2026-03":
                base = 0.10 + 0.04 * (MONTHS.index(m) - MONTHS.index("2026-03"))
            prev = dpd_state.get(a["account_id"], "Current")
            ladder = ["Current", "1-30", "31-60", "61-90", "90+"]
            if prev != "Current" and random.random() < 0.75:
                dpd = ladder[min(ladder.index(prev) + 1, 4)]
            elif random.random() < base:
                dpd = "1-30"
            dpd_state[a["account_id"]] = dpd
        pd_rate = {"Current": 0.01, "1-30": 0.08, "31-60": 0.25, "61-90": 0.45, "90+": 0.80}[dpd]
        lgd = {"HL": 0.25, "AL": 0.35, "SBL": 0.45, "CL": 0.40}.get(code, 0.75)
        ecl = round(eop * pd_rate * lgd, 2) if side == "asset" else 0.0
        row = dict(month=m, account_id=a["account_id"], avg_balance=round(avg, 2), eop_balance=round(eop, 2),
                   interest_income=0.0, interest_expense=0.0, ftp_charge=0.0, ftp_credit=0.0,
                   fee_income=round(fee, 2), dpd_bucket=dpd if side == "asset" else "", ecl_allowance=ecl)
        if side == "asset":
            earning = 0 if dpd in ("90+",) else 1  # stop accruing on 90+ (non-performing)
            row["interest_income"] = round(avg * rate / 12 * earning, 2)
            row["ftp_charge"] = round(avg * ftp / 12, 2)
        else:
            row["interest_expense"] = round(avg * rate / 12, 2)
            row["ftp_credit"] = round(avg * ftp / 12, 2)
        monthly.append(row)

# Story 3: channel usage shifts from branch to mobile.
CHANNELS = [("Branch", 95.0), ("ATM", 12.0), ("Online", 3.5), ("Mobile", 1.8), ("Agency", 9.0)]  # illustrative cost per txn PHP
txn = []
for c in customers:
    base = {"Mass": 9, "Mass Affluent": 14, "Affluent": 12, "SME": 40, "Corporate": 120}[c["segment"]]
    digital_bias = 0.7 if c["onboard_channel"] == "Digital" else 0.35
    for mi, m in enumerate(MONTHS):
        if c["onboard_date"] > m + "-28":
            continue
        tot = max(1, int(random.gauss(base, base * 0.25)))
        mob = min(0.85, digital_bias + 0.012 * mi)
        shares = {"Mobile": mob * 0.8, "Online": mob * 0.2, "ATM": (1 - mob) * 0.45, "Branch": (1 - mob) * 0.45, "Agency": (1 - mob) * 0.10}
        if c["segment"] == "Corporate":
            shares = {"Online": 0.75, "Mobile": 0.05, "Branch": 0.18, "ATM": 0.0, "Agency": 0.02}
        for ch, s in shares.items():
            n = int(round(tot * s))
            if n:
                txn.append(dict(month=m, customer_id=c["customer_id"], channel=ch, txn_count=n))

# Story 4: GL vs source reconciliation. GL deposit interest expense = sum of account level, except
# 2026-06 where a manual accrual adjustment of PHP 1,250,000 was booked in the GL only.
gl = []
agg = {}
for r in monthly:
    k = r["month"]
    a = agg.setdefault(k, dict(ii=0.0, ie=0.0, fee=0.0, loans=0.0, deps=0.0))
    a["ii"] += r["interest_income"]; a["ie"] += r["interest_expense"]; a["fee"] += r["fee_income"]
side = {a["account_id"]: P[a["product_code"]][4] for a in accounts}
for r in monthly:
    agg[r["month"]]["loans" if side[r["account_id"]] == "asset" else "deps"] += r["eop_balance"]
TREASURY_YIELD = 0.058  # illustrative yield on government securities
treasury = []
treas = {}
for m in MONTHS:
    a = agg[m]
    bal = max(a["deps"] - a["loans"], 0) * 0.9  # most excess deposits are invested; the rest is cash and reserves
    treas[m] = dict(month=m, avg_securities_balance=round(bal, 2), interest_income=round(bal * TREASURY_YIELD / 12, 2))
    treasury.append(treas[m])

for m in MONTHS:
    a = agg[m]
    adj = 1_250_000.0 if m == "2026-06" else 0.0
    gl += [dict(month=m, gl_code="410000", gl_name="Interest income - loans and receivables", amount=round(a["ii"], 2)),
           dict(month=m, gl_code="411000", gl_name="Interest income - investment securities", amount=round(treas[m]["interest_income"], 2)),
           dict(month=m, gl_code="510000", gl_name="Interest expense - deposit liabilities", amount=round(a["ie"] + adj, 2)),
           dict(month=m, gl_code="420000", gl_name="Service charges, fees and commissions", amount=round(a["fee"], 2)),
           dict(month=m, gl_code="120000", gl_name="Loans and receivables (gross, end of month)", amount=round(a["loans"], 2)),
           dict(month=m, gl_code="210000", gl_name="Deposit liabilities (end of month)", amount=round(a["deps"], 2))]

# Operating expenses by cost centre (illustrative), with the driver used to allocate them in Lesson 18.
opex = []
for mi, m in enumerate(MONTHS):
    for cc, amt, drv in [("Branch network", sum(b["monthly_opex_php"] for b in BRANCHES), "Branch transactions"),
                         ("Technology & digital", 3.5e6, "Digital transactions"),
                         ("Card operations", 1.0e6, "Card accounts"),
                         ("Credit & collections", 0.8e6, "Loan accounts"),
                         ("Marketing", 0.9e6, "New accounts opened"),
                         ("Head office & support", 3.0e6, "Revenue share")]:
        opex.append(dict(month=m, cost_centre=cc, amount_php=round(amt * (1 + 0.004 * mi) * random.uniform(0.97, 1.03), 2),
                         allocation_driver=drv))


products = [dict(product_code=p[0], product_name=p[1], product_family=p[2], business_unit=p[3], balance_side=p[4],
                 ftp_rate_annual=p[6]) for p in PRODUCTS]
channels = [dict(channel=c, cost_per_txn_php=v) for c, v in CHANNELS]
for a in accounts:
    a.pop("_bal")

TABLES = dict(customers=customers, products=products, branches=BRANCHES, accounts=accounts,
              monthly_account=monthly, channel_txn=txn, channel_costs=channels, opex_monthly=opex, treasury_monthly=treasury, gl_monthly=gl)
dbp = os.path.join(HERE, "sample_bank.db")
if os.path.exists(dbp):
    os.remove(dbp)
con = sqlite3.connect(dbp)
for name, rows in TABLES.items():
    cols = list(rows[0].keys())
    with open(os.path.join(HERE, f"{name}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    def typ(v):
        return "REAL" if isinstance(v, float) else "INTEGER" if isinstance(v, int) else "TEXT"
    con.execute(f"CREATE TABLE {name} ({', '.join(f'{c} {typ(rows[0][c])}' for c in cols)})")
    con.executemany(f"INSERT INTO {name} VALUES ({', '.join('?' * len(cols))})", [tuple(r[c] for c in cols) for r in rows])
    print(f"{name:16s} {len(rows):>7,d} rows")
con.commit(); con.close()
