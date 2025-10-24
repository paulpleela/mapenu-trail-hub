
# MAPENU Frontend 🗺️

A modern React-based web application for trail analysis, visualization, and sharing.

## Features ✨

- **📤 GPX & LiDAR Uploads**: Upload trail data from GPX files, LiDAR scans, or use MAPENU's built-in GPX Tracker. The upload modal supports multiple formats and guides users through the process.
- **🗺️ Interactive Map Interface**: The Dashboard displays an interactive map with selectable trails, start/end markers, and overlays for elevation and terrain. Users can refresh data, filter trails, and view real-time updates.
- **📊 Trail Metrics & Insights**: For each trail, view detailed statistics including elevation gain/loss, total distance, rolling hills count, technical rating, and difficulty score. Metrics are visualized with charts and summary cards.
- **📈 Elevation Profile & Slope Analysis**: The ElevationChart component shows the trail’s elevation profile, slope variation (highlighted in yellow), and key stats like elevation range and slope extremes.
- **🌄 High-Resolution Terrain Data**: Explore official QSpatial DEM and user-supplied LiDAR visualizations in 3D using Three.js. The TrailVisualization component renders interactive terrain models and point clouds.
- **🧭 Trail Recommendations**: The app suggests similar trails based on your activity and preferences, helping users discover new routes.
- **📚 User Guide & Analytics**: The InfoPage provides comprehensive help, best practices, and explanations of all metrics and scales. The Analytics page summarizes network-wide statistics, difficulty distributions, and trail comparisons.
- **🛰️ Built-in GPX Tracker**: A dedicated page for recording and exporting GPX tracks directly from the platform, streamlining field data collection.

## Tech Stack 🛠️

- **⚛️ React** (with Vite for fast development and hot reload)
- **🎨 Tailwind CSS** (for modern, responsive UI)
- **🟩 Node.js** (for development tooling)
- **🔺 Three.js** (for 3D terrain and LiDAR visualization)
- **🔗 Fetch API** (for backend communication)

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

## Setup & Development ⚡

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

## Usage 🚀

- **🗺️ Main Dashboard**: Upload GPX or LiDAR files, refresh data, and explore trails on the interactive map.
- **📊 Trail Overview**: Select a trail to view its metrics, elevation profile, and terrain insights.
- **🌄 3D Visualization**: Access high-resolution terrain and LiDAR data for advanced analysis.
- **📚 User Guide**: Open the InfoPage for help, best practices, and metric explanations.
- **📈 Analytics**: View aggregate statistics and compare trails.
- **🛰️ GPX Tracker**: Use the built-in tracker for direct field data collection.

## Contributing 🤝

- Fork the repository
- Create a feature branch
- Commit and push your changes
- Open a pull request

## License 📄
This project is private and proprietary.

---

Made with ❤️ for trail enthusiasts
