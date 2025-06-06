from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app import schemas
from app.crud import crud_device as crud
from app.database import get_db
from app.models import Device, DeviceMetric, Interface, InterfaceMetric

router = APIRouter(prefix="", tags=["devices"])

@router.post("/", response_model=schemas.Device, status_code=status.HTTP_201_CREATED)
async def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    """
    Create a new network device
    
    - **hostname**: Device hostname (required)
    - **ip_address**: Device IP address (required)
    - **vendor**: Device vendor (cisco, huawei, etc.)
    - **model**: Device model
    - **os_version**: Operating system version
    - **snmp_community**: SNMP community string (if using SNMP v1/v2c)
    - **snmp_port**: SNMP port (default: 161)
    - **ssh_username**: SSH username (if using SSH)
    - **ssh_password**: SSH password (if using SSH)
    """
    # Check if device with same IP or hostname already exists
    db_device = crud.get_device_by_ip(db, ip_address=device.ip_address)
    if db_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this IP address already exists"
        )
        
    db_device = crud.get_device_by_hostname(db, hostname=device.hostname)
    if db_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this hostname already exists"
        )
    
    return crud.create_device(db=db, device=device)

@router.get("/", response_model=List[schemas.Device])
async def read_devices(
    skip: int = 0, 
    limit: int = 100,
    vendor: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of network devices with optional filtering
    """
    return crud.get_devices(
        db, 
        skip=skip, 
        limit=limit,
        vendor=vendor,
        status=status
    )

@router.get("/{device_id}", response_model=schemas.Device)
async def read_device(
    device_id: int = Path(..., title="The ID of the device to get"),
    db: Session = Depends(get_db)
):
    """
    Get a device by ID
    
    - **device_id**: The ID of the device to retrieve
    """
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return db_device

@router.put("/{device_id}", response_model=schemas.Device)
async def update_device(
    device_id: int = Path(..., title="The ID of the device to update"),
    device: schemas.DeviceUpdate = Body(..., title="The device data to update"),
    db: Session = Depends(get_db)
):
    """
    Update a device
    
    - **device_id**: The ID of the device to update
    - **device**: The updated device data
    """
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Check for duplicate IP or hostname if they are being updated
    if device.ip_address:
        existing = crud.get_device_by_ip(db, ip_address=device.ip_address)
        if existing and existing.id != device_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another device with this IP address already exists"
            )
            
    if device.hostname:
        existing = crud.get_device_by_hostname(db, hostname=device.hostname)
        if existing and existing.id != device_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another device with this hostname already exists"
            )
    
    return crud.update_device(db=db, db_device=db_device, device_update=device)

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int = Path(..., title="The ID of the device to delete"),
    db: Session = Depends(get_db)
):
    """
    Delete a device
    
    - **device_id**: The ID of the device to delete
    """
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    crud.delete_device(db=db, device_id=device_id)
    return None

@router.post(
    "/{device_id}/metrics/", 
    response_model=schemas.DeviceMetric, 
    status_code=status.HTTP_201_CREATED
)
async def create_device_metric(
    device_id: int = Path(..., title="The ID of the device to add metrics for"),
    metric: schemas.DeviceMetricCreate = Body(..., title="The device metrics data"),
    db: Session = Depends(get_db)
):
    """
    Add metrics for a device
    
    - **device_id**: The ID of the device
    - **metric**: The metrics data including CPU, memory, etc.
    """
    # Check if device exists
    db_device = crud.get_device(db, device_id=device_id)
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Update device status if needed
    if hasattr(metric, 'status') and metric.status:
        crud.update_device_status(
            db=db,
            device_id=device_id,
            status=metric.status,
            last_seen=datetime.utcnow()
        )
    
    # Add the metric
    return crud.add_device_metrics(db=db, device_id=device_id, metrics=metric)

@router.get(
    "/{device_id}/metrics/", 
    response_model=List[schemas.DeviceMetric]
)
async def get_device_metrics(
    device_id: int = Path(..., title="The ID of the device"),
    start_time: Optional[datetime] = Query(
        None, 
        description="Start time for filtering metrics"
    ),
    end_time: Optional[datetime] = Query(
        None, 
        description="End time for filtering metrics"
    ),
    limit: int = Query(
        100, 
        ge=1, 
        le=1000, 
        description="Maximum number of metrics to return"
    ),
    db: Session = Depends(get_db)
):
    """
    Get metrics for a specific device
    
    - **device_id**: The ID of the device
    - **start_time**: Optional start time for filtering metrics
    - **end_time**: Optional end time for filtering metrics
    - **limit**: Maximum number of metrics to return (1-1000, default: 100)
    """
    # Check if device exists
    if not crud.get_device(db, device_id=device_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Device not found"
        )
    
    return crud.get_device_metrics(
        db=db,
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )

@router.post(
    "/{device_id}/interfaces/",
    response_model=schemas.Interface,
    status_code=status.HTTP_201_CREATED
)
async def create_interface(
    device_id: int = Path(..., title="The ID of the device"),
    interface: schemas.InterfaceCreate = Body(..., title="The interface data"),
    db: Session = Depends(get_db)
):
    """
    Create a new interface for a device
    
    - **device_id**: The ID of the device
    - **interface**: The interface data including name, description, etc.
    """
    # Check if device exists
    db_device = crud.get_device(db, device_id=device_id)
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Check if interface with same name already exists for this device
    db_interface = crud.get_interface_by_name(db, device_id=device_id, interface_name=interface.name)
    if db_interface:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interface with name '{interface.name}' already exists for this device"
        )
    
    # Create a new Interface instance with the device_id
    db_interface = Interface(**interface.dict())
    db_interface.device_id = device_id
    
    # Add to the database
    db.add(db_interface)
    db.commit()
    db.refresh(db_interface)
    
    # Return the created interface
    return db_interface

@router.get(
    "/{device_id}/interfaces/", 
    response_model=List[schemas.Interface]
)
async def get_device_interfaces(
    device_id: int = Path(..., title="The ID of the device"),
    db: Session = Depends(get_db)
):
    """
    Get all interfaces for a specific device
    
    - **device_id**: The ID of the device
    """
    # Check if device exists
    if not crud.get_device(db, device_id=device_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Device not found"
        )
    
    # Get all interfaces for the device
    return crud.get_interfaces(db=db, device_id=device_id)

@router.post(
    "/{device_id}/interfaces/{interface_name:path}/metrics/", 
    response_model=schemas.InterfaceMetric, 
    status_code=status.HTTP_201_CREATED,
    summary="Add metrics for a network interface"
)
async def create_interface_metric(
    device_id: int = Path(..., title="The ID of the device"),
    interface_name: str = Path(..., title="The name of the interface (URL-encoded if it contains slashes)"),
    metric: schemas.InterfaceMetricCreate = Body(..., title="The interface metrics data"),
    db: Session = Depends(get_db)
):
    """
    Add metrics for a network interface
    
    - **device_id**: The ID of the device
    - **interface_name**: The name of the interface
    - **metric**: The metrics data including bytes in/out, errors, etc.
    """
    # Check if device exists
    db_device = crud.get_device(db, device_id=device_id)
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Check if interface exists
    db_interface = crud.get_interface_by_name(db, device_id=device_id, interface_name=interface_name)
    if not db_interface:
        # Create interface if it doesn't exist
        db_interface = crud.create_interface(
            db=db,
            interface=schemas.InterfaceCreate(
                name=interface_name,
                description=f"Auto-created interface {interface_name}",
                if_index=0,  # Will be updated by SNMP poller
                device_id=device_id
            )
        )
    
    # Create the metric data with the interface_id
    metric_data = metric.dict()
    metric_data['interface_id'] = db_interface.id
    
    # Create the metric
    db_metric = InterfaceMetric(**metric_data)
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    
    return db_metric

@router.get(
    "/{device_id}/interfaces/{interface_name:path}/metrics/", 
    response_model=List[schemas.InterfaceMetric],
    summary="Get metrics for a network interface"
)
async def get_interface_metrics(
    device_id: int = Path(..., title="The ID of the device"),
    interface_name: str = Path(..., title="The name of the interface (URL-encoded if it contains slashes)"),
    start_time: Optional[datetime] = Query(
        None, 
        description="Start time for filtering metrics"
    ),
    end_time: Optional[datetime] = Query(
        None, 
        description="End time for filtering metrics"
    ),
    limit: int = Query(
        100, 
        ge=1, 
        le=1000, 
        description="Maximum number of metrics to return"
    ),
    db: Session = Depends(get_db)
):
    """
    Get metrics for a specific interface
    
    - **device_id**: The ID of the device
    - **interface_name**: The name of the interface
    - **start_time**: Optional start time for filtering metrics
    - **end_time**: Optional end time for filtering metrics
    - **limit**: Maximum number of metrics to return (1-1000, default: 100)
    """
    # Check if device exists
    if not crud.get_device(db, device_id=device_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Device not found"
        )
    
    # Check if interface exists
    if not crud.get_interface_by_name(db, device_id=device_id, interface_name=interface_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interface not found"
        )
    
    return crud.get_interface_metrics(
        db=db,
        device_id=device_id,
        interface_name=interface_name,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )
