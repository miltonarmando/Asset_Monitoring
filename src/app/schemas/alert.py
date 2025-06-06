from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class AlertRuleBase(BaseModel):
    name: str
    device_id: Optional[int] = None
    oid: str
    operator: str
    threshold: float
    severity: str = "warning"
    enabled: bool = True

class AlertRuleCreate(AlertRuleBase):
    pass

class AlertRule(AlertRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AlertEventBase(BaseModel):
    rule_id: int
    device_id: int
    value: float
    message: str
    severity: str
    acknowledged: bool = False
    extra: Optional[Any] = None

class AlertEventCreate(AlertEventBase):
    pass

class AlertEvent(AlertEventBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
