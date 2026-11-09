# Banking lessons – schedule and auto-shift

- `events.json` – the 40 lessons as originally planned (Mon–Fri 12:15–12:45 Asia/Manila, Tue 10 Nov 2026 → Fri 15 Jan 2027; no lessons on 30 Nov, 8 Dec or 24 Dec – 3 Jan).
- `notion_ids.json` – lesson number → page in the Notion "Banking Lessons" database.
- `reschedule.py` – works out the new dates after a cancellation.

**How cancelling works:** delete a lesson's Google Calendar event. Twice a day (about 07:41 and 19:41 Manila) a scheduled Claude task lists the `Bank N – …` events, runs `python3 banking/plan/reschedule.py input.json`, moves that lesson and every later one to the next free weekday lunch slot, re-creates the deleted lesson in its new slot, and updates the Date in Notion. It never deletes anything. If you missed a lesson but left its event, it counts as done.

Input format and rules are in the docstring at the top of `reschedule.py`. This is separate from the AWS roadmap's `plan/` folder and its evening/Saturday slots, so the two never collide.
