# MAPENU Backend API

**Trail Analysis API with Multi-Source Elevation Data**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Code Coverage](https://img.shields.io/badge/coverage-27%25-yellow.svg)](./htmlcov/index.html)
[![Tests](https://img.shields.io/badge/tests-13%20passing-brightgreen.svg)](./tests/)

## 📖 Overview

MAPENU Backend is a powerful RESTful API for trail analysis and visualization. It processes GPS data, LiDAR point clouds, DEM (Digital Elevation Model) files, and XLSX elevation data to provide comprehensive trail analytics including difficulty ratings, terrain variety, weather exposure, and elevation profiles.

### ✨ Key Features

- 🗺️ **Multi-source elevation data** - GPX, LiDAR (.las/.laz), QSpatial DEM, XLSX
- 📊 **Advanced trail analytics** - Difficulty scoring, terrain variety, rolling hills detection
- 🌦️ **Weather exposure analysis** - Elevation-based risk assessment
- 📈 **Elevation profile comparison** - Compare data from multiple sources
- 🎯 **Trail similarity matching** - Find trails with similar characteristics
- 🗺️ **Interactive map generation** - Folium-based trail visualization
- 🔄 **Real-time DEM processing** - High-resolution terrain analysis
- 📁 **File uploads** - Support for GPX, LiDAR, and XLSX files

## 🏗️ Architecture

### Modular Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── database.py             # Supabase client initialization
├── app_state.py            # Shared application state
├── lidar_extraction.py     # LiDAR processing service
├── real_dem_analysis.py    # DEM analysis service
│
├── routes/                 # API endpoints (2,482 lines)
│   ├── trails.py           # Trail CRUD & analytics
│   ├── uploads.py          # File upload handlers
│   ├── analysis.py         # Elevation analysis
│   └── maps.py             # Map generation
│
├── utils/                  # Reusable utilities (775 lines)
│   ├── calculations.py     # Math functions
│   ├── terrain_analysis.py # Terrain utilities
│   └── dem_processing.py   # DEM utilities
│
├── tests/                  # Unit tests (48 tests)
│   └── TESTING_GUIDE.md
│
├── scripts/                # Admin tools
│   ├── add_local_lidar_to_db.py
│   ├── diagnose_lidar.py
│   ├── test_lidar.py
│   └── update_technical_rating.py
│
├── sql/                    # Database schema and bucket setup
│   ├── create_table_trails.sql         # Create main trails table
│   ├── create_table_lidar_files.sql    # Create LiDAR file metadata table
│   ├── create_table_xlsx_files.sql     # Create XLSX elevation data table
│   ├── create_bucket_lidar_files.sql   # Set up storage bucket for LiDAR files
│   └── create_bucket_xlsx_files.sql    # Set up storage bucket for XLSX files
```

### SQL Folder

The `sql/` directory contains SQL scripts for setting up and managing the database schema. These scripts include table creation for trails, LiDAR files, and XLSX files, as well as bucket setup for file storage. Use these scripts to initialize or update your Supabase/PostgreSQL database structure as required for MAPENU.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database (via Supabase)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/phurinjeffy/MAPENU.git
   cd MAPENU/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   
   Windows:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   
   Linux/Mac:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment**
   
   Create `.env` file:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```

6. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

   Server runs at: `http://localhost:8000`
   
   API docs: `http://localhost:8000/docs`

## 📚 API Documentation

### Core Endpoints

#### Trails

- `GET /trails` - List all trails
- `GET /trail/{id}/similar` - Find similar trails
- `DELETE /trail/{id}` - Delete trail

#### Analytics

- `GET /analytics/overview` - Dashboard analytics
  - Total trails, distance, elevation gain
  - Difficulty distribution
  - Distance categories
  - Longest trail, most challenging trail
  - Average difficulty score

#### Elevation Analysis

- `GET /trail/{id}/elevation-sources` - Multi-source elevation data
  - GPX baseline
  - QSpatial DEM (1-meter resolution)
  - LiDAR point clouds
  - XLSX elevation data
- `GET /trail/{id}/dem-analysis` - DEM-specific analysis
- `GET /trail/{id}/3d-terrain` - 3D terrain data
- `GET /dem/coverage` - DEM tile coverage information

#### Maps

- `GET /map` - Generate Folium interactive map
- `GET /maps/{filename}` - Serve static map files

#### Uploads

- `POST /upload-gpx` - Upload GPX trail file
- `POST /upload-lidar` - Upload LiDAR (.las/.laz) file
- `POST /upload-xlsx` - Upload XLSX elevation data
- `GET /lidar-files` - List available LiDAR files
- `DELETE /lidar-files/{id}` - Delete LiDAR file

#### Weather

- `GET /trail/{id}/weather` - Weather exposure analysis

### Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation with:
- Try-it-out functionality
- Request/response examples
- Schema definitions
- Authentication testing

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_calculations.py

# Verbose output
pytest -v
```

### Test Coverage

- **Overall**: 27%
- **Utils (calculations)**: 98% ✅
- **Utils (terrain analysis)**: 55%
- **Utils (DEM processing)**: 20%

View detailed coverage: Open `htmlcov/index.html`

See [tests/TESTING_GUIDE.md](tests/TESTING_GUIDE.md) for comprehensive testing documentation.

## 🛠️ Technology Stack

### Core Framework
- **FastAPI** - Modern, fast web framework
- **Uvicorn** - ASGI server with auto-reload

### Database
- **Supabase** - PostgreSQL database with real-time capabilities

### Geospatial Processing
- **Rasterio** - DEM/raster data processing
- **GeoPandas** - Geospatial operations
- **Shapely** - Geometric operations
- **PyProj** - Coordinate transformations

### LiDAR Processing
- **LASpy** - LAS/LAZ file reading
- **LAZrs** - LAZ compression support

### Scientific Computing
- **NumPy** - Numerical operations
- **Pandas** - Data manipulation
- **SciPy** - Scientific algorithms

### Visualization
- **Matplotlib** - Static plots
- **Plotly** - Interactive visualizations
- **Folium** - Interactive maps
- **Seaborn** - Statistical visualizations

### GPS Data
- **GPXpy** - GPX file parsing

### Testing
- **Pytest** - Testing framework
- **Pytest-cov** - Coverage reporting
- **Pytest-asyncio** - Async testing

## 📊 Key Algorithms

### Trail Difficulty Scoring

Multi-factor algorithm considering:
- Distance (5-20+ km)
- Elevation gain/loss
- Maximum slope (capped at 200%)
- Average slope
- Rolling hills index
- Terrain variety (0-1 scale)
- Weather exposure multiplier
- Technical rating

Result: 1-10 difficulty score + level (Easy/Moderate/Hard/Extreme)

### Rolling Hills Detection

Sophisticated algorithm detecting:
- Significant elevation changes (>5m)
- Peaks and valleys
- Changes per kilometer
- Average change magnitude
- Hills index calculation (0-1 scale)

### Trail Similarity

Compares trails using weighted factors:
- Distance similarity (30%)
- Elevation gain similarity (30%)
- Difficulty score similarity (20%)
- Rolling hills similarity (20%)

Result: 0-1 similarity score

### Terrain Variety

Analyzes elevation profile for:
- Standard deviation
- Range
- Slope variance
- Profile complexity

Result: 0-1 variety score with descriptions

### Weather Exposure

Elevation-based risk assessment:
- Low (<600m): Minimal risk
- Low-Moderate (600-900m): Some exposure
- Moderate (900-1200m): Significant exposure
- High (>1200m): Extreme conditions

Includes risk factors and recommendations.

## 🔧 Development

### Development Dependencies

```bash
pip install -r requirements-dev.txt
```

Includes:
- Code formatters (black, autopep8)
- Linters (flake8, pylint, bandit)
- Type checking (mypy)
- Testing tools (pytest-watch, faker)
- Documentation (mkdocs)
- Debugging (ipython, ipdb)

### Code Quality

```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .
```

### Project Scripts

Located in `scripts/` directory:

- `add_local_lidar_to_db.py` - Add LiDAR files to database
- `diagnose_lidar.py` - Debug LiDAR file issues
- `test_lidar.py` - Inspect LiDAR file structure
- `update_technical_rating.py` - Recalculate trail ratings

## 📈 Performance

- **DEM Processing**: 1-2 seconds for typical trail
- **LiDAR Extraction**: 2-5 seconds for 5km trail
- **GPX Upload**: <1 second
- **Trail Similarity**: <100ms for 50 trails
- **Analytics Dashboard**: <200ms

## 🔐 Security

- API key authentication via Supabase
- Service role separation
- File upload validation
- SQL injection prevention (parameterized queries)
- CORS configuration

## 🐛 Troubleshooting

### Common Issues

**Import errors**
```bash
pip install -r requirements.txt
```

**Port already in use**
```bash
uvicorn main:app --port 8001 --reload
```

**Database connection fails**
- Check `.env` file configuration
- Verify Supabase credentials
- Check network connectivity

**Test failures**
```bash
pytest --cache-clear
pip check
```

## 📖 Additional Documentation

- [SETUP.md](SETUP.md) - Quick setup guide
- [tests/TESTING_GUIDE.md](tests/TESTING_GUIDE.md) - Comprehensive testing guide
- [TESTING_SUMMARY.txt](TESTING_SUMMARY.txt) - Current test status

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Contribution Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Ensure all tests pass
- Keep coverage above 80%

## 📝 License

This project is private and proprietary.


## 🙏 Acknowledgments

- FastAPI for excellent web framework
- Supabase for powerful backend services
- Queensland Spatial for DEM data

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check API docs at `/docs`
- Review troubleshooting section above

---

**Made with ❤️ for trail enthusiasts**

*Version 2.0.0 - Modular Architecture*
