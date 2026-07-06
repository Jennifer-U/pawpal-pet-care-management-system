# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**
<!-- Describe the goal you asked the agent to accomplish -->
**What did the agent do?**
If the agent helped fix a bug it would flagg and tell me any possible side effects of the fix. Example1: Claude AI pointed out that (during Algorithmic Layer -Automate Recurring Tasks section) changes to complete()'s return type from None to Optional[Task] and changes its side effects (original task no longer flips back to pending) — if app.py or anywhere else in your assignment later calls .complete() expecting the old in-place-reset behavior, that call site would need updating, but nothing in the current codebase does.

Example2: Claude AI pointed out that (during algorthimic Layer-Detect Task Conflicts section) behavior change worth flagging: previously two different pets could be scheduled at the exact same time (e.g., Biscuit's breakfast and Luna's litter cleaning both at 8am), since only same-pet double-booking counted as a conflict. Now that's treated as a conflict too — only one of them will make it into the schedule, with the other reported as skipped. Verified via the full pytest suite (14/14 passing), python main.py, and a headless Streamlit AppTest run reproducing a live cross-pet conflict in the UI.

Asked Claude AI agent to create skeleton for pawpal_system.py that mirrors the UML diagram.

Agent also helped with debugging.
<!-- List the steps the agent took (files edited, commands run, etc.) -->
Agent edited files after I prompted it to create a skeleton for pawpal_system.py. It also helped with debugging by suggesting changes to the code and providing explanations for errors.
**What did you have to verify or fix manually?**
verified manually that items in uml covered all desired classes and methods.

Claude AI agent would run pytests internally when I gave it permission. When given permission, the Claude AI agent would have direct terminal access in my project, so it would execute the following commands when I allowed it to:  
python -m pytest tests/ -v 
python main.py

Verified manually that the tests were running correctly and that the output was as expected using above commands. I also executed mannually:
python -m streamlit run app.py



<!-- Describe anything the agent got wrong or that required human review -->
Agent did not know when a critical attribute was missing from a class, so I had to verify that all desired attributes were present in debugged code. For instance, I created the pet_quality_time class and I did not list time as one of the attributes initially. That was an error that the agent did not catch during debugging. I verified after human review of uml.mmd code that the critical attribute was missing and added it to the class. 
---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
