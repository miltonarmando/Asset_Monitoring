# Import models here to make them available when importing from app.models
# This helps avoid circular imports
from .base import Base, BaseModel
from .device import Device, Interface, DeviceMetric, InterfaceMetric
from .alert import AlertRule, AlertEvent

# This makes these available when doing 'from app.models import *'
__all__ = [
    'Base',
    'BaseModel',
    'Device',
    'Interface',
    'DeviceMetric',
    'InterfaceMetric',
    'AlertRule',
    'AlertEvent'
]

# Initialize models to ensure they're registered with SQLAlchemy
def init_models():
    """Initialize all models to ensure they're registered with SQLAlchemy"""
    # Import models here to avoid circular imports
    from . import device  # noqa
    from . import alert  # noqa
