import { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import { ArrowUpRight, MapPin } from 'lucide-react';

// Recenter component to update view when center or zoom changes
function ChangeView({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center && Array.isArray(center) && center.length === 2 && !isNaN(center[0]) && !isNaN(center[1])) {
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);
  return null;
}

export default function ProjectsMap({
  projects = [],
  center = [19.7515, 75.7139], // Default Maharashtra state center
  zoom = 7,
}) {
  const navigate = useNavigate();

  // Color helper based on risk level or status
  const getMarkerOptions = (status, riskLevel) => {
    const risk = (riskLevel || '').toUpperCase();
    const stat = (status || '').toLowerCase();

    if (risk === 'CRITICAL' || risk === 'HIGH' || stat === 'high risk' || stat === 'delayed') {
      return { color: '#EF4444', fillColor: '#F87171', radius: 10 };
    }
    if (risk === 'MEDIUM' || stat === 'review required' || stat === 'under review') {
      return { color: '#F59E0B', fillColor: '#FBBF24', radius: 9 };
    }
    if (risk === 'LOW' || stat === 'verified' || stat === 'completed') {
      return { color: '#10B981', fillColor: '#34D399', radius: 8 };
    }
    return { color: '#1769D2', fillColor: '#60A5FA', radius: 8 };
  };

  // Filter projects with valid latitude and longitude
  const validProjects = projects.filter((proj) => {
    const lat = proj.latitude ?? proj.lat;
    const lng = proj.longitude ?? proj.lng;
    return (
      lat !== null &&
      lat !== undefined &&
      lng !== null &&
      lng !== undefined &&
      !isNaN(Number(lat)) &&
      !isNaN(Number(lng)) &&
      (Number(lat) !== 0 || Number(lng) !== 0)
    );
  });

  return (
    <div className="w-full h-full relative" style={{ minHeight: '500px' }}>
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={true}
        className="w-full h-full rounded-2xl shadow-xs border border-gray-200 z-0"
      >
        <ChangeView center={center} zoom={zoom} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {validProjects.map((proj) => {
          const lat = Number(proj.latitude ?? proj.lat);
          const lng = Number(proj.longitude ?? proj.lng);
          const pCode = proj.project_code || `ID-${proj.id}`;
          const phys = proj.physical_progress ?? proj.reported_progress ?? 0;
          const fin = proj.financial_progress ?? 0;
          const opt = getMarkerOptions(proj.status, proj.risk_level);

          return (
            <CircleMarker
              key={proj.id || pCode}
              center={[lat, lng]}
              radius={opt.radius}
              weight={2}
              color={opt.color}
              fillColor={opt.fillColor}
              fillOpacity={0.85}
            >
              <Popup className="setux-map-popup">
                <div className="p-1 font-sans space-y-2 min-w-[200px]">
                  <div className="flex items-center justify-between border-b border-gray-100 pb-1">
                    <span className="font-mono text-[10px] font-bold text-[#1769D2]">{pCode}</span>
                    <span className="text-[10px] text-[#64748B] bg-gray-100 px-1.5 py-0.5 rounded">
                      {proj.status || 'Ongoing'}
                    </span>
                  </div>

                  <h4 className="text-xs font-bold text-[#14213D] leading-tight">{proj.name}</h4>

                  <div className="text-[11px] text-[#64748B] flex items-center space-x-1">
                    <MapPin size={11} className="text-gray-400 shrink-0" />
                    <span>{proj.district || proj.state || 'Maharashtra'} • {proj.sector || 'Infrastructure'}</span>
                  </div>

                  <div className="space-y-1 pt-1">
                    <div className="flex justify-between text-[10px] font-bold text-[#14213D]">
                      <span>Physical Completion</span>
                      <span className="font-mono">{phys.toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-[#1769D2] h-full rounded-full"
                        style={{ width: `${Math.min(100, Math.max(0, phys))}%` }}
                      />
                    </div>

                    {fin > 0 && (
                      <div className="flex justify-between text-[10px] text-[#64748B] pt-0.5">
                        <span>Financial Progress</span>
                        <span className="font-mono font-semibold text-[#14213D]">{fin.toFixed(0)}%</span>
                      </div>
                    )}
                  </div>

                  <div className="pt-2 border-t border-gray-100 flex items-center justify-between">
                    {proj.risk_level && (
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded border bg-gray-50 text-gray-700">
                        Risk: {proj.risk_level}
                      </span>
                    )}
                    <button
                      type="button"
                      onClick={() => navigate(`/projects/${proj.id || pCode}`)}
                      className="ml-auto inline-flex items-center space-x-1 text-[11px] font-bold text-[#1769D2] hover:underline"
                    >
                      <span>View Project</span>
                      <ArrowUpRight size={12} />
                    </button>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-xs p-3 rounded-xl shadow-md z-[1000] border border-gray-200 font-sans text-xs space-y-1.5">
        <span className="font-bold text-[#14213D] text-[11px] block border-b border-gray-100 pb-1">
          GIS Project Legend ({validProjects.length} mapped)
        </span>
        <div className="flex items-center space-x-2 text-[10px] text-[#64748B]">
          <span className="w-3 h-3 rounded-full bg-red-400 border-2 border-red-600 shrink-0" />
          <span>High / Critical Risk / Delayed</span>
        </div>
        <div className="flex items-center space-x-2 text-[10px] text-[#64748B]">
          <span className="w-3 h-3 rounded-full bg-amber-400 border-2 border-amber-600 shrink-0" />
          <span>Medium Risk / Under Review</span>
        </div>
        <div className="flex items-center space-x-2 text-[10px] text-[#64748B]">
          <span className="w-3 h-3 rounded-full bg-emerald-400 border-2 border-emerald-600 shrink-0" />
          <span>Low Risk / Verified / Completed</span>
        </div>
        <div className="flex items-center space-x-2 text-[10px] text-[#64748B]">
          <span className="w-3 h-3 rounded-full bg-blue-400 border-2 border-blue-600 shrink-0" />
          <span>Ongoing / Normal</span>
        </div>
      </div>
    </div>
  );
}
