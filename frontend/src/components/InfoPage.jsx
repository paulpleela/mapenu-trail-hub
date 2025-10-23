import React from "react";
import {
  Info,
  FileUp,
  Map,
  Smartphone,
  Mountain,
  Activity,
  TrendingUp,
  Gauge,
  LineChart,
  Box,
  Database,
  Download,
  CheckCircle,
  AlertCircle,
  BookOpen,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

export default function InfoPage({ onClose }) {
  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 z-50 overflow-y-auto"
      onClick={onClose}
    >
      <div className="min-h-screen px-2 sm:px-4 py-4 sm:py-8">
        <div 
          className="max-w-5xl mx-auto bg-white rounded-lg sm:rounded-2xl shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 sm:p-6 rounded-t-lg sm:rounded-t-2xl">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2 sm:gap-3 mb-2">
                  <BookOpen className="w-6 h-6 sm:w-8 sm:h-8" />
                  <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold">MAPENU Guide</h1>
                </div>
                <p className="text-blue-100 text-sm sm:text-base lg:text-lg">
                  Data Collection Methods & Platform Overview
                </p>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-colors"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-8">
            {/* Section 1: Platform Overview */}
            <section>
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Info className="w-6 h-6 text-blue-600" />
                What is MAPENU?
              </h2>
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6">
                <p className="text-gray-700 leading-relaxed mb-4">
                  MAPENU (Mapped Analysis Platform for Elevation and Navigation
                  Utility) is a specialized trail analysis platform designed for
                  hikers and trail runners. Our primary focus is{" "}
                  <strong className="text-blue-600">
                    identifying and analyzing rolling hills
                  </strong>{" "}
                  in trail data, providing detailed terrain insights that go
                  beyond basic elevation profiles.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <Activity className="w-6 h-6 text-purple-600 mb-2" />
                    <h3 className="font-semibold text-gray-800 mb-1">
                      Rolling Hills Detection
                    </h3>
                    <p className="text-sm text-gray-600">
                      Advanced algorithm measuring trail "bumpiness" - frequency
                      (60%) and amplitude (40%) of elevation changes &gt;1m
                    </p>
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <Mountain className="w-6 h-6 text-green-600 mb-2" />
                    <h3 className="font-semibold text-gray-800 mb-1">
                      Terrain Analysis
                    </h3>
                    <p className="text-sm text-gray-600">
                      Comprehensive metrics including elevation gain/loss,
                      slopes, terrain variety, and difficulty scoring
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 2: Data Collection Methods */}
            <section>
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <FileUp className="w-6 h-6 text-green-600" />
                Data Collection Methods
              </h2>

              {/* Method 1: GPX Files */}
              <Card className="mb-4 border-l-4 border-l-blue-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Map className="w-5 h-5 text-blue-600" />
                    Method 1: GPX Files (Recommended for Trail Recording)
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-800 mb-2">
                      What is GPX?
                    </h4>
                    <p className="text-sm text-gray-700">
                      GPX (GPS Exchange Format) is a standard XML format for GPS
                      data. It records your trail's coordinates, elevation, and
                      timestamps as you hike.
                    </p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <Smartphone className="w-5 h-5" />
                      Recommended Apps:
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="font-medium text-gray-800">
                          📱 GPS Tracks
                        </p>
                        <p className="text-xs text-gray-600 mt-1">
                          iOS - Accurate GPS tracking with offline maps
                        </p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="font-medium text-gray-800">
                          📱 My Tracks (OSM Tracker)
                        </p>
                        <p className="text-xs text-gray-600 mt-1">
                          Android - Open-source GPS logger
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                    <h4 className="font-semibold text-green-800 mb-2 flex items-center gap-2">
                      <CheckCircle className="w-5 h-5" />
                      Best Practices:
                    </h4>
                    <ul className="space-y-1 text-sm text-gray-700">
                      <li>✓ Enable high-accuracy GPS mode on your device</li>
                      <li>
                        ✓ Record at 1-5 second intervals for detailed data
                      </li>
                      <li>
                        ✓ Keep phone in an easily accessible pocket/holder
                      </li>
                      <li>✓ Ensure phone has sufficient battery</li>
                      <li>✓ Start recording before the trail begins</li>
                      <li>✓ Stop recording after completing the trail</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>

              {/* Method 2: LiDAR Files */}
              <Card className="mb-4 border-l-4 border-l-purple-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Box className="w-5 h-5 text-purple-600" />
                    Method 2: LiDAR Files (.las format)
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-purple-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-800 mb-2">
                      What is LiDAR?
                    </h4>
                    <p className="text-sm text-gray-700">
                      LiDAR (Light Detection and Ranging) creates detailed 3D
                      point clouds of terrain using laser scanning. iPhone Pro
                      and iPad Pro models have built-in LiDAR sensors.
                    </p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <Smartphone className="w-5 h-5" />
                      Recommended LiDAR Scanner Apps:
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="font-medium text-gray-800">📱 dot3D</p>
                        <p className="text-xs text-gray-600 mt-1">
                          Professional-grade scanning
                        </p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="font-medium text-gray-800">📱 Polycam</p>
                        <p className="text-xs text-gray-600 mt-1">
                          Easy-to-use 3D scanner
                        </p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="font-medium text-gray-800">
                          📱 Scaniverse
                        </p>
                        <p className="text-xs text-gray-600 mt-1">
                          Free LiDAR scanning
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                    <h4 className="font-semibold text-amber-800 mb-2 flex items-center gap-2">
                      <AlertCircle className="w-5 h-5" />
                      Requirements & Tips:
                    </h4>
                    <ul className="space-y-1 text-sm text-gray-700">
                      <li>
                        • Requires iPhone 12 Pro or later, iPad Pro (2020+)
                      </li>
                      <li>• Export scans in .las or .laz format</li>
                      <li>• Scan in good lighting conditions</li>
                      <li>• Move slowly and steadily while scanning</li>
                      <li>• Overlap scan areas for better coverage</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>

              {/* Method 3: QSpatial Data */}
              <Card className="border-l-4 border-l-emerald-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="w-5 h-5 text-emerald-600" />
                    Method 3: QSpatial Open Data (Queensland, Australia)
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-emerald-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-800 mb-2">
                      What is QSpatial?
                    </h4>
                    <p className="text-sm text-gray-700">
                      QSpatial provides free high-resolution (1-meter) LiDAR
                      elevation data for Queensland regions. This is
                      professional-grade DEM (Digital Elevation Model) data.
                    </p>
                  </div>

                  <div className="bg-white rounded-lg p-4 border border-gray-200">
                    <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <Download className="w-5 h-5" />
                      How to Access:
                    </h4>
                    <ol className="space-y-2 text-sm text-gray-700 list-decimal list-inside">
                      <li>
                        Visit{" "}
                        <a
                          href="https://qldspatial.information.qld.gov.au/"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          QSpatial Portal
                        </a>
                      </li>
                      <li>Search for "LiDAR" or "Digital Elevation Model"</li>
                      <li>Select your region of interest</li>
                      <li>Download GeoTIFF (.tif) or LAS files</li>
                      <li>Upload to MAPENU for analysis</li>
                    </ol>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                    <p className="text-sm text-gray-700">
                      <strong>Note:</strong> MAPENU currently uses QSpatial DEM
                      data for Brisbane region analysis and 3D terrain
                      visualizations.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </section>

            {/* Section 3: What the Website Analyzes */}
            <section>
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-orange-600" />
                What MAPENU Analyzes
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Visual 1: 2D Elevation Profile */}
                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <LineChart className="w-5 h-5" />
                      2D Elevation Profile Chart
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <div className="bg-gray-50 rounded-lg p-3 mb-3">
                      <img
                        src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 200'%3E%3Crect fill='%23f3f4f6' width='400' height='200'/%3E%3Cpath d='M 20 180 L 50 160 L 80 140 L 110 145 L 140 120 L 170 100 L 200 110 L 230 80 L 260 90 L 290 70 L 320 75 L 350 60 L 380 65' stroke='%233b82f6' fill='none' stroke-width='3'/%3E%3Cpath d='M 20 180 L 50 160 L 80 140 L 110 145 L 140 120 L 170 100 L 200 110 L 230 80 L 260 90 L 290 70 L 320 75 L 350 60 L 380 65 L 380 180 Z' fill='%233b82f6' opacity='0.2'/%3E%3Ctext x='200' y='195' text-anchor='middle' font-size='12' fill='%236b7280'%3EDistance (km)%3C/text%3E%3Ctext x='10' y='100' font-size='12' fill='%236b7280' transform='rotate(-90 10 100)'%3EElevation (m)%3C/text%3E%3C/svg%3E"
                        alt="Elevation Profile Example"
                        className="w-full rounded"
                      />
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Shows:</strong>
                    </p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Elevation changes over distance</li>
                      <li>• Gradient/slope percentages</li>
                      <li>• Cumulative elevation gain/loss</li>
                      <li>• Visual identification of climbs and descents</li>
                    </ul>
                  </CardContent>
                </Card>

                {/* Visual 2: 3D Terrain */}
                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Box className="w-5 h-5" />
                      3D Terrain Visualization
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <div className="bg-gray-50 rounded-lg p-3 mb-3">
                      <img
                        src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 200'%3E%3Cdefs%3E%3ClinearGradient id='grad1' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%23f3f4f6;stop-opacity:1'/%3E%3Cstop offset='100%25' style='stop-color:%23d1d5db;stop-opacity:1'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect fill='url(%23grad1)' width='400' height='200'/%3E%3Cpath d='M 50 150 Q 100 120 150 130 T 250 100 T 350 120' stroke='%238b5cf6' fill='none' stroke-width='3' stroke-dasharray='5,5'/%3E%3Cellipse cx='150' cy='80' rx='80' ry='30' fill='%239ca3af' opacity='0.3'/%3E%3Cellipse cx='250' cy='100' rx='60' ry='25' fill='%239ca3af' opacity='0.4'/%3E%3Cpath d='M 100 140 L 120 130 L 140 135 L 160 125 L 180 130 L 200 120' stroke='%23ef4444' fill='none' stroke-width='2'/%3E%3Ctext x='200' y='190' text-anchor='middle' font-size='14' fill='%236b7280' font-weight='bold'%3E3D Interactive View%3C/text%3E%3C/svg%3E"
                        alt="3D Terrain Example"
                        className="w-full rounded"
                      />
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Shows:</strong>
                    </p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Interactive 3D terrain surface</li>
                      <li>• Trail path overlaid on real elevation</li>
                      <li>• Surrounding topography</li>
                      <li>• Rotatable and zoomable view</li>
                    </ul>
                  </CardContent>
                </Card>

                {/* Metric 1: Rolling Hills Index */}
                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Activity className="w-5 h-5" />
                      Rolling Hills Index (0-1)
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <div className="bg-emerald-50 rounded-lg p-4 mb-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">
                          Example: 0.65
                        </span>
                        <span className="text-xs text-emerald-600 font-semibold">
                          MODERATE ROLLING
                        </span>
                      </div>
                      <div className="bg-gray-200 rounded-full h-3">
                        <div
                          className="bg-gradient-to-r from-emerald-500 to-teal-500 h-3 rounded-full"
                          style={{ width: "65%" }}
                        ></div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Measures:</strong>
                    </p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Trail "bumpiness" or undulation</li>
                      <li>• Frequency: # of hills per km (60% weight)</li>
                      <li>• Amplitude: Average hill size (40% weight)</li>
                      <li>• Threshold: Elevation changes &gt;1 meter</li>
                    </ul>
                  </CardContent>
                </Card>

                {/* Metric 2: Difficulty Score */}
                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader className="bg-gradient-to-r from-orange-500 to-red-500 text-white">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Gauge className="w-5 h-5" />
                      Difficulty Score & Time
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <div className="bg-orange-50 rounded-lg p-4 mb-3">
                      <div className="grid grid-cols-2 gap-3 text-center">
                        <div>
                          <p className="text-2xl font-bold text-orange-600">
                            6.5
                          </p>
                          <p className="text-xs text-gray-600">
                            Difficulty Score
                          </p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-red-600">
                            3.2h
                          </p>
                          <p className="text-xs text-gray-600">Est. Time</p>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Calculates:</strong>
                    </p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Distance factor (30%)</li>
                      <li>• Elevation gain factor (40%)</li>
                      <li>• Rolling hills factor (30%)</li>
                      <li>• Time via Naismith's Rule</li>
                      <li>• Classification: Easy/Moderate/Hard/Extreme</li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </section>

            {/* Section 4: Metrics & Scales */}
            <section>
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Gauge className="w-6 h-6 text-indigo-600" />
                Metrics & Scales Explained
              </h2>

              <div className="space-y-6">
                {/* Difficulty Score Card */}
                <Card className="border-l-4 border-l-blue-500">
                  <CardHeader className="bg-gradient-to-r from-blue-50 to-cyan-50">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <TrendingUp className="w-5 h-5 text-blue-600" />
                      Difficulty Score (0-10 Scale)
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <p className="text-sm text-gray-600 mb-4">
                      Overall trail difficulty combining distance, elevation,
                      and terrain complexity.
                    </p>

                    {/* Formula Breakdown */}
                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <h4 className="font-semibold text-gray-800 mb-3">
                        📐 Formula Components:
                      </h4>
                      <div className="space-y-3">
                        <div className="flex items-start gap-3">
                          <span className="flex-shrink-0 w-16 h-8 bg-blue-100 text-blue-700 rounded text-sm font-semibold flex items-center justify-center">
                            0-3 pts
                          </span>
                          <div>
                            <p className="font-medium text-gray-800">
                              Distance Factor
                            </p>
                            <p className="text-sm text-gray-600">
                              <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                                min(distance / 10, 1) × 3
                              </code>
                              <br />
                              <span className="text-xs">
                                Examples: 5km = 1.5pts, 10km = 3pts
                              </span>
                            </p>
                          </div>
                        </div>

                        <div className="flex items-start gap-3">
                          <span className="flex-shrink-0 w-16 h-8 bg-green-100 text-green-700 rounded text-sm font-semibold flex items-center justify-center">
                            0-4 pts
                          </span>
                          <div>
                            <p className="font-medium text-gray-800">
                              Elevation Factor
                            </p>
                            <p className="text-sm text-gray-600">
                              <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                                min(elevation_gain / 1000, 1) × 4
                              </code>
                              <br />
                              <span className="text-xs">
                                Examples: 250m = 1pt, 500m = 2pts, 1000m = 4pts
                              </span>
                            </p>
                          </div>
                        </div>

                        <div className="flex items-start gap-3">
                          <span className="flex-shrink-0 w-16 h-8 bg-purple-100 text-purple-700 rounded text-sm font-semibold flex items-center justify-center">
                            0-3 pts
                          </span>
                          <div>
                            <p className="font-medium text-gray-800">
                              Rolling Terrain Factor
                            </p>
                            <p className="text-sm text-gray-600">
                              <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                                min(rolling_index / 50, 1) × 3
                              </code>
                              <br />
                              <span className="text-xs">
                                Examples: Index 10 = 0.6pts, Index 25 = 1.5pts
                              </span>
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Difficulty Levels */}
                    <div className="space-y-2">
                      <h4 className="font-semibold text-gray-800 mb-2">
                        🎯 Difficulty Levels:
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                          <p className="text-xs text-green-600 font-semibold mb-1">
                            EASY
                          </p>
                          <p className="text-lg font-bold text-green-700">
                            0-3
                          </p>
                          <p className="text-xs text-gray-600 mt-1">
                            Beginner friendly
                          </p>
                        </div>
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-center">
                          <p className="text-xs text-yellow-600 font-semibold mb-1">
                            MODERATE
                          </p>
                          <p className="text-lg font-bold text-yellow-700">
                            3.1-6
                          </p>
                          <p className="text-xs text-gray-600 mt-1">
                            Some challenge
                          </p>
                        </div>
                        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-center">
                          <p className="text-xs text-orange-600 font-semibold mb-1">
                            HARD
                          </p>
                          <p className="text-lg font-bold text-orange-700">
                            6.1-8
                          </p>
                          <p className="text-xs text-gray-600 mt-1">
                            Experienced
                          </p>
                        </div>
                        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
                          <p className="text-xs text-red-600 font-semibold mb-1">
                            EXTREME
                          </p>
                          <p className="text-lg font-bold text-red-700">
                            8.1-10
                          </p>
                          <p className="text-xs text-gray-600 mt-1">
                            Very difficult
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Rolling Intensity Card */}
                <Card className="border-l-4 border-l-emerald-500">
                  <CardHeader className="bg-gradient-to-r from-emerald-50 to-teal-50">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Activity className="w-5 h-5 text-emerald-600" />
                      Rolling Intensity (0-10 Scale)
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <p className="text-sm text-gray-600 mb-4">
                      Measures how "bumpy" or undulating the trail is. Higher
                      values mean more tiring up-and-down terrain.
                    </p>

                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <h4 className="font-semibold text-gray-800 mb-3">
                        🧮 How It Works:
                      </h4>
                      <ul className="text-sm text-gray-600 space-y-2">
                        <li>• Counts elevation changes &gt; 1 meter</li>
                        <li>
                          • <strong>60% weight:</strong> Hills per kilometer
                          (frequency)
                        </li>
                        <li>
                          • <strong>40% weight:</strong> Average hill size
                          (amplitude)
                        </li>
                        <li>• Displayed on normalized 0-10 scale</li>
                      </ul>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-green-50 border border-green-200 rounded p-2 text-center">
                        <p className="text-xs text-green-600 font-semibold">
                          0-3
                        </p>
                        <p className="text-xs text-gray-600">Smooth</p>
                      </div>
                      <div className="bg-yellow-50 border border-yellow-200 rounded p-2 text-center">
                        <p className="text-xs text-yellow-600 font-semibold">
                          3-6
                        </p>
                        <p className="text-xs text-gray-600">Moderate</p>
                      </div>
                      <div className="bg-orange-50 border border-orange-200 rounded p-2 text-center">
                        <p className="text-xs text-orange-600 font-semibold">
                          6-8
                        </p>
                        <p className="text-xs text-gray-600">Rolling</p>
                      </div>
                      <div className="bg-red-50 border border-red-200 rounded p-2 text-center">
                        <p className="text-xs text-red-600 font-semibold">
                          8-10
                        </p>
                        <p className="text-xs text-gray-600">Very Rolling</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Hills Count Card */}
                <Card className="border-l-4 border-l-purple-500">
                  <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Mountain className="w-5 h-5 text-purple-600" />
                      Hills Count (Actual Number)
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <p className="text-sm text-gray-600 mb-4">
                      The actual number of distinct peaks and valleys on the
                      trail.
                    </p>

                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-800 mb-3">
                        🏔️ Detection:
                      </h4>
                      <ul className="text-sm text-gray-600 space-y-2">
                        <li>
                          • <strong>Peak:</strong> Point higher than both
                          neighbors
                        </li>
                        <li>
                          • <strong>Valley:</strong> Point lower than both
                          neighbors
                        </li>
                        <li>
                          • <strong>Threshold:</strong> ≥1m elevation difference
                        </li>
                        <li>
                          • <strong>Total:</strong> Peaks + Valleys
                        </li>
                      </ul>
                      <div className="mt-3 bg-blue-50 border border-blue-200 rounded p-2">
                        <p className="text-xs text-gray-700">
                          <strong>Example:</strong> "23 hills" = 23 direction
                          changes (e.g., 12 peaks + 11 valleys)
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Technical Difficulty Card */}
                <Card className="border-l-4 border-l-rose-500">
                  <CardHeader className="bg-gradient-to-r from-rose-50 to-pink-50">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Gauge className="w-5 h-5 text-rose-600" />
                      Technical Difficulty (1-10)
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <p className="text-sm text-gray-600 mb-4">
                      Technical challenge rating based on slopes and terrain complexity. 
                      Measures how technically demanding a trail is to navigate.
                    </p>

                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <h4 className="font-semibold text-gray-800 mb-3">
                        🧮 Formula:
                      </h4>
                      <div className="bg-white p-3 rounded border font-mono text-sm text-gray-800">
                        <div className="text-blue-600 mb-2">Technical Rating = max(1, min(10, calculation))</div>
                        <div>calculation = 1 + (max_slope/100)×3.5 + min(rolling_index/50, 1)×3.5 + (avg_slope/30)×2.0</div>
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <h4 className="font-semibold text-gray-800 mb-3">
                        ⚙️ Components:
                      </h4>
                      <ul className="text-sm text-gray-600 space-y-2">
                        <li>
                          • <strong>Max Slope (39%):</strong> Steepest section impact (0-100% → 0-3.5 points)
                        </li>
                        <li>
                          • <strong>Rolling Terrain (39%):</strong> Terrain complexity normalized (0-50 index → 0-3.5 points)
                        </li>
                        <li>
                          • <strong>Average Slope (22%):</strong> Overall gradient difficulty (0-30% → 0-2.0 points)
                        </li>
                      </ul>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="bg-green-100 p-2 rounded text-center">
                        <div className="font-bold text-green-800">Easy</div>
                        <div className="text-green-600">1-3</div>
                      </div>
                      <div className="bg-yellow-100 p-2 rounded text-center">
                        <div className="font-bold text-yellow-800">Moderate</div>
                        <div className="text-yellow-600">4-6</div>
                      </div>
                      <div className="bg-orange-100 p-2 rounded text-center">
                        <div className="font-bold text-orange-800">Hard</div>
                        <div className="text-orange-600">7-8</div>
                      </div>
                      <div className="bg-red-100 p-2 rounded text-center">
                        <div className="font-bold text-red-800">Extreme</div>
                        <div className="text-red-600">9-10</div>
                      </div>
                    </div>

                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <h5 className="font-semibold text-blue-800 text-sm mb-2">💡 Real Examples:</h5>
                      <div className="text-xs text-blue-700 space-y-1">
                        <div>• <strong>375-Botanic-Gardens (4/10):</strong> 34% max, 7.6% avg, gentle rolling</div>
                        <div>• <strong>Trail 1 (6/10):</strong> 41% max, 14.6% avg, moderate rolling</div>
                        <div>• <strong>Trail 2 (8/10):</strong> 62% max, 24.9% avg, intense rolling</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Estimated Time Card */}
                <Card className="border-l-4 border-l-cyan-500">
                  <CardHeader className="bg-gradient-to-r from-cyan-50 to-blue-50">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Info className="w-5 h-5 text-cyan-600" />
                      Estimated Time
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <p className="text-sm text-gray-600 mb-4">
                      Based on Naismith's Rule with rolling terrain adjustment.
                    </p>

                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-800 mb-3">
                        ⏱️ Formula:
                      </h4>
                      <p className="text-sm text-gray-600 mb-2">
                        <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                          (distance/5) + (elevation/600) + (rolling × 0.5)
                        </code>
                      </p>
                      <ul className="text-xs text-gray-600 space-y-1">
                        <li>• 5 km/hour base speed</li>
                        <li>• +1 hour per 600m elevation</li>
                        <li>• Extra time for rolling terrain</li>
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </section>

            {/* Section 5: Additional Features */}
            <section>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                Additional Features
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-800 mb-2">
                    📊 Trail Comparison
                  </h3>
                  <p className="text-sm text-gray-600">
                    Find similar trails based on distance, elevation, and
                    rolling hills characteristics
                  </p>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-800 mb-2">
                    📐 Measure GPX
                  </h3>
                  <p className="text-sm text-gray-600">
                    Measure distance, elevation gain, and other metrics from GPX
                    files
                  </p>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-800 mb-2">
                    🗺️ Interactive Maps
                  </h3>
                  <p className="text-sm text-gray-600">
                    View trails on interactive maps with start/end markers and
                    elevation overlays
                  </p>
                </div>
              </div>
            </section>

            {/* Quick Start Guide */}
            <section className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                🚀 Quick Start Guide
              </h2>
              <ol className="space-y-3">
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">
                    1
                  </span>
                  <div>
                    <p className="font-semibold text-gray-800">
                      Record Your Trail
                    </p>
                    <p className="text-sm text-gray-600">
                      Use a GPS tracking app or the built-in <a href="/measure" target="_blank" className="text-blue-500">MAPENU GPX Tracker</a> to record your hike as a GPX file
                    </p>
                  </div>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">
                    2
                  </span>
                  <div>
                    <p className="font-semibold text-gray-800">
                      Upload to MAPENU
                    </p>
                    <p className="text-sm text-gray-600">
                      Click "Upload Trail Data" button in the header → Select "New Trail (GPX)" → Choose your trail file → Name your trail
                    </p>
                  </div>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">
                    3
                  </span>
                  <div>
                    <p className="font-semibold text-gray-800">View Elevation Profile</p>
                    <p className="text-sm text-gray-600">
                      Select your trail from the list → Check the "Elevation Profile" tab to see elevation charts with multiple data sources (if available)
                    </p>
                  </div>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">
                    4
                  </span>
                  <div>
                    <p className="font-semibold text-gray-800">Explore Trail Analysis</p>
                    <p className="text-sm text-gray-600">
                      View rolling hills metrics, difficulty ratings, elevation gain/loss, slope analysis, and estimated completion time
                    </p>
                  </div>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">
                    5
                  </span>
                  <div>
                    <p className="font-semibold text-gray-800">View 3D Terrain</p>
                    <p className="text-sm text-gray-600">
                      Check "Real-Time DEM Analysis" to see interactive 3D terrain visualization with your trail path overlaid on actual elevation data
                    </p>
                  </div>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">
                    6
                  </span>
                  <div>
                    <p className="font-semibold text-gray-800">Add Additional Data (Enhance Analysis)</p>
                    <p className="text-sm text-gray-600">
                      Click the "Upload Trail Data" button → Select "LiDAR Data" (.las/.laz) or "Elevation Profile" (.xlsx) to upload → Select an existing trail to enhance with this new data. Compare different data sources using the elevation source dropdown.
                    </p>
                  </div>
                </li>
              </ol>
              
              <div className="mt-6 bg-white rounded-lg p-4 border-2 border-indigo-200">
                <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                  <Info className="w-5 h-5 text-indigo-600" />
                  Pro Tips:
                </h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Use the elevation source dropdown to compare GPX vs LiDAR vs QSpatial vs XLSX data</li>
                  <li>• Metrics (elevation gain, loss, slope) update dynamically based on selected source</li>
                  <li>• Click the refresh icon in DEM Analysis to reload 3D terrain visualization</li>
                  <li>• Use "Find Similar" to discover trails with comparable difficulty and terrain</li>
                </ul>
              </div>
            </section>
          </div>

          {/* Footer */}
          <div className="bg-gray-100 p-4 rounded-b-2xl text-center">
            <p className="text-sm text-gray-600">
              Questions or feedback?{" "}
              <a
                href="https://github.com/phurinjeffy/MAPENU"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline font-medium"
              >
                Visit our GitHub
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
