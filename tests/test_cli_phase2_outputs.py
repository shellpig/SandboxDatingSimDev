"""Phase 2-A-0 CLI 輸出布局與防覆寫測試。"""

import pytest
from pathlib import Path
import yaml

from sandbox_dating_sim.schema.setup import SetupPackage
from sandbox_dating_sim.pipeline.setup_exporter import SetupPackageExporter


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_minimal() -> SetupPackage:
    with open(FIXTURES_DIR / "setup_minimal.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return SetupPackage(**data)


# ---------------------------------------------------------------------------
# Test 7: export 預設路徑
# ---------------------------------------------------------------------------

def test_export_default_path(tmp_path: Path):
    """測試 #7：CLI export setup 不給 --out 時寫入固定布局路徑。"""
    pkg = _load_minimal()
    exporter = SetupPackageExporter()
    filepath = exporter.write_file_default_path(pkg, outputs_root=tmp_path)

    world_id = pkg.world.world_id
    expected = tmp_path / world_id / "setup_package" / f"{world_id}_setup_package.md"
    assert filepath == expected
    assert filepath.exists()
    assert filepath.stat().st_size > 0


def test_export_default_path_creates_dirs(tmp_path: Path):
    """write_file_default_path 會自動建立不存在的目錄。"""
    pkg = _load_minimal()
    exporter = SetupPackageExporter()
    outputs_root = tmp_path / "deep" / "nested"
    filepath = exporter.write_file_default_path(pkg, outputs_root=outputs_root)
    assert filepath.exists()


# ---------------------------------------------------------------------------
# Test 8: 同名不覆寫
# ---------------------------------------------------------------------------

def test_export_no_overwrite(tmp_path: Path):
    """測試 #8：目標檔已存在時報錯，不覆寫。"""
    pkg = _load_minimal()
    exporter = SetupPackageExporter()

    # 第一次匯出
    filepath = exporter.write_file_default_path(pkg, outputs_root=tmp_path)
    original_content = filepath.read_text(encoding="utf-8")

    # 第二次應拋 FileExistsError
    with pytest.raises(FileExistsError):
        exporter.write_file_default_path(pkg, outputs_root=tmp_path)

    # 確認檔案內容未被修改
    assert filepath.read_text(encoding="utf-8") == original_content


def test_export_write_file_no_overwrite(tmp_path: Path):
    """write_file 直接指定目錄時，同名也防覆寫。"""
    pkg = _load_minimal()
    exporter = SetupPackageExporter()
    out_dir = tmp_path / "custom_out"

    filepath = exporter.write_file(pkg, out_dir)
    assert filepath.exists()

    with pytest.raises(FileExistsError):
        exporter.write_file(pkg, out_dir)


# ---------------------------------------------------------------------------
# Exporter: write_file 寫入內容正確性
# ---------------------------------------------------------------------------

def test_export_file_content(tmp_path: Path):
    """匯出的 MD 檔包含 YAML code block 且可被 parser 解析。"""
    from sandbox_dating_sim.pipeline.setup_parser import SetupPackageParser

    pkg = _load_minimal()
    exporter = SetupPackageExporter()
    filepath = exporter.write_file_default_path(pkg, outputs_root=tmp_path)

    content = filepath.read_text(encoding="utf-8")
    assert "```yaml" in content

    parser = SetupPackageParser()
    parsed = parser.parse_markdown(content)
    assert parsed.world.world_id == pkg.world.world_id


# ---------------------------------------------------------------------------
# CLI integration（typer CliRunner）
# ---------------------------------------------------------------------------

def test_cli_export_setup_default_path(tmp_path: Path):
    """CLI export-setup 不給 --out 時寫入 outputs/<world_id>/setup_package/ 。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app
    import os

    runner = CliRunner()
    input_yaml = str(FIXTURES_DIR / "setup_minimal.yaml")

    # 切到 tmp_path 讓 outputs/ 建在臨時目錄
    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["export-setup", input_yaml])
    finally:
        os.chdir(old_cwd)

    assert result.exit_code == 0, result.output
    world_id = "summer_city_2026"
    expected = tmp_path / "outputs" / world_id / "setup_package" / f"{world_id}_setup_package.md"
    assert expected.exists(), f"Expected file not found: {expected}\nCLI output: {result.output}"


def test_cli_export_setup_no_overwrite(tmp_path: Path):
    """CLI export-setup 對同名檔案報錯並以 exit code 1 退出。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app
    import os

    runner = CliRunner()
    input_yaml = str(FIXTURES_DIR / "setup_minimal.yaml")

    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        # 第一次 — 成功
        result1 = runner.invoke(app, ["export-setup", input_yaml])
        assert result1.exit_code == 0, result1.output

        # 第二次 — 應報錯
        result2 = runner.invoke(app, ["export-setup", input_yaml])
    finally:
        os.chdir(old_cwd)

    assert result2.exit_code == 1
    assert "已存在" in result2.output or "FileExistsError" in result2.output or "錯誤" in result2.output


def test_cli_export_setup_custom_out(tmp_path: Path):
    """CLI export-setup --out 指定目錄時正常輸出。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app

    runner = CliRunner()
    input_yaml = str(FIXTURES_DIR / "setup_minimal.yaml")
    out_dir = str(tmp_path / "custom")

    result = runner.invoke(app, ["export-setup", input_yaml, "--out", out_dir])
    assert result.exit_code == 0, result.output

    world_id = "summer_city_2026"
    expected = tmp_path / "custom" / f"{world_id}_setup_package.md"
    assert expected.exists()


def test_cli_export_setup_custom_out_no_overwrite(tmp_path: Path):
    """CLI export-setup --out 也防覆寫。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app

    runner = CliRunner()
    input_yaml = str(FIXTURES_DIR / "setup_minimal.yaml")
    out_dir = str(tmp_path / "custom")

    runner.invoke(app, ["export-setup", input_yaml, "--out", out_dir])
    result2 = runner.invoke(app, ["export-setup", input_yaml, "--out", out_dir])
    assert result2.exit_code == 1
