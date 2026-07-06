from datetime import date, timedelta

from pawpal_system import Feeding, Frequency, Owner, Pet, Priority, Scheduler, TaskCategory


def _make_feeding_task(
    time: str = "morning",
    duration_minutes: int = 10,
    priority: Priority = Priority.MEDIUM,
    frequency: Frequency = Frequency.ONCE,
    due_date: date = None,
) -> Feeding:
    return Feeding(
        description="Breakfast",
        due_date=due_date or date.today(),
        time=time,
        status="pending",
        duration_minutes=duration_minutes,
        priority=priority,
        category=TaskCategory.FEEDING,
        frequency=frequency,
        food_type="kibble",
        notes="",
    )


def test_complete_changes_task_status():
    task = _make_feeding_task()
    assert task.status == "pending"

    task.complete()

    assert task.status == "completed"


def test_complete_once_task_returns_none_and_creates_no_new_task():
    pet = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    task = _make_feeding_task(frequency=Frequency.ONCE)
    pet.add_task(task)

    next_task = task.complete()

    assert next_task is None
    assert task.status == "completed"
    assert pet.get_tasks() == [task]


def test_complete_daily_task_creates_next_occurrence_one_day_later():
    pet = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    today = date.today()
    task = _make_feeding_task(frequency=Frequency.DAILY, due_date=today)
    pet.add_task(task)

    next_task = task.complete()

    # Original stays completed as a historical record, at its original due date.
    assert task.status == "completed"
    assert task.due_date == today

    # A new pending instance is created for the next occurrence, exactly
    # one day later via timedelta(days=1).
    assert next_task is not task
    assert next_task.status == "pending"
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.frequency == Frequency.DAILY
    assert pet.get_tasks() == [task, next_task]


def test_complete_weekly_task_creates_next_occurrence_one_week_later():
    pet = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    today = date.today()
    task = _make_feeding_task(frequency=Frequency.WEEKLY, due_date=today)
    pet.add_task(task)

    next_task = task.complete()

    assert next_task.due_date == today + timedelta(weeks=1)
    assert next_task.status == "pending"


def test_complete_monthly_task_creates_next_occurrence_next_month():
    pet = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    task = _make_feeding_task(frequency=Frequency.MONTHLY, due_date=date(2026, 1, 31))
    pet.add_task(task)

    next_task = task.complete()

    # Jan 31 has no Feb 31, so it clamps to the last day of February.
    assert next_task.due_date == date(2026, 2, 28)


def test_add_task_increases_pet_task_count():
    pet = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    assert len(pet.get_tasks()) == 0

    pet.add_task(_make_feeding_task())

    assert len(pet.get_tasks()) == 1


def test_build_schedule_skips_overlapping_task_for_same_pet():
    owner = Owner(owner_id="O1", name="Roy Moon", email="roy@example.com")
    pet = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    owner.add_pet(pet)

    # Both due at "morning" (8:00) for the same pet; the second would run
    # until 8:45, overlapping the first task's 8:00-8:30 window.
    first = _make_feeding_task(time="morning", duration_minutes=30, priority=Priority.HIGH)
    second = _make_feeding_task(time="morning", duration_minutes=45, priority=Priority.MEDIUM)
    pet.add_task(first)
    pet.add_task(second)

    scheduler = Scheduler(available_minutes=120)
    schedule = scheduler.build_schedule(owner)

    assert first in schedule
    assert second not in schedule
    assert scheduler.last_conflicts == [second]


def test_build_schedule_detects_overlap_across_different_pets():
    # The owner can only do one task at a time, so an overlap between two
    # different pets' tasks is still a conflict, not just a same-pet one.
    owner = Owner(owner_id="O1", name="Roy Moon", email="roy@example.com")
    dog = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    cat = Pet(pet_id="P2", name="Luna", species="cat", age=2)
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog_task = _make_feeding_task(time="morning", duration_minutes=30)
    cat_task = _make_feeding_task(time="morning", duration_minutes=30)
    dog.add_task(dog_task)
    cat.add_task(cat_task)

    scheduler = Scheduler(available_minutes=120)
    schedule = scheduler.build_schedule(owner)

    assert len(schedule) == 1
    assert len(scheduler.last_conflicts) == 1


def test_detect_conflicts_finds_overlap_for_same_pet():
    pet = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    first = _make_feeding_task(time="morning", duration_minutes=30)
    second = _make_feeding_task(time="morning", duration_minutes=45)
    pet.add_task(first)
    pet.add_task(second)

    scheduler = Scheduler(available_minutes=120)
    conflicts = scheduler.detect_conflicts([first, second])

    assert conflicts == [(first, second)]


def test_detect_conflicts_finds_overlap_across_different_pets():
    dog = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    cat = Pet(pet_id="P2", name="Luna", species="cat", age=2)
    dog_task = _make_feeding_task(time="morning", duration_minutes=30)
    cat_task = _make_feeding_task(time="morning", duration_minutes=30)
    dog.add_task(dog_task)
    cat.add_task(cat_task)

    scheduler = Scheduler(available_minutes=120)
    conflicts = scheduler.detect_conflicts([dog_task, cat_task])

    assert conflicts == [(dog_task, cat_task)]


def test_detect_conflicts_ignores_non_overlapping_tasks():
    morning_task = _make_feeding_task(time="morning", duration_minutes=15)
    afternoon_task = _make_feeding_task(time="afternoon", duration_minutes=15)

    scheduler = Scheduler(available_minutes=120)
    conflicts = scheduler.detect_conflicts([morning_task, afternoon_task])

    assert conflicts == []


def test_sort_by_time_orders_tasks_chronologically():
    night_task = _make_feeding_task(time="night")
    morning_task = _make_feeding_task(time="morning")
    afternoon_task = _make_feeding_task(time="afternoon")
    evening_task = _make_feeding_task(time="evening")

    scheduler = Scheduler(available_minutes=120)
    ordered = scheduler.sort_by_time([night_task, afternoon_task, morning_task, evening_task])

    assert ordered == [morning_task, afternoon_task, evening_task, night_task]


def test_filter_tasks_by_status():
    pending = _make_feeding_task()
    completed = _make_feeding_task()
    completed.status = "completed"

    scheduler = Scheduler(available_minutes=120)
    result = scheduler.filter_tasks([pending, completed], status="completed")

    assert result == [completed]


def test_filter_tasks_by_pet_name_is_case_insensitive():
    dog = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    cat = Pet(pet_id="P2", name="Luna", species="cat", age=2)
    dog_task = _make_feeding_task()
    cat_task = _make_feeding_task()
    dog.add_task(dog_task)
    cat.add_task(cat_task)

    scheduler = Scheduler(available_minutes=120)
    result = scheduler.filter_tasks([dog_task, cat_task], pet_name="biscuit")

    assert result == [dog_task]
