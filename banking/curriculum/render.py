import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m1, m2, m3, m4, m5, m6, m7, m8
from schedule import dates, SLOT
LESSONS = sorted(m1.L + m2.L + m3.L + m4.L + m5.L + m6.L + m7.L + m8.L, key=lambda x: x["n"])
DATES = dates(len(LESSONS))
REPO = "https://github.com/Heyitsbeejay/data-journey/tree/main/banking"
WD = "Mon Tue Wed Thu Fri Sat Sun".split()

def page(l):
    d = DATES[l["n"] - 1]
    recall = (f"Answer Lesson {l['n']-1}'s review questions from memory, then check the answers."
              if l["n"] > 1 else "Skim the hub page: how the course works and how to open the sample data.")
    head = f"""<callout icon="📅" color="blue_bg">
<b>Lesson {l['n']} of 40</b> · Module {l['module']} · {l['level']} · planned {WD[d.weekday()]} {d.strftime('%d %b %Y')}, {SLOT[0]}–{SLOT[1]}
</callout>

## Your 30 minutes
- **3 min – recall:** {recall}
- **12 min – read** the concept sections below.
- **12 min – do** the hands-on exercise.
- **3 min – check** yourself with the review questions; rate your confidence in the database.
"""
    foot = f"""
---
## My notes
<p />

<callout icon="🗂️" color="gray_bg">
Sample data and SQL: [banking/ in your data-journey repo]({REPO}) · ✅ = publicly verified (source linked) · 🧪 = illustrative, made-up numbers · Can't make it? Delete today's calendar event and the remaining lessons move forward automatically.
</callout>"""
    return head + "\n" + l["body"] + "\n" + foot

if __name__ == "__main__":
    out = []
    for l in LESSONS:
        d = DATES[l["n"] - 1]
        out.append(dict(n=l["n"], title=l["title"], module=l["module"], level=l["level"], focus=l["focus"],
                        date=d.isoformat(), content=page(l)))
    json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
    tot = sum(len(x["content"]) for x in out)
    print("chars", tot, "max", max(len(x["content"]) for x in out), "end", out[-1]["date"])
