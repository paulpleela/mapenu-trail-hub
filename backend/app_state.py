"""
Shared application state and singletons
Provides access to dem_analyzer and lidar_extractor across modules
"""

# Global instances (initialized by main.py on startup)
dem_analyzer = None
lidar_extractor = None


def set_dem_analyzer(analyzer):
    """Set the global DEM analyzer instance"""
    global dem_analyzer
    dem_analyzer = analyzer


def set_lidar_extractor(extractor):
    """Set the global LiDAR extractor instance"""
    global lidar_extractor
    lidar_extractor = extractor


def get_dem_analyzer():
    """Get the global DEM analyzer instance"""
    return dem_analyzer


def get_lidar_extractor():
    """Get the global LiDAR extractor instance"""
    return lidar_extractor
