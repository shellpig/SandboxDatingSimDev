"""Phase 2 Event Blueprint Schema — Pydantic models."""

from typing import Literal

from pydantic import BaseModel, Field

from sandbox_dating_sim.schema.setup import FlagDef, TimeSlot

RepeatPolicy = Literal["once", "daily"]
BlueprintPriority = Literal["critical", "main", "route", "normal", "ambient"]


class BlueprintChoice(BaseModel):
    choice_id: str
    choice_label: str
    choice_intent: str
    result: list[str] = Field(min_length=1)


class ExpectedCharacterAsset(BaseModel):
    character_id: str
    costume: str
    emotion: str
    position: str


class ExpectedAssets(BaseModel):
    background: str | None = None
    bgm: str | None = None
    characters: list[ExpectedCharacterAsset] = Field(default_factory=list)


class BlueprintEvent(BaseModel):
    event_id: str
    title: str
    scene_summary: str
    location_id: str
    time_slot: TimeSlot
    priority: BlueprintPriority
    repeat_policy: RepeatPolicy = "once"
    route_tags: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    event_purpose: str
    cast: list[str] = Field(default_factory=list)
    expected_assets: ExpectedAssets
    choices: list[BlueprintChoice] = Field(min_length=1, max_length=4)
    time_cost: int = Field(gt=0)


class EventBlueprint(BaseModel):
    event_blueprint_version: str = "1.0"
    blueprint_id: str
    source_world_id: str
    source_setup_package: str
    target_game_spec_version: str = "1.2"
    initial_event_id: str
    events: list[BlueprintEvent] = Field(min_length=1)
    new_flags_proposed: list[FlagDef] = Field(default_factory=list)
