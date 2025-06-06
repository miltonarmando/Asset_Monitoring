from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class DeviceVendor(str, Enum):
    cisco = "cisco"
    huawei = "huawei"
    other = "other"

class DeviceStatus(str, Enum):
    up = "up"
    down = "down"
    unknown = "unknown"

# Shared properties
class DeviceBase(BaseModel):
    hostname: str = Field(..., max_length=255)
    ip_address: str = Field(..., max_length=45)  # IPv6 compatible
    vendor: DeviceVendor
    model: Optional[str] = Field(None, max_length=100)
    os_version: Optional[str] = Field(None, max_length=100)
    snmp_community: Optional[str] = Field(None, max_length=100)
    snmp_port: int = Field(default=161, ge=1, le=65535)
    ssh_username: Optional[str] = Field(None, max_length=100)
    ssh_password: Optional[str] = Field(None, max_length=100)

# Properties to receive on device creation
class DeviceCreate(DeviceBase):
    pass

# Properties to receive on device update
class DeviceUpdate(DeviceBase):
    hostname: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    vendor: Optional[DeviceVendor] = None
    snmp_port: Optional[int] = Field(None, ge=1, le=65535)

# Properties shared by models stored in DB
class DeviceInDBBase(DeviceBase):
    id: int
    status: DeviceStatus = DeviceStatus.unknown
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Properties to return to client
class Device(DeviceInDBBase):
    pass

# Properties stored in DB
class DeviceInDB(DeviceInDBBase):
    pass

# Nested schemas for relationships
class InterfaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    if_index: int
    mac_address: Optional[str] = None
    mtu: Optional[int] = None
    speed: Optional[int] = None
    admin_status: bool = True
    oper_status: bool = False

class InterfaceCreate(InterfaceBase):
    pass

class Interface(InterfaceBase):
    id: int
    device_id: Optional[int] = None  # Make device_id optional in response
    
    class Config:
        orm_mode = True
        
    @validator('device_id', pre=True, always=True)
    def set_device_id(cls, v, values):
        return v or values.get('device_id')

class DeviceWithInterfaces(Device):
    interfaces: List[Interface] = []

# Metrics schemas
class DeviceMetricBase(BaseModel):
    cpu_usage: Optional[int] = Field(None, ge=0, le=100)  # percentage
    memory_usage: Optional[int] = Field(None, ge=0, le=100)  # percentage
    temperature: Optional[int] = None  # Celsius
    uptime: Optional[int] = None  # seconds

class DeviceMetricCreate(DeviceMetricBase):
    device_id: int
    timestamp: Optional[datetime] = None

class DeviceMetric(DeviceMetricBase):
    id: int
    device_id: int
    timestamp: datetime
    
    class Config:
        orm_mode = True

class InterfaceMetricBase(BaseModel):
    bytes_in: Optional[int] = None  # bytes
    bytes_out: Optional[int] = None  # bytes
    errors_in: Optional[int] = None
    errors_out: Optional[int] = None
    discards_in: Optional[int] = None
    discards_out: Optional[int] = None

class InterfaceMetricCreate(InterfaceMetricBase):
    interface_id: Optional[int] = None
    timestamp: Optional[datetime] = None

class InterfaceMetric(InterfaceMetricBase):
    id: int
    interface_id: int
    timestamp: datetime
    
    class Config:
        orm_mode = True
