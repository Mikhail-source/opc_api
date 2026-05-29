import asyncio
import logging
import time
from typing import Dict, Any, Optional
from backend.models.tag import Tag
from backend.models.events import TagUpdateEvent

logger = logging.getLogger(__name__)

class TagRegistry:
    def __init__(self):
        self._tags: Dict[str, Tag] = {}
        self._lock = asyncio.Lock()

    async def init_from_config(self, tags_config: list[dict]) -> None:
        async with self._lock:
            self._tags.clear()
            valid_keys = set(Tag.__annotations__.keys())
            for cfg in tags_config:
                try:
                    tag_data = {k: v for k, v in cfg.items() if k in valid_keys}
                    self._tags[tag_data["name"]] = Tag(**tag_data)
                except Exception as e:
                    logger.warning(f"⚠️ Skipping invalid tag config: {e}")
            logger.info(f"📦 Registry initialized with {len(self._tags)} tags.")

    async def update(self, name: str, value: Any, quality: str, timestamp: Optional[float] = None) -> Optional[TagUpdateEvent]:
        async with self._lock:
            tag = self._tags.get(name)
            if not tag: return None
            ts = timestamp or time.time()
            if tag.value != value or tag.quality != quality:
                tag.value = value
                tag.quality = quality
                tag.timestamp = ts
                return TagUpdateEvent(name=name, value=value, quality=quality, timestamp=ts)
            return None

    async def get_snapshot(self) -> Dict[str, dict]:
        async with self._lock:
            return {name: tag.to_dict() for name, tag in self._tags.items()}

    async def add_or_update_tag(self, tag_cfg: dict) -> bool:
        async with self._lock:
            name = tag_cfg.get("name")
            if not name: return False
            valid_keys = set(Tag.__annotations__.keys())
            try:
                self._tags[name] = Tag(**{k: v for k, v in tag_cfg.items() if k in valid_keys})
                return True
            except Exception as e:
                logger.error(f"❌ Failed to add/update tag {name}: {e}")
                return False

    async def remove_tag(self, name: str) -> bool:
        async with self._lock:
            return self._tags.pop(name, None) is not None
