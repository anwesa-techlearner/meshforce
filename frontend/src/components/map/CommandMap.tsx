'use client';
import { useEffect, useRef } from 'react';
import type { Incident } from '@/types/incident';
import type { Volunteer } from '@/types/volunteer';

// Leaflet is imported dynamically at runtime only
interface Props {
  incidents: Incident[];
  volunteers: Volunteer[];
}

const PRAYAGRAJ: [number, number] = [25.4358, 81.8836];

export default function CommandMap({ incidents, volunteers }: Props) {
  const mapRef = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mapInstanceRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const layersRef = useRef<any[]>([]);

  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current) return;
    if (mapInstanceRef.current) return; // already initialized

    // Dynamic import of Leaflet
    import('leaflet').then((L) => {
      // Fix default icon paths broken by webpack
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });

      const map = L.map(mapRef.current!, {
        center: PRAYAGRAJ,
        zoom: 13,
        zoomControl: true,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map);

      mapInstanceRef.current = map;
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update markers when data changes
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    import('leaflet').then((L) => {
      const map = mapInstanceRef.current;

      // Remove old layers
      layersRef.current.forEach((l) => map.removeLayer(l));
      layersRef.current = [];

      const sevColor: Record<string, string> = {
        CRITICAL: '#dc2626', HIGH: '#f97316', MEDIUM: '#eab308', LOW: '#22c55e',
      };

      // Incident markers
      incidents.forEach((inc) => {
        const color = sevColor[inc.severity] ?? '#6b7280';
        const icon = L.divIcon({
          html: `<div style="background:${color};width:14px;height:14px;border-radius:50%;border:2px solid white;box-shadow:0 0 4px rgba(0,0,0,.5)"></div>`,
          className: '',
          iconSize: [14, 14],
          iconAnchor: [7, 7],
        });
        const m = L.marker([inc.location_lat, inc.location_lng], { icon })
          .addTo(map)
          .bindPopup(`<b>${inc.severity}</b><br>${inc.summary}<br><i>${inc.category}</i>`);
        layersRef.current.push(m);
      });

      // Volunteer markers
      const sectorCoords: Record<string, [number, number]> = {
        'SEC-01': [25.4244, 81.8846], 'SEC-02': [25.4358, 81.8836],
        'SEC-03': [25.4484, 81.8661], 'SEC-04': [25.4512, 81.8340],
        'SEC-05': [25.4125, 81.9012], 'SEC-06': [25.4390, 81.8750],
      };

      const statusColor: Record<string, string> = {
        active_idle: '#3b82f6', on_mission: '#ef4444', resting: '#eab308', offline: '#6b7280',
      };

      volunteers.forEach((vol) => {
        const coords = vol.sector_id ? sectorCoords[vol.sector_id] : null;
        if (!coords) return;
        // Jitter slightly so markers don't stack
        const jLat = coords[0] + (Math.random() - 0.5) * 0.003;
        const jLng = coords[1] + (Math.random() - 0.5) * 0.003;
        const color = statusColor[vol.status] ?? '#6b7280';
        const icon = L.divIcon({
          html: `<div style="background:${color};width:10px;height:10px;border-radius:50%;border:1px solid white;opacity:0.85"></div>`,
          className: '',
          iconSize: [10, 10],
          iconAnchor: [5, 5],
        });
        const m = L.marker([jLat, jLng], { icon })
          .addTo(map)
          .bindPopup(`<b>${vol.name}</b><br>Status: ${vol.status}<br>Sector: ${vol.sector_id}`);
        layersRef.current.push(m);
      });

      // Routing lines for dispatched incidents
      incidents
        .filter((i) => i.status === 'dispatched' && i.assigned_volunteer_ids.length > 0)
        .forEach((inc) => {
          const dispatchedVols = volunteers.filter((v) =>
            inc.assigned_volunteer_ids.includes(v.id) && v.sector_id
          );
          dispatchedVols.forEach((vol) => {
            if (!vol.sector_id) return;
            const vCoords = sectorCoords[vol.sector_id];
            if (!vCoords) return;
            const line = L.polyline(
              [vCoords, [inc.location_lat, inc.location_lng]],
              { color: '#a855f7', weight: 2, dashArray: '6 4', opacity: 0.8 }
            ).addTo(map);
            layersRef.current.push(line);
          });
        });
    });
  }, [incidents, volunteers]);

  return (
    <div className="relative w-full h-full">
      <link
        rel="stylesheet"
        href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      />
      <div ref={mapRef} className="w-full h-full" />
    </div>
  );
}
