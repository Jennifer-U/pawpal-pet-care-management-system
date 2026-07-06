from dataclasses import dataclass, field, replace
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


def _resolve_period_hour(period: str) -> clock_time:
    """Resolve a free-text time-of-day period to its mapped clock time.

    Args:
        period: A time-of-day label such as "morning" (case and surrounding
            whitespace are normalized before lookup).

    Returns:
        The clock time PERIOD_TO_HOUR maps the normalized period to.

    Raises:
        ValueError: If the normalized period isn't a recognized key.
    """
    normalized = period.strip().lower()
    if normalized not in PERIOD_TO_HOUR:
        raise ValueError(f"Unknown time period: {period!r}")
    return PERIOD_TO_HOUR[normalized]


def _add_one_month(d: date) -> date:
    """Return the date one calendar month after d, clamping to the target month's last valid day.

    Args:
        d: The date to advance.

    Returns:
        A date in the following month. If d.day exceeds the number of days
        in that month (e.g. Jan 31 -> Feb), the day is clamped to the last
        valid day of the target month rather than overflowing into March.
    """
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

    def _next_due_date(self) -> Optional[date]:
        """Compute this task's next due date based on its recurrence frequency.

        Returns:
            The next due date for DAILY/WEEKLY tasks (advanced by a fixed
            timedelta) or MONTHLY tasks (advanced calendar-aware via
            _add_one_month()). None for ONCE tasks, which don't recur.
        """
        # DAILY/WEEKLY advance by a fixed timedelta; MONTHLY needs the
        # calendar-aware _add_one_month() since months vary in length.
        if self.frequency == Frequency.MONTHLY:
            return _add_one_month(self.due_date)
        if self.frequency in FREQUENCY_TO_INTERVAL:
            return self.due_date + FREQUENCY_TO_INTERVAL[self.frequency]
        return None

    def complete(self) -> Optional["Task"]:
        """Mark this task completed and spawn its next occurrence if it recurs.

        This task's own status becomes "completed" and its due_date is left
        untouched, preserving it as a historical record. If the frequency
        recurs (DAILY/WEEKLY/MONTHLY), a new Task of the same subclass is
        built via dataclasses.replace() with the next due date and
        status="pending", attached to the same pet (if any), and returned.

        Returns:
            The newly created next-occurrence Task, or None if this task's
            frequency is ONCE.
        """
        self.status = "completed"

        next_due_date = self._next_due_date()
        if next_due_date is None:
            return None

        # dataclasses.replace() builds a new instance of this same subclass
        # (Feeding/Cleaning/Pet_Quality_time) copying every init field, then
        # overrides due_date/status. scheduled_at and pet are init=False, so
        # the copy gets fresh defaults (unscheduled, unattached) rather than
        # inheriting this task's scheduled_at/pet.
        next_task = replace(self, due_date=next_due_date, status="pending")
        if self.pet is not None:
            self.pet.add_task(next_task)
        return next_task

    def is_due(self) -> bool:
        """Return True if the task's due date is today or earlier."""
        # Due today or earlier.
        return self.due_date <= date.today()

    def is_overdue(self) -> bool:
        """Return True if the task's due date is strictly in the past."""
        # Strictly in the past (today doesn't count as overdue).
        return self.due_date < date.today()

    def _resolve_scheduled_datetime(self) -> datetime:
        """Resolve this task's time-of-day period into a concrete datetime, without mutating state."""
        return datetime.combine(self.due_date, _resolve_period_hour(self.time))

    def schedule(self) -> None:
        """Resolve the task's time-of-day period into a concrete datetime and mark it scheduled."""
        self.scheduled_at = self._resolve_scheduled_datetime()
        self.status = "scheduled"

    @property
    def ends_at(self) -> Optional[datetime]:
        """Return when this task ends, or None if it hasn't been scheduled yet."""
        if self.scheduled_at is None:
            return None
        return self.scheduled_at + timedelta(minutes=self.duration_minutes)


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
        # Tasks the last build_schedule() call skipped because they'd overlap
        # another already-scheduled task's time window (same pet or not —
        # the owner can only be doing one task at a time).
        self.last_conflicts: list = []
        # Tasks the last build_schedule() call skipped because they didn't
        # fit in the remaining time budget.
        self.last_skipped_over_budget: list = []

    def sort_by_time(self, tasks: list) -> list:
        """Sort tasks chronologically by their time-of-day period.

        Args:
            tasks: Tasks to sort; each must have a `time` recognized by
                PERIOD_TO_HOUR.

        Returns:
            A new list ordered by resolved clock time (morning -> afternoon
            -> evening -> night), using _resolve_period_hour() as the key.
        """
        return sorted(tasks, key=lambda task: _resolve_period_hour(task.time))

    def filter_tasks(self, tasks: list, status: Optional[str] = None, pet_name: Optional[str] = None) -> list:
        """Filter tasks by status and/or owning pet's name.

        Args:
            tasks: Tasks to filter.
            status: If given, keep only tasks with this exact status.
            pet_name: If given, keep only tasks whose pet's name matches,
                case-insensitively.

        Returns:
            A new list of tasks matching every filter provided. Returns all
            input tasks unchanged if neither filter is given.
        """
        filtered = tasks
        if status is not None:
            filtered = [task for task in filtered if task.status == status]
        if pet_name is not None:
            filtered = [
                task for task in filtered
                if task.pet is not None and task.pet.name.strip().lower() == pet_name.strip().lower()
            ]
        return filtered

    def build_schedule(self, owner: "Owner") -> list:
        """Greedily build a same-day task schedule within the available time budget.

        Algorithm:
            1. Collect every not-yet-completed task across the owner's pets
               that is due today or overdue.
            2. Rank them by (overdue first, then priority high-to-low, then
               preferred time-of-day match).
            3. Walk the ranked list, accepting each candidate unless it
               would exceed the remaining minutes or its time window
               overlaps a task already accepted — the owner can only do one
               task at a time, regardless of which pet it's for.

        Args:
            owner: The owner whose pets' tasks should be scheduled.

        Returns:
            The accepted tasks, each marked via schedule() and sorted
            chronologically via sort_by_time(). Tasks skipped for budget or
            time-conflict reasons are recorded on self.last_skipped_over_budget
            and self.last_conflicts respectively (reset on every call, not
            accumulated across calls).
        """
        # Gather not-yet-completed tasks across every pet the owner has that
        # are due today or overdue (is_due() covers both: due_date <= today).
        eligible = [task for task in owner.get_all_tasks() if task.status != "completed" and task.is_due()]

        def _sort_key(task: "Task") -> tuple:
            """Rank a task by overdue status, then priority, then preferred-time match."""
            overdue_rank = 0 if task.is_overdue() else 1      # 0 sorts before 1 → overdue first
            priority_rank = -task.priority.value               # Priority is an IntEnum (HIGH=3) → negate so HIGH sorts first
            preference_rank = 0 if task.time in owner.preferences else 1  # preferred time period sorts first
            return (overdue_rank, priority_rank, preference_rank)

        # Overdue tasks always come first; within each group, higher priority
        # and preferred time-of-day slots are ranked ahead.
        all_candidates = sorted(eligible, key=_sort_key)

        # Greedily fill the available time budget in ranked order, marking
        # each chosen task as scheduled. The owner can only be doing one
        # task at a time, so a candidate that would overlap a task already
        # scheduled for ANY pet (not just the same one) is skipped, recorded
        # in last_conflicts, rather than double-booking the owner.
        schedule = []
        self.last_conflicts = []
        self.last_skipped_over_budget = []
        remaining = self.available_minutes
        accepted: List[Task] = []
        for candidate in all_candidates:
            if candidate.duration_minutes > remaining:
                self.last_skipped_over_budget.append(candidate)
                continue

            start = candidate._resolve_scheduled_datetime()
            end = start + timedelta(minutes=candidate.duration_minutes)

            if any(self._intervals_overlap(start, end, task.scheduled_at, task.ends_at) for task in accepted):
                self.last_conflicts.append(candidate)
                continue

            remaining -= candidate.duration_minutes
            candidate.schedule()
            accepted.append(candidate)
            schedule.append(candidate)
        return self.sort_by_time(schedule)

    @staticmethod
    def _intervals_overlap(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
        """Return True if time window [start_a, end_a) overlaps [start_b, end_b)."""
        return start_a < end_b and start_b < end_a

    def detect_conflicts(self, tasks: list) -> list:
        """Find every pair of tasks whose resolved time windows overlap.

        Unlike build_schedule()'s incremental conflict check, this inspects
        an arbitrary list of tasks directly (they don't need to already be
        scheduled) and compares every pair once — an O(n^2) scan, fine for
        a personal task list but not meant to scale to a very large one.

        Args:
            tasks: Tasks to check, same pet or different pets alike. Each
                is resolved to a start/end time via its scheduled_at if
                already scheduled, or by resolving its time-of-day period
                otherwise.

        Returns:
            A list of (task_a, task_b) tuples for every overlapping pair,
            in the order the pairs were found.
        """
        resolved = [
            (task, task.scheduled_at or task._resolve_scheduled_datetime())
            for task in tasks
        ]
        conflicts = []
        for i, (task_a, start_a) in enumerate(resolved):
            end_a = start_a + timedelta(minutes=task_a.duration_minutes)
            for task_b, start_b in resolved[i + 1:]:
                end_b = start_b + timedelta(minutes=task_b.duration_minutes)
                if self._intervals_overlap(start_a, end_a, start_b, end_b):
                    conflicts.append((task_a, task_b))
        return conflicts

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

        if self.last_conflicts:
            lines = ["SKIPPED (TIME CONFLICT)", "-" * 23]
            for task in self.last_conflicts:
                pet_label = f"[{task.pet.name}] " if task.pet else ""
                lines.append(
                    f"{pet_label}{task.get_summary()} ({task.priority.name}) "
                    f"overlaps another already-scheduled {task.time} task"
                )
            sections.append("\n".join(lines))

        return "\n\n".join(sections)
