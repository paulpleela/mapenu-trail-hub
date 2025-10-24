"""
Route modules initialization
Imports and exports all API route routers
"""
from .trails import router as trails_router
from .uploads import router as uploads_router
from .analysis import router as analysis_router
from .maps import router as maps_router

__all__ = ["trails_router", "uploads_router", "analysis_router", "maps_router"]
