from dataclasses import dataclass, field
from datetime import date
from enum import Enum, IntEnum
from typing import List, Optional


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class TaskCategory(Enum):
    FEEDING = "feeding"
    CLEANING = "cleaning"
    QUALITY_TIME = "quality_time"


@dataclass
class Owner:
    owner_id: str
    name: str
    email: str
    preferences: List[str] = field(default_factory=list)
    pets: List["Pet"] = field(default_factory=list)

    def add_pet(self, pet: "Pet") -> None:
        pass

    def get_pets(self) -> list:
        pass


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    age: int
    tasks: List["Task"] = field(default_factory=list)
    owner: Optional["Owner"] = field(default=None, repr=False, compare=False)

    def add_task(self, task: "Task") -> None:
        pass

    def get_tasks(self) -> list:
        pass


@dataclass
class Task:
    description: str
    due_date: date
    status: str
    duration_minutes: int
    priority: Priority
    category: TaskCategory

    def complete(self) -> None:
        pass

    def is_due(self) -> bool:
        pass


@dataclass
class Feeding(Task):
    time: str
    food_type: str
    notes: str

    def schedule(self) -> None:
        pass

    def get_summary(self) -> str:
        pass


@dataclass
class Cleaning(Task):
    time: str
    bathing: bool
    grooming: str
    notes: str

    def cleaning_pet(self) -> bool:
        pass

    def cleaning_pet_living_quarters(self) -> bool:
        pass

    def schedule(self) -> None:
        pass

    def get_summary(self) -> str:
        pass


@dataclass
class Pet_Quality_time(Task):
    time: str
    exercise: str
    play_time_w_toys: bool
    outing_with_pet: bool
    notes: str

    def schedule(self) -> None:
        pass

    def get_summary(self) -> str:
        pass


class Scheduler:
    def __init__(self, available_minutes: int):
        self.available_minutes = available_minutes

    def build_schedule(self, owner: "Owner", pet: "Pet") -> list:
        pass

    def explain_plan(self, schedule: list) -> str:
        pass
