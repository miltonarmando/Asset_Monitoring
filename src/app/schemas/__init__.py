# Import all schemas to make them available from app.schemas
from .device import (
    # Enums
    DeviceVendor,
    DeviceStatus,
    
    # Device schemas
    DeviceBase,
    DeviceCreate,
    DeviceUpdate,
    DeviceInDBBase,
    Device,
    DeviceInDB,
    
    # Interface schemas
    InterfaceBase,
    InterfaceCreate,
    Interface,
    DeviceWithInterfaces,
    
    # Metrics schemas
    DeviceMetricBase,
    DeviceMetricCreate,
    DeviceMetric,
    InterfaceMetricBase,
    InterfaceMetricCreate,
    InterfaceMetric
)

__all__ = [
    # Enums
    'DeviceVendor',
    'DeviceStatus',
    
    # Device schemas
    'DeviceBase',
    'DeviceCreate',
    'DeviceUpdate',
    'DeviceInDBBase',
    'Device',
    'DeviceInDB',
    
    # Interface schemas
    'InterfaceBase',
    'InterfaceCreate',
    'Interface',
    'DeviceWithInterfaces',
    
    # Metrics schemas
    'DeviceMetricBase',
    'DeviceMetricCreate',
    'DeviceMetric',
    'InterfaceMetricBase',
    'InterfaceMetricCreate',
    'InterfaceMetric'
]
