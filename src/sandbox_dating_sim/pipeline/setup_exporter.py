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
        若目標檔案已存在則拋 FileExistsError（不覆寫）。
        回傳寫入路徑。
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        content = self.to_markdown(package)
        filename = f"{package.world.world_id}_setup_package.md"
        filepath = output_dir / filename
        if filepath.exists():
            raise FileExistsError(
                f"目標檔案已存在，拒絕覆寫：{filepath}\n"
                "請手動刪除或重新命名後再匯出。"
            )
        filepath.write_text(content, encoding="utf-8")
        return filepath

    def write_file_default_path(self, package: SetupPackage, outputs_root: Path | None = None) -> Path:
        """
        使用 Phase 2 固定輸出布局：
          outputs/<world_id>/setup_package/<world_id>_setup_package.md
        若 outputs_root 為 None，預設使用當前工作目錄下的 outputs/。
        目標檔案已存在時拋 FileExistsError（不覆寫）。
        """
        root = outputs_root or Path("outputs")
        world_id = package.world.world_id
        output_dir = root / world_id / "setup_package"
        return self.write_file(package, output_dir)
