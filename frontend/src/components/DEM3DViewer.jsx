import React, { Suspense, useRef, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Text, Line } from "@react-three/drei";
import * as THREE from "three";

// 3D Terrain Surface Component with Topographic Colors
function TerrainSurface({ demData }) {
  const meshRef = useRef();
  const [geometry, setGeometry] = useState(null);
  const [material, setMaterial] = useState(null);

  useEffect(() => {
    if (!demData?.surface) return;

    const { surface } = demData;
    const { x, y, z } = surface;

    // Create geometry from DEM data
    const geometry = new THREE.PlaneGeometry(
      8,
      8, // Much much larger scale for very wide view
      x.length - 1,
      y.length - 1
    );

    // Calculate elevation bounds for color mapping
    const elevations = z.flat().filter((val) => val != null);
    const minElev = Math.min(...elevations);
    const maxElev = Math.max(...elevations);
    const elevRange = maxElev - minElev;

    // Update vertices with elevation data and create color array
    const vertices = geometry.attributes.position.array;
    const colors = new Float32Array(vertices.length); // RGB for each vertex

    for (let i = 0; i < y.length; i++) {
      for (let j = 0; j < x.length; j++) {
        const index = i * x.length + j;
        const vertexIndex = index * 3;

        const elevation = z[i][j] || minElev;

        // Set x, y coordinates (normalized to -4 to 4 range for much wider view)
        vertices[vertexIndex] = (j / (x.length - 1)) * 8 - 4; // x
        vertices[vertexIndex + 1] = (i / (y.length - 1)) * 8 - 4; // y
        vertices[vertexIndex + 2] = (elevation - minElev) * 0.012; // z (even more dramatic scaling)

        // Topographic color mapping based on elevation
        const normalizedElev = (elevation - minElev) / elevRange;
        const color = getTopographicColor(normalizedElev);

        colors[vertexIndex] = color.r; // R
        colors[vertexIndex + 1] = color.g; // G
        colors[vertexIndex + 2] = color.b; // B
      }
    }

    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geometry.attributes.position.needsUpdate = true;
    geometry.computeVertexNormals();

    // Create material with vertex colors
    const material = new THREE.MeshLambertMaterial({
      vertexColors: true,
      side: THREE.DoubleSide,
      wireframe: false,
    });

    setGeometry(geometry);
    setMaterial(material);
  }, [demData]);

  // Topographic color function
  function getTopographicColor(normalizedElevation) {
    // Classic topographic map colors (green to brown to white)
    if (normalizedElevation < 0.2) {
      // Deep green for valleys/low areas
      return { r: 0.2, g: 0.6, b: 0.2 };
    } else if (normalizedElevation < 0.4) {
      // Light green for foothills
      return { r: 0.4, g: 0.8, b: 0.3 };
    } else if (normalizedElevation < 0.6) {
      // Yellow-brown for mid elevations
      return { r: 0.8, g: 0.7, b: 0.3 };
    } else if (normalizedElevation < 0.8) {
      // Brown for high elevations
      return { r: 0.6, g: 0.4, b: 0.2 };
    } else {
      // Light gray/white for peaks
      return { r: 0.9, g: 0.9, b: 0.9 };
    }
  }

  if (!geometry || !material) return null;

  return (
    <mesh
      ref={meshRef}
      geometry={geometry}
      material={material}
      rotation={[-Math.PI / 2, 0, 0]}
    />
  );
}

// 3D Trail Line Component
function TrailLine({ trailData, bounds }) {
  if (!trailData || !bounds) return null;

  // Calculate elevation range for scaling
  const elevRange = bounds.z_max - bounds.z_min;

  // Normalize trail coordinates to match new terrain scale (8x8 grid)
  const normalizedPoints = trailData.map((point) => {
    const normalizedX =
      ((point.x - bounds.x_min) / (bounds.x_max - bounds.x_min)) * 8 - 4;
    const normalizedY =
      ((point.y - bounds.y_min) / (bounds.y_max - bounds.y_min)) * 8 - 4;
    const normalizedZ = (point.z - bounds.z_min) * 0.012 + 0.03; // Match terrain scaling + offset

    return [normalizedX, normalizedZ, -normalizedY]; // Note: Y and Z swapped for correct orientation
  });

  return <Line points={normalizedPoints} color="#FF0000" lineWidth={8} />;
}

