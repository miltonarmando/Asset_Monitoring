from fastapi import APIRouter

from app.api.endpoints import devices, alerts, alerts_ws

api_router = APIRouter()
# Include the devices router with the /devices prefix
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(alerts_ws.router)
