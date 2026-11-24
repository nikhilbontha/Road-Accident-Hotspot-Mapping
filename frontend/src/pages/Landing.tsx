import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MapPin,
  ArrowRight,
  ShieldCheck,
  EyeOff,
  History,
  Layers,
  Sparkles,
  BarChart3,
  Sliders,
  CheckCircle2,
  Users,
  Compass,
  FileSpreadsheet
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-paper font-sans text-ink">
      {/* 1. Asphalt Hero Section */}
      <section className="bg-asphalt text-white pt-6 pb-20 px-6 lg:px-12 relative overflow-hidden border-b-4 border-lane">
        {/* Subtle grid texture */}
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#F5B800_1px,transparent_1px)] [background-size:24px_24px] pointer-events-none" />

        {/* Top Navigation */}
        <header className="max-w-7xl mx-auto flex items-center justify-between pb-12 relative z-10">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-9 h-9 rounded-md bg-lane flex items-center justify-center shadow-md">
              <MapPin className="w-5 h-5 text-ink fill-ink" />
            </div>
            <div>
              <span className="font-bold text-[17px] tracking-tight text-white">Hotspot Mapping</span>
              <span className="text-[11px] block text-muted uppercase tracking-wider font-mono">Team 12 · Anurag Univ</span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-[13.5px] font-medium text-white/80">
            <a href="#how-it-works" className="hover:text-lane transition">How it works</a>
            <a href="#features" className="hover:text-lane transition">Features</a>
            <a href="#personas" className="hover:text-lane transition">Who it's for</a>
            <button onClick={() => navigate('/public')} className="hover:text-lane transition flex items-center gap-1">
              <Compass className="w-3.5 h-3.5 text-lane" />
              Public map
            </button>
          </nav>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-2 rounded-btn border border-white/20 text-white text-[13.5px] font-semibold hover:bg-white/10 transition"
            >
              Sign in
            </button>
            <button
              onClick={() => navigate('/signup')}
              className="px-4 py-2 rounded-btn bg-lane text-ink text-[13.5px] font-bold hover:brightness-105 transition shadow-sm"
            >
              Create account
            </button>
          </div>
        </header>

        {/* Hero Content */}
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10 pt-4">
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/15 text-xs text-lane font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Geospatial Decision-Support Platform · BRD-RAH-001</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-[52px] font-bold tracking-tight text-white leading-[1.15]">
              Know which roads to fix first.
            </h1>

            <p className="text-base sm:text-lg text-white/70 max-w-xl font-normal leading-relaxed">
              A high-precision Blackspot detection system for traffic police, road safety analysts, and transport authorities to collect, cluster, rank, and track high-fatality accident corridors.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={() => navigate('/signup')}
                className="px-6 py-3.5 rounded-btn bg-lane text-ink font-bold text-[14.5px] hover:brightness-105 transition shadow-lg flex items-center gap-2"
              >
                <span>Create an account</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={() => navigate('/public')}
                className="px-6 py-3.5 rounded-btn border border-white/25 text-white font-semibold text-[14.5px] hover:bg-white/10 transition flex items-center gap-2"
              >
                <Compass className="w-4 h-4 text-lane" />
                <span>View the public map</span>
              </button>
            </div>

            <p className="text-[12.5px] text-white/50 pt-2 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-lane shrink-0" />
              <span>Rankings are advice for experts to check. Nothing changes on a road automatically.</span>
            </p>
          </div>

          {/* Right Framed Map Preview */}
          <div className="lg:col-span-5 relative">
            <div className="p-3 bg-white/5 border border-white/15 rounded-2xl shadow-2xl backdrop-blur-sm">
              <div className="h-80 bg-asphalt rounded-xl overflow-hidden relative border border-white/10 flex flex-col justify-between p-4">
                {/* Background map grid lines */}
                <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#DADCD5_1px,transparent_1px)] [background-size:16px_16px]" />

                {/* Floating Rank 1 Card */}
                <div className="relative z-10 bg-card text-ink p-4 rounded-card border border-line shadow-xl space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-[#8A6A00] uppercase tracking-wider text-[11px]">
                      Rank 1 of 47 · Demo Data
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-crit text-white text-[10.5px] font-bold">
                      Critical
                    </span>
                  </div>
                  <div className="font-bold text-ink text-[14.5px]">NH-65 × Station Road Junction</div>
                  <div className="flex items-center gap-3 text-xs text-muted pt-1 border-t border-line/60">
                    <span className="font-semibold text-ink">41 accidents</span>
                    <span>·</span>
                    <span className="font-bold text-crit">9 deaths</span>
                    <span>·</span>
                    <span className="font-semibold text-ink">63 injured</span>
                  </div>
                </div>

                {/* Floating Map Pins in graphic preview */}
                <div className="relative z-10 flex justify-around items-center">
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-crit text-white flex items-center justify-center font-bold text-xs ring-4 ring-crit/30 shadow-lg">
                      1
                    </div>
                    <span className="text-[10px] bg-white text-ink px-1.5 py-0.5 rounded font-bold shadow-sm mt-1">
                      H-0142
                    </span>
                  </div>

                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-crit text-white flex items-center justify-center font-bold text-xs ring-4 ring-crit/30 shadow-lg">
                      2
                    </div>
                    <span className="text-[10px] bg-white text-ink px-1.5 py-0.5 rounded font-bold shadow-sm mt-1">
                      H-0087
                    </span>
                  </div>

                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-[#E2762B] text-white flex items-center justify-center font-bold text-xs ring-4 ring-[#E2762B]/30 shadow-lg">
                      3
                    </div>
                    <span className="text-[10px] bg-white text-ink px-1.5 py-0.5 rounded font-bold shadow-sm mt-1">
                      H-0103
                    </span>
                  </div>
                </div>

                <div className="relative z-10 flex justify-between items-center text-[11px] text-white/50">
                  <span>Telangana NH-65 Corridor</span>
                  <span>47 blackspots detected</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. From Spreadsheet to Action in Seven Steps */}
      <section id="how-it-works" className="py-20 px-6 max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-[12px] font-bold text-[#8A6A00] uppercase tracking-wider">The Lifecycle</span>
          <h2 className="text-3xl font-bold text-ink mt-1">From spreadsheet to action in seven steps</h2>
          <p className="text-muted text-[14.5px] mt-2">
            A continuous, verifiable workflow designed to turn raw police logs into engineered road safety improvements.
          </p>
        </div>

        {/* 7-Step Horizontal Process Line with Yellow Lane Marking */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-4 relative">
          {[
            { step: '1', title: 'Collect', desc: 'Manual or batch CSV/Excel import' },
            { step: '2', title: 'Validate', desc: 'PII mask & coordinate geocoding' },
            { step: '3', title: 'Analyze', desc: 'DBSCAN clustering & KDE heat surface' },
            { step: '4', title: 'Map', desc: 'Interactive Leaflet OSM visualization' },
            { step: '5', title: 'Prioritize', desc: 'Multi-criteria severity score (0–100)' },
            { step: '6', title: 'Recommend', desc: 'AI factor diagnosis & civil advice' },
            { step: '7', title: 'Track', desc: 'Before/after intervention evaluation' },
          ].map((s, idx) => (
            <div
              key={idx}
              className="p-4 rounded-card border border-line bg-card shadow-sm flex flex-col justify-between hover:border-lane transition relative group"
            >
              <div>
                <div className="w-7 h-7 rounded-full bg-lane text-ink font-bold text-xs flex items-center justify-center mb-3">
                  {s.step}
                </div>
                <h3 className="font-bold text-ink text-[14.5px]">{s.title}</h3>
                <p className="text-[12px] text-muted mt-1 leading-snug">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 3. Built for the People Who Decide Where Money Goes */}
      <section id="features" className="py-20 px-6 bg-white border-y border-line">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-[12px] font-bold text-[#8A6A00] uppercase tracking-wider">Features</span>
            <h2 className="text-3xl font-bold text-ink mt-1">Built for the people who decide where money goes</h2>
            <p className="text-muted text-[14.5px] mt-2">
              Defensible, statistically rigorous evidence to support high-impact road infrastructure investments.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: <Layers className="w-5 h-5 text-crit" />,
                title: 'DBSCAN & KDE Clustering',
                desc: 'Clusters accident occurrences with configurable eps radius (250m) and min accidents threshold (5). Computes a smooth Gaussian density heat surface.'
              },
              {
                icon: <BarChart3 className="w-5 h-5 text-lane" />,
                title: 'Multi-Criteria Risk Scoring',
                desc: 'Computes objective composite risk score from deaths (45%), accident volume (35%), and severe injuries (20%) with transparent point breakdown.'
              },
              {
                icon: <ShieldCheck className="w-5 h-5 text-[#2F6FB5]" />,
                title: 'Human-in-the-Loop Case Workflow',
                desc: 'Assign officials, transition through 6-step lifecycle (Identified → Under Review → Assigned → In Progress → Implemented → Closed), and override risk with mandatory reason.'
              },
              {
                icon: <EyeOff className="w-5 h-5 text-[#3E8E62]" />,
                title: 'Automated Privacy Masking',
                desc: 'Masks Indian vehicle registration plates, phone numbers, and driver names prior to database persistence and LLM transmission.'
              },
              {
                icon: <Sliders className="w-5 h-5 text-[#E2762B]" />,
                title: 'Two-Tier Geocoding Engine',
                desc: 'Converts textual police landmarks into lat/lon coordinates with confidence scoring and fallback verification for address-only entries.'
              },
              {
                icon: <History className="w-5 h-5 text-asphalt" />,
                title: 'Before & After Intervention Impact',
                desc: 'Evaluates accident and fatality reduction rates following signal installation, speed calming, or civil remodeling to prove ROI.'
              }
            ].map((f, idx) => (
              <div key={idx} className="p-6 rounded-card border border-line bg-paper/40 hover:bg-paper transition space-y-3">
                <div className="p-2.5 rounded-md bg-card border border-line w-fit shadow-sm">{f.icon}</div>
                <h3 className="font-bold text-ink text-[16px]">{f.title}</h3>
                <p className="text-[13px] text-muted leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>

          {/* Sample AI Recommendation Card */}
          <div className="mt-12 p-6 rounded-card border border-line bg-card shadow-sm max-w-3xl mx-auto space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-lane" />
                <h4 className="font-bold text-ink text-[14.5px]">Sample AI Recommendation Dossier</h4>
              </div>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-semibold bg-amber-50 border border-lane/40 text-[#8A6A00]">
                AI-generated · expert review needed
              </span>
            </div>
            <p className="text-[13px] text-muted leading-relaxed">
              <strong>Action:</strong> Install high-mast LED illumination and raised zebra crossing along NH-65 junction approaches. Addresses two-wheeler turning conflicts (58%) and inadequate nighttime lighting (46%).
            </p>
          </div>
        </div>
      </section>

      {/* 4. One Platform, Four Kinds of Users */}
      <section id="personas" className="py-20 px-6 max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-[12px] font-bold text-[#8A6A00] uppercase tracking-wider">Stakeholders</span>
          <h2 className="text-3xl font-bold text-ink mt-1">One platform, four kinds of users</h2>
          <p className="text-muted text-[14.5px] mt-2">
            Tailored workflows and role-based permissions designed specifically for each road safety discipline.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              role: 'Traffic Police',
              desc: 'Target patrol beats at peak accident hours (6–9 pm), report road hazards, and verify incident coordinates.',
              badge: 'police_officer'
            },
            {
              role: 'Road Safety Analysts',
              desc: 'Tune clustering parameters, run factor analysis, test hypotheses, and prioritize blackspot dossiers.',
              badge: 'safety_analyst'
            },
            {
              role: 'Road Authorities',
              desc: 'Commission civil engineering works, approve zebra crossings, optimize signal timings, and track completions.',
              badge: 'authority_official'
            },
            {
              role: 'The Public',
              desc: 'View grid-banded 500m cautionary hazard zones and high-risk corridors with zero personal data leakage.',
              badge: 'public_viewer'
            }
          ].map((u, idx) => (
            <div key={idx} className="p-5 rounded-card border border-line bg-card shadow-sm flex flex-col justify-between">
              <div>
                <span className="text-[11px] font-mono text-muted uppercase font-bold">{u.badge}</span>
                <h3 className="font-bold text-ink text-[16px] mt-1 mb-2">{u.role}</h3>
                <p className="text-[13px] text-muted leading-relaxed">{u.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 5. Dark Asphalt Band: Advice, Never Automatic Action */}
      <section className="bg-asphalt text-white py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-[11px] font-bold text-lane uppercase tracking-widest">Safeguards & Governance</span>
            <h2 className="text-3xl font-bold text-white mt-1">Advice, never automatic action</h2>
            <p className="text-white/70 text-[14px] mt-2">
              Three inviolable architectural principles (BR-01, BR-02, BR-03) governing all system outputs.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="space-y-2">
              <div className="font-bold text-white text-[16px] flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-lane" />
                Evidence on every result
              </div>
              <p className="text-[13px] text-white/70 leading-relaxed">
                Every identified hotspot shows the underlying accident count, fatalities, time-of-day concentration, and parameter settings. No black boxes.
              </p>
            </div>

            <div className="space-y-2">
              <div className="font-bold text-white text-[16px] flex items-center gap-2">
                <EyeOff className="w-5 h-5 text-lane" />
                Personal details hidden
              </div>
              <p className="text-[13px] text-white/70 leading-relaxed">
                Vehicle numbers, phone numbers, and driver names are permanently masked before database storage and LLM evaluation. Public map shows only 500m aggregated grid bands.
              </p>
            </div>

            <div className="space-y-2">
              <div className="font-bold text-white text-[16px] flex items-center gap-2">
                <History className="w-5 h-5 text-lane" />
                Every change is recorded
              </div>
              <p className="text-[13px] text-white/70 leading-relaxed">
                An append-only audit trail logs every import, analysis run, risk override with justification, assignment, and status transition.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Closing Call to Action & Footer */}
      <section className="py-20 px-6 text-center max-w-4xl mx-auto space-y-6">
        <h2 className="text-3xl sm:text-4xl font-bold text-ink">See the hotspots near you</h2>
        <p className="text-muted text-[15px] max-w-xl mx-auto">
          Explore the public map or sign in with your department credentials to run blackspot evaluations.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <button
            onClick={() => navigate('/signup')}
            className="px-6 py-3 rounded-btn bg-lane text-ink font-bold text-[14px] hover:brightness-105 transition shadow-sm"
          >
            Create an account
          </button>
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-3 rounded-btn border border-line bg-card text-ink font-semibold text-[14px] hover:bg-paper transition"
          >
            Sign in
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 bg-card border-t border-line text-center text-xs text-muted space-y-2">
        <p>Road Accident Hotspot Mapping · Team 12 · Anurag University</p>
        <p>Demo data only · Specification BRD-RAH-001</p>
      </footer>
    </div>
  );
};
