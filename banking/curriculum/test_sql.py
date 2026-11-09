import re, sqlite3, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import m1, m2, m3, m4, m5, m6, m7, m8
LESSONS = sorted(m1.L + m2.L + m3.L + m4.L + m5.L + m6.L + m7.L + m8.L, key=lambda x: x["n"])
assert [l["n"] for l in LESSONS] == list(range(1, 41)), [l["n"] for l in LESSONS]
con = sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "data", "sample_bank.db"))
show = set(int(a) for a in sys.argv[1:])
bad = 0
for l in LESSONS:
    for i, q in enumerate(re.findall(r"```sql\n(.*?)\n```", l["body"], re.S)):
        try:
            cur = con.execute(q); rows = cur.fetchall()
            if l["n"] in show:
                print(f"--- L{l['n']} q{i}", [d[0] for d in cur.description]); [print(r) for r in rows[:14]]
            if not rows: print(f"L{l['n']} q{i}: NO ROWS")
        except Exception as e:
            bad += 1; print(f"L{l['n']} q{i}: ERROR {e}")
print("lessons", len(LESSONS), "errors", bad)
