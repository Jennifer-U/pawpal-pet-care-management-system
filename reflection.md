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
brainstorming and debugging were the main ways I used AI tools during this project. I found that asking specific questions about how to implement certain features or how to fix errors in the code was most helpful. For example, I would ask the AI to explain why a particular error was occurring in the code.
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
I would have to run the code and test it to see if it worked as expected. If it did not, I would review the AI's suggestion and compare it to the requirements of the project to determine if it was a valid solution. 
---

## 4. Testing and Verification

**a. What you tested**
- What behaviors did you test?
Behaviors tested included the scheduling logic, task management, and the overall functionality of the app. I tested whether tasks were scheduled correctly based on time, priority, and owner preferences. 

- Why were these tests important?
These tests were important to ensure that the app was functioning as intended and that the scheduling logic was working correctly. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
Very confident. I ran multiple tests and verified that the output matched the expected results.

- What edge cases would you test next if you had more time?
I ended up testing edge cases like scheduling tasks with overlapping times, tasks with the same priority, and tasks with conflicting owner preferences. If I had more time, I would test additional edge cases like scheduling tasks for multiple pets with different care needs and testing the app's behavior when there are no available time slots for tasks.
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

When creating the main it auto entered my name and email address for the owner. I had to delete that information and replace it with the made-up owner information. It was a reminder that it's important to review and verify the AI generated content to ensure personal info is not leaked.