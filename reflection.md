# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
I designed a system that allows users to manage their pets and their associated tasks. The core classes I included were:

1) owner class - represents a pet owner with attributes like name, contact information, and a list of pets.
2) pet class - represents a pet with attributes like name, species, and age.
3) task class - represents a task with attributes like description of the task, due date, and status.
4) feeding class - represents a feeding schedule with attributes like time, food type, and notes.
5) quality_time class - represents quality time spent with a pet with attributes like time, exercises, and summary.
6) cleaning class - represents cleaning tasks with attributes like time, types of cleaning, and summary.

The owner class is responsible for managing the list of pets and their associated tasks. The pet class is responsible for managing the pet's information and its associated tasks. The task class is responsible for managing the task's information and its status. The feeding, quality_time, and cleaning classes are responsible for managing their respective task types.

This was initially the design I created, but it was revised a couple of times and some additional classes were added (see my mermaid diagrams for review of some of the changes).

**b. Design changes**

- Did your design change during implementation?
Yes.
- If yes, describe at least one change and why you made it.
The design changed during implementation as I realized that some classes needed additional attributes and methods to better represent the tasks and their relationships with pets and owners.  I created a "pet_quality_time" class to specifically handle quality time activities with pets, which was not initially included in the design.

later I added constraints. I addeded a scheduler class to handle the scheduling of tasks based on constraints like time, priority, and owner preferences. 
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
time, priority, and owner preferences were the main constraints considered by the scheduler. Time was prioritized to ensure that tasks were scheduled within the available time slots. Priority was considered to ensure that high-priority tasks were scheduled first. Owner preferences were taken into account to ensure that the schedule aligned with the owner's desired activities and routines.
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

1. Greedy scheduling instead of optimal bin-packing
build_schedule() picks tasks in ranked order (overdue → priority → preference) and fills the time budget greedily, rather than solving for the combination of tasks that best uses the available minutes. A HIGH-priority 50-minute task might get skipped for lack of room while two MEDIUM 25-minute tasks together would've fit perfectly. Reasonable because the ranking stays simple to explain to the owner ("why was this chosen") — true optimization would make explain_plan()'s reasoning much harder to state in plain language.

2. Treating the owner as single-threaded, even across pets
Conflict detection now blocks two different pets' tasks from occupying the same time slot, not just the same pet's tasks. This matches reality for hands-on care (you can't literally feed two pets at once) but incorrectly flags truly passive tasks (e.g., an automatic feeder needing zero attention) as conflicts too, since the model has no concept of "hands-on" vs "passive."

3. Coarse time-of-day slots instead of precise times
time is one of four fixed periods (morning/afternoon/evening/night) mapped to a single clock hour, not an exact user-chosen time. This keeps the UI to one dropdown and keeps explain_plan()'s grouping simple, but it means any two same-slot tasks are always modeled as fully overlapping — even though "morning" could really span 6am–11am. That coarseness is also what caused the Streamlit "schedule generates nothing" bug earlier: a due-date one day off silently excludes a task with no visible error.

4. Recurring tasks spawn a new object instead of mutating in place
complete() now creates a brand-new Task for the next occurrence and leaves the original as permanent completed history, rather than resetting the same object's due date. Good for a future "completion history" feature, but the task list only grows — there's no archiving, and a caller who ignores complete()'s return value silently loses the next occurrence (it's created but never scheduled again unless something holds onto it — actually it self-attaches via pet.add_task(), but the point about caller-must-use-return-value applies to any code that wants a handle on the new instance).

