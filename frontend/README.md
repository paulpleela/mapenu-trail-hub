# MAPENU Frontend 🗺️

A modern React-based web application for trail analysis, visualization, and sharing.

---

## Overview

MAPENU enables users to analyze, visualize, and share trail data using geospatial elevation sources (GPX, LiDAR, DTM). The system detects and classifies rolling hill patterns, provides interactive maps and charts, and supports reproducible terrain analysis for trail certification and planning.

**PLACEHOLDER: Project logo or banner image here**

---

## Features ✨

- **📤 GPX & LiDAR Uploads**: Upload trail data from GPX files, LiDAR scans, or use MAPENU's built-in GPX Tracker. The upload modal supports multiple formats and guides users through the process.
- **🗺️ Interactive Map Interface**: Explore trails, start/end markers, overlays for elevation and terrain, and real-time updates.
- **📊 Trail Metrics & Insights**: View elevation gain/loss, distance, rolling hills count, technical rating, and difficulty score. Metrics are visualized with charts and summary cards.
- **📈 Elevation Profile & Slope Analysis**: See elevation profiles, slope variation, and key stats.
- **🌄 High-Resolution Terrain Data**: Visualize QSpatial DEM and user-supplied LiDAR in 3D.
- **🧭 Trail Recommendations**: Discover similar trails based on your activity and preferences.
- **📚 User Guide & Analytics**: Access help, best practices, and analytics dashboards.
- **🛰️ Built-in GPX Tracker**: Record and export GPX tracks directly from the platform.

**PLACEHOLDER: Example website screenshot here**

---

## Project Structure 🗂️

```
frontend/
├── public/                # Static assets
├── src/
│   ├── components/        # React components (Dashboard, InfoPage, ElevationChart, TrailVisualization, UnifiedUploadModal, etc.)
│   ├── assets/            # Images and icons
│   ├── App.jsx            # Main app entry point
│   ├── main.jsx           # React root
│   ├── App.css, index.css # Styles
│   └── ...
├── package.json           # Project metadata and dependencies
├── tailwind.config.js     # Tailwind CSS configuration
├── vite.config.js         # Vite configuration
└── README.md              # Project documentation
```

---

## Tech Stack 🛠️

- **⚛️ React** (Vite)
- **🎨 Tailwind CSS**
- **🟩 Node.js**
- **🔺 Three.js**
- **🔗 Fetch API**

---

## How to Run Locally ⚡

### Prerequisites

- 🟩 Node.js 18+

### Install Dependencies

```bash
cd frontend
npm install
```

### Run Development Server

```bash
npm run dev
```

Frontend will run on: `http://localhost:5173`

---

## Deployment 🌐

The latest version is deployed at: **PLACEHOLDER**

---

## Usage 🚀

- **🗺️ Main Dashboard**: Upload GPX or LiDAR files, refresh data, and explore trails on the interactive map.
- **📊 Trail Overview**: Select a trail to view its metrics, elevation profile, and terrain insights.
- **🌄 3D Visualization**: Access high-resolution terrain and LiDAR data for advanced analysis.
- **📚 User Guide**: Open the InfoPage for help, best practices, and metric explanations.
- **📈 Analytics**: View aggregate statistics and compare trails.
- **🛰️ GPX Tracker**: Use the built-in tracker for direct field data collection.

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

Made with ❤️ for trail enthusiasts
