import streamlit as st
from datetime import date

# Added Cleaning/Pet_Quality_time/Scheduler imports so the UI can build every task type and run the scheduler.
from pawpal_system import (
    Owner,
    Pet,
    Task,
    Feeding,
    Cleaning,
    Pet_Quality_time,
    Scheduler,
    Frequency,
    Priority,
    TaskCategory,
)


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_id="owner-1", name=owner_name, email="")

st.session_state.owner.name = owner_name
owner = st.session_state.owner

st.markdown("### Pets")
pet_col1, pet_col2, pet_col3 = st.columns(3)
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pet_col3:
    pet_age = st.number_input("Age", min_value=0, max_value=40, value=2)

# Builds a Pet and registers it with the owner via Owner.add_pet().
if st.button("Add pet"):
    owner.add_pet(
        Pet(pet_id=f"pet-{len(owner.get_pets()) + 1}", name=pet_name, species=species, age=int(pet_age))
    )

if owner.get_pets():
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species, "age": p.age} for p in owner.get_pets()])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add tasks for a pet; they feed directly into the scheduler below.")

if not owner.get_pets():
    st.info("Add a pet first before creating tasks.")
else:
    pets_by_name = {p.name: p for p in owner.get_pets()}
    selected_pet_name = st.selectbox("Pet", list(pets_by_name.keys()))
    selected_pet = pets_by_name[selected_pet_name]

    category_by_label = {
        "Feeding": TaskCategory.FEEDING,
        "Cleaning": TaskCategory.CLEANING,
        "Quality Time": TaskCategory.QUALITY_TIME,
    }
    category = category_by_label[st.selectbox("Category", list(category_by_label.keys()))]

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5, col6 = st.columns(3)
    with col4:
        time_period = st.selectbox("Time of day", ["morning", "afternoon", "evening", "night"])
    with col5:
        frequency_value = st.selectbox("Frequency", ["once", "daily", "weekly", "monthly"])
    with col6:
        due = st.date_input("Due date", value=date.today())

    notes = st.text_input("Notes", value="")

    # Category-specific inputs; only the fields for the selected task type are shown.
    if category == TaskCategory.FEEDING:
        food_type = st.text_input("Food type", value="Dry food")
    elif category == TaskCategory.CLEANING:
        clean_pet = st.checkbox("Clean the pet (bathing/grooming)", value=True)
        clean_living_quarters = st.checkbox("Clean living quarters", value=False)
    else:
        exercise = st.text_input("Exercise", value="Fetch")
        play_time_w_toys = st.checkbox("Play with toys", value=True)
        outing_with_pet = st.checkbox("Outing with pet", value=False)

    # Builds the right Task subclass for the chosen category and attaches it via Pet.add_task().
    if st.button("Add task"):
        common_kwargs = dict(
            description=task_title,
            due_date=due,
            time=time_period,
            status="pending",
            duration_minutes=int(duration),
            priority=Priority[priority.upper()],
            category=category,
            frequency=Frequency(frequency_value),
        )
        if category == TaskCategory.FEEDING:
            new_task = Feeding(**common_kwargs, food_type=food_type, notes=notes)
        elif category == TaskCategory.CLEANING:
            new_task = Cleaning(
                **common_kwargs,
                clean_pet=clean_pet,
                clean_living_quarters=clean_living_quarters,
                notes=notes,
            )
        else:
            new_task = Pet_Quality_time(
                **common_kwargs,
                exercise=exercise,
                play_time_w_toys=play_time_w_toys,
                outing_with_pet=outing_with_pet,
                notes=notes,
            )
        selected_pet.add_task(new_task)

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")

        # Filter and sort controls, backed by Scheduler.filter_tasks()/sort_by_time()
        # rather than reimplementing that logic here.
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            status_filter = st.selectbox("Filter by status", ["All", "pending", "scheduled", "completed"])
        with filter_col2:
            pet_filter = st.selectbox("Filter by pet", ["All"] + list(pets_by_name.keys()))

        display_scheduler = Scheduler(available_minutes=0)
        filtered_tasks = display_scheduler.filter_tasks(
            all_tasks,
            status=None if status_filter == "All" else status_filter,
            pet_name=None if pet_filter == "All" else pet_filter,
        )
        sorted_tasks = display_scheduler.sort_by_time(filtered_tasks)

        if sorted_tasks:
            st.table(
                [
                    {
                        "time": task.time,
                        "pet": task.pet.name if task.pet else "",
                        "type": task.get_summary(),
                        "title": task.description,
                        "duration": task.duration_minutes,
                        "priority": task.priority.name,
                        "status": task.status,
                    }
                    for task in sorted_tasks
                ]
            )
        else:
            st.info("No tasks match the selected filters.")

        # Surface time conflicts as soon as they exist, without requiring the
        # owner to click "Generate schedule" first.
        conflicts = display_scheduler.detect_conflicts(sorted_tasks)
        if conflicts:
            for task_a, task_b in conflicts:
                label_a = f"[{task_a.pet.name}] " if task_a.pet else ""
                label_b = f"[{task_b.pet.name}] " if task_b.pet else ""
                st.warning(
                    f"⏰ Time conflict: {label_a}{task_a.get_summary()} \"{task_a.description}\" "
                    f"overlaps {label_b}{task_b.get_summary()} \"{task_b.description}\" "
                    f"(both {task_a.time})."
                )
        elif sorted_tasks:
            st.success("No time conflicts detected among the tasks shown.")
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Builds today's plan from your pets' pending tasks within a fixed time budget.")

