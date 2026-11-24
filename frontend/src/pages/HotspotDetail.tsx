import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Clock,
  Sparkles,
  ShieldCheck,
  Send,
  AlertTriangle,
  History,
  TrendingDown,
  ChevronRight,
  UserCheck,
} from 'lucide-react';

export const HotspotDetailPage: React.FC = () => {
  const { code } = useParams();
  const navigate = useNavigate();

  const [activeStep, setActiveStep] = useState<number>(2); // 1: Identified, 2: Under review, 3: Assigned, 4: Progress, 5: Implemented, 6: Closed
  const [selectedAssignee, setSelectedAssignee] = useState<string>('Ravi Kumar');
  const [comments, setComments] = useState<Array<{ author: string; text: string; date: string }>>([
    {
      author: 'Asha Reddy (Analyst)',
      text: 'Verified nighttime cluster. 23 of 41 incidents occurred between 6pm and midnight.',
      date: 'Today, 11:20 am',
    },
    {
      author: 'System',
      text: 'Hotspot H-0142 identified by analysis run RUN-20261124 with Critical risk score 92.',
      date: '24 Nov 2026, 09:15 am',
    },
  ]);
  const [newComment, setNewComment] = useState('');
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [overrideReason, setOverrideReason] = useState('');
  const [currentRisk, setCurrentRisk] = useState<'critical' | 'high' | 'medium' | 'low'>('critical');
  const [riskOverridden, setRiskOverridden] = useState(false);

  // Reference data for H-0142
  const hotspotData = {
    code: code || 'H-0142',
    name: 'NH-65 × Station Road Junction',
    roadName: 'National Highway 65',
    area: 'Central Zone',
    riskScore: 92,
    scoreBreakdown: { deaths: 41, frequency: 32, injuries: 19 },
    accidentsCount: 41,
    fatalities: 9,
    injured: 63,
    peakTime: '6–9 pm, Fri–Sat',
    settings: '250 m radius · 5+ accidents · 12 months',
    timeDistribution: [
      { label: '12–3a', val: 3 },
      { label: '3–6a', val: 1 },
      { label: '6–9a', val: 3 },
      { label: '9–12p', val: 2 },
      { label: '12–3p', val: 3 },
      { label: '3–6p', val: 6 },
      { label: '6–9p', val: 15, peak: true },
      { label: '9–12a', val: 8, peak: true },
    ],
    factors: [
      { label: 'Two-wheelers involved', percent: 58 },
      { label: 'Poor lighting at night', percent: 46 },
      { label: 'Overspeeding on approach', percent: 34 },
      { label: 'Wet road / poor drainage', percent: 21 },
      { label: 'No pedestrian crossing', percent: 18 },
    ],
    recommendations: [
      {
        title: 'High-mast illumination & junction street lighting',
        factor: 'Addresses poor lighting at night',
        evidence: '23 of 41 crashes happened between 6 pm and midnight',
        confidence: 'High',
      },
      {
        title: 'Warning signage, radar speed display & rumble strips',
        factor: 'Addresses overspeeding on approach',
        evidence: '34% of crashes involved overspeeding on junction approach',
        confidence: 'Medium',
      },
      {
        title: 'Protected turning lane & segregated motorcycle bay',
        factor: 'Addresses two-wheelers involved',
        evidence: '58% of vehicles involved in conflicts were two-wheelers',
        confidence: 'Medium',
      },
      {
        title: 'Marked pedestrian crossing with central refuge island',
        factor: 'Addresses pedestrian exposure',
        evidence: 'Pedestrian conflicts recorded without crossing infrastructure',
        confidence: 'Low',
      },
    ],
  };

  const lifecycleSteps = [
    'Identified',
    'Under review',
    'Assigned',
    'Action in progress',
    'Implemented',
    'Closed',
  ];

  const handleAddComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setComments([
      {
        author: 'Current User',
        text: newComment.trim(),
        date: 'Just now',
      },
      ...comments,
    ]);
    setNewComment('');
  };

  const handleSaveOverride = (e: React.FormEvent) => {
    e.preventDefault();
    if (!overrideReason.trim()) return;
    setRiskOverridden(true);
    setShowOverrideModal(false);
    setComments([
      {
        author: 'Dr. Kiran Rao (Admin)',
        text: `Risk level overridden to ${currentRisk.toUpperCase()}. Reason: ${overrideReason}`,
        date: 'Just now',
      },
      ...comments,
    ]);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Back button and Header */}
      <div>
        <button
          onClick={() => navigate('/cases')}
          className="text-xs font-semibold text-muted hover:text-ink flex items-center gap-1 mb-2"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Hotspot Cases</span>
        </button>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-ink">
              Hotspot {hotspotData.code}: {hotspotData.name}
            </h1>
            <span
              className={`px-3 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider text-white ${
                currentRisk === 'critical'
                  ? 'bg-crit'
                  : currentRisk === 'high'
                  ? 'bg-high'
                  : 'bg-med text-ink'
              }`}
            >
              {currentRisk}
            </span>
            {riskOverridden && (
              <span className="text-[11px] font-medium text-warn-text bg-warn-bg border border-[#FDE68A] px-2 py-0.5 rounded">
                Manually Overridden
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowOverrideModal(true)}
              className="px-3 py-1.5 rounded-btn border border-line bg-card text-ink text-[12.5px] font-medium hover:bg-paper"
            >
              Change risk level
            </button>
            <button
              onClick={() => navigate('/map')}
              className="px-3.5 py-1.5 rounded-btn bg-lane text-ink font-semibold text-[12.5px] hover:brightness-105"
            >
              View on map
            </button>
          </div>
        </div>
      </div>

      {/* 6-Step Lifecycle Stepper (Page_08_Hotspot_Detail.png) */}
      <div className="bg-card border border-line rounded-card p-4 shadow-sm">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
          {lifecycleSteps.map((stepName, i) => {
            const stepNum = i + 1;
            const isCurrent = activeStep === stepNum;
            const isCompleted = stepNum < activeStep;
            return (
              <button
                key={stepName}
                onClick={() => setActiveStep(stepNum)}
                className={`p-2.5 rounded-btn text-left transition-all border ${
                  isCurrent
                    ? 'bg-lane text-ink border-lane font-semibold shadow-sm'
                    : isCompleted
                    ? 'bg-paper text-ink border-line'
                    : 'bg-card text-muted border-line opacity-60 hover:opacity-100'
                }`}
              >
                <div className="text-[11px] uppercase tracking-wider opacity-75">
                  Step {stepNum}
                </div>
                <div className="text-[13px] font-medium truncate">{stepName}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Key Metrics Ribbon */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-card border border-line rounded-card p-3.5 shadow-sm">
          <span className="text-muted text-[11.5px] block font-medium">Risk score</span>
          <span className="text-2xl font-bold text-ink font-mono">
            {hotspotData.riskScore} <span className="text-xs font-normal text-muted">/ 100</span>
          </span>
        </div>
        <div className="bg-card border border-line rounded-card p-3.5 shadow-sm">
          <span className="text-muted text-[11.5px] block font-medium">Accidents</span>
          <span className="text-2xl font-bold text-ink font-mono">{hotspotData.accidentsCount}</span>
        </div>
        <div className="bg-card border border-line rounded-card p-3.5 shadow-sm">
          <span className="text-muted text-[11.5px] block font-medium">Deaths</span>
          <span className="text-2xl font-bold text-crit font-mono">{hotspotData.fatalities}</span>
        </div>
        <div className="bg-card border border-line rounded-card p-3.5 shadow-sm">
          <span className="text-muted text-[11.5px] block font-medium">Injured</span>
          <span className="text-2xl font-bold text-ink font-mono">{hotspotData.injured}</span>
        </div>
        <div className="bg-card border border-line rounded-card p-3.5 shadow-sm col-span-2 sm:col-span-1">
          <span className="text-muted text-[11.5px] block font-medium">Peak time</span>
          <span className="text-[14px] font-semibold text-ink leading-tight block mt-1">
            {hotspotData.peakTime}
          </span>
        </div>
        <div className="bg-card border border-line rounded-card p-3.5 shadow-sm col-span-2 sm:col-span-1">
          <span className="text-muted text-[11.5px] block font-medium">Analysis settings</span>
          <span className="text-[12px] text-muted block mt-1 leading-snug">
            {hotspotData.settings}
          </span>
        </div>
      </div>

      {/* Two Column Layout: Charts (Left 7 cols) & Actions/Tracking (Right 5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Analytics Visualizations */}
        <div className="lg:col-span-7 space-y-6">
          {/* 1. Accidents by Time of Day (8-Bar Chart matching Page_08) */}
          <div className="bg-card border border-line rounded-card p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-ink text-[15px]">Accidents by time of day</h3>
              <span className="text-xs text-muted">8 blocks of 3 hours</span>
            </div>

            <div className="h-44 flex items-end justify-between gap-2 pt-6 pb-2 px-2 border-b border-line">
              {hotspotData.timeDistribution.map((bar, i) => {
                const heightPercent = (bar.val / 16) * 100;
                return (
                  <div key={bar.label} className="flex-1 flex flex-col items-center h-full justify-end group">
                    <span className="text-[11px] font-bold text-ink mb-1 group-hover:scale-110 transition-transform">
                      {bar.val}
                    </span>
                    <div
                      style={{ height: `${heightPercent}%` }}
                      className={`w-full max-w-[34px] rounded-t transition-all ${
                        bar.peak ? 'bg-asphalt' : 'bg-[#D2D6CE]'
                      }`}
                    />
                    <span className="text-[11px] text-muted mt-2 font-mono">{bar.label}</span>
                  </div>
                );
              })}
            </div>
            <div className="text-[12px] text-muted flex items-center justify-between">
              <span>Dark bars highlight evening peak concentration (6 pm – 12 am).</span>
              <span className="font-semibold text-ink">56% of total crashes</span>
            </div>
          </div>

          {/* 2. Contributing Factors Horizontal Bars */}
          <div className="bg-card border border-line rounded-card p-5 shadow-sm space-y-3.5">
            <h3 className="font-semibold text-ink text-[15px]">
              What contributed to these accidents
            </h3>

            <div className="space-y-3">
              {hotspotData.factors.map((f) => (
                <div key={f.label} className="space-y-1">
                  <div className="flex justify-between text-[13px]">
                    <span className="text-ink font-medium">{f.label}</span>
                    <span className="font-semibold font-mono text-ink">{f.percent}%</span>
                  </div>
                  <div className="h-2.5 rounded-full bg-paper overflow-hidden border border-line">
                    <div
                      style={{ width: `${f.percent}%` }}
                      className={`h-full rounded-full ${
                        f.percent > 40 ? 'bg-asphalt' : 'bg-lane'
                      }`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 3. Why the Score is 92 (Stacked Breakdown Bar) */}
          <div className="bg-card border border-line rounded-card p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-ink text-[15px]">Why the score is 92</h3>
              <span className="text-xs text-muted font-mono">100 pt normalized scale</span>
            </div>

            {/* Stacked bar */}
            <div className="h-4 rounded-full overflow-hidden flex border border-line">
              <div
                style={{ width: '45%' }}
                className="bg-crit h-full"
                title="41 points from deaths"
              />
              <div
                style={{ width: '35%' }}
                className="bg-high h-full"
                title="32 points from frequency"
              />
              <div
                style={{ width: '20%' }}
                className="bg-med h-full"
                title="19 points from injuries"
              />
            </div>

            <div className="flex flex-wrap items-center justify-between text-[12.5px] text-muted pt-1">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-crit" />
                <strong className="text-ink">41</strong> from deaths
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-high" />
                <strong className="text-ink">32</strong> from crash frequency
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-med" />
                <strong className="text-ink">19</strong> from injuries
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Recommendations & Case Tracking */}
        <div className="lg:col-span-5 space-y-6">
          {/* 1. Suggested Actions Card (with mandatory AI-generated label) */}
          <div className="bg-card border border-line rounded-card p-5 shadow-sm space-y-3.5">
            <div className="flex items-center justify-between pb-2 border-b border-line">
              <h3 className="font-semibold text-ink text-[15px]">Suggested actions</h3>
              <span className="text-[11px] font-semibold text-muted bg-paper px-2 py-0.5 rounded border border-line">
                AI-generated · expert review needed
              </span>
            </div>

            <div className="space-y-3">
              {hotspotData.recommendations.map((rec) => (
                <div
                  key={rec.title}
                  className="p-3.5 rounded-btn border border-line bg-paper/60 hover:border-lane transition-colors space-y-1.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold text-ink text-[13.5px] leading-snug">
                      {rec.title}
                    </h4>
                    <span
                      className={`text-[10.5px] font-bold px-2 py-0.5 rounded-full uppercase shrink-0 ${
                        rec.confidence === 'High'
                          ? 'bg-[#DEF7EC] text-[#03543F]'
                          : rec.confidence === 'Medium'
                          ? 'bg-lane/20 text-ink'
                          : 'bg-paper text-muted border border-line'
                      }`}
                    >
                      {rec.confidence} confidence
                    </span>
                  </div>
                  <div className="text-[12px] text-[#8A6A00] font-medium">{rec.factor}</div>
                  <div className="text-[12px] text-muted leading-relaxed">
                    Evidence: {rec.evidence}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 2. Before/After Safety Intervention Impact */}
          <div className="bg-card border border-line rounded-card p-5 shadow-sm space-y-3">
            <div className="flex items-center gap-2">
              <TrendingDown className="w-4 h-4 text-status-implemented" />
              <h3 className="font-semibold text-ink text-[14.5px]">
                Before / After Safety Evaluation
              </h3>
            </div>
            <div className="p-3 bg-paper rounded-btn border border-line text-[12.5px] space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-muted">Intervention:</span>
                <span className="font-semibold text-ink">Signal + High-mast lighting</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted">Impact (6 mo window):</span>
                <span className="font-bold text-status-implemented font-mono">
                  14 → 9 crashes (-35.7%)
                </span>
              </div>
              <p className="text-[11px] text-muted pt-1 border-t border-line">
                Short observation windows are indicative only. Longer evaluation periods needed for statistical certainty.
              </p>
            </div>
          </div>

          {/* 3. Assignment, Status & Case Comments */}
          <div className="bg-card border border-line rounded-card p-5 shadow-sm space-y-4">
            <h3 className="font-semibold text-ink text-[15px]">Case notes & tracking</h3>

            {/* Official Assignment Form */}
            <div className="space-y-2 pb-3 border-b border-line">
              <label className="block text-[12px] font-medium text-muted">
                Assigned official
              </label>
              <div className="flex gap-2">
                <select
                  value={selectedAssignee}
                  onChange={(e) => setSelectedAssignee(e.target.value)}
                  className="flex-1 px-3 py-1.5 rounded-btn border border-line bg-card text-ink text-[13px]"
                >
                  <option>Ravi Kumar (Traffic Police Officer)</option>
                  <option>Asha Reddy (Road Safety Analyst)</option>
                  <option>Sana Fatima (Road Authority Official)</option>
                  <option>Meera Iyer (Road Authority Official)</option>
                </select>
                <button
                  onClick={() => alert(`Assigned to ${selectedAssignee}`)}
                  className="px-3.5 py-1.5 rounded-btn bg-lane text-ink font-semibold text-[12.5px]"
                >
                  Assign
                </button>
              </div>
            </div>

            {/* Comment timeline */}
            <div className="space-y-2.5 max-h-48 overflow-y-auto pr-1">
              {comments.map((cm, i) => (
                <div key={i} className="text-[12.5px] p-2.5 rounded bg-paper/60 border border-line">
                  <div className="flex justify-between text-[11px] text-muted mb-1">
                    <span className="font-semibold text-ink">{cm.author}</span>
                    <span>{cm.date}</span>
                  </div>
                  <p className="text-ink leading-snug">{cm.text}</p>
                </div>
              ))}
            </div>

            {/* Add Comment input */}
            <form onSubmit={handleAddComment} className="flex gap-2 pt-2">
              <input
                type="text"
                placeholder="Add case observation..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                className="flex-1 px-3 py-1.5 rounded-btn border border-line bg-card text-ink text-[13px] focus:ring-2 focus:ring-lane"
              />
              <button
                type="submit"
                className="p-2 rounded-btn bg-asphalt text-white hover:bg-black transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Risk Override Dialog Modal */}
      {showOverrideModal && (
        <div className="fixed inset-0 bg-asphalt/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border border-line rounded-card max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-semibold text-ink">Override Risk Level</h3>
            <p className="text-[13px] text-muted">
              Overriding calculated score requires a mandatory professional justification (BR-01, BR-05).
            </p>

            <form onSubmit={handleSaveOverride} className="space-y-3.5">
              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1">
                  New Risk Level
                </label>
                <select
                  value={currentRisk}
                  onChange={(e) => setCurrentRisk(e.target.value as any)}
                  className="w-full px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13px]"
                >
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1">
                  Justification Reason (Mandatory)
                </label>
                <textarea
                  required
                  rows={3}
                  placeholder="e.g. Completed speed hump installation and improved lighting reduces imminent risk."
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  className="w-full px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13px] focus:ring-2 focus:ring-lane"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-line">
                <button
                  type="button"
                  onClick={() => setShowOverrideModal(false)}
                  className="px-4 py-2 rounded-btn border border-line text-[13px] text-muted hover:bg-paper"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-btn bg-lane text-ink font-semibold text-[13px]"
                >
                  Confirm Override
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
