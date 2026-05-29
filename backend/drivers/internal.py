import asyncio
import math
import time
import random
from backend.drivers.base import BaseDriver

class InternalDriver(BaseDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_time = time.time()

    async def connect(self) -> bool: return True
    async def disconnect(self) -> None: pass

    async def poll_loop(self) -> None:
        interval = self.config.get("poll_interval", 1.0)
        t = time.time() - self._start_time

        for tag_name, tag_cfg in self.config.get("tags", {}).items():
            mode = tag_cfg.get("mode", "sine")
            if mode == "sine":
                val = math.sin(t * 2 * math.pi / tag_cfg.get("period", 10.0)) * tag_cfg.get("amplitude", 10.0)
            elif mode == "random":
                val = random.uniform(tag_cfg.get("min", 0), tag_cfg.get("max", 100))
            elif mode == "counter":
                val = int(t * tag_cfg.get("rate", 1.0))
            else:
                val = 0.0

            update = await self.registry.update(tag_name, round(val, 3), "Good")
            if update:
                await self.event_bus.publish("tag_updated", update)

        await asyncio.sleep(interval)
