import logging
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from backend.models.config import ProjectConfig

logger = logging.getLogger(__name__)

class ProjectManager:
    PROJECTS_DIR = Path("projects")
    
    def __init__(self, projects_dir: Optional[Path] = None):
        self.PROJECTS_DIR = projects_dir or self.PROJECTS_DIR
        self.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        self._current_project: Optional[ProjectConfig] = None
        self._current_path: Optional[Path] = None

    def list_projects(self) -> list[str]:
        """Список доступных проектов (*.yaml)"""
        return [p.name for p in self.PROJECTS_DIR.glob("*.yaml")]

    def load_project(self, path: str | Path) -> ProjectConfig:
        """Загружает и валидирует проект"""
        project_path = self.PROJECTS_DIR / path if isinstance(path, str) else path
        if not project_path.exists():
            raise FileNotFoundError(f"Project not found: {project_path}")
        
        with open(project_path, 'r', encoding='utf-8') as f:
            raw_data = yaml.safe_load(f)
        
        # Валидация через Pydantic
        config = ProjectConfig(**raw_data)
        self._current_project = config
        self._current_path = project_path
        logger.info(f"📦 Project loaded: {config.project.get('name')} ({len(config.tags)} tags)")
        return config

    def save_project(self, path: Optional[str | Path] = None) -> bool:
        """Сохраняет текущий проект (атомарная запись)"""
        if not self._current_project:
            logger.warning("⚠️ No project loaded to save")
            return False
        
        save_path = Path(path) if path else self._current_path
        if not save_path:
            logger.error("❌ No path specified for save")
            return False
        
        # Атомарная запись: пишем во временный файл, затем переименовываем
        temp_path = save_path.with_suffix('.tmp')
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._current_project.model_dump(mode='json'), f, allow_unicode=True, default_flow_style=False)
            temp_path.rename(save_path)
            logger.info(f"💾 Project saved: {save_path.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save project: {e}")
            if temp_path.exists():
                temp_path.unlink()
            return False

    def get_current_project(self) -> Optional[ProjectConfig]:
        return self._current_project

    def get_current_path(self) -> Optional[Path]:
        return self._current_path
