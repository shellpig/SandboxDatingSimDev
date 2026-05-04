# Blueprint Invalid — unknown_location（測試用）

此 fixture 的 event 引用了不存在的 location_id，用於測試 full linter cross-check。

```yaml
event_blueprint_version: "1.0"
blueprint_id: summer_city_2026_event_blueprint
source_world_id: summer_city_2026
source_setup_package: summer_city_2026_setup_package.md
target_game_spec_version: "1.2"
initial_event_id: opening_morning

events:
  - event_id: opening_morning
    title: 新的一天
    scene_summary: 主角在家中醒來。
    location_id: nonexistent_location
    time_slot: morning
    priority: main
    repeat_policy: once
    route_tags: []
    conditions: []
    event_purpose: 測試事件。
    cast: []
    expected_assets:
      background: null
      bgm: null
      characters: []
    choices:
      - choice_id: go
        choice_label: 前往
        choice_intent: 前往。
        result:
          - "goto: free_roam"
    time_cost: 1

new_flags_proposed: []
```
