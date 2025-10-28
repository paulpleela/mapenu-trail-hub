import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import API_BASE_URL from "../config/api";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { Button } from "../ui/button";
import {
  AlertCircle,
  Mountain,
  TreePine,
  Map,
  Activity,
  Eye,
  Download,
} from "lucide-react";

const TrailVisualization = ({ trailId, trailName }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const fetchAnalysisData = async (analysisType = "combined") => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/trail/${trailId}/${analysisType}-analysis`
      );
      const data = await response.json();

      if (data.success) {
        setAnalysisData(data);
      } else {
        setError(data.message || "Analysis failed");
      }
    } catch (err) {
      setError(`Failed to load ${analysisType} analysis: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (trailId) {
      fetchAnalysisData();
    }
  }, [trailId]);

  const AnalysisOverview = () => {
    if (!analysisData) return null;

    const { dem_analysis, lidar_analysis, analysis_summary } = analysisData;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Mountain className="w-4 h-4" />
              DEM Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-2xl font-bold text-green-600">
                {analysis_summary.dem_available
                  ? "✓ Available"
                  : "✗ Not Available"}
              </div>
              {dem_analysis && (
                <div className="text-sm text-gray-600 space-y-1">
                  <p>
                    Elevation Range:{" "}
                    {dem_analysis.statistics?.elevation_range?.[0]?.toFixed(1)}m
                    -{" "}
                    {dem_analysis.statistics?.elevation_range?.[1]?.toFixed(1)}m
                  </p>
                  <p>
                    Data Points: {dem_analysis.total_points?.toLocaleString()}
                  </p>
                  <p>Sources: {dem_analysis.data_sources?.length} DEM tiles</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <TreePine className="w-4 h-4" />
              LiDAR Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-2xl font-bold text-blue-600">
                {analysis_summary.lidar_available
                  ? "✓ Available"
                  : "✗ Not Available"}
              </div>
              {lidar_analysis && (
                <div className="text-sm text-gray-600 space-y-1">
                  <p>
                    Point Cloud:{" "}
                    {lidar_analysis.total_lidar_points?.toLocaleString()} points
                  </p>
                  <p>
                    Vegetation:{" "}
                    {lidar_analysis.statistics?.vegetation_percentage?.toFixed(
                      1
                    )}
                    %
                  </p>
                  <p>Corridor: {lidar_analysis.corridor_width_meters}m width</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Data Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-2xl font-bold text-purple-600">
                {analysis_summary.total_data_sources}
              </div>
              <p className="text-sm text-gray-600">Total Data Sources</p>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span>DEM Coverage:</span>
                  <span className="font-medium">
                    {analysis_summary.dem_available ? "Yes" : "No"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>LiDAR Coverage:</span>
                  <span className="font-medium">
                    {analysis_summary.lidar_available ? "Yes" : "No"}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const DEMAnalysisTab = () => {
    if (!analysisData?.dem_analysis) {
      return (
        <div className="text-center py-8">
          <AlertCircle className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900">
            No DEM Data Available
          </h3>
          <p className="text-gray-600">
            DEM elevation data is not available for this trail location.
          </p>
        </div>
      );
    }

    const { statistics, elevation_profile, visualization, data_sources } =
      analysisData.dem_analysis;

    return (
      <div className="space-y-6">
        {/* Elevation Profile Visualization */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mountain className="w-5 h-5" />
              Elevation Profile Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <img
                src={visualization}
                alt="DEM Elevation Analysis"
                className="w-full rounded-lg border"
                style={{ maxHeight: "600px", objectFit: "contain" }}
              />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div className="text-center p-3 bg-blue-50 rounded">
                <div className="text-2xl font-bold text-blue-600">
                  {statistics?.min_elevation?.toFixed(1)}m
                </div>
                <div className="text-sm text-blue-800">Min Elevation</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded">
                <div className="text-2xl font-bold text-green-600">
                  {statistics?.max_elevation?.toFixed(1)}m
                </div>
                <div className="text-sm text-green-800">Max Elevation</div>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded">
                <div className="text-2xl font-bold text-orange-600">
                  {statistics?.elevation_gain?.toFixed(1)}m
                </div>
                <div className="text-sm text-orange-800">Elevation Gain</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded">
                <div className="text-2xl font-bold text-purple-600">
                  {statistics?.total_distance?.toFixed(2)}km
                </div>
                <div className="text-sm text-purple-800">Total Distance</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Data Sources */}
        <Card>
          <CardHeader>
            <CardTitle>Data Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                Analysis based on {data_sources?.length} DEM tiles:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {data_sources?.map((source, index) => (
                  <div
                    key={index}
                    className="text-xs bg-gray-100 p-2 rounded font-mono"
                  >
                    {source}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const LiDARAnalysisTab = () => {
    if (!analysisData?.lidar_analysis) {
      return (
        <div className="text-center py-8">
          <AlertCircle className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900">
            No LiDAR Data Available
          </h3>
          <p className="text-gray-600">
            LiDAR point cloud data is not available for this trail location.
          </p>
        </div>
      );
    }

    const { vegetation_analysis, visualization, data_sources, statistics } =
      analysisData.lidar_analysis;

    return (
      <div className="space-y-6">
        {/* Point Cloud Visualization */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TreePine className="w-5 h-5" />
              LiDAR Point Cloud Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <img
                src={visualization}
                alt="LiDAR Point Cloud Analysis"
                className="w-full rounded-lg border"
                style={{ maxHeight: "600px", objectFit: "contain" }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Vegetation Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Vegetation Classification</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-brown-50 rounded">
                <div className="text-2xl font-bold text-brown-600">
                  {(
                    (vegetation_analysis?.ground_points /
                      vegetation_analysis?.total_points) *
                    100
                  )?.toFixed(1)}
                  %
                </div>
                <div className="text-sm text-brown-800">Ground</div>
                <div className="text-xs text-gray-600">
                  {vegetation_analysis?.ground_points?.toLocaleString()} pts
                </div>
              </div>
              <div className="text-center p-3 bg-green-100 rounded">
                <div className="text-2xl font-bold text-green-600">
                  {(
                    (vegetation_analysis?.low_vegetation /
                      vegetation_analysis?.total_points) *
                    100
                  )?.toFixed(1)}
                  %
                </div>
                <div className="text-sm text-green-800">Low Vegetation</div>
                <div className="text-xs text-gray-600">
                  {vegetation_analysis?.low_vegetation?.toLocaleString()} pts
                </div>
              </div>
              <div className="text-center p-3 bg-green-200 rounded">
                <div className="text-2xl font-bold text-green-700">
                  {(
                    (vegetation_analysis?.medium_vegetation /
                      vegetation_analysis?.total_points) *
                    100
                  )?.toFixed(1)}
                  %
                </div>
                <div className="text-sm text-green-900">Medium Vegetation</div>
                <div className="text-xs text-gray-600">
                  {vegetation_analysis?.medium_vegetation?.toLocaleString()} pts
                </div>
              </div>
              <div className="text-center p-3 bg-green-300 rounded">
                <div className="text-2xl font-bold text-green-800">
                  {(
                    (vegetation_analysis?.high_vegetation /
                      vegetation_analysis?.total_points) *
                    100
                  )?.toFixed(1)}
                  %
                </div>
                <div className="text-sm text-green-900">High Vegetation</div>
                <div className="text-xs text-gray-600">
                  {vegetation_analysis?.high_vegetation?.toLocaleString()} pts
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Data Sources */}
        <Card>
          <CardHeader>
            <CardTitle>LiDAR Data Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                Analysis based on {data_sources?.length} point cloud files:
              </p>
              <div className="grid grid-cols-1 gap-2">
                {data_sources?.map((source, index) => (
                  <div
                    key={index}
                    className="text-xs bg-gray-100 p-2 rounded font-mono"
                  >
                    {source}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 mx-auto text-red-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900">Analysis Error</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <Button onClick={() => fetchAnalysisData()} variant="outline">
          Retry Analysis
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">
          Enhanced Trail Visualization: {trailName}
        </h2>
        <div className="flex gap-2">
          <Button
            onClick={() => fetchAnalysisData("dem")}
            variant="outline"
            size="sm"
            disabled={loading}
          >
            <Mountain className="w-4 h-4 mr-2" />
            DEM Only
          </Button>
          <Button
            onClick={() => fetchAnalysisData("lidar")}
            variant="outline"
            size="sm"
            disabled={loading}
          >
            <TreePine className="w-4 h-4 mr-2" />
            LiDAR Only
          </Button>
          <Button
            onClick={() => fetchAnalysisData("combined")}
            variant="outline"
            size="sm"
            disabled={loading}
          >
            <Eye className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {analysisData && <AnalysisOverview />}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="dem">DEM Analysis</TabsTrigger>
          <TabsTrigger value="lidar">LiDAR Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <Card>
            <CardHeader>
              <CardTitle>Analysis Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-gray-600">
                  This comprehensive analysis combines Digital Elevation Model
                  (DEM) data and Light Detection and Ranging (LiDAR) point cloud
                  data to provide detailed insights about the trail terrain,
                  vegetation, and surrounding environment.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <Mountain className="w-4 h-4" />
                      DEM Analysis Features
                    </h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Detailed elevation profiles along the trail</li>
                      <li>• Gradient analysis and slope calculations</li>
                      <li>• 3D terrain visualization</li>
                      <li>• 1-meter resolution elevation data</li>
                    </ul>
                  </div>

                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <TreePine className="w-4 h-4" />
                      LiDAR Analysis Features
                    </h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Vegetation classification and density</li>
                      <li>• Ground surface detection</li>
                      <li>• Trail corridor analysis (30m width)</li>
                      <li>• Point cloud intensity analysis</li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dem">
          <DEMAnalysisTab />
        </TabsContent>

        <TabsContent value="lidar">
          <LiDARAnalysisTab />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TrailVisualization;
