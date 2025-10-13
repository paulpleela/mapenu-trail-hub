import React from "react";

// Visual Preview Component - Shows what the Info Page looks like
export default function InfoPagePreview() {
  return (
    <div className="p-8 bg-gray-100">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header Preview */}
        <div className="bg-white rounded-lg shadow-lg p-4">
          <h2 className="text-xl font-bold mb-4">Dashboard Header Preview</h2>
          <div className="flex items-center justify-between border-2 border-blue-300 rounded-lg p-4">
            <div>
              <h1 className="text-2xl font-bold">MAPENU</h1>
              <p className="text-sm text-gray-600">12 trails available</p>
            </div>
            <div className="flex gap-2">
              <button className="px-4 py-2 border rounded-lg hover:bg-gray-50">
                📤 Upload GPX
              </button>
              <button className="px-4 py-2 border rounded-lg hover:bg-gray-50">
                🔄 Refresh
              </button>
              <button className="px-4 py-2 border rounded-lg hover:bg-gray-50">
                📊 Analytics
              </button>
              <button className="px-4 py-2 bg-blue-50 border-2 border-blue-500 rounded-lg hover:bg-blue-100 text-blue-700 font-semibold shadow-md">
                ℹ️ Help & Guide ← NEW!
              </button>
            </div>
          </div>
        </div>

        {/* Info Page Content Preview */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
            <h2 className="text-3xl font-bold">📚 MAPENU Guide</h2>
            <p className="text-blue-100">Data Collection Methods & Platform Overview</p>
          </div>

          <div className="p-6 space-y-4">
            {/* Section Preview */}
            <div className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded">
              <h3 className="font-bold text-lg mb-2">📍 Method 1: GPX Files</h3>
              <p className="text-sm text-gray-700">
                GPS Exchange Format for recording trail coordinates with apps like GPS Tracks and My Tracks
              </p>
              <div className="mt-3 bg-green-50 border border-green-300 rounded p-3">
                <p className="text-sm font-semibold text-green-800">✓ Best Practices:</p>
                <ul className="text-xs text-gray-700 mt-1 space-y-1">
                  <li>✓ Enable high-accuracy GPS mode</li>
                  <li>✓ Record at 1-5 second intervals</li>
                  <li>✓ Keep phone accessible</li>
                </ul>
              </div>
            </div>

            <div className="border-l-4 border-purple-500 bg-purple-50 p-4 rounded">
              <h3 className="font-bold text-lg mb-2">📦 Method 2: LiDAR Files</h3>
              <p className="text-sm text-gray-700">
                3D point cloud scanning with iPhone/iPad Pro using dot3D, Polycam, or Scaniverse
              </p>
            </div>

            <div className="border-l-4 border-emerald-500 bg-emerald-50 p-4 rounded">
              <h3 className="font-bold text-lg mb-2">🗺️ Method 3: QSpatial Data</h3>
              <p className="text-sm text-gray-700">
                Free 1-meter resolution LiDAR data from Queensland Government portal
              </p>
            </div>

            {/* What We Analyze Section */}
            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="border-2 border-blue-300 rounded-lg p-4 bg-gradient-to-br from-blue-50 to-cyan-50">
                <h4 className="font-bold text-blue-700 mb-2">📊 2D Elevation Profile</h4>
                <div className="bg-white rounded h-24 flex items-center justify-center">
                  <div className="text-xs text-gray-500">[Chart Preview]</div>
                </div>
                <p className="text-xs text-gray-600 mt-2">
                  Shows elevation changes, slopes, and gradients
                </p>
              </div>

              <div className="border-2 border-purple-300 rounded-lg p-4 bg-gradient-to-br from-purple-50 to-pink-50">
                <h4 className="font-bold text-purple-700 mb-2">🏔️ 3D Terrain View</h4>
                <div className="bg-white rounded h-24 flex items-center justify-center">
                  <div className="text-xs text-gray-500">[3D Preview]</div>
                </div>
                <p className="text-xs text-gray-600 mt-2">
                  Interactive 3D terrain with trail overlay
                </p>
              </div>

              <div className="border-2 border-emerald-300 rounded-lg p-4 bg-gradient-to-br from-emerald-50 to-teal-50">
                <h4 className="font-bold text-emerald-700 mb-2">📈 Rolling Hills Index</h4>
                <div className="bg-emerald-100 rounded p-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span>0.65</span>
                    <span className="font-bold text-emerald-600">MODERATE</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div className="bg-emerald-500 h-2 rounded-full w-[65%]"></div>
                  </div>
                </div>
                <p className="text-xs text-gray-600 mt-2">
                  Measures trail bumpiness: frequency + amplitude
                </p>
              </div>

              <div className="border-2 border-orange-300 rounded-lg p-4 bg-gradient-to-br from-orange-50 to-red-50">
                <h4 className="font-bold text-orange-700 mb-2">⏱️ Difficulty & Time</h4>
                <div className="bg-orange-100 rounded p-3 grid grid-cols-2 gap-2 text-center">
                  <div>
                    <p className="text-2xl font-bold text-orange-600">6.5</p>
                    <p className="text-xs text-gray-600">Score /10</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-red-600">3.2h</p>
                    <p className="text-xs text-gray-600">Est. Time</p>
                  </div>
                </div>
                <p className="text-xs text-gray-600 mt-2">
                  Based on Naismith's Rule + terrain
                </p>
              </div>
            </div>

            {/* Quick Start */}
            <div className="bg-gradient-to-r from-indigo-100 to-purple-100 rounded-lg p-4 mt-6">
              <h3 className="font-bold text-lg mb-3">🚀 Quick Start Guide</h3>
              <div className="space-y-2">
                <div className="flex gap-3 items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</span>
                  <div>
                    <p className="font-semibold text-sm">Record Your Trail</p>
                    <p className="text-xs text-gray-600">Use GPS app to record as GPX</p>
                  </div>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</span>
                  <div>
                    <p className="font-semibold text-sm">Upload to MAPENU</p>
                    <p className="text-xs text-gray-600">Click Upload GPX button</p>
                  </div>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</span>
                  <div>
                    <p className="font-semibold text-sm">View Analysis</p>
                    <p className="text-xs text-gray-600">Explore metrics and visualizations</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">✨ Key Features of Info Page</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl">📱</span>
              <div>
                <h3 className="font-semibold">App Recommendations</h3>
                <p className="text-sm text-gray-600">Lists specific apps for iOS and Android</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-2xl">✅</span>
              <div>
                <h3 className="font-semibold">Best Practices</h3>
                <p className="text-sm text-gray-600">Step-by-step collection guidelines</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-2xl">🎨</span>
              <div>
                <h3 className="font-semibold">Visual Examples</h3>
                <p className="text-sm text-gray-600">Shows what each metric looks like</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-2xl">🚀</span>
              <div>
                <h3 className="font-semibold">Quick Start</h3>
                <p className="text-sm text-gray-600">Get started in 3 easy steps</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
