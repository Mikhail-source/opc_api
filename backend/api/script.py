from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ScriptPayload(BaseModel):
    content: str
    interval: float = 1.0

@router.get("/content")
async def get_script():
    from backend.main import engine
    if not engine or not hasattr(engine, 'lua'):
        return {"content": "", "interval": 1.0}
    return {"content": engine.lua._script, "interval": engine.lua._interval}

@router.post("/reload")
async def reload_script(data: ScriptPayload):
    from backend.main import engine
    if not engine or not hasattr(engine, 'lua'):
        raise HTTPException(503, "Lua engine not initialized")
    
    engine.lua.load_script(data.content)
    # Если движок уже запущен, перезапускаем Lua с новым кодом (hot-reload)
    if engine.is_running:
        engine.lua.stop()
        await engine.lua.start(interval=data.interval)
        
    return {"message": "Script reloaded", "interval": data.interval}
