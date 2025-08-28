import React, { useState, useMemo } from "react";
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
} from "lucide-react";

// Mock trail data for Mt. Coot-tha
const mockTrails = [
  {
    id: "mt-coot-tha",
    name: "Mt. Coot-tha Summit Track",
    location: "Brisbane, Queensland",
    distance: 4.8,
    elevationGain: 287,
    elevationLoss: 15,
    maxElevation: 287,
    minElevation: 52,
    difficulty: "Moderate",
    difficultyScore: 6.8,
    rollingHillsIndex: 0.73,
    coordinates: [
      { lat: -27.4698, lng: 152.956 },
      { lat: -27.4705, lng: 152.9565 },
      { lat: -27.4712, lng: 152.957 },
    ],
    elevationProfile: Array.from({ length: 48 }, (_, i) => ({
      distance: (i * 0.1).toFixed(1),
      elevation: Math.round(
        52 + i * 5 + Math.sin(i * 0.5) * 15 + Math.random() * 8
      ),
      rollingIndex: parseFloat(
        (0.5 + Math.sin(i * 0.3) * 0.3 + Math.random() * 0.2).toFixed(2)
      ),
    })),
  },
  {
    id: "another-trail",
    name: "Sample Trail 2",
    location: "Queensland",
    distance: 3.2,
    elevationGain: 180,
    elevationLoss: 25,
    maxElevation: 210,
    minElevation: 45,
    difficulty: "Easy",
    difficultyScore: 4.2,
    rollingHillsIndex: 0.45,
    elevationProfile: Array.from({ length: 32 }, (_, i) => ({
      distance: (i * 0.1).toFixed(1),
      elevation: Math.round(45 + i * 4 + Math.sin(i * 0.4) * 10),
      rollingIndex: parseFloat((0.3 + Math.sin(i * 0.2) * 0.2).toFixed(2)),
    })),
  },
];

