import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  SlidersHorizontal,
  Layers,
  MapPin,
  ExternalLink,
  UserPlus,
  ShieldAlert,
  Clock,
  Car,
  ChevronRight,
  Maximize2,
  RotateCcw,
} from 'lucide-react';
import { apiRequest } from '../services/api';

interface HotspotItem {
  id: string;
  code: string;
  name: string;
  roadName: string;
  lat: number;
  lon: number;
  riskScore: number;
  riskLevel: 'critical' | 'high' | 'medium' | 'low';
  accidentsCount: number;
  fatalities: number;
  injured: number;
  status: string;
  peakTimeText: string;
  factorsText?: string;
}

export const HotspotMapPage: React.FC = () => {
  const navigate = useNavigate();

  // Filters State
  const [dateRange, setDateRange] = useState('Dec 2025 – Nov 2026');
  const [selectedSeverities, setSelectedSeverities] = useState<string[]>(['Fatal', 'Grievous', 'Minor', 'Non-injury']);
  const [timeFilter, setTimeFilter] = useState<string>('all'); // all or evening
  const [roadType, setRoadType] = useState<string>('all');
  const [weather, setWeather] = useState<string>('all');
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showPoints, setShowPoints] = useState(true);
  const [showRanked, setShowRanked] = useState(true);
  const [unassignedOnly, setUnassignedOnly] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Selected Hotspot for floating drawer
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Reactive search that selects matching hotspot on the map
  useEffect(() => {
    if (!searchQuery.trim()) return;
    const q = searchQuery.toLowerCase();
    const foundIdx = seededHotspots.findIndex(
      (h) => h.code.toLowerCase().includes(q) || h.name.toLowerCase().includes(q) || h.roadName.toLowerCase().includes(q)
    );
    if (foundIdx !== -1) {
      setSelectedIndex(foundIdx);
    }
  }, [searchQuery]);

  // Default seeded hotspots matching reference mockups
  const seededHotspots: HotspotItem[] = [
    {
      id: 'h-1',
      code: 'H-0142',
      name: 'NH-65 × Station Road Junction',
      roadName: 'National Highway 65',
      lat: 17.4125,
      lon: 78.5721,
      riskScore: 92,
      riskLevel: 'critical',
      accidentsCount: 41,
      fatalities: 9,
      injured: 63,
      status: 'Under review',
      peakTimeText: '6–9 pm, Fri–Sat',
      factorsText: 'Two-wheelers 58% · Poor lighting at night 46%',
    },
    {
      id: 'h-2',
      code: 'H-0087',
      name: 'Outer Ring Road, Exit 12',
      roadName: 'Outer Ring Road',
      lat: 17.4890,
      lon: 78.6120,
      riskScore: 88,
      riskLevel: 'critical',
      accidentsCount: 37,
      fatalities: 7,
      injured: 48,
      status: 'Assigned',
      peakTimeText: '9–12 pm, Sat–Sun',
      factorsText: 'Overspeeding 62% · Truck lane conflicts 38%',
    },
    {
      id: 'h-3',
      code: 'H-0103',
      name: 'Market Road Curve',
      roadName: 'Market Road',
      lat: 17.3980,
      lon: 78.4720,
      riskScore: 79,
      riskLevel: 'high',
      accidentsCount: 29,
      fatalities: 4,
      injured: 38,
      status: 'Action in progress',
      peakTimeText: '3–6 pm, Daily',
      factorsText: 'Sharp curve negotiation · Pedestrian spillover',
    },
    {
      id: 'h-4',
      code: 'H-0215',
      name: 'Bypass Road Underpass',
      roadName: 'Bypass Road',
      lat: 17.4420,
      lon: 78.3810,
      riskScore: 74,
      riskLevel: 'high',
      accidentsCount: 26,
      fatalities: 3,
      injured: 31,
      status: 'Identified',
      peakTimeText: '6–9 pm, Mon–Wed',
      factorsText: 'Water logging · Inadequate clearance signage',
    },
    {
      id: 'h-5',
      code: 'H-0061',
      name: 'School Crossing, Ring Road',
      roadName: 'Ring Road',
      lat: 17.4310,
      lon: 78.5310,
      riskScore: 58,
      riskLevel: 'medium',
      accidentsCount: 22,
      fatalities: 1,
      injured: 29,
      status: 'Implemented',
      peakTimeText: '8–10 am & 3–5 pm',
      factorsText: 'Vulnerable road user exposure · Missing zebra',
    },
  ];

  const currentHotspot = seededHotspots[selectedIndex] || seededHotspots[0];

  const toggleSeverity = (sev: string) => {
    if (selectedSeverities.includes(sev)) {
      if (selectedSeverities.length > 1) {
        setSelectedSeverities(selectedSeverities.filter((s) => s !== sev));
      }
    } else {
      setSelectedSeverities([...selectedSeverities, sev]);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical':
        return '#C62F2A';
      case 'high':
        return '#E2762B';
      case 'medium':
        return '#E7B416';
      case 'low':
        return '#3E8E62';
      default:
        return '#9AA0A6';
    }
  };

  return (
    <div className="relative -m-6 md:-m-7 h-[calc(100vh-64px)] flex overflow-hidden select-none">
      {/* 1. Full-Bleed Map Canvas with SVG Roads & Clusters */}
      <div className="flex-1 relative bg-[#E8EBE3] overflow-hidden">
        {/* Render Map Vector Roads & Clusters */}
        <svg
          className="w-full h-full object-cover"
          viewBox="0 0 1000 640"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <radialGradient id="grad-crit" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#C62F2A" stopOpacity="0.75" />
              <stop offset="60%" stopColor="#C62F2A" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#C62F2A" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="grad-high" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#E2762B" stopOpacity="0.75" />
              <stop offset="60%" stopColor="#E2762B" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#E2762B" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="grad-med" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#E7B416" stopOpacity="0.75" />
              <stop offset="60%" stopColor="#E7B416" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#E7B416" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Grid pattern lines */}
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#DFE2DA" strokeWidth="0.8" />
          </pattern>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Major Road Artery Highways (NH-65, ORR, Bypass) */}
          <path d="M-20 560C220 520 420 480 560 330S700 250 1020 160" stroke="#DADCD5" strokeWidth="22" fill="none" />
          <path d="M-20 560C220 520 420 480 560 330S700 250 1020 160" stroke="#F5B800" strokeWidth="18" fill="none" />
          <path d="M-20 560C220 520 420 480 560 330S700 250 1020 160" stroke="#FFF" strokeWidth="2" strokeDasharray="14 10" fill="none" />

          <path d="M330 -20C340 200 340 400 350 430S470 600 480 700" stroke="#C7CABF" strokeWidth="14" fill="none" />
          <path d="M330 -20C340 200 340 400 350 430S470 600 480 700" stroke="#FFF" strokeWidth="10" fill="none" />

          <path d="M-20 230C200 250 380 255 520 270S700 300 1020 330" stroke="#C7CABF" strokeWidth="12" fill="none" />
          <path d="M-20 230C200 250 380 255 520 270S700 300 1020 330" stroke="#FFF" strokeWidth="8" fill="none" />

          <path d="M700 -20C700 100 700 190 700 250S760 500 780 700" stroke="#C7CABF" strokeWidth="14" fill="none" />
          <path d="M700 -20C700 100 700 190 700 250S760 500 780 700" stroke="#FFF" strokeWidth="10" fill="none" />

          {/* KDE Heatmap Density Halos */}
          {showHeatmap && (
            <>
              <circle cx="560" cy="330" r="110" fill="url(#grad-crit)" />
              <circle cx="700" cy="190" r="95" fill="url(#grad-crit)" />
              <circle cx="350" cy="430" r="80" fill="url(#grad-high)" />
              <circle cx="250" cy="170" r="75" fill="url(#grad-high)" />
              <circle cx="640" cy="400" r="65" fill="url(#grad-med)" />
            </>
          )}

          {/* Individual Accident Points (small red dots) */}
          {showPoints && (
            <g opacity="0.6">
              {[
                [555, 325], [568, 335], [562, 340], [550, 320], [572, 328], [558, 338], [564, 318],
                [695, 185], [705, 195], [710, 188], [692, 192], [708, 182],
                [345, 428], [355, 435], [352, 422], [348, 438],
                [245, 168], [255, 174], [252, 165],
                [638, 398], [644, 404], [642, 395],
              ].map(([px, py], i) => (
                <circle key={i} cx={px} cy={py} r="2.5" fill="#C62F2A" />
              ))}
            </g>
          )}

          {/* Ranked Hotspot Markers with numbered badges */}
          {showRanked && (
            <>
              {/* Marker 1: NH-65 (560, 330) */}
              <g
                className="cursor-pointer transition-transform hover:scale-110"
                onClick={() => setSelectedIndex(0)}
              >
                {selectedIndex === 0 && (
                  <circle cx="560" cy="330" r="24" fill="none" stroke="#1F2328" strokeWidth="2.5" />
                )}
                <circle cx="560" cy="330" r="14" fill="#C62F2A" stroke="#FFFFFF" strokeWidth="3" />
                <text x="560" y="334.5" textAnchor="middle" fontSize="12" fontWeight="700" fill="#FFF">
                  1
                </text>
              </g>

              {/* Marker 2: ORR Exit 12 (700, 190) */}
              <g
                className="cursor-pointer transition-transform hover:scale-110"
                onClick={() => setSelectedIndex(1)}
              >
                {selectedIndex === 1 && (
                  <circle cx="700" cy="190" r="24" fill="none" stroke="#1F2328" strokeWidth="2.5" />
                )}
                <circle cx="700" cy="190" r="14" fill="#C62F2A" stroke="#FFFFFF" strokeWidth="3" />
                <text x="700" y="194.5" textAnchor="middle" fontSize="12" fontWeight="700" fill="#FFF">
                  2
                </text>
              </g>

              {/* Marker 3: Market Road Curve (350, 430) */}
              <g
                className="cursor-pointer transition-transform hover:scale-110"
                onClick={() => setSelectedIndex(2)}
              >
                {selectedIndex === 2 && (
                  <circle cx="350" cy="430" r="24" fill="none" stroke="#1F2328" strokeWidth="2.5" />
                )}
                <circle cx="350" cy="430" r="14" fill="#E2762B" stroke="#FFFFFF" strokeWidth="3" />
                <text x="350" y="434.5" textAnchor="middle" fontSize="12" fontWeight="700" fill="#FFF">
                  3
                </text>
              </g>

              {/* Marker 4: Bypass Road (250, 170) */}
              <g
                className="cursor-pointer transition-transform hover:scale-110"
                onClick={() => setSelectedIndex(3)}
              >
                {selectedIndex === 3 && (
                  <circle cx="250" cy="170" r="24" fill="none" stroke="#1F2328" strokeWidth="2.5" />
                )}
                <circle cx="250" cy="170" r="14" fill="#E2762B" stroke="#FFFFFF" strokeWidth="3" />
                <text x="250" y="174.5" textAnchor="middle" fontSize="12" fontWeight="700" fill="#FFF">
                  4
                </text>
              </g>

              {/* Marker 5: School Crossing (640, 400) */}
              <g
                className="cursor-pointer transition-transform hover:scale-110"
                onClick={() => setSelectedIndex(4)}
              >
                {selectedIndex === 4 && (
                  <circle cx="640" cy="400" r="24" fill="none" stroke="#1F2328" strokeWidth="2.5" />
                )}
                <circle cx="640" cy="400" r="14" fill="#E7B416" stroke="#FFFFFF" strokeWidth="3" />
                <text x="640" y="404.5" textAnchor="middle" fontSize="12" fontWeight="700" fill="#1D2125">
                  5
                </text>
              </g>
            </>
          )}
        </svg>

        {/* 2. Top Bar Search Input Floating on Map */}
        <div className="absolute top-4 left-6 right-6 md:right-auto md:w-96 z-10">
          <div className="relative shadow-md rounded-btn">
            <Search className="w-4 h-4 text-muted absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search road or junction (e.g. NH-65, ORR)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 rounded-btn border border-line bg-card/95 backdrop-blur-sm text-ink text-[13.5px] shadow-sm focus:outline-none focus:ring-2 focus:ring-lane"
            />
          </div>
        </div>

        {/* 3. Left Floating Filters Panel (Page_05_Hotspot_Map.png) */}
        <div className="absolute top-16 left-6 w-[280px] bg-card/95 backdrop-blur-md border border-line rounded-panel p-4 shadow-lg z-10 space-y-4 max-h-[calc(100vh-140px)] overflow-y-auto">
          <div className="flex items-center justify-between pb-2 border-b border-line">
            <div className="flex items-center gap-2 text-ink font-semibold text-[13.5px]">
              <SlidersHorizontal className="w-4 h-4 text-lane" />
              <span>Map Filters</span>
            </div>
            <button
              onClick={() => {
                setSelectedSeverities(['Fatal', 'Grievous', 'Minor', 'Non-injury']);
                setShowHeatmap(true);
                setShowPoints(true);
                setShowRanked(true);
              }}
              className="text-xs text-muted hover:text-ink flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          </div>

          {/* Date Range */}
          <div>
            <label className="block text-[11.5px] font-semibold text-muted uppercase tracking-wider mb-1">
              Time Horizon
            </label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-btn border border-line bg-paper text-ink text-[12.5px]"
            >
              <option>Dec 2025 – Nov 2026 (Past 12 mo)</option>
              <option>Last 6 Months</option>
              <option>Year 2025 Full</option>
            </select>
          </div>

          {/* Severity Chips */}
          <div>
            <label className="block text-[11.5px] font-semibold text-muted uppercase tracking-wider mb-1.5">
              Severity
            </label>
            <div className="flex flex-wrap gap-1.5">
              {[
                { label: 'Fatal', color: 'bg-crit text-white' },
                { label: 'Grievous', color: 'bg-high text-white' },
                { label: 'Minor', color: 'bg-med text-ink' },
                { label: 'Non-injury', color: 'bg-low text-white' },
              ].map((s) => {
                const active = selectedSeverities.includes(s.label);
                return (
                  <button
                    key={s.label}
                    onClick={() => toggleSeverity(s.label)}
                    className={`px-2.5 py-1 rounded-full text-[11.5px] font-semibold transition-all ${
                      active ? s.color : 'bg-paper text-muted border border-line opacity-50'
                    }`}
                  >
                    {s.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Road Type Chips */}
          <div>
            <label className="block text-[11.5px] font-semibold text-muted uppercase tracking-wider mb-1.5">
              Road Type
            </label>
            <div className="flex flex-wrap gap-1.5">
              {['all', 'national_highway', 'city_road', 'junction'].map((rt) => (
                <button
                  key={rt}
                  onClick={() => setRoadType(rt)}
                  className={`px-2.5 py-1 rounded-full text-[11.5px] font-medium border transition-colors ${
                    roadType === rt
                      ? 'bg-asphalt text-white border-asphalt'
                      : 'bg-paper text-muted border-line hover:border-ink'
                  }`}
                >
                  {rt === 'all'
                    ? 'All roads'
                    : rt === 'national_highway'
                    ? 'National highway'
                    : rt === 'city_road'
                    ? 'City road'
                    : 'Junction only'}
                </button>
              ))}
            </div>
          </div>

          {/* Weather Chips */}
          <div>
            <label className="block text-[11.5px] font-semibold text-muted uppercase tracking-wider mb-1.5">
              Weather
            </label>
            <div className="flex gap-1.5">
              {['all', 'rain', 'fog'].map((w) => (
                <button
                  key={w}
                  onClick={() => setWeather(w)}
                  className={`px-2.5 py-1 rounded-full text-[11.5px] font-medium border capitalize ${
                    weather === w
                      ? 'bg-asphalt text-white border-asphalt'
                      : 'bg-paper text-muted border-line'
                  }`}
                >
                  {w}
                </button>
              ))}
            </div>
          </div>

          {/* Layer Checkboxes */}
          <div className="pt-2 border-t border-line space-y-1.5">
            <label className="block text-[11.5px] font-semibold text-muted uppercase tracking-wider mb-1">
              Map Layers
            </label>
            <label className="flex items-center gap-2 text-[12.5px] text-ink cursor-pointer">
              <input
                type="checkbox"
                checked={showHeatmap}
                onChange={(e) => setShowHeatmap(e.target.checked)}
                className="rounded border-line text-lane focus:ring-lane"
              />
              <span>Heatmap density layer</span>
            </label>
            <label className="flex items-center gap-2 text-[12.5px] text-ink cursor-pointer">
              <input
                type="checkbox"
                checked={showPoints}
                onChange={(e) => setShowPoints(e.target.checked)}
                className="rounded border-line text-lane focus:ring-lane"
              />
              <span>Accident crash points</span>
            </label>
            <label className="flex items-center gap-2 text-[12.5px] text-ink cursor-pointer">
              <input
                type="checkbox"
                checked={showRanked}
                onChange={(e) => setShowRanked(e.target.checked)}
                className="rounded border-line text-lane focus:ring-lane"
              />
              <span>Ranked hotspot blackspots</span>
            </label>
            <label className="flex items-center gap-2 text-[12.5px] text-ink cursor-pointer">
              <input
                type="checkbox"
                checked={unassignedOnly}
                onChange={(e) => setUnassignedOnly(e.target.checked)}
                className="rounded border-line text-lane focus:ring-lane"
              />
              <span>Show only unassigned cases</span>
            </label>
          </div>
        </div>

        {/* 4. Right Floating Hotspot Preview Card (Page_05_Hotspot_Map.png) */}
        <div className="absolute top-4 right-6 w-[340px] bg-card/95 backdrop-blur-md border border-line rounded-panel p-5 shadow-xl z-10 space-y-4">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-[11.5px] font-semibold text-muted uppercase tracking-wider">
                Hotspot {currentHotspot.code} · Rank {selectedIndex + 1} of 47
              </div>
              <h3 className="text-[16px] font-semibold text-ink leading-tight mt-0.5">
                {currentHotspot.name}
              </h3>
            </div>
            <div className="text-right">
              <span
                className="inline-block px-2.5 py-0.5 rounded-full text-[11.5px] font-bold text-white uppercase tracking-wide"
                style={{ backgroundColor: getRiskColor(currentHotspot.riskLevel) }}
              >
                {currentHotspot.riskLevel}
              </span>
              <div className="text-[11px] text-muted mt-0.5 font-medium">
                {currentHotspot.status}
              </div>
            </div>
          </div>

          {/* Score Badge */}
          <div className="flex items-center justify-between p-2.5 rounded-btn bg-paper border border-line">
            <span className="text-[12.5px] text-muted">Risk Score</span>
            <span className="text-[17px] font-bold text-ink font-mono">
              {currentHotspot.riskScore} <span className="text-xs font-normal text-muted">/ 100</span>
            </span>
          </div>

          {/* 3 Metric Columns */}
          <div className="grid grid-cols-3 gap-2 text-center py-1 border-y border-line">
            <div>
              <div className="text-[18px] font-bold text-ink">
                {currentHotspot.accidentsCount}
              </div>
              <div className="text-[11px] text-muted">Accidents</div>
            </div>
            <div>
              <div className="text-[18px] font-bold text-crit">
                {currentHotspot.fatalities}
              </div>
              <div className="text-[11px] text-muted">Deaths</div>
            </div>
            <div>
              <div className="text-[18px] font-bold text-ink">
                {currentHotspot.injured}
              </div>
              <div className="text-[11px] text-muted">Injured</div>
            </div>
          </div>

          {/* Temporal & Factor context */}
          <div className="space-y-1.5 text-[12.5px]">
            <div className="flex items-center gap-1.5 text-muted">
              <Clock className="w-3.5 h-3.5 text-lane" />
              <span>Peak: <strong className="text-ink">{currentHotspot.peakTimeText}</strong></span>
            </div>
            <div className="text-muted leading-relaxed">
              {currentHotspot.factorsText}
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex items-center gap-2 pt-1">
            <button
              onClick={() => navigate(`/cases/${currentHotspot.code}`)}
              className="flex-1 py-2 rounded-btn bg-lane text-ink font-semibold text-[13px] hover:brightness-105 transition-all shadow-sm flex items-center justify-center gap-1.5"
            >
              <span>Open details</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => alert(`Assigning official to ${currentHotspot.code}`)}
              className="px-3.5 py-2 rounded-btn border border-line bg-card text-ink text-[13px] font-medium hover:bg-paper"
            >
              Assign
            </button>
          </div>

          {/* Other High-Priority Hotspots Mini List */}
          <div className="pt-2 border-t border-line">
            <div className="text-[11.5px] font-semibold text-muted uppercase tracking-wider mb-2">
              Other High-Priority Hotspots
            </div>
            <div className="space-y-1">
              {seededHotspots.slice(1, 4).map((h, i) => (
                <div
                  key={h.code}
                  onClick={() => setSelectedIndex(i + 1)}
                  className="p-1.5 rounded-btn hover:bg-paper cursor-pointer flex items-center justify-between text-[12px] transition-colors"
                >
                  <div className="truncate pr-2">
                    <span className="font-semibold text-ink">{h.code}</span> · {h.name}
                  </div>
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: getRiskColor(h.riskLevel) }}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 5. Bottom-Left Risk Legend */}
        <div className="absolute bottom-4 left-6 bg-card/90 backdrop-blur-sm border border-line rounded-btn px-3.5 py-2 shadow-md z-10 flex items-center gap-3 text-[12px]">
          <span className="font-semibold text-muted">Risk:</span>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-crit" />
            <span className="text-ink">Critical</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-high" />
            <span className="text-ink">High</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-med" />
            <span className="text-ink">Medium</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-low" />
            <span className="text-ink">Low</span>
          </div>
        </div>
      </div>
    </div>
  );
};
