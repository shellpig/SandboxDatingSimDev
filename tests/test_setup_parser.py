import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError
from sandbox_dating_sim.schema.setup import SetupPackage
from sandbox_dating_sim.pipeline.setup_exporter import SetupPackageExporter
from sandbox_dating_sim.pipeline.setup_parser import SetupPackageParser
from sandbox_dating_sim.core.exceptions import MarkdownParseError

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def load_yaml(filename: str) -> SetupPackage:
    with open(FIXTURES_DIR / filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return SetupPackage(**data)

def test_parse_exported_markdown_roundtrip():
    """SetupPackage -> Markdown -> SetupPackage 後核心欄位一致。"""
    pkg_in = load_yaml("setup_minimal.yaml")
    exporter = SetupPackageExporter()
    md = exporter.to_markdown(pkg_in)
    
    parser = SetupPackageParser()
    pkg_out = parser.parse_markdown(md)
    
    assert pkg_out.world.world_id == pkg_in.world.world_id
    assert pkg_out.world.title == pkg_in.world.title
    assert pkg_out.protagonist.name == pkg_in.protagonist.name

def test_parse_rejects_missing_yaml_block():
    """沒有 yaml code block 時拋出 MarkdownParseError。"""
    md = "# Setup Package\n\nNo yaml here."
    parser = SetupPackageParser()
    with pytest.raises(MarkdownParseError, match="找不到 ```yaml 區塊"):
        parser.parse_markdown(md)

def test_parse_rejects_invalid_schema():
    """YAML 欄位不完整時 validation fail。"""
    md = "# Setup Package\n\n```yaml\nworld:\n  title: invalid\n```\n"
    parser = SetupPackageParser()
    with pytest.raises(ValidationError):
        parser.parse_markdown(md)

def test_roundtrip_preserves_nested_locations_and_schedule():
    """巢狀 locations 與 character schedule 在 roundtrip 後一致。"""
    pkg_in = load_yaml("setup_minimal.yaml")
    exporter = SetupPackageExporter()
    md = exporter.to_markdown(pkg_in)
    
    parser = SetupPackageParser()
    pkg_out = parser.parse_markdown(md)
    
    assert len(pkg_out.locations) == len(pkg_in.locations)
    assert pkg_out.locations[0].location_id == pkg_in.locations[0].location_id
    assert pkg_out.characters[0].schedule[0].schedule_id == pkg_in.characters[0].schedule[0].schedule_id
    assert pkg_out.characters[0].schedule[0].location_id == pkg_in.characters[0].schedule[0].location_id

def test_roundtrip_preserves_status_flag_lifecycle():
    """duration、clear_rule、permanent_reason 在 roundtrip 後一致。"""
    pkg_in = load_yaml("setup_minimal.yaml")
    exporter = SetupPackageExporter()
    md = exporter.to_markdown(pkg_in)
    
    parser = SetupPackageParser()
    pkg_out = parser.parse_markdown(md)
    
    status_in = pkg_in.status_flags[0]
    status_out = pkg_out.status_flags[0]
    assert status_out.duration.type == status_in.duration.type
    assert status_out.duration.value == status_in.duration.value
    assert status_out.clear_rule == status_in.clear_rule
    assert status_out.permanent_reason == status_in.permanent_reason

def test_roundtrip_preserves_asset_vocabularies_and_aliases():
    """asset vocabularies 與 alias tables 在 roundtrip 後一致。"""
    pkg_in = load_yaml("setup_minimal.yaml")
    exporter = SetupPackageExporter()
    md = exporter.to_markdown(pkg_in)
    
    parser = SetupPackageParser()
    pkg_out = parser.parse_markdown(md)
    
    assert pkg_out.asset_vocabularies == pkg_in.asset_vocabularies
    assert pkg_out.alias_tables == pkg_in.alias_tables
