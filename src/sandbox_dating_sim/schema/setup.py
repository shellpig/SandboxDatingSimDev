from typing import Any, Literal
from datetime import date
from pydantic import BaseModel, Field
from sandbox_dating_sim.schema.validation import ValidationReport

LocationType = Literal["container", "sub_location", "standalone"]
EmptyBehavior = Literal["hidden", "show_empty", "show_ambient_text", "allow_rest", "allow_wait"]
DayType = Literal["weekday", "weekend", "holiday", "specific_date", "any"]
TimeSlot = Literal["morning", "afternoon", "evening"]
SchedulePriority = Literal["critical", "route", "normal", "ambient"]
EventPriority = Literal["critical", "main", "route", "normal", "ambient"]
Gender = Literal["male", "female", "non_binary"]
Orientation = Literal["heterosexual", "homosexual", "bisexual", "pansexual"]
FlagType = Literal["boolean", "integer", "string", "enum"]
DurationType = Literal["time_slots", "days", "until_event", "until_cleared", "permanent"]
ClearRule = Literal["on_time_advance", "on_day_end", "on_rest", "on_item_used", "on_event_result", "on_location_visit", "manual_only"]

class World(BaseModel):
    world_id: str
    title: str
    start_date: date
    end_date: date
    time_slots: list[TimeSlot]
    total_days: int | None = None
    global_style: list[str] = []

class InitialStats(BaseModel):
    INT: int
    CHA: int
    STR: int
    MORAL: int
    Cash: int
    Debt: int = 0

class Protagonist(BaseModel):
    protagonist_id: str = "protagonist"
    name: str
    gender: Gender
    age: int
    occupation: str
    initial_stats: InitialStats
    personality: str
    secret: str | None = None

class Location(BaseModel):
    location_id: str
    name: str
    location_type: LocationType
    parent_location_id: str | None = None
    is_visitable: bool
    base_cost: int = 0
    available_time_slots: list[TimeSlot]
    tags: list[str] = []
    unlock_conditions: list[str] = []
    closed_conditions: list[str] = []
    map_priority: str = "normal"
    map_display_group: str | None = None
    default_npc_capacity: int = 0
    empty_behavior: EmptyBehavior = "show_empty"
    ambient_text: str | None = None

class ScheduleEntry(BaseModel):
    schedule_id: str
    day_type: DayType
    time_slot: TimeSlot
    location_id: str
    condition: list[str] = []
    priority: SchedulePriority = "normal"
    schedule_order: int

class AssetOption(BaseModel):
    id: str
    label: str

class Character(BaseModel):
    character_id: str
    display_name: str
    gender: Gender
    orientation: list[Orientation]
    role: str
    identity: str
    personality_tags: list[str]
    secret: str | None = None
    initial_favor: int = 0
    schedule: list[ScheduleEntry] = []
    allowed_emotions: list[AssetOption]
    allowed_costumes: list[AssetOption]
    allowed_positions: list[AssetOption]

class FlagDef(BaseModel):
    flag_id: str
    type: FlagType
    initial_value: bool | int | str
    description: str

class StatusDuration(BaseModel):
    type: DurationType
    value: int | None = None

class StatusFlag(BaseModel):
    status_id: str
    label: str
    target: str
    effect: list[dict[str, Any]]
    duration: StatusDuration
    clear_rule: list[ClearRule]
    description: str
    permanent_reason: str | None = None

class Ending(BaseModel):
    ending_id: str
    title: str
    ending_type: str
    target_character_id: str | None = None
    description: str
    required_flags: list[str] = []
    required_stats: list[str] = []
    forbidden_flags: list[str] = []
    priority: EventPriority = "normal"
    route_tags: list[str] = []

class SetupPackage(BaseModel):
    setup_package_version: str = "1.0"
    uiw_version: str = "1.2"
    target_game_spec_version: str = "1.2"
    world: World
    protagonist: Protagonist
    locations: list[Location]
    characters: list[Character]
    flags: list[FlagDef] = []
    status_flags: list[StatusFlag] = []
    endings: list[Ending] = []
    asset_vocabularies: dict = Field(default_factory=dict)
    alias_tables: dict = Field(default_factory=dict)
    validation_report: ValidationReport | None = None
