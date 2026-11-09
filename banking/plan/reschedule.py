"""Shift Banking Analyst Academy lessons when one is deleted from Google Calendar.

Input (JSON file, argv[1]):
  {"now": "2026-11-10T07:41:00",            # current local time, Asia/Manila
   "events": [{"n": 3, "eventId": "...", "start": "2026-11-12T12:15:00"}, ...]}
  'events' = every calendar event whose title matches ^Bank <n> – (all dates).

Rules (same idea as plan/reschedule.py for the AWS roadmap)
  * A lesson is done if its event exists and has already started. Everything else is still to do,
    including lessons whose event was deleted (skipped / cancelled).
  * Lessons fill Mon-Fri 12:15-12:45 slots in order, starting after 'now'.
    PH holidays in SKIP and the 24 Dec - 3 Jan break are never used.
  * A future slot left empty by a deleted event (an empty slot before the last remaining
    lesson event) counts as "can't make it" and is skipped.
  * So deleting one lesson pushes that lesson and every later lesson one weekday later.

Output (stdout JSON): {"update": [...], "create": [...], "notion": [...], "unchanged": k}
  update: {n, eventId, startTime, endTime}                    -> calendar update_event
  create: {n, summary, description, startTime, endTime}       -> calendar create_event
  notion: {n, page_id, date}  -> set the Banking Lessons page's Date (date:Date:start) to date
All times are local Asia/Manila without offset. Nothing is ever deleted.
"""
import json, sys, os, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = {dt.date(2026, 11, 30), dt.date(2026, 12, 8),                       # Bonifacio Day, Immaculate Conception
        dt.date(2027, 2, 25), dt.date(2027, 3, 25), dt.date(2027, 3, 26),   # EDSA, Maundy Thu, Good Fri
        dt.date(2027, 4, 9)}                                                # Araw ng Kagitingan
BREAKS = [(dt.date(2026, 12, 24), dt.date(2027, 1, 3))]
START, END = "12:15", "12:45"

def ok(d):
    return d.weekday() < 5 and d not in SKIP and not any(a <= d <= b for a, b in BREAKS)

def slots(after):
    d = after.date()
    while True:
        if ok(d):
            start = dt.datetime.fromisoformat(f"{d.isoformat()}T{START}:00")
            if start > after:
                yield start, dt.datetime.fromisoformat(f"{d.isoformat()}T{END}:00")
        d += dt.timedelta(days=1)

def plan(inp, lessons, notion_ids):
    now = dt.datetime.fromisoformat(inp["now"][:19])
    found = {}
    for ev in inp["events"]:
        found.setdefault(int(ev["n"]), ev)
    res = {"update": [], "create": [], "notion": [], "unchanged": 0}
    todo = [s for s in lessons if not (
        s["n"] in found and dt.datetime.fromisoformat(found[s["n"]]["start"][:19]) <= now)]
    taken = {dt.datetime.fromisoformat(ev["start"][:19]) for ev in found.values()}
    last = max([t for t in taken if t > now], default=None)
    free = (sl for sl in slots(now) if last is None or sl[0] in taken or sl[0] > last)
    for s, (a, b) in zip(todo, free):
        st, en = a.isoformat(), b.isoformat()
        ev = found.get(s["n"])
        if (ev is None or ev["start"][:19] != st) and str(s["n"]) in notion_ids:
            res["notion"].append(dict(n=s["n"], page_id=notion_ids[str(s["n"])], date=st[:10]))
        if ev is None:
            res["create"].append(dict(n=s["n"], summary=s["summary"], description=s["description"], startTime=st, endTime=en))
        elif ev["start"][:19] != st:
            res["update"].append(dict(n=s["n"], eventId=ev["eventId"], startTime=st, endTime=en))
        else:
            res["unchanged"] += 1
    return res

def main(path):
    lessons = json.load(open(os.path.join(HERE, "events.json")))
    notion_ids = json.load(open(os.path.join(HERE, "notion_ids.json")))
    print(json.dumps(plan(json.load(open(path)), lessons, notion_ids), ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(sys.argv[1])
