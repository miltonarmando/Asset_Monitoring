from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from .. import schemas
from ..models import Device, Interface, DeviceMetric, InterfaceMetric
from ..database import SessionLocal
from fastapi import HTTPException, status

def get_device(db: Session, device_id: int) -> Optional[Device]:
    """Get a device by ID"""
    return db.query(Device).filter(Device.id == device_id).first()

def get_device_by_hostname(db: Session, hostname: str) -> Optional[Device]:
    """Get a device by hostname"""
    return db.query(Device).filter(Device.hostname == hostname).first()

def get_device_by_ip(db: Session, ip_address: str) -> Optional[Device]:
    """Get a device by IP address"""
    return db.query(Device).filter(Device.ip_address == ip_address).first()

def get_devices(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    vendor: Optional[str] = None,
    status: Optional[str] = None
) -> List[Device]:
    """Get a list of devices with optional filtering"""
    query = db.query(Device)
    
    if vendor:
        query = query.filter(Device.vendor == vendor)
    if status:
        query = query.filter(Device.status == status)
        
    return query.offset(skip).limit(limit).all()

def create_device(db: Session, device: schemas.DeviceCreate) -> Device:
    """Create a new device"""
    # Convert Pydantic model to dict and exclude unset values
    device_data = device.dict(exclude_unset=True)
    
    # Create the device
    db_device = Device(**device_data)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def update_device(
    db: Session, 
    db_device: Device, 
    device_update: Union[schemas.DeviceUpdate, Dict[str, Any]]
) -> Device:
    """
    Update a device
    
    Args:
        db: Database session
        db_device: Device model instance to update
        device_update: Either a DeviceUpdate Pydantic model or a dict with fields to update
        
    Returns:
        Updated Device model instance
    """
    # Convert Pydantic model to dict if needed
    update_data = device_update.dict(exclude_unset=True) \
        if not isinstance(device_update, dict) else device_update
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_device, field, value)
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: int) -> Optional[Device]:
    """Delete a device"""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if db_device:
        db.delete(db_device)
        db.commit()
        return db_device
    return None

def update_device_status(
    db: Session, 
    device_id: int, 
    status: str, 
    last_seen: datetime = None
) -> Optional[Device]:
    """Update device status and last seen timestamp"""
    db_device = get_device(db, device_id)
    if not db_device:
        return None
        
    db_device.status = status
    if last_seen:
        db_device.last_seen = last_seen
    else:
        db_device.last_seen = datetime.utcnow()
        
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def add_device_metrics(
    db: Session, 
    device_id: int, 
    metrics: schemas.DeviceMetricCreate
) -> DeviceMetric:
    """
    Add device metrics
    
    Args:
        db: Database session
        device_id: ID of the device to add metrics for
        metrics: Device metrics data
        
    Returns:
        Created DeviceMetric instance
    """
    # Convert Pydantic model to dict and add device_id
    metrics_data = metrics.dict(exclude_unset=True)
    metrics_data['device_id'] = device_id
    
    # Create the metric
    db_metric = DeviceMetric(**metrics_data)
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

def add_interface_metrics(
    db: Session,
    device_id: int,
    interface_name: str,
    metrics: schemas.InterfaceMetricCreate
) -> InterfaceMetric:
    """
    Add interface metrics
    
    Args:
        db: Database session
        device_id: ID of the device the interface belongs to
        interface_name: Name of the interface
        metrics: Interface metrics data
        
    Returns:
        Created InterfaceMetric instance
    """
    # Get the interface to get its ID
    db_interface = get_interface_by_name(db, device_id=device_id, interface_name=interface_name)
    if not db_interface:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interface '{interface_name}' not found for device {device_id}"
        )
    
    # Convert Pydantic model to dict and add required fields
    metrics_data = metrics.dict(exclude_unset=True)
    metrics_data.update({
        'interface_id': db_interface.id
    })
    
    # Create the metric
    db_metric = InterfaceMetric(**metrics_data)
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

def get_interfaces(
    db: Session,
    device_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Interface]:
    """
    Get all interfaces for a device
    
    Args:
        db: Database session
        device_id: ID of the device
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Interface instances
    """
    return db.query(Interface)\
        .filter(Interface.device_id == device_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_interface_by_name(
    db: Session,
    device_id: int,
    interface_name: str
) -> Optional[Interface]:
    """
    Get an interface by name for a specific device
    
    Args:
        db: Database session
        device_id: ID of the device
        interface_name: Name of the interface
        
    Returns:
        Interface instance if found, None otherwise
    """
    return db.query(Interface)\
        .filter(
            and_(
                Interface.device_id == device_id,
                Interface.name == interface_name
            )
        )\
        .first()

def create_interface(
    db: Session,
    interface: schemas.InterfaceCreate
) -> Interface:
    """
    Create a new interface
    
    Args:
        db: Database session
        interface: Interface data
        
    Returns:
        Created Interface instance with all fields
    """
    # Create a new Interface instance with all fields from the schema
    db_interface = Interface(**interface.dict())
    
    # Add to the database
    db.add(db_interface)
    db.commit()
    
    # Refresh to get all fields including auto-generated ones
    db.refresh(db_interface)
    
    # Ensure we return the complete interface with all fields
    return db_interface

def get_interface_metrics(
    db: Session,
    device_id: int,
    interface_name: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100
) -> List[InterfaceMetric]:
    """
    Get metrics for a specific interface
    
    Args:
        db: Database session
        device_id: ID of the device
        interface_name: Name of the interface
        start_time: Optional start time for filtering
        end_time: Optional end time for filtering
        limit: Maximum number of records to return
        
    Returns:
        List of InterfaceMetric instances
    """
    # First, get the interface to get its ID
    db_interface = get_interface_by_name(db, device_id=device_id, interface_name=interface_name)
    if not db_interface:
        return []
    
    # Now query the metrics using the interface_id
    query = db.query(InterfaceMetric).filter(
        InterfaceMetric.interface_id == db_interface.id
    )
    
    if start_time:
        query = query.filter(InterfaceMetric.timestamp >= start_time)
    if end_time:
        query = query.filter(InterfaceMetric.timestamp <= end_time)
        
    return query.order_by(InterfaceMetric.timestamp.desc()).limit(limit).all()

def get_device_metrics(
    db: Session,
    device_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100
) -> List[DeviceMetric]:
    """
    Get metrics for a specific device
    
    Args:
        db: Database session
        device_id: ID of the device
        start_time: Optional start time for filtering
        end_time: Optional end time for filtering
        limit: Maximum number of records to return
        
    Returns:
        List of DeviceMetric instances
    """
    query = db.query(DeviceMetric).filter(
        DeviceMetric.device_id == device_id
    )
    
    if start_time:
        query = query.filter(DeviceMetric.timestamp >= start_time)
    if end_time:
        query = query.filter(DeviceMetric.timestamp <= end_time)
        
    return query.order_by(DeviceMetric.timestamp.desc()).limit(limit).all()
