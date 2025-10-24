import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';

const ElevationChart = ({ elevationSources }) => {
  // Transform the data for Recharts format
  const chartData = useMemo(() => {
    if (!elevationSources) return [];
    
    // Get all available sources
    const availableSources = Object.entries(elevationSources)
      .filter(([key, source]) => source.available && source.elevations?.length > 0);
    
    if (availableSources.length === 0) return [];
    
    // Create a unified array of all distance points from all sources
    const allDistances = new Set();
    availableSources.forEach(([name, source]) => {
      if (source.distances && source.distances.length > 0) {
        source.distances.forEach(d => allDistances.add(d));
      }
    });
    
    // Convert to sorted array
    const sortedDistances = Array.from(allDistances).sort((a, b) => a - b);
    
    // Create data points for each distance
    const data = sortedDistances.map(distance => {
      const point = { distance };
      
      // For each source, find the closest elevation value for this distance
      availableSources.forEach(([sourceName, source]) => {
        if (source.distances && source.elevations) {
          // Find the closest distance in this source's data
          let closestIndex = 0;
          let minDiff = Math.abs(source.distances[0] - distance);
          
          for (let i = 1; i < source.distances.length; i++) {
            const diff = Math.abs(source.distances[i] - distance);
            if (diff < minDiff) {
              minDiff = diff;
              closestIndex = i;
            }
          }
          
          // Only include if the distance is close enough (within 0.01 km = 10m)
          if (minDiff < 0.01) {
            point[`${sourceName}_elevation`] = source.elevations[closestIndex];
          }
        }
      });
      
      return point;
    });
    
    return data;
  }, [elevationSources]);
  
  // Get available sources for legend
  const availableSources = useMemo(() => {
    if (!elevationSources) return [];
    return Object.entries(elevationSources)
      .filter(([key, source]) => source.available && source.elevations?.length > 0)
      .map(([key, source]) => ({
        name: key,
        color: getSourceColor(key),
        dataPoints: source.elevations?.length || 0,
      }));
  }, [elevationSources]);
  
  function getSourceColor(sourceName) {
    const colors = {
      GPX: '#2563eb',      // Blue
      LiDAR: '#16a34a',    // Green  
      XLSX: '#dc2626',     // Red
      DEM: '#7c3aed',      // Purple
      QSpatial: '#ea580c', // Orange
    };
    return colors[sourceName] || '#6b7280'; // Gray fallback
  }
  
  if (chartData.length === 0) {
    return (
      <div className="w-full h-[400px] flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">📈</div>
          <div className="text-gray-600 font-medium">No elevation data available</div>
          <div className="text-sm text-gray-500">Upload a GPX file, LiDAR data, or XLSX file to see elevation profiles</div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="w-full space-y-4">
      {/* Legend */}
      {availableSources.length > 0 && (
        <div className="flex flex-wrap gap-4 justify-center">
          {availableSources.map((source) => (
            <div key={source.name} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: source.color }}
              />
              <span className="text-sm font-medium">{source.name}</span>
              <span className="text-xs text-gray-500">({source.dataPoints} points)</span>
            </div>
          ))}
        </div>
      )}
      
      {/* Chart */}
      <div className="w-full h-[500px] bg-white rounded-lg border shadow-sm">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart 
            data={chartData} 
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="distance"
              type="number"
              domain={['dataMin', 'dataMax']}
              tickCount={8}
              label={{ 
                value: 'Distance (km)', 
                position: 'insideBottom', 
                offset: -10,
                style: { textAnchor: 'middle' }
              }}
              tickFormatter={(value) => value.toFixed(2)}
            />
            <YAxis
              tickCount={8}
              label={{ 
                value: 'Elevation (m)', 
                angle: -90, 
                position: 'insideLeft',
                style: { textAnchor: 'middle' }
              }}
              tickFormatter={(value) => Math.round(value)}
            />
            <ReferenceLine y={0} stroke="#e2e8f0" strokeDasharray="2 2" />
            <Tooltip 
              formatter={(value, name) => [
                `${Math.round(value)}m`, 
                name.replace('_elevation', '').toUpperCase()
              ]}
              labelFormatter={(value) => `Distance: ${value.toFixed(3)} km`}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
              }}
            />
            {availableSources.map((source) => (
              <Line
                key={source.name}
                type="monotone"
                dataKey={`${source.name}_elevation`}
                stroke={source.color}
                strokeWidth={2}
                dot={false}
                connectNulls={false}
                name={source.name}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Data Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        {availableSources.map((source) => {
          const sourceData = elevationSources[source.name];
          const elevations = sourceData.elevations || [];
          const minElev = elevations.length > 0 ? Math.min(...elevations) : 0;
          const maxElev = elevations.length > 0 ? Math.max(...elevations) : 0;
          const elevGain = maxElev - minElev;
          
          return (
            <div key={source.name} className="bg-gray-50 rounded-lg p-3 border">
              <div className="flex items-center gap-2 mb-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: source.color }}
                />
                <span className="font-medium">{source.name}</span>
              </div>
              <div className="space-y-1 text-xs text-gray-600">
                <div>Min: {minElev.toFixed(1)}m</div>
                <div>Max: {maxElev.toFixed(1)}m</div>
                <div>Gain: {elevGain.toFixed(1)}m</div>
                <div>Points: {source.dataPoints}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ElevationChart;