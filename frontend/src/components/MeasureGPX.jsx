
/*
Phone GPS distance-based GPX tracker

Features:
- Uses browser Geolocation API (navigator.geolocation.watchPosition)
- Records points when device moves >= distanceThreshold (meters)
- Stores latitude, longitude, altitude, timestamp, accuracy
- Exports GPX 1.1 file for download
- Shows live stats (current coords, altitude, accuracy, speed estimates, points count)

Important notes for iPhone/iOS Safari:
- Must be served over HTTPS (localhost with dev certs or via ngrok for testing)
- iOS may throttle background geolocation in the browser and may pause updates when the screen is off

How to use:
- Open the page in Safari on iPhone, grant location permission, press Start and begin moving

*/

import React, { useEffect, useRef, useState } from "react";

// AltitudeChart component: SVG line chart for altitude
function AltitudeChart({ points }) {
  const altPoints = points.filter(p => p.altitude !== null && p.altitude !== undefined);
  if (altPoints.length < 2) {
    return <div style={{ color: '#888', fontSize: 13, marginTop: 6 }}>Not enough altitude data to plot.</div>;
  }

  // Chart dimensions
  const width = 320, height = 100, pad = 24;
  const altitudes = altPoints.map(p => p.altitude);
  const minAlt = Math.min(...altitudes), maxAlt = Math.max(...altitudes);
  const range = maxAlt - minAlt || 1;

  const stepX = (width - pad * 2) / (altPoints.length - 1);
  const pointsStr = altPoints.map((p, i) => {
    const x = pad + i * stepX;
    const y = pad + (height - pad * 2) * (1 - (p.altitude - minAlt) / range);
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} style={{ background: '#f8f8f8', borderRadius: 6, marginTop: 8, width: '100%', maxWidth: 320 }}>
      <polyline points={pointsStr} fill="none" stroke="#3498db" strokeWidth={2} />
      <text x={4} y={height - 6} fontSize={12} fill="#555">{minAlt.toFixed(1)} m</text>
      <text x={width - pad} y={pad + 12} fontSize={12} fill="#555" textAnchor="end">{maxAlt.toFixed(1)} m</text>
    </svg>
  );
}

