import asyncio
import logging
from pymodbus.client import AsyncModbusTcpClient
from backend.drivers.base import BaseDriver

logger = logging.getLogger(__name__)

class ModbusTcpDriver(BaseDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.host = self.config.get("host", "127.0.0.1")
        self.port = self.config.get("port", 502)

    async def connect(self) -> bool:
        self.client = AsyncModbusTcpClient(self.host, port=self.port)
        try:
            await self.client.connect()
            return self.client.connected
        except Exception as e:
            logger.error(f"Modbus connection failed: {e}")
            return False

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None

    async def poll_loop(self) -> None:
        tags = self.config.get("tags", {})
        if not tags:
            await asyncio.sleep(1.0)
            return

        for tag_name, tag_cfg in tags.items():
            addr = tag_cfg.get("address", 0)
            try:
                result = await self.client.read_holding_registers(int(addr), count=1, slave=1)
                if result.isError():
                    raise Exception(f"Modbus error at {addr}")
                val = result.registers[0] / tag_cfg.get("scale", 1.0)
                update = await self.registry.update(tag_name, val, "Good")
                if update:
                    await self.event_bus.publish("tag_updated", update)
            except Exception as e:
                await self.registry.update(tag_name, None, "Bad")
        await asyncio.sleep(self.config.get("poll_interval", 1.0))
