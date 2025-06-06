from pysnmp.hlapi import (
    getCmd, SnmpEngine, CommunityData, UdpTransportTarget,
    ContextData, ObjectType, ObjectIdentity
)
from pysnmp.proto import error
from typing import List, Dict, Any, Optional, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor
from ..core.config import settings

class SNMPClient:
    def __init__(self, community: str = None, timeout: int = None, retries: int = None):
        self.community = community or settings.SNMP_COMMUNITY
        self.timeout = timeout or settings.SNMP_TIMEOUT
        self.retries = retries or settings.SNMP_RETRIES
        self.executor = ThreadPoolExecutor(max_workers=10)

    async def get(self, host: str, oid: str) -> Dict[str, Any]:
        """Get a single SNMP OID value asynchronously."""
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                self.executor,
                self._get_sync,
                host,
                oid
            )
            return {"oid": oid, "value": result}
        except Exception as e:
            return {"oid": oid, "error": str(e)}

    def _get_sync(self, host: str, oid: str) -> Any:
        """Synchronous SNMP GET operation."""
        error_indication, error_status, error_index, var_binds = next(
            getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((host, 161), timeout=self.timeout, retries=self.retries),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
        )

        if error_indication:
            raise Exception(f"SNMP error: {error_indication}")
        elif error_status:
            raise Exception(
                f"SNMP error: {error_status.prettyPrint()} at "
                f"{error_index and var_binds[int(error_index) - 1][0] or '?'}"
            )
        else:
            for var_bind in var_binds:
                return var_bind[1].prettyPrint()

    async def get_multiple(self, host: str, oids: List[str]) -> Dict[str, Any]:
        """Get multiple SNMP OIDs asynchronously."""
        tasks = [self.get(host, oid) for oid in oids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {result["oid"]: result for result in results}

    async def get_device_info(self, host: str) -> Dict[str, Any]:
        """Get basic device information using common SNMP OIDs."""
        oids = {
            "sysDescr": "1.3.6.1.2.1.1.1.0",
            "sysName": "1.3.6.1.2.1.1.5.0",
            "sysLocation": "1.3.6.1.2.1.1.6.0",
            "sysContact": "1.3.6.1.2.1.1.4.0",
            "sysUpTime": "1.3.6.1.2.1.1.3.0"
        }
        
        results = await self.get_multiple(host, list(oids.values()))
        
        # Map results back to their names
        return {
            name: results[oid].get("value") if not results[oid].get("error") else None
            for name, oid in oids.items()
        }
