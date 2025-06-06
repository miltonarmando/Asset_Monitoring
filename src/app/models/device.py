from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class DeviceStatus(str, enum.Enum):
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"

class DeviceVendor(str, enum.Enum):
    CISCO = "cisco"
    HUAWEI = "huawei"
    OTHER = "other"

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, unique=True, index=True, nullable=False)
    ip_address = Column(String, unique=True, index=True, nullable=False)
    vendor = Column(Enum(DeviceVendor), nullable=False)
    model = Column(String)
    os_version = Column(String)
    snmp_community = Column(String, nullable=True)  # For SNMP v2c
    snmp_port = Column(Integer, default=161)
    ssh_username = Column(String, nullable=True)
    ssh_password = Column(String, nullable=True)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.UNKNOWN)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    interfaces = relationship("Interface", back_populates="device")
    metrics = relationship("DeviceMetric", back_populates="device")

class Interface(Base):
    __tablename__ = "interfaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    if_index = Column(Integer, nullable=False)
    mac_address = Column(String)
    mtu = Column(Integer)
    speed = Column(Integer)  # in bps
    admin_status = Column(Boolean, default=True)
    oper_status = Column(Boolean, default=False)
    device_id = Column(Integer, ForeignKey("devices.id"))
    
    # Relationships
    device = relationship("Device", back_populates="interfaces")
    metrics = relationship("InterfaceMetric", back_populates="interface")

class DeviceMetric(Base):
    __tablename__ = "device_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    cpu_usage = Column(Integer)  # percentage
    memory_usage = Column(Integer)  # percentage
    temperature = Column(Integer)  # in Celsius
    uptime = Column(Integer)  # in seconds
    
    # Relationships
    device = relationship("Device", back_populates="metrics")

class InterfaceMetric(Base):
    __tablename__ = "interface_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    interface_id = Column(Integer, ForeignKey("interfaces.id"))
    bytes_in = Column(Integer)  # bytes
    bytes_out = Column(Integer)  # bytes
    errors_in = Column(Integer)
    errors_out = Column(Integer)
    discards_in = Column(Integer)
    discards_out = Column(Integer)
    
    # Relationships
    interface = relationship("Interface", back_populates="metrics")
