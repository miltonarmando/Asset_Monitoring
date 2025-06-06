from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class AlertRule(Base):
    __tablename__ = "alert_rules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)  # Null = global
    oid = Column(String, nullable=False)
    operator = Column(String, nullable=False)  # e.g. '>', '<', '=='
    threshold = Column(Float, nullable=False)
    severity = Column(String, nullable=False, default="warning")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    device = relationship("Device", back_populates="alert_rules")

class AlertEvent(Base):
    __tablename__ = "alert_events"
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    value = Column(Float, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    acknowledged = Column(Boolean, default=False)
    extra = Column(JSON, nullable=True)

    rule = relationship("AlertRule")
    device = relationship("Device")
