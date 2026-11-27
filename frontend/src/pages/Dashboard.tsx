import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getApiUrl } from '../services/api';
import {
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  Calendar,
  Filter,
  FileDown,
  ArrowRight,
  ChevronRight
} from 'lucide-react';

interface SummaryData {
  accidents: { value: number; change: number; change_direction: string; is_improvement: boolean; label: string };
  fatalities: { value: number; change: number; change_direction: string; is_improvement: boolean; label: string };
  injured: { value: number; change: number; change_direction: string; is_improvement: boolean; label: string };
  hotspots: { value: number; critical_count: number; change: number; subtitle: string; label: string };
  interventions: { implemented: number; in_progress: number; subtitle: string; label: string };
}

interface MonthlyItem {
  month: string;
  short: string;
  accidents: number;
  fatalities: number;
}

interface RiskDistribution {
  total: number;
  new_this_week: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

interface HeatGridData {
  days: string[];
  time_blocks: string[];
  matrix: number[][];
  peak_summary: string;
}

interface TopHotspot {
  id: string;
  code: string;
  name: string;
  risk_level: string;
  risk_score: number;
  accidents_count: number;
  fatalities_count: number;
  status: string;
  assigned_to: string;
}

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedPeriod, setSelectedPeriod] = useState('Dec 2025 – Nov 2026');
  const [selectedArea, setSelectedArea] = useState('All areas');

  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [monthly, setMonthly] = useState<MonthlyItem[]>([]);
  const [riskDist, setRiskDist] = useState<RiskDistribution | null>(null);
  const [heatGrid, setHeatGrid] = useState<HeatGridData | null>(null);
  const [topHotspots, setTopHotspots] = useState<TopHotspot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem('rah_token');
        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        };

        const [sumRes, monRes, riskRes, heatRes, topRes] = await Promise.all([
          fetch(getApiUrl('/dashboard/summary'), { headers }),
          fetch(getApiUrl('/dashboard/monthly'), { headers }),
          fetch(getApiUrl('/dashboard/risk-distribution'), { headers }),
          fetch(getApiUrl('/dashboard/heat-grid'), { headers }),
          fetch(getApiUrl('/dashboard/top-hotspots'), { headers })
        ]);

        if (sumRes.ok) setSummary(await sumRes.json());
        if (monRes.ok) setMonthly(await monRes.json());
        if (riskRes.ok) setRiskDist(await riskRes.json());
        if (heatRes.ok) setHeatGrid(await heatRes.json());
        if (topRes.ok) setTopHotspots(await topRes.json());
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [selectedPeriod, selectedArea]);

  // Fallback data if still loading or offline
  const s = summary || {
    accidents: { value: 4812, change: -4.2, change_direction: 'down', is_improvement: true, label: 'vs previous 12 months' },
    fatalities: { value: 389, change: -8.5, change_direction: 'down', is_improvement: true, label: 'vs previous 12 months' },
    injured: { value: 5274, change: +2.1, change_direction: 'up', is_improvement: false, label: 'vs previous 12 months' },
    hotspots: { value: 47, critical_count: 12, change: -2, subtitle: '12 are critical', label: '2 new this week' },
    interventions: { implemented: 18, in_progress: 11, subtitle: '11 more in progress', label: 'Tracked across all zones' }
  };

  const rd = riskDist || { total: 47, new_this_week: 2, critical: 12, high: 15, medium: 13, low: 7 };

  const rawMonths = monthly.length > 0 ? monthly : [
    { month: 'Dec 2025', short: 'Dec', accidents: 412, fatalities: 34 },
    { month: 'Jan 2026', short: 'Jan', accidents: 398, fatalities: 31 },
    { month: 'Feb 2026', short: 'Feb', accidents: 365, fatalities: 28 },
    { month: 'Mar 2026', short: 'Mar', accidents: 425, fatalities: 36 },
    { month: 'Apr 2026', short: 'Apr', accidents: 380, fatalities: 29 },
    { month: 'May 2026', short: 'May', accidents: 440, fatalities: 38 },
    { month: 'Jun 2026', short: 'Jun', accidents: 395, fatalities: 30 },
    { month: 'Jul 2026', short: 'Jul', accidents: 410, fatalities: 33 },
    { month: 'Aug 2026', short: 'Aug', accidents: 430, fatalities: 35 },
    { month: 'Sep 2026', short: 'Sep', accidents: 372, fatalities: 27 },
    { month: 'Oct 2026', short: 'Oct', accidents: 395, fatalities: 32 },
    { month: 'Nov 2026', short: 'Nov', accidents: 390, fatalities: 36 }
  ];
  const months = rawMonths.length > 12 ? rawMonths.slice(-12) : rawMonths;

  const grid = heatGrid || {
    days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    time_blocks: ['12a-3a', '3a-6a', '6a-9a', '9a-12p', '12p-3p', '3p-6p', '6p-9p', '9p-12a'],
    matrix: [
      [12, 6, 18, 32, 45, 68, 92, 54],
      [10, 5, 20, 35, 42, 72, 88, 48],
      [14, 7, 22, 38, 48, 75, 95, 52],
      [15, 8, 25, 40, 52, 82, 105, 62],
      [22, 12, 30, 48, 65, 110, 142, 98],
      [35, 18, 24, 52, 70, 115, 158, 120],
      [28, 15, 16, 42, 60, 95, 124, 85]
    ],
    peak_summary: '6–9 pm, Fri–Sat accounts for 34% of all severe crashes.'
  };

  const priorityHotspots: TopHotspot[] = topHotspots.length > 0 ? topHotspots : [
    { id: '1', code: 'H-0142', name: 'NH-65 × Station Road Junction', risk_level: 'critical', risk_score: 92.0, accidents_count: 41, fatalities_count: 9, status: 'Under review', assigned_to: 'Unassigned' },
    { id: '2', code: 'H-0087', name: 'Outer Ring Road, Exit 12', risk_level: 'critical', risk_score: 88.0, accidents_count: 37, fatalities_count: 7, status: 'Assigned', assigned_to: 'Ravi Kumar' },
    { id: '3', code: 'H-0103', name: 'Market Road Curve', risk_level: 'high', risk_score: 79.0, accidents_count: 29, fatalities_count: 4, status: 'Action in progress', assigned_to: 'Sana Fatima' },
    { id: '4', code: 'H-0215', name: 'Bypass Road Underpass', risk_level: 'high', risk_score: 74.0, accidents_count: 26, fatalities_count: 3, status: 'Identified', assigned_to: 'Unassigned' },
    { id: '5', code: 'H-0061', name: 'School Crossing, Ring Road', risk_level: 'medium', risk_score: 58.0, accidents_count: 22, fatalities_count: 1, status: 'Implemented', assigned_to: 'Meera Iyer' },
    { id: '6', code: 'H-0178', name: 'Lake View Roundabout', risk_level: 'medium', risk_score: 54.0, accidents_count: 19, fatalities_count: 1, status: 'Under review', assigned_to: 'Unassigned' }
  ];

  // Helper for cell color intensity
  const getCellBg = (val: number) => {
    if (val >= 120) return 'bg-[#C62F2A] text-white font-semibold';
    if (val >= 80) return 'bg-[#E2762B] text-white';
    if (val >= 50) return 'bg-[#F5B800] text-ink font-medium';
    if (val >= 25) return 'bg-[#FFF3C4] text-ink';
    return 'bg-[#F2F3EF] text-muted';
  };

  // Status dot color mapping
  const getStatusDot = (st: string) => {
    const s = st.toLowerCase();
    if (s.includes('identified')) return 'bg-[#9AA0A6]';
    if (s.includes('review')) return 'bg-[#F5B800]';
    if (s.includes('assigned')) return 'bg-[#2F6FB5]';
    if (s.includes('progress')) return 'bg-[#E2762B]';
    if (s.includes('implemented')) return 'bg-[#3E8E62]';
    return 'bg-[#1F2328]';
  };

  // Risk Chip styling
  const getRiskChip = (level: string) => {
    const l = level.toLowerCase();
    if (l === 'critical') return 'bg-[#C62F2A] text-white';
    if (l === 'high') return 'bg-[#E2762B] text-white';
    if (l === 'medium') return 'bg-[#E7B416] text-ink';
    return 'bg-[#3E8E62] text-white';
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Filter Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-card border border-line rounded-card p-4 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-line bg-paper text-ink text-[13px] font-medium">
            <Calendar className="w-3.5 h-3.5 text-muted" />
            <span>{selectedPeriod}</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-line bg-paper text-ink text-[13px] font-medium">
            <Filter className="w-3.5 h-3.5 text-muted" />
            <select
              value={selectedArea}
              onChange={(e) => setSelectedArea(e.target.value)}
              className="bg-transparent border-none text-[13px] text-ink focus:outline-none cursor-pointer"
            >
              <option value="All areas">All areas</option>
              <option value="Zone 3 (Industrial)">Zone 3 (Industrial)</option>
              <option value="Zone 5 (NH-65 / Ring Road)">Zone 5 (NH-65 / Ring Road)</option>
              <option value="Central Corridor">Central Corridor</option>
            </select>
          </div>
        </div>

        <button
          onClick={() => navigate('/reports')}
          className="flex items-center gap-2 px-4 py-2 rounded-btn bg-lane text-ink font-semibold text-[13.5px] hover:brightness-95 transition shadow-sm"
        >
          <FileDown className="w-4 h-4 text-ink" />
          Export report
        </button>
      </div>

      {/* KPI Ribbon (5 Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Accidents */}
        <div className="bg-card border border-line rounded-card p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[12.5px] font-medium text-muted">Accidents recorded</span>
            <div className="p-1.5 rounded-full bg-paper">
              <AlertTriangle className="w-4 h-4 text-muted" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-[26px] font-bold text-ink tabular-nums leading-none">
              {s.accidents.value.toLocaleString()}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[12px]">
              <span className="flex items-center font-medium text-[#3E8E62]">
                <TrendingDown className="w-3.5 h-3.5 mr-0.5" />
                {Math.abs(s.accidents.change)}%
              </span>
              <span className="text-muted">{s.accidents.label}</span>
            </div>
          </div>
        </div>

        {/* Fatalities */}
        <div className="bg-card border border-line rounded-card p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[12.5px] font-medium text-muted">Fatalities</span>
            <div className="p-1.5 rounded-full bg-crit/10">
              <ShieldAlert className="w-4 h-4 text-crit" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-[26px] font-bold text-crit tabular-nums leading-none">
              {s.fatalities.value.toLocaleString()}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[12px]">
              <span className="flex items-center font-medium text-[#3E8E62]">
                <TrendingDown className="w-3.5 h-3.5 mr-0.5" />
                {Math.abs(s.fatalities.change)}%
              </span>
              <span className="text-muted">{s.fatalities.label}</span>
            </div>
          </div>
        </div>

        {/* People Injured */}
        <div className="bg-card border border-line rounded-card p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[12.5px] font-medium text-muted">People injured</span>
            <div className="p-1.5 rounded-full bg-[#E2762B]/10">
              <AlertTriangle className="w-4 h-4 text-[#E2762B]" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-[26px] font-bold text-ink tabular-nums leading-none">
              {s.injured.value.toLocaleString()}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[12px]">
              <span className="flex items-center font-medium text-crit">
                <TrendingUp className="w-3.5 h-3.5 mr-0.5" />
                +{s.injured.change}%
              </span>
              <span className="text-muted">{s.injured.label}</span>
            </div>
          </div>
        </div>

        {/* Hotspots Identified */}
        <div className="bg-card border border-line rounded-card p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[12.5px] font-medium text-muted">Hotspots identified</span>
            <span className="px-2 py-0.5 text-[11px] font-semibold rounded-full bg-crit/10 text-crit">
              {s.hotspots.subtitle}
            </span>
          </div>
          <div className="mt-2">
            <div className="text-[26px] font-bold text-ink tabular-nums leading-none">
              {s.hotspots.value}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[12px]">
              <span className="font-medium text-[#8A6A00]">{s.hotspots.label}</span>
            </div>
          </div>
        </div>

        {/* Actions Implemented */}
        <div className="bg-card border border-line rounded-card p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[12.5px] font-medium text-muted">Actions implemented</span>
            <div className="p-1.5 rounded-full bg-[#3E8E62]/10">
              <CheckCircle2 className="w-4 h-4 text-[#3E8E62]" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-[26px] font-bold text-ink tabular-nums leading-none">
              {s.interventions.implemented}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[12px]">
              <span className="font-semibold text-ink">{s.interventions.subtitle}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Monthly Trends Chart + Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Accidents by Month (2 Cols) */}
        <div className="lg:col-span-2 bg-card border border-line rounded-card p-5 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-[15px] font-semibold text-ink">Accidents by month</h2>
              <p className="text-[12.5px] text-muted">Monthly accident volume and fatalities (Dec 2025 – Nov 2026)</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-amber-200 border border-amber-400" />
                <span className="text-muted">Accidents</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded bg-crit" />
                <span className="text-muted">Fatalities</span>
              </div>
            </div>
          </div>

          {/* Handcrafted Visual Bar/Line Chart */}
          <div className="h-64 flex flex-col justify-end pt-4">
            <div className="flex-1 flex items-end gap-2 sm:gap-4 px-2 border-b border-line pb-2">
              {months.map((m, idx) => {
                const accHeight = Math.round((m.accidents / 500) * 160);
                const fatHeight = Math.round((m.fatalities / 50) * 120);

                return (
                  <div key={idx} className="flex-1 flex flex-col items-center gap-1 group relative">
                    {/* Tooltip on hover */}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-12 bg-asphalt text-white text-[11px] rounded px-2 py-1 pointer-events-none whitespace-nowrap z-10 shadow-md">
                      {m.month}: {m.accidents} crashes, {m.fatalities} deaths
                    </div>

                    <div className="w-full flex items-end justify-center gap-1 h-44">
                      {/* Accidents volume bar */}
                      <div
                        style={{ height: `${accHeight}px` }}
                        className="w-1/2 bg-amber-100 border-t-2 border-lane rounded-t-sm transition-all group-hover:bg-amber-200"
                      />
                      {/* Fatalities bar */}
                      <div
                        style={{ height: `${fatHeight}px` }}
                        className="w-1/2 bg-crit rounded-t-sm transition-all group-hover:brightness-110 flex items-start justify-center pt-0.5"
                      >
                        <span className="text-[9px] text-white font-bold hidden sm:inline">{m.fatalities}</span>
                      </div>
                    </div>
                    <span className="text-[11px] text-muted font-medium mt-1">{m.short}</span>
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between items-center text-[11px] text-muted pt-2 px-1">
              <span>Average: 401 crashes/mo</span>
              <span>Total recorded: 4,812</span>
            </div>
          </div>
        </div>

        {/* Hotspots by Risk Level (1 Col) */}
        <div className="bg-card border border-line rounded-card p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-[15px] font-semibold text-ink">Hotspots by risk level</h2>
              <span className="text-xs text-muted">{rd.total} total</span>
            </div>
            <p className="text-[12.5px] text-muted mb-5">
              Ranked according to deaths, crash volume, and severe injury weights.
            </p>

            {/* Risk bars */}
            <div className="space-y-4">
              {/* Critical */}
              <div>
                <div className="flex justify-between text-[13px] font-medium mb-1">
                  <span className="text-crit font-semibold flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-crit" />
                    Critical
                  </span>
                  <span className="font-bold text-ink tabular-nums">{rd.critical}</span>
                </div>
                <div className="w-full h-2.5 bg-paper rounded-full overflow-hidden">
                  <div
                    style={{ width: `${(rd.critical / rd.total) * 100}%` }}
                    className="h-full bg-crit rounded-full"
                  />
                </div>
              </div>

              {/* High */}
              <div>
                <div className="flex justify-between text-[13px] font-medium mb-1">
                  <span className="text-[#E2762B] font-semibold flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#E2762B]" />
                    High
                  </span>
                  <span className="font-bold text-ink tabular-nums">{rd.high}</span>
                </div>
                <div className="w-full h-2.5 bg-paper rounded-full overflow-hidden">
                  <div
                    style={{ width: `${(rd.high / rd.total) * 100}%` }}
                    className="h-full bg-[#E2762B] rounded-full"
                  />
                </div>
              </div>

              {/* Medium */}
              <div>
                <div className="flex justify-between text-[13px] font-medium mb-1">
                  <span className="text-[#8A6A00] font-semibold flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#E7B416]" />
                    Medium
                  </span>
                  <span className="font-bold text-ink tabular-nums">{rd.medium}</span>
                </div>
                <div className="w-full h-2.5 bg-paper rounded-full overflow-hidden">
                  <div
                    style={{ width: `${(rd.medium / rd.total) * 100}%` }}
                    className="h-full bg-[#E7B416] rounded-full"
                  />
                </div>
              </div>

              {/* Low */}
              <div>
                <div className="flex justify-between text-[13px] font-medium mb-1">
                  <span className="text-[#3E8E62] font-semibold flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#3E8E62]" />
                    Low
                  </span>
                  <span className="font-bold text-ink tabular-nums">{rd.low}</span>
                </div>
                <div className="w-full h-2.5 bg-paper rounded-full overflow-hidden">
                  <div
                    style={{ width: `${(rd.low / rd.total) * 100}%` }}
                    className="h-full bg-[#3E8E62] rounded-full"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 p-3 bg-paper rounded-btn border border-line text-[12.5px] text-muted flex items-center justify-between">
            <span>2 newly identified this week</span>
            <button
              onClick={() => navigate('/cases')}
              className="text-xs font-semibold text-[#8A6A00] hover:underline flex items-center gap-1"
            >
              View cases <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Row 3: Temporal Heat Grid + Priority Hotspots Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Temporal Heat Grid */}
        <div className="bg-card border border-line rounded-card p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-[15px] font-semibold text-ink">When accidents happen</h2>
              <span className="text-xs text-muted">7 days × 8 time blocks</span>
            </div>
            <p className="text-[12.5px] text-muted mb-4">{grid.peak_summary}</p>

            {/* Heat Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-center text-xs">
                <thead>
                  <tr>
                    <th className="py-1 text-left text-muted font-medium w-10">Day</th>
                    {grid.time_blocks.map((tb, idx) => (
                      <th key={idx} className="py-1 text-[11px] text-muted font-medium px-1">
                        {tb}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white">
                  {grid.days.map((day, dIdx) => (
                    <tr key={dIdx}>
                      <td className="text-left font-semibold text-ink text-[11.5px] py-1">{day}</td>
                      {grid.matrix[dIdx].map((val, tIdx) => (
                        <td key={tIdx} className="p-0.5">
                          <div
                            className={`w-full py-1.5 rounded text-[10.5px] tabular-nums transition ${getCellBg(val)}`}
                            title={`${day} ${grid.time_blocks[tIdx]}: ${val} crashes`}
                          >
                            {val}
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center justify-between pt-4 border-t border-line text-[11.5px] text-muted mt-3">
            <span>Crash density:</span>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-paper border border-line" />
                <span>Low</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-lane" />
                <span>Medium</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-crit" />
                <span>Peak</span>
              </div>
            </div>
          </div>
        </div>

        {/* Hotspots that need action first */}
        <div className="bg-card border border-line rounded-card p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-[15px] font-semibold text-ink">Hotspots that need action first</h2>
              <button
                onClick={() => navigate('/cases')}
                className="text-xs font-semibold text-[#8A6A00] hover:underline flex items-center gap-1"
              >
                View all 47 <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-[12.5px] text-muted mb-4">
              Ranked highest priority blackspots pending assignment or civil review.
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-[13px]">
                <thead>
                  <tr className="border-b border-line text-[11.5px] text-muted">
                    <th className="pb-2 font-medium">Rank</th>
                    <th className="pb-2 font-medium">Location</th>
                    <th className="pb-2 font-medium">Risk</th>
                    <th className="pb-2 font-medium text-center">Accidents</th>
                    <th className="pb-2 font-medium text-center">Deaths</th>
                    <th className="pb-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line/60">
                  {priorityHotspots.map((h, idx) => (
                    <tr
                      key={h.id || idx}
                      onClick={() => navigate(`/cases/${h.code}`)}
                      className="hover:bg-paper/80 cursor-pointer transition"
                    >
                      <td className="py-2.5 font-bold text-ink">#{idx + 1}</td>
                      <td className="py-2.5">
                        <div className="font-semibold text-ink leading-tight hover:text-[#8A6A00]">
                          {h.code}
                        </div>
                        <div className="text-[11.5px] text-muted truncate max-w-[180px]">
                          {h.name}
                        </div>
                      </td>
                      <td className="py-2.5">
                        <span className={`px-2 py-0.5 text-[11px] font-semibold rounded-full uppercase ${getRiskChip(h.risk_level)}`}>
                          {h.risk_level}
                        </span>
                      </td>
                      <td className="py-2.5 text-center tabular-nums font-medium text-ink">
                        {h.accidents_count}
                      </td>
                      <td className="py-2.5 text-center tabular-nums font-bold text-crit">
                        {h.fatalities_count}
                      </td>
                      <td className="py-2.5">
                        <div className="flex items-center gap-1.5 text-[12px] text-ink">
                          <span className={`w-2 h-2 rounded-full ${getStatusDot(h.status)}`} />
                          <span className="truncate max-w-[110px]">{h.status}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="pt-3 border-t border-line text-right">
            <span className="text-[11.5px] text-muted italic">
              AI-generated rankings · expert review needed before road alteration
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
