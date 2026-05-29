import asyncio
import logging
from abc import ABC, abstractmethod
from backend.core.registry import TagRegistry
from backend.core.event_bus import EventBus
from backend.models.events import DriverErrorEvent

logger = logging.getLogger(__name__)

class BaseDriver(ABC):
    def __init__(self, driver_id: str, config: dict, registry: TagRegistry, event_bus: EventBus):
        self.id = driver_id
        self.config = config
        self.registry = registry
        self.event_bus = event_bus
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._running: return
        self._running = True
        self._task = asyncio.create_task(self._run_loop(), name=f"driver_{self.id}")
        logger.info(f"🚀 Driver {self.id} started.")

    def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info(f"🛑 Driver {self.id} stopping...")

    async def _run_loop(self) -> None:
        reconnect_delay = 1.0
        while self._running:
            try:
                if not await self.connect():
                    await self._handle_error("Connection failed", reconnect_delay)
                    continue
                reconnect_delay = 1.0
                while self._running:
                    await self.poll_loop()
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self._handle_error(str(e), reconnect_delay)
            finally:
                await self.disconnect()

    async def _handle_error(self, error: str, delay: float) -> None:
        logger.error(f"❌ Driver {self.id} error: {error}. Retry in {delay:.1f}s")
        await self.event_bus.publish("driver_error", DriverErrorEvent(driver_id=self.id, error=error))
        await self.disconnect()
        await asyncio.sleep(delay)

    @abstractmethod
    async def connect(self) -> bool: pass
    @abstractmethod
    async def disconnect(self) -> None: pass
    @abstractmethod
    async def poll_loop(self) -> None: pass
