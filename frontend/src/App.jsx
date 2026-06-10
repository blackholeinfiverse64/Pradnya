import { useState, useEffect } from "react";
import { getSignalsWithSummary, getPatterns, getHealth, NICAI_API } from "./services/api.js";

// ── API Config Defaults ──────────────────────────────────────────────────────

const DEFAULT_SAMACHAR = import.meta.env.VITE_SAMACHAR_API;
const DEFAULT_MITRA = import.meta.env.VITE_MITRA_API;

const MARITIME_SCENARIO =
  "Multiple reports indicate a vessel operating in restricted waters near a coastal zone. Movement pattern suggests loitering behavior with intermittent communication signals. No authorized activity recorded for this region.";
const ENVIRONMENTAL_SCENARIO =
  "Recent field reports indicate abnormal changes in water quality levels across multiple monitoring points. Possible contamination event suspected with inconsistent readings from different sources.";

// ── Mock Data ────────────────────────────────────────────────────────────────

const MOCK_SIGNALS = [
  { id: "SIG-20250519-124", type: "AQI", location: "Mumbai", risk: "HIGH", anomaly: "AQI_SPIKE", time: "12:44 PM", details: "Air Quality Index exceeded safe threshold by 340%. PM2.5 levels at 487 µg/m³. Source: IoT sensor grid cluster MH-W-07." },
  { id: "SIG-20250519-123", type: "Temperature", location: "Delhi", risk: "MEDIUM", anomaly: "TEMP_RISE", time: "12:43 PM", details: "Temperature anomaly of +4.2°C above seasonal baseline detected across 3 monitoring stations. Gradual increase over 48h." },
  { id: "SIG-20250519-122", type: "Weather", location: "Pune", risk: "HIGH", anomaly: "HEAVY_RAIN", time: "12:42 PM", details: "Rainfall intensity at 92mm/hr exceeding 50-year return period threshold. Flash flood advisory issued for downstream areas." },
  { id: "SIG-20250519-121", type: "AQI", location: "Bangalore", risk: "LOW", anomaly: "NORMAL", time: "12:41 PM", details: "All air quality parameters within normal range. AQI at 42 (Good). Routine monitoring continues." },
  { id: "SIG-20250519-120", type: "Temperature", location: "Hyderabad", risk: "MEDIUM", anomaly: "TEMP_RISE", time: "12:40 PM", details: "Surface temperature anomaly detected. Urban heat island effect amplifying readings by +2.8°C in central zones." },
];

const MOCK_PATTERNS = [
  { id: "PATTERN-20250519-07", type: "REPEATED_ANOMALY", risk: "HIGH", zones: "Mumbai, Thane", count: 5 },
  { id: "PATTERN-20250519-06", type: "CORRELATED_SPIKE", risk: "MEDIUM", zones: "Delhi, Noida", count: 3 },
  { id: "PATTERN-20250519-05", type: "GRADUAL_INCREASE", risk: "LOW", zones: "Pune", count: 2 },
];

const ACTIONS = [
  { traceId: "T20250519-000124", action: "eligible_for_escalation", target: "authority", time: "12:44 PM" },
  { traceId: "T20250519-000123", action: "requires_review", target: "operator", time: "12:43 PM" },
  { traceId: "T20250519-000122", action: "monitor", target: "system", time: "12:42 PM" },
  { traceId: "T20250519-000121", action: "eligible_for_escalation", target: "authority", time: "12:41 PM" },
  { traceId: "T20250519-000120", action: "requires_review", target: "operator", time: "12:40 PM" },
];

const TREND = {
  labels: ["May 13", "May 14", "May 15", "May 16", "May 17", "May 18", "May 19"],
  high: [22, 25, 30, 22, 15, 20, 18],
  medium: [38, 42, 48, 55, 62, 45, 37],
  low: [58, 65, 72, 78, 85, 68, 69],
};

const NAV_ITEMS = [
  { key: "overview", label: "Overview", icon: "◉" },
  { key: "signals", label: "Signals", icon: "◆" },
  { key: "anomalies", label: "Anomalies", icon: "△" },
  { key: "patterns", label: "Patterns", icon: "◈" },
  { key: "actions", label: "Actions", icon: "▸" },
  { key: "logs", label: "Logs", icon: "☰" },
  { key: "health", label: "System Health", icon: "♥" },
  { key: "settings", label: "Settings", icon: "⚙" },
];

const RISK_COLORS = { HIGH: "#ef4444", MEDIUM: "#f59e0b", LOW: "#22c55e" };

function mapApiSignal(signal) {
  return {
    id: signal.signal_id,
    type: signal.feature_type || "Signal",
    location: `${signal.latitude?.toFixed?.(2) ?? signal.latitude}, ${signal.longitude?.toFixed?.(2) ?? signal.longitude}`,
    risk: signal.risk_level,
    anomaly: signal.anomaly_type,
    time: "Live",
    details: signal.explanation,
    traceId: signal.trace_id,
  };
}

function mapApiPattern(pattern) {
  if (!pattern || pattern.pattern_type === "NONE") return [];
  return [{
    id: pattern.pattern_id,
    type: pattern.pattern_type,
    risk: pattern.anomaly_count > 5 ? "HIGH" : pattern.anomaly_count > 2 ? "MEDIUM" : "LOW",
    zones: (pattern.affected_zones || []).join(", ") || "Multiple zones",
    count: pattern.anomaly_count,
    summary: pattern.pattern_summary,
  }];
}

// ── Shared Components ────────────────────────────────────────────────────────

function RiskBadge({ level }) {
  return (
    <span style={{ display: "inline-block", padding: "3px 14px", borderRadius: 4, fontSize: 11, fontWeight: 700, letterSpacing: 0.5, color: "#fff", background: RISK_COLORS[level] || "#64748b" }}>
      {level}
    </span>
  );
}

function SectionHeader({ title, btnText, onBtn }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
      <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600, color: "#e2e8f0" }}>{title}</h3>
      {btnText && (
        <button onClick={onBtn} style={{ padding: "5px 14px", borderRadius: 6, border: "1px solid #1e3a5f", background: "transparent", color: "#60a5fa", fontSize: 12, fontWeight: 500, cursor: "pointer", fontFamily: "inherit" }}>
          {btnText}
        </button>
      )}
    </div>
  );
}

function Modal({ title, onClose, children }) {
  return (
    <div style={S.modalOverlay} onClick={onClose}>
      <div className="nicai-modal" style={S.modal} onClick={(e) => e.stopPropagation()}>
        <div style={S.modalHeader}>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: "#e2e8f0" }}>{title}</h3>
          <button onClick={onClose} style={S.modalClose}>✕</button>
        </div>
        <div style={S.modalBody}>{children}</div>
      </div>
    </div>
  );
}

