"""Phase 2-C Blueprint Parser 測試（#1-#7）。"""

import pytest
from pathlib import Path
from sandbox_dating_sim.pipeline.blueprint_parser import BlueprintParser, BlueprintParseError
from sandbox_dating_sim.schema.blueprint import EventBlueprint

FIXTURES = Path(__file__).parent / "fixtures"
parser = BlueprintParser()

MINIMAL_MD = (FIXTURES / "blueprint_minimal.md").read_text(encoding="utf-8")


def test_parse_single_yaml_block():
    """#1: 單一 yaml block → EventBlueprint。"""
    bp = parser.parse_markdown(MINIMAL_MD)
    assert isinstance(bp, EventBlueprint)
    assert bp.blueprint_id == "summer_city_2026_event_blueprint"


def test_parse_yml_alias():
    """#2: yml block alias 也可解析。"""
    md = MINIMAL_MD.replace("```yaml", "```yml", 1)
    bp = parser.parse_markdown(md)
    assert isinstance(bp, EventBlueprint)


def test_no_yaml_block():
    """#3: 無 YAML block → BlueprintParseError。"""
    with pytest.raises(BlueprintParseError, match="找不到"):
        parser.parse_file(FIXTURES / "blueprint_invalid_no_yaml.md")


def test_multi_yaml_block():
    """#4: 多個 YAML block → BlueprintParseError。"""
    with pytest.raises(BlueprintParseError, match="個 YAML block"):
        parser.parse_file(FIXTURES / "blueprint_invalid_multi_yaml.md")


def test_malformed_yaml():
    """#5: YAML 語法錯 → BlueprintParseError。"""
    md = "# Test\n```yaml\n: bad: yaml: here:\n  - [unclosed\n```\n"
    with pytest.raises(BlueprintParseError, match="YAML 語法錯誤"):
        parser.parse_markdown(md)


def test_yaml_root_not_mapping():
    """#6: YAML root 非 mapping（list）→ BlueprintParseError。"""
    md = "# Test\n```yaml\n- item_one\n- item_two\n```\n"
    with pytest.raises(BlueprintParseError, match="mapping"):
        parser.parse_markdown(md)


def test_external_markdown_ignored():
    """#7: YAML block 外的 Markdown 廢話被忽略，仍可 parse。"""
    extra = "AI generated text here.\nSome extra words.\n\n"
    md = extra + MINIMAL_MD + "\nMore text after."
    bp = parser.parse_markdown(md)
    assert isinstance(bp, EventBlueprint)


def test_parse_file():
    """parse_file 從路徑讀取並解析。"""
    bp = parser.parse_file(FIXTURES / "blueprint_minimal.md")
    assert isinstance(bp, EventBlueprint)
