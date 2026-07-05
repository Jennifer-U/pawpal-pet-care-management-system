from datetime import date

from pawpal_system import Feeding, Frequency, Pet, Priority, TaskCategory


def _make_feeding_task() -> Feeding:
    return Feeding(
        description="Breakfast",
        due_date=date.today(),
        time="morning",
        status="pending",
        duration_minutes=10,
        priority=Priority.MEDIUM,
        category=TaskCategory.FEEDING,
        frequency=Frequency.ONCE,
        food_type="kibble",
        notes="",
    )


def test_complete_changes_task_status():
    task = _make_feeding_task()
    assert task.status == "pending"

    task.complete()

    assert task.status == "completed"


def test_add_task_increases_pet_task_count():
    pet = Pet(pet_id="P1", name="Biscuit", species="dog", age=4)
    assert len(pet.get_tasks()) == 0

    pet.add_task(_make_feeding_task())

    assert len(pet.get_tasks()) == 1
