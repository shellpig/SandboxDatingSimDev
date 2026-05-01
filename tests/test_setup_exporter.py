import pytest
import yaml
from pathlib import Path
from sandbox_dating_sim.schema.setup import SetupPackage
from sandbox_dating_sim.pipeline.setup_exporter import SetupPackageExporter

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def load_yaml(filename: str) -> SetupPackage:
    with open(FIXTURES_DIR / filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return SetupPackage(**data)

def test_exporter_outputs_markdown_with_yaml_block():
    """輸出包含 # Setup Package 與單一 yaml code block。"""
    pkg = load_yaml("setup_minimal.yaml")
    exporter = SetupPackageExporter()
    md = exporter.to_markdown(pkg)
    assert "# Setup Package: 夏日債務街" in md
    assert "```yaml" in md
    assert md.count("```yaml") == 1

def test_exporter_includes_validation_report():
    """輸出 YAML 包含 validation_report。"""
    pkg = load_yaml("setup_minimal.yaml")
    exporter = SetupPackageExporter()
    md = exporter.to_markdown(pkg)
    assert "validation_report:" in md
    assert "status: passed" in md

def test_exporter_calculates_total_days():
    """total_days 如果沒填，應自動計算"""
    pkg = load_yaml("setup_minimal.yaml")
    pkg.world.total_days = None
    exporter = SetupPackageExporter()
    md = exporter.to_markdown(pkg)
    assert "total_days: 30" in md

def test_exporter_writes_uiw_version_1_2():
    """輸出 YAML 的 uiw_version 必須是 1.2。"""
    pkg = load_yaml("setup_minimal.yaml")
    exporter = SetupPackageExporter()
    md = exporter.to_markdown(pkg)
    assert "uiw_version: '1.2'" in md

def test_write_file_uses_world_id_filename(tmp_path):
    """輸出檔名為 <world_id>_setup_package.md。"""
    pkg = load_yaml("setup_minimal.yaml")
    exporter = SetupPackageExporter()
    path = exporter.write_file(pkg, tmp_path)
    assert path.name == "summer_city_2026_setup_package.md"
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "# Setup Package: 夏日債務街" in content

def test_exporter_preserves_chinese_labels():
    """中文 label 在 YAML 中保留，canonical ID 不被中文取代。"""
    pkg = load_yaml("setup_minimal.yaml")
    exporter = SetupPackageExporter()
    md = exporter.to_markdown(pkg)
    assert "label: 平常" in md


# ─── 1-G-3 Tests ────────────────────────────────────────────────────────────

def test_exporter_outputs_semantic_choice_id_and_label():
    """SemanticChoice 語意型欄位輸出包含 id 與中文 label。"""
    pkg = load_yaml("setup_minimal.yaml")
    exporter = SetupPackageExporter()
    md = exporter.to_markdown(pkg)
    # protagonist.occupation 應輸出 id + label
    assert "id: student" in md
    assert "label: 學生" in md
    # world.global_style 應輸出 id + label
    assert "id: urban_romance" in md
    assert "label: 都市戀愛" in md
    # character personality_tags 應輸出 id + label
    assert "id: guarded" in md
    assert "label: 戒心重" in md
