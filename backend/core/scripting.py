import asyncio
import logging
import time
from lupa import LuaRuntime
from backend.core.registry import TagRegistry
from backend.core.event_bus import EventBus

logger = logging.getLogger(__name__)

class LuaEngine:
    def __init__(self, registry: TagRegistry, event_bus: EventBus):
        self.registry = registry
        self.event_bus = event_bus
        self._lua: LuaRuntime | None = None
        self._task: asyncio.Task | None = None
        self._running = False
        self._script = ""
        self._interval = 1.0
        self._local_tags: dict = {}  # Синхронный кэш для Lua

    def load_script(self, content: str):
        self._script = content.strip()

    async def start(self, interval: float = 1.0):
        if self._running or not self._script:
            if not self._script:
                logger.info("ℹ️ Lua script is empty, skipping start")
            return
        self._interval = interval
        self._running = True
        self._task = asyncio.create_task(self._run_loop(), name="lua_engine")
        logger.info(f"🟢 Lua engine started (interval: {interval}s)")

    def stop(self):
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("🛑 Lua engine stopped")

    def _create_runtime(self):
        """Создаёт новый Lua-рантайм с изолированным окружением."""
        self._lua = LuaRuntime(unpack_returned_tuples=True)
        # Инжектируем API в глобальную таблицу Lua
        g = self._lua.globals()
        g['tag_get'] = lambda name: self._local_tags.get(name)
        g['tag_set'] = lambda name, value: self._local_tags.__setitem__(name, value)
        g['log'] = lambda msg: logger.info(f"[Lua] {msg}")
        g['time'] = lambda: time.time()

    async def _run_loop(self):
        while self._running:
            try:
                # 1. Снимок тегов (синхронный)
                snapshot = await self.registry.get_snapshot()
                self._local_tags = {name: data.get('value') for name, data in snapshot.items()}

                # 2. Создаём свежий Lua-рантайм для hot-reload
                self._create_runtime()

                # 3. Выполняем скрипт в отдельном потоке
                await asyncio.to_thread(self._execute_script)

                # 4. Применяем изменения обратно в реестр (атомарно)
                for name, value in self._local_tags.items():
                    if snapshot.get(name, {}).get('value') != value:
                        await self.registry.update(name, value, "Good")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Lua execution error: {e}")
            await asyncio.sleep(self._interval)

    def _execute_script(self):
        """Синхронный запуск Lua-кода (вызывается из to_thread)."""
        if not self._lua or not self._script:
            return
        self._lua.execute(self._script)
