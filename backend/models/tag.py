from dataclasses import dataclass, field
from typing import Any
import time

@dataclass(slots=True)
class Tag:
    name: str
    value: Any = None
    quality: str = "Unknown"
    timestamp: float = field(default_factory=time.time)
    source: str = ""
    address: str = ""
    type: str = "float32"
    enabled: bool = True
    disconnect_value: Any = None
    poll_interval: float | None = None

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "quality": self.quality,
            "timestamp": self.timestamp,
            "type": self.type,
            "enabled": self.enabled
        }
