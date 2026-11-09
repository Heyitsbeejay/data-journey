# plan/

The study schedule and the script that keeps it on track when a session is cancelled.

| File | What it is |
|------|------------|
| `events.json` | All 64 sessions in order: kind (`night` or `lab`), calendar title and description, original date and time. |
| `notion_ids.json` | Session number → Notion Daily Log page id. |
| `reschedule.py` | Works out which calendar events to move or recreate after one is deleted. |

## How the auto-shift works

A scheduled task runs twice a day. It lists the calendar events titled `Learn N – …` and `Lab N – …`, passes them to `reschedule.py`, and applies the result.

- A session whose event has already started counts as done.
- If you delete a future event, that session moves into the next free slot of the same kind, and every later session of that kind moves one slot along. Learning nights use Mon–Thu 8:30 PM slots; labs use Saturday 2 PM slots.
- No sessions are placed from Dec 24 to Jan 3, or on Fridays and Sundays.
- The Notion Daily Log dates are updated to match.

Run it by hand:

```bash
python3 plan/reschedule.py input.json
```

where `input.json` is `{"now": "2026-11-10T07:00:00", "events": [{"n": 1, "eventId": "...", "start": "2026-11-10T20:30:00"}, ...]}`.
