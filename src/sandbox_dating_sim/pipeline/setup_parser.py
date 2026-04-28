import yaml
from pathlib import Path
from sandbox_dating_sim.schema.setup import SetupPackage
from sandbox_dating_sim.pipeline.markdown import extract_first_yaml_block

class SetupPackageParser:
    """
    從 Setup Package MD 讀回 SetupPackage。
    """

    def parse_markdown(self, markdown_text: str) -> SetupPackage:
        """擷取 YAML block 並轉為 SetupPackage。"""
        yaml_text = extract_first_yaml_block(markdown_text)
        data = yaml.safe_load(yaml_text)
        return SetupPackage(**data)

    def parse_file(self, path: Path) -> SetupPackage:
        """讀取檔案並 parse。"""
        content = path.read_text(encoding="utf-8")
        return self.parse_markdown(content)
