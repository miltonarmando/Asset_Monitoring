from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas import alert as schemas
from app.models import alert as models
from app.database import get_db

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.post("/rules/", response_model=schemas.AlertRule)
def create_alert_rule(rule: schemas.AlertRuleCreate, db: Session = Depends(get_db)):
    db_rule = models.AlertRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.get("/rules/", response_model=List[schemas.AlertRule])
def list_alert_rules(db: Session = Depends(get_db)):
    return db.query(models.AlertRule).all()

@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.AlertRule).get(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return None

@router.get("/events/", response_model=List[schemas.AlertEvent])
def list_alert_events(db: Session = Depends(get_db)):
    return db.query(models.AlertEvent).order_by(models.AlertEvent.timestamp.desc()).all()

@router.post("/events/ack/{event_id}")
def acknowledge_alert_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.AlertEvent).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.acknowledged = True
    db.commit()
    db.refresh(event)
    return {"ok": True, "event_id": event_id}
