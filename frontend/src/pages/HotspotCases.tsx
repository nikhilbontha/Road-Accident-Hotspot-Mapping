import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FolderKanban,
  Search,
  Filter,
  Download,
  ExternalLink,
  UserPlus,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { apiRequest } from '../services/api';

interface CaseItem {
  id: string;
  code: string;
  name: string;
  roadName: string;
  riskScore: number;
  riskLevel: 'critical' | 'high' | 'medium' | 'low';
  accidentsCount: number;
  fatalities: number;
  assignedTo?: string;
  status: string;
  updatedAt: string;
}

export const HotspotCasesPage: React.FC = () => {
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<string>('All');
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const [assigneeFilter, setAssigneeFilter] = useState('all');

  // Reference Tab counts matching Page_07_Hotspot_Cases.png
  const tabCounts: Record<string, number> = {
    All: 47,
    Identified: 9,
    'Under review': 11,
    Assigned: 8,
    'Action in progress': 11,
    Implemented: 6,
    Closed: 2,
  };

  const initialCases: CaseItem[] = [
    {
      id: 'h-1',
      code: 'H-0142',
      name: 'NH-65 × Station Road Junction',
      roadName: 'National Highway 65',
      riskScore: 92,
      riskLevel: 'critical',
      accidentsCount: 41,
      fatalities: 9,
      status: 'Under review',
      updatedAt: 'Today, 2:40 pm',
    },
    {
      id: 'h-2',
      code: 'H-0087',
      name: 'Outer Ring Road, Exit 12',
      roadName: 'Outer Ring Road',
      riskScore: 88,
      riskLevel: 'critical',
      accidentsCount: 37,
      fatalities: 7,
      assignedTo: 'Ravi Kumar',
      status: 'Assigned',
      updatedAt: 'Yesterday',
    },
    {
      id: 'h-3',
      code: 'H-0103',
      name: 'Market Road Curve',
      roadName: 'Market Road',
      riskScore: 79,
      riskLevel: 'high',
      accidentsCount: 29,
      fatalities: 4,
      assignedTo: 'Sana Fatima',
      status: 'Action in progress',
      updatedAt: '2 days ago',
    },
    {
      id: 'h-4',
      code: 'H-0215',
      name: 'Bypass Road Underpass',
      roadName: 'Bypass Road',
      riskScore: 74,
      riskLevel: 'high',
      accidentsCount: 26,
      fatalities: 3,
      status: 'Identified',
      updatedAt: '18 Nov 2026',
    },
    {
      id: 'h-5',
      code: 'H-0061',
      name: 'School Crossing, Ring Road',
      roadName: 'Ring Road',
      riskScore: 58,
      riskLevel: 'medium',
      accidentsCount: 22,
      fatalities: 1,
      assignedTo: 'Meera Iyer',
      status: 'Implemented',
      updatedAt: '14 Nov 2026',
    },
    {
      id: 'h-6',
      code: 'H-0178',
      name: 'Lake View Roundabout',
      roadName: 'Lake View Road',
      riskScore: 54,
      riskLevel: 'medium',
      accidentsCount: 20,
      fatalities: 1,
      status: 'Identified',
      updatedAt: '10 Nov 2026',
    },
    {
      id: 'h-7',
      code: 'H-0039',
      name: 'Industrial Area Gate 2',
      roadName: 'Industrial Corridor',
      riskScore: 51,
      riskLevel: 'medium',
      accidentsCount: 18,
      fatalities: 1,
      assignedTo: 'Imran Sheikh',
      status: 'Action in progress',
      updatedAt: '08 Nov 2026',
    },
    {
      id: 'h-8',
      code: 'H-0124',
      name: 'Old Town Bridge Approach',
      roadName: 'Old Town Main Road',
      riskScore: 38,
      riskLevel: 'low',
      accidentsCount: 14,
      fatalities: 0,
      status: 'Closed',
      updatedAt: '02 Nov 2026',
    },
    {
      id: 'h-9',
      code: 'H-0196',
      name: 'Canal Road Bend',
      roadName: 'Canal Road',
      riskScore: 34,
      riskLevel: 'low',
      accidentsCount: 11,
      fatalities: 0,
      status: 'Closed',
      updatedAt: '28 Oct 2026',
    },
    {
      id: 'h-10',
      code: 'H-0052',
      name: 'Railway Station Crossing',
      roadName: 'Station Road',
      riskScore: 31,
      riskLevel: 'low',
      accidentsCount: 9,
      fatalities: 0,
      status: 'Identified',
      updatedAt: '25 Oct 2026',
    },
  ];

  const [cases, setCases] = useState<CaseItem[]>(initialCases);

  useEffect(() => {
    // Attempt backend fetch
    apiRequest('/hotspots')
      .then((res) => {
        if (res.hotspots && res.hotspots.length > 0) {
          setCases(res.hotspots);
        }
      })
      .catch(() => {});
  }, []);

  const filteredCases = cases.filter((c) => {
    const matchesTab = activeTab === 'All' || c.status.toLowerCase() === activeTab.toLowerCase();
    const matchesSearch =
      c.code.toLowerCase().includes(search.toLowerCase()) ||
      c.name.toLowerCase().includes(search.toLowerCase());
    const matchesRisk = riskFilter === 'all' || c.riskLevel === riskFilter;
    const matchesAssignee =
      assigneeFilter === 'all' ||
      (assigneeFilter === 'unassigned' && !c.assignedTo) ||
      (c.assignedTo && c.assignedTo.toLowerCase().includes(assigneeFilter.toLowerCase()));
    return matchesTab && matchesSearch && matchesRisk && matchesAssignee;
  });

  const getStatusColor = (st: string) => {
    switch (st) {
      case 'Identified':
        return 'bg-status-identified';
      case 'Under review':
        return 'bg-status-review';
      case 'Assigned':
        return 'bg-status-assigned';
      case 'Action in progress':
        return 'bg-status-progress';
      case 'Implemented':
        return 'bg-status-implemented';
      case 'Closed':
        return 'bg-status-closed';
      default:
        return 'bg-muted';
    }
  };

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'critical':
        return 'bg-crit text-white';
      case 'high':
        return 'bg-high text-white';
      case 'medium':
        return 'bg-med text-ink';
      case 'low':
        return 'bg-low text-white';
      default:
        return 'bg-muted text-white';
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Status Tabs with Counts (Page_07_Hotspot_Cases.png) */}
      <div className="flex border-b border-line overflow-x-auto gap-2">
        {Object.entries(tabCounts).map(([tabName, count]) => {
          const isActive = activeTab === tabName;
          return (
            <button
              key={tabName}
              onClick={() => setActiveTab(tabName)}
              className={`pb-3 px-3.5 text-[13.5px] font-medium whitespace-nowrap transition-colors border-b-2 flex items-center gap-2 ${
                isActive
                  ? 'border-lane text-ink font-semibold'
                  : 'border-transparent text-muted hover:text-ink'
              }`}
            >
              <span>{tabName}</span>
              <span
                className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                  isActive ? 'bg-lane/25 text-ink' : 'bg-paper text-muted'
                }`}
              >
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* 2. Search & Filter Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-muted absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search location, road or hotspot ID (e.g. H-0142)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3.5 py-2 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:outline-none focus:ring-2 focus:ring-lane"
          />
        </div>

        {/* Filters & Export */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Risk Level Filter */}
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13px]"
          >
            <option value="all">Risk: All levels</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          {/* Assigned To Filter */}
          <select
            value={assigneeFilter}
            onChange={(e) => setAssigneeFilter(e.target.value)}
            className="px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13px]"
          >
            <option value="all">Assigned to: Anyone</option>
            <option value="unassigned">Unassigned only</option>
            <option value="ravi">Ravi Kumar</option>
            <option value="sana">Sana Fatima</option>
            <option value="meera">Meera Iyer</option>
          </select>

          {/* Export Action */}
          <button
            onClick={() => alert('Exporting cases list to CSV...')}
            className="px-4 py-2 rounded-btn border border-line bg-card text-ink text-[13px] font-medium hover:bg-paper transition-colors flex items-center gap-1.5 ml-2"
          >
            <Download className="w-4 h-4 text-muted" />
            <span>Export list</span>
          </button>
        </div>
      </div>

      {/* 3. Hotspot Cases Table */}
      <div className="bg-card border border-line rounded-card overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-line bg-paper/60 text-muted text-[12.5px] font-medium">
                <th className="py-3 px-4 w-24">ID</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4">Risk</th>
                <th className="py-3 px-4">Score</th>
                <th className="py-3 px-4">Accidents & Deaths</th>
                <th className="py-3 px-4">Assigned to</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line text-[13.3px]">
              {filteredCases.map((c) => (
                <tr
                  key={c.code}
                  onClick={() => navigate(`/cases/${c.code}`)}
                  className="hover:bg-paper/40 cursor-pointer transition-colors"
                >
                  <td className="py-3.5 px-4 font-mono font-semibold text-ink text-[13px]">
                    {c.code}
                  </td>
                  <td className="py-3.5 px-4 font-medium text-ink">
                    <span className="hover:underline">{c.name}</span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`inline-block px-2.5 py-0.5 rounded-full text-[11.5px] font-bold uppercase tracking-wider ${getRiskBadge(
                        c.riskLevel
                      )}`}
                    >
                      {c.riskLevel}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-mono font-semibold text-ink">
                    {c.riskScore}
                  </td>
                  <td className="py-3.5 px-4 text-muted">
                    <span className="font-semibold text-ink">{c.accidentsCount}</span> crashes ·{' '}
                    <span className="text-crit font-semibold">{c.fatalities}</span> deaths
                  </td>
                  <td className="py-3.5 px-4">
                    {c.assignedTo ? (
                      <span className="text-ink font-medium">{c.assignedTo}</span>
                    ) : (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          alert(`Assign official to ${c.code}`);
                        }}
                        className="text-xs font-semibold text-[#8A6A00] hover:underline flex items-center gap-1"
                      >
                        <UserPlus className="w-3.5 h-3.5" />
                        <span>Assign</span>
                      </button>
                    )}
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${getStatusColor(c.status)}`} />
                      <span className="text-[12.5px]">{c.status}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-right text-muted text-[12px]">
                    {c.updatedAt}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="px-4 py-3 border-t border-line bg-paper/30 flex items-center justify-between text-xs text-muted">
          <span>Showing 10 of 47 hotspots</span>
          <div className="flex items-center gap-1">
            <button className="p-1 rounded border border-line bg-card disabled:opacity-40" disabled>
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-2 font-medium text-ink">Page 1 of 5</span>
            <button className="p-1 rounded border border-line bg-card hover:bg-paper">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
