import asyncio
import logging
from typing import Dict, Any, Awaitable
from backend.core.registry import TagRegistry
from backend.core.event_bus import EventBus
from backend.models.events import SystemEvent

logger = logging.getLogger(__name__)

class Engine:
    def __init__(self):
        self.registry = TagRegistry()
        self.event_bus = EventBus()
        self._running = False
        self._stop_event = asyncio.Event()
        self._background_tasks: list[asyncio.Task] = []
        self._config: Dict[str, Any] = {}

    async def start(self) -> None:
        if self._running:
            logger.warning("⚠️ Engine is already running.")
            return
        self._running = True
        self._stop_event.clear()
        logger.info("🚀 Engine starting...")
        await self.event_bus.publish("system", SystemEvent(type="started", message="Engine running"))
        await self._stop_event.wait()
        logger.info("🛑 Graceful shutdown initiated...")
        self._running = False
        await self._stop_background_tasks()
        await self.event_bus.publish("system", SystemEvent(type="stopped", message="Engine stopped"))

    def stop(self) -> None:
        self._stop_event.set()

    @property
    def is_running(self) -> bool:
        return self._running

    def start_background(self, coro: Awaitable, name: str = "unnamed") -> None:
        if not self._running:
            logger.warning(f"⚠️ Cannot start {name}: engine is not running.")
            return
        task = asyncio.create_task(coro, name=name)
        self._background_tasks.append(task)
        task.add_done_callback(lambda t: self._background_tasks.remove(t) if t in self._background_tasks else None)

    async def _stop_background_tasks(self) -> None:
        if not self._background_tasks:
            return
        logger.info(f"🔄 Cancelling {len(self._background_tasks)} background tasks...")
        for task in self._background_tasks:
            task.cancel()
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()

    def load_config(self, config: Dict[str, Any]) -> None:
        self._config = config
        logger.info(f"📄 Config loaded. Tags: {len(config.get('tags', []))}")

    def status(self) -> dict:
        return {
            "running": self._running,
            "tags_count": len(self.registry._tags),
            "config_loaded": bool(self._config),
            "background_tasks": len(self._background_tasks)
        }
