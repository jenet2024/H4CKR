import { useState, useEffect, useRef } from "react";
import { useAuth } from "../hooks/useAuth";
import { getToken } from "../api/client";

const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function adminFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${getToken()}`, ...(options.headers as any) },
  });
  if (!res.ok) { const e = await res.json().catch(() => ({ detail: "Erreur" })); throw e; }
  return res.json();
}

interface Stats { total_users: number; total_scores: number; total_badges_earned: number; total_levels: number; total_enigmas: number; top_player: string|null; top_score: number; }
interface AdminUser { id: number; pseudo: string; email: string; is_admin: boolean; is_active: boolean; is_verified: boolean; auth_provider: string; created_at: string; total_points: number; badges_count: number; }
interface AdminLevel { id: number; slug: string; name: string; order: number; is_active: boolean; max_points: number; enigmas_count: number; }
interface AdminCert { id: number; unique_code: string; level: string; score: number; issued_at: string; user_pseudo: string; user_email: string; }
interface AdminBadge { id: number; slug: string; name: string; icon: string; color: string; points_reward: number; earned_count: number; }

// ── Mini Bar Chart ────────────────────────────────────────────────
function BarChart({ data, color = "#00ff41", label, theme }: { data: { label: string; value: number }[]; color?: string; label: string; theme: any }) {
  const max = Math.max(...data.map(d => d.value), 1);
  return (
    <div>
      <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 10, color: theme.textMuted, letterSpacing: 2, marginBottom: 12 }}>{label}</div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 80 }}>
        {data.map((d, i) => (
          <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
            <div style={{ fontSize: 9, color: color === "#00ff41" ? theme.primary : color, fontFamily: "monospace" }}>{d.value}</div>
            <div style={{ width: "100%", height: `${(d.value / max) * 64}px`, background: `linear-gradient(180deg, ${color === "#00ff41" ? theme.primary : color}, ${color === "#00ff41" ? theme.primary : color}44)`, borderRadius: "3px 3px 0 0", transition: "height 1s ease", minHeight: 4, position: "relative", overflow: "hidden" }}>
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "30%", background: `${color}30`, borderRadius: "3px 3px 0 0" }} />
            </div>
            <div style={{ fontSize: 8, color: theme.textMuted, fontFamily: "monospace", textAlign: "center", maxWidth: 40, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{d.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Donut Chart ───────────────────────────────────────────────────
function DonutChart({ segments, size = 120, theme }: { segments: { label: string; value: number; color: string }[]; size?: number; theme: any }) {
  const total = segments.reduce((s, d) => s + d.value, 0) || 1;
  const r = 40; const cx = size / 2; const cy = size / 2;
  let angle = -Math.PI / 2;
  const arcs = segments.map(seg => {
    const sweep = (seg.value / total) * 2 * Math.PI;
    const x1 = cx + r * Math.cos(angle), y1 = cy + r * Math.sin(angle);
    angle += sweep;
    const x2 = cx + r * Math.cos(angle), y2 = cy + r * Math.sin(angle);
    const large = sweep > Math.PI ? 1 : 0;
    return { ...seg, d: `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} Z`, pct: Math.round((seg.value / total) * 100) };
  });
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
      <svg width={size} height={size}>
        <circle cx={cx} cy={cy} r={r + 2} fill="none" stroke={theme.borderLight} strokeWidth={1} />
        {arcs.map((a, i) => <path key={i} d={a.d} fill={a.color === "#00ff41" ? theme.primary : a.color} opacity={0.85} />)}
        <circle cx={cx} cy={cy} r={26} fill={theme.cardBgInternal} />
        <text x={cx} y={cy + 4} textAnchor="middle" fill={theme.primary} fontSize={14} fontFamily="'Orbitron',sans-serif" fontWeight="bold">{total}</text>
      </svg>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {arcs.map((a, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 8, height: 8, borderRadius: 2, background: a.color === "#00ff41" ? theme.primary : a.color, flexShrink: 0 }} />
            <span style={{ fontSize: 10, color: theme.textMuted, fontFamily: "monospace" }}>{a.label}</span>
            <span style={{ fontSize: 10, color: a.color === "#00ff41" ? theme.primary : a.color, fontFamily: "'Orbitron',sans-serif", marginLeft: "auto" }}>{a.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Sparkline ─────────────────────────────────────────────────────
function Sparkline({ values, color = "#00ff41", width = 120, height = 36 }: { values: number[]; color?: string; width?: number; height?: number }) {
  if (values.length < 2) return null;
  const max = Math.max(...values); const min = Math.min(...values);
  const range = max - min || 1;
  const pts = values.map((v, i) => `${(i / (values.length - 1)) * width},${height - ((v - min) / range) * (height - 4) - 2}`).join(" ");
  return (
    <svg width={width} height={height}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      <polyline points={`0,${height} ${pts} ${width},${height}`} fill={`${color}18`} stroke="none" />
    </svg>
  );
}

// ── Stat Card ─────────────────────────────────────────────────────
function StatCard({ label, value, icon, color = "#00ff41", sub, trend, theme }: { label: string; value: any; icon: string; color?: string; sub?: string; trend?: number[]; theme: any }) {
  const finalColor = color === "#00ff41" ? theme.primary : color;
  return (
    <div style={{ background: theme.cardBg, border: `1px solid ${theme.isDark ? finalColor + '25' : 'rgba(0,0,0,0.08)'}`, boxShadow: theme.isDark ? 'none' : '0 2px 8px rgba(0,0,0,0.04)', borderRadius: 8, padding: "18px 20px", position: "relative", overflow: "hidden", animation: "fadeUp .4s ease" }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg,transparent,${finalColor}70,transparent)` }} />
      <div style={{ position: "absolute", bottom: 0, right: 0, opacity: 0.04, fontSize: 80, color: theme.text }}>{icon}</div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 9, color: theme.textMuted, letterSpacing: 3, marginBottom: 8 }}>{label}</div>
          <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 28, fontWeight: 900, color: finalColor, lineHeight: 1 }}>{value}</div>
          {sub && <div style={{ fontSize: 10, color: theme.textMuted, marginTop: 6, fontFamily: "monospace" }}>{sub}</div>}
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          <div style={{ fontSize: 26, filter: theme.isDark ? `drop-shadow(0 0 8px ${finalColor}60)` : "none" }}>{icon}</div>
          {trend && <Sparkline values={trend} color={finalColor} />}
        </div>
      </div>
    </div>
  );
}

