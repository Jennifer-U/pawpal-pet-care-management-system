# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**
<!-- Describe the goal you asked the agent to accomplish -->
**What did the agent do?**
Asked agent to create skeleton for pawpal_system.py that mirrors the UML diagram.
Agent also helped with debugging.
<!-- List the steps the agent took (files edited, commands run, etc.) -->
Agent edited files after I prompted it to create a skeleton for pawpal_system.py. It also helped with debugging by suggesting changes to the code and providing explanations for errors.
**What did you have to verify or fix manually?**
verified manually that items in uml covered all desired classes and methods.
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
