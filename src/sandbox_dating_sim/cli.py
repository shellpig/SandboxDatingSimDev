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
    out: Path = typer.Option(None, "--out", help="自訂輸出目錄（省略時使用預設 outputs/<world_id>/setup_package/）。"),
) -> None:
    """
    讀取 YAML 初始設定，驗證後輸出 Setup Package MD。

    預設輸出路徑：outputs/<world_id>/setup_package/<world_id>_setup_package.md
    若目標檔案已存在則報錯，不覆寫。
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

    try:
        if out is not None:
            # 進階：使用者指定目錄，同樣防覆寫
            filepath = exporter.write_file(package, out)
        else:
            # 預設：Phase 2 固定輸出布局
            filepath = exporter.write_file_default_path(package)
    except FileExistsError as e:
        console.print(f"[red]錯誤：{e}[/red]")
        raise typer.Exit(code=1)

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


@app.command("build-blueprint-prompt")
def build_blueprint_prompt(
    outputs_root: Path = typer.Option(Path("outputs"), "--outputs-root", help="outputs 根目錄，預設為 outputs/。"),
) -> None:
    """
    互動式產生 Event Blueprint Prompt MD。

    流程：
    1. 掃描 outputs/<world_id>/setup_package/ 找可用 Setup Package。
    2. 選擇 world 與 Setup Package 檔。
    3. 選擇 prompt scope。
    4. 若 custom scope，輸入目標事件數與說明。
    5. 輸出 outputs/<world_id>/prompts/<world_id>_event_blueprint_prompt.md。
    若目標已存在則報錯，不覆寫。
    """
    from sandbox_dating_sim.prompts.blueprint_prompt import (
        build_event_blueprint_prompt,
        write_prompt_file,
    )

    # ── Step 1: 掃描可用 worlds ──
    if not outputs_root.exists():
        console.print(f"[red]錯誤：找不到 outputs 目錄 {outputs_root}[/red]")
        raise typer.Exit(code=1)

    worlds = sorted([
        d for d in outputs_root.iterdir()
        if d.is_dir() and (d / "setup_package").exists()
    ])
    if not worlds:
        console.print(f"[red]錯誤：{outputs_root} 下找不到任何含 setup_package/ 的 world 目錄。[/red]")
        console.print("請先執行 export-setup 產生 Setup Package。")
        raise typer.Exit(code=1)

    # ── Step 2: 選 world ──
    console.print("[bold]可用的 World：[/bold]")
    for i, w in enumerate(worlds):
        console.print(f"  [{i+1}] {w.name}")
    world_idx = typer.prompt("請選擇 World 編號", type=int) - 1
    if not (0 <= world_idx < len(worlds)):
        console.print("[red]錯誤：無效的 World 編號。[/red]")
        raise typer.Exit(code=1)
    world_dir = worlds[world_idx]
    world_id = world_dir.name

    # ── Step 3: 選 setup package 檔 ──
    setup_dir = world_dir / "setup_package"
    setup_files = sorted(setup_dir.glob("*_setup_package.md"))
    if not setup_files:
        console.print(f"[red]錯誤：在 {setup_dir} 下找不到 *_setup_package.md。[/red]")
        raise typer.Exit(code=1)

    console.print(f"\n[bold]可用的 Setup Package ({world_id})：[/bold]")
    for i, f in enumerate(setup_files):
        console.print(f"  [{i+1}] {f.name}")
    setup_idx = typer.prompt("請選擇 Setup Package 編號", type=int) - 1
    if not (0 <= setup_idx < len(setup_files)):
        console.print("[red]錯誤：無效的 Setup Package 編號。[/red]")
        raise typer.Exit(code=1)
    setup_file = setup_files[setup_idx]
    setup_md = setup_file.read_text(encoding="utf-8")

    # ── Step 4: 選 scope ──
    scope_choices = {
        "1": "minimal_complete",
        "2": "ai_decides",
        "3": "custom",
    }
    console.print("\n[bold]Prompt Scope：[/bold]")
    console.print("  [1] minimal_complete  （最小完整事件網，含 opening、主線、所有 endings）")
    console.print("  [2] ai_decides        （AI 自決事件數，但必須 cover all endings）")
    console.print("  [3] custom            （自訂目標事件數與說明）")
    scope_key = typer.prompt("請選擇 scope 編號", default="1")
    if scope_key not in scope_choices:
        console.print("[red]錯誤：無效的 scope 編號。[/red]")
        raise typer.Exit(code=1)
    scope = scope_choices[scope_key]

    # ── Step 5: custom scope 額外輸入 ──
    target_event_count: int | None = None
    custom_scope_notes: str | None = None
    if scope == "custom":
        count_str = typer.prompt("目標事件數（留空則不指定）", default="")
        if count_str.strip():
            try:
                target_event_count = int(count_str.strip())
                if target_event_count <= 0:
                    raise ValueError
            except ValueError:
                console.print("[red]錯誤：目標事件數必須是正整數。[/red]")
                raise typer.Exit(code=1)
        custom_scope_notes = typer.prompt("額外說明（留空則略過）", default="") or None

    # ── Step 6: 產生 prompt ──
    prompt_text = build_event_blueprint_prompt(
        setup_package_markdown=setup_md,
        scope=scope,
        target_event_count=target_event_count,
        custom_scope=custom_scope_notes,
    )

    # ── Step 7: 寫出 prompt ──
    try:
        filepath = write_prompt_file(outputs_root, world_id, prompt_text)
    except FileExistsError as e:
        console.print(f"[red]錯誤：{e}[/red]")
        raise typer.Exit(code=1)

    console.print(Panel(
        f"[green]Prompt 已產生[/green]\n"
        f"World  ：{world_id}\n"
        f"Scope  ：{scope}\n"
        f"輸出   ：{filepath.absolute()}",
        title="Blueprint Prompt Builder",
    ))
    raise typer.Exit(code=0)


@app.command("validate-blueprint")
def validate_blueprint(
    outputs_root: Path = typer.Option(Path("outputs"), "--outputs-root"),
) -> None:
    """互動式驗證 Event Blueprint。只印 terminal report，不寫檔。"""
    from sandbox_dating_sim.pipeline.blueprint_parser import BlueprintParser, BlueprintParseError
    from sandbox_dating_sim.pipeline.setup_parser import SetupPackageParser
    from sandbox_dating_sim.validation.blueprint_linter import BlueprintLinter

    if not outputs_root.exists():
        console.print(f"[red]錯誤：找不到 {outputs_root}[/red]")
        raise typer.Exit(code=1)

    worlds = sorted([d for d in outputs_root.iterdir()
                     if d.is_dir() and (d / "setup_package").exists()])
    if not worlds:
        console.print("[red]錯誤：找不到任何含 setup_package/ 的 world 目錄。[/red]")
        raise typer.Exit(code=1)

    console.print("[bold]可用 World：[/bold]")
    for i, w in enumerate(worlds):
        console.print(f"  [{i+1}] {w.name}")
    idx = typer.prompt("選 World 編號", type=int) - 1
    if not (0 <= idx < len(worlds)):
        console.print("[red]錯誤：無效編號。[/red]")
        raise typer.Exit(code=1)
    world_dir = worlds[idx]
    world_id = world_dir.name

    setup_files = sorted((world_dir / "setup_package").glob("*_setup_package.md"))
    if not setup_files:
        console.print(f"[red]錯誤：找不到 setup package 檔案。[/red]")
        raise typer.Exit(code=1)
    console.print(f"\n[bold]可用 Setup Package：[/bold]")
    for i, f in enumerate(setup_files):
        console.print(f"  [{i+1}] {f.name}")
    sidx = typer.prompt("選 Setup Package 編號", type=int) - 1
    if not (0 <= sidx < len(setup_files)):
        console.print("[red]錯誤：無效編號。[/red]")
        raise typer.Exit(code=1)
    setup_file = setup_files[sidx]

    blueprint_path = world_dir / "event_blueprints" / f"{world_id}_event_blueprint.md"
    if not blueprint_path.exists():
        console.print(f"[red]錯誤：找不到 blueprint 檔案：{blueprint_path}[/red]")
        raise typer.Exit(code=1)

    sp_parser = SetupPackageParser()
    bp_parser = BlueprintParser()
    try:
        setup_pkg = sp_parser.parse_file(setup_file)
    except Exception as e:
        console.print(f"[red]Setup Package 解析失敗：{e}[/red]")
        raise typer.Exit(code=1)
    try:
        blueprint = bp_parser.parse_file(blueprint_path)
    except BlueprintParseError as e:
        console.print(f"[red]Blueprint 解析失敗：{e}[/red]")
        raise typer.Exit(code=1)

    linter = BlueprintLinter()

    console.print("\n[bold]── Blueprint-Only Report ──[/bold]")
    bp_report = linter.validate_blueprint_only(blueprint)
    _print_report(bp_report)

    console.print("\n[bold]── Full Validation Report ──[/bold]")
    full_report = linter.validate(setup_pkg, blueprint)
    _print_report(full_report)

    code = 0 if full_report.status == "passed" else 1
    raise typer.Exit(code=code)


@app.command("walkthrough-blueprint")
def walkthrough_blueprint(
    outputs_root: Path = typer.Option(Path("outputs"), "--outputs-root"),
) -> None:
    """互動式執行 Event Blueprint 邏輯推演。"""
    from sandbox_dating_sim.pipeline.blueprint_parser import BlueprintParser
    from sandbox_dating_sim.pipeline.setup_parser import SetupPackageParser
    from sandbox_dating_sim.validation.blueprint_linter import BlueprintLinter
    from sandbox_dating_sim.walkthrough.blueprint_walkthrough import (
        create_initial_walkthrough_state, enter_event, list_available_events,
        list_available_actions, apply_choice, apply_action
    )
    from sandbox_dating_sim.walkthrough.checkpoint import make_checkpoint, dump_checkpoint, load_checkpoint
    from sandbox_dating_sim.walkthrough.route_graph import build_route_graph

    if not outputs_root.exists():
        console.print(f"[red]錯誤：找不到 {outputs_root}[/red]")
        raise typer.Exit(code=1)

    worlds = sorted([d for d in outputs_root.iterdir()
                     if d.is_dir() and (d / "setup_package").exists()])
    if not worlds:
        console.print("[red]錯誤：找不到任何含 setup_package/ 的 world 目錄。[/red]")
        raise typer.Exit(code=1)

    console.print("[bold]可用 World：[/bold]")
    for i, w in enumerate(worlds):
        console.print(f"  [{i+1}] {w.name}")
    idx = typer.prompt("選 World 編號", type=int) - 1
    world_dir = worlds[idx]
    world_id = world_dir.name

    setup_files = sorted((world_dir / "setup_package").glob("*_setup_package.md"))
    console.print(f"\n[bold]可用 Setup Package：[/bold]")
    for i, f in enumerate(setup_files):
        console.print(f"  [{i+1}] {f.name}")
    sidx = typer.prompt("選 Setup Package 編號", type=int) - 1
    setup_file = setup_files[sidx]

    blueprint_path = world_dir / "event_blueprints" / f"{world_id}_event_blueprint.md"
    
    setup_pkg = SetupPackageParser().parse_file(setup_file)
    blueprint = BlueprintParser().parse_file(blueprint_path)
    report = BlueprintLinter().validate(setup_pkg, blueprint)
    if report.status == "failed":
        console.print("[red]Blueprint Validation Failed. Cannot start walkthrough.[/red]")
        raise typer.Exit(code=1)

    start_mode = typer.prompt("Select start mode (1: beginning, 2: checkpoint)", default="1")
    state = None
    history = []
    start_state_checkpoint = None

    if start_mode == "2":
        cp_dir = world_dir / "walkthrough_checkpoints" / f"{world_id}_event_blueprint"
        if cp_dir.exists():
            cps = sorted(cp_dir.glob("*.yaml"))
            valid_cps = []
            for cp_path in cps:
                try:
                    cp_content = cp_path.read_text(encoding="utf-8")
                    cp = load_checkpoint(cp_content)
                    if cp.source_world_id == world_id and cp.blueprint_id == blueprint.blueprint_id:
                        valid_cps.append((cp_path, cp))
                except Exception:
                    pass
            if valid_cps:
                for i, (p, c) in enumerate(valid_cps):
                    lbl = f" - {c.label}" if c.label else ""
                    console.print(f"  [{i+1}] {p.name}{lbl}")
                cidx = typer.prompt("Select checkpoint", type=int) - 1
                cp_path, cp = valid_cps[cidx]
                state = cp.state
                history = cp.history
                start_state_checkpoint = state.model_copy(deep=True)
            else:
                console.print("No valid checkpoints found for this world and blueprint.")
                raise typer.Exit(code=1)
        else:
            console.print("No checkpoints found.")
            raise typer.Exit(code=1)
    else:
        state = create_initial_walkthrough_state(setup_pkg, blueprint)
        enter_event(setup_pkg, blueprint, state, blueprint.initial_event_id)

    test_mode = typer.prompt("Select test mode (1: omniscient, 2: normal)", default="1")
    normal_selected_location = None
    
    while True:
        if state.mode == "ending_reached":
            console.print("[green]Ending Reached![/green]")
        elif state.mode == "dead_end":
            console.print(f"[yellow]Dead End: {state.blocked_reason}[/yellow]")
        elif state.mode == "blocked":
            console.print(f"[red]Blocked: {state.blocked_reason}[/red]")
            
        console.print(f"\n=== {state.current_date} {state.current_time_slot} @ {state.current_location_id} ===")
        
        lookup = {}
        if state.mode == "in_event":
            ev = next((e for e in blueprint.events if e.event_id == state.current_event_id), None)
            if ev:
                console.print(f"[bold]Event: {ev.title}[/bold]")
                for i, ch in enumerate(ev.choices):
                    console.print(f"  [{i+1}] {ch.choice_label}")
                    lookup[str(i+1)] = ("choice", ch.choice_id)
        elif state.mode == "free_roam":
            avail_evs = list_available_events(setup_pkg, blueprint, state)
            avail_acts = list_available_actions(setup_pkg, state)
            
            idx = 1
            if test_mode == "1":
                # Omniscient mode
                for loc, evs in avail_evs.items():
                    console.print(f"[[{loc}]]")
                    for e in evs:
                        ev = e["event"]
                        console.print(f"  [{idx}] Event: {ev.title}")
                        lookup[str(idx)] = ("event", ev.event_id)
                        idx += 1
                for loc, acts in avail_acts.items():
                    if acts:
                        console.print(f"[[{loc}]]")
                        for a in acts:
                            console.print(f"  [{idx}] Action: {a}")
                            lookup[str(idx)] = ("action", a, loc)
                            idx += 1
            else:
                # Normal mode
                if normal_selected_location is None:
                    locs = set(list(avail_evs.keys()) + list(avail_acts.keys()))
                    console.print("[bold]Available Locations:[/bold]")
                    for loc in sorted(list(locs)):
                        console.print(f"  [{idx}] Location: {loc}")
                        lookup[str(idx)] = ("location", loc)
                        idx += 1
                else:
                    loc = normal_selected_location
                    console.print(f"[bold]Location: {loc}[/bold]")
                    if loc in avail_evs:
                        for e in avail_evs[loc]:
                            ev = e["event"]
                            console.print(f"  [{idx}] Event: {ev.title}")
                            lookup[str(idx)] = ("event", ev.event_id)
                            idx += 1
                    if loc in avail_acts:
                        for a in avail_acts[loc]:
                            console.print(f"  [{idx}] Action: {a}")
                            lookup[str(idx)] = ("action", a, loc)
                            idx += 1
                    console.print(f"  [0] Back to locations")
                    lookup["0"] = ("back",)

        cmd = typer.prompt("Command (<number>, s/save, state, history, graph, restart, q/quit)")
        
        if cmd in ("q", "quit"):
            break
        elif cmd in ("s", "save"):
            if state.mode == "in_event":
                console.print("Cannot save inside an event.")
                continue
            lbl = typer.prompt("Checkpoint label", default="")
            cp = make_checkpoint(state, history, world_id, blueprint.blueprint_id, lbl if lbl else None)
            out_dir = world_dir / "walkthrough_checkpoints" / f"{world_id}_event_blueprint"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{cp.checkpoint_id}.yaml"
            out_path.write_text(dump_checkpoint(cp), encoding="utf-8")
            console.print(f"Saved checkpoint to {out_path}")
        elif cmd == "graph":
            g = build_route_graph(blueprint)
            out_dir = world_dir / "route_graphs"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{world_id}_event_blueprint_graph.md"
            if out_path.exists():
                console.print("Graph already exists. Not overwriting.")
            else:
                out_path.write_text(g, encoding="utf-8")
                console.print(f"Saved graph to {out_path}")
        elif cmd == "state":
            console.print(f"Mode: {state.mode}, Date: {state.current_date}, Slot: {state.current_time_slot}")
            console.print(f"Flags: {[k for k,v in state.flags.items() if v]}")
            console.print(f"Stats: {state.stats}")
            console.print(f"Favor: {state.character_favor}")
            console.print(f"Active Statuses: {state.active_statuses}")
        elif cmd == "history":
            for h in history:
                console.print(f"{h.date} {h.time_slot} {h.kind} {h.event_id} {h.choice_id} {h.ending_id}")
        elif cmd == "restart":
            if start_state_checkpoint is not None:
                state = start_state_checkpoint.model_copy(deep=True)
            else:
                state = create_initial_walkthrough_state(setup_pkg, blueprint)
                enter_event(setup_pkg, blueprint, state, blueprint.initial_event_id)
            history = []
            normal_selected_location = None
            continue
        else:
            if cmd in lookup:
                tup = lookup[cmd]
                if tup[0] == "choice":
                    apply_choice(setup_pkg, blueprint, state, state.current_event_id, tup[1], history)
                elif tup[0] == "event":
                    enter_event(setup_pkg, blueprint, state, tup[1])
                    normal_selected_location = None
                elif tup[0] == "action":
                    state.current_location_id = tup[2]
                    apply_action(setup_pkg, blueprint, state, tup[1], history)
                    normal_selected_location = None
                elif tup[0] == "location":
                    normal_selected_location = tup[1]
                elif tup[0] == "back":
                    normal_selected_location = None

def _print_report(report) -> None:
    if report.status == "passed":
        console.print("[green]✅ passed[/green]")
    else:
        console.print(f"[red]❌ failed — {len(report.issues)} 個問題[/red]")
    for issue in report.issues:
        color = "red" if issue.severity == "error" else "yellow"
        console.print(f"  [{color}][{issue.severity}][/{color}] [{issue.type}] {issue.path}: {issue.message}")


if __name__ == "__main__":
    app()
