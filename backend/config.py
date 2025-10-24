"""
Configuration and environment variables for MAPENU backend.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Validate required configuration
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing Supabase credentials. Please check your .env file.")

# Paths
DEM_PATH = os.path.join(
    os.path.dirname(__file__), "data", "QSpatial", "DEM", "1 Metre"
)
LIDAR_CACHE_PATH = "/tmp/lidar_cache"

# CORS Configuration
CORS_ORIGINS = ["*"]  # Configure as needed for production

# Application Settings
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB
TEMP_DIR = "/tmp"
