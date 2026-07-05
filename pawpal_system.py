from dataclasses import dataclass, field
from datetime import date, datetime, time as clock_time, timedelta
from enum import Enum, IntEnum
from typing import List, Optional


# Ordered low->high so Priority.HIGH sorts as the biggest value.
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# What kind of care task this is.
class TaskCategory(Enum):
    FEEDING = "feeding"
    CLEANING = "cleaning"
    QUALITY_TIME = "quality_time"


# How often a task recurs. ONCE never advances due_date after completion.
class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Maps a free-text time-of-day period to an approximate clock time,
# used by Task.schedule() to turn "morning"/"evening"/etc. into a real datetime.
PERIOD_TO_HOUR = {
    "morning": clock_time(8, 0),
    "afternoon": clock_time(13, 0),
    "evening": clock_time(18, 0),
    "night": clock_time(21, 0),
}

# Fixed-length recurrence intervals. MONTHLY is handled separately by
# _add_one_month() since months don't all have the same number of days.
FREQUENCY_TO_INTERVAL = {
    Frequency.DAILY: timedelta(days=1),
    Frequency.WEEKLY: timedelta(weeks=1),
}


def _add_one_month(d: date) -> date:
    # Roll over to the next month, wrapping the year at December.
    if d.month == 12:
        next_year, next_month = d.year + 1, 1
    else:
        next_year, next_month = d.year, d.month + 1

    # Clamp the day to the last valid day of the next month
    # (e.g. Jan 31 -> Feb 28/29, not an invalid Feb 31).
    if next_month == 12:
        first_of_following_month = date(next_year + 1, 1, 1)
    else:
        first_of_following_month = date(next_year, next_month + 1, 1)
    last_day_of_next_month = (first_of_following_month - timedelta(days=1)).day

    return date(next_year, next_month, min(d.day, last_day_of_next_month))


# A pet owner. Holds their pets and their scheduling preferences
# (e.g. preferred time-of-day periods) used by the Scheduler.
@dataclass
class Owner:
    owner_id: str
    name: str
    email: str
    preferences: List[str] = field(default_factory=list)
    pets: List["Pet"] = field(default_factory=list)

    def add_pet(self, pet: "Pet") -> None:
        """Register a pet with this owner, ignoring duplicates by pet_id."""
        # Skip if this pet_id is already registered, so re-adding is a no-op.
        if not any(existing.pet_id == pet.pet_id for existing in self.pets):
            self.pets.append(pet)

    def get_pets(self) -> list:
        """Return this owner's list of pets."""
        return self.pets

    def get_all_tasks(self) -> list:
        """Return every task across all of this owner's pets, flattened into one list."""
        # Flatten every pet's tasks into one list, e.g. for Scheduler.build_schedule().
        return [task for pet in self.pets for task in pet.get_tasks()]


# A single pet belonging to an Owner, with its own list of care tasks.
@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    age: int
    tasks: List["Task"] = field(default_factory=list)
    owner: Optional["Owner"] = field(default=None, repr=False, compare=False)

    def add_task(self, task: "Task") -> None:
        """Attach a task to this pet, linking it back via task.pet."""
        # Back-reference so a task always knows which pet it belongs to
        # (used by explain_plan() to label each line with the pet's name).
        task.pet = self
        self.tasks.append(task)

    def get_tasks(self) -> list:
        """Return this pet's list of tasks."""
        return self.tasks


# Base class for a single care task. Feeding/Cleaning/Pet_Quality_time
# extend this with their own type-specific attributes.
@dataclass
class Task:
    description: str
    due_date: date
    time: str
    status: str
    duration_minutes: int
    priority: Priority
    category: TaskCategory
    frequency: Frequency
    # Set by schedule(), not passed in at construction.
    scheduled_at: Optional[datetime] = field(default=None, init=False)
    # Set automatically by Pet.add_task(), not passed in at construction.
    pet: Optional["Pet"] = field(default=None, init=False, repr=False, compare=False)

    def complete(self) -> None:
        """Mark the task completed, rolling recurring tasks forward to their next due date."""
        self.status = "completed"
        # Recurring tasks roll forward to their next occurrence instead of
        # staying completed forever; ONCE tasks just stay completed.
        if self.frequency == Frequency.MONTHLY:
            self.due_date = _add_one_month(self.due_date)
            self.scheduled_at = None
            self.status = "pending"
        elif self.frequency in FREQUENCY_TO_INTERVAL:
            self.due_date += FREQUENCY_TO_INTERVAL[self.frequency]
            self.scheduled_at = None
            self.status = "pending"

    def is_due(self) -> bool:
        """Return True if the task's due date is today or earlier."""
        # Due today or earlier.
        return self.due_date <= date.today()

    def is_overdue(self) -> bool:
        """Return True if the task's due date is strictly in the past."""
        # Strictly in the past (today doesn't count as overdue).
        return self.due_date < date.today()

    def schedule(self) -> None:
        """Resolve the task's time-of-day period into a concrete datetime and mark it scheduled."""
        # Turn the free-text time period into a concrete datetime and mark
        # this task as scheduled.
        period = self.time.strip().lower()
        if period not in PERIOD_TO_HOUR:
            raise ValueError(f"Unknown time period: {self.time!r}")
        self.scheduled_at = datetime.combine(self.due_date, PERIOD_TO_HOUR[period])
        self.status = "scheduled"