available_minutes = st.number_input("Available minutes today", min_value=1, max_value=1440, value=120)

# Runs Scheduler.build_schedule()/explain_plan() against the owner's tasks and renders the result.
if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(available_minutes=int(available_minutes))
        schedule = scheduler.build_schedule(owner)  # already chronologically sorted via sort_by_time()

        if schedule:
            st.success(f"✅ Scheduled {len(schedule)} task(s) within your {available_minutes}-minute budget.")
            st.table(
                [
                    {
                        "time": task.time,
                        "pet": task.pet.name if task.pet else "",
                        "type": task.get_summary(),
                        "title": task.description,
                        "duration": task.duration_minutes,
                        "priority": task.priority.name,
                    }
                    for task in schedule
                ]
            )
            with st.expander("Why this plan?"):
                st.text(scheduler.explain_plan(schedule, owner))
        else:
            st.warning("No tasks were scheduled — see why below.")

        # Flag skipped-for-conflict tasks front and center: a pet owner needs
        # to know their pets can't both be cared for in the same time slot.
        if scheduler.last_conflicts:
            st.warning(f"⏰ {len(scheduler.last_conflicts)} task(s) skipped due to a time conflict:")
            for task in scheduler.last_conflicts:
                pet_label = f"[{task.pet.name}] " if task.pet else ""
                st.markdown(
                    f"- {pet_label}{task.get_summary()} \"{task.description}\" "
                    f"overlaps another already-scheduled {task.time} task"
                )

        if scheduler.last_skipped_over_budget:
            st.info(f"⌛ {len(scheduler.last_skipped_over_budget)} task(s) didn't fit in today's time budget:")
            for task in scheduler.last_skipped_over_budget:
                pet_label = f"[{task.pet.name}] " if task.pet else ""
                st.markdown(f"- {pet_label}{task.get_summary()} \"{task.description}\" ({task.duration_minutes} min)")

        # Anything excluded for a reason other than conflict/budget (already
        # completed, or not due yet).
        scheduled_ids = {id(task) for task in schedule}
        conflict_ids = {id(task) for task in scheduler.last_conflicts}
        over_budget_ids = {id(task) for task in scheduler.last_skipped_over_budget}
        other_excluded = [
            task
            for task in owner.get_all_tasks()
            if id(task) not in scheduled_ids and id(task) not in conflict_ids and id(task) not in over_budget_ids
        ]
        if other_excluded:
            st.markdown("**Also not scheduled:**")
            for task in other_excluded:
                pet_label = f"[{task.pet.name}] " if task.pet else ""
                reason = (
                    "already completed"
                    if task.status == "completed"
                    else f"not due yet — due {task.due_date.isoformat()}"
                )
                st.markdown(f"- {pet_label}{task.get_summary()} \"{task.description}\" — {reason}")
