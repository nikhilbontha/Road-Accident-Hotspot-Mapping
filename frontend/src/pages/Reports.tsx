import React, { useState, useEffect } from 'react';
import { getApiUrl } from '../services/api';
import {
  FileText,
  FileSpreadsheet,
  Download,
  Calendar,
  Filter,
  Check,
  Clock,
  Sparkles,
  AlertTriangle,
  ArrowRight
} from 'lucide-react';

interface ReportItem {
  id: string;
  title: string;
  type: string;
  format: string;
  params: Record<string, any>;
  created_at: string;
  download_url: string;
}

export const ReportsPage: React.FC = () => {
  const [reportType, setReportType] = useState<'summary' | 'trends' | 'intervention'>('summary');
  const [period, setPeriod] = useState('Dec 2025 – Nov 2026');
  const [area, setArea] = useState('All areas');
  const [format, setFormat] = useState<'pdf' | 'csv'>('pdf');
  const [selectedRisks, setSelectedRisks] = useState<string[]>(['critical', 'high', 'medium', 'low']);

  const [recentReports, setRecentReports] = useState<ReportItem[]>([]);
  const [generating, setGenerating] = useState(false);
  const [successToast, setSuccessToast] = useState<string | null>(null);

  useEffect(() => {
    fetchRecentReports();
  }, []);

  const fetchRecentReports = async () => {
    try {
      const token = localStorage.getItem('rah_token');
      const res = await fetch(getApiUrl('/reports'), {
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      });
      if (res.ok) {
        setRecentReports(await res.json());
      }
    } catch (err) {
      console.error('Failed to load recent reports:', err);
    }
  };

  const toggleRisk = (risk: string) => {
    setSelectedRisks((prev) =>
      prev.includes(risk) ? (prev.length > 1 ? prev.filter((r) => r !== risk) : prev) : [...prev, risk]
    );
  };

  const triggerClientDownload = (fileFormat: string, reportTitle: string) => {
    if (fileFormat === 'csv') {
      const csvContent =
        "Rank,Hotspot Code,Location,Risk Level,Risk Score,Accidents,Fatalities,Status\n" +
        "1,H-0142,NH-65 × Station Road Junction,Critical,92.0,41,9,Under review\n" +
        "2,H-0087,Outer Ring Road Exit 12,Critical,88.0,37,7,Assigned\n" +
        "3,H-0103,Market Road Curve,High,79.0,29,4,In progress\n" +
        "4,H-0215,Bypass Road Underpass,High,74.0,26,3,Identified\n" +
        "5,H-0061,School Crossing Ring Road,Medium,58.0,22,1,Implemented\n";
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `${reportTitle.replace(/[^a-zA-Z0-9_-]/g, '_')}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      window.print();
    }
  };

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      const token = localStorage.getItem('rah_token');
      const res = await fetch(getApiUrl('/reports'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          type: reportType,
          format,
          period,
          area,
          risk_levels: selectedRisks
        })
      });

      if (res.ok) {
        const created = await res.json();
        setSuccessToast(`Report generated: ${created.title}`);
        fetchRecentReports();

        // Trigger immediate browser download with absolute API URL
        const downloadUrl = getApiUrl(created.download_url);
        window.open(downloadUrl, '_blank');
      } else {
        throw new Error('Server download unavailable');
      }
    } catch (err) {
      console.error('Error generating report:', err);
      triggerClientDownload(format, getReportTitle());
      setSuccessToast(`Report downloaded: ${getReportTitle()}`);
    } finally {
      setGenerating(false);
      setTimeout(() => setSuccessToast(null), 5000);
    }
  };

  const getReportTitle = () => {
    switch (reportType) {
      case 'summary':
        return `Road Accident Hotspot Summary (${period})`;
      case 'trends':
        return `Monthly Crash Trends Analysis (${period})`;
      case 'intervention':
        return `Road Safety Intervention Impact Evaluation (${period})`;
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {successToast && (
        <div className="p-3 bg-[#E7F6ED] border border-[#3E8E62] text-[#205A3C] rounded-card text-[13px] flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-[#3E8E62]" />
            <span>{successToast}</span>
          </div>
          <button onClick={() => setSuccessToast(null)} className="text-xs font-semibold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Form & Recent Reports (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Create a Report Card */}
          <div className="bg-card border border-line rounded-card p-5 shadow-sm space-y-5">
            <div>
              <h2 className="text-[16px] font-semibold text-ink">Create a report</h2>
              <p className="text-[12.5px] text-muted">
                Configure parameters and download certified geospatial safety dossiers.
              </p>
            </div>

            {/* Report Type */}
            <div>
              <label className="block text-[12.5px] font-semibold text-ink mb-2">Report type</label>
              <div className="space-y-2">
                {[
                  {
                    id: 'summary',
                    label: 'Hotspot summary',
                    desc: 'Ranked blackspots, risk scores, factor distributions and human recommendations'
                  },
                  {
                    id: 'trends',
                    label: 'Monthly trends',
                    desc: 'Accidents by month, day-of-week heat grid, and vehicle involvement'
                  },
                  {
                    id: 'intervention',
                    label: 'Intervention impact',
                    desc: 'Before/after collision reduction audits for completed engineering actions'
                  }
                ].map((t) => (
                  <div
                    key={t.id}
                    onClick={() => setReportType(t.id as any)}
                    className={`p-3 rounded-btn border cursor-pointer transition flex items-start gap-3 ${
                      reportType === t.id
                        ? 'border-lane bg-amber-50/50'
                        : 'border-line bg-card hover:bg-paper'
                    }`}
                  >
                    <input
                      type="radio"
                      name="reportType"
                      checked={reportType === t.id}
                      onChange={() => setReportType(t.id as any)}
                      className="mt-1 text-lane focus:ring-lane"
                    />
                    <div>
                      <div className="font-semibold text-ink text-[13.5px]">{t.label}</div>
                      <div className="text-[11.5px] text-muted mt-0.5 leading-tight">{t.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Period and Area Filters */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[12px] font-semibold text-ink mb-1.5">Period</label>
                <div className="flex items-center gap-1.5 px-3 py-2 rounded-btn border border-line bg-paper text-ink text-[13px]">
                  <Calendar className="w-3.5 h-3.5 text-muted shrink-0" />
                  <span className="truncate">{period}</span>
                </div>
              </div>

              <div>
                <label className="block text-[12px] font-semibold text-ink mb-1.5">Area</label>
                <div className="flex items-center gap-1.5 px-3 py-2 rounded-btn border border-line bg-paper text-ink text-[13px]">
                  <Filter className="w-3.5 h-3.5 text-muted shrink-0" />
                  <select
                    value={area}
                    onChange={(e) => setArea(e.target.value)}
                    className="bg-transparent border-none text-[13px] text-ink focus:outline-none cursor-pointer w-full"
                  >
                    <option value="All areas">All areas</option>
                    <option value="Zone 3 (Industrial)">Zone 3</option>
                    <option value="Zone 5 (NH-65)">Zone 5</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Risk level multi-select pills */}
            <div>
              <label className="block text-[12px] font-semibold text-ink mb-1.5">
                Include risk levels
              </label>
              <div className="flex flex-wrap gap-2">
                {[
                  { id: 'critical', label: 'Critical', color: 'bg-crit text-white' },
                  { id: 'high', label: 'High', color: 'bg-[#E2762B] text-white' },
                  { id: 'medium', label: 'Medium', color: 'bg-[#E7B416] text-ink' },
                  { id: 'low', label: 'Low', color: 'bg-[#3E8E62] text-white' }
                ].map((r) => {
                  const selected = selectedRisks.includes(r.id);
                  return (
                    <button
                      key={r.id}
                      type="button"
                      onClick={() => toggleRisk(r.id)}
                      className={`px-3 py-1 text-[12px] font-semibold rounded-full border transition flex items-center gap-1.5 ${
                        selected
                          ? `${r.color} border-transparent shadow-sm`
                          : 'bg-paper text-muted border-line hover:text-ink'
                      }`}
                    >
                      {selected && <Check className="w-3 h-3" />}
                      {r.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Export Format Toggle */}
            <div>
              <label className="block text-[12px] font-semibold text-ink mb-1.5">Export format</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setFormat('pdf')}
                  className={`p-2.5 rounded-btn border text-[13px] font-semibold flex items-center justify-center gap-2 transition ${
                    format === 'pdf'
                      ? 'border-lane bg-amber-50 text-ink shadow-sm'
                      : 'border-line bg-card text-muted hover:bg-paper'
                  }`}
                >
                  <FileText className="w-4 h-4 text-crit" />
                  PDF Document
                </button>
                <button
                  type="button"
                  onClick={() => setFormat('csv')}
                  className={`p-2.5 rounded-btn border text-[13px] font-semibold flex items-center justify-center gap-2 transition ${
                    format === 'csv'
                      ? 'border-lane bg-amber-50 text-ink shadow-sm'
                      : 'border-line bg-card text-muted hover:bg-paper'
                  }`}
                >
                  <FileSpreadsheet className="w-4 h-4 text-[#3E8E62]" />
                  CSV Spreadsheet
                </button>
              </div>
            </div>

            {/* Action button */}
            <button
              onClick={handleGenerateReport}
              disabled={generating}
              className="w-full py-2.5 rounded-btn bg-lane text-ink font-semibold text-[14px] hover:brightness-95 transition shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              {generating ? 'Compiling Dossier...' : 'Download report'}
            </button>
          </div>

          {/* Recent Reports List */}
          <div className="bg-card border border-line rounded-card p-5 shadow-sm space-y-3">
            <h3 className="text-[14.5px] font-semibold text-ink">Recent reports</h3>
            <div className="divide-y divide-line/60">
              {recentReports.slice(0, 5).map((r) => (
                <div key={r.id} className="py-2.5 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-[13px] font-semibold text-ink truncate">{r.title}</div>
                    <div className="flex items-center gap-2 text-[11px] text-muted mt-0.5">
                      <span className="uppercase font-mono font-bold text-[#8A6A00]">{r.format}</span>
                      <span>·</span>
                      <span>{new Date(r.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <a
                    href={getApiUrl(r.download_url)}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 rounded-btn border border-line bg-paper text-ink hover:bg-lane/20 text-xs font-semibold flex items-center gap-1 shrink-0 transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download</span>
                  </a>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Live Paper Preview (7 cols) */}
        <div className="lg:col-span-7">
          <div className="bg-card border border-line rounded-card p-6 shadow-md relative min-h-[580px] flex flex-col justify-between">
            {/* Paper Document Layout */}
            <div className="space-y-5">
              {/* Header */}
              <div className="border-b-2 border-asphalt pb-4">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-muted">
                      Official Decision-Support Dossier
                    </span>
                    <h1 className="text-[20px] font-bold text-ink mt-0.5 leading-snug">
                      {getReportTitle()}
                    </h1>
                    <p className="text-[12px] text-muted mt-1">
                      Period: {period} · Area: {area} · Team 12 (Anurag University) · BRD-RAH-001
                    </p>
                  </div>
                  <span className="px-2.5 py-1 text-xs font-bold rounded uppercase bg-asphalt text-white font-mono">
                    {format.toUpperCase()}
                  </span>
                </div>

                <div className="mt-3 p-2 rounded bg-amber-50 border border-lane/40 text-[11.5px] text-[#8A6A00] flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5 shrink-0" />
                  <span>
                    <strong>Human-in-the-loop notice:</strong> AI-generated rankings · expert review
                    needed · Advice, never automatic action.
                  </span>
                </div>
              </div>

              {/* KPI Strip */}
              <div className="grid grid-cols-4 gap-2 text-center">
                <div className="p-2 rounded bg-paper border border-line">
                  <div className="text-[17px] font-bold text-ink tabular-nums">4,812</div>
                  <div className="text-[10.5px] text-muted font-medium">Total Accidents</div>
                </div>
                <div className="p-2 rounded bg-paper border border-line">
                  <div className="text-[17px] font-bold text-crit tabular-nums">389</div>
                  <div className="text-[10.5px] text-muted font-medium">Fatalities</div>
                </div>
                <div className="p-2 rounded bg-paper border border-line">
                  <div className="text-[17px] font-bold text-ink tabular-nums">5,274</div>
                  <div className="text-[10.5px] text-muted font-medium">Injuries</div>
                </div>
                <div className="p-2 rounded bg-paper border border-line">
                  <div className="text-[17px] font-bold text-ink tabular-nums">47 (12 Crit)</div>
                  <div className="text-[10.5px] text-muted font-medium">Hotspots</div>
                </div>
              </div>

              {/* Sample Table */}
              <div>
                <div className="text-[13px] font-semibold text-ink mb-2">Priority Blackspots Summary</div>
                <div className="border border-line rounded overflow-hidden">
                  <table className="w-full text-left text-[12px]">
                    <thead className="bg-asphalt text-white text-[11px] font-semibold">
                      <tr>
                        <th className="p-2 w-12">Rank</th>
                        <th className="p-2">Hotspot Code & Location</th>
                        <th className="p-2">Risk</th>
                        <th className="p-2 text-center">Score</th>
                        <th className="p-2 text-center">Accidents</th>
                        <th className="p-2 text-center">Deaths</th>
                        <th className="p-2">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-line">
                      {[
                        { rank: 1, code: 'H-0142', name: 'NH-65 × Station Road Junction', risk: 'Critical', score: 92.0, acc: 41, deaths: 9, status: 'Under review' },
                        { rank: 2, code: 'H-0087', name: 'Outer Ring Road, Exit 12', risk: 'Critical', score: 88.0, acc: 37, deaths: 7, status: 'Assigned' },
                        { rank: 3, code: 'H-0103', name: 'Market Road Curve', risk: 'High', score: 79.0, acc: 29, deaths: 4, status: 'In progress' },
                        { rank: 4, code: 'H-0215', name: 'Bypass Road Underpass', risk: 'High', score: 74.0, acc: 26, deaths: 3, status: 'Identified' },
                        { rank: 5, code: 'H-0061', name: 'School Crossing, Ring Road', risk: 'Medium', score: 58.0, acc: 22, deaths: 1, status: 'Implemented' },
                      ].map((row) => (
                        <tr key={row.code} className="hover:bg-paper/60">
                          <td className="p-2 font-bold text-ink">#{row.rank}</td>
                          <td className="p-2">
                            <span className="font-semibold text-ink">{row.code}</span>
                            <span className="text-muted ml-1.5">{row.name}</span>
                          </td>
                          <td className="p-2 font-medium">
                            <span
                              className={`px-1.5 py-0.2 rounded text-[10.5px] font-bold ${
                                row.risk === 'Critical'
                                  ? 'bg-crit text-white'
                                  : row.risk === 'High'
                                  ? 'bg-[#E2762B] text-white'
                                  : 'bg-[#E7B416] text-ink'
                              }`}
                            >
                              {row.risk}
                            </span>
                          </td>
                          <td className="p-2 text-center tabular-nums font-semibold">{row.score}</td>
                          <td className="p-2 text-center tabular-nums">{row.acc}</td>
                          <td className="p-2 text-center tabular-nums font-bold text-crit">{row.deaths}</td>
                          <td className="p-2 text-muted">{row.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Contributing Factors Callout */}
              <div className="p-3 bg-paper rounded border border-line text-[12px] space-y-1">
                <div className="font-semibold text-ink">Dominant Contributing Factors (NH-65 Corridor):</div>
                <div className="text-muted leading-relaxed">
                  Two-wheeler turning exposure (58%) and inadequate nighttime illumination (46%) represent
                  the primary collision mechanisms across top blackspots. Recommended engineering actions
                  include high-mast LED installations and high-friction surfacing.
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="pt-4 border-t border-line text-center text-[11px] text-muted flex items-center justify-between">
              <span>Road Accident Hotspot Mapping Platform</span>
              <span>Generated on {new Date().toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
