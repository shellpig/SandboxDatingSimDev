# Blueprint Invalid — 多個 YAML block（測試用）

此文件故意包含兩個 YAML fenced code block，用於測試 parser error。

```yaml
event_blueprint_version: "1.0"
blueprint_id: test_bp
```

中間的說明文字。

```yaml
source_world_id: other_world
```
