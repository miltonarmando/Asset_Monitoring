import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import SessionLocal
from ..utils.snmp import SNMPClient
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class SNMPCollector:
    def __init__(self):
        self.snmp = SNMPClient()
        self.running = False
        self.task = None

    async def start(self, interval: int = 300):
        """Start the SNMP collector with the specified interval in seconds."""
        if self.running:
            logger.warning("SNMP collector is already running")
            return

        self.running = True
        logger.info(f"Starting SNMP collector with {interval}s interval")
        
        while self.running:
            try:
                await self.collect_all_devices()
            except Exception as e:
                logger.error(f"Error in SNMP collection: {str(e)}", exc_info=True)
            
            # Wait for the next collection interval
            await asyncio.sleep(interval)
    
    def stop(self):
        """Stop the SNMP collector."""
        self.running = False
        if self.task:
            self.task.cancel()
        logger.info("SNMP collector stopped")

    async def collect_all_devices(self):
        """Collect metrics from all enabled devices."""
        db = SessionLocal()
        try:
            # Get all devices that have SNMP enabled
            devices = crud.get_devices(db, skip=0, limit=1000)  # Adjust limit as needed
            logger.info(f"Collecting metrics for {len(devices)} devices")
            
            for device in devices:
                if not device.snmp_enabled:
                    continue
                    
                try:
                    await self.collect_device_metrics(db, device)
                except Exception as e:
                    logger.error(f"Error collecting metrics for device {device.id}: {str(e)}", exc_info=True)
                    # Update device status to indicate error
                    device.status = "error"
                    db.commit()
                    
        finally:
            db.close()
    
    async def collect_device_metrics(self, db: Session, device: models.Device):
        """Collect metrics for a single device."""
        try:
            # Update device status to indicate we're collecting
            device.status = "collecting"
            device.last_seen = datetime.utcnow()
            db.commit()
            
            # Get basic device info
            device_info = await self.snmp.get_device_info(device.ip_address)
            
            # Get CPU metrics
            cpu_metrics = await self.collect_cpu_metrics(device.ip_address)
            
            # Get interface metrics
            interface_metrics = await self.collect_interface_metrics(device.ip_address)
            
            # Update device status
            device.status = "online"
            db.commit()
            
            return {
                "device_info": device_info,
                "cpu_metrics": cpu_metrics,
                "interface_metrics": interface_metrics
            }
            
        except Exception as e:
            logger.error(f"Error collecting metrics for device {device.id}: {str(e)}", exc_info=True)
            device.status = "error"
            db.commit()
            raise
    
    async def collect_cpu_metrics(self, host: str) -> Dict[str, Any]:
        """Collect CPU metrics from the device."""
        # OID for CPU usage (1.3.6.1.2.1.25.3.3.1.2 - hrProcessorLoad)
        oids = ["1.3.6.1.2.1.25.3.3.1.2"]
        results = await self.snmp.get_multiple(host, oids)
        
        # Process CPU metrics
        cpu_usage = []
        for oid, result in results.items():
            if not result.get("error"):
                cpu_usage.append({
                    "index": oid.split(".")[-1],
                    "usage_percent": int(result["value"])
                })
        
        return {"cpus": cpu_usage}
    
    async def collect_interface_metrics(self, host: str) -> Dict[str, Any]:
        """Collect interface metrics from the device."""
        # OIDs for interface metrics
        oids = [
            "1.3.6.1.2.1.2.2.1.2",  # ifDescr
            "1.3.6.1.2.1.2.2.1.7",  # ifAdminStatus
            "1.3.6.1.2.1.2.2.1.8",  # ifOperStatus
            "1.3.6.1.2.1.2.2.1.10", # ifInOctets
            "1.3.6.1.2.1.2.2.1.16", # ifOutOctets
            "1.3.6.1.2.1.2.2.1.14", # ifInErrors
            "1.3.6.1.2.1.2.2.1.20", # ifOutErrors
            "1.3.6.1.2.1.2.2.1.13", # ifInDiscards
            "1.3.6.1.2.1.2.2.1.19"   # ifOutDiscards
        ]
        
        results = await self.snmp.get_multiple(host, oids)
        
        # Process interface metrics
        interfaces = {}
        
        # First, get all interface indices
        if_descr_oid = "1.3.6.1.2.1.2.2.1.2"
        for oid, result in results.items():
            if oid.startswith(if_descr_oid) and not result.get("error"):
                if_index = oid.split(".")[-1]
                interfaces[if_index] = {
                    "name": result["value"],
                    "index": if_index
                }
        
        # Add other metrics to interfaces
        for oid, result in results.items():
            if not result.get("value") or result.get("error"):
                continue
                
            parts = oid.split(".")
            base_oid = ".".join(parts[:-1])
            if_index = parts[-1]
            
            if if_index not in interfaces:
                continue
                
            if base_oid == "1.3.6.1.2.1.2.2.1.7":  # ifAdminStatus
                interfaces[if_index]["admin_status"] = result["value"]
            elif base_oid == "1.3.6.1.2.1.2.2.1.8":  # ifOperStatus
                interfaces[if_index]["oper_status"] = result["value"]
            elif base_oid == "1.3.6.1.2.1.2.2.1.10":  # ifInOctets
                interfaces[if_index]["bytes_in"] = int(result["value"])
            elif base_oid == "1.3.6.1.2.1.2.2.1.16":  # ifOutOctets
                interfaces[if_index]["bytes_out"] = int(result["value"])
            elif base_oid == "1.3.6.1.2.1.2.2.1.14":  # ifInErrors
                interfaces[if_index]["errors_in"] = int(result["value"])
            elif base_oid == "1.3.6.1.2.1.2.2.1.20":  # ifOutErrors
                interfaces[if_index]["errors_out"] = int(result["value"])
            elif base_oid == "1.3.6.1.2.1.2.2.1.13":  # ifInDiscards
                interfaces[if_index]["discards_in"] = int(result["value"])
            elif base_oid == "1.3.6.1.2.1.2.2.1.19":  # ifOutDiscards
                interfaces[if_index]["discards_out"] = int(result["value"])
        
        return {"interfaces": list(interfaces.values())}
