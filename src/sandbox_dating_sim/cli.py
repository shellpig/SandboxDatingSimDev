"""CLI for Sandbox Dating Sim Dev tools."""

from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel

from sandbox_dating_sim.schema.setup import SetupPackage
from sandbox_dating_sim.pipeline.setup_exporter import SetupPackageExporter

app = typer.Typer()
console = Console()


@app.callback()
def main() -> None:
    """Sandbox Dating Sim Dev CLI"""


@app.command("export-setup")
def export_setup(
    input_yaml: Path = typer.Argument(..., help="輸入的 YAML 初始設定檔路徑。"),
    out: Path = typer.Option(Path("examples"), "--out", help="輸出目錄。"),
) -> None:
    """
    讀取 YAML 初始設定，驗證後輸出 Setup Package MD。
    """
    if not input_yaml.exists():
        console.print(f"[red]錯誤：找不到檔案 {input_yaml}[/red]")
        raise typer.Exit(code=1)

    try:
        with open(input_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        console.print(f"[red]錯誤：YAML 解析失敗：{e}[/red]")
        raise typer.Exit(code=1)

    try:
        package = SetupPackage(**data)
    except Exception as e:
        console.print(f"[red]錯誤：Schema 驗證失敗：{e}[/red]")
        raise typer.Exit(code=1)

    exporter = SetupPackageExporter()
    filepath = exporter.write_file(package, out)

    # 顯示驗證結果
    report = exporter.linter.validate(package)
    if report.status == "passed":
        console.print(Panel(
            f"[green]驗證通過[/green]\n輸出：{filepath}",
            title="Setup Package Export",
        ))
    else:
        console.print(Panel(
            f"[yellow]驗證完成（有問題）[/yellow]\n輸出：{filepath}\n問題數：{len(report.issues)}",
            title="Setup Package Export",
        ))
        for issue in report.issues:
            color = "red" if issue.severity == "error" else "yellow"
            console.print(f"  [{color}][{issue.severity}][/{color}] {issue.path}: {issue.message}")

    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
