# MAPENU - Trail Sharing Platform

A platform for hikers and trail runners to analyse, share, and discover trails.

## Features

- **GPX Analysis** - Upload GPX files for detailed elevation and difficulty analysis
- **Interactive Trail Maps** - Visualise trails on an interactive map using Folium
- **Detailed Statistics** - Shows statistics like distance, elevation gain/loss, difficulty scoring, and rolling hills detection

## How to Setup

### Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)

### 1. Clone the Repository

```bash
git clone https://github.com/phurinjeffy/MAPENU.git
cd MAPENU
```

### 2. Backend Setup

```bash
# Navigate to backend directory (from project root)
cd backend

# Install dependencies
pip install -r requirements.txt
```

#### 2.1 Create an `.env` file in the `backend` directory:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

## How to Run

**Start Backend** (in `backend` directory):
```bash
uvicorn main:app --reload
```
Backend will run on: `http://localhost:8000`

**Start Frontend** (in `frontend` directory):
```bash
npm run dev
```
Frontend will run on: `http://localhost:5173`
