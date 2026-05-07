# Event Blueprint：夏日債務街

此文件由 Prompt Builder 產出後交給外部 AI 生成，再由 Blueprint Parser 驗證。
Markdown 外殼僅供人類閱讀，系統只信任下方 YAML code block。

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
    scene_summary: 主角在家中醒來，準備開始新的一天。
    location_id: protagonist_home
    time_slot: morning
    priority: main
    repeat_policy: once
    route_tags:
      - opening
      - tutorial
    conditions: []
    event_purpose: 介紹主角的處境與初始狀態，帶出債務壓力。
    cast: []
    expected_assets:
      background: null
      bgm: null
      characters: []
    choices:
      - choice_id: go_school
        choice_label: 去學校
        choice_intent: 前往學校，可能與蘇菲相遇。
        result:
          - "goto: free_roam"
      - choice_id: stay_home
        choice_label: 繼續睡
        choice_intent: 休息，今天不外出。
        result:
          - "goto: fallback_debt_ending"
      - choice_id: meet_sophie
        choice_label: 去找蘇菲
        choice_intent: 進入蘇菲路線。
        result:
          - "goto: sophie_good_event"
    time_cost: 1

  - event_id: fallback_debt_ending
    title: 普通還債結局
    scene_summary: 主角沒有深入任何角色路線，靠自己的努力撐過債務壓力。
    location_id: protagonist_home
    time_slot: afternoon
    priority: normal
    repeat_policy: once
    route_tags:
      - fallback_ending
    conditions: []
    event_purpose: 提供保底結局，避免路線未完成時無結局可達。
    cast: []
    expected_assets:
      background: null
      bgm: null
      characters: []
    choices:
      - choice_id: accept
        choice_label: 接受現實
        choice_intent: 結束在普通還債結局。
        result:
          - "ending: debt_normal_ending"
    time_cost: 1

  - event_id: sophie_good_event
    title: 蘇菲 Good Ending
    scene_summary: 主角與蘇菲互相理解，決定一起面對債務與家庭問題。
    location_id: school_library
    time_slot: afternoon
    priority: route
    repeat_policy: once
    route_tags:
      - character_route:sophie
    conditions: []
    event_purpose: 覆蓋蘇菲 Good Ending。
    cast:
      - sophie
    expected_assets:
      background: school_library_day
      bgm: null
      characters:
        - character_id: sophie
          costume: school_uniform
          emotion: happy
          position: center
    choices:
      - choice_id: accept
        choice_label: 接受蘇菲的心意
        choice_intent: 結束在蘇菲 Good Ending。
        result:
          - "ending: sophie_good_ending"
    time_cost: 1

new_flags_proposed: []
```