# A feeding task, e.g. breakfast/dinner.
@dataclass
class Feeding(Task):
    food_type: str
    notes: str

    def get_summary(self) -> str:
        """Return the display label for this task type."""
        return "Feeding"

    def get_details(self) -> List[str]:
        """Return the food type and notes as display lines."""
        return [f"Food Type: {self.food_type}", f"Notes: {self.notes}"]


# A cleaning task. Can cover the pet itself (bathing/grooming) and/or its
# living quarters (litter box, cage, etc.), independently.
@dataclass
class Cleaning(Task):
    clean_pet: bool
    clean_living_quarters: bool
    notes: str
    bathing: Optional[bool] = None
    grooming: Optional[str] = None
    quarters_detail: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate that bathing/grooming/quarters_detail are only set when their flag is True."""
        # Enforce that pet-hygiene / quarters details are only set when the
        # matching clean_pet / clean_living_quarters flag says they apply.
        if not self.clean_pet and (self.bathing is not None or self.grooming is not None):
            raise ValueError("bathing/grooming can only be set when clean_pet is True")
        if not self.clean_living_quarters and self.quarters_detail is not None:
            raise ValueError("quarters_detail can only be set when clean_living_quarters is True")

    def cleaning_pet(self) -> bool:
        """Return True if this task covers cleaning the pet itself."""
        return self.clean_pet

    def cleaning_pet_living_quarters(self) -> bool:
        """Return True if this task covers cleaning the pet's living quarters."""
        return self.clean_living_quarters

    def get_summary(self) -> str:
        """Return the display label for this task type."""
        return "Cleaning"

    def get_details(self) -> List[str]:
        """Return the notes as a display line."""
        return [f"Notes: {self.notes}"]


# A bonding/enrichment task, e.g. playtime or an outing.
@dataclass
class Pet_Quality_time(Task):
    exercise: str
    play_time_w_toys: bool
    outing_with_pet: bool
    notes: str

    def get_summary(self) -> str:
        """Return the display label for this task type."""
        return "Pet Quality Time"

    def get_details(self) -> List[str]:
        """Return the notes as a display line."""
        return [f"Notes: {self.notes}"]


# Builds a daily task plan for an owner within a fixed time budget.
class Scheduler:
    def __init__(self, available_minutes: int):
        """Create a scheduler with a fixed daily time budget in minutes."""
        self.available_minutes = available_minutes

    def build_schedule(self, owner: "Owner") -> list:
        """Greedily pick the owner's highest-ranked due/overdue tasks that fit the time budget."""
        # Gather not-yet-completed tasks across every pet the owner has,
        # split into "overdue" and "due today" groups.
        all_tasks = owner.get_all_tasks()
        candidates = [ task for task in all_tasks if task.status != "completed" and task.is_due() and not task.is_overdue()]
        overdue_candidates = [ task for task in all_tasks if task.status != "completed" and task.is_overdue()]

        def _sort_key(task: "Task", owner: "Owner") -> tuple:
            """Rank a task by overdue status, then priority, then preferred-time match."""
            overdue_rank = 0 if task.is_overdue() else 1      # 0 sorts before 1 → overdue first
            priority_rank = -task.priority.value               # Priority is an IntEnum (HIGH=3) → negate so HIGH sorts first
            preference_rank = 0 if task.time in owner.preferences else 1  # preferred time period sorts first
            return (overdue_rank, priority_rank, preference_rank)

        # Overdue tasks always come first; within each group, higher priority
        # and preferred time-of-day slots are ranked ahead.
        all_candidates = sorted(
        overdue_candidates + candidates,
        key=lambda task: _sort_key(task, owner),
        )

        # Greedily fill the available time budget in ranked order, marking
        # each chosen task as scheduled.
        schedule = []
        remaining = self.available_minutes
        for candidate in all_candidates:
            if candidate.duration_minutes <= remaining:
                remaining -= candidate.duration_minutes
                candidate.schedule()
                schedule.append(candidate)
        return schedule

    # Time slots are shown in this order when present; any other value
    # (e.g. a custom slot) is appended afterwards in first-seen order.
    _TIME_SLOT_ORDER = ["morning", "afternoon", "evening", "night"]

    def explain_plan(self, schedule: list, owner: "Owner") -> str:
        """Render a scheduled task list as a human-readable plan grouped by time slot."""
        # Build a multi-line, human-readable block per scheduled task,
        # grouped by time slot, explaining why each task was chosen
        # (overdue / priority / preference match).
        grouped: dict = {}
        for task in schedule:
            grouped.setdefault(task.time, []).append(task)

        slots = [slot for slot in self._TIME_SLOT_ORDER if slot in grouped]
        slots += [slot for slot in grouped if slot not in slots]

        sections = []
        for slot in slots:
            lines = [slot.upper(), "-" * len(slot)]
            for task in grouped[slot]:
                reasons = []
                if task.is_overdue():
                    reasons.append("overdue")
                reasons.append(f"{task.priority.name} priority")
                if task.time in owner.preferences:
                    reasons.append(f"in your preferred {task.time} slot")
                pet_label = f"[{task.pet.name}] " if task.pet else ""
                lines.append(f"{pet_label}{task.get_summary()} ({task.priority.name})")
                lines.extend(f"    {detail}" for detail in task.get_details())
                lines.append(f"    Why: {', '.join(reasons)}")
                lines.append("")
            sections.append("\n".join(lines).rstrip())
        return "\n\n".join(sections)
