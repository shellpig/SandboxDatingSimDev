"""Phase 2-C Blueprint Parser.

從 Markdown 文件中提取 exactly one YAML fenced code block，
並解析為 EventBlueprint Pydantic model。
"""

import re
import yaml
from pydantic import ValidationError
from sandbox_dating_sim.schema.blueprint import EventBlueprint


class BlueprintParseError(Exception):
    """Blueprint 解析失敗（格式錯誤、YAML 語法錯、schema 不合）。"""


_YAML_BLOCK_RE = re.compile(r"```(?:yaml|yml)\n(.*?)```", re.DOTALL)


class BlueprintParser:
    """從 Markdown 解析 EventBlueprint。"""

    def parse_markdown(self, markdown_text: str) -> EventBlueprint:
        """
        從 Markdown 文字解析 EventBlueprint。

        Rules:
        - 恰好一個 yaml/yml fenced code block。
        - YAML block 外的 Markdown 全部忽略。
        - 0 個 block → BlueprintParseError
        - 多個 block → BlueprintParseError
        - YAML 語法錯 → BlueprintParseError
        - YAML root 非 mapping → BlueprintParseError
        - Pydantic schema 驗證失敗 → BlueprintParseError（含原始 ValidationError）
        """
        blocks = _YAML_BLOCK_RE.findall(markdown_text)

        if len(blocks) == 0:
            raise BlueprintParseError("Blueprint Markdown 中找不到任何 YAML fenced code block。")
        if len(blocks) > 1:
            raise BlueprintParseError(
                f"Blueprint Markdown 中找到 {len(blocks)} 個 YAML block，必須恰好一個。"
            )

        raw_yaml = blocks[0]

        try:
            data = yaml.safe_load(raw_yaml)
        except yaml.YAMLError as e:
            raise BlueprintParseError(f"YAML 語法錯誤：{e}") from e

        if not isinstance(data, dict):
            raise BlueprintParseError(
                f"YAML block 根節點必須是 mapping（dict），實際為 {type(data).__name__}。"
            )

        try:
            return EventBlueprint(**data)
        except ValidationError as e:
            raise BlueprintParseError(f"Blueprint schema 驗證失敗：{e}") from e

    def parse_file(self, path) -> EventBlueprint:
        """從檔案路徑讀取並解析。"""
        from pathlib import Path
        text = Path(path).read_text(encoding="utf-8")
        return self.parse_markdown(text)
