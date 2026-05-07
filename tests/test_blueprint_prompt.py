"""Phase 2-B Blueprint Prompt Builder 測試。

必測項目 #1-#12（依測試指南）。
"""

import os
import pytest
from pathlib import Path

from sandbox_dating_sim.prompts.blueprint_prompt import (
    build_event_blueprint_prompt,
    write_prompt_file,
    prompt_output_path,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SETUP_MD = (FIXTURES_DIR / "blueprint_minimal.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# #1: 回傳 Markdown prompt，含章節標題
# ---------------------------------------------------------------------------

def test_returns_markdown_with_sections():
    """#1: build_event_blueprint_prompt 回傳 str，含章節 heading。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD)
    assert isinstance(prompt, str)
    assert "# Event Blueprint Generation Instructions" in prompt
    assert "## 1. Your Task" in prompt
    assert "## 2. Output Format" in prompt
    assert "## 10. Scope" in prompt
    assert "## 11. Setup Package" in prompt
    assert "## 12. Silent Final Check" in prompt


# ---------------------------------------------------------------------------
# #2: 含 output format 說明（exactly one YAML code block）
# ---------------------------------------------------------------------------

def test_output_format_mentions_yaml_block():
    """#2: prompt 明確要求 exactly one YAML code block。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD)
    assert "YAML" in prompt
    assert "one" in prompt.lower() or "一個" in prompt or "exactly" in prompt.lower()
    assert "```yaml" in prompt or "yaml" in prompt.lower()


# ---------------------------------------------------------------------------
# #3: 含 schema 欄位說明
# ---------------------------------------------------------------------------

def test_contains_required_schema_fields():
    """#3: prompt 包含 blueprint_id、source_world_id、initial_event_id、events、new_flags_proposed。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD)
    for field in ("blueprint_id", "source_world_id", "initial_event_id", "events", "new_flags_proposed"):
        assert field in prompt, f"Missing schema field: {field}"


# ---------------------------------------------------------------------------
# #4: 含 DSL 白名單，且禁止 item.* / inventory.*
# ---------------------------------------------------------------------------

def test_contains_dsl_whitelist_and_restrictions():
    """#4: condition/result DSL 列出，且禁止 item.* / inventory.*。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD)
    # DSL 白名單關鍵字
    assert "goto:" in prompt
    assert "ending:" in prompt
    assert "flag." in prompt
    assert "stat." in prompt
    # 明確禁止
    assert "item.*" in prompt or "item." in prompt
    assert "inventory.*" in prompt or "inventory." in prompt
    assert "禁止" in prompt or "❌" in prompt


# ---------------------------------------------------------------------------
# #5: 含 initial event 規則（protagonist_home + 第一個 time slot）
# ---------------------------------------------------------------------------

def test_contains_initial_event_rules():
    """#5: prompt 包含 protagonist_home、第一個 time slot 限制、不可要求 flag/stat 條件。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD)
    assert "protagonist_home" in prompt
    # 第一個 time slot 規則
    assert "time_slot" in prompt
    # 不可要求 flag / stat / favor / status
    assert "flag" in prompt
    assert "stat" in prompt
    assert "favor" in prompt or "status" in prompt


# ---------------------------------------------------------------------------
# #6: 含 ending 規則（fallback_ending、ending: result）
# ---------------------------------------------------------------------------

def test_contains_ending_rules():
    """#6: 每個 ending 必須被 ending: 引用，且需要 fallback_ending event。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD)
    assert "ending:" in prompt
    assert "fallback_ending" in prompt

def test_contains_character_boundary_rules():
    """Prompt 明確禁止 AI 新增 canonical characters，但允許純文字背景 NPC。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD)
    assert "不可新增 canonical characters" in prompt
    assert "SetupPackage 已存在的 character_id" in prompt
    assert "背景 NPC" in prompt
    assert "不可進入 cast" in prompt


# ---------------------------------------------------------------------------
# #7: 含 status 規則
# ---------------------------------------------------------------------------

def test_contains_status_rules():
    """#7: 不依賴 clear_rule；status 變更需 explicit result。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD)
    assert "clear_rule" in prompt
    assert "status" in prompt
    # 必須說明不依賴 clear_rule
    assert "不依賴" in prompt or "不可依賴" in prompt or "不可" in prompt


# ---------------------------------------------------------------------------
# #8: minimal_complete scope
# ---------------------------------------------------------------------------

def test_minimal_complete_scope():
    """#8: scope=minimal_complete prompt 要求最小完整事件網並 cover all endings。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD, scope="minimal_complete")
    assert "minimal_complete" in prompt
    assert "ending" in prompt.lower()
    # 要求 cover all endings
    assert "all endings" in prompt.lower() or "所有" in prompt


# ---------------------------------------------------------------------------
# #9: ai_decides scope
# ---------------------------------------------------------------------------

def test_ai_decides_scope():
    """#9: scope=ai_decides prompt 要求 AI 自決事件數但 cover all endings。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD, scope="ai_decides")
    assert "ai_decides" in prompt
    assert "all endings" in prompt.lower() or "所有" in prompt


# ---------------------------------------------------------------------------
# #10: custom scope（含 target_event_count + custom_scope notes）
# ---------------------------------------------------------------------------

def test_custom_scope_with_count_and_notes():
    """#10: custom scope prompt 含 target event count / custom notes，仍要求 cover all endings。"""
    prompt = build_event_blueprint_prompt(
        SAMPLE_SETUP_MD,
        scope="custom",
        target_event_count=12,
        custom_scope="重點在蘇菲路線",
    )
    assert "custom" in prompt
    assert "12" in prompt
    assert "蘇菲路線" in prompt
    assert "all endings" in prompt.lower() or "所有" in prompt


def test_custom_scope_without_count():
    """#10: custom scope 無 count 也合法。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD, scope="custom")
    assert "custom" in prompt
    assert "所有" in prompt or "all endings" in prompt.lower()


# ---------------------------------------------------------------------------
# Setup Package 內容被嵌入 prompt
# ---------------------------------------------------------------------------

def test_setup_package_embedded():
    """setup_package_markdown 的內容會出現在 prompt 中。"""
    prompt = build_event_blueprint_prompt(SAMPLE_SETUP_MD)
    # blueprint_minimal.md 的 world_id 應出現在 prompt 裡
    assert "summer_city_2026" in prompt


# ---------------------------------------------------------------------------
# write_prompt_file - 輸出路徑
# ---------------------------------------------------------------------------

def test_prompt_output_path():
    """prompt_output_path 回傳正確結構路徑。"""
    path = prompt_output_path(Path("/base/outputs"), "my_world")
    assert path == Path("/base/outputs/my_world/prompts/my_world_event_blueprint_prompt.md")


def test_write_prompt_file_creates_file(tmp_path: Path):
    """write_prompt_file 建立正確路徑的檔案。"""
    filepath = write_prompt_file(tmp_path, "test_world", "prompt content")
    expected = tmp_path / "test_world" / "prompts" / "test_world_event_blueprint_prompt.md"
    assert filepath == expected
    assert filepath.exists()
    assert filepath.read_text(encoding="utf-8") == "prompt content"


def test_write_prompt_file_no_overwrite(tmp_path: Path):
    """write_prompt_file 同名報 FileExistsError。"""
    write_prompt_file(tmp_path, "test_world", "first")
    with pytest.raises(FileExistsError):
        write_prompt_file(tmp_path, "test_world", "second")


# ---------------------------------------------------------------------------
# #11 & #12: CLI 互動流程（mock stdin）
# ---------------------------------------------------------------------------

def _setup_fake_outputs(tmp_path: Path, world_id: str = "summer_city_2026") -> Path:
    """在 tmp_path/outputs/ 建立假 setup_package 目錄與 MD 檔。"""
    setup_dir = tmp_path / "outputs" / world_id / "setup_package"
    setup_dir.mkdir(parents=True)
    setup_file = setup_dir / f"{world_id}_setup_package.md"
    setup_file.write_text(SAMPLE_SETUP_MD, encoding="utf-8")
    return tmp_path / "outputs"


def test_cli_build_blueprint_prompt_minimal_complete(tmp_path: Path):
    """#11: mock input 選 world/setup/scope=minimal_complete，輸出 prompt MD。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app

    outputs_root = _setup_fake_outputs(tmp_path)
    world_id = "summer_city_2026"

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["build-blueprint-prompt", "--outputs-root", str(outputs_root)],
        input="1\n1\n1\n",  # world=1, setup=1, scope=1(minimal_complete)
    )
    assert result.exit_code == 0, result.output

    expected = outputs_root / world_id / "prompts" / f"{world_id}_event_blueprint_prompt.md"
    assert expected.exists(), f"Expected file not found\nCLI output: {result.output}"
    content = expected.read_text(encoding="utf-8")
    assert "Event Blueprint Generation Instructions" in content


def test_cli_build_blueprint_prompt_ai_decides(tmp_path: Path):
    """#11: scope=ai_decides 時 prompt 正確產生。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app

    outputs_root = _setup_fake_outputs(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["build-blueprint-prompt", "--outputs-root", str(outputs_root)],
        input="1\n1\n2\n",  # scope=2(ai_decides)
    )
    assert result.exit_code == 0, result.output


def test_cli_build_blueprint_prompt_custom_scope(tmp_path: Path):
    """#11: scope=custom，含 event count 與 notes。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app

    outputs_root = _setup_fake_outputs(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["build-blueprint-prompt", "--outputs-root", str(outputs_root)],
        input="1\n1\n3\n8\n測試說明\n",  # scope=3, count=8, notes=測試說明
    )
    assert result.exit_code == 0, result.output
    world_id = "summer_city_2026"
    prompt_file = outputs_root / world_id / "prompts" / f"{world_id}_event_blueprint_prompt.md"
    assert prompt_file.exists()
    content = prompt_file.read_text(encoding="utf-8")
    assert "8" in content
    assert "測試說明" in content


def test_cli_build_blueprint_prompt_no_overwrite(tmp_path: Path):
    """#12: 同名 prompt 存在時 CLI 報錯，exit code 1，檔案不覆寫。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app

    outputs_root = _setup_fake_outputs(tmp_path)
    runner = CliRunner()
    inputs = "1\n1\n1\n"

    # 第一次 — 成功
    result1 = runner.invoke(
        app,
        ["build-blueprint-prompt", "--outputs-root", str(outputs_root)],
        input=inputs,
    )
    assert result1.exit_code == 0, result1.output

    world_id = "summer_city_2026"
    prompt_file = outputs_root / world_id / "prompts" / f"{world_id}_event_blueprint_prompt.md"
    original_content = prompt_file.read_text(encoding="utf-8")

    # 第二次 — 應報錯
    result2 = runner.invoke(
        app,
        ["build-blueprint-prompt", "--outputs-root", str(outputs_root)],
        input=inputs,
    )
    assert result2.exit_code == 1
    assert "已存在" in result2.output or "錯誤" in result2.output
    # 內容不被修改
    assert prompt_file.read_text(encoding="utf-8") == original_content


def test_cli_no_outputs_dir(tmp_path: Path):
    """outputs 目錄不存在時 CLI 報錯。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["build-blueprint-prompt", "--outputs-root", str(tmp_path / "nonexistent")],
        input="1\n",
    )
    assert result.exit_code == 1


def test_cli_no_worlds(tmp_path: Path):
    """outputs 目錄存在但無任何 world 時 CLI 報錯。"""
    from typer.testing import CliRunner
    from sandbox_dating_sim.cli import app

    (tmp_path / "outputs").mkdir()
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["build-blueprint-prompt", "--outputs-root", str(tmp_path / "outputs")],
        input="1\n",
    )
    assert result.exit_code == 1
