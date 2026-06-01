from fastapi import APIRouter, HTTPException
# Lazy import: импортируем только внутри функции
# для решения проблемы с Circular Import

router = APIRouter()

@router.get("/status")
async def get_status():
    from backend.main import engine
    if not engine:
        raise HTTPException(503, "Engine not initialized")
    return engine.status()

@router.post("/start")
async def start_server():
    from backend.main import engine
    if not engine:
        raise HTTPException(503, "Engine not initialized")
    if engine.is_running:
        raise HTTPException(400, "Server is already running")
    # Запускаем в фоне
    import asyncio
    asyncio.create_task(engine.start())
    return {"message": "Server starting...", "status": engine.status()}

@router.post("/stop")
async def stop_server():
    from backend.main import engine
    if not engine:
        raise HTTPException(503, "Engine not initialized")
    if not engine.is_running:
        raise HTTPException(400, "Server is not running")
    engine.stop()
    return {"message": "Server stopping...", "status": engine.status()}