// Folium Map Component - uses real Folium maps from backend
const FoliumMap = ({ selectedTrail, mapUrl, onMapLoad, onTrailClick }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Listen for messages from the Folium iframe
  React.useEffect(() => {
    const handleMessage = (event) => {
      // Accept messages from localhost
      if (event.origin !== "http://localhost:8000") {
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

  // Load demo map on component mount if no map URL provided
  React.useEffect(() => {
    if (!mapUrl && !loading) {
      loadDemoMap();
    }
  }, []);

  const loadDemoMap = async () => {
    setLoading(true);
    setError(null);
    console.log("Attempting to load demo map from backend...");

    try {
      const response = await fetch("http://localhost:8000/demo-map");
      console.log("Response status:", response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("Response data:", data);

      if (data.success) {
        console.log("Map loaded successfully:", data.map_url);
        onMapLoad(data.map_url, data.trail_stats);
      } else {
        console.error("Backend error:", data.error);
        setError(data.error || "Failed to load demo map");
      }
    } catch (err) {
      console.error("Frontend error:", err);
      setError(
        `Backend server not available: ${err.message}. Please ensure Flask server is running.`
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
          <p className="text-gray-600">Generating Folium map...</p>
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
          <Button onClick={loadDemoMap} variant="outline">
            Retry Demo Map
          </Button>
        </div>
      </div>
    );
  }

  if (!mapUrl) {
    return (
      <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No map loaded</p>
          <Button onClick={loadDemoMap} className="mt-2">
            Load Demo Map
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full rounded-lg overflow-hidden border">
      <iframe
        src={`http://localhost:8000${mapUrl}`}
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
  const [selectedTrailId, setSelectedTrailId] = useState("mt-coot-tha");
  const [isImporting, setIsImporting] = useState(false);
  const [mapUrl, setMapUrl] = useState(null);
  const [realTrailStats, setRealTrailStats] = useState(null);
  const [activeTrailData, setActiveTrailData] = useState(null);

  const selectedTrail = useMemo(() => {
    // Use active trail data if available (from Folium click), otherwise use mock data
    if (activeTrailData) {
      return {
        ...mockTrails.find((trail) => trail.id === selectedTrailId),
        distance: activeTrailData.distance,
        elevationGain: activeTrailData.elevationGain,
        elevationLoss: activeTrailData.elevationLoss,
        maxElevation: activeTrailData.maxElevation,
        minElevation: activeTrailData.minElevation,
        rollingHillsIndex: activeTrailData.rollingHillsIndex,
        elevationProfile: activeTrailData.elevationProfile,
      };
    }
    return mockTrails.find((trail) => trail.id === selectedTrailId);
  }, [selectedTrailId, activeTrailData]);

  // Handle map loading from Folium backend
  const handleMapLoad = (url, stats) => {
    setMapUrl(url);
    setRealTrailStats(stats);
  };

  // Handle trail click from Folium map
  const handleTrailClick = (trailData) => {
    console.log("Updating dashboard with trail data:", trailData);
    setActiveTrailData(trailData);
  };

  const handleGPXImport = async (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith(".gpx")) {
      setIsImporting(true);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://localhost:8000/upload-gpx", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (data.success) {
          handleMapLoad(data.map_url, data.trail_stats);
          // You could also create a new trail entry in mockTrails here
        } else {
          alert("Error processing GPX file: " + data.error);
        }
      } catch (error) {
        alert("Error uploading GPX file: " + error.message);
      } finally {
        setIsImporting(false);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Trail Analysis
              </h1>
              <p className="text-gray-600">
                Rolling Hills Detection & Trail Classification
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Select
                value={selectedTrailId}
                onValueChange={setSelectedTrailId}
              >
                <SelectTrigger className="w-64">
                  <SelectValue placeholder="Select a trail" />
                </SelectTrigger>
                <SelectContent>
                  {mockTrails.map((trail) => (
                    <SelectItem key={trail.id} value={trail.id}>
                      {trail.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* GPX Import Button */}
              <div className="relative">
                <input
                  type="file"
                  accept=".gpx"
                  onChange={handleGPXImport}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  id="gpx-upload"
                />
                <Button
                  variant="outline"
                  size="sm"
                  disabled={isImporting}
                  className="relative"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  {isImporting ? "Importing..." : "Import GPX"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 space-y-4">
        {/* Top Half - Map */}
        <Card className="h-96">
          <CardContent className="p-4 h-full">
            <FoliumMap
              selectedTrail={selectedTrail}
              mapUrl={mapUrl}
              onMapLoad={handleMapLoad}
              onTrailClick={handleTrailClick}
            />
          </CardContent>
        </Card>

        {/* Bottom Half - Trail Details */}
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
                <h3 className="font-semibold text-lg">{selectedTrail?.name}</h3>
                <p className="text-gray-600">{selectedTrail?.location}</p>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Difficulty</p>
                  <p className="font-medium">{selectedTrail?.difficulty}</p>
                </div>
                <DifficultyRing
                  score={selectedTrail?.difficultyScore}
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
                      width: `${selectedTrail?.rollingHillsIndex * 100}%`,
                    }}
                  />
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {(selectedTrail?.rollingHillsIndex * 100).toFixed(1)}% -
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
                {activeTrailData && (
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                    Live Data
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={selectedTrail?.elevationProfile}>
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
                        name === "elevation" ? "Elevation" : "Rolling Index",
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
            value={selectedTrail?.elevationGain}
            unit="m"
          />
          <StatCard
            icon={Mountain}
            label="Max Elevation"
            value={selectedTrail?.maxElevation}
            unit="m"
          />
          <StatCard
            icon={Gauge}
            label="Avg Gradient"
            value={(
              (selectedTrail?.elevationGain /
                (selectedTrail?.distance * 1000)) *
              100
            ).toFixed(1)}
            unit="%"
          />
          <StatCard
            icon={Activity}
            label="Rolling Intensity"
            value={(selectedTrail?.rollingHillsIndex * 10).toFixed(1)}
            unit="/10"
          />
          <StatCard icon={MapPin} label="Trail Type" value="Natural" unit="" />
        </div>
      </div>
    </div>
  );
}
