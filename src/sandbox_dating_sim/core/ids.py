import re

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