function InfoRow({ label, children }) {
  return (
    <div className="info-row" style={{ display: "flex", gap: 12, padding: "10px 0", borderBottom: "1px solid #151d2e", fontSize: 13 }}>
      <span style={{ color: "#64748b", minWidth: 120, fontWeight: 500 }}>{label}</span>
      <span style={{ color: "#e2e8f0", minWidth: 0, wordBreak: "break-word" }}>{children}</span>
    </div>
  );
}

function DonutChart() {
  const high = 14.5, med = 29.8, low = 55.7;
  const d1 = high * 3.6, d2 = (high + med) * 3.6;
  return (
    <div className="donut-wrap" style={{ display: "flex", alignItems: "center", gap: 32, justifyContent: "center", padding: "12px 0", flexWrap: "wrap" }}>
      <div style={{ position: "relative", width: 180, height: 180, flexShrink: 0 }}>
        <div style={{ width: 180, height: 180, borderRadius: "50%", background: `conic-gradient(#ef4444 0deg ${d1}deg, #f59e0b ${d1}deg ${d2}deg, #22c55e ${d2}deg 360deg)` }} />
        <div style={{ position: "absolute", top: 28, left: 28, width: 124, height: 124, borderRadius: "50%", background: "#0d1424", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <span style={{ fontSize: 32, fontWeight: 700, color: "#22c55e" }}>124</span>
          <span style={{ fontSize: 12, color: "#64748b" }}>Total</span>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {[{ label: "High Risk", val: `18 (${high}%)`, color: "#ef4444" }, { label: "Medium Risk", val: `37 (${med}%)`, color: "#f59e0b" }, { label: "Low Risk", val: `69 (${low}%)`, color: "#22c55e" }].map((r) => (
          <div key={r.label} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 13 }}>
            <div style={{ width: 10, height: 10, borderRadius: 2, background: r.color, flexShrink: 0 }} />
            <span style={{ color: "#94a3b8", minWidth: 90 }}>{r.label}</span>
            <span style={{ color: "#e2e8f0", fontWeight: 600 }}>{r.val}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function TrendChart() {
  const W = 440, H = 220, PL = 38, PR = 10, PT = 10, PB = 40;
  const plotW = W - PL - PR, plotH = H - PT - PB;
  const toX = (i) => PL + (i / 6) * plotW;
  const toY = (v) => PT + plotH - (v / 100) * plotH;
  const toPoints = (arr) => arr.map((v, i) => `${toX(i)},${toY(v)}`).join(" ");
  const yTicks = [0, 20, 40, 60, 80, 100];
  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto" }}>
      {yTicks.map((v) => (
        <g key={v}>
          <line x1={PL} y1={toY(v)} x2={W - PR} y2={toY(v)} stroke="#1e293b" strokeWidth="1" strokeDasharray="4 3" />
          <text x={PL - 6} y={toY(v) + 4} textAnchor="end" fill="#475569" fontSize="10">{v}</text>
        </g>
      ))}
      {TREND.labels.map((l, i) => <text key={l} x={toX(i)} y={H - 8} textAnchor="middle" fill="#475569" fontSize="9">{l}</text>)}
      <polyline points={toPoints(TREND.low)} fill="none" stroke="#22c55e" strokeWidth="2" strokeLinejoin="round" />
      <polyline points={toPoints(TREND.medium)} fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinejoin="round" />
      <polyline points={toPoints(TREND.high)} fill="none" stroke="#ef4444" strokeWidth="2" strokeLinejoin="round" />
      {TREND.high.map((v, i) => <circle key={`h${i}`} cx={toX(i)} cy={toY(v)} r="3" fill="#ef4444" />)}
      {TREND.medium.map((v, i) => <circle key={`m${i}`} cx={toX(i)} cy={toY(v)} r="3" fill="#f59e0b" />)}
      {TREND.low.map((v, i) => <circle key={`l${i}`} cx={toX(i)} cy={toY(v)} r="3" fill="#22c55e" />)}
    </svg>
  );
}

function StatIcon({ type, color }) {
  const paths = {
    signals: <path d="M3 17l4-4 4 4 4-8 4 4" stroke={color} fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />,
    highRisk: <><path d="M12 3L3 21h18L12 3z" stroke={color} fill="none" strokeWidth="1.8" strokeLinejoin="round" /><line x1="12" y1="10" x2="12" y2="14" stroke={color} strokeWidth="2" /><circle cx="12" cy="17" r="1" fill={color} /></>,
    medRisk: <><circle cx="12" cy="12" r="9" stroke={color} fill="none" strokeWidth="1.8" /><line x1="12" y1="8" x2="12" y2="13" stroke={color} strokeWidth="2" strokeLinecap="round" /><circle cx="12" cy="16.5" r="1" fill={color} /></>,
    lowRisk: <path d="M12 3l7 4v5c0 5-3.5 9.7-7 11-3.5-1.3-7-6-7-11V7l7-4z" stroke={color} fill="none" strokeWidth="1.8" strokeLinejoin="round" />,
    patterns: <><circle cx="8" cy="7" r="3" stroke={color} fill="none" strokeWidth="1.8" /><circle cx="16" cy="7" r="3" stroke={color} fill="none" strokeWidth="1.8" /><path d="M4 21v-1a4 4 0 014-4h8a4 4 0 014 4v1" stroke={color} fill="none" strokeWidth="1.8" strokeLinecap="round" /></>,
  };
  return (
    <div style={{ width: 44, height: 44, borderRadius: 10, background: `${color}15`, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <svg viewBox="0 0 24 24" width="24" height="24">{paths[type]}</svg>
    </div>
  );
}

// ── Main App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [activeNav, setActiveNav] = useState("overview");
  const [now, setNow] = useState(new Date());
  const [sidebarOpen, setSidebarOpen] = useState(() => window.innerWidth > 768);
  const [signals, setSignals] = useState(MOCK_SIGNALS);
  const [patterns, setPatterns] = useState(MOCK_PATTERNS);
  const [liveSummary, setLiveSummary] = useState(null);
  const [usingLiveData, setUsingLiveData] = useState(false);

  const [traceSearch, setTraceSearch] = useState("");
  const [selectedSignal, setSelectedSignal] = useState(null);
  const [selectedTrace, setSelectedTrace] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  const [samacharUrl, setSamacharUrl] = useState(DEFAULT_SAMACHAR);
  const [mitraUrl, setMitraUrl] = useState(DEFAULT_MITRA);
  const [pipelineInput, setPipelineInput] = useState("");
  const [samacharResult, setSamacharResult] = useState(null);
  const [mitraResult, setMitraResult] = useState(null);
  const [samacharError, setSamacharError] = useState(null);
  const [mitraError, setMitraError] = useState(null);
  const [pipelineLoading, setPipelineLoading] = useState(false);
  const [pipelineStep, setPipelineStep] = useState("idle");

  const [healthStatus, setHealthStatus] = useState({ nicai: null, samachar: null, mitra: null });
  const [checkingHealth, setCheckingHealth] = useState(false);

  const [logs, setLogs] = useState(() => [{ time: new Date(), msg: "System initialized", type: "system" }]);

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (!NICAI_API) return;

    async function loadLiveData() {
      try {
        const [signalsData, pattern] = await Promise.all([
          getSignalsWithSummary(),
          getPatterns(),
        ]);

        if (signalsData.signals?.length) {
          setSignals(signalsData.signals.map(mapApiSignal));
          setLiveSummary(signalsData.summary);
          setUsingLiveData(true);
        }

        const mappedPatterns = mapApiPattern(pattern);
        if (mappedPatterns.length) {
          setPatterns(mappedPatterns);
        }

        addLog("Loaded live data from NICAI API", "api");
      } catch {
        addLog("NICAI API unavailable — using demo data", "error");
      }
    }

    loadLiveData();
  }, []);

  const isMobile = () => window.innerWidth <= 768;
  const addLog = (msg, type = "info") => setLogs((p) => [{ time: new Date(), msg, type }, ...p]);
  const timeStr = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const dateStr = now.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  const refreshedStr = lastRefreshed.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });

  const navigate = (key) => {
    setActiveNav(key);
    addLog(`Navigated to ${NAV_ITEMS.find((n) => n.key === key)?.label}`, "nav");
    if (isMobile()) setSidebarOpen(false);
  };
  const handleRefresh = async () => {
    setLastRefreshed(new Date());
    if (NICAI_API) {
      try {
        const signalsData = await getSignalsWithSummary();
        if (signalsData.signals?.length) {
          setSignals(signalsData.signals.map(mapApiSignal));
          setLiveSummary(signalsData.summary);
          setUsingLiveData(true);
        }
        const pattern = await getPatterns();
        const mappedPatterns = mapApiPattern(pattern);
        if (mappedPatterns.length) setPatterns(mappedPatterns);
        addLog("Live data refreshed from NICAI API", "api");
      } catch {
        addLog("Refresh failed — NICAI API unreachable", "error");
      }
    } else {
      addLog("Data refreshed", "system");
    }
  };
  const handleTraceSearch = () => {
    if (!traceSearch.trim()) return;
    const found = ACTIONS.find((a) => a.traceId.toLowerCase().includes(traceSearch.toLowerCase()));
    if (found) { setSelectedTrace(found); addLog(`Trace searched: ${traceSearch}`, "search"); }
    else { setSelectedTrace({ traceId: traceSearch, action: "Not found", target: "—", time: "—" }); addLog(`Trace not found: ${traceSearch}`, "search"); }
  };
  const handleViewFullTrace = () => { const r = ACTIONS[0]; setSelectedTrace(r); addLog(`Viewed trace: ${r.traceId}`, "search"); };

  async function handleProcess() {
    if (!pipelineInput.trim()) { setSamacharError("Error processing request"); setSamacharResult(null); setMitraResult(null); setMitraError(null); setPipelineStep("idle"); return; }
    setSamacharResult(null); setSamacharError(null); setMitraResult(null); setMitraError(null); setPipelineLoading(true); setPipelineStep("samachar");
    addLog("Pipeline started — calling Samachar API", "api");
    let samacharData;
    try {
      const res = await fetch(`${samacharUrl}/api/samachar/process`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: pipelineInput }) });
      if (!res.ok) throw new Error(res.statusText);
      samacharData = await res.json(); setSamacharResult(samacharData); addLog("Samachar API responded successfully", "api");
    } catch { setSamacharError("Error processing request"); addLog("Samachar API call failed", "error"); setPipelineLoading(false); setPipelineStep("idle"); return; }
    setPipelineStep("mitra"); addLog("Calling Mitra API with Samachar output", "api");
    try {
      const res = await fetch(`${mitraUrl}/api/mitra/evaluate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ event: samacharData }) });
      if (!res.ok) throw new Error(res.statusText);
      const mitraData = await res.json(); setMitraResult(mitraData); addLog("Mitra API responded successfully", "api");
    } catch { setMitraError("Error processing request"); addLog("Mitra API call failed", "error"); }
    setPipelineLoading(false); setPipelineStep("done"); addLog("Pipeline complete", "system");
  }

  async function checkHealth() {
    setCheckingHealth(true); addLog("Running health checks...", "system");
    const check = async (url) => { try { const res = await fetch(url, { signal: AbortSignal.timeout(8000) }); return res.ok ? "online" : "error"; } catch { return "offline"; } };
    const nicaiCheck = async () => {
      if (!NICAI_API) return "not_configured";
      try { await getHealth(); return "online"; } catch { return "offline"; }
    };
    const [n, s, m] = await Promise.all([nicaiCheck(), check(samacharUrl), check(mitraUrl)]);
    setHealthStatus({ nicai: n, samachar: s, mitra: m });
    addLog(`Health check complete — NICAI: ${n}, Samachar: ${s}, Mitra: ${m}`, "system");
    setCheckingHealth(false);
  }

  const stats = liveSummary ? [
    { title: "TOTAL SIGNALS", value: String(liveSummary.total), change: usingLiveData ? "Live from NICAI API" : "Demo data", color: "#3b82f6", icon: "signals" },
    { title: "HIGH RISK", value: String(liveSummary.high), change: "Processed signals", color: "#ef4444", icon: "highRisk" },
    { title: "MEDIUM RISK", value: String(liveSummary.medium), change: "Processed signals", color: "#f59e0b", icon: "medRisk" },
    { title: "LOW RISK", value: String(liveSummary.low), change: "Processed signals", color: "#22c55e", icon: "lowRisk" },
    { title: "ACTIVE PATTERNS", value: String(patterns.length), change: usingLiveData ? "Live from NICAI API" : "Demo data", color: "#3b82f6", icon: "patterns" },
  ] : [
    { title: "TOTAL SIGNALS", value: "124", change: "↑ 18% from yesterday", color: "#3b82f6", icon: "signals" },
    { title: "HIGH RISK", value: "18", change: "↑ 12% from yesterday", color: "#ef4444", icon: "highRisk" },
    { title: "MEDIUM RISK", value: "37", change: "↑ 5% from yesterday", color: "#f59e0b", icon: "medRisk" },
    { title: "LOW RISK", value: "69", change: "↓ 8% from yesterday", color: "#22c55e", icon: "lowRisk" },
    { title: "ACTIVE PATTERNS", value: "7", change: "↑ 2 from yesterday", color: "#3b82f6", icon: "patterns" },
  ];

  const collapsed = !sidebarOpen && !isMobile();

  return (
    <div style={S.layout}>
      <style>{CSS}</style>

      {/* ═══ MOBILE BACKDROP ═══ */}
      <div className={`sidebar-backdrop ${sidebarOpen ? "visible" : ""}`} onClick={() => setSidebarOpen(false)} />

      {/* ═══ SIDEBAR ═══ */}
      <aside className={`nicai-sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div style={S.sidebarLogo}>
          <div style={S.logoIcon}>N</div>
          <div className="sidebar-label">
            <div style={S.logoTitle}>NICAI</div>
            <div style={S.logoSub}>Deterministic Intelligence System</div>
          </div>
        </div>
        <nav style={S.nav}>
          {NAV_ITEMS.map((n) => (
            <button key={n.key} onClick={() => navigate(n.key)} title={n.label} style={{ ...S.navItem, background: activeNav === n.key ? "linear-gradient(90deg, #1d4ed8, #2563eb)" : "transparent", color: activeNav === n.key ? "#fff" : "#94a3b8" }}>
              <span style={{ width: 20, textAlign: "center", fontSize: 14, opacity: activeNav === n.key ? 1 : 0.6, flexShrink: 0 }}>{n.icon}</span>
              <span className="sidebar-label">{n.label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-label" style={S.traceBox}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#94a3b8", marginBottom: 8 }}>Trace Search</div>
          <div style={{ display: "flex", gap: 6, marginBottom: 12 }}>
            <input style={S.traceInput} placeholder="Enter Trace ID..." value={traceSearch} onChange={(e) => setTraceSearch(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleTraceSearch()} />
            <button style={S.traceSearchBtn} onClick={handleTraceSearch}>⌕</button>
          </div>
          <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>Recent Trace ID</div>
          <div style={{ fontSize: 13, color: "#38bdf8", fontFamily: "'JetBrains Mono', monospace", marginBottom: 10 }}>T20250519-000124</div>
          <button style={S.viewTraceBtn} onClick={handleViewFullTrace}>View Full Trace</button>
        </div>
      </aside>

      {/* ═══ MAIN ═══ */}
      <div style={S.mainWrap}>
        <header className="nicai-header" style={S.header}>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <button onClick={() => setSidebarOpen((p) => !p)} style={{ fontSize: 22, color: "#94a3b8", cursor: "pointer", background: "none", border: "none", padding: 4, lineHeight: 1 }} title={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}>☰</button>
            <div>
              <div style={{ fontSize: 18, fontWeight: 700, color: "#f1f5f9" }}>NICAI Dashboard</div>
              <div className="hide-mobile" style={{ fontSize: 12, color: "#64748b" }}>Real-time Intelligence Overview</div>
            </div>
          </div>
          <div className="header-right" style={{ display: "flex", alignItems: "center", gap: 20, flexWrap: "wrap" }}>
            <div className="hide-mobile" style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: "#94a3b8" }}>
              System Status:<span style={S.statusBadge}>OPERATIONAL</span>
            </div>
            <span className="hide-mobile" style={{ fontSize: 13, color: "#94a3b8" }}>🕐 {timeStr}</span>
            <span className="hide-mobile" style={{ fontSize: 13, color: "#94a3b8" }}>📅 {dateStr}</span>
            <button style={S.refreshBtn} onClick={handleRefresh}>↻ Refresh</button>
          </div>
        </header>

        <main style={S.content}>

          {/* ═══ OVERVIEW ═══ */}
          {activeNav === "overview" && (
            <>
              <div className="stats-row">
                {stats.map((s) => (
                  <div key={s.title} style={S.statCard}>
                    <div style={{ flex: 1 }}>
                      <div style={S.statLabel}>{s.title}</div>
                      <div style={{ ...S.statValue, color: s.color }}>{s.value}</div>
                      <div style={{ ...S.statChange, color: s.color === "#ef4444" || s.color === "#f59e0b" ? s.color : "#22c55e" }}>{s.change}</div>
                    </div>
                    <StatIcon type={s.icon} color={s.color} />
                  </div>
                ))}
              </div>

              <div className="flex-row">
                <div style={{ ...S.card, flex: 3 }}>
                  <SectionHeader title="Recent Signals" btnText="View All" onBtn={() => navigate("signals")} />
                  <div style={{ overflowX: "auto" }}>
                    <table style={S.table}>
                      <thead><tr>{["Signal ID", "Type", "Location", "Risk Level", "Anomaly", "Time", "Action"].map((h) => <th key={h} style={S.th}>{h}</th>)}</tr></thead>
                      <tbody>
                        {signals.map((s) => (
                          <tr key={s.id} style={S.tr}>
                            <td style={S.td}><span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}><span style={{ width: 7, height: 7, borderRadius: "50%", background: "#22c55e", flexShrink: 0 }} />{s.id}</span></td>
                            <td style={S.td}>{s.type}</td>
                            <td style={S.td}>{s.location}</td>
                            <td style={S.td}><RiskBadge level={s.risk} /></td>
                            <td style={S.td}>{s.anomaly}</td>
                            <td style={S.td}>{s.time}</td>
                            <td style={S.td}><button style={S.viewBtn} onClick={() => { setSelectedSignal(s); addLog(`Viewed signal: ${s.id}`, "info"); }}>▸ View</button></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
                <div style={{ ...S.card, flex: 2 }}>
                  <SectionHeader title="Risk Distribution" />
                  <DonutChart />
                  <div style={{ textAlign: "right", fontSize: 11, color: "#475569", marginTop: 8 }}>Last Updated: {refreshedStr}</div>
                </div>
              </div>

              <div className="flex-row three-col">
                <div style={{ ...S.card, flex: 1 }}>
                  <SectionHeader title="Anomaly Trend (Last 7 Days)" btnText="View Details" onBtn={() => navigate("anomalies")} />
                  <TrendChart />
                  <div style={{ display: "flex", justifyContent: "center", gap: 20, marginTop: 8 }}>
                    {[{ label: "High", color: "#ef4444" }, { label: "Medium", color: "#f59e0b" }, { label: "Low", color: "#22c55e" }].map((l) => (
                      <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "#94a3b8" }}>
                        <span style={{ width: 8, height: 8, borderRadius: "50%", background: l.color }} />{l.label}
                      </div>
                    ))}
                  </div>
                </div>
                <div style={{ ...S.card, flex: 1 }}>
                  <SectionHeader title="Active Patterns" btnText="View All" onBtn={() => navigate("patterns")} />
                  <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                    {patterns.map((p) => (
                      <div key={p.id} style={S.patternItem}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                          <span style={{ width: 8, height: 8, borderRadius: "50%", background: RISK_COLORS[p.risk] }} />
                          <span style={{ fontSize: 12, color: "#cbd5e1", fontFamily: "'JetBrains Mono', monospace" }}>{p.id}</span>
                        </div>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
                          <span style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0" }}>{p.type}</span>
                          <RiskBadge level={p.risk} />
                        </div>
                        <div style={{ fontSize: 12, color: "#64748b" }}><strong style={{ color: "#94a3b8" }}>Affected Zones:</strong> {p.zones}</div>
                        <div style={{ fontSize: 12, color: "#64748b" }}><strong style={{ color: "#94a3b8" }}>Anomaly Count:</strong> {p.count}</div>
                      </div>
                    ))}
                  </div>
                </div>
                <div style={{ ...S.card, flex: 1 }}>
                  <SectionHeader title="Recent Actions" btnText="View All" onBtn={() => navigate("actions")} />
                  <div style={{ overflowX: "auto" }}>
                    <table style={S.table}>
                      <thead><tr>{["Trace ID", "Action", "Target Role", "Time", "Status"].map((h) => <th key={h} style={S.th}>{h}</th>)}</tr></thead>
                      <tbody>
                        {ACTIONS.map((a) => (
                          <tr key={a.traceId} style={S.tr}>
                            <td style={{ ...S.td, fontFamily: "'JetBrains Mono', monospace", fontSize: 11 }}>{a.traceId}</td>
                            <td style={S.td}>{a.action}</td>
                            <td style={S.td}>{a.target}</td>
                            <td style={S.td}>{a.time}</td>
                            <td style={S.td}><span style={S.loggedBadge}>Logged</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* ═══ signals (Pipeline) ═══ */}
          {activeNav === "signals" && (
            <>
              <div style={{ ...S.card, marginBottom: 20 }}>
                <SectionHeader title="Intelligence Pipeline — Samachar → Mitra" />
                <div style={{ display: "flex", gap: 10, marginBottom: 14, flexWrap: "wrap" }}>
                  <button style={S.scenarioBtn} onClick={() => setPipelineInput(MARITIME_SCENARIO)}>⚓ Load Maritime Scenario</button>
                  <button style={S.scenarioBtn} onClick={() => setPipelineInput(ENVIRONMENTAL_SCENARIO)}>🌊 Load Environmental Scenario</button>
                </div>
                <textarea value={pipelineInput} onChange={(e) => setPipelineInput(e.target.value)} rows={5} placeholder="Enter scenario text or load a preset above..." style={S.textarea} />
                <div style={{ display: "flex", gap: 10, marginTop: 14, alignItems: "center", flexWrap: "wrap" }}>
                  <button onClick={handleProcess} disabled={pipelineLoading} style={{ ...S.processBtn, opacity: pipelineLoading ? 0.7 : 1, cursor: pipelineLoading ? "not-allowed" : "pointer" }}>
                    {pipelineLoading && <span style={S.spinner} />}
                    {pipelineLoading ? (pipelineStep === "samachar" ? "Processing Samachar..." : "Processing Mitra...") : "▸ Process Pipeline"}
                  </button>
                  {pipelineStep === "done" && <span style={{ ...S.loggedBadge, fontSize: 12 }}>Pipeline Complete ✓</span>}
                </div>
              </div>
              <div className="flex-row">
                <div style={{ ...S.card, flex: 1 }}>
                  <SectionHeader title="Samachar Output" />
                  {samacharError && <div style={S.errorBox}>{samacharError}</div>}
                  {samacharResult && <pre style={S.jsonPre}>{JSON.stringify(samacharResult, null, 2)}</pre>}
                  {!samacharError && !samacharResult && <div style={S.emptyState}>📡<br /><span style={{ color: "#475569", fontSize: 13 }}>Awaiting pipeline execution.</span></div>}
                </div>
                <div style={{ ...S.card, flex: 1 }}>
                  <SectionHeader title="Mitra Output" />
                  {mitraError && <div style={S.errorBox}>{mitraError}</div>}
                  {mitraResult && <pre style={S.jsonPre}>{JSON.stringify(mitraResult, null, 2)}</pre>}
                  {!mitraError && !mitraResult && <div style={S.emptyState}>🛡️<br /><span style={{ color: "#475569", fontSize: 13 }}>Waiting for Samachar extraction.</span></div>}
                </div>
              </div>
              <div style={S.card}>
                <SectionHeader title="All Signals" />
                <div style={{ overflowX: "auto" }}>
                  <table style={S.table}>
                    <thead><tr>{["Signal ID", "Type", "Location", "Risk Level", "Anomaly", "Time", "Action"].map((h) => <th key={h} style={S.th}>{h}</th>)}</tr></thead>
                    <tbody>
                      {signals.map((s) => (
                        <tr key={s.id} style={S.tr}>
                          <td style={S.td}><span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}><span style={{ width: 7, height: 7, borderRadius: "50%", background: "#22c55e", flexShrink: 0 }} />{s.id}</span></td>
                          <td style={S.td}>{s.type}</td>
                          <td style={S.td}>{s.location}</td>
                          <td style={S.td}><RiskBadge level={s.risk} /></td>
                          <td style={S.td}>{s.anomaly}</td>
                          <td style={S.td}>{s.time}</td>
                          <td style={S.td}><button style={S.viewBtn} onClick={() => { setSelectedSignal(s); addLog(`Viewed signal: ${s.id}`, "info"); }}>▸ View</button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {/* ═══ ANOMALIES ═══ */}
          {activeNav === "anomalies" && (
            <>
              <div style={{ ...S.card, marginBottom: 20 }}>
                <SectionHeader title="Anomaly Trend — Last 7 Days" />
                <TrendChart />
                <div style={{ display: "flex", justifyContent: "center", gap: 20, marginTop: 12 }}>
                  {[{ label: "High", color: "#ef4444" }, { label: "Medium", color: "#f59e0b" }, { label: "Low", color: "#22c55e" }].map((l) => (
                    <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "#94a3b8" }}>
                      <span style={{ width: 10, height: 10, borderRadius: "50%", background: l.color }} />{l.label}
                    </div>
                  ))}
                </div>
              </div>
              <div style={S.card}>
                <SectionHeader title="Anomaly Events" />
                <div style={{ overflowX: "auto" }}>
                  <table style={S.table}>
                    <thead><tr>{["Signal ID", "Type", "Location", "Risk Level", "Anomaly", "Time", "Action"].map((h) => <th key={h} style={S.th}>{h}</th>)}</tr></thead>
                    <tbody>
                      {signals.filter((s) => s.anomaly !== "NORMAL").map((s) => (
                        <tr key={s.id} style={S.tr}>
                          <td style={S.td}>{s.id}</td><td style={S.td}>{s.type}</td><td style={S.td}>{s.location}</td>
                          <td style={S.td}><RiskBadge level={s.risk} /></td><td style={S.td}>{s.anomaly}</td><td style={S.td}>{s.time}</td>
                          <td style={S.td}><button style={S.viewBtn} onClick={() => setSelectedSignal(s)}>▸ View</button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {/* ═══ patterns ═══ */}
          {activeNav === "patterns" && (
            <div className="patterns-grid">
              {patterns.map((p) => (
                <div key={p.id} style={S.card}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                    <span style={{ width: 10, height: 10, borderRadius: "50%", background: RISK_COLORS[p.risk] }} />
                    <span style={{ fontSize: 13, color: "#cbd5e1", fontFamily: "'JetBrains Mono', monospace" }}>{p.id}</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
                    <span style={{ fontSize: 16, fontWeight: 700, color: "#e2e8f0" }}>{p.type}</span>
                    <RiskBadge level={p.risk} />
                  </div>
                  <InfoRow label="Affected Zones">{p.zones}</InfoRow>
                  <InfoRow label="Anomaly Count"><span style={{ fontWeight: 700, color: RISK_COLORS[p.risk] }}>{p.count}</span></InfoRow>
                  <InfoRow label="Status"><span style={S.loggedBadge}>Active</span></InfoRow>
                </div>
              ))}
            </div>
          )}

          {/* ═══ ACTIONS ═══ */}
          {activeNav === "actions" && (
            <div style={S.card}>
              <SectionHeader title="All Actions & Decisions" />
              <div style={{ overflowX: "auto" }}>
                <table style={S.table}>
                  <thead><tr>{["Trace ID", "Action", "Target Role", "Time", "Status"].map((h) => <th key={h} style={S.th}>{h}</th>)}</tr></thead>
                  <tbody>
                    {ACTIONS.map((a) => (
                      <tr key={a.traceId} style={{ ...S.tr, cursor: "pointer" }} onClick={() => { setSelectedTrace(a); addLog(`Viewed trace: ${a.traceId}`, "info"); }}>
                        <td style={{ ...S.td, fontFamily: "'JetBrains Mono', monospace", fontSize: 11 }}>{a.traceId}</td>
                        <td style={S.td}>{a.action}</td><td style={S.td}>{a.target}</td><td style={S.td}>{a.time}</td>
                        <td style={S.td}><span style={S.loggedBadge}>Logged</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ═══ LOGS ═══ */}
          {activeNav === "logs" && (
            <div style={S.card}>
              <SectionHeader title="Activity Log" btnText="Clear" onBtn={() => setLogs([])} />
              {logs.length === 0 && <div style={S.emptyState}>📋<br /><span style={{ color: "#475569", fontSize: 13 }}>No activity logged yet.</span></div>}
              <div style={{ overflowX: "auto" }}>
                <table style={S.table}>
                  <thead><tr>{["Time", "Type", "Message"].map((h) => <th key={h} style={S.th}>{h}</th>)}</tr></thead>
                  <tbody>
                    {logs.map((l, i) => (
                      <tr key={i} style={S.tr}>
                        <td style={{ ...S.td, fontFamily: "'JetBrains Mono', monospace", fontSize: 11, whiteSpace: "nowrap" }}>{l.time.toLocaleTimeString()}</td>
                        <td style={S.td}>
                          <span style={{ padding: "2px 10px", borderRadius: 4, fontSize: 10, fontWeight: 700, color: l.type === "error" ? "#ef4444" : l.type === "api" ? "#3b82f6" : l.type === "nav" ? "#8b5cf6" : l.type === "search" ? "#f59e0b" : "#22c55e", background: l.type === "error" ? "rgba(239,68,68,0.1)" : l.type === "api" ? "rgba(59,130,246,0.1)" : l.type === "nav" ? "rgba(139,92,246,0.1)" : l.type === "search" ? "rgba(245,158,11,0.1)" : "rgba(34,197,94,0.1)" }}>
                            {l.type.toUpperCase()}
                          </span>
                        </td>
                        <td style={S.td}>{l.msg}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ═══ HEALTH ═══ */}
          {activeNav === "health" && (
            <>
              <div className="health-grid">
                {[
                  { name: "NICAI API", url: NICAI_API || "Not configured (set VITE_NICAI_API)", status: healthStatus.nicai },
                  { name: "Samachar API", url: samacharUrl || "Not configured", status: healthStatus.samachar },
                  { name: "Mitra API", url: mitraUrl || "Not configured", status: healthStatus.mitra },
                ].map((api) => (
                  <div key={api.name} style={S.card}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14, flexWrap: "wrap", gap: 8 }}>
                      <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: "#e2e8f0" }}>{api.name}</h3>
                      {api.status && (
                        <span style={{
                          padding: "3px 12px", borderRadius: 4, fontSize: 11, fontWeight: 700,
                          color: api.status === "online" ? "#22c55e" : api.status === "not_configured" ? "#94a3b8" : "#ef4444",
                          background: api.status === "online" ? "rgba(34,197,94,0.1)" : api.status === "not_configured" ? "rgba(148,163,184,0.1)" : "rgba(239,68,68,0.1)",
                          border: `1px solid ${api.status === "online" ? "rgba(34,197,94,0.25)" : api.status === "not_configured" ? "rgba(148,163,184,0.25)" : "rgba(239,68,68,0.25)"}`,
                        }}>
                          {api.status === "online" ? "ONLINE" : api.status === "offline" ? "OFFLINE" : api.status === "not_configured" ? "NOT SET" : "ERROR"}
                        </span>
                      )}
                    </div>
                    <InfoRow label="Endpoint">{api.url}</InfoRow>
                    <InfoRow label="Status">
                      {api.status === "online" ? "Connected & responding" : api.status === "not_configured" ? "Environment variable not set" : api.status ? "Unreachable" : "Not checked yet"}
                    </InfoRow>
                  </div>
                ))}
              </div>
              <button onClick={checkHealth} disabled={checkingHealth} style={{ ...S.processBtn, maxWidth: 260, opacity: checkingHealth ? 0.7 : 1, cursor: checkingHealth ? "not-allowed" : "pointer" }}>
                {checkingHealth ? <><span style={S.spinner} />Checking...</> : "▸ Run Health Check"}
              </button>
            </>
          )}

          {/* ═══ SETTINGS ═══ */}
          {activeNav === "settings" && (
            <div style={S.card}>
              <SectionHeader title="API Configuration" />
              <div style={{ marginBottom: 20 }}><label style={S.settingsLabel}>Samachar API Base URL</label><input style={S.settingsInput} value={samacharUrl} onChange={(e) => setSamacharUrl(e.target.value)} /></div>
              <div style={{ marginBottom: 20 }}><label style={S.settingsLabel}>Mitra API Base URL</label><input style={S.settingsInput} value={mitraUrl} onChange={(e) => setMitraUrl(e.target.value)} /></div>
              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <button style={S.processBtn} onClick={() => addLog(`API URLs updated — Samachar: ${samacharUrl}, Mitra: ${mitraUrl}`, "system")}>Save Configuration</button>
                <button style={{ ...S.scenarioBtn, padding: "10px 20px" }} onClick={() => { setSamacharUrl(DEFAULT_SAMACHAR); setMitraUrl(DEFAULT_MITRA); addLog("API URLs reset to defaults", "system"); }}>Reset Defaults</button>
              </div>
            </div>
          )}
        </main>

        <footer className="nicai-footer">
          <span style={{ fontWeight: 600 }}>NICAI v2.0.0</span>
          <span className="footer-divider" />
          <span>✔ Deterministic</span>
          <span className="footer-divider" />
          <span>✔ Traceable</span>
          <span className="footer-divider" />
          <span>✔ Explainable</span>
          <span className="footer-divider" />
          <span>✔ TANTRA Compliant</span>
          <span style={{ marginLeft: "auto" }}>© 2025 NICAI System</span>
        </footer>
      </div>

      {/* ═══ MODALS ═══ */}
      {selectedSignal && (
        <Modal title="Signal Details" onClose={() => setSelectedSignal(null)}>
          <InfoRow label="Signal ID"><span style={{ fontFamily: "'JetBrains Mono', monospace" }}>{selectedSignal.id}</span></InfoRow>
          <InfoRow label="Type">{selectedSignal.type}</InfoRow>
          <InfoRow label="Location">{selectedSignal.location}</InfoRow>
          <InfoRow label="Risk Level"><RiskBadge level={selectedSignal.risk} /></InfoRow>
          <InfoRow label="Anomaly">{selectedSignal.anomaly}</InfoRow>
          <InfoRow label="Time">{selectedSignal.time}</InfoRow>
          <InfoRow label="Status"><span style={S.loggedBadge}>Active</span></InfoRow>
          <div style={{ marginTop: 16, padding: 14, borderRadius: 8, background: "#0a0f1e", border: "1px solid #151d2e", fontSize: 13, color: "#94a3b8", lineHeight: 1.7 }}>
            <strong style={{ color: "#cbd5e1" }}>Analysis:</strong><br />{selectedSignal.details}
          </div>
        </Modal>
      )}
      {selectedTrace && (
        <Modal title="Trace Details" onClose={() => setSelectedTrace(null)}>
          <InfoRow label="Trace ID"><span style={{ fontFamily: "'JetBrains Mono', monospace", color: "#38bdf8" }}>{selectedTrace.traceId}</span></InfoRow>
          <InfoRow label="Action">{selectedTrace.action}</InfoRow>
          <InfoRow label="Target Role">{selectedTrace.target}</InfoRow>
          <InfoRow label="Time">{selectedTrace.time}</InfoRow>
          <InfoRow label="Status"><span style={S.loggedBadge}>Logged</span></InfoRow>
        </Modal>
      )}
    </div>
  );
}



// ── CSS with responsive breakpoints ──────────────────────────────────────────

const CSS = `
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #060b18; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
  ::selection { background: rgba(59,130,246,0.4); }
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: #334155; }
  table { border-collapse: collapse; }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Sidebar ── */
  .nicai-sidebar {
    width: 240px; flex-shrink: 0; background: #0a0e1a; border-right: 1px solid #111827;
    display: flex; flex-direction: column; position: sticky; top: 0; height: 100vh;
    overflow-y: auto; overflow-x: hidden; transition: width 0.25s ease;
    z-index: 50;
  }
  .nicai-sidebar.closed {
    width: 60px;
  }
  .nicai-sidebar.closed .sidebar-label {
    display: none;
  }
  .sidebar-backdrop { display: none; pointer-events: none; }

  /* ── Grids (desktop defaults) ── */
  .stats-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 20px; }
  .flex-row { display: flex; gap: 16px; margin-bottom: 20px; }
  .patterns-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
  .health-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }

  /* ── Footer ── */
  .nicai-footer {
    display: flex; align-items: center; gap: 16px; padding: 14px 24px;
    border-top: 1px solid #111827; font-size: 12px; color: #475569; flex-wrap: wrap;
  }
  .footer-divider { width: 1px; height: 14px; background: #1e293b; }

  /* ══════════════ TABLET (≤1024px) ══════════════ */
  @media (max-width: 1024px) {
    .stats-row { grid-template-columns: repeat(3, 1fr); }
    .flex-row.three-col { flex-direction: column; }
    .patterns-grid { grid-template-columns: repeat(2, 1fr); }
  }

  /* ══════════════ MOBILE (≤768px) ══════════════ */
  @media (max-width: 768px) {
    .nicai-sidebar {
      position: fixed; top: 0; left: 0; width: 260px; height: 100vh;
      transform: translateX(-100%); transition: transform 0.25s ease;
      z-index: 60; box-shadow: none;
    }
    .nicai-sidebar.open {
      transform: translateX(0);
      box-shadow: 8px 0 32px rgba(0,0,0,0.5);
      width: 260px;
    }
    .nicai-sidebar.open .sidebar-label { display: block; }
    .nicai-sidebar.closed { transform: translateX(-100%); width: 260px; }

    .sidebar-backdrop.visible {
      display: block; position: fixed; inset: 0; background: rgba(0,0,0,0.5);
      z-index: 55; backdrop-filter: blur(2px); pointer-events: auto;
    }

    .stats-row { grid-template-columns: repeat(2, 1fr); }
    .flex-row { flex-direction: column; }
    .patterns-grid { grid-template-columns: 1fr; }
    .health-grid { grid-template-columns: 1fr; }

    .hide-mobile { display: none !important; }

    .nicai-header { padding: 10px 14px !important; }
    .header-right { gap: 10px !important; }

    .nicai-footer { justify-content: center; text-align: center; gap: 10px; padding: 12px 16px; }
    .nicai-footer > span:last-child { margin-left: 0 !important; }
    .footer-divider { display: none; }

    .nicai-modal { width: 95% !important; max-height: 90vh !important; }
  }

  /* ══════════════ SMALL MOBILE (≤480px) ══════════════ */
  @media (max-width: 480px) {
    .stats-row { grid-template-columns: 1fr; }
  }
`;

// ── Styles (non-responsive properties) ───────────────────────────────────────

const S = {
  layout: { display: "flex", minHeight: "100vh", background: "#060b18", color: "#e2e8f0", fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif" },
  sidebarLogo: { display: "flex", alignItems: "center", gap: 12, padding: "20px 12px", borderBottom: "1px solid #111827", overflow: "hidden" },
  logoIcon: { width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg, #3b82f6, #2563eb)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 800, color: "#fff", flexShrink: 0, boxShadow: "0 0 16px rgba(59,130,246,0.3)" },
  logoTitle: { fontSize: 17, fontWeight: 700, color: "#f1f5f9", letterSpacing: 1.2, whiteSpace: "nowrap" },
  logoSub: { fontSize: 9, color: "#64748b", fontWeight: 500, letterSpacing: 0.3, marginTop: 1, whiteSpace: "nowrap" },
  nav: { display: "flex", flexDirection: "column", gap: 2, padding: "12px 8px", flex: 1 },
  navItem: { display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", borderRadius: 8, border: "none", fontSize: 13, fontWeight: 500, cursor: "pointer", fontFamily: "inherit", textAlign: "left", whiteSpace: "nowrap", overflow: "hidden" },
  traceBox: { padding: "16px 12px", borderTop: "1px solid #111827" },
  traceInput: { flex: 1, padding: "7px 10px", borderRadius: 6, border: "1px solid #1e293b", background: "#0f172a", color: "#e2e8f0", fontSize: 12, fontFamily: "inherit", outline: "none", minWidth: 0 },
  traceSearchBtn: { width: 32, borderRadius: 6, border: "1px solid #1e293b", background: "#0f172a", color: "#64748b", fontSize: 16, cursor: "pointer", flexShrink: 0 },
  viewTraceBtn: { width: "100%", padding: "8px 0", borderRadius: 8, border: "1px solid #2563eb", background: "transparent", color: "#60a5fa", fontSize: 13, fontWeight: 600, cursor: "pointer", fontFamily: "inherit" },

  header: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 24px", borderBottom: "1px solid #111827", background: "rgba(6,11,24,0.85)", backdropFilter: "blur(12px)", position: "sticky", top: 0, zIndex: 40, flexWrap: "wrap", gap: 12 },
  statusBadge: { display: "inline-block", padding: "3px 12px", borderRadius: 4, fontSize: 11, fontWeight: 700, letterSpacing: 0.8, color: "#22c55e", background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.25)" },
  refreshBtn: { padding: "7px 16px", borderRadius: 8, border: "none", background: "linear-gradient(135deg, #2563eb, #1d4ed8)", color: "#fff", fontSize: 13, fontWeight: 600, cursor: "pointer", fontFamily: "inherit", boxShadow: "0 0 16px rgba(37,99,235,0.2)", whiteSpace: "nowrap" },

  content: { padding: 20, flex: 1, overflowY: "auto" },
  mainWrap: { flex: 1, display: "flex", flexDirection: "column", minWidth: 0 },

  statCard: { display: "flex", alignItems: "center", gap: 12, padding: "18px 20px", borderRadius: 12, background: "#0d1424", border: "1px solid #151d2e" },
  statLabel: { fontSize: 11, fontWeight: 600, color: "#64748b", letterSpacing: 0.8, marginBottom: 6 },
  statValue: { fontSize: 28, fontWeight: 700, lineHeight: 1, marginBottom: 6 },
  statChange: { fontSize: 11, fontWeight: 500 },

  card: { background: "#0d1424", border: "1px solid #151d2e", borderRadius: 12, padding: 20 },
  table: { width: "100%", fontSize: 13 },
  th: { textAlign: "left", padding: "8px 10px", color: "#64748b", fontWeight: 600, fontSize: 11, letterSpacing: 0.5, borderBottom: "1px solid #1e293b", whiteSpace: "nowrap" },
  tr: { borderBottom: "1px solid #111827" },
  td: { padding: "10px 10px", color: "#cbd5e1", fontSize: 12, whiteSpace: "nowrap" },
  viewBtn: { padding: "4px 12px", borderRadius: 5, border: "1px solid #1e3a5f", background: "transparent", color: "#60a5fa", fontSize: 11, fontWeight: 500, cursor: "pointer", fontFamily: "inherit" },
  loggedBadge: { display: "inline-block", padding: "3px 10px", borderRadius: 4, fontSize: 11, fontWeight: 600, color: "#22c55e", background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.2)" },
  patternItem: { padding: 14, borderRadius: 10, background: "#0a0f1e", border: "1px solid #151d2e" },

  scenarioBtn: { padding: "9px 16px", borderRadius: 8, border: "1px solid #1e293b", background: "#0f172a", color: "#94a3b8", fontSize: 13, fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 8, fontFamily: "inherit" },
  textarea: { width: "100%", minHeight: 120, padding: 14, borderRadius: 8, border: "1px solid #1e293b", background: "#0f172a", color: "#e2e8f0", fontSize: 14, fontFamily: "inherit", lineHeight: 1.6, resize: "vertical", outline: "none" },
  processBtn: { padding: "12px 24px", borderRadius: 8, border: "none", background: "linear-gradient(135deg, #2563eb, #1d4ed8)", color: "#fff", fontSize: 14, fontWeight: 600, fontFamily: "inherit", display: "flex", alignItems: "center", gap: 10, cursor: "pointer", boxShadow: "0 0 24px rgba(37,99,235,0.25)" },
  spinner: { width: 16, height: 16, border: "2px solid rgba(255,255,255,0.25)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.7s linear infinite", flexShrink: 0 },
  errorBox: { padding: "12px 16px", borderRadius: 8, background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)", color: "#f87171", fontSize: 13, fontWeight: 500, fontFamily: "'JetBrains Mono', monospace" },
  jsonPre: { margin: 0, padding: 16, borderRadius: 8, background: "#0a0f1e", border: "1px solid #151d2e", color: "#7dd3fc", fontSize: 12.5, lineHeight: 1.7, fontFamily: "'JetBrains Mono', monospace", overflowX: "auto", whiteSpace: "pre-wrap", wordBreak: "break-word" },
  emptyState: { padding: "40px 16px", textAlign: "center", fontSize: 28, opacity: 0.5 },

  settingsLabel: { display: "block", fontSize: 13, fontWeight: 600, color: "#94a3b8", marginBottom: 8 },
  settingsInput: { width: "100%", padding: "10px 14px", borderRadius: 8, border: "1px solid #1e293b", background: "#0f172a", color: "#e2e8f0", fontSize: 14, fontFamily: "'JetBrains Mono', monospace", outline: "none" },

  modalOverlay: { position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 },
  modal: { background: "#0d1424", border: "1px solid #1e293b", borderRadius: 16, padding: 0, width: "90%", maxWidth: 520, maxHeight: "85vh", overflowY: "auto", boxShadow: "0 24px 64px rgba(0,0,0,0.5)" },
  modalHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "18px 24px", borderBottom: "1px solid #151d2e" },
  modalClose: { width: 32, height: 32, borderRadius: 8, border: "1px solid #1e293b", background: "transparent", color: "#64748b", fontSize: 16, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "inherit" },
  modalBody: { padding: "16px 24px 24px" },
};
