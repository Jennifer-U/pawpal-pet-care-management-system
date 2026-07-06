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

    scheduler = Scheduler(available_minutes=60)
    schedule = scheduler.build_schedule(owner)

    print("Today's Schedule\n")
    print(scheduler.explain_plan(schedule, owner))


if __name__ == "__main__":
    main()
