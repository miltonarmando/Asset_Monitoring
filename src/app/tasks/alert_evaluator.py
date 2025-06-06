import asyncio
from sqlalchemy.orm import Session
from app.models import AlertRule, AlertEvent, DeviceMetric
from app.database import SessionLocal
from app.utils.snmp import SNMPClient
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AlertEvaluator:
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.snmp_client = SNMPClient()
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            try:
                await self.evaluate_all_rules()
            except Exception as e:
                logger.error(f"Error evaluating alert rules: {e}")
            await asyncio.sleep(self.interval)

    async def evaluate_all_rules(self):
        db: Session = SessionLocal()
        try:
            rules = db.query(AlertRule).filter(AlertRule.enabled == True).all()
            for rule in rules:
                # For demo: get last metric from DeviceMetric (should be by OID)
                metric = db.query(DeviceMetric).filter(
                    DeviceMetric.device_id == rule.device_id
                ).order_by(DeviceMetric.timestamp.desc()).first()
                if metric:
                    value = getattr(metric, 'value', None)
                    if value is not None and self.check_condition(value, rule.operator, rule.threshold):
                        # Check if already alerted recently (avoid duplicates)
                        recent = db.query(AlertEvent).filter(
                            AlertEvent.rule_id == rule.id,
                            AlertEvent.device_id == rule.device_id,
                            AlertEvent.timestamp > datetime.utcnow()
                        ).first()
                        if not recent:
                            event = AlertEvent(
                                rule_id=rule.id,
                                device_id=rule.device_id,
                                value=value,
                                message=f"Alert: {rule.name} triggered (value: {value})",
                                severity=rule.severity
                            )
                            db.add(event)
                            db.commit()
                            db.refresh(event)
                            logger.info(f"Alert triggered: {event.message}")
        finally:
            db.close()

    def check_condition(self, value, operator, threshold):
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '==':
            return value == threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        return False
