import asyncio
import logging
from typing import Callable, Any, Dict, List
from collections import defaultdict

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable[[Any], Any]) -> None:
        self._handlers[event_type].append(handler)
        logger.debug(f"📥 Subscribed to '{event_type}'")

    async def publish(self, event_type: str, payload: Any) -> None:
        handlers = self._handlers.get(event_type, [])
        if not handlers:
            return
        for handler in handlers:
            try:
                asyncio.create_task(self._safe_invoke(handler, payload, event_type))
            except RuntimeError as e:
                logger.warning(f"Event loop closed, dropping event '{event_type}': {e}")

    async def _safe_invoke(self, handler: Callable, payload: Any, event_type: str) -> None:
        try:
            await handler(payload)
        except Exception as e:
            logger.error(f"❌ Handler failed for '{event_type}': {e}", exc_info=True)
