import React, { useState, useEffect, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import {
  MapPin,
  Mountain,
  Ruler,
  TrendingUp,
  Activity,
  Gauge,
  Info,
  Upload,
  RefreshCw,
  Database,
} from "lucide-react";

// API URL
const API_BASE_URL = "http://localhost:8000";

// Folium Map Component - shows all trails
const FoliumMap = ({ onTrailClick, trails }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mapUrl, setMapUrl] = useState(null);

  // Listen for messages from the Folium iframe
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.origin !== API_BASE_URL) {
        return;
      }

      if (event.data.type === "trail-clicked") {
        console.log("Trail clicked, received data:", event.data.data);
        onTrailClick && onTrailClick(event.data.data);
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [onTrailClick]);

  // Load map when trails change
  useEffect(() => {
    loadMap();
  }, [trails]);

  const loadMap = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/map`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success) {
        setMapUrl(data.map_url);
      } else {
        setError(data.error || "Failed to load map");
      }
    } catch (err) {
      console.error("Map loading error:", err);
      setError(
        `Unable to load map: ${err.message}. Please ensure the backend server is running.`
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading trail map...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center max-w-md p-6">
          <div className="text-red-500 mb-4">
            <MapPin className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Map Error
          </h3>
          <p className="text-gray-600 text-sm mb-4">{error}</p>
          <Button onClick={loadMap} variant="outline">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!mapUrl) {
    return (
      <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          {trails.length === 0 ? (
            <>
              <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                No Trails Available
              </h3>
              <p className="text-gray-600 mb-4">
                Upload some GPX files to start analyzing trails!
              </p>
            </>
          ) : (
            <>
              <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Loading map...</p>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full rounded-lg overflow-hidden border">
      <iframe
        src={`${API_BASE_URL}${mapUrl}`}
        className="w-full h-full border-0"
        title="Trail Map"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
};

// Difficulty ring component
const DifficultyRing = ({ score, label }) => {
  const radius = 40;
  const stroke = 8;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 10) * circumference;

  const getColor = (score) => {
    if (score <= 3) return "#22c55e";
    if (score <= 6) return "#eab308";
    if (score <= 8) return "#f97316";
    return "#ef4444";
  };

  return (
    <div className="relative w-24 h-24">
      <svg className="w-24 h-24 transform -rotate-90">
        <circle
          cx="48"
          cy="48"
          r={radius}
          stroke="#e5e7eb"
          strokeWidth={stroke}
          fill="none"
        />
        <circle
          cx="48"
          cy="48"
          r={radius}
          stroke={getColor(score)}
          strokeWidth={stroke}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-xl font-bold">{score}</span>
        <span className="text-xs text-gray-500">{label}</span>
      </div>
    </div>
  );
};

// Stat card component
const StatCard = ({ icon: Icon, label, value, unit }) => (
  <div className="bg-white rounded-lg p-4 border shadow-sm">
    <div className="flex items-center gap-3">
      <div className="p-2 bg-blue-50 rounded-lg">
        <Icon className="w-5 h-5 text-blue-600" />
      </div>
      <div>
        <p className="text-sm text-gray-600">{label}</p>
        <p className="text-lg font-semibold">
          {value}{" "}
          <span className="text-sm font-normal text-gray-500">{unit}</span>
        </p>
      </div>
    </div>
  </div>
);

export default function Dashboard() {
  const [trails, setTrails] = useState([]);
  const [selectedTrail, setSelectedTrail] = useState(null);
  const [isImporting, setIsImporting] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load trails on component mount
  useEffect(() => {
    loadTrails();
  }, []);

  const loadTrails = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/trails`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success) {
        setTrails(data.trails);

        // If no trails and demo data available, load demo
        if (data.trails.length === 0) {
          await loadDemoData();
        }
      } else {
        setError(data.error || "Failed to load trails");
      }
    } catch (err) {
      console.error("Failed to load trails:", err);
      setError(
        `Unable to connect to backend: ${err.message}. Please ensure the server is running.`
      );
    } finally {
      setIsLoading(false);
    }
  };

  const loadDemoData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/demo-data`);
      const data = await response.json();

      if (data.success && data.trail) {
        // Reload trails to include the demo trail
        await loadTrails();
      }
    } catch (err) {
      console.log("No demo data available:", err);
    }
  };

  // Handle trail click from Folium map
  const handleTrailClick = (trailData) => {
    console.log("Updating dashboard with trail data:", trailData);

    // Find the trail in our database
    const trail = trails.find((t) => t.id === trailData.id);
    if (trail) {
      setSelectedTrail(trail);
    } else {
      // Create a temporary trail object from the clicked data
      setSelectedTrail({
        id: trailData.id,
        name: trailData.name,
        distance: trailData.distance,
        elevation_gain: trailData.elevationGain,
        elevation_loss: trailData.elevationLoss,
        max_elevation: trailData.maxElevation,
        min_elevation: trailData.minElevation,
        rolling_hills_index: trailData.rollingHillsIndex,
        difficulty_score: trailData.difficultyScore,
        difficulty_level: trailData.difficultyLevel,
        elevation_profile: trailData.elevationProfile,
      });
    }
  };

  const handleGPXImport = async (event) => {
    const file = event.target.files[0];
    console.log("File selected:", file);

    if (file && file.name.endsWith(".gpx")) {
      console.log("Valid GPX file, starting upload...");
      setIsImporting(true);

      try {
        const formData = new FormData();
        formData.append("file", file);

        console.log("Sending upload request...");
        const response = await fetch(`${API_BASE_URL}/upload-gpx`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        console.log("Upload response:", data);

        if (data.success) {
          console.log(`Trail "${data.trail.name}" uploaded successfully!`);

          // Cool loading effect - show processing state
          setIsImporting(false);
          setIsProcessing(true);

          // Wait a moment for visual effect, then reload trails
          setTimeout(async () => {
            await loadTrails();
            setIsProcessing(false);
          }, 1000); // 1 second loading effect
        } else {
          console.error(
            "Error processing GPX file:",
            data.detail || data.error
          );
        }
      } catch (error) {
        console.error("Upload error:", error);
      } finally {
        // Only reset importing state if there was an error
        if (!data?.success) {
          setIsImporting(false);
        }
        // Reset file input
        event.target.value = "";
      }
    } else if (file) {
      console.warn("Please select a valid GPX file");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Loading Trails
          </h2>
          <p className="text-gray-600">Connecting to trail database...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md p-6">
          <div className="text-red-500 mb-4">
            <Database className="w-16 h-16 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Connection Error
          </h2>
          <p className="text-gray-600 text-sm mb-4">{error}</p>
          <Button onClick={loadTrails} className="mt-2">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Trail Hub</h1>
              <p className="text-gray-600">
                Community Trail Analysis & Sharing Platform
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-sm text-gray-600">
                {trails.length} trail{trails.length !== 1 ? "s" : ""} available
              </div>

              {/* GPX Import Button */}
              <div className="relative">
                <input
                  type="file"
                  accept=".gpx"
                  onChange={handleGPXImport}
                  className="hidden"
                  id="gpx-upload"
                  disabled={isImporting || isProcessing}
                  ref={(input) => {
                    if (input) {
                      window.openFileDialog = () => {
                        input.click();
                      };
                    }
                  }}
                />
                <Button
                  variant="outline"
                  size="sm"
                  disabled={isImporting || isProcessing}
                  className="inline-flex items-center"
                  type="button"
                  onClick={() => {
                    document.getElementById("gpx-upload").click();
                  }}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  {isImporting
                    ? "Uploading..."
                    : isProcessing
                    ? "Processing..."
                    : "Upload GPX"}
                </Button>
              </div>

              <Button onClick={loadTrails} variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 space-y-4">
        {/* Top Half - Map */}
        <Card className="h-[600px]">
          <CardContent className="p-4 h-full">
            <FoliumMap onTrailClick={handleTrailClick} trails={trails} />
          </CardContent>
        </Card>

        {/* Bottom Half - Trail Details */}
        {selectedTrail ? (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Trail Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="w-5 h-5" />
                    Trail Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-lg">
                      {selectedTrail?.name}
                    </h3>
                    <p className="text-gray-600">
                      Uploaded{" "}
                      {selectedTrail?.created_at
                        ? new Date(
                            selectedTrail.created_at
                          ).toLocaleDateString()
                        : "Recently"}
                    </p>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Difficulty</p>
                      <p className="font-medium">
                        {selectedTrail?.difficulty_level}
                      </p>
                    </div>
                    <DifficultyRing
                      score={selectedTrail?.difficulty_score}
                      label="Score"
                    />
                  </div>

                  <div className="pt-4 border-t">
                    <div className="flex items-center gap-2 mb-2">
                      <Activity className="w-4 h-4 text-blue-600" />
                      <span className="font-medium">Rolling Hills Index</span>
                      <Info className="w-4 h-4 text-gray-400" />
                    </div>
                    <div className="bg-gray-100 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full"
                        style={{
                          width: `${selectedTrail?.rolling_hills_index * 100}%`,
                        }}
                      />
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {(selectedTrail?.rolling_hills_index * 100).toFixed(1)}% -
                      Rolling terrain intensity
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Elevation Profile */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mountain className="w-5 h-5" />
                    Elevation Profile
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={selectedTrail?.elevation_profile}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="distance"
                          label={{
                            value: "Distance (km)",
                            position: "insideBottom",
                            offset: -5,
                          }}
                        />
                        <YAxis
                          label={{
                            value: "Elevation (m)",
                            angle: -90,
                            position: "insideLeft",
                          }}
                        />
                        <Tooltip
                          formatter={(value, name) => [
                            `${value}${name === "elevation" ? "m" : ""}`,
                            name === "elevation"
                              ? "Elevation"
                              : "Rolling Index",
                          ]}
                          labelFormatter={(label) => `Distance: ${label}km`}
                        />
                        <Area
                          type="monotone"
                          dataKey="elevation"
                          stroke="#2563eb"
                          fill="#3b82f6"
                          fillOpacity={0.3}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Trail Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              <StatCard
                icon={Ruler}
                label="Distance"
                value={selectedTrail?.distance}
                unit="km"
              />
              <StatCard
                icon={TrendingUp}
                label="Elevation Gain"
                value={selectedTrail?.elevation_gain}
                unit="m"
              />
              <StatCard
                icon={Mountain}
                label="Max Elevation"
                value={selectedTrail?.max_elevation}
                unit="m"
              />
              <StatCard
                icon={Gauge}
                label="Avg Gradient"
                value={(
                  (selectedTrail?.elevation_gain /
                    (selectedTrail?.distance * 1000)) *
                  100
                ).toFixed(1)}
                unit="%"
              />
              <StatCard
                icon={Activity}
                label="Rolling Intensity"
                value={(selectedTrail?.rolling_hills_index * 10).toFixed(1)}
                unit="/10"
              />
              <StatCard
                icon={MapPin}
                label="Difficulty"
                value={selectedTrail?.difficulty_level}
                unit=""
              />
            </div>
          </>
        ) : (
          <Card>
            <CardContent className="p-8 text-center">
              <Mountain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Select a Trail
              </h3>
              <p className="text-gray-600">
                Click on a trail in the map above to view its detailed analysis
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
