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

A tradeoff made by the scheduler is that it may not always schedule all tasks within a single day if there are too many high-priority tasks. This tradeoff is reasonable because it ensures that the most important tasks are completed first, even if it means some lower-priority tasks may need to be rescheduled for another day. This approach helps maintain a manageable workload for the pet owner while still addressing critical pet care needs.
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
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

When creating the main it auto entered my name and email address for the owner. I had to delete that information and replace it with the made-up owner information. It was a reminder that it's important to review and verify the AI generated content to ensure personal info is not leaked.