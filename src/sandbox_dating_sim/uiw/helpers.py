import re
import yaml

FLAG_REF_PATTERN = re.compile(r"\bflag\.([a-zA-Z0-9_]+)\b")
STATUS_QUALIFIED_PATTERN = re.compile(r"\bstatus\.([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\b")
STATUS_BARE_PATTERN = re.compile(r"\bstatus\.([a-zA-Z0-9_]+)\b")

def _has_flag_reference(text: str, flag_id: str) -> bool:
    return any(m.group(1) == flag_id for m in FLAG_REF_PATTERN.finditer(text))

def _has_status_reference(text: str, status_id: str) -> bool:
    if any(m.group(2) == status_id for m in STATUS_QUALIFIED_PATTERN.finditer(text)):
        return True

    qualified_spans = [m.span() for m in STATUS_QUALIFIED_PATTERN.finditer(text)]
    for m in STATUS_BARE_PATTERN.finditer(text):
        if m.group(1) != status_id:
            continue
        if any(qs <= m.start() < qe for qs, qe in qualified_spans):
            continue
        return True
    return False

def _parse_effect_yaml(yaml_str: str) -> list[dict]:
    # 必須先擋非字串輸入：MagicMock 等 truthy 物件會被 PyYAML Reader 當 file-like，
    # stream.read(N) 永遠回非空 → 死迴圈。type hint 是 str，這裡是 runtime 防線。
    if not isinstance(yaml_str, str):
        raise ValueError("effect YAML 必須是字串")
    if not yaml_str.strip():
        raise ValueError("effect 必須是非空 list")
    try:
        parsed = yaml.safe_load(yaml_str)
    except yaml.YAMLError:
        raise ValueError("YAML 解析失敗")

    if not isinstance(parsed, list) or not parsed:
        raise ValueError("effect 必須是非空 list")

    for item in parsed:
        if not isinstance(item, dict) or not item:
            raise ValueError("effect list 元素必須是非空 dict")
        for k, v in item.items():
            if not isinstance(k, str) or not k:
                raise ValueError("dict key 必須是非空字串")

    return parsed

def _status_targets_options(characters: list[dict], current_targets: list[str]) -> list[tuple[str, str]]:
    """回傳 [(label, id), ...]；label 給 UI 顯示，id 是寫回 canonical 的值。"""
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    out.append(("主角(protagonist)", "protagonist"))
    seen.add("protagonist")
    for ch in characters:
        cid = ch.get("character_id")
        if not cid or cid in seen:
            continue
        display_name = ch.get('display_name', cid)
        out.append((f"{display_name}({cid})", cid))
        seen.add(cid)
    for tgt in current_targets:
        if tgt and tgt not in seen:
            out.append((f"{tgt}(角色已刪除)", tgt))
            seen.add(tgt)
    return out
