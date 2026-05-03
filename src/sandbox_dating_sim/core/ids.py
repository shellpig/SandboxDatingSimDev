import re
import pypinyin

ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

def is_valid_id(value: str) -> bool:
    """回傳 value 是否符合 canonical ID 格式。"""
    if not isinstance(value, str):
        return False
    return bool(ID_PATTERN.match(value))

def normalize_id(value: str) -> str:
    """
    將輸入轉為小寫底線格式。
    僅處理英文、數字、空格、連字號。
    中文不得自動音譯，應回報錯誤或要求使用者輸入英文 ID。
    """
    # Check for Chinese characters
    if any('\u4e00' <= char <= '\u9fff' for char in value):
        raise ValueError(f"ID contains Chinese characters: {value}. Please use English IDs.")

    # Convert to lowercase and replace spaces/hyphens with underscores
    n_id = value.lower().strip()
    n_id = re.sub(r"[\s\-]+", "_", n_id)

    # Remove invalid characters
    n_id = re.sub(r"[^a-z0-9_]", "", n_id)

    if not is_valid_id(n_id):
         # It might not start with a letter after stripping
         if n_id and n_id[0].isdigit():
             n_id = f"id_{n_id}"
         elif not n_id:
             raise ValueError("Resulting ID is empty.")

         if not is_valid_id(n_id):
             raise ValueError(f"Could not normalize '{value}' to a valid ID.")

    return n_id

def _slugify_label(label: str, fallback: str = "unnamed") -> str:
    """
    1-G-7: 將標籤轉為小寫拼音/英文 slug。
    包含處理中文標點、截斷與合併重複底線。
    """
    if not label or not label.strip():
        return fallback

    # 處理中文標點與空格轉底線
    s = re.sub(r"[、，。：\s]+", "_", label.strip())

    # 若為純英數底線則轉小寫，否則轉拼音
    if re.match(r"^[a-zA-Z0-9_]+$", s):
        candidate = s.lower()
    else:
        pinyin_list = pypinyin.lazy_pinyin(s)
        candidate = "_".join(pinyin_list).lower()

    # 清除非法字元
    candidate = re.sub(r"[^a-z0-9_]", "", candidate)
    # 合併重複底線並去前後綴
    candidate = re.sub(r"_+", "_", candidate).strip("_")
    # 移除開頭數字
    candidate = re.sub(r"^[0-9]+", "", candidate).strip("_")

    # 截斷至前 8 個 token
    tokens = candidate.split("_")
    if len(tokens) > 8:
        candidate = "_".join(tokens[:8])

    return candidate if candidate else fallback

def _make_unique_id(label: str, prefix: str, fallback: str, existing_ids: set[str]) -> str:
    """
    1-G-7: 產生全域唯一的 ID，支援連鎖 suffix 避讓。
    """
    base_slug = _slugify_label(label, fallback)
    candidate = f"{prefix}{base_slug}"

    if candidate not in existing_ids:
        return candidate

    counter = 2
    while True:
        suffix_candidate = f"{candidate}_{counter}"
        if suffix_candidate not in existing_ids:
            return suffix_candidate
        counter += 1
