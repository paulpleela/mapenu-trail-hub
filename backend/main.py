"""
MAPENU Backend - Main FastAPI Application
Refactored modular version with route separation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Import database clients
from database import supabase, supabase_service
from config import CORS_ORIGINS

# Import shared application state
import app_state

# Import route modules
from routes import trails_router, uploads_router, analysis_router, maps_router

# Load environment variables
load_dotenv()

# Initialize DEM analyzer
try:
    from utils.real_dem_analysis import RealDEMAnalyzer

    dem_path = os.path.join(
        os.path.dirname(__file__), "data", "QSpatial", "DEM", "1 Metre"
    )
    dem_analyzer = RealDEMAnalyzer(dem_path)
    app_state.set_dem_analyzer(dem_analyzer)
    print(f"✅ DEM Analyzer initialized with {len(dem_analyzer.dem_files)} DEM files")
except ImportError as e:
    print(f"⚠️  DEM analysis not available: {e}")
    dem_analyzer = None
except Exception as e:
    print(f"❌ DEM initialization error: {e}")
    dem_analyzer = None

# Initialize LiDAR extractor
try:
    from utils.lidar_extraction import LiDARExtractor

    lidar_cache_path = "/tmp/lidar_cache"
    lidar_extractor = LiDARExtractor(lidar_cache_path, supabase_client=supabase)
    app_state.set_lidar_extractor(lidar_extractor)
    print(f"✅ LiDAR Extractor initialized with {len(lidar_extractor.lidar_files)} LiDAR files")
except ImportError as e:
    print(f"⚠️  LiDAR extraction not available: {e}")
    lidar_extractor = None
except Exception as e:
    print(f"❌ LiDAR initialization error: {e}")
    lidar_extractor = None

# Create FastAPI application
app = FastAPI(
    title="MAPENU API",
    description="Trail analysis API with multi-source elevation data",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(trails_router, tags=["Trails"])
app.include_router(uploads_router, tags=["Uploads"])
app.include_router(analysis_router, tags=["Analysis"])
app.include_router(maps_router, tags=["Maps"])


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "name": "MAPENU API",
        "version": "2.0.0",
        "status": "operational",
        "description": "Trail analysis API (Refactored)",
        "features": {
            "dem_analyzer": app_state.get_dem_analyzer() is not None,
            "lidar_extractor": app_state.get_lidar_extractor() is not None,
            "supabase_connected": supabase is not None,
        },
        "documentation": "/docs",
    }


@app.on_event("startup")
async def startup_event():
    """Run startup tasks"""
    print("🚀 MAPENU Backend starting...")
    print(f"📊 DEM: {'✅' if app_state.get_dem_analyzer() else '❌'}")
    print(f"🗺️  LiDAR: {'✅' if app_state.get_lidar_extractor() else '❌'}")
    print(f"🔐 Supabase: {'✅' if supabase else '❌'}")
    print("✅ Ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks"""
    print("👋 MAPENU Backend shutting down...")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
