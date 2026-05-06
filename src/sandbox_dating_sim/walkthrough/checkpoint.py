import yaml
from datetime import datetime, timezone
from pydantic import BaseModel

from sandbox_dating_sim.walkthrough.blueprint_walkthrough import WalkthroughState, HistoryEntry

class Checkpoint(BaseModel):
    checkpoint_version: str = "1.0"
    checkpoint_id: str
    label: str | None = None
    source_world_id: str
    blueprint_id: str
    created_at: str
    state: WalkthroughState
    history: list[HistoryEntry]

def make_checkpoint(state: WalkthroughState, history: list[HistoryEntry], source_world_id: str, blueprint_id: str, label: str | None = None) -> Checkpoint:
    now = datetime.now(timezone.utc).astimezone()
    ts = now.strftime("%Y%m%d_%H%M%S")
    return Checkpoint(
        checkpoint_id=f"cp_{ts}",
        label=label,
        source_world_id=source_world_id,
        blueprint_id=blueprint_id,
        created_at=now.isoformat(timespec='seconds'),
        state=state,
        history=history
    )

def dump_checkpoint(cp: Checkpoint) -> str:
    # Serialize Checkpoint using model_dump
    d = cp.model_dump(mode="json", exclude_none=True)
    
    # Custom format active_statuses nested dict to dict[str, dict] which YAML can dump
    # pydantic model_dump handles it, but let's ensure it's clean
    return yaml.safe_dump(d, allow_unicode=True, sort_keys=False, default_flow_style=False)

def load_checkpoint(yaml_content: str) -> Checkpoint:
    d = yaml.safe_load(yaml_content)
    return Checkpoint.model_validate(d)
