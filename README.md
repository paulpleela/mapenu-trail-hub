# MAPENU 🗺️

A modern, innovative platform for trail analysis, visualization, and certification. MAPENU combines geospatial data science, interactive web technologies, and advanced terrain analytics to support athletes, certifiers, and organizers in understanding trail complexity and rolling hill patterns.

---

## Overview

MAPENU enables users to upload, analyze, and visualize trail elevation data from GPX, LiDAR, and DTM sources. The system detects and classifies rolling hills, validates results on real-world trails, and presents intuitive visual outputs for decision-making and certification.

<p align="center">
  <img width="512" height="512" alt="mapenu-logo" src="https://github.com/user-attachments/assets/f7894f0c-149f-46b4-8cc5-31fe31c7a394" />
</p>


---

## Key Features

- **Rolling Hill Detection & Classification**: Identifies human-scale undulations in trail elevation data, supporting difficulty ratings and certification.
- **Real Trail Validation**: Tested on actual trail segments (e.g., Mt Coot-tha) with field measurements and expert feedback.
- **Reproducible Terrain Analysis**: Consistent outputs across different trails and datasets, supporting scalable assessment.
- **Intuitive Visualizations**: Interactive maps, elevation charts, and summary metrics for stakeholders.
- **Secure & Ethical Data Handling**: User privacy and data security are prioritized throughout the platform.

<img width="1083" height="820" alt="image" src="https://github.com/user-attachments/assets/6ea3bc14-c35e-42fb-8ffa-e7ceff2372be" />

---

## Project Structure

```
MAPENU/
├── backend/      # FastAPI backend, LiDAR/GPX processing, API endpoints
├── frontend/     # React web app, visualization, user interface
├── README.md     # Outermost project overview (this file)
└── ...           # Data, scripts, documentation
```

---

## How to Run Locally ⚡

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

External Data Files & Datasets Required Data Files DEM/GeoTIFF Files
- QSpatial Queensland Government .tif (GeoTIFF) files placed in backend/dem_data/ 
- Example: brisbane_dem_1m.tif (1-meter resolution Digital Elevation Model) 
- Request files from: https://elevation.fsdf.org.au/ bounding areas of interest (Mt Coot-Tha)

Example Trail Datasets (Provided)
- GPX files: backend/example_data/sample_trails/.gpx 
- LiDAR files: backend/example_data/.las or .laz 
- XLSX profiles: backend/example_data/.xlsx 


### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Access

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

---

## Deployment 🌐

The latest version is deployed at: https://mapenu.site/

---

## Documentation

For a detailed explanation of the project implementation, algorithms, and features, please refer to:

- [Frontend README](frontend/README.md)
- [Backend README](backend/README.md)

---

## 👥 Authors

- **phurinjeffy** - [GitHub](https://github.com/phurinjeffy)
- **nownver** - [GitHub](https://github.com/nownver)
- **paulpleela** - [GitHub](https://github.com/paulpleela)
- **Enix47** - [GitHub](https://github.com/Enix47)
- **matildas23** - [GitHub](https://github.com/matildas23)
- **Dmar-Create** - [GitHub](https://github.com/Dmar-Create)

---

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit and push your changes
4. Open a pull request

---

## License 📄

This project is private and proprietary.

---

## 🤖 AI Acknowledgment
This project used GitHub Copilot as a coding assistant to help with debugging, fixing syntax errors, and suggesting code completions during development.
All ideas, architectural designs, and final implementation decisions were developed independently by our team.
AI-generated code suggestions were reviewed, tested, and modified to fit the project’s design intent and coding standards.
Example Prompts Used:
- “Fix the syntax error in this React component.”
- “Why does this useEffect cause an infinite re-render?”
- “Suggest a cleaner way to handle this form submission in React.”
- “Add proper error handling for this async API call.”
- “Explain what this TypeScript error means and how to fix it.”
- “Improve the readability of this JSX render function.”

---

Made with ❤️ for trail enthusiasts