5. Silent exclusion + side-channel reporting instead of errors
When a task can't be scheduled (budget, conflict, not due yet), the scheduler doesn't raise — it just drops it from the result and records why on self.last_conflicts/self.last_skipped_over_budget for the caller to surface. Keeps the scheduler crash-proof on messy data, but it's a stateful side-channel (valid only for the most recent build_schedule() call) rather than part of the return value — a caller that forgets to check it gets no explanation at all, which is exactly what happened before the UI fix.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used Claude as more than a Q&A tool — I gave it direct terminal access in my project so it could act as an agent rather than just suggest code. I asked it to generate a first skeleton of pawpal_system.py mirroring my UML diagram, and from there used it for iterative debugging with permission to run `python -m pytest tests/ -v`, `python main.py`, and `streamlit run app.py`. The most helpful prompts were "what else does this change affect" — for example, when I changed `complete()`'s return type from `None` to `Optional[Task]`, it flagged that any caller expecting the old in-place-reset behavior would break, even though nothing in my codebase actually called it that way yet. It did the same when I added cross-pet conflict detection, pointing out that two different pets' tasks at the same time slot (e.g., Biscuit's breakfast and Luna's litter cleaning both at 8am) used to schedule fine and now one gets bumped.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
One clear example: after Claude generated the class skeletons from my UML, I didn't just assume the translation was complete. I manually reviewed the generated `Pet_Quality_time` class against uml.mmd and caught that it was missing the `time` attribute — the code ran fine and no test failed, so nothing would have caught this by execution alone, only by re-checking the source design.

A second example was the cross-pet conflict-detection change described above. I didn't accept the explanation on its own — I verified it concretely with `test_build_schedule_detects_overlap_across_different_pets` and `test_detect_conflicts_finds_overlap_across_different_pets` in the suite, then ran `python main.py` and a manual `streamlit run app.py` session to confirm the schedule output actually dropped the conflicting task the way the explanation claimed.
---

## 4. Testing and Verification

**a. What you tested**
- What behaviors did you test?
My final suite has 21 automated tests covering four areas: (1) recurrence math — one-off tasks completing exactly once with no follow-up, and daily/weekly/monthly recurrence generating the next occurrence, including month-end clamping edge cases (Jan 31 -> Feb 28, leap-year Feb 29, Aug 31 -> Sep 30, and Dec 31 rolling over into January of the next year); (2) conflict detection — same-pet overlap, cross-pet overlap (since the owner can only do one task at a time), exact-duplicate time slots, and confirming back-to-back tasks that merely touch endpoints are NOT flagged as conflicts; (3) sorting/filtering — chronological ordering by time-of-day slot, sort stability when two tasks share a slot, filtering by status, and case-insensitive filtering by pet name; (4) budget-constrained scheduling — confirming an overdue lower-priority task beats a higher-priority task that's merely due today when only one fits the time budget, and that the skipped one shows up in `last_skipped_over_budget`.

- Why were these tests important?
These tests pin down exact boundary and tie-breaking rules (leap years, exact-duplicate times, back-to-back non-overlap, overdue-vs-priority) that are easy to get subtly wrong and that won't surface unless you deliberately construct the edge case.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Confident for the cases I've actually pinned down: all 21 tests pass, and I additionally sanity-checked real output by running `python main.py` and `streamlit run app.py` manually rather than trusting the unit tests alone.

- What edge cases would you test next if you had more time?
The edge cases I originally guessed I'd need (overlapping times, same-priority ties, cross-pet conflicts) are already covered above. What I'd actually test next: my budget-constrained tests only pit one or two tasks against each other — I haven't stress-tested the greedy ranking with something like 10+ tasks across 3 pets to see whether the "overdue -> priority -> preference" ordering ever produces a schedule an owner would find surprising even though each individual rule is followed. I'd also want a test for the exact boundary where an owner preference and a due date actively conflict, since right now those are two separate constraints and I haven't confirmed how they interact when they disagree.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The overall design and implementation of the scheduling logic went well. I am satisfied with how the app is able to generate a daily plan based on the constraints and priorities set by the user. The app is also able to handle edge cases and provide clear explanations for the generated plan.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would add more features to the app, such as the ability to set reminders for tasks and the ability to track the completion of tasks over time. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

When creating the main it auto entered my name and email address for the owner. I had to delete that information and replace it with made-up owner information. It was a reminder that it's important to review and verify the AI generated content to ensure personal info is not leaked.