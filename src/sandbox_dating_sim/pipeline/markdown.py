import re
from sandbox_dating_sim.core.exceptions import MarkdownParseError

def wrap_yaml_markdown(title: str, yaml_text: str) -> str:
    """
    將 YAML 包成 Markdown。
    輸出必須只有一個主要 ```yaml code block。
    """
    return f"# {title}\n\n```yaml\n{yaml_text.strip()}\n```\n"

def extract_first_yaml_block(markdown_text: str) -> str:
    """
    從 Markdown 擷取第一個 ```yaml code block。
    找不到時拋出 MarkdownParseError。
    """
    match = re.search(r"```yaml\n(.*?)\n```", markdown_text, re.DOTALL)
    if not match:
        raise MarkdownParseError("找不到 ```yaml 區塊。")
    return match.group(1).strip()
