# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample output:

Today's Schedule

MORNING
-------
[Biscuit] Feeding (HIGH)
    Food Type: dry kibble
    Notes: Half cup, fresh water too
    Why: HIGH priority, in your preferred morning slot

AFTERNOON
---------
[Luna] Cleaning (MEDIUM)
    Notes: Scoop and refill litter
    Why: MEDIUM priority

EVENING
-------
[Biscuit] Pet Quality Time (LOW)
    Notes: Backyard fetch session
    Why: LOW priority, in your preferred evening slot

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically by their resolved time-of-day period (morning → afternoon → evening → night), using `PERIOD_TO_HOUR` as the sort key. Also applied to `build_schedule()`'s final result so the returned plan is always in time order. |
| Filtering | `Scheduler.filter_tasks(tasks, status=None, pet_name=None)` | Filters a task list by completion status and/or owning pet's name (case-insensitive). Either filter, both, or neither can be supplied; supplying neither returns the input unchanged. |
| Conflict handling | `Scheduler.build_schedule()`, `Scheduler.detect_conflicts()` | `build_schedule()` skips any candidate whose time window overlaps a task it already accepted — for the same pet *or* a different one, since the owner can only do one task at a time — and records what it skipped in `self.last_conflicts`. `detect_conflicts(tasks)` is a standalone method that finds every overlapping pair in an arbitrary task list, independent of the greedy scheduling algorithm. |
| Recurring tasks | `Task.complete()`, `Task._next_due_date()` | Completing a `DAILY`/`WEEKLY`/`MONTHLY` task leaves it marked `"completed"` (a historical record) and creates + attaches a new `pending` `Task` for the next occurrence — due `+1 day`/`+1 week` via `timedelta`, or the calendar-aware `_add_one_month()` for monthly tasks (e.g. Jan 31 → Feb 28). `ONCE` tasks just complete, with no new task created. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