// Elevation markers with topographic styling
function ElevationMarkers({ bounds }) {
  if (!bounds) return null;

  const minElev = Math.floor(bounds.z_min);
  const maxElev = Math.ceil(bounds.z_max);
  const range = maxElev - minElev;

  // Create multiple elevation markers
  const markers = [];
  const numMarkers = 5;

  for (let i = 0; i <= numMarkers; i++) {
    const elevation = minElev + (range * i) / numMarkers;
    const normalizedZ = (elevation - bounds.z_min) * 0.012;

    markers.push(
      <Text
        key={i}
        position={[4.5, normalizedZ, 0]}
        fontSize={0.12}
        color="#ffffff"
        anchorX="left"
        outlineWidth={0.02}
        outlineColor="#000000"
      >
        {Math.round(elevation)}m
      </Text>
    );
  }

  return <group>{markers}</group>;
}

// Loading component
function LoadingSpinner() {
  const meshRef = useRef();

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.z += 0.1;
    }
  });

  return (
    <mesh ref={meshRef}>
      <ringGeometry args={[0.2, 0.3, 8]} />
      <meshBasicMaterial color="#3B82F6" />
    </mesh>
  );
}

// Main 3D DEM Viewer Component
export default function DEM3DViewer({ trailId, isVisible }) {
  const [demData, setDemData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isVisible || !trailId) return;

    const fetchDEMData = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `http://localhost:8000/trail/${trailId}/dem3d`
        );
        const data = await response.json();

        if (data.success) {
          setDemData(data.dem_data);
        } else {
          setError(data.detail || "Failed to load DEM data");
        }
      } catch (err) {
        console.error("Error fetching DEM data:", err);
        setError("Failed to connect to server");
      } finally {
        setLoading(false);
      }
    };

    fetchDEMData();
  }, [trailId, isVisible]);

  if (!isVisible) return null;

  if (loading) {
    return (
      <div className="w-full h-96 bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <p className="text-gray-600">Loading 3D terrain...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-96 bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 font-medium mb-2">
            3D Terrain Unavailable
          </p>
          <p className="text-gray-600 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!demData) {
    return (
      <div className="w-full h-96 bg-gray-100 rounded-lg flex items-center justify-center">
        <p className="text-gray-600">No 3D terrain data available</p>
      </div>
    );
  }

  return (
    <div className="w-full h-96 bg-gray-900 rounded-lg overflow-hidden relative">
      <Canvas
        camera={{
          position: [6, 4, 6],
          fov: 85,
        }}
        style={{
          background:
            "linear-gradient(to bottom, #87CEEB 0%, #98D8E8 50%, #B0E0E6 100%)",
        }}
      >
        <Suspense fallback={<LoadingSpinner />}>
          {/* Enhanced lighting for topographic visualization */}
          <ambientLight intensity={0.6} />
          <directionalLight position={[10, 10, 5]} intensity={1.0} castShadow />
          <directionalLight position={[-10, 5, -5]} intensity={0.3} />
          <pointLight position={[0, 3, 0]} intensity={0.4} />

          {/* 3D Terrain */}
          <TerrainSurface demData={demData} />

          {/* Trail Line */}
          <TrailLine
            trailData={demData.trail_line}
            bounds={demData.surface.bounds}
          />

          {/* Elevation Markers */}
          <ElevationMarkers bounds={demData.surface.bounds} />

          {/* Enhanced Controls */}
          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            minDistance={2}
            maxDistance={15}
            maxPolarAngle={Math.PI * 0.8}
          />
        </Suspense>
      </Canvas>

      {/* Enhanced controls info overlay */}
      <div className="absolute bottom-4 left-4 bg-black/80 text-white text-xs p-3 rounded-lg">
        <p className="font-medium mb-1">🏔️ 3D Topographic View</p>
        <p>🖱️ Drag to rotate • 🔍 Scroll to zoom • ⌨️ Right-click to pan</p>
      </div>

      {/* Enhanced stats overlay with Mt Coot-tha info */}
      {demData.metadata && (
        <div className="absolute top-4 right-4 bg-black/80 text-white text-xs p-3 rounded-lg">
          <p className="font-medium mb-1">
            🏔️ {demData.metadata.area_name || "Mt Coot-tha Area"}
          </p>
          <p>
            Peak:{" "}
            {demData.metadata.peak_elevation ||
              Math.round(demData.surface.bounds.z_max) + "m"}
          </p>
          <p>Range: {Math.round(demData.metadata.elevation_range)}m</p>
          <p>Trail: {demData.metadata.num_trail_points} points</p>
          <p className="mt-2 text-gray-300">
            <span className="inline-block w-3 h-3 bg-green-500 rounded mr-1"></span>
            Valleys
            <span className="inline-block w-3 h-3 bg-yellow-600 rounded mr-1 ml-2"></span>
            Hills
            <span className="inline-block w-3 h-3 bg-gray-300 rounded mr-1 ml-2"></span>
            Peaks
          </p>
        </div>
      )}
    </div>
  );
}
