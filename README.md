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

# Testing PawPal+
command to run tests: `python -m pytest`

**Recurrence logic**
- Completing a daily/weekly task creates the next occurrence exactly 1 day/week later; a `ONCE` task creates no successor.
- Monthly recurrence correctly clamps to the last valid day of the next month (Jan 31→Feb 28, and the leap-year case Jan 31→Feb 29), handles 31-day→30-day rollovers (Aug 31→Sep 30), and rolls the year over at December→January.

**Conflict detection**
- Flags overlapping tasks whether they belong to the same pet or different pets (the owner can only do one task at a time).
- Flags two tasks scheduled at the exact same time as a duplicate-time conflict.
- Does not flag back-to-back tasks that touch at the boundary (one ends exactly when the next starts) — confirms the overlap check is a strict inequality, not inclusive.
- Ignores genuinely non-overlapping tasks.

**Sorting correctness**
- Orders tasks chronologically by time-of-day period (morning → afternoon → evening → night).
- Preserves original relative order for tasks with identical time slots (sort stability).
- Confirms overdue status outranks priority when building a schedule — an overdue low-priority task is scheduled ahead of a same-day high-priority one.

**Supporting coverage**
- Task status transitions on `complete()`, pet/task registration, budget-based schedule building (including skipping tasks that don't fit or that conflict), and status/pet-name filtering (case-insensitive).

### Test run output

```
tests/test_pawpal.py::test_complete_changes_task_status PASSED                                            [  4%]
tests/test_pawpal.py::test_complete_once_task_returns_none_and_creates_no_new_task PASSED                 [  9%]
tests/test_pawpal.py::test_complete_daily_task_creates_next_occurrence_one_day_later PASSED               [ 14%]
tests/test_pawpal.py::test_complete_weekly_task_creates_next_occurrence_one_week_later PASSED             [ 19%]
tests/test_pawpal.py::test_complete_monthly_task_creates_next_occurrence_next_month PASSED                [ 23%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED                                       [ 28%]
tests/test_pawpal.py::test_build_schedule_skips_overlapping_task_for_same_pet PASSED                      [ 33%]
tests/test_pawpal.py::test_build_schedule_detects_overlap_across_different_pets PASSED                    [ 38%]
tests/test_pawpal.py::test_detect_conflicts_finds_overlap_for_same_pet PASSED                             [ 42%]
tests/test_pawpal.py::test_detect_conflicts_finds_overlap_across_different_pets PASSED                    [ 47%]
tests/test_pawpal.py::test_detect_conflicts_ignores_non_overlapping_tasks PASSED                          [ 52%]
tests/test_pawpal.py::test_sort_by_time_orders_tasks_chronologically PASSED                               [ 57%]
tests/test_pawpal.py::test_filter_tasks_by_status PASSED                                                  [ 61%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name_is_case_insensitive PASSED                             [ 66%]
tests/test_pawpal.py::test_complete_monthly_task_clamps_to_leap_year_february PASSED                      [ 71%]
tests/test_pawpal.py::test_complete_monthly_task_rolls_over_to_next_year PASSED                           [ 76%]
tests/test_pawpal.py::test_complete_monthly_task_clamps_to_30_day_month PASSED                            [ 80%]
tests/test_pawpal.py::test_detect_conflicts_flags_tasks_scheduled_at_the_exact_same_time PASSED           [ 85%]
tests/test_pawpal.py::test_detect_conflicts_does_not_flag_back_to_back_tasks PASSED                       [ 90%]
tests/test_pawpal.py::test_sort_by_time_preserves_original_order_for_tasks_with_same_time PASSED          [ 95%]
tests/test_pawpal.py::test_build_schedule_prioritizes_overdue_task_over_higher_priority_task PASSED       [100%]

========================================================================== 21 passed in 0.02s ==========================================================================
```

### Confidence Level

⭐⭐⭐⭐☆ (4/5)

All 21 tests pass, covering the core recurrence, conflict-detection, and sorting logic plus several boundary cases (month-end clamping, leap years, touching-endpoint conflicts, overdue-vs-priority ranking). One star held back because the UI layer (`app.py`) and multi-pet/multi-owner scale scenarios aren't covered by automated tests — those have only been checked manually.