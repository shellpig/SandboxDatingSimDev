import yaml
from pathlib import Path
from sandbox_dating_sim.schema.setup import SetupPackage
from sandbox_dating_sim.uiw.linter import UIWLinter
from sandbox_dating_sim.pipeline.markdown import wrap_yaml_markdown

class SetupPackageExporter:
    """
    將 SetupPackage 匯出成 Setup Package MD。
    """

    def __init__(self, linter: UIWLinter | None = None):
        self.linter = linter or UIWLinter()

    def to_markdown(self, package: SetupPackage) -> str:
        # 使用深拷貝，不修改原始 package
        pkg = package.model_copy(deep=True)

        # 計算 total_days
        if pkg.world.total_days is None:
            delta = pkg.world.end_date - pkg.world.start_date
            pkg.world.total_days = delta.days + 1

        # 執行 UIW Linter
        report = self.linter.validate(pkg)
        pkg.validation_report = report

        # serialize 成 YAML
        data = pkg.model_dump(mode="json", exclude_none=True)
        yaml_text = yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)

        # 包成 Markdown
        return wrap_yaml_markdown(f"Setup Package: {pkg.world.title}", yaml_text)

    def write_file(self, package: SetupPackage, output_dir: Path) -> Path:
        """
        輸出檔名：<world_id>_setup_package.md
        回傳寫入路徑。
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        content = self.to_markdown(package)
        filename = f"{package.world.world_id}_setup_package.md"
        filepath = output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return filepath