// ── Confirm ───────────────────────────────────────────────────────
function Confirm({ msg, onOk, onCancel, theme }: { msg: string; onOk: () => void; onCancel: () => void; theme: any }) {
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 9999, background: "rgba(0,0,0,0.75)", display: "flex", alignItems: "center", justifyContent: "center", backdropFilter: "blur(4px)" }}>
      <div style={{ background: theme.cardBg, border: "1px solid rgba(255,0,60,0.4)", boxShadow: "0 10px 30px rgba(0,0,0,0.3)", borderRadius: 10, padding: "32px 36px", maxWidth: 400, textAlign: "center" }}>
        <div style={{ fontSize: 36, marginBottom: 14 }}>⚠️</div>
        <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 11, color: "#ff6060", marginBottom: 22, lineHeight: 1.7 }}>{msg}</div>
        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
          <button onClick={onCancel} style={{ background: "transparent", border: `1px solid ${theme.border}`, color: theme.textMuted, padding: "8px 18px", borderRadius: 4, cursor: "pointer", fontFamily: "'Orbitron',sans-serif", fontSize: 10, letterSpacing: 2 }}>ANNULER</button>
          <button onClick={onOk} style={{ background: "rgba(255,0,60,0.12)", border: "1px solid rgba(255,0,60,0.5)", color: "#ff6060", padding: "8px 18px", borderRadius: 4, cursor: "pointer", fontFamily: "'Orbitron',sans-serif", fontSize: 10, letterSpacing: 2 }}>CONFIRMER</button>
        </div>
      </div>
    </div>
  );
}

// ── Toast ─────────────────────────────────────────────────────────
function useToast(theme: any) {
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const show = (msg: string, ok = true) => { setToast({ msg, ok }); setTimeout(() => setToast(null), 3000); };
  const Toast = toast ? (
    <div style={{ position: "fixed", top: 72, right: 24, zIndex: 8888, background: toast.ok ? (theme.isDark ? "rgba(0,20,0,0.97)" : "#e6fbee") : (theme.isDark ? "rgba(20,0,0,0.97)" : "#fce8e6"), border: `1px solid ${toast.ok ? theme.primary : "#ff003c"}`, borderRadius: 6, padding: "12px 20px", color: toast.ok ? theme.primary : "#ff003c", fontFamily: "'Orbitron',sans-serif", fontSize: 11, letterSpacing: 2, animation: "fadeIn .2s ease", boxShadow: `0 4px 20px ${toast.ok ? "rgba(0,255,65,.2)" : "rgba(255,0,60,.2)"}` }}>
      {toast.ok ? "✓" : "✕"} {toast.msg}
    </div>
  ) : null;
  return { show, Toast };
}

