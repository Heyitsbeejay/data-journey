"""Lesson dates: weekdays 12:15-12:45 Asia/Manila from Tue 10 Nov 2026, skipping PH holidays and the year-end break."""
import datetime as dt
START = dt.date(2026, 11, 10)
SKIP = {dt.date(2026, 11, 30), dt.date(2026, 12, 8)}          # Bonifacio Day, Immaculate Conception
BREAKS = [(dt.date(2026, 12, 24), dt.date(2027, 1, 3))]          # same year-end break as the AWS plan
SLOT = ("12:15", "12:45")

def ok(d):
    return d.weekday() < 5 and d not in SKIP and not any(a <= d <= b for a, b in BREAKS)

def dates(n, start=START):
    out, d = [], start
    while len(out) < n:
        if ok(d):
            out.append(d)
        d += dt.timedelta(days=1)
    return out
