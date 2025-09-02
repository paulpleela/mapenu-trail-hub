#!/usr/bin/env python3
"""
Setup script for MAPENU enhanced visualization features
Run this to install required packages for DEM and LiDAR analysis
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command):
    """Run a command and return success status"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is suitable"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required for geospatial packages")
        return False
    print(f"✓ Python {version.major}.{version.minor} is suitable")
    return True

def install_geospatial_packages():
    """Install geospatial packages in the correct order"""
    
    print("\n🚀 Installing geospatial packages for enhanced trail visualization...")
    
    # Core packages first
    essential_packages = [
        "numpy>=1.24.0",
        "pandas>=2.0.0", 
        "matplotlib>=3.7.0",
        "scipy>=1.10.0"
    ]
    
    print("\n📦 Installing essential scientific packages...")
    for package in essential_packages:
        if not run_command(f"pip install {package}"):
            print(f"❌ Failed to install {package}")
            return False
    
    # Geospatial packages (order matters due to dependencies)
    geospatial_packages = [
        "fiona>=1.9.0",
        "pyproj>=3.6.0", 
        "shapely>=2.0.0",
        "rasterio>=1.3.0",
        "geopandas>=0.13.0",
    ]
    
    print("\n🌍 Installing geospatial packages...")
    for package in geospatial_packages:
        if not run_command(f"pip install {package}"):
            print(f"❌ Failed to install {package}")
            return False
    
    # LiDAR and visualization packages
    specialized_packages = [
        "laspy>=2.4.0",
        "plotly>=5.15.0",
        "seaborn>=0.12.0"
    ]
    
    print("\n📡 Installing LiDAR and visualization packages...")
    for package in specialized_packages:
        if not run_command(f"pip install {package}"):
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def test_imports():
    """Test if key packages can be imported"""
    print("\n🧪 Testing package imports...")
    
    test_packages = [
        ("rasterio", "DEM processing"),
        ("geopandas", "Geospatial data handling"),
        ("laspy", "LiDAR processing"),
        ("matplotlib.pyplot", "Plotting"),
        ("numpy", "Numerical operations"),
        ("shapely.geometry", "Geometric operations")
    ]
    
    failed_imports = []
    
    for package, description in test_packages:
        try:
            __import__(package)
            print(f"✓ {package} - {description}")
        except ImportError as e:
            print(f"✗ {package} - {description} - FAILED: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ {len(failed_imports)} packages failed to import")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def create_test_script():
    """Create a test script to verify the installation"""
    test_script = '''
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dem_trail_analysis import TrailDEMAnalyzer
from lidar_trail_analysis import TrailLiDARAnalyzer

def test_installation():
    print("🧪 Testing MAPENU enhanced visualization installation...")
    
    # Test DEM analyzer initialization
    try:
        analyzer = TrailDEMAnalyzer("test_folder", "test_file.gpx")
        print("✓ DEM Analyzer can be initialized")
    except Exception as e:
        print(f"✗ DEM Analyzer failed: {e}")
        return False
    
    # Test LiDAR analyzer initialization  
    try:
        analyzer = TrailLiDARAnalyzer("test_folder", "test_file.gpx")
        print("✓ LiDAR Analyzer can be initialized")
    except Exception as e:
        print(f"✗ LiDAR Analyzer failed: {e}")
        return False
    
    print("\\n✅ Installation test completed successfully!")
    print("🎉 Enhanced trail visualization features are ready to use!")
    return True

if __name__ == "__main__":
    test_installation()
'''
    
    with open("test_installation.py", "w") as f:
        f.write(test_script)
    
    print("📄 Created test_installation.py")

def main():
    print("🗺️  MAPENU Enhanced Visualization Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("❌ Please run this script from the MAPENU root directory")
        sys.exit(1)
    
    # Install packages
    if not install_geospatial_packages():
        print("\n❌ Package installation failed")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n❌ Package testing failed")
        sys.exit(1)
    
    # Create test script
    create_test_script()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run: python test_installation.py")
    print("2. Add the enhanced visualization API endpoints to your main.py")
    print("3. Update your frontend to use the new TrailVisualization component")
    print("\n💡 Tips:")
    print("- Your 6GB of QLD Government data will be processed on-demand")
    print("- DEM analysis provides elevation profiles and terrain analysis") 
    print("- LiDAR analysis provides vegetation classification and point cloud visualization")
    print("- Both analyses create interactive visualizations for the frontend")
    
    print("\n🔧 Troubleshooting:")
    print("- If packages fail to install, try: pip install --upgrade pip")
    print("- On Windows, you may need Visual Studio Build Tools for some packages")
    print("- For large datasets, consider increasing system memory or processing smaller chunks")

if __name__ == "__main__":
    main()
