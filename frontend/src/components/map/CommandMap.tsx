'use client';
import { useEffect, useRef } from 'react';
import { useRealtimeVolunteers } from '@/hooks/useRealtimeVolunteers';
import { useRealtimeIncidents } from '@/hooks/useRealtimeIncidents';
import type { Incident } from '@/types/incident';
import type { Volunteer } from '@/types/volunteer';

const PRAYAGRAJ: [number, number] = [25.4358, 81.8836];

const SECTOR_COORDS: Record<string, [number, number]> = {
  'SEC-01': [25.4244, 81.8846],
  'SEC-02': [25.4358, 81.8836],
  'SEC-03': [25.4484, 81.8661],
  'SEC-04': [25.4512, 81.8340],
  'SEC-05': [25.4125, 81.9012],
  'SEC-06': [25.4390, 81.8750],
};

const SECTOR_BOUNDS: Record<string, [[number, number], [number, number]]> = {
  'SEC-01': [[25.4194, 81.8796], [25.4294, 81.8896]],
  'SEC-02': [[25.4308, 81.8786], [25.4408, 81.8886]],
  'SEC-03': [[25.4434, 81.8611], [25.4534, 81.8711]],
  'SEC-04': [[25.4462, 81.8290], [25.4562, 81.8390]],
  'SEC-05': [[25.4075, 81.8962], [25.4175, 81.9062]],
  'SEC-06': [[25.4340, 81.8700], [25.4440, 81.8800]],
};

const SEV_COLOR: Record<string, string> = {
  CRITICAL: '#dc2626', HIGH: '#f97316', MEDIUM: '#eab308', LOW: '#22c55e',
};

const STATUS_COLOR: Record<string, string> = {
  active_idle: '#3b82f6', on_mission: '#ef4444', resting: '#eab308', offline: '#6b7280',
};

// Stable jitter per volunteer id
function jitter(id: string): [number, number] {
  let h = 0;
  for (let i = 0; i < id.length; i++) h = (Math.imul(31, h) + id.charCodeAt(i)) | 0;
  const lat = ((h & 0xffff) / 0xffff - 0.5) * 0.004;
  const lng = (((h >> 16) & 0xffff) / 0xffff - 0.5) * 0.004;
  return [lat, lng];
}

export default function CommandMap() {
  const volunteers = useRealtimeVolunteers();
  const incidents = useRealtimeIncidents();

  const mapRef = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mapInstanceRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const layersRef = useRef<any[]>([]);

  // Initialise map once
  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current || mapInstanceRef.current) return;
    import('leaflet').then((L) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });
      const map = L.map(mapRef.current!, { center: PRAYAGRAJ, zoom: 13 });
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors', maxZoom: 19,
      }).addTo(map);
      mapInstanceRef.current = map;
    });
    return () => {
      if (mapInstanceRef.current) { mapInstanceRef.current.remove(); mapInstanceRef.current = null; }
    };
  }, []);

  // Re-render all markers whenever data changes
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    import('leaflet').then((L) => {
      const map = mapInstanceRef.current;

      // Clear previous layers
      layersRef.current.forEach(l => map.removeLayer(l));
      layersRef.current = [];

      // --- Sector rectangles (Demand-Supply Ratio colouring) ---
      Object.entries(SECTOR_BOUNDS).forEach(([secId, bounds]) => {
        const secIncidents = incidents.filter(i => i.sector_id === secId).length;
        const secActiveVols = volunteers.filter(v => v.sector_id === secId && v.status === 'active_idle').length;
        const rs = secActiveVols === 0 ? 999 : secIncidents / secActiveVols;
        const color = rs > 1.5 ? '#dc2626' : rs >= 0.8 ? '#eab308' : '#22c55e';
        const opacity = rs > 1.5 ? 0.4 : 0.15;
        const rect = L.rectangle(bounds as [[number, number], [number, number]], {
          color, weight: 2, fillColor: color, fillOpacity: opacity,
        }).addTo(map).bindTooltip(`${secId} — Rs: ${rs === 999 ? '∞' : rs.toFixed(2)}`);
        layersRef.current.push(rect);
      });

      // --- Incident markers ---
      incidents.forEach((inc: Incident) => {
        const color = SEV_COLOR[inc.severity] ?? '#6b7280';
        const pulse = inc.severity === 'CRITICAL' ? 'animation:pulse 1s infinite' : '';
        const icon = L.divIcon({
          html: `<div style="background:${color};width:16px;height:16px;border-radius:50%;border:2px solid white;box-shadow:0 0 6px rgba(0,0,0,.6);${pulse}"></div>`,
          className: '', iconSize: [16, 16], iconAnchor: [8, 8],
        });
        const m = L.marker([inc.location_lat, inc.location_lng], { icon })
          .addTo(map)
          .bindPopup(`<b>${inc.severity}</b> — ${inc.category}<br>${inc.summary}<br><i>${inc.sector_id} · ${inc.status}</i>`);
        layersRef.current.push(m);
      });

      // --- Volunteer markers ---
      volunteers.forEach((vol: Volunteer) => {
        const base = vol.sector_id ? SECTOR_COORDS[vol.sector_id] : null;
        if (!base) return;
        const [jLat, jLng] = jitter(vol.id);
        const lat = base[0] + jLat;
        const lng = base[1] + jLng;
        const color = STATUS_COLOR[vol.status] ?? '#6b7280';
        const icon = L.divIcon({
          html: `<div style="background:${color};width:10px;height:10px;border-radius:50%;border:1px solid white;opacity:0.9"></div>`,
          className: '', iconSize: [10, 10], iconAnchor: [5, 5],
        });
        const m = L.marker([lat, lng], { icon })
          .addTo(map)
          .bindPopup(`<b>${vol.name}</b><br>${vol.status}<br>${vol.sector_id}<br>Skills: ${vol.skills?.join(', ') || '—'}`);
        layersRef.current.push(m);
      });

      // --- Routing lines (dispatched incidents → assigned volunteers) ---
      incidents
        .filter(i => i.status === 'dispatched' && i.assigned_volunteer_ids?.length > 0)
        .forEach(inc => {
          const assignedVols = volunteers.filter(v => inc.assigned_volunteer_ids.includes(v.id));
          assignedVols.forEach(vol => {
            const base = vol.sector_id ? SECTOR_COORDS[vol.sector_id] : null;
            if (!base) return;
            const [jLat, jLng] = jitter(vol.id);
            const vCoords: [number, number] = [base[0] + jLat, base[1] + jLng];
            const iCoords: [number, number] = [inc.location_lat, inc.location_lng];
            const line = L.polyline([vCoords, iCoords], {
              color: '#a855f7', weight: 2, dashArray: '8 5', opacity: 0.85,
              className: 'routing-line',
            }).addTo(map);
            layersRef.current.push(line);
          });
        });
    });
  }, [volunteers, incidents]);

  return (
    <div className="relative w-full h-full">
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <div ref={mapRef} className="w-full h-full" />
    </div>
  );
}
