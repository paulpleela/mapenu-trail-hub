import React, { useState, useEffect, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
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
  BarChart,
  Bar,
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
import InfoPage from "./InfoPage";

// API URL
const API_BASE_URL = "http://localhost:8000";

// Helper function for terrain variety description
const getTerrainVarietyDescription = (score) => {
  if (score === null || score === undefined || isNaN(score)) {
    return "Terrain variety data not available";
  }

  const numScore = Number(score);
  if (numScore >= 8)
    return "Highly varied terrain with multiple elevation zones";
  if (numScore >= 6)
    return "Good terrain variety with several elevation changes";
  if (numScore >= 4)
    return "Moderate terrain variety with some elevation changes";
  if (numScore >= 2)
    return "Limited terrain variety, mostly consistent elevation";
  return "Flat or very consistent terrain";
};

// Helper function to normalize rolling hills index for display (0-10 scale)
const normalizeRollingHillsForDisplay = (rawIndex) => {
  if (rawIndex === null || rawIndex === undefined || isNaN(rawIndex)) {
    return 0;
  }
  // Use logarithmic scale to map wide range to 0-10
  // Most trails are 10-50, extreme trails can be 100+
  // Formula: 10 * (1 - e^(-rawIndex/15))
  // This maps: 0→0, 15→6.3, 30→8.6, 45→9.5, 60→9.8, 100→9.99
  const normalized = 10 * (1 - Math.exp(-rawIndex / 15));
  return Math.min(10, normalized); // Cap at 10
};

// Removed getWeatherExposureFromScore function - weather feature disabled

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
    <div className="w-full h-full rounded-lg overflow-hidden border shadow-lg">
      <iframe
        src={`${API_BASE_URL}${mapUrl}`}
        className="w-full h-full border-0"
        title="Interactive Trail Map"
        sandbox="allow-scripts allow-same-origin allow-popups"
        style={{ minHeight: "500px" }}
        loading="lazy"
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

// Enhanced stat card component with tooltip
const StatCard = ({ icon: Icon, label, value, unit, tooltip, description }) => (
  <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200 hover:-translate-y-1 relative group">
    <div className="flex items-center gap-3">
      <div className="p-2 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
        <Icon className="w-5 h-5 text-blue-600" />
      </div>
      <div className="flex-1">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1 flex items-center gap-1">
          {label}
          {tooltip && <Info className="w-3 h-3 text-gray-400" />}
        </p>
        <p className="text-lg font-bold text-gray-800">
          {value}{" "}
          <span className="text-sm font-normal text-gray-500">{unit}</span>
        </p>
        {description && (
          <p className="text-xs text-gray-500 mt-1 italic">{description}</p>
        )}
      </div>
    </div>
    {/* Tooltip */}
    {tooltip && (
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 max-w-xs">
        {tooltip}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
      </div>
    )}
  </div>
);

export default function Dashboard() {
  const [trails, setTrails] = useState([]);
  const [selectedTrail, setSelectedTrail] = useState(null);
  const [similarTrails, setSimilarTrails] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [isImporting, setIsImporting] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDuplicate, setIsDuplicate] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showInfoPage, setShowInfoPage] = useState(false);

  // DEM and terrain state
  const [demData, setDemData] = useState(null);
  const [demCoverage, setDemCoverage] = useState(null);
  const [terrain3D, setTerrain3D] = useState(null);
  const [loading3D, setLoading3D] = useState(false);

  // Load trails on component mount
  useEffect(() => {
    loadTrails();
    loadAnalytics();
    loadDemCoverage();
  }, []);

  // Load DEM data when trail is selected
  useEffect(() => {
    if (selectedTrail?.id) {
      // Clear previous 3D terrain when selecting new trail
      setTerrain3D(null);
      loadDemData(selectedTrail.id);
      load3DTerrain(selectedTrail.id); // Auto-generate 3D terrain view
      loadElevationSources(selectedTrail.id); // Load multi-source elevation data
    }
  }, [selectedTrail]);

  const loadAnalytics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/overview`);
      const data = await response.json();
      if (data.success) {
        setAnalytics(data.analytics);
      }
    } catch (err) {
      console.error("Failed to load analytics:", err);
    }
  };

  const loadSimilarTrails = async (trailId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/trail/${trailId}/similar`);
      const data = await response.json();
      if (data.success) {
        setSimilarTrails(data.similar_trails);
      }
    } catch (err) {
      console.error("Failed to load similar trails:", err);
      setSimilarTrails([]);
    }
  };

  // Multi-source elevation data
  const [elevationSources, setElevationSources] = useState(null);
  const [selectedElevationSource, setSelectedElevationSource] =
    useState("Overall");
  const [loadingElevationSources, setLoadingElevationSources] = useState(false);

  // LiDAR upload
  const [isUploadingLidar, setIsUploadingLidar] = useState(false);
  const [lidarUploadSuccess, setLidarUploadSuccess] = useState(false);

  const loadElevationSources = async (trailId) => {
    setLoadingElevationSources(true);
    console.log("🔍 Loading elevation sources for trail:", trailId);
    try {
      const response = await fetch(
        `${API_BASE_URL}/trail/${trailId}/elevation-sources`
      );
      const data = await response.json();
      console.log("📊 Elevation sources response:", data);

      if (data.success) {
        console.log("✅ Available sources:", {
          GPX: data.sources.GPX?.available,
          LiDAR: data.sources.LiDAR?.available,
          QSpatial: data.sources.QSpatial?.available,
          Overall: data.sources.Overall?.available,
        });

        setElevationSources(data);
        // Auto-select first available source if Overall not available
        if (!data.sources.Overall?.available) {
          if (data.sources.QSpatial?.available) {
            setSelectedElevationSource("QSpatial");
          } else if (data.sources.LiDAR?.available) {
            setSelectedElevationSource("LiDAR");
          } else if (data.sources.GPX?.available) {
            setSelectedElevationSource("GPX");
          }
        }
      } else {
        console.error("❌ Elevation sources failed:", data.error);
        setElevationSources({ error: data.error });
      }
    } catch (err) {
      console.error("❌ Error loading elevation sources:", err);
      setElevationSources({ error: err.message });
    } finally {
      setLoadingElevationSources(false);
    }
  };

  const loadDemData = async (trailId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/trail/${trailId}/dem-analysis`
      );
      const data = await response.json();
      if (data.success) {
        setDemData(data);
      } else {
        console.error("DEM analysis failed:", data.error);
        setDemData({ error: data.error });
      }
    } catch (err) {
      console.error("Failed to load DEM data:", err);
      setDemData({ error: "Failed to connect to DEM analysis service" });
    }
  };

  const load3DTerrain = async (trailId) => {
    if (!trailId) return;

    setLoading3D(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/trail/${trailId}/3d-terrain`
      );
      const data = await response.json();
      if (data.success) {
        setTerrain3D(data);
      } else {
        setTerrain3D({ error: data.error });
      }
    } catch (err) {
      console.error("Failed to load 3D terrain:", err);
      setTerrain3D({ error: "Failed to generate 3D visualization" });
    } finally {
      setLoading3D(false);
    }
  };

  const loadDemCoverage = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/dem/coverage`);
      const data = await response.json();
      if (data.success) {
        setDemCoverage(data.coverage);
      }
    } catch (err) {
      console.error("Failed to load DEM coverage:", err);
      setDemCoverage(null);
    }
  };

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
      loadSimilarTrails(trail.id); // Load similar trails
      loadDemData(trail.id); // Load DEM analysis data
    } else {
      // Create a temporary trail object from the clicked data
      const tempTrail = {
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
      };
      setSelectedTrail(tempTrail);
      if (tempTrail.id) {
        loadSimilarTrails(tempTrail.id);
        loadDemData(tempTrail.id);
      }
    }
  };

  const handleGPXImport = async (event) => {
    const file = event.target.files[0];
    console.log("File selected:", file);

    if (file && file.name.endsWith(".gpx")) {
      console.log("Valid GPX file, starting upload...");
      setIsImporting(true);
      setIsDuplicate(false); // Reset duplicate state

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

        if (response.ok && data.success) {
          console.log(`Trail "${data.trail.name}" uploaded successfully!`);

          // Cool loading effect - show processing state
          setIsImporting(false);
          setIsProcessing(true);

          // Wait a moment for visual effect, then reload trails
          setTimeout(async () => {
            await loadTrails();
            await loadAnalytics(); // Refresh analytics too
            setIsProcessing(false);
          }, 1000); // 1 second loading effect
        } else {
          // Handle errors including duplicates
          let errorMessage = data.detail || data.error || "Upload failed";

          if (response.status === 409) {
            // Duplicate trail error
            console.warn("Duplicate trail detected:", errorMessage);
            setIsImporting(false);
            setIsDuplicate(true);

            // Show duplicate feedback briefly
            setTimeout(() => {
              setIsDuplicate(false);
            }, 2000); // Show for 2 seconds
          } else {
            console.error("Error processing GPX file:", errorMessage);
            setIsImporting(false);
          }
        }
      } catch (error) {
        console.error("Upload error:", error);
        setIsImporting(false);
      } finally {
        // Reset file input
        event.target.value = "";
      }
    } else if (file) {
      console.warn("Please select a valid GPX file");
    }
  };

  const handleLidarUpload = async (event) => {
    const file = event.target.files?.[0];

    if (file && file.name.endsWith(".las")) {
      setIsUploadingLidar(true);
      setLidarUploadSuccess(false);

      try {
        const formData = new FormData();
        formData.append("file", file);

        // Add trail_id if a trail is selected
        if (selectedTrail?.id) {
          formData.append("trail_id", selectedTrail.id);
        }

        const response = await fetch(`${API_BASE_URL}/upload-lidar`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (response.ok && data.success) {
          console.log("LiDAR file uploaded successfully:", data);
          setLidarUploadSuccess(true);

          // Reload elevation sources if a trail is selected
          if (selectedTrail?.id) {
            loadElevationSources(selectedTrail.id);
          }

          // Reset success message after 3 seconds
          setTimeout(() => {
            setLidarUploadSuccess(false);
          }, 3000);
        } else {
          console.error("LiDAR upload failed:", data.error || data.detail);
          alert(
            `Upload failed: ${data.error || data.detail || "Unknown error"}`
          );
        }
      } catch (error) {
        console.error("LiDAR upload error:", error);
        alert(`Upload error: ${error.message}`);
      } finally {
        setIsUploadingLidar(false);
        // Reset file input
        event.target.value = "";
      }
    } else if (file) {
      alert("Please select a valid .las file");
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
              <h1 className="text-2xl font-bold text-gray-900">
                MAPENU Trail Hub
              </h1>
              <p className="text-gray-600">
                Mapped Analysis Platform for Elevation and Navigation Utility
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
                  disabled={isImporting || isProcessing || isDuplicate}
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
                    : isDuplicate
                    ? "Duplicate Trail!"
                    : "Upload GPX"}
                </Button>
              </div>

              {/* LiDAR Upload Button */}
              <div className="relative">
                <input
                  type="file"
                  accept=".las"
                  onChange={handleLidarUpload}
                  id="lidar-upload"
                  className="hidden"
                />
                <Button
                  variant="outline"
                  size="sm"
                  disabled={isUploadingLidar}
                  className={`inline-flex items-center ${
                    lidarUploadSuccess
                      ? "bg-green-100 border-green-500 text-green-700"
                      : ""
                  }`}
                  type="button"
                  onClick={() => {
                    document.getElementById("lidar-upload").click();
                  }}
                >
                  <Database className="w-4 h-4 mr-2" />
                  {isUploadingLidar
                    ? "Uploading LiDAR..."
                    : lidarUploadSuccess
                    ? "LiDAR Uploaded ✓"
                    : "Upload LiDAR"}
                </Button>
              </div>

              <Button onClick={loadTrails} variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>

              <Button
                onClick={() => window.open("/measure", "_blank")}
                variant="outline"
                size="sm"
              >
                <Ruler className="w-4 h-4 mr-2" />
                Measure GPX
              </Button>

              <Button
                onClick={() => setShowAnalytics(!showAnalytics)}
                variant={showAnalytics ? "default" : "outline"}
                size="sm"
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                Analytics
              </Button>

              <Button
                onClick={() => setShowInfoPage(true)}
                variant="outline"
                size="sm"
                className="bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-300"
              >
                <Info className="w-4 h-4 mr-2" />
                Help & Guide
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 space-y-4">
        {/* Analytics Dashboard */}
        {showAnalytics && analytics && (
          <Card className="shadow-lg border-0 bg-gradient-to-br from-white to-gray-50">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <div className="p-3 bg-purple-100 rounded-xl">
                  <TrendingUp className="w-6 h-6 text-purple-600" />
                </div>
                Platform Analytics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <StatCard
                  icon={Database}
                  label="Total Trails"
                  value={analytics.total_trails}
                  unit="trails"
                />
                <StatCard
                  icon={Ruler}
                  label="Total Distance"
                  value={analytics.total_distance_km}
                  unit="km"
                />
                <StatCard
                  icon={Mountain}
                  label="Total Elevation"
                  value={analytics.total_elevation_gain_m}
                  unit="m"
                />
                <StatCard
                  icon={Gauge}
                  label="Avg Difficulty"
                  value={analytics.avg_difficulty_score}
                  unit="/10"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl p-4 shadow-sm">
                  <h4 className="font-semibold text-gray-800 mb-4">
                    Difficulty Distribution
                  </h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart
                      data={Object.entries(
                        analytics.difficulty_distribution
                      ).map(([level, count]) => ({ level, count }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="level" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip />
                      <Bar
                        dataKey="count"
                        fill="#3b82f6"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="bg-white rounded-xl p-4 shadow-sm">
                  <h4 className="font-semibold text-gray-800 mb-4">
                    Distance Categories
                  </h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart
                      data={Object.entries(analytics.distance_categories).map(
                        ([category, count]) => ({
                          category: category.replace(/[<>()]/g, ""),
                          count,
                        })
                      )}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis
                        dataKey="category"
                        stroke="#64748b"
                        fontSize={12}
                      />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip />
                      <Bar
                        dataKey="count"
                        fill="#10b981"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 mt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-semibold text-gray-800">
                      🏔️ Most Challenging
                    </h5>
                    <p className="text-gray-600">
                      {analytics.most_challenging}
                    </p>
                  </div>
                  <div>
                    <h5 className="font-semibold text-gray-800">
                      📏 Longest Trail
                    </h5>
                    <p className="text-gray-600">{analytics.longest_trail}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Top Half - Map */}
        <Card className="h-[600px]">
          <CardContent className="p-4 h-full">
            <FoliumMap onTrailClick={handleTrailClick} trails={trails} />
          </CardContent>
        </Card>

        {/* Bottom Half - Trail Details */}
        {selectedTrail ? (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Trail Info */}
              <Card className="shadow-lg border-0 bg-gradient-to-br from-white to-gray-50">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-3 text-xl">
                    <div className="p-3 bg-blue-100 rounded-xl">
                      <MapPin className="w-6 h-6 text-blue-600" />
                    </div>
                    Trail Overview
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="text-center">
                    <h3 className="font-bold text-2xl text-gray-800 mb-2">
                      {selectedTrail?.name}
                    </h3>
                    <p className="text-gray-500 text-sm">
                      Added{" "}
                      {selectedTrail?.created_at
                        ? new Date(
                            selectedTrail.created_at
                          ).toLocaleDateString()
                        : "Recently"}
                    </p>
                  </div>

                  <div className="flex items-center justify-between bg-white rounded-xl p-4 shadow-sm">
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-1">
                        Difficulty Level
                      </p>
                      <p className="text-xl font-bold text-gray-800">
                        {selectedTrail?.difficulty_level}
                      </p>
                    </div>
                    <DifficultyRing
                      score={selectedTrail?.difficulty_score}
                      label="Score"
                    />
                  </div>

                  <div className="bg-white rounded-xl p-4 shadow-sm">
                    <div className="flex items-center gap-2 mb-3">
                      <Activity className="w-5 h-5 text-blue-600" />
                      <span className="font-semibold text-gray-800">
                        Rolling Hills Index
                      </span>
                    </div>
                    <div className="bg-gray-200 rounded-full h-4 mb-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-600 h-4 rounded-full shadow-sm transition-all duration-300"
                        style={{
                          width: `${
                            normalizeRollingHillsForDisplay(
                              selectedTrail?.rolling_hills_index
                            ) * 10
                          }%`,
                        }}
                      />
                    </div>
                    <p className="text-sm text-gray-600 font-medium">
                      {normalizeRollingHillsForDisplay(
                        selectedTrail?.rolling_hills_index
                      ).toFixed(1)}
                      /10 terrain intensity
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Elevation Profile */}
              <Card className="lg:col-span-2 shadow-lg border-0 bg-gradient-to-br from-white to-gray-50 overflow-visible">
                <CardHeader className="pb-4 overflow-visible">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-3 text-xl">
                      <div className="p-3 bg-green-100 rounded-xl">
                        <Mountain className="w-6 h-6 text-green-600" />
                      </div>
                      Elevation Profile
                    </CardTitle>
                    {/* Data Source Selector */}
                    {loadingElevationSources ? (
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Loading data sources...
                      </div>
                    ) : elevationSources &&
                      elevationSources.summary?.total_sources_available > 0 ? (
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-gray-600">
                          Data Source:
                        </span>
                        <Select
                          value={selectedElevationSource}
                          onValueChange={setSelectedElevationSource}
                        >
                          <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Select source" />
                          </SelectTrigger>
                          <SelectContent>
                            {elevationSources.sources?.Overall?.available && (
                              <SelectItem value="Overall">
                                Overall (Average)
                              </SelectItem>
                            )}
                            {elevationSources.sources?.GPX?.available && (
                              <SelectItem value="GPX">GPX</SelectItem>
                            )}
                            {elevationSources.sources?.LiDAR?.available && (
                              <SelectItem value="LiDAR">LiDAR</SelectItem>
                            )}
                            {elevationSources.sources?.QSpatial?.available && (
                              <SelectItem value="QSpatial">
                                QSpatial DEM
                              </SelectItem>
                            )}
                          </SelectContent>
                        </Select>
                      </div>
                    ) : elevationSources ? (
                      <div className="text-sm text-amber-600 bg-amber-50 px-3 py-2 rounded-md">
                        ⚠️ No elevation data sources available for this trail
                      </div>
                    ) : null}
                  </div>
                  {/* Source Info Badge */}
                  {elevationSources?.sources?.[selectedElevationSource] && (
                    <div className="mt-2 text-xs text-gray-500">
                      {elevationSources.sources[selectedElevationSource].source}
                      {elevationSources.sources[selectedElevationSource]
                        .coverage_percent && (
                        <span className="ml-2">
                          • Coverage:{" "}
                          {elevationSources.sources[
                            selectedElevationSource
                          ].coverage_percent.toFixed(1)}
                          %
                        </span>
                      )}
                    </div>
                  )}
                  {/* Debug: Show availability status */}
                  {elevationSources && elevationSources.summary && (
                    <div className="mt-2 text-xs text-gray-400 flex gap-2">
                      <span>Available:</span>
                      {elevationSources.summary.gpx_available && (
                        <span className="text-green-600">✓ GPX</span>
                      )}
                      {elevationSources.summary.lidar_available && (
                        <span className="text-green-600">✓ LiDAR</span>
                      )}
                      {elevationSources.summary.qspatial_available && (
                        <span className="text-green-600">✓ QSpatial</span>
                      )}
                      {elevationSources.summary.total_sources_available ===
                        0 && (
                        <span className="text-red-600">None available</span>
                      )}
                    </div>
                  )}
                </CardHeader>
                <CardContent>
                  {loadingElevationSources ? (
                    <div className="flex items-center justify-center h-80">
                      <div className="text-center">
                        <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-blue-500" />
                        <p className="text-gray-600">
                          Loading elevation data...
                        </p>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="bg-white rounded-xl p-4 shadow-sm mb-6">
                        <div className="h-80">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart
                              data={(() => {
                                // Prepare chart data from selected source
                                const sourceData =
                                  elevationSources?.sources?.[
                                    selectedElevationSource
                                  ];
                                if (!sourceData?.available) {
                                  return selectedTrail?.elevation_profile || [];
                                }

                                // Convert to chart format
                                return sourceData.elevations.map(
                                  (elev, idx) => ({
                                    distance:
                                      sourceData.distances[idx]?.toFixed(2) ||
                                      0,
                                    elevation: parseFloat(elev.toFixed(2)),
                                    slope:
                                      sourceData.slopes?.[idx]?.toFixed(2) || 0,
                                  })
                                );
                              })()}
                            >
                              <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="#f1f5f9"
                              />
                              <XAxis
                                dataKey="distance"
                                label={{
                                  value: "Distance (km)",
                                  position: "insideBottom",
                                  offset: -5,
                                }}
                                stroke="#64748b"
                                fontSize={12}
                              />
                              <YAxis
                                yAxisId="left"
                                label={{
                                  value: "Elevation (m)",
                                  angle: -90,
                                  position: "insideLeft",
                                }}
                                stroke="#64748b"
                                fontSize={12}
                              />
                              <YAxis
                                yAxisId="right"
                                orientation="right"
                                label={{
                                  value: "Slope (%)",
                                  angle: 90,
                                  position: "insideRight",
                                }}
                                stroke="#f59e0b"
                                fontSize={12}
                              />
                              <Tooltip
                                formatter={(value, name) => [
                                  `${value}${
                                    name === "elevation"
                                      ? "m"
                                      : name === "slope"
                                      ? "%"
                                      : ""
                                  }`,
                                  name === "elevation"
                                    ? "Elevation"
                                    : name === "slope"
                                    ? "Slope"
                                    : name,
                                ]}
                                labelFormatter={(label) =>
                                  `Distance: ${label}km`
                                }
                                contentStyle={{
                                  backgroundColor: "#1f2937",
                                  color: "#f9fafb",
                                  border: "none",
                                  borderRadius: "12px",
                                  boxShadow: "0 10px 25px rgba(0,0,0,0.15)",
                                }}
                              />
                              <Area
                                yAxisId="left"
                                type="monotone"
                                dataKey="elevation"
                                stroke="#3b82f6"
                                fill="url(#elevationGradient)"
                                strokeWidth={3}
                              />
                              <Line
                                yAxisId="right"
                                type="monotone"
                                dataKey="slope"
                                stroke="#f59e0b"
                                strokeWidth={2}
                                strokeDasharray="5 5"
                                dot={false}
                                name="Slope"
                              />
                              <defs>
                                <linearGradient
                                  id="elevationGradient"
                                  x1="0"
                                  y1="0"
                                  x2="0"
                                  y2="1"
                                >
                                  <stop
                                    offset="5%"
                                    stopColor="#3b82f6"
                                    stopOpacity={0.4}
                                  />
                                  <stop
                                    offset="95%"
                                    stopColor="#3b82f6"
                                    stopOpacity={0.1}
                                  />
                                </linearGradient>
                              </defs>
                              {/* Min/Max elevation reference lines */}
                              {selectedTrail?.max_elevation && (
                                <Line
                                  yAxisId="left"
                                  type="step"
                                  dataKey={() => selectedTrail.max_elevation}
                                  stroke="#ef4444"
                                  strokeDasharray="8 4"
                                  strokeWidth={2}
                                  dot={false}
                                  name="Max Elevation"
                                />
                              )}
                              {selectedTrail?.min_elevation && (
                                <Line
                                  yAxisId="left"
                                  type="step"
                                  dataKey={() => selectedTrail.min_elevation}
                                  stroke="#22c55e"
                                  strokeDasharray="8 4"
                                  strokeWidth={2}
                                  dot={false}
                                  name="Min Elevation"
                                />
                              )}
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                      {/* Elevation Stats */}
                    </>
                  )}

                  <div className="mt-4"></div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <StatCard
                      icon={TrendingUp}
                      label="Elevation Gain"
                      value={selectedTrail?.elevation_gain}
                      unit="m"
                      tooltip="Total upward elevation change throughout the trail"
                    />
                    <StatCard
                      icon={TrendingUp}
                      label="Elevation Loss"
                      value={selectedTrail?.elevation_loss}
                      unit="m"
                      tooltip="Total downward elevation change throughout the trail"
                    />
                    <StatCard
                      icon={Mountain}
                      label="Elevation Range"
                      value={`${selectedTrail?.min_elevation}m - ${selectedTrail?.max_elevation}m`}
                      unit=""
                      description={`${
                        selectedTrail?.max_elevation -
                        selectedTrail?.min_elevation
                      }m span`}
                      tooltip="Minimum to maximum elevation with total elevation span"
                    />
                    <StatCard
                      icon={Gauge}
                      label="Slope Range"
                      value={`${selectedTrail?.avg_slope?.toFixed(1)}% avg`}
                      unit=""
                      description={`${selectedTrail?.max_slope?.toFixed(
                        1
                      )}% max`}
                      tooltip="Average slope with maximum slope encountered - yellow line shows slope variation"
                    />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Trail Statistics */}
            {/* Terrain Difficulty */}
            <Card className="shadow-lg border-0 bg-gradient-to-br from-white to-gray-50">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-3 text-xl">
                  <div className="p-3 bg-purple-100 rounded-xl">
                    <Activity className="w-6 h-6 text-purple-600" />
                  </div>
                  Trail Metrics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <StatCard
                    icon={Ruler}
                    label="Distance"
                    value={selectedTrail?.distance}
                    unit="km"
                    tooltip="Total trail distance measured from GPS track"
                  />
                  <StatCard
                    icon={Info}
                    label="Est. Time"
                    value={selectedTrail?.estimated_time_hours}
                    unit="hrs"
                    tooltip="Estimated completion time using Naismith's Rule + terrain adjustments"
                  />
                  <StatCard
                    icon={Activity}
                    label="Rolling Intensity"
                    value={normalizeRollingHillsForDisplay(
                      selectedTrail?.rolling_hills_index
                    ).toFixed(1)}
                    unit="/10"
                    tooltip="How much the trail goes up and down - higher = more tiring"
                  />
                  <StatCard
                    icon={TrendingUp}
                    label="Hills Count"
                    value={selectedTrail?.rolling_hills_count || 0}
                    unit="hills"
                    tooltip="Number of significant elevation changes (1m+ threshold) on the trail"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Trail Insights Section */}
            {selectedTrail && (
              <Card className="shadow-lg border-0 bg-gradient-to-br from-white to-gray-50">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-3 text-xl">
                    <div className="p-3 bg-emerald-100 rounded-xl">
                      <Info className="w-6 h-6 text-emerald-600" />
                    </div>
                    Trail Insights
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 gap-6">
                    {/* Terrain Analysis Box */}
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Mountain className="w-5 h-5 text-green-600" />
                        <h4 className="font-semibold text-gray-800">
                          Terrain Analysis
                        </h4>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">
                        <strong>Variety Score:</strong>{" "}
                        {selectedTrail?.terrain_variety_score}/10
                      </p>
                      <p className="text-sm text-gray-700 mb-2">
                        <strong>Total Elevation Change:</strong>{" "}
                        {selectedTrail?.elevation_change_total}m
                      </p>
                      <p className="text-sm text-gray-600">
                        {getTerrainVarietyDescription(
                          selectedTrail?.terrain_variety_score
                        )}
                      </p>
                    </div>

                    {/* Effort Analysis Box */}
                    <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Gauge className="w-5 h-5 text-orange-600" />
                        <h4 className="font-semibold text-gray-800">
                          Effort Estimation
                        </h4>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">
                        <strong>Estimated Time:</strong>{" "}
                        {selectedTrail?.estimated_time_hours} hours
                      </p>
                      <p className="text-sm text-gray-700 mb-2">
                        <strong>Rolling Intensity:</strong>{" "}
                        {normalizeRollingHillsForDisplay(
                          selectedTrail?.rolling_hills_index
                        ).toFixed(1)}
                        /10
                      </p>
                      <p className="text-sm text-gray-600">
                        Based on Naismith's Rule: 5km/h + 1h per 600m elevation
                        gain, adjusted for terrain complexity
                      </p>
                    </div>

                    {/* Technical Difficulty Box */}
                    <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Activity className="w-5 h-5 text-purple-600" />
                        <h4 className="font-semibold text-gray-800">
                          Technical Difficulty
                        </h4>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">
                        <strong>Technical Rating:</strong>{" "}
                        {selectedTrail?.technical_rating}/10
                      </p>
                      <p className="text-sm text-gray-700 mb-2">
                        <strong>Max Slope:</strong>{" "}
                        {selectedTrail?.max_slope?.toFixed(1)}% |{" "}
                        <strong>Avg:</strong>{" "}
                        {selectedTrail?.avg_slope?.toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        Combines maximum slope and rolling terrain index for
                        overall technical challenge
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Enhanced DEM/LiDAR Analysis Section */}
            {selectedTrail && (
              <Card className="shadow-lg border-0 bg-gradient-to-br from-white to-gray-50">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-3 text-xl">
                    <div className="p-3 bg-indigo-100 rounded-xl">
                      <Mountain className="w-6 h-6 text-indigo-600" />
                    </div>
                    High-Resolution Terrain Data
                    <span className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                      DEM + LiDAR
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <Mountain className="w-6 h-6 text-green-600" />
                      <h4 className="font-semibold text-gray-800 text-lg">
                        Real-Time DEM Analysis
                      </h4>
                      {selectedTrail?.id && (
                        <button
                          onClick={() => loadDemData(selectedTrail.id)}
                          className="ml-auto p-1 hover:bg-green-200 rounded text-green-600"
                          title="Refresh DEM analysis"
                        >
                          <RefreshCw className="w-4 h-4" />
                        </button>
                      )}
                    </div>

                    {demData?.error ? (
                      <div className="bg-yellow-100 border border-yellow-400 rounded-lg p-4">
                        <p className="text-yellow-800 font-semibold">
                          ⚠️ DEM Analysis Unavailable
                        </p>
                        <p className="text-yellow-700 text-sm mt-1">
                          {demData.error}
                        </p>
                        <p className="text-yellow-600 text-xs mt-2">
                          Ensure your 6GB DEM files are properly located and
                          rasterio is installed.
                        </p>
                      </div>
                    ) : demData?.success ? (
                      <div className="space-y-4">
                        {/* Elevation Profile Analysis */}
                        {demData.elevation_analysis?.elevation_profile && (
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-semibold text-gray-800 mb-3">
                              High-Resolution Elevation Profile
                            </h5>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-gray-600">
                                  Sample Points:
                                </span>
                                <span className="font-bold text-blue-600 ml-2">
                                  {
                                    demData.elevation_analysis.elevation_profile
                                      .elevations.length
                                  }
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-600">
                                  Resolution:
                                </span>
                                <span className="font-bold text-green-600 ml-2">
                                  {demData.elevation_analysis.sample_interval}
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-600">
                                  Max Elevation:
                                </span>
                                <span className="font-bold text-purple-600 ml-2">
                                  {demData.elevation_analysis.statistics.max_elevation.toFixed(
                                    1
                                  )}
                                  m
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-600">
                                  Min Elevation:
                                </span>
                                <span className="font-bold text-indigo-600 ml-2">
                                  {demData.elevation_analysis.statistics.min_elevation.toFixed(
                                    1
                                  )}
                                  m
                                </span>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Terrain Features */}
                        {demData.terrain_features?.success && (
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-semibold text-gray-800 mb-3">
                              Identified Terrain Features
                            </h5>
                            {demData.terrain_features.features.length > 0 ? (
                              <div className="space-y-2 max-h-48 overflow-y-auto">
                                {demData.terrain_features.features
                                  .slice(0, 10)
                                  .map((feature, idx) => (
                                    <div
                                      key={idx}
                                      className="flex items-center justify-between text-sm border-b border-gray-100 pb-1"
                                    >
                                      <span className="font-medium text-gray-700">
                                        {feature.type}
                                      </span>
                                      <span className="text-gray-600">
                                        {feature.elevation
                                          ? `${feature.elevation.toFixed(1)}m`
                                          : feature.slope
                                          ? `${feature.slope.toFixed(1)}%`
                                          : ""}
                                      </span>
                                      <span className="text-xs text-gray-500">
                                        {feature.distance
                                          ? `${feature.distance.toFixed(0)}m`
                                          : ""}
                                      </span>
                                    </div>
                                  ))}
                                {demData.terrain_features.features.length >
                                  10 && (
                                  <p className="text-xs text-gray-500 text-center">
                                    +
                                    {demData.terrain_features.features.length -
                                      10}{" "}
                                    more features
                                  </p>
                                )}
                              </div>
                            ) : (
                              <p className="text-gray-500 text-sm">
                                No significant terrain features detected
                              </p>
                            )}

                            <div className="mt-3 pt-3 border-t border-gray-200">
                              <div className="grid grid-cols-3 gap-2 text-xs">
                                <div className="text-center">
                                  <div className="text-lg font-bold text-blue-600">
                                    {demData.terrain_features.summary?.peaks ||
                                      0}
                                  </div>
                                  <div className="text-gray-600">Peaks</div>
                                </div>
                                <div className="text-center">
                                  <div className="text-lg font-bold text-green-600">
                                    {demData.terrain_features.summary
                                      ?.valleys || 0}
                                  </div>
                                  <div className="text-gray-600">Valleys</div>
                                </div>
                                <div className="text-center">
                                  <div className="text-lg font-bold text-red-600">
                                    {demData.terrain_features.summary
                                      ?.steep_sections || 0}
                                  </div>
                                  <div className="text-gray-600">
                                    Steep Grades
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 3D Terrain Visualization */}
                        <div className="bg-white rounded-lg p-4">
                          <div className="flex items-center justify-between mb-3">
                            <h5 className="font-semibold text-gray-800">
                              3D Terrain Visualization
                            </h5>
                            {loading3D && (
                              <div className="flex items-center text-blue-600 text-xs">
                                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600 mr-2"></div>
                                Generating...
                              </div>
                            )}
                          </div>

                          {terrain3D?.visualization_type === "interactive" &&
                          terrain3D?.visualization_html ? (
                            <div className="text-center">
                              <div className="w-full h-screen rounded-lg border shadow-lg overflow-hidden">
                                <iframe
                                  src={`${API_BASE_URL}/trail/${selectedTrail.id}/3d-terrain-viewer`}
                                  className="w-full h-full border-0"
                                  title="Interactive 3D Terrain Visualization"
                                  sandbox="allow-scripts allow-same-origin"
                                  loading="lazy"
                                />
                              </div>
                              <p className="text-xs text-gray-600 mt-2">
                                🎮 Interactive 3D terrain - Click and drag to
                                rotate, scroll to zoom
                              </p>
                            </div>
                          ) : terrain3D?.visualization ? (
                            <div className="text-center">
                              <img
                                src={terrain3D.visualization}
                                alt="3D Terrain Visualization"
                                className="max-w-full h-auto rounded-lg border"
                              />
                              <p className="text-xs text-gray-600 mt-2">
                                3D terrain model showing trail path over DEM
                                data
                              </p>
                            </div>
                          ) : terrain3D?.error ? (
                            <div className="text-center py-4">
                              <p className="text-red-600 text-sm">
                                {terrain3D.error}
                              </p>
                            </div>
                          ) : !terrain3D ? (
                            <div className="text-center py-8 text-gray-500 border-2 border-dashed border-gray-200 rounded-lg">
                              <Mountain className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                              <p>3D terrain visualization will appear here</p>
                              <p className="text-xs mt-1">
                                Shows trail path over real DEM elevation data
                              </p>
                            </div>
                          ) : null}
                        </div>

                        {/* Data Quality Info */}
                        <div className="bg-gradient-to-r from-blue-100 to-green-100 rounded-lg p-3">
                          <p className="text-sm text-gray-700">
                            <strong>Data Sources:</strong>{" "}
                            {demData.elevation_analysis?.data_sources?.length ||
                              0}{" "}
                            DEM tiles •<strong> Resolution:</strong>{" "}
                            {demData.data_quality?.resolution} •
                            <strong> Accuracy:</strong>{" "}
                            {demData.data_quality?.accuracy}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="animate-pulse">
                          <Database className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                          <p className="text-gray-500">
                            Analyzing 6GB of high-resolution DEM data...
                          </p>
                          <p className="text-gray-400 text-xs mt-2">
                            Processing Brisbane Government elevation tiles
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        ) : (
          <Card className="shadow-lg border-0 bg-gradient-to-br from-gray-50 to-white">
            <CardContent className="p-12 text-center">
              <div className="p-4 bg-gray-100 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <Mountain className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-2xl font-bold text-gray-800 mb-3">
                Select a Trail
              </h3>
              <p className="text-gray-500 text-lg max-w-md mx-auto">
                Click on any trail marker in the map above to explore detailed
                analytics and insights
              </p>
            </CardContent>
          </Card>
        )}

        {/* Similar Trails Recommendations */}
        {selectedTrail && similarTrails.length > 0 && (
          <Card className="shadow-lg border-0 bg-gradient-to-br from-white to-gray-50">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <div className="p-3 bg-yellow-100 rounded-xl">
                  <MapPin className="w-6 h-6 text-yellow-600" />
                </div>
                Similar Trails You Might Like
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {similarTrails.map((similar, index) => (
                  <div
                    key={similar.trail.id}
                    className="bg-white rounded-xl p-4 shadow-sm border hover:shadow-md transition-all duration-200 cursor-pointer"
                    onClick={() =>
                      handleTrailClick({
                        id: similar.trail.id,
                        name: similar.trail.name,
                        distance: similar.trail.distance,
                        elevationGain: similar.trail.elevation_gain,
                        elevationLoss: similar.trail.elevation_loss,
                        maxElevation: similar.trail.max_elevation,
                        minElevation: similar.trail.min_elevation,
                        rollingHillsIndex: similar.trail.rolling_hills_index,
                        difficultyScore: similar.trail.difficulty_score,
                        difficultyLevel: similar.trail.difficulty_level,
                        elevationProfile: similar.trail.elevation_profile,
                      })
                    }
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-bold text-gray-800">
                        {similar.trail.name}
                      </h4>
                      <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-semibold">
                        {(similar.similarity_score * 100).toFixed(0)}% match
                      </div>
                    </div>
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex justify-between">
                        <span>Distance:</span>
                        <span className="font-semibold">
                          {similar.trail.distance}km
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Elevation:</span>
                        <span className="font-semibold">
                          {similar.trail.elevation_gain}m
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Difficulty:</span>
                        <span
                          className={`font-semibold ${
                            similar.trail.difficulty_level === "Easy"
                              ? "text-green-600"
                              : similar.trail.difficulty_level === "Moderate"
                              ? "text-yellow-600"
                              : similar.trail.difficulty_level === "Hard"
                              ? "text-orange-600"
                              : "text-red-600"
                          }`}
                        >
                          {similar.trail.difficulty_level}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="bg-blue-50 rounded-xl p-4 mt-4">
                <p className="text-sm text-gray-700 font-medium">
                  💡 Recommendations based on distance, elevation gain,
                  difficulty score, and terrain characteristics similar to{" "}
                  <strong>{selectedTrail.name}</strong>
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Info/Help Page Modal */}
      {showInfoPage && <InfoPage onClose={() => setShowInfoPage(false)} />}
    </div>
  );
}
