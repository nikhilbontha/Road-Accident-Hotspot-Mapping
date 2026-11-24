import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, ShieldCheck, AlertCircle, Eye, ArrowRight } from 'lucide-react';

interface PublicArea {
  id: string;
  name: string;
  lat: number;
  lon: number;
  riskLevel: 'critical' | 'high' | 'medium';
  accidentBand: string;
  advisory: string;
}

export const PublicMapPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedIndex, setSelectedIndex] = useState(0);

  const publicAreas: PublicArea[] = [
    {
      id: 'pa-1',
      name: 'NH-65 × Station Road Area',
      lat: 17.4125,
      lon: 78.5721,
      riskLevel: 'critical',
      accidentBand: '40+ crashes',
      advisory:
        'High density of two-wheeler turning conflicts during evening hours (6–9 pm). Pedestrians should use designated crossing zones and drivers must observe signal clearance.',
    },
    {
      id: 'pa-2',
      name: 'Outer Ring Road, Exit 12 Area',
      lat: 17.4890,
      lon: 78.6120,
      riskLevel: 'critical',
      accidentBand: '30–39 crashes',
      advisory:
        'High-speed merge zone. Heavy commercial vehicle movement at night. Maintain safe following distance and avoid abrupt lane changes.',
    },
    {
      id: 'pa-3',
      name: 'Market Road Corridor',
      lat: 17.3980,
      lon: 78.4720,
      riskLevel: 'high',
      accidentBand: '20–29 crashes',
      advisory:
        'Sharp curved road section with high pedestrian footfall. Speed limit strictly 30 km/h.',
    },
    {
      id: 'pa-4',
      name: 'Bypass Road Underpass',
      lat: 17.4420,
      lon: 78.3810,
      riskLevel: 'high',
      accidentBand: '20–29 crashes',
      advisory:
        'Low visibility on approach and potential water pooling during wet weather. Drive with headlights on.',
    },
    {
      id: 'pa-5',
      name: 'Ring Road School Stretch',
      lat: 17.4310,
      lon: 78.5310,
      riskLevel: 'medium',
      accidentBand: '20–29 crashes',
      advisory:
        'School zone active 8–10 am and 3–5 pm. Yield to student pedestrian crossings.',
    },
  ];

  const currentArea = publicAreas[selectedIndex];

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical':
        return '#C62F2A';
      case 'high':
        return '#E2762B';
      default:
        return '#E7B416';
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-paper">
      {/* Light Public Header (Page_13_Public_Map.png) */}
      <header className="h-16 bg-card border-b border-line px-6 flex items-center justify-between z-20 sticky top-0 shadow-sm">
        <div className="flex items-center gap-3">
          <div
            onClick={() => navigate('/')}
            className="flex items-center gap-2 cursor-pointer"
          >
            <div className="w-8 h-8 rounded-lg bg-lane flex items-center justify-center text-asphalt shadow-sm">
              <MapPin className="w-4 h-4 text-asphalt fill-asphalt" />
            </div>
            <span className="text-[16px] font-semibold text-ink">
              Hotspot Mapping
            </span>
          </div>
          <span className="hidden sm:inline text-line text-lg">|</span>
          <span className="hidden sm:inline text-[13px] text-muted">
            Public hotspot map · Combined, anonymized figures · Dec 2025 – Nov 2026
          </span>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => navigate('/login')}
            className="px-3.5 py-1.5 rounded-btn border border-line bg-card text-ink text-[13px] font-medium hover:bg-paper"
          >
            Sign in
          </button>
          <button
            onClick={() => navigate('/signup')}
            className="px-3.5 py-1.5 rounded-btn bg-lane text-ink text-[13px] font-semibold hover:brightness-105 shadow-sm"
          >
            Create account
          </button>
        </div>
      </header>

      {/* Main Map Canvas */}
      <div className="flex-1 relative bg-[#E8EBE3] overflow-hidden min-h-[calc(100vh-64px)]">
        {/* SVG Public Map with aggregated banded circles only */}
        <svg
          className="w-full h-full object-cover"
          viewBox="0 0 1000 640"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <radialGradient id="pub-crit" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#C62F2A" stopOpacity="0.6" />
              <stop offset="70%" stopColor="#C62F2A" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#C62F2A" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="pub-high" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#E2762B" stopOpacity="0.6" />
              <stop offset="70%" stopColor="#E2762B" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#E2762B" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="pub-med" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#E7B416" stopOpacity="0.6" />
              <stop offset="70%" stopColor="#E7B416" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#E7B416" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Road Network Lines */}
          <path d="M-20 560C220 520 420 480 560 330S700 250 1020 160" stroke="#DADCD5" strokeWidth="20" fill="none" />
          <path d="M-20 560C220 520 420 480 560 330S700 250 1020 160" stroke="#F5B800" strokeWidth="16" fill="none" />
          <path d="M-20 560C220 520 420 480 560 330S700 250 1020 160" stroke="#FFF" strokeWidth="2" strokeDasharray="12 10" fill="none" />

          <path d="M330 -20C340 200 340 400 350 430S470 600 480 700" stroke="#C7CABF" strokeWidth="12" fill="none" />
          <path d="M-20 230C200 250 380 255 520 270S700 300 1020 330" stroke="#C7CABF" strokeWidth="10" fill="none" />
          <path d="M700 -20C700 100 700 190 700 250S760 500 780 700" stroke="#C7CABF" strokeWidth="12" fill="none" />

          {/* Aggregated ~500m Safety Warning Circles (BR-08) */}
          <circle cx="560" cy="330" r="105" fill="url(#pub-crit)" />
          <circle cx="700" cy="190" r="90" fill="url(#pub-crit)" />
          <circle cx="350" cy="430" r="75" fill="url(#pub-high)" />
          <circle cx="250" cy="170" r="70" fill="url(#pub-high)" />
          <circle cx="640" cy="400" r="60" fill="url(#pub-med)" />

          {/* Area Markers with Letters */}
          {[
            { cx: 560, cy: 330, label: 'A', color: '#C62F2A' },
            { cx: 700, cy: 190, label: 'B', color: '#C62F2A' },
            { cx: 350, cy: 430, label: 'C', color: '#E2762B' },
            { cx: 250, cy: 170, label: 'D', color: '#E2762B' },
            { cx: 640, cy: 400, label: 'E', color: '#E7B416' },
          ].map((m, idx) => (
            <g
              key={m.label}
              className="cursor-pointer transition-transform hover:scale-110"
              onClick={() => setSelectedIndex(idx)}
            >
              {selectedIndex === idx && (
                <circle cx={m.cx} cy={m.cy} r="22" fill="none" stroke="#1F2328" strokeWidth="2.5" />
              )}
              <circle cx={m.cx} cy={m.cy} r="13" fill={m.color} stroke="#FFFFFF" strokeWidth="3" />
              <text x={m.cx} y={m.cy + 4.5} textAnchor="middle" fontSize="12" fontWeight="700" fill="#FFF">
                {m.label}
              </text>
            </g>
          ))}
        </svg>

        {/* Left Floating Card: "Areas to take extra care" */}
        <div className="absolute top-6 left-6 w-[310px] bg-card/95 backdrop-blur-md border border-line rounded-panel p-4 shadow-xl z-10 space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-line">
            <AlertCircle className="w-4 h-4 text-crit" />
            <h3 className="font-semibold text-ink text-[14.5px]">
              Areas to take extra care
            </h3>
          </div>

          <div className="space-y-1.5 max-h-[calc(100vh-220px)] overflow-y-auto pr-1">
            {publicAreas.map((area, i) => {
              const isSelected = selectedIndex === i;
              return (
                <div
                  key={area.id}
                  onClick={() => setSelectedIndex(i)}
                  className={`p-2.5 rounded-btn cursor-pointer transition-all border ${
                    isSelected
                      ? 'bg-paper border-lane shadow-sm'
                      : 'border-transparent hover:bg-paper/60'
                  }`}
                >
                  <div className="flex items-center justify-between text-[13px] mb-1">
                    <span className="font-semibold text-ink leading-tight">
                      {String.fromCharCode(65 + i)}. {area.name}
                    </span>
                    <span
                      className="px-2 py-0.5 rounded-full text-[10.5px] font-bold text-white uppercase"
                      style={{ backgroundColor: getRiskColor(area.riskLevel) }}
                    >
                      {area.riskLevel}
                    </span>
                  </div>
                  <div className="text-[12px] text-muted">
                    {area.accidentBand} in past 12 months
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Floating Card: "Selected area advisory" */}
        <div className="absolute top-6 right-6 w-[340px] bg-card/95 backdrop-blur-md border border-line rounded-panel p-5 shadow-xl z-10 space-y-3.5">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-[11px] font-semibold text-muted uppercase tracking-wider">
                Area {String.fromCharCode(65 + selectedIndex)} · Public Safety Note
              </div>
              <h3 className="text-[16px] font-semibold text-ink leading-tight mt-0.5">
                {currentArea.name}
              </h3>
            </div>
            <span
              className="px-2.5 py-0.5 rounded-full text-[11px] font-bold text-white uppercase"
              style={{ backgroundColor: getRiskColor(currentArea.riskLevel) }}
            >
              {currentArea.riskLevel}
            </span>
          </div>

          <div className="p-3 bg-paper rounded-btn border border-line text-[12.5px] text-ink leading-relaxed">
            <strong className="block mb-1 text-ink">Citizen Advisory:</strong>
            {currentArea.advisory}
          </div>

          <div className="text-[12px] text-muted pt-1 flex items-center justify-between">
            <span>Historical crash band:</span>
            <strong className="text-ink font-mono">{currentArea.accidentBand}</strong>
          </div>
        </div>

        {/* Bottom Notice Banner (BR-08 Privacy Assurance) */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-asphalt text-white text-[12.5px] px-5 py-2.5 rounded-full shadow-lg z-10 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-lane" />
          <span>Areas are shown within about 500 m. No personal details are shown.</span>
        </div>
      </div>
    </div>
  );
};
