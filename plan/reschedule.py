"""Shift study sessions when one is deleted from Google Calendar.

Input (JSON file, argv[1]):
  {"now": "2026-11-10T07:15:00",            # current local time, Asia/Manila
   "events": [{"n": 3, "eventId": "...", "start": "2026-11-12T20:30:00"}, ...]}
  'events' = every calendar event whose title matches ^(Learn|Lab) <n> – (all dates).

Rules
  * A session is done if its event exists and has already started. Everything else is still to do,
    including sessions whose event was deleted (skipped / cancelled).
  * Learning nights fill Mon-Thu 20:30-21:30 slots, Saturday labs fill Sat 14:00-16:00 slots,
    each in their original order, starting after 'now'.
  * A future slot left empty by a deleted event (an empty slot before the last remaining event of
    that kind) counts as "can't make it" and is skipped.
    No sessions 24 Dec - 3 Jan. Fridays and Sundays always stay free.
  * So deleting one night pushes that night and every later night one weeknight later;
    deleting a lab pushes that lab and every later lab one Saturday later.

Output (stdout JSON): {"update": [...], "create": [...], "notion": [...], "unchanged": k}
  update: {n, eventId, startTime, endTime}                    -> calendar update_event
  create: {n, summary, description, startTime, endTime}       -> calendar create_event
  notion: {n, page_id, date}  -> set the Daily Log page's Date (date:Date:start) to date
All times are local Asia/Manila without offset.
"""
import json, sys, os, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
BREAKS = [(dt.date(2026, 12, 24), dt.date(2027, 1, 3))]
SLOT = {"night": ((0, 1, 2, 3), "20:30", "21:30"), "lab": ((5,), "14:00", "16:00")}

def in_break(d):
    return any(a <= d <= b for a, b in BREAKS)

def slots(kind, after):
    days, s, e = SLOT[kind]
    d = after.date()
    while True:
        if d.weekday() in days and not in_break(d):
            start = dt.datetime.fromisoformat(f"{d.isoformat()}T{s}:00")
            if start > after:
                yield start, dt.datetime.fromisoformat(f"{d.isoformat()}T{e}:00")
        d += dt.timedelta(days=1)

def main(path):
    inp = json.load(open(path))
    now = dt.datetime.fromisoformat(inp["now"][:19])
    sessions = json.load(open(os.path.join(HERE, "events.json")))
    found = {}
    for ev in inp["events"]:
        found.setdefault(int(ev["n"]), ev)
    res = {"update": [], "create": [], "notion": [], "unchanged": 0}
    ids_path = os.path.join(HERE, "notion_ids.json")
    notion_ids = json.load(open(ids_path)) if os.path.exists(ids_path) else {}
    for kind in ("night", "lab"):
        todo = [s for s in sessions if s["kind"] == kind and not (
            s["n"] in found and dt.datetime.fromisoformat(found[s["n"]]["start"][:19]) <= now)]
        taken = {dt.datetime.fromisoformat(ev["start"][:19]) for n, ev in found.items()
                 if any(x["n"] == n and x["kind"] == kind for x in sessions)}
        last = max([t for t in taken if t > now], default=None)
        free = (sl for sl in slots(kind, now) if last is None or sl[0] in taken or sl[0] > last)
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
    print(json.dumps(res, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(sys.argv[1])
