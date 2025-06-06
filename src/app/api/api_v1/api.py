from fastapi import APIRouter

from app.api.endpoints import devices

api_router = APIRouter()
# Include the devices router with the /devices prefix
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