// ── Dashboard Tab ─────────────────────────────────────────────────
function DashboardTab({ stats, users, levels, badges, theme }: { stats: Stats | null; users: AdminUser[]; levels: AdminLevel[]; badges: AdminBadge[]; theme: any }) {
  if (!stats) return <div style={{ textAlign: "center", padding: 60, color: theme.primary, opacity: 0.5, fontFamily: "monospace" }}>Chargement...</div>;

  const topUsers = [...users].sort((a, b) => b.total_points - a.total_points).slice(0, 5);
  const providerData = [
    { label: "Local", value: users.filter(u => u.auth_provider === "local").length, color: "#00ff41" },
    { label: "Google", value: users.filter(u => u.auth_provider === "google").length, color: "#00e5ff" },
    { label: "Twitter", value: users.filter(u => u.auth_provider === "twitter").length, color: "#cc44ff" },
  ].filter(d => d.value > 0);

  const badgeBarData = badges.slice(0, 6).map(b => ({ label: b.icon + " " + b.name.slice(0, 6), value: b.earned_count }));
  const trendFake = [2, 5, 3, 8, 6, 12, 9, 15, 11, 18];

  return (
    <div style={{ animation: "fadeUp .3s ease" }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ color: "rgba(255,0,60,0.75)", fontFamily: "'Orbitron',sans-serif", fontSize: 9, letterSpacing: 4, marginBottom: 6 }}>● SYSTÈME ACTIF — ACCÈS NIVEAU ALPHA</div>
        <h1 style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 24, fontWeight: 900, color: theme.primary, letterSpacing: 4, textShadow: theme.isDark ? "0 0 20px rgba(0,255,65,.35)" : "none" }}>TABLEAU DE BORD</h1>
        <div style={{ color: theme.textMuted, fontSize: 11, marginTop: 6, fontFamily: "monospace" }}>Vue d'ensemble du système H4CKR en temps réel</div>
      </div>

      {/* Stat cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(200px,1fr))", gap: 14, marginBottom: 24 }}>
        <StatCard label="AGENTS" value={stats.total_users} icon="👤" color="#00ff41" sub="utilisateurs inscrits" trend={trendFake} theme={theme} />
        <StatCard label="PARTIES JOUÉES" value={stats.total_scores} icon="🎮" color="#00e5ff" sub="scores enregistrés" trend={[1,3,2,6,5,8,7,10]} theme={theme} />
        <StatCard label="BADGES GAGNÉS" value={stats.total_badges_earned} icon="🏅" color="#ffd700" sub="récompenses obtenues" trend={[0,1,3,2,5,4,7,9]} theme={theme} />
        <StatCard label="NIVEAUX" value={stats.total_levels} icon="🗂️" color="#ff9900" sub={`${stats.total_enigmas} énigmes`} theme={theme} />
        {stats.top_player && <StatCard label="TOP AGENT" value={stats.top_player} icon="🥇" color="#ffd700" sub={`${stats.top_score.toLocaleString()} pts`} theme={theme} />}
        <StatCard label="ADMINS" value={users.filter(u => u.is_admin).length} icon="👑" color="#ff003c" sub="administrateurs" theme={theme} />
      </div>

      {/* Row charts */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 24 }}>
        {/* Providers */}
        <div style={{ background: theme.cardBg, border: `1px solid ${theme.border}`, borderRadius: 8, padding: 20 }}>
          <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 10, color: theme.primary, opacity: 0.8, letterSpacing: 2, marginBottom: 16 }}>🔐 PROVIDERS AUTH</div>
          <DonutChart segments={providerData} theme={theme} />
        </div>

        {/* Badges earned */}
        <div style={{ background: theme.cardBg, border: `1px solid ${theme.border}`, borderRadius: 8, padding: 20 }}>
          <BarChart data={badgeBarData} color="#ffd700" label="🏅 BADGES LES PLUS OBTENUS" theme={theme} />
        </div>

        {/* Niveaux */}
        <div style={{ background: theme.cardBg, border: `1px solid ${theme.border}`, borderRadius: 8, padding: 20 }}>
          <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 10, color: theme.primary, opacity: 0.8, letterSpacing: 2, marginBottom: 16 }}>🎮 ÉTAT DES NIVEAUX</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {levels.map(l => (
              <div key={l.id} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: l.is_active ? theme.primary : "#ff003c", boxShadow: l.is_active ? `0 0 6px ${theme.primary}` : "0 0 6px #ff003c", flexShrink: 0 }} />
                <div style={{ flex: 1, fontSize: 11, fontFamily: "monospace", color: theme.text }}>{l.name.slice(0, 20)}</div>
                <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 9, color: l.is_active ? theme.primary : "#ff003c" }}>{l.is_active ? "ON" : "OFF"}</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 14, height: 4, background: theme.borderLight, borderRadius: 2, overflow: "hidden" }}>
            <div style={{ height: "100%", width: `${(levels.filter(l => l.is_active).length / Math.max(levels.length, 1)) * 100}%`, background: theme.primary, borderRadius: 2 }} />
          </div>
          <div style={{ fontSize: 10, color: theme.textMuted, marginTop: 4, fontFamily: "monospace" }}>{levels.filter(l => l.is_active).length}/{levels.length} actifs</div>
        </div>
      </div>

      {/* Top agents + system */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Top agents */}
        <div style={{ background: theme.cardBg, border: `1px solid ${theme.border}`, borderRadius: 8, padding: 20 }}>
          <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 10, color: theme.primary, opacity: 0.8, letterSpacing: 2, marginBottom: 16 }}>🏆 TOP 5 AGENTS</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {topUsers.map((u, i) => {
              const medals = ["🥇", "🥈", "🥉", "④", "⑤"];
              const barW = topUsers[0]?.total_points ? (u.total_points / topUsers[0].total_points) * 100 : 0;
              return (
                <div key={u.id} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 16, width: 22, textAlign: "center" }}>{medals[i]}</span>
                  <div style={{ width: 28, height: 28, borderRadius: "50%", background: theme.borderLight, border: `1px solid ${theme.border}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Orbitron',sans-serif", fontSize: 11, color: theme.primary, flexShrink: 0 }}>
                    {u.pseudo[0]?.toUpperCase()}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                      <span style={{ fontSize: 11, fontFamily: "monospace", color: theme.text, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{u.pseudo}</span>
                      <span style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 10, color: "#ffd700", flexShrink: 0 }}>{u.total_points.toLocaleString()}</span>
                    </div>
                    <div style={{ height: 3, background: theme.borderLight, borderRadius: 2, overflow: "hidden" }}>
                      <div style={{ height: "100%", width: `${barW}%`, background: i === 0 ? "#ffd700" : theme.primary, borderRadius: 2, transition: "width 1s ease" }} />
                    </div>
                  </div>
                </div>
              );
            })}
            {topUsers.length === 0 && <div style={{ color: theme.textMuted, fontSize: 11, fontFamily: "monospace", textAlign: "center", padding: "20px 0" }}>Aucun agent classé</div>}
          </div>
        </div>

        {/* System status */}
        <div style={{ background: theme.cardBg, border: `1px solid ${theme.border}`, borderRadius: 8, padding: 20 }}>
          <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 10, color: theme.primary, opacity: 0.8, letterSpacing: 2, marginBottom: 16 }}>🖥️ ÉTAT DU SYSTÈME</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[
              { label: "API Backend",     status: "OPÉRATIONNEL", ok: true,  icon: "⚡" },
              { label: "Base PostgreSQL",  status: "CONNECTÉE",    ok: true,  icon: "🗄️" },
              { label: "Assets / Fichiers",status: "DISPONIBLES",  ok: true,  icon: "📁" },
              { label: "Auth JWT",         status: "ACTIF",        ok: true,  icon: "🔐" },
              { label: "Docker",           status: "RUNNING",      ok: true,  icon: "🐳" },
            ].map((s, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", background: theme.cardBgInternal, borderRadius: 6, border: `1px solid ${theme.borderLight}` }}>
                <span style={{ fontSize: 18 }}>{s.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 9, color: theme.textMuted, letterSpacing: 1 }}>{s.label}</div>
                  <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 11, color: s.ok ? theme.primary : "#ff003c", marginTop: 2 }}>{s.status}</div>
                </div>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: s.ok ? theme.primary : "#ff003c", boxShadow: s.ok ? `0 0 8px ${theme.primary}` : "0 0 8px #ff003c", animation: "pulse 2s ease infinite" }} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Users Tab ─────────────────────────────────────────────────────
function UsersTab({ users, onRefresh, theme }: { users: AdminUser[]; onRefresh: () => void; theme: any }) {
  const [search, setSearch] = useState("");
  const [confirm, setConfirm] = useState<{ msg: string; fn: () => void } | null>(null);
  const { show, Toast } = useToast(theme);
  const [filter, setFilter] = useState<"all"|"admin"|"banned">("all");

  const act = async (fn: () => Promise<void>, msg: string) => { try { await fn(); show(msg); onRefresh(); } catch { show("Erreur", false); } };

  const filtered = users.filter(u => {
    const matchSearch = u.pseudo.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase());
    if (filter === "admin") return matchSearch && u.is_admin;
    if (filter === "banned") return matchSearch && !u.is_active;
    return matchSearch;
  });

  return (
    <div>
      {Toast}
      {confirm && <Confirm msg={confirm.msg} onOk={confirm.fn} onCancel={() => setConfirm(null)} theme={theme} />}

      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <h2 style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 15, color: theme.primary, letterSpacing: 3 }}>GESTION AGENTS</h2>
        <div style={{ display: "flex", gap: 6 }}>
          {(["all", "admin", "banned"] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)}
              style={{ background: filter === f ? "rgba(0,255,65,0.12)" : "transparent", border: `1px solid ${filter === f ? theme.primary : theme.border}`, color: filter === f ? theme.primary : theme.textMuted, padding: "5px 12px", borderRadius: 4, cursor: "pointer", fontFamily: "'Orbitron',sans-serif", fontSize: 9, letterSpacing: 2 }}>
              {f === "all" ? `TOUS (${users.length})` : f === "admin" ? `ADMINS (${users.filter(u => u.is_admin).length})` : `BANNIS (${users.filter(u => !u.is_active).length})`}
            </button>
          ))}
        </div>
        <div style={{ flex: 1 }} />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..."
          style={{ background: theme.cardBgInternal, border: `1px solid ${theme.border}`, borderRadius: 4, padding: "7px 12px", color: theme.text, fontFamily: "monospace", fontSize: 12, outline: "none", width: 200 }} />
      </div>

      <div style={{ background: theme.cardBg, border: `1px solid ${theme.border}`, borderRadius: 8, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: theme.borderLight, borderBottom: `1px solid ${theme.border}` }}>
              {["#", "AGENT", "EMAIL", "PROVIDER", "POINTS", "BADGES", "RÔLE", "STATUT", "ACTIONS"].map(h => (
                <th key={h} style={{ padding: "10px 14px", textAlign: "left", fontFamily: "'Orbitron',sans-serif", fontSize: 9, letterSpacing: 2, color: theme.textMuted }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((u, i) => (
              <tr key={u.id} style={{ borderBottom: `1px solid ${theme.borderLight}`, transition: "background .15s" }}
                onMouseEnter={e => (e.currentTarget.style.background = theme.borderLight)}
                onMouseLeave={e => (e.currentTarget.style.background = "transparent")}>
                <td style={{ padding: "10px 14px", color: theme.textMuted, fontSize: 11, fontFamily: "monospace" }}>#{u.id}</td>
                <td style={{ padding: "10px 14px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 30, height: 30, borderRadius: "50%", background: theme.borderLight, border: `1px solid ${theme.border}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Orbitron',sans-serif", fontSize: 12, color: theme.primary, flexShrink: 0 }}>
                      {u.pseudo[0]?.toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 11, color: theme.text }}>{u.pseudo}</div>
                      <div style={{ fontSize: 10, color: theme.textMuted, fontFamily: "monospace" }}>{new Date(u.created_at).toLocaleDateString("fr-FR")}</div>
                    </div>
                  </div>
                </td>
                <td style={{ padding: "10px 14px", color: theme.textMuted, fontSize: 11, fontFamily: "monospace" }}>{u.email}</td>
                <td style={{ padding: "10px 14px" }}>
                  <span style={{ background: u.auth_provider === "local" ? "rgba(0,255,65,0.1)" : "rgba(0,229,255,0.1)", border: `1px solid ${u.auth_provider === "local" ? "rgba(0,255,65,0.3)" : "rgba(0,229,255,0.3)"}`, color: u.auth_provider === "local" ? theme.primary : "#00e5ff", borderRadius: 10, padding: "2px 8px", fontSize: 9, fontFamily: "'Orbitron',sans-serif" }}>
                    {u.auth_provider}
                  </span>
                </td>
                <td style={{ padding: "10px 14px", fontFamily: "'Orbitron',sans-serif", fontSize: 13, color: "#ffd700" }}>{u.total_points.toLocaleString()}</td>
                <td style={{ padding: "10px 14px", color: "#00e5ff", fontSize: 12 }}>🏅 {u.badges_count}</td>
                <td style={{ padding: "10px 14px" }}>
                  <span style={{ background: u.is_admin ? "rgba(255,0,60,0.1)" : "transparent", border: `1px solid ${u.is_admin ? "rgba(255,0,60,0.3)" : theme.border}`, color: u.is_admin ? "#ff6060" : theme.textMuted, borderRadius: 10, padding: "2px 8px", fontSize: 9, fontFamily: "'Orbitron',sans-serif" }}>
                    {u.is_admin ? "👑 ADMIN" : "USER"}
                  </span>
                </td>
                <td style={{ padding: "10px 14px" }}>
                  <span style={{ background: u.is_active ? "rgba(0,255,65,0.08)" : "rgba(255,0,60,0.08)", border: `1px solid ${u.is_active ? "rgba(0,255,65,0.25)" : "rgba(255,0,60,0.25)"}`, color: u.is_active ? theme.primary : "#ff003c", borderRadius: 10, padding: "2px 8px", fontSize: 9, fontFamily: "'Orbitron',sans-serif" }}>
                    {u.is_active ? "● ACTIF" : "○ BANNI"}
                  </span>
                </td>
                <td style={{ padding: "10px 14px" }}>
                  <div style={{ display: "flex", gap: 5 }}>
                    <button onClick={() => setConfirm({ msg: `${u.is_admin ? "Révoquer" : "Accorder"} les droits admin à ${u.pseudo} ?`, fn: () => act(() => adminFetch(`/admin/users/${u.id}`, { method: "PATCH", body: JSON.stringify({ is_admin: !u.is_admin }) }), "Rôle mis à jour") })}
                      style={{ background: "transparent", border: "1px solid rgba(0,229,255,0.3)", color: "#00e5ff", padding: "4px 8px", borderRadius: 3, cursor: "pointer", fontSize: 9, fontFamily: "'Orbitron',sans-serif" }}>
                      {u.is_admin ? "↓" : "↑"}
                    </button>
                    <button onClick={() => act(() => adminFetch(`/admin/users/${u.id}`, { method: "PATCH", body: JSON.stringify({ is_active: !u.is_active }) }), "Statut mis à jour")}
                      style={{ background: "transparent", border: `1px solid ${u.is_active ? "rgba(255,153,0,0.3)" : "rgba(0,255,65,0.3)"}`, color: u.is_active ? "#ff9900" : theme.primary, padding: "4px 8px", borderRadius: 3, cursor: "pointer", fontSize: 9, fontFamily: "'Orbitron',sans-serif" }}>
                      {u.is_active ? "BAN" : "ACT"}
                    </button>
                    <button onClick={() => setConfirm({ msg: `Réinitialiser les scores de ${u.pseudo} ?`, fn: () => act(() => adminFetch(`/admin/users/${u.id}/reset-scores`, { method: "POST" }), "Scores réinitialisés") })}
                      style={{ background: "transparent", border: "1px solid rgba(255,153,0,0.3)", color: "#ff9900", padding: "4px 8px", borderRadius: 3, cursor: "pointer", fontSize: 9, fontFamily: "'Orbitron',sans-serif" }}>
                      RST
                    </button>
                    <button onClick={() => setConfirm({ msg: `Supprimer définitivement ${u.pseudo} ?`, fn: () => act(() => adminFetch(`/admin/users/${u.id}`, { method: "DELETE" }), "Supprimé") })}
                      style={{ background: "transparent", border: "1px solid rgba(255,0,60,0.3)", color: "#ff003c", padding: "4px 8px", borderRadius: 3, cursor: "pointer", fontSize: 9, fontFamily: "'Orbitron',sans-serif" }}>
                      ✕
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <div style={{ textAlign: "center", padding: 30, color: theme.textMuted, fontFamily: "monospace" }}>Aucun agent trouvé</div>}
      </div>
    </div>
  );
}

