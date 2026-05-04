# Agent Instructions

## New Conversation Opening Check

At conversation start, read in this layered order. Ignore `舊文件/`.

**Layer 1 — Always read (build full picture fast):**
1. `AGENTS.md` (this file)
2. `PROJECT_BRIEF.md` (architecture, progress, spec index)
3. `已知問題.md` (current todos and known gaps)
4. `git log --oneline -15` (recent commits)

**Layer 2 — Expand per current task (targeted sections only):**
- Use line-number index in `PROJECT_BRIEF.md` to read only relevant sections of `開發設計方針.md` / `測試指南.md`. Don't read entire files.

**Layer 3 — Reference during implementation:**
- `Sandbox_Dating_Sim_初始設定_v1.2.md` — field definitions, default options, UI specs
- `Sandbox_Dating_Sim_Dev_正式規格_v1.2.md` — system architecture, DSL syntax
- `Sandbox_Dating_Sim_文件管線規格_v1.1.md` — document format specs
- Source code: read as needed per task

Report to user: current progress, and any issues with their scope of impact.

## Project Skills

This project uses local skills from `C:\Users\User\OneDrive\桌面\AI_Work\Skills\`.

Trigger rules:
- Diagnosing bugs / analyzing errors / finding root cause → read `Skills\engineering\diagnose\SKILL.md` first
- Requirements unclear / spec discussion / planning / need to ask clarifying questions → read `Skills\productivity\grill-me\SKILL.md` first
- Normal state / no urgent or special situation → read `Skills\productivity\caveman\SKILL.md` first

Only modify files when user explicitly requests fix, implement, or commit. Verify/diagnose = report only.
