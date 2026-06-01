import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# Lazy import: импортируем только внутри функции
# для решения проблемы с Circular Import

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/tags")
async def websocket_tags(ws: WebSocket):
    from backend.main import engine
    
    await ws.accept()
    logger.info(f"🔌 WebSocket client connected: {ws.client}")
    
    if engine:
        # Начальный снапшот
        snapshot = await engine.registry.get_snapshot()
        await ws.send_text(json.dumps({"type": "snapshot", "payload": snapshot}))
        
        # Подписка на обновления
        async def on_tag_update(evt):
            try:
                await ws.send_text(json.dumps({"type": "update", "payload": {
                    "name": evt.name, "value": evt.value, "quality": evt.quality, "timestamp": evt.timestamp
                }}))
            except Exception as e:
                logger.error(f"WS send error: {e}")
        
        engine.event_bus.subscribe("tag_updated", on_tag_update)
    
    try:
        while True:
            await ws.receive_text()  # Держим соединение
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket client disconnected: {ws.client}")