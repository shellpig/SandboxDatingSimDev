import pytest
from pathlib import Path
from typer.testing import CliRunner

from sandbox_dating_sim.cli import app
from sandbox_dating_sim.pipeline.setup_parser import SetupPackageParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"
runner = CliRunner()


def test_cli_export_setup_creates_file(tmp_path):
    """CLI 可從 fixture YAML 產出 Setup Package MD。"""
    result = runner.invoke(app, [
        "export-setup",
        str(FIXTURES_DIR / "setup_minimal.yaml"),
        "--out", str(tmp_path),
    ])
    assert result.exit_code == 0, result.output
    files = list(tmp_path.glob("*_setup_package.md"))
    assert len(files) == 1
    assert files[0].name == "summer_city_2026_setup_package.md"


def test_cli_export_setup_output_can_parse(tmp_path):
    """CLI 產出的 MD 可被 SetupPackageParser 讀回。"""
    runner.invoke(app, [
        "export-setup",
        str(FIXTURES_DIR / "setup_minimal.yaml"),
        "--out", str(tmp_path),
    ])
    md_file = tmp_path / "summer_city_2026_setup_package.md"
    parser = SetupPackageParser()
    pkg = parser.parse_file(md_file)
    assert pkg.world.world_id == "summer_city_2026"
    assert pkg.uiw_version == "1.2"
    assert pkg.validation_report is not None


def test_cli_invalid_input_returns_nonzero(tmp_path):
    """不合法 input 應回傳非 0。"""
    result = runner.invoke(app, [
        "export-setup",
        str(tmp_path / "nonexistent.yaml"),
        "--out", str(tmp_path),
    ])
    assert result.exit_code != 0


def test_cli_invalid_yaml_returns_nonzero(tmp_path):
    """不合法 YAML 內容應回傳非 0。"""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("world:\n  title: incomplete\n", encoding="utf-8")
    result = runner.invoke(app, [
        "export-setup",
        str(bad_yaml),
        "--out", str(tmp_path),
    ])
    assert result.exit_code != 0