// ── Levels Tab ────────────────────────────────────────────────────
function LevelsTab({ levels, onRefresh, theme }: { levels: AdminLevel[]; onRefresh: () => void; theme: any }) {
  const { show, Toast } = useToast(theme);
  const toggle = async (l: AdminLevel) => {
    try { await adminFetch(`/admin/levels/${l.id}/toggle`, { method: "PATCH" }); show(`Niveau ${l.is_active ? "désactivé" : "activé"}`); onRefresh(); }
    catch { show("Erreur", false); }
  };
  return (
    <div>
      {Toast}
      <h2 style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 15, color: theme.primary, letterSpacing: 3, marginBottom: 20 }}>GESTION DES NIVEAUX</h2>
      <div style={{ display: "grid", gap: 14 }}>
        {levels.map((l, i) => (
          <div key={l.id} style={{ background: theme.cardBg, border: `1px solid ${l.is_active ? "rgba(0,255,65,0.2)" : "rgba(255,0,60,0.15)"}`, borderRadius: 8, padding: 20, animation: `fadeUp .3s ease ${i * .08}s both`, position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg,transparent,${l.is_active ? theme.primary : "#ff003c"}50,transparent)` }} />
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div style={{ width: 50, height: 50, borderRadius: "50%", border: `2px solid ${l.is_active ? theme.primary : "#ff003c"}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Orbitron',sans-serif", fontSize: 20, color: l.is_active ? theme.primary : "#ff003c", flexShrink: 0 }}>{l.order}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 14, color: theme.text, marginBottom: 8 }}>{l.name}</div>
                <div style={{ display: "flex", gap: 20, fontSize: 11, color: theme.textMuted, fontFamily: "monospace" }}>
                  <span>📋 {l.enigmas_count} énigmes</span>
                  <span>⭐ {l.max_points} pts max</span>
                  <span>🔑 {l.slug}</span>
                </div>
                <div style={{ marginTop: 10, height: 4, background: theme.borderLight, borderRadius: 2, overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${(l.enigmas_count / 10) * 100}%`, background: l.is_active ? theme.primary : "#ff003c", borderRadius: 2 }} />
                </div>
              </div>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
                <span style={{ background: l.is_active ? "rgba(0,255,65,0.1)" : "rgba(255,0,60,0.1)", border: `1px solid ${l.is_active ? "rgba(0,255,65,0.3)" : "rgba(255,0,60,0.3)"}`, color: l.is_active ? theme.primary : "#ff003c", borderRadius: 10, padding: "3px 10px", fontSize: 9, fontFamily: "'Orbitron',sans-serif" }}>
                  {l.is_active ? "● ACTIF" : "○ INACTIF"}
                </span>
                <button onClick={() => toggle(l)}
                  style={{ background: l.is_active ? "rgba(255,0,60,0.08)" : "rgba(0,255,65,0.08)", border: `1px solid ${l.is_active ? "rgba(255,0,60,0.3)" : "rgba(0,255,65,0.3)"}`, color: l.is_active ? "#ff003c" : theme.primary, padding: "7px 16px", borderRadius: 4, cursor: "pointer", fontFamily: "'Orbitron',sans-serif", fontSize: 10, letterSpacing: 2 }}>
                  {l.is_active ? "DÉSACTIVER" : "ACTIVER"}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Certificates Tab ──────────────────────────────────────────────
function CertificatesTab({ theme }: { theme: any }) {
  const [certs, setCerts] = useState<AdminCert[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirm, setConfirm] = useState<{ msg: string; fn: () => void } | null>(null);
  const { show, Toast } = useToast(theme);

  const load = () => { setLoading(true); adminFetch<AdminCert[]>("/admin/certificates").then(setCerts).finally(() => setLoading(false)); };
  useEffect(load, []);

  return (
    <div>
      {Toast}
      {confirm && <Confirm msg={confirm.msg} onOk={confirm.fn} onCancel={() => setConfirm(null)} theme={theme} />}
      <h2 style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 15, color: theme.primary, letterSpacing: 3, marginBottom: 20 }}>CERTIFICATS ÉMIS</h2>
      
      {loading ? (
        <div style={{ color: theme.textMuted, fontFamily: "monospace" }}>Chargement des certificats...</div>
      ) : (
        <div style={{ background: theme.cardBg, border: `1px solid ${theme.border}`, borderRadius: 8, overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: theme.borderLight, borderBottom: `1px solid ${theme.border}` }}>
                {["CODE UNIQUE", "AGENT", "NIVEAU", "SCORE", "DATE"].map(h => (
                  <th key={h} style={{ padding: "10px 14px", textAlign: "left", fontFamily: "'Orbitron',sans-serif", fontSize: 9, letterSpacing: 2, color: theme.textMuted }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {certs.map(c => (
                <tr key={c.id} style={{ borderBottom: `1px solid ${theme.borderLight}` }}>
                  <td style={{ padding: "10px 14px", color: theme.primary, fontSize: 11, fontFamily: "monospace" }}>{c.unique_code}</td>
                  <td style={{ padding: "10px 14px", color: theme.text }}>{c.user_pseudo} <span style={{ color: theme.textMuted, fontSize: 10 }}>({c.user_email})</span></td>
                  <td style={{ padding: "10px 14px", color: theme.text }}>{c.level}</td>
                  <td style={{ padding: "10px 14px", color: "#ffd700", fontFamily: "monospace" }}>{c.score} pts</td>
                  <td style={{ padding: "10px 14px", color: theme.textMuted, fontSize: 11 }}>{new Date(c.issued_at).toLocaleDateString("fr-FR")}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {certs.length === 0 && <div style={{ textAlign: "center", padding: 30, color: theme.textMuted, fontFamily: "monospace" }}>Aucun certificat émis</div>}
        </div>
      )}
    </div>
  );
}

// ── Main Admin Panel (Export Global) ──────────────────────────────
export default function AdminPanel() {
  const [tab, setTab] = useState<"dashboard" | "users" | "levels" | "certs">("dashboard");
  const [stats, setStats] = useState<Stats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [levels, setLevels] = useState<AdminLevel[]>([]);
  const [badges, setBadges] = useState<AdminBadge[]>([]);
  
  // Gestion du mode clair / sombre
  const [isDarkMode, setIsDarkMode] = useState(true);

  const loadData = () => {
    adminFetch<Stats>("/admin/stats").then(setStats).catch(() => {});
    adminFetch<AdminUser[]>("/admin/users").then(setUsers).catch(() => {});
    adminFetch<AdminLevel[]>("/admin/levels").then(setLevels).catch(() => {});
    adminFetch<AdminBadge[]>("/admin/badges").then(setBadges).catch(() => {});
  };

  useEffect(loadData, []);

  // Définition des couleurs du thème
  const theme = {
    isDark: isDarkMode,
    bg: isDarkMode ? "#020c02" : "#f4f7f5",
    text: isDarkMode ? "#d4ffd4" : "#1a2e1a",
    textMuted: isDarkMode ? "rgba(212,255,212,0.4)" : "rgba(26,46,26,0.55)",
    primary: isDarkMode ? "#00ff41" : "#00aa25",
    cardBg: isDarkMode ? "rgba(3,14,3,0.95)" : "#ffffff",
    cardBgInternal: isDarkMode ? "rgba(0,0,0,0.3)" : "#f9fbf9",
    border: isDarkMode ? "rgba(0,255,65,0.15)" : "rgba(0,170,37,0.15)",
    borderLight: isDarkMode ? "rgba(0,255,65,0.05)" : "rgba(0,170,37,0.05)"
  };

  return (
    <div style={{ minHeight: "100vh", background: theme.bg, color: theme.text, padding: "24px 40px", transition: "background 0.3s, color 0.3s", fontFamily: "sans-serif" }}>
      {/* Top Navbar */}
      <div style={{ display: "flex", alignItems: "center", justifyItems: "center", gap: 12, borderBottom: `1px solid ${theme.border}`, paddingBottom: 16, marginBottom: 24 }}>
        <div style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 13, fontWeight: "bold", color: theme.primary, letterSpacing: 2, marginRight: 20 }}>H4CKR_ADMIN</div>
        
        {[
          { id: "dashboard", label: "TABLEAU DE BORD" },
          { id: "users", label: "AGENTS" },
          { id: "levels", label: "NIVEAUX" },
          { id: "certs", label: "CERTIFICATS" }
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id as any)}
            style={{ background: "transparent", border: "none", borderBottom: tab === t.id ? `2px solid ${theme.primary}` : "2px solid transparent", color: tab === t.id ? theme.primary : theme.textMuted, padding: "6px 12px", cursor: "pointer", fontFamily: "'Orbitron',sans-serif", fontSize: 10, letterSpacing: 2, fontWeight: tab === t.id ? "bold" : "normal", transition: "all .2s" }}>
            {t.label}
          </button>
        ))}

        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center" }}>
          {/* Bouton bascule Mode Clair / Sombre */}
          <button onClick={() => setIsDarkMode(!isDarkMode)} 
            style={{ background: theme.cardBg, border: `1px solid ${theme.border}`, color: theme.primary, padding: "6px 12px", borderRadius: 20, cursor: "pointer", fontFamily: "'Orbitron',sans-serif", fontSize: 12, display: "flex", alignItems: "center", gap: 6, boxShadow: isDarkMode ? "none" : "0 2px 5px rgba(0,0,0,0.1)" }}>
            {isDarkMode ? "☀️ MODE CLAIR" : "🌙 MODE SOMBRE"}
          </button>
        </div>
      </div>

      {/* Render active Tab */}
      {tab === "dashboard" && <DashboardTab stats={stats} users={users} levels={levels} badges={badges} theme={theme} />}
      {tab === "users" && <UsersTab users={users} onRefresh={loadData} theme={theme} />}
      {tab === "levels" && <LevelsTab levels={levels} onRefresh={loadData} theme={theme} />}
      {tab === "certs" && <CertificatesTab theme={theme} />}
    </div>
  );
}