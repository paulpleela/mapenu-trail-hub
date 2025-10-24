# MAPENU Backend - Quick Setup Guide

## 📦 Installation

### 1. Create Virtual Environment
```bash
python -m venv .venv
```

### 2. Activate Virtual Environment
**Windows:**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

**Production:**
```bash
pip install -r requirements.txt
```

**Development (includes testing, linting, docs):**
```bash
pip install -r requirements-dev.txt
```

## 🚀 Running the Application

### Start Backend Server
```bash
cd backend
uvicorn main:app --reload
```

Server will run at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_calculations.py
```

### View Coverage Report
Open `htmlcov/index.html` in your browser

## 📚 Documentation

- **Testing Guide**: `tests/TESTING_GUIDE.md`
- **Testing Summary**: `TESTING_SUMMARY.txt`
- **API Documentation**: Start server and visit `/docs`

## 🗂️ Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration
├── database.py          # Supabase client
├── app_state.py         # Application state
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
├── pytest.ini           # Test configuration
│
├── routes/              # API endpoints
│   ├── trails.py        # Trail CRUD & analytics
│   ├── uploads.py       # File uploads
│   ├── analysis.py      # Elevation analysis
│   └── maps.py          # Map generation
│
├── utils/               # Reusable utilities
│   ├── calculations.py  # Math functions
│   ├── terrain_analysis.py  # Terrain utilities
│   └── dem_processing.py  # DEM utilities
│
├── tests/               # Unit tests
│   ├── TESTING_GUIDE.md # Testing documentation
│   ├── conftest.py      # Test fixtures
│   ├── test_calculations.py
│   ├── test_terrain_analysis.py
│   ├── test_dem_processing.py
│   └── test_routes.py
│
└── scripts/             # Admin/development scripts
    ├── add_local_lidar_to_db.py
    ├── diagnose_lidar.py
    ├── test_lidar.py
    └── update_technical_rating.py
```

## 🔧 Common Commands

### Check Dependencies
```bash
pip check
```

### List Installed Packages
```bash
pip list
```

### Freeze Current Environment
```bash
pip freeze > requirements-frozen.txt
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

## 🌍 Environment Variables

Create a `.env` file in the backend directory:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## ✅ Health Check

Test if everything is working:

```bash
# Check imports
python -c "from main import app; print('✅ Backend imports successful!')"

# Run a quick test
pytest tests/test_calculations.py::TestHaversine -v
```

## 🐛 Troubleshooting

**Import errors?**
- Make sure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

**Test failures?**
- Check if all dependencies installed: `pip check`
- Clear pytest cache: `pytest --cache-clear`

**Port already in use?**
- Change port: `uvicorn main:app --port 8001 --reload`

## 📞 Need Help?

- Check `tests/TESTING_GUIDE.md` for testing help
- View API docs at `/docs` when server is running
- Check logs in terminal for error details