function haversineMeters(lat1, lon1, lat2, lon2) {
  const toRad = (x) => (x * Math.PI) / 180;
  const R = 6371000; // metres
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function formatISO(ts) {
  return new Date(ts).toISOString();
}

function buildGpx(trackName, points) {
  const header = `<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="iPhone-GPS-Tracker" xmlns="http://www.topografix.com/GPX/1/1">\n  <metadata>\n    <name>${trackName}</name>\n    <time>${formatISO(points.length ? points[0].timestamp : Date.now())}</time>\n  </metadata>\n  <trk>\n    <name>${trackName}</name>\n    <trkseg>`;
  const footer = `\n    </trkseg>\n  </trk>\n</gpx>`;

  const segPoints = points.map(p => {
    const ele = (p.altitude !== null && p.altitude !== undefined) ? `<ele>${p.altitude}</ele>` : "";
    const time = p.timestamp ? `<time>${formatISO(p.timestamp)}</time>` : "";
    return `\n      <trkpt lat="${p.latitude}" lon="${p.longitude}">${ele}${time}\n      </trkpt>`;
  }).join('');

  return header + segPoints + footer;
}

export default function App() {
  const [watching, setWatching] = useState(false);
  const [points, setPoints] = useState([]);
  const [distanceThreshold, setDistanceThreshold] = useState(1); // meters
  const [lastPoint, setLastPoint] = useState(null);
  const watchIdRef = useRef(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const [trackName, setTrackName] = useState('My Track');

  useEffect(() => {
    return () => stopTracking();
  }, []);

  function onPosition(pos) {
    setError(null);
    const { latitude, longitude, altitude, accuracy, speed } = pos.coords;
    const timestamp = pos.timestamp || Date.now();
    const p = { latitude, longitude, altitude: altitude ?? null, accuracy, speed: speed ?? null, timestamp };

    // if no last point, always accept
    if (!lastPoint) {
      setPoints(prev => [...prev, p]);
      setLastPoint(p);
      return;
    }

    // compute distance
    const d = haversineMeters(lastPoint.latitude, lastPoint.longitude, latitude, longitude);
    
    // More strict filtering to avoid stationary noise:
    // 1. Must move at least the threshold distance
    // 2. If accuracy is poor (>20m), require larger movement
    // 3. Use speed as additional filter if available
    const minDistance = accuracy > 20 ? Math.max(distanceThreshold * 2, 5) : distanceThreshold;
    const hasSpeed = speed !== null && speed !== undefined;
    const isMoving = hasSpeed ? speed > 0.5 : true; // 0.5 m/s = walking pace
    
    if (d >= minDistance && isMoving) {
      setPoints(prev => [...prev, p]);
      setLastPoint(p);
    }
  }

  function onError(err) {
    console.error('Geolocation error', err);
    setError(err.message || String(err));
    setStatus('error');
  }

  function startTracking() {
    if (!("geolocation" in navigator)) {
      alert("Geolocation is not available in this browser.");
      return;
    }

    // Ask once immediately to trigger the permission popup
    navigator.geolocation.getCurrentPosition(
      () => {
        // If granted, now start continuous tracking
        const opts = { enableHighAccuracy: true, maximumAge: 0, timeout: 10000 };
        watchIdRef.current = navigator.geolocation.watchPosition(onPosition, console.error, opts);
        setWatching(true);
      },
      (err) => {
        alert("Error getting location: " + err.message);
      },
      { enableHighAccuracy: true }
    );
  }

  function stopTracking() {
    if (watchIdRef.current !== null && navigator.geolocation) {
      navigator.geolocation.clearWatch(watchIdRef.current);
    }
    watchIdRef.current = null;
    setWatching(false);
    setStatus('stopped');
  }

  function reset() {
    setPoints([]);
    setLastPoint(null);
    setStatus('idle');
    setError(null);
  }

  function downloadGpx() {
    const gpx = buildGpx(trackName, points);
    const blob = new Blob([gpx], { type: 'application/gpx+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const safeName = trackName.replace(/[^a-z0-9_-]/gi, '_').toLowerCase();
    a.download = `${safeName || 'track'}.gpx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  const last = points.length ? points[points.length - 1] : null;

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', maxWidth: 600, margin: '32px auto', padding: 24, background: '#fafbfc', borderRadius: 12, boxShadow: '0 2px 12px #0001' }}>
      <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 8, color: '#2a2a2a' }}>Trail Hub's GPX Tracker</h1>
      <p style={{ marginTop: 0, color: '#444', fontSize: 15 }}>Records GPS points when you move a specified distance. Built to run on your mobile's web browser.</p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 18, marginTop: 18 }}>
        <div style={{ background: '#fff', padding: 18, borderRadius: 8, boxShadow: '0 1px 4px #0001' }}>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontWeight: 500 }}>Track name: <input value={trackName} onChange={e => setTrackName(e.target.value)} style={{ marginLeft: 8, padding: '4px 8px', borderRadius: 4, border: '1px solid #ccc', background: '#fff', color: '#222' }} /></label>
          </div>

          <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
            <button onClick={() => watching ? stopTracking() : startTracking()} style={{ padding: '8px 16px', borderRadius: 6, background: watching ? '#e74c3c' : '#2ecc40', color: '#fff', border: 'none', fontWeight: 600 }}>{watching ? 'Stop' : 'Start'}</button>
            <button onClick={reset} style={{ padding: '8px 16px', borderRadius: 6, background: '#f1c40f', color: '#fff', border: 'none', fontWeight: 600 }}>Reset</button>
            <button onClick={downloadGpx} style={{ padding: '8px 16px', borderRadius: 6, background: '#3498db', color: '#fff', border: 'none', fontWeight: 600 }} disabled={!points.length}>Download GPX</button>
          </div>

          <div style={{ display: 'flex', gap: 16, alignItems: 'center', marginBottom: 12 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <label style={{ fontWeight: 500, color: '#333' }}>Distance threshold: {distanceThreshold}m</label>
              <input 
                type="range" 
                min="0.5" 
                max="10" 
                step="0.5" 
                value={distanceThreshold} 
                onChange={e => setDistanceThreshold(Number(e.target.value))} 
                style={{ 
                  width: 200, 
                  accentColor: '#3498db',
                  background: '#f0f0f0'
                }} 
              />
              <div style={{ fontSize: 11, color: '#666', display: 'flex', justifyContent: 'space-between', width: 200 }}>
                <span>0.5m</span>
                <span>10m</span>
              </div>
            </div>
            <span style={{ fontSize: 13, color: '#666' }}>To get continuous, fine-grained updates, use lower values but battery use and noise will increase.</span>
          </div>

          <div style={{ background: '#fff', color: '#222', padding: 14, borderRadius: 8, border: '1px solid #eee', boxShadow: '0 1px 4px #0001', marginBottom: 18 }}>
            <strong>Status:</strong> {status} {error ? ` — error: ${error}` : ''}
            <div style={{ marginTop: 8, fontSize: 15, lineHeight: 1.7 }}>
              <div><strong>Points:</strong> {points.length}</div>
              <div><strong>Last latitude:</strong> {last ? last.latitude.toFixed(6) : '-'}</div>
              <div><strong>Last longitude:</strong> {last ? last.longitude.toFixed(6) : '-'}</div>
              <div><strong>Altitude (m):</strong> {last && last.altitude !== null ? last.altitude.toFixed(2) : 'n/a'}</div>
              <div><strong>Accuracy (m):</strong> {last ? last.accuracy : '-'}</div>
              <div><strong>Last timestamp:</strong> {last ? new Date(last.timestamp).toLocaleString() : '-'}</div>
            </div>
            {/* Altitude Chart */}
            <div style={{ marginTop: 18 }}>
              <strong>Altitude visualisation</strong>
              <AltitudeChart points={points} />
            </div>
          </div>
        </div>

        <div style={{ background: '#fff', padding: 18, borderRadius: 8, boxShadow: '0 1px 4px #0001' }}>
          <h3 style={{ marginTop: 0, fontSize: 18, fontWeight: 600 }}>Live preview</h3>
          <div style={{ fontSize: 13, lineHeight: 1.5 }}>
            <div><strong>Most recent point</strong></div>
            <pre style={{ whiteSpace: 'pre-wrap', background: '#f8f8f8', padding: 8, borderRadius: 4, maxHeight: 200, overflow: 'auto', fontSize: 12 }}>{last ? JSON.stringify(last, null, 2) : 'No points yet'}</pre>
          </div>

          <div style={{ marginTop: 8 }}>
            <h4 style={{ fontSize: 15, fontWeight: 500 }}>Track export</h4>
            <textarea readOnly value={buildGpx(trackName, points)} style={{ width: '100%', height: 120, fontSize: 12, background: '#fff', color: '#222', borderRadius: 4, border: '1px solid #eee' }} />
          </div>
        </div>
      </div>

      <footer style={{ marginTop: 24, fontSize: 12, color: '#555' }}>
        <div>Notes:</div>
        <ul>
          <li>On iPhone, you may need to allow the page to use location in Settings → Safari → Location.</li>
          <li>Tracking may be paused when the screen is off.</li>
        </ul>
      </footer>
    </div>
  );
}