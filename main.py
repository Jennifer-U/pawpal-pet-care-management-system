from datetime import date

from pawpal_system import (
    Cleaning,
    Feeding,
    Frequency,
    Owner,
    Pet,
    Pet_Quality_time,
    Priority,
    Scheduler,
    TaskCategory,
)


def main() -> None:
    owner = Owner(
        owner_id="O1",
        name="Roy Moon",
        email="example@example.com",
        preferences=["morning", "evening"],
    )

    dog = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    cat = Pet(pet_id="P2", name="Luna", species="cat", age=2)
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Tasks are added out of chronological order (evening, then night, then
    # morning, ...) on purpose, to prove sort_by_time() reorders them rather
    # than relying on insertion order.
    evening_playtime = Pet_Quality_time(
        description="Evening playtime",
        due_date=date.today(),
        time="evening",
        status="pending",
        duration_minutes=20,
        priority=Priority.LOW,
        category=TaskCategory.QUALITY_TIME,
        frequency=Frequency.DAILY,
        exercise="fetch",
        play_time_w_toys=True,
        outing_with_pet=False,
        notes="Backyard fetch session",
    )
    dog.add_task(evening_playtime)

    # Already completed, to exercise filter_tasks(status=...).
    night_meds = Feeding(
        description="Night medication",
        due_date=date.today(),
        time="night",
        status="completed",
        duration_minutes=5,
        priority=Priority.HIGH,
        category=TaskCategory.FEEDING,
        frequency=Frequency.DAILY,
        food_type="pill in treat",
        notes="Already given before bed",
    )
    dog.add_task(night_meds)

    breakfast = Feeding(
        description="Breakfast",
        due_date=date.today(),
        time="morning",
        status="pending",
        duration_minutes=15,
        priority=Priority.HIGH,
        category=TaskCategory.FEEDING,
        frequency=Frequency.DAILY,
        food_type="dry kibble",
        notes="Half cup, fresh water too",
    )
    dog.add_task(breakfast)

    litter_cleaning = Cleaning(
        description="Litter box cleaning",
        due_date=date.today(),
        time="afternoon",
        status="pending",
        duration_minutes=10,
        priority=Priority.MEDIUM,
        category=TaskCategory.CLEANING,
        frequency=Frequency.DAILY,
        clean_pet=False,
        clean_living_quarters=True,
        notes="Scoop and refill litter",
        quarters_detail="litter box",
    )
    cat.add_task(litter_cleaning)

    # Overlaps breakfast's 8:00-8:15 morning window, so the scheduler should
    # skip it as a time conflict rather than double-booking Biscuit.
    vet_meds = Feeding(
        description="Morning medication",
        due_date=date.today(),
        time="morning",
        status="pending",
        duration_minutes=15,
        priority=Priority.HIGH,
        category=TaskCategory.FEEDING,
        frequency=Frequency.DAILY,
        food_type="pill in treat",
        notes="Give with breakfast",
    )
    dog.add_task(vet_meds)

    scheduler = Scheduler(available_minutes=60)
    schedule = scheduler.build_schedule(owner)

    print("Today's Schedule\n")
    print(scheduler.explain_plan(schedule, owner))

    all_tasks = owner.get_all_tasks()

    print("\n\nAll Tasks Sorted By Time\n")
    for task in scheduler.sort_by_time(all_tasks):
        pet_label = f"[{task.pet.name}] " if task.pet else ""
        print(f"{task.time:<10} {pet_label}{task.get_summary()} ({task.status})")

    print("\n\nPending Tasks Only (filter by status)\n")
    for task in scheduler.filter_tasks(all_tasks, status="pending"):
        pet_label = f"[{task.pet.name}] " if task.pet else ""
        print(f"{pet_label}{task.get_summary()} ({task.status})")

    print("\n\nBiscuit's Tasks Only (filter by pet name)\n")
    for task in scheduler.filter_tasks(all_tasks, pet_name="Biscuit"):
        print(f"{task.get_summary()} - {task.time} ({task.status})")

    print("\n\nCompleting Breakfast (a DAILY task)\n")
    print(f"Before: {breakfast.description} - due {breakfast.due_date}, status={breakfast.status}")
    next_breakfast = breakfast.complete()
    print(f"After:  {breakfast.description} - due {breakfast.due_date}, status={breakfast.status}")
    print(
        f"New occurrence: {next_breakfast.description} - due {next_breakfast.due_date}, "
        f"status={next_breakfast.status}"
    )
    print(f"Biscuit now has {len(dog.get_tasks())} tasks (was {len(dog.get_tasks()) - 1} before completing).")


if __name__ == "__main__":
    main()
