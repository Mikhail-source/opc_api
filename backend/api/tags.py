from fastapi import APIRouter, HTTPException
# Lazy import: импортируем только внутри функции
# для решения проблемы с Circular Import

router = APIRouter()

@router.get("")
async def list_tags():
    from backend.main import engine
    if not engine:
        raise HTTPException(503, "Engine not initialized")
    return await engine.registry.get_snapshot()

@router.get("/{name}")
async def get_tag(name: str):
    from backend.main import engine
    if not engine:
        raise HTTPException(503, "Engine not initialized")
    tag = await engine.registry.get_tag(name)
    if not tag:
        raise HTTPException(404, f"Tag '{name}' not found")
    return tag.to_dict()