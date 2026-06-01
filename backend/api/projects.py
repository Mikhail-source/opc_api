from fastapi import APIRouter, HTTPException, Query
from pathlib import Path

router = APIRouter()

@router.get("")
async def list_projects():
    """Список доступных проектов"""
    from backend.core.project_manager import ProjectManager
    pm = ProjectManager()
    return pm.list_projects()

@router.post("/load")
async def load_project(path: str = Query(..., description="Имя файла проекта в папке projects/")):
    """Загружает проект и обновляет реестр тегов"""
    from backend.core.project_manager import ProjectManager
    from backend.main import engine as global_engine  # 🔹 Lazy import
    
    if not global_engine:
        raise HTTPException(503, "Engine not initialized")
    
    pm = ProjectManager()
    try:
        config = pm.load_project(path)
        # Обновляем реестр тегов из конфига (hot-reload)
        await global_engine.registry.init_from_config([t.model_dump() for t in config.tags])
        return {"message": f"Project '{path}' loaded", "tags_count": len(config.tags)}
    except FileNotFoundError:
        raise HTTPException(404, f"Project '{path}' not found")
    except Exception as e:
        raise HTTPException(400, f"Failed to load project: {str(e)}")

@router.post("/save")
async def save_project():
    """Сохраняет текущее состояние в проект"""
    from backend.core.project_manager import ProjectManager
    from backend.main import engine as global_engine  # 🔹 Lazy import
    
    if not global_engine:
        raise HTTPException(503, "Engine not initialized")
    
    pm = ProjectManager()
    if not pm.get_current_path():
        raise HTTPException(400, "No project loaded to save")
    
    # Обновляем конфиг из текущего состояния реестра
    config = pm.get_current_project()
    if config:
        snapshot = await global_engine.registry.get_snapshot()
        for tag_cfg in config.tags:
            if tag_cfg.name in snapshot:
                tag_cfg.value = snapshot[tag_cfg.name]["value"]
                tag_cfg.quality = snapshot[tag_cfg.name]["quality"]
    
    if pm.save_project():
        return {"message": "Project saved"}
    else:
        raise HTTPException(500, "Failed to save project")

@router.get("/status")
async def project_status():
    """Статус текущего проекта"""
    from backend.core.project_manager import ProjectManager
    from backend.main import engine as global_engine  # 🔹 Lazy import
    
    pm = ProjectManager()
    current = pm.get_current_project()
    return {
        "loaded": current is not None,
        "path": str(pm.get_current_path()) if pm.get_current_path() else None,
        "name": current.project.get("name") if current else None,
        "tags_count": len(current.tags) if current else 0,
        "engine_running": global_engine.is_running if global_engine else False
    }
