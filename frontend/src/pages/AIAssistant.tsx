import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getApiUrl } from '../services/api';
import {
  Send,
  Sparkles,
  AlertCircle,
  MapPin,
  ExternalLink,
  ShieldAlert,
  Info,
  ChevronRight,
  Bot,
  User as UserIcon
} from 'lucide-react';

interface CitedHotspot {
  code: string;
  name: string;
  risk_level: string;
  score: number;
  accidents: number;
  deaths?: number;
  injuries?: number;
  lat: number;
  lon: number;
  status?: string;
}

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  citations?: string[];
  data_period?: string;
  caveats?: string;
  cited_hotspots?: CitedHotspot[];
  time: string;
}

export const AIAssistantPage: React.FC = () => {
  const navigate = useNavigate();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'm1',
      sender: 'assistant',
      text: (
        "Welcome to the **Road Accident Hotspot Mapping AI Assistant**.\n\n" +
        "I provide grounded analysis based strictly on your department's stored accident data, blackspot rankings, and intervention evaluations.\n\n" +
        "You can ask about specific hotspot factors (e.g. `H-0142`), compare zones, request unassigned critical hotspots, or review before/after intervention impacts."
      ),
      citations: ['H-0142', 'H-0087'],
      data_period: '1 Dec 2025 – 23 Nov 2026',
      caveats: 'All insights are advisory for safety engineers and traffic police officers. Human-in-the-loop validation is required.',
      cited_hotspots: [
        {
          code: 'H-0142',
          name: 'NH-65 × Station Road Junction',
          risk_level: 'critical',
          score: 92.0,
          accidents: 41,
          deaths: 9,
          injuries: 63,
          lat: 17.4399,
          lon: 78.4983,
          status: 'Under review'
        },
        {
          code: 'H-0087',
          name: 'Outer Ring Road, Exit 12',
          risk_level: 'critical',
          score: 88.0,
          accidents: 37,
          deaths: 7,
          injuries: 48,
          lat: 17.4125,
          lon: 78.5320,
          status: 'Assigned'
        }
      ],
      time: 'Just now'
    }
  ]);

  const [activeCitations, setActiveCitations] = useState<CitedHotspot[]>(
    messages[0].cited_hotspots || []
  );

  const suggestions = [
    'What caused most crashes at H-0142?',
    'Show unassigned critical hotspots',
    'Compare Zone 3 with Zone 5',
    'Evaluate before/after impact of signals on H-0087'
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || input).trim();
    if (!textToSend || loading) return;

    const userMsg: Message = {
      id: `u-${Date.now()}`,
      sender: 'user',
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem('rah_token');
      const res = await fetch(getApiUrl('/assistant/chat'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ message: textToSend })
      });

      if (res.ok) {
        const data = await res.json();
        const assistantMsg: Message = {
          id: `a-${Date.now()}`,
          sender: 'assistant',
          text: data.answer,
          citations: data.citations,
          data_period: data.data_period,
          caveats: data.caveats,
          cited_hotspots: data.cited_hotspots,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages((prev) => [...prev, assistantMsg]);
        if (data.cited_hotspots && data.cited_hotspots.length > 0) {
          setActiveCitations(data.cited_hotspots);
        }
      } else {
        throw new Error('Server error');
      }
    } catch (err) {
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: 'An error occurred while querying the safety analysis engine. Please try again or check your query format.',
        caveats: 'Unable to reach backend analytics database.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const getRiskChip = (level: string) => {
    const l = level.toLowerCase();
    if (l === 'critical') return 'bg-[#C62F2A] text-white';
    if (l === 'high') return 'bg-[#E2762B] text-white';
    if (l === 'medium') return 'bg-[#E7B416] text-ink';
    return 'bg-[#3E8E62] text-white';
  };

  return (
    <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-130px)]">
      {/* Left Chat Column (7 cols) */}
      <div className="lg:col-span-7 flex flex-col bg-card border border-line rounded-card shadow-sm overflow-hidden h-full">
        {/* Suggestion Chips */}
        <div className="p-3 bg-paper border-b border-line flex items-center gap-2 overflow-x-auto no-scrollbar shrink-0">
          <span className="text-[11.5px] font-semibold text-muted flex items-center gap-1 shrink-0">
            <Sparkles className="w-3.5 h-3.5 text-lane" />
            Suggested:
          </span>
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(s)}
              className="text-[12px] px-3 py-1 rounded-full border border-line bg-card hover:bg-lane/20 text-ink whitespace-nowrap transition"
            >
              {s}
            </button>
          ))}
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-5 space-y-5">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              {/* Sender label & avatar */}
              <div className="flex items-center gap-1.5 mb-1 text-[11px] text-muted">
                {m.sender === 'user' ? (
                  <>
                    <span>You</span>
                    <span className="w-4 h-4 rounded-full bg-asphalt flex items-center justify-center text-[9px] text-white">
                      U
                    </span>
                  </>
                ) : (
                  <>
                    <div className="w-4 h-4 rounded-full bg-lane flex items-center justify-center text-[9px] text-ink font-bold">
                      AI
                    </div>
                    <span>Safety Insights Assistant</span>
                    <span className="text-[10px] bg-paper px-1.5 py-0.2 rounded border border-line">
                      AI-generated · expert review needed
                    </span>
                  </>
                )}
                <span>· {m.time}</span>
              </div>

              {/* Message Bubble */}
              <div
                className={`max-w-[92%] rounded-card p-4 text-[13.5px] leading-relaxed shadow-sm ${
                  m.sender === 'user'
                    ? 'bg-asphalt text-white'
                    : 'bg-white border border-line text-ink'
                }`}
              >
                {/* Render markdown text */}
                <div className="whitespace-pre-wrap space-y-2">
                  {m.text.split('\n\n').map((paragraph, pIdx) => {
                    // Check if table
                    if (paragraph.includes('|')) {
                      const lines = paragraph.split('\n').filter((l) => l.trim().startsWith('|'));
                      if (lines.length >= 2) {
                        const headers = lines[0].split('|').map((c) => c.trim()).filter(Boolean);
                        const rows = lines.slice(2).map((row) =>
                          row.split('|').map((c) => c.trim()).filter(Boolean)
                        );
                        return (
                          <div key={pIdx} className="overflow-x-auto my-2">
                            <table className="w-full text-left text-xs border border-line rounded">
                              <thead className="bg-paper border-b border-line">
                                <tr>
                                  {headers.map((h, hIdx) => (
                                    <th key={hIdx} className="p-2 font-semibold text-ink">
                                      {h}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-line">
                                {rows.map((r, rIdx) => (
                                  <tr key={rIdx} className="hover:bg-paper/50">
                                    {r.map((cell, cIdx) => (
                                      <td key={cIdx} className="p-2 text-ink">
                                        {cell}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        );
                      }
                    }

                    // Render standard formatted paragraph
                    return (
                      <p key={pIdx}>
                        {paragraph.split('**').map((part, idx) =>
                          idx % 2 === 1 ? <strong key={idx}>{part}</strong> : part
                        )}
                      </p>
                    );
                  })}
                </div>

                {/* Caveat Box if present */}
                {m.caveats && (
                  <div className="mt-3 p-2.5 rounded bg-[#FFF3C4] border border-[#F5B800]/40 text-[#6B5200] text-[12px] flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                    <span>{m.caveats}</span>
                  </div>
                )}

                {/* Citation Footer */}
                {m.citations && m.citations.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-line/60 flex items-center justify-between text-[11px] text-muted">
                    <span className="flex items-center gap-1">
                      <Info className="w-3.5 h-3.5 text-[#8A6A00]" />
                      Based on {m.citations.join(', ')} · {m.data_period || '2025–2026'}
                    </span>
                    <button
                      onClick={() => m.cited_hotspots && setActiveCitations(m.cited_hotspots)}
                      className="font-semibold text-[#8A6A00] hover:underline"
                    >
                      Inspect data →
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-xs text-muted p-2">
              <div className="w-4 h-4 rounded-full bg-lane animate-pulse" />
              <span>Querying stored accident database & calculating factor weights...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-3 bg-card border-t border-line shrink-0">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about hotspots, factors, or safety interventions..."
              className="flex-1 px-4 py-2.5 rounded-full border border-line bg-paper text-ink text-[13.5px] focus:outline-none focus:border-lane transition"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2.5 rounded-full bg-lane text-ink font-semibold hover:brightness-95 disabled:opacity-50 transition shadow-sm"
              title="Send question"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="text-center mt-2">
            <span className="text-[11px] text-muted">
              Answers come from your stored accident data. Check them before acting on a road.
            </span>
          </div>
        </div>
      </div>

      {/* Right Column: "Data behind this answer" (5 cols) */}
      <div className="lg:col-span-5 flex flex-col bg-card border border-line rounded-card shadow-sm p-5 overflow-hidden h-full">
        <div className="flex items-center justify-between pb-3 border-b border-line mb-4 shrink-0">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-[#8A6A00]" />
            <h2 className="text-[15px] font-semibold text-ink">Data behind this answer</h2>
          </div>
          <button
            onClick={() => navigate('/map')}
            className="text-xs font-semibold text-[#8A6A00] hover:underline flex items-center gap-1"
          >
            Open Hotspot Map <ExternalLink className="w-3 h-3" />
          </button>
        </div>

        {/* Mini Map Placeholder / Coordinate Card */}
        <div className="h-44 bg-paper rounded-btn border border-line p-3 relative overflow-hidden flex flex-col justify-between shrink-0 mb-4">
          <div className="absolute inset-0 opacity-15 bg-[radial-gradient(#1F2328_1px,transparent_1px)] [background-size:12px_12px]" />
          <div className="relative z-10 flex justify-between items-start text-xs text-muted">
            <span className="font-mono">NH-65 & ORR Sector</span>
            <span className="px-2 py-0.5 rounded bg-card border border-line font-medium text-ink">
              {activeCitations.length} cited places
            </span>
          </div>

          {/* Graphical pins */}
          <div className="relative z-10 flex justify-center items-center gap-8 py-2">
            {activeCitations.map((c, idx) => (
              <div key={idx} className="flex flex-col items-center">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center shadow-md font-bold text-xs ring-2 ring-white ${getRiskChip(
                    c.risk_level
                  )}`}
                >
                  {idx + 1}
                </div>
                <span className="text-[10px] font-bold text-ink mt-1 bg-white/90 px-1 rounded shadow-sm">
                  {c.code}
                </span>
              </div>
            ))}
          </div>

          <div className="relative z-10 flex justify-between items-end text-[11px] text-muted">
            <span>Center: 17.4399° N, 78.4983° E</span>
            <span className="text-[10px]">OpenStreetMap projection</span>
          </div>
        </div>

        {/* Cited Hotspot Dossier Cards */}
        <div className="flex-1 overflow-y-auto space-y-3 pr-1">
          <div className="text-[12px] font-medium text-muted mb-2">
            Cited Blackspot Dossiers ({activeCitations.length}):
          </div>

          {activeCitations.map((h, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-card border border-line bg-paper/60 hover:bg-paper transition space-y-2.5"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-ink text-[14px]">{h.code}</span>
                    <span
                      className={`px-2 py-0.2 text-[10.5px] font-semibold rounded-full uppercase ${getRiskChip(
                        h.risk_level
                      )}`}
                    >
                      {h.risk_level}
                    </span>
                  </div>
                  <div className="text-[12.5px] text-muted font-medium mt-0.5">{h.name}</div>
                </div>

                <div className="text-right">
                  <div className="text-[16px] font-bold text-ink tabular-nums leading-none">
                    {h.score}
                  </div>
                  <span className="text-[10px] text-muted">Score / 100</span>
                </div>
              </div>

              {/* Stats Strip */}
              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-line/60 text-center text-xs">
                <div className="p-1 rounded bg-card border border-line/60">
                  <div className="font-bold text-ink tabular-nums">{h.accidents}</div>
                  <div className="text-[10px] text-muted">Accidents</div>
                </div>
                <div className="p-1 rounded bg-card border border-line/60">
                  <div className="font-bold text-crit tabular-nums">{h.deaths ?? '—'}</div>
                  <div className="text-[10px] text-muted">Fatalities</div>
                </div>
                <div className="p-1 rounded bg-card border border-line/60">
                  <div className="font-bold text-ink tabular-nums">{h.injuries ?? '—'}</div>
                  <div className="text-[10px] text-muted">Injuries</div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-[11px] text-muted">Status: {h.status || 'Active case'}</span>
                <button
                  onClick={() => navigate(`/cases/${h.code}`)}
                  className="text-xs font-semibold text-[#8A6A00] hover:underline flex items-center gap-0.5"
                >
                  View full case <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
