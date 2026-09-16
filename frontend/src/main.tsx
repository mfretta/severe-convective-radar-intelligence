import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';
import './tracks.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
type Cell = { component_id: number; track_id?: string; area_km2: number; max_dbzh: number; grid_pixels?: [number, number][]; hazards?: Record<string, { level: string }> };
type Point = { track_id: string; timestamp_token: string; grid_x: number; grid_y: number; max_dbzh: number };

function trackPath(track: Point[]) {
  return track.map((point, index) => `${index ? 'L' : 'M'} ${(point.grid_x / 240 * 100).toFixed(2)} ${(100 - point.grid_y / 240 * 100).toFixed(2)}`).join(' ');
}
function cellColor(dbzh: number) { return dbzh >= 65 ? '#9b59ff' : dbzh >= 55 ? '#ed1c24' : dbzh >= 45 ? '#ff8c00' : '#ffe600'; }
function cellFootprintPath(pixels: [number, number][]) {
  type Vertex = [number, number]; type Edge = [Vertex, Vertex];
  const vertexKey = ([x, y]: Vertex) => `${x},${y}`;
  const edgeKey = (a: Vertex, b: Vertex) => [vertexKey(a), vertexKey(b)].sort().join('|');
  const edges = new Map<string, Edge>();
  // Remove shared pixel edges. The remaining directed edges are the measured
  // exterior perimeter of the connected 2 km CAPPI component.
  pixels.forEach(([x, y]) => {
    const top = 239 - y; const ring: Vertex[] = [[x, top], [x + 1, top], [x + 1, top + 1], [x, top + 1]];
    ring.forEach((a, index) => { const b = ring[(index + 1) % 4]; const key = edgeKey(a, b); if (edges.has(key)) edges.delete(key); else edges.set(key, [a, b]); });
  });
  const paths: string[] = [];
  while (edges.size) {
    const first = edges.values().next().value as Edge;
    const loop: Vertex[] = [first[0], first[1]]; edges.delete(edgeKey(first[0], first[1]));
    while (vertexKey(loop[loop.length - 1]) !== vertexKey(loop[0])) {
      const current = vertexKey(loop[loop.length - 1]);
      const next = [...edges.values()].find(([a]) => vertexKey(a) === current);
      if (!next) break;
      loop.push(next[1]); edges.delete(edgeKey(next[0], next[1]));
    }
    paths.push(loop.map(([x, y], index) => `${index ? 'L' : 'M'} ${(x / 240 * 100).toFixed(3)} ${(y / 240 * 100).toFixed(3)}`).join(' ') + 'Z');
  }
  return paths.join(' ');
}
function RadarMap({ time, trails, cells }: { time: string; trails: Point[][]; cells: Cell[] }) {
  return <div className="city-map" aria-label="Santa Catarina shapefile map with animated real 2 km CAPPI overlay">
    <img className="shp-basemap" src={`${API}/products/santa_catarina_shp_basemap.png`} alt="Santa Catarina municipal boundaries from supplied shapefile" />
    <img className="cappi-overlay" src={`${API}/api/cappi-image/${time}?frame=${time}`} alt={`Real 2 km DBZH CAPPI ${time}`} />
    <svg className="track-svg" viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Tracked storm cells">
      {trails.filter((track) => track.length > 1).map((track) => <path key={track[0].track_id} d={trackPath(track)} stroke={cellColor(track[track.length - 1].max_dbzh)} />)}
      {cells.filter((cell) => cell.grid_pixels?.length).map((cell) => <path className="cell-footprint" key={cell.component_id} d={cellFootprintPath(cell.grid_pixels!)} stroke={cellColor(cell.max_dbzh)} />)}
    </svg>
    <span className="radar-site" title="Chapecó radar">▲</span>
  </div>;
}
function App() {
  const [times, setTimes] = useState<string[]>([]); const [index, setIndex] = useState(0); const [cells, setCells] = useState<Cell[]>([]); const [points, setPoints] = useState<Point[]>([]); const [playing, setPlaying] = useState(false); const time = times[index];
  useEffect(() => { Promise.all([fetch(`${API}/api/scans`).then((response) => response.json()), fetch(`${API}/api/archive/track-geometry`).then((response) => response.ok ? response.json() : { points: [] })]).then(([scans, tracks]) => { setTimes(scans.timestamps); setIndex(Math.min(50, scans.timestamps.length - 1)); setPoints(tracks.points || []); }); }, []);
  useEffect(() => { if (time) fetch(`${API}/api/cells/${time}`).then((response) => response.ok ? response.json() : { cells: [] }).then((data) => setCells(data.cells || [])); }, [time]);
  useEffect(() => { if (!playing) return; const timer = window.setInterval(() => setIndex((value) => value >= times.length - 1 ? 0 : value + 1), 2500); return () => window.clearInterval(timer); }, [playing, times.length]);
  const activeTrackIds = useMemo(() => new Set(cells.map((cell) => cell.track_id).filter(Boolean) as string[]), [cells]);
  // Keep the display operational: only objects alive in this frame and their
  // latest hour of history.  Full track history remains in the API/archive.
  const trails = useMemo(() => { const grouped = new Map<string, Point[]>(); points.filter((point) => activeTrackIds.has(point.track_id) && point.timestamp_token <= time).forEach((point) => grouped.set(point.track_id, [...(grouped.get(point.track_id) || []), point])); return [...grouped.values()].map((track) => track.slice(-12)); }, [points, activeTrackIds, time]);
  const visibleTracks = trails.filter((track) => track.length > 1).length;
  const bands = [{ name: 'yellow', label: '40–45 dBZ', visible: cells.some((cell) => cell.max_dbzh >= 40 && cell.max_dbzh < 45) }, { name: 'orange', label: '45–55 dBZ', visible: cells.some((cell) => cell.max_dbzh >= 45 && cell.max_dbzh < 55) }, { name: 'red', label: '55–65 dBZ', visible: cells.some((cell) => cell.max_dbzh >= 55 && cell.max_dbzh < 65) }, { name: 'purple', label: '≥65 dBZ', visible: cells.some((cell) => cell.max_dbzh >= 65) }];
  return <main><header><div><b>SC SENTINEL</b><span>SANTA CATARINA RADAR REPLAY · 2 KM CAPPI CELL TRACKS</span></div><time>{time || 'Loading archive…'}</time></header><section className="grid"><article className="radar"><h2>REAL 2 KM CAPPI DBZH · {time}</h2>{time && <RadarMap time={time} trails={trails} cells={cells} />}<p>Base map: supplied Santa Catarina and country SHP files. Overlay: real 2 km DBZH CAPPI. Outlined footprints: detected cells; paths: selected live cells, last 60 minutes only.</p></article><aside><h2>REPLAY</h2><div className="metric"><b>{cells.length}</b><span>2 km CAPPI cells</span></div><div className="metric"><b>{visibleTracks}</b><span>live cell tracks</span></div><div className="dbzh-legend">{bands.filter((band) => band.visible).map((band) => <span key={band.name} className={band.name}>{band.label}</span>)}</div><p className="notice">Tracks are intentionally limited to cells present in this scan, preventing old tracks from obscuring the radar field.</p><button onClick={() => setPlaying(!playing)}>{playing ? 'PAUSE' : 'PLAY'}</button><button onClick={() => { setPlaying(false); setIndex(50); }}>RESET</button></aside></section><section className="cells"><h2>TRACKED CELLS · {time}</h2>{cells.map((cell) => <div className="cell" key={cell.component_id}><b>{cell.track_id || `CELL ${cell.component_id}`}</b><span>{cell.max_dbzh.toFixed(1)} dBZ · {cell.area_km2.toFixed(0)} km²</span><span>{Object.entries(cell.hazards || {}).map(([name, hazard]) => `${name}: ${hazard.level}`).join(' · ')}</span></div>)}</section><footer><input type="range" min="0" max={Math.max(0, times.length - 1)} value={index} onChange={(event) => { setPlaying(false); setIndex(+event.target.value); }} /><div className="timeline">{index + 1}/{times.length} · 2.5 s / frame</div></footer></main>;
}
createRoot(document.getElementById('root')!).render(<App />);
