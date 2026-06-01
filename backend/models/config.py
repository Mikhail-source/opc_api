from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, List, Optional
import re

class TagConfig(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    path: str = ""
    source: str = "internal"
    address: str = ""
    type: str = "float32"
    value: Any = None
    quality: str = "Unknown"
    enabled: bool = True
    disconnect_value: Any = None
    poll_interval: Optional[float] = Field(None, ge=0.1)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_\-.]+$', v):
            raise ValueError('Tag name must contain only letters, numbers, underscore, hyphen, dot')
        return v

class DriverConfig(BaseModel):
    id: str = Field(..., min_length=1)
    type: str = Field(..., pattern='^(internal|modbus_tcp|opcua_client)$')
    host: Optional[str] = None
    port: Optional[int] = None
    poll_interval: float = 1.0
    tags: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1 <= v <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v

class OutputConfig(BaseModel):
    type: str = Field(..., pattern='^(rest_api|websocket|opcua_server|prometheus)$')
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)

class ProjectConfig(BaseModel):
    project: Dict[str, str] = Field(default_factory=lambda: {"name": "Unnamed", "version": "1.0"})
    tags: List[TagConfig] = Field(default_factory=list)
    drivers: List[DriverConfig] = Field(default_factory=list)
    outputs: List[OutputConfig] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    script: Dict[str, str] = Field(default_factory=lambda: {"content": ""})
