# Blueprint Invalid — missing terminal（測試用）

此 fixture 的 choice result 沒有任何 goto 或 ending，用於測試 missing_terminal。

```yaml
event_blueprint_version: "1.0"
blueprint_id: test_world_event_blueprint
source_world_id: test_world
source_setup_package: test_world_setup_package.md
target_game_spec_version: "1.2"
initial_event_id: ev1

events:
  - event_id: ev1
    title: 測試
    scene_summary: 場景。
    location_id: protagonist_home
    time_slot: morning
    priority: main
    repeat_policy: once
    route_tags: []
    conditions: []
    event_purpose: 測試。
    cast: []
    expected_assets:
      background: null
      bgm: null
      characters: []
    choices:
      - choice_id: c1
        choice_label: 選項
        choice_intent: 測試。
        result:
          - "flag.some_flag = true"
    time_cost: 1

new_flags_proposed: []
```
