from dataclasses import dataclass, field
from typing import Any
import time

@dataclass
class TagUpdateEvent:
    name: str
    value: Any
    quality: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class DriverErrorEvent:
    driver_id: str
    error: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class SystemEvent:
    type: str
    message: str
    timestamp: float = field(default_factory=time.time)
