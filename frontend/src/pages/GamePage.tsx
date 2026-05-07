import { useState, useEffect, useRef, useCallback } from "react";
import { gameApi, type LevelOut, type EnigmaOut, type LeaderboardEntry, type BadgeOut } from "../api/client";
import { useAuth } from "../hooks/useAuth";

// ═══════════════════════════════════════════════════════════════════
// GLOBAL STYLES
// ═══════════════════════════════════════════════════════════════════
const GLOBAL_STYLES = `
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@400;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --green: #00ff41;
  --green-dim: rgba(0,255,65,0.5);
  --green-faint: rgba(0,255,65,0.08);
  --red: #ff003c;
  --cyan: #00e5ff;
  --gold: #ffd700;
  --bg: #020c02;
  --card: rgba(2,14,2,0.92);
  --border: rgba(0,255,65,0.2);
  --border-bright: rgba(0,255,65,0.5);
  --text: #d4ffd4;
  --text-dim: rgba(212,255,212,0.55);
  --font-mono: 'Share Tech Mono', monospace;
  --font-hud: 'Orbitron', sans-serif;
  --font-body: 'Rajdhani', sans-serif;
}

html, body { background: var(--bg); color: var(--text); font-family: var(--font-body); font-size: 16px; min-height: 100vh; overflow-x: hidden; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,255,65,0.25); border-radius: 3px; }

@keyframes fadeUp    { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
@keyframes fadeIn    { from { opacity:0; } to { opacity:1; } }
@keyframes blink     { 0%,100%{opacity:1} 50%{opacity:0} }
@keyframes spin      { to{transform:rotate(360deg)} }
@keyframes pulse     { 0%,100%{opacity:.6;transform:scale(1)} 50%{opacity:1;transform:scale(1.02)} }
@keyframes glow      { 0%,100%{box-shadow:0 0 8px rgba(0,255,65,.3)} 50%{box-shadow:0 0 24px rgba(0,255,65,.7),0 0 48px rgba(0,255,65,.2)} }
@keyframes shake     { 0%,100%{transform:translateX(0)} 20%{transform:translateX(-6px)} 40%{transform:translateX(6px)} 60%{transform:translateX(-4px)} 80%{transform:translateX(4px)} }
@keyframes robotFloat{ 0%,100%{transform:translateY(0) rotate(-1deg)} 50%{transform:translateY(-8px) rotate(1deg)} }
@keyframes eyeBlink  { 0%,92%,100%{transform:scaleY(1)} 95%{transform:scaleY(0.05)} }
@keyframes typeBar   { 0%,100%{opacity:1} 50%{opacity:0} }
@keyframes badgePop  { 0%{transform:translateX(100px) scale(.8);opacity:0} 15%{transform:translateX(0) scale(1.05);opacity:1} 85%{transform:translateX(0) scale(1);opacity:1} 100%{transform:translateX(100px);opacity:0} }
@keyframes countUp   { from{transform:scale(1.4);color:var(--gold)} to{transform:scale(1)} }
@keyframes progressFill { from{width:0} }
@keyframes scanbeam  { from{top:-4px} to{top:100%} }

.hud-btn {
  position: relative; background: transparent;
  border: 1px solid var(--green-dim); color: var(--green-dim);
  font-family: var(--font-hud); font-size: 11px; letter-spacing: 2px;
  padding: 8px 18px; cursor: pointer; text-transform: uppercase;
  transition: all .2s; overflow: hidden;
}
.hud-btn::before {
  content:''; position:absolute; inset:0;
  background: linear-gradient(90deg, transparent, rgba(0,255,65,.12), transparent);
  transform: translateX(-100%); transition: transform .4s;
}
.hud-btn:hover::before { transform: translateX(100%); }
.hud-btn:hover { border-color: var(--green); color: var(--green); box-shadow: 0 0 12px rgba(0,255,65,.2); }
.hud-btn.active { border-color: var(--green); color: var(--green); background: var(--green-faint); }
.hud-btn.danger { border-color: rgba(255,0,60,.3); color: rgba(255,0,60,.5); }
.hud-btn.danger:hover { border-color: var(--red); color: var(--red); }
.hud-btn.primary { border-color: var(--green); color: #000; background: var(--green); font-weight:700; }
.hud-btn.primary:hover { background: #00cc35; box-shadow: 0 0 20px rgba(0,255,65,.5); }

.game-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 6px; position: relative; overflow: hidden;
  transition: border-color .3s, box-shadow .3s;
}
.game-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background: linear-gradient(90deg, transparent, rgba(0,255,65,.4), transparent);
  opacity: 0; transition: opacity .3s;
}
.game-card:hover::before { opacity: 1; }
.game-card.solved { border-color: rgba(0,255,65,.4); box-shadow: 0 0 20px rgba(0,255,65,.06); }
.game-card.solved::before { opacity:1; }

.game-input {
  background: rgba(0,255,65,.04); border: 1px solid var(--border);
  border-radius: 3px; padding: 10px 14px; color: var(--green);
  font-family: var(--font-mono); font-size: 13px; outline: none; width: 100%;
  transition: border-color .2s, box-shadow .2s;
}
.game-input:focus { border-color: var(--green); box-shadow: 0 0 10px rgba(0,255,65,.15); }
.game-input::placeholder { color: rgba(0,255,65,.2); }

.tag {
  display: inline-block; padding: 2px 8px; border-radius: 3px;
  font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
  font-family: var(--font-hud); border: 1px solid;
}

details summary { list-style: none; }
details summary::-webkit-details-marker { display: none; }
`;

// ═══════════════════════════════════════════════════════════════════
// ANIMATED CYBER BACKGROUND
// ═══════════════════════════════════════════════════════════════════
function CyberBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = canvasRef.current!;
    const ctx = c.getContext("2d")!;
    let raf: number;
    const resize = () => { c.width = window.innerWidth; c.height = window.innerHeight; };
    resize();
    window.addEventListener("resize", resize);
    const particles = Array.from({ length: 55 }, () => ({
      x: Math.random() * window.innerWidth, y: Math.random() * window.innerHeight,
      vx: (Math.random() - .5) * .28, vy: (Math.random() - .5) * .28,
      r: Math.random() * 1.4 + .4,
    }));
    const draw = () => {
      ctx.clearRect(0, 0, c.width, c.height);
      ctx.strokeStyle = "rgba(0,255,65,0.025)";
      ctx.lineWidth = 1;
      for (let x = 0; x < c.width; x += 64) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, c.height); ctx.stroke(); }
      for (let y = 0; y < c.height; y += 64) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(c.width, y); ctx.stroke(); }
      particles.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > c.width) p.vx *= -1;
        if (p.y < 0 || p.y > c.height) p.vy *= -1;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(0,255,65,0.45)"; ctx.fill();
      });
      particles.forEach((a, i) => particles.slice(i + 1).forEach(b => {
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d < 110) {
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(0,255,65,${.14 * (1 - d / 110)})`; ctx.lineWidth = .5; ctx.stroke();
        }
      }));
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", resize); };
  }, []);
  return <canvas ref={canvasRef} style={{ position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none" }} />;
}

// ═══════════════════════════════════════════════════════════════════
// ROBOT GUIDE
// ═══════════════════════════════════════════════════════════════════
function RobotGuide({ text, onDone, accent = "#00ff41" }: { text: string; onDone?: () => void; accent?: string }) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  const idx = useRef(0);

  useEffect(() => {
    idx.current = 0; setDisplayed(""); setDone(false);
    const id = setInterval(() => {
      if (idx.current < text.length) { setDisplayed(text.slice(0, ++idx.current)); }
      else { clearInterval(id); setDone(true); }
    }, 20);
    return () => clearInterval(id);
  }, [text]);

  return (
    <div style={{ display: "flex", gap: 20, alignItems: "flex-start", padding: "20px 28px", background: "rgba(0,20,0,0.6)", borderBottom: "1px solid rgba(0,255,65,0.12)", animation: "fadeIn .4s ease" }}>
      <div style={{ flexShrink: 0, animation: "robotFloat 3s ease-in-out infinite" }}>
        <svg width="70" height="86" viewBox="0 0 72 88" fill="none">
          <line x1="36" y1="0" x2="36" y2="10" stroke={accent} strokeWidth="2"/>
          <circle cx="36" cy="3" r="3" fill={accent} style={{ filter: `drop-shadow(0 0 4px ${accent})` }}/>
          <rect x="12" y="10" width="48" height="36" rx="6" fill="#050d05" stroke={accent} strokeWidth="1.5"/>
          <rect x="19" y="20" width="14" height="10" rx="2" fill={accent} style={{ animation: "eyeBlink 4s ease-in-out infinite", transformOrigin: "26px 25px", filter: `drop-shadow(0 0 6px ${accent})` }}/>
          <rect x="39" y="20" width="14" height="10" rx="2" fill={accent} style={{ animation: "eyeBlink 4s ease-in-out infinite .15s", transformOrigin: "46px 25px", filter: `drop-shadow(0 0 6px ${accent})` }}/>
          <rect x="22" y="36" width="28" height="4" rx="2" fill={`${accent}30`} stroke={accent} strokeWidth="1"/>
          {[24,29,34,39,44].map(x => <rect key={x} x={x} y="37" width="2" height="2" rx="1" fill={accent}/>)}
          <rect x="30" y="46" width="12" height="6" rx="2" fill="#050d05" stroke={accent} strokeWidth="1"/>
          <rect x="8" y="52" width="56" height="32" rx="6" fill="#050d05" stroke={accent} strokeWidth="1.5"/>
          <rect x="16" y="58" width="16" height="12" rx="2" fill={`${accent}08`} stroke={accent} strokeWidth="1"/>
          <rect x="40" y="58" width="16" height="12" rx="2" fill={`${accent}08`} stroke={accent} strokeWidth="1"/>
          {[0,1,2].map(i => <rect key={i} x={18+i*4} y={60} width="2" height={4+i*2} rx="1" fill={accent} style={{ opacity: 0.8 }}/>)}
          <polyline points="40,64 44,60 46,68 50,58 52,68 54,64 56,64" stroke={accent} strokeWidth="1.5" fill="none"/>
          <rect x="0" y="54" width="8" height="20" rx="4" fill="#050d05" stroke={accent} strokeWidth="1"/>
          <rect x="64" y="54" width="8" height="20" rx="4" fill="#050d05" stroke={accent} strokeWidth="1"/>
        </svg>
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ color: accent, fontFamily: "var(--font-hud)", fontSize: 10, letterSpacing: 3, marginBottom: 8, opacity: 0.7 }}>● NEXUS-7 — IA GUIDE</div>
        <div style={{ background: "rgba(0,255,65,0.04)", border: "1px solid rgba(0,255,65,0.18)", borderRadius: "4px 12px 12px 12px", padding: "14px 18px", color: "var(--text)", fontFamily: "var(--font-body)", fontSize: 15, lineHeight: 1.7, minHeight: 50 }}>
          {displayed}
          {!done && <span style={{ animation: "typeBar .8s step-end infinite", color: accent }}>█</span>}
        </div>
        {done && onDone && (
          <button className="hud-btn" onClick={onDone} style={{ marginTop: 10, fontSize: 10 }}>Commencer la mission →</button>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// TERMINAL
// ═══════════════════════════════════════════════════════════════════
function Terminal({ enigmaId, accent = "#00ff41" }: { enigmaId?: number; accent?: string }) {
  const [history, setHistory] = useState<Array<{ type: "input"|"output"|"error"|"success"; text: string }>>([
    { type: "output", text: "H4CKR Terminal v2.0 — Système actif\nTapez 'help' pour la liste des commandes.\n─────────────────────────────────────────" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [cmdHist, setCmdHist] = useState<string[]>([]);
  const [histIdx, setHistIdx] = useState(-1);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [history]);

  const run = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const cmd = input.trim();
    if (!cmd || loading) return;
    setInput(""); setHistIdx(-1);
    setCmdHist(h => [cmd, ...h.slice(0, 49)]);
    setHistory(h => [...h, { type: "input", text: cmd }]);
    if (cmd.toLowerCase() === "clear") { setHistory([]); return; }
    setLoading(true);
    try {
      const res = await gameApi.terminal(cmd, enigmaId);
      setHistory(h => [...h, { type: res.success ? "success" : "output", text: res.output }]);
    } catch {
      setHistory(h => [...h, { type: "error", text: "Commande non reconnue. Tapez 'help'." }]);
    } finally { setLoading(false); setTimeout(() => inputRef.current?.focus(), 50); }
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowUp") { const ni = Math.min(histIdx + 1, cmdHist.length - 1); setHistIdx(ni); setInput(cmdHist[ni] ?? ""); }
    else if (e.key === "ArrowDown") { const ni = Math.max(histIdx - 1, -1); setHistIdx(ni); setInput(ni === -1 ? "" : cmdHist[ni]); }
  };

  const col = { input: accent, output: "rgba(200,255,200,0.7)", error: "#ff4060", success: "#80ff80" };

  return (
    <div style={{ background: "#000", border: `1px solid ${accent}35`, borderRadius: 6, overflow: "hidden" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 14px", background: `${accent}06`, borderBottom: `1px solid ${accent}15` }}>
        {["#ff5f57","#febc2e","#28c840"].map((c,i) => <div key={i} style={{ width: 10, height: 10, borderRadius: "50%", background: c, opacity: .7 }}/>)}
        <span style={{ marginLeft: 6, color: `${accent}50`, fontFamily: "var(--font-mono)", fontSize: 11 }}>h4ckr@terminal:~$</span>
      </div>
      <div style={{ padding: "14px 16px", minHeight: 200, maxHeight: 320, overflowY: "auto", fontFamily: "var(--font-mono)", fontSize: 12.5 }} onClick={() => inputRef.current?.focus()}>
        {history.map((h, i) => (
          <div key={i} style={{ marginBottom: 3 }}>
            {h.type === "input"
              ? <div><span style={{ color: `${accent}50` }}>$ </span><span style={{ color: accent }}>{h.text}</span></div>
              : <pre style={{ color: col[h.type], margin: 0, whiteSpace: "pre-wrap", lineHeight: 1.6 }}>{h.text}</pre>}
          </div>
        ))}
        {loading && <div style={{ color: `${accent}50` }}><span style={{ animation: "blink .6s step-end infinite" }}>▐ </span>traitement...</div>}
        <div ref={endRef}/>
      </div>
      <form onSubmit={run} style={{ display: "flex", alignItems: "center", padding: "8px 16px", borderTop: `1px solid ${accent}12`, gap: 8 }}>
        <span style={{ color: `${accent}55`, fontFamily: "var(--font-mono)", fontSize: 12 }}>$</span>
        <input ref={inputRef} value={input} onChange={e => setInput(e.target.value)} onKeyDown={onKey}
          style={{ flex: 1, background: "none", border: "none", outline: "none", color: accent, fontFamily: "var(--font-mono)", fontSize: 12.5, caretColor: accent }}
          placeholder="commande..." spellCheck={false} autoComplete="off" disabled={loading}/>
        {loading && <div style={{ width: 11, height: 11, border: `2px solid ${accent}30`, borderTopColor: accent, borderRadius: "50%", animation: "spin .6s linear infinite" }}/>}
      </form>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// ENIGMA CARD
// ═══════════════════════════════════════════════════════════════════
const TYPE_CFG: Record<string, { label: string; color: string; icon: string; placeholder: string }> = {
  base64:   { label: "BASE64",          color: "#00e5ff", icon: "🔢", placeholder: "Mot de passe décodé..." },
  caesar:   { label: "CHIFFREMENT",     color: "#ff9900", icon: "🔄", placeholder: "Message déchiffré..." },
  stegano:  { label: "STÉGANOGRAPHIE",  color: "#cc44ff", icon: "🖼️", placeholder: "Commentaire trouvé..." },
  audio:    { label: "AUDIO",           color: "#ff6b35", icon: "🎧", placeholder: "Mot prononcé à l'envers..." },
  logs:     { label: "ANALYSE LOGS",    color: "#ffd700", icon: "📋", placeholder: "Adresse IP ou valeur..." },
  terminal: { label: "TERMINAL",        color: "#00ff41", icon: "💻", placeholder: "" },
  metadata: { label: "METADATA",        color: "#ff4488", icon: "🔍", placeholder: "Valeur trouvée..." },
  default:  { label: "ÉNIGME",          color: "#00ff41", icon: "❓", placeholder: "Votre réponse..." },
};

function EnigmaCard({ enigma, index, isLocked, onSolve }: { enigma: EnigmaOut; index: number; isLocked: boolean; onSolve: (b?: BadgeOut) => void }) {
  const [answer, setAnswer] = useState("");
  const [msg, setMsg] = useState<{ text: string; ok: boolean } | null>(null);
  const [hint, setHint] = useState("");
  const [loading, setLoading] = useState(false);
  const [solved, setSolved] = useState(enigma.solved);
  const [shake, setShake] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const cfg = TYPE_CFG[enigma.type] ?? TYPE_CFG.default;
  const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

  if (isLocked) return (
    <div style={{ background: "rgba(0,0,0,0.35)", border: "1px solid rgba(0,255,65,0.06)", borderRadius: 6, padding: "18px 22px", opacity: 0.38, display: "flex", alignItems: "center", gap: 14, marginBottom: 12 }}>
      <span style={{ fontSize: 22 }}>🔒</span>
      <div>
        <div style={{ color: "rgba(0,255,65,0.4)", fontFamily: "var(--font-hud)", fontSize: 12 }}>Énigme {index + 1} — {enigma.title}</div>
        <div style={{ color: "rgba(0,255,65,0.2)", fontSize: 11, marginTop: 2 }}>Résolvez l'énigme précédente pour débloquer</div>
      </div>
    </div>
  );

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim() || loading) return;
    setLoading(true); setMsg(null);
    try {
      const res = await gameApi.submitAnswer(enigma.id, answer);
      setMsg({ text: res.message, ok: res.correct });
      if (res.correct) { setSolved(true); onSolve(res.badge_earned ?? undefined); }
      else { setShake(true); setTimeout(() => setShake(false), 500); setShowHint(true); if (res.hint) setHint(res.hint); }
    } catch (err: any) { setMsg({ text: err?.detail ?? "Erreur", ok: false }); }
    finally { setLoading(false); }
  };

  const askHint = async () => {
    try { const r = await gameApi.requestHint(enigma.id); setHint(r.hint); } catch {}
  };

  return (
    <div className={`game-card ${solved ? "solved" : ""}`} style={{ padding: 24, marginBottom: 14, animation: `fadeUp .35s ease ${index * .08}s both`, ...(shake ? { animation: "shake .4s ease" } : {}) }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${cfg.color}55, transparent)`, opacity: solved ? 1 : 0.3 }}/>

      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14, flexWrap: "wrap", gap: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span className="tag" style={{ color: cfg.color, borderColor: `${cfg.color}45`, background: `${cfg.color}0d` }}>{cfg.icon} {cfg.label}</span>
          <h3 style={{ fontFamily: "var(--font-hud)", fontSize: 14, color: "#dfffd4" }}>{index + 1}. {enigma.title}</h3>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {solved && <span style={{ color: "#00ff41", fontFamily: "var(--font-hud)", fontSize: 10, letterSpacing: 2, animation: "countUp .4s ease" }}>✓ RÉSOLU</span>}
          <span style={{ fontFamily: "var(--font-hud)", fontSize: 17, color: cfg.color }}>{enigma.points}<span style={{ fontSize: 9, opacity: 0.5, marginLeft: 2 }}>PTS</span></span>
        </div>
      </div>

      {/* Description */}
      <div style={{ background: "rgba(0,0,0,0.3)", borderLeft: `3px solid ${cfg.color}40`, borderRadius: "0 4px 4px 0", padding: "12px 16px", marginBottom: 16, color: "var(--text)", fontFamily: "var(--font-mono)", fontSize: 12.5, lineHeight: 1.8, whiteSpace: "pre-wrap" }}>
        {enigma.description}
      </div>

      {/* File: image */}
      {enigma.file_path?.match(/\.(png|jpg|jpeg|gif|webp)$/i) && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ color: "var(--green-dim)", fontSize: 10, letterSpacing: 2, marginBottom: 8, fontFamily: "var(--font-hud)" }}>🖼️ FICHIER SUSPECT — Cherchez l'indice caché</div>
          <div style={{ position: "relative", display: "inline-block" }}>
            <img src={`${API}/assets/${enigma.file_path}`} alt="Fichier suspect"
              style={{ maxWidth: "100%", maxHeight: 260, objectFit: "contain", border: "1px solid rgba(0,255,65,0.2)", borderRadius: 4, display: "block", filter: "saturate(0.65) contrast(1.15)" }}
              onError={e => { (e.target as HTMLImageElement).style.display = "none"; }}/>
            {/* Scanbeam animation */}
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 3, background: `linear-gradient(90deg, transparent, ${cfg.color}80, transparent)`, animation: "scanbeam 3s linear infinite" }}/>
          </div>
          <div style={{ color: "rgba(0,255,65,0.35)", fontSize: 11, marginTop: 6, fontFamily: "var(--font-mono)" }}>→ Examinez les métadonnées EXIF avec ExifTool ou dans le terminal : extract &lt;fichier&gt;</div>
        </div>
      )}

      {/* File: audio */}
      {enigma.file_path?.match(/\.(wav|mp3|ogg|flac)$/i) && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ color: "var(--green-dim)", fontSize: 10, letterSpacing: 2, marginBottom: 8, fontFamily: "var(--font-hud)" }}>🎧 SIGNAL AUDIO — Analysez attentivement</div>
          <div style={{ background: "rgba(0,0,0,0.5)", border: "1px solid rgba(0,255,65,0.18)", borderRadius: 4, padding: 16, display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ fontSize: 28, animation: "pulse 2s ease-in-out infinite" }}>📻</div>
            <div style={{ flex: 1 }}>
              <audio controls src={`${API}/assets/${enigma.file_path}`} style={{ width: "100%", filter: "invert(1) hue-rotate(120deg)" }}/>
            </div>
          </div>
          <div style={{ color: "rgba(255,165,0,0.6)", fontSize: 11, marginTop: 6, fontFamily: "var(--font-mono)" }}>
            💡 Astuce : Importez dans Audacity (gratuit) et inversez la piste pour révéler le message caché.
          </div>
        </div>
      )}

      {/* File: text/logs */}
      {enigma.file_path?.match(/\.(txt|log|b64)$/i) && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ color: "var(--green-dim)", fontSize: 10, letterSpacing: 2, marginBottom: 8, fontFamily: "var(--font-hud)" }}>📄 FICHIER DE DONNÉES</div>
          <a href={`${API}/assets/${enigma.file_path}`} target="_blank" rel="noopener noreferrer" className="hud-btn" style={{ display: "inline-block", textDecoration: "none", fontSize: 10 }}>
            ⬇ Télécharger {enigma.file_path.split("/").pop()}
          </a>
        </div>
      )}

      {/* Terminal */}
      {enigma.type === "terminal" && !solved && <div style={{ marginBottom: 16 }}><Terminal enigmaId={enigma.id} accent={cfg.color}/></div>}

      {/* Answer */}
      {!solved && enigma.type !== "terminal" && (
        <form onSubmit={submit}>
          <div style={{ color: "rgba(0,255,65,0.45)", fontSize: 10, letterSpacing: 2, marginBottom: 6, fontFamily: "var(--font-hud)" }}>VOTRE RÉPONSE</div>
          <div style={{ display: "flex", gap: 8 }}>
            <input className="game-input" value={answer} onChange={e => setAnswer(e.target.value)} placeholder={cfg.placeholder} autoComplete="off"/>
            <button type="submit" className="hud-btn" disabled={loading} style={{ whiteSpace: "nowrap", fontFamily: "var(--font-hud)", fontSize: 10 }}>
              {loading ? <span style={{ width: 13, height: 13, border: "2px solid rgba(0,255,65,.3)", borderTopColor: "#00ff41", borderRadius: "50%", display: "inline-block", animation: "spin .6s linear infinite" }}/> : "VALIDER ▶"}
            </button>
          </div>
        </form>
      )}

      {msg && <div style={{ marginTop: 10, padding: "9px 13px", borderRadius: 4, fontSize: 13, background: msg.ok ? "rgba(0,255,65,0.06)" : "rgba(255,0,60,0.06)", border: `1px solid ${msg.ok ? "rgba(0,255,65,.28)" : "rgba(255,0,60,.28)"}`, color: msg.ok ? "#00ff41" : "#ff4060", fontFamily: "var(--font-mono)", animation: "fadeIn .2s ease" }}>{msg.text}</div>}
      {hint && <div style={{ marginTop: 8, padding: "9px 13px", borderRadius: 4, fontSize: 12, background: "rgba(255,200,0,0.04)", border: "1px solid rgba(255,200,0,0.2)", color: "#ffc800", fontFamily: "var(--font-mono)", animation: "fadeIn .3s ease" }}>💡 {hint}</div>}
      {showHint && !solved && <button onClick={askHint} style={{ marginTop: 8, background: "none", border: "none", color: "rgba(0,255,65,0.32)", fontSize: 11, cursor: "pointer", padding: 0, fontFamily: "var(--font-mono)" }} onMouseEnter={e => (e.currentTarget.style.color = "rgba(0,255,65,.65)")} onMouseLeave={e => (e.currentTarget.style.color = "rgba(0,255,65,.32)")}>→ Obtenir un indice (-10 pts)</button>}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// LEVEL SECTION
// ═══════════════════════════════════════════════════════════════════
const ROBOT_INTROS: Record<string, string> = {
  beginner: "Bienvenue Agent. Je suis NEXUS-7, votre IA de soutien tactique. Ce niveau va tester vos bases : décodage Base64, chiffrement de César ROT13, stéganographie dans des images, et analyse d'un fichier audio suspect. Chaque énigme se débloque quand vous résolvez la précédente. Restez concentré — le réseau vous observe.",
  expert: "Agent. Niveau EXPERT chargé. Ici on simule un vrai pentest : analyse de logs serveur compromis, intrusion réseau SSH, extraction de métadonnées cachées, et terminal interactif live. Les erreurs coûtent des points. Vos décisions comptent. La clé finale assemble tous vos indices. Bonne chance.",
  default: "Nouvelle mission opérationnelle. Des indices sont cachés dans des fichiers, images et sons. Lisez chaque énigme attentivement. Utilisez le terminal pour les commandes avancées. Vous pouvez demander des indices — mais chaque indice coûte 10 points.",
};

const LEVEL_COLORS = ["#00ff41", "#00e5ff", "#ff9900", "#cc44ff", "#ff4488"];

function LevelSection({ level, onBadge }: { level: LevelOut; onBadge: (b: BadgeOut) => void }) {
  const [open, setOpen] = useState(false);
  const [robotDone, setRobotDone] = useState(false);
  const [enigmas, setEnigmas] = useState<EnigmaOut[]>([...level.enigmas].sort((a, b) => a.order - b.order));
  const [genCert, setGenCert] = useState(false);
  const accent = LEVEL_COLORS[(level.order - 1) % LEVEL_COLORS.length];
  const solved = enigmas.filter(e => e.solved).length;
  const total = enigmas.length;
  const complete = solved === total && total > 0;
  const pct = total > 0 ? (solved / total) * 100 : 0;

  const handleSolve = (idx: number) => (badge?: BadgeOut) => {
    setEnigmas(prev => prev.map((e, i) => i === idx ? { ...e, solved: true } : e));
    if (badge) onBadge(badge);
  };

  const downloadCert = async () => {
    setGenCert(true);
    try { const cert = await gameApi.generateCertificate(level.slug); window.open(gameApi.downloadCertificate(cert.unique_code), "_blank"); }
    catch (e: any) { alert(e?.detail ?? "Impossible de générer le certificat"); }
    finally { setGenCert(false); }
  };

  return (
    <div style={{ marginBottom: 22, animation: "fadeUp .4s ease" }}>
      {/* Header */}
      <div onClick={() => setOpen(o => !o)} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "18px 26px", cursor: "pointer", background: open ? "rgba(0,6,0,0.9)" : "rgba(0,3,0,0.7)", border: `1px solid ${open ? accent + "38" : "rgba(0,255,65,0.13)"}`, borderRadius: open ? "6px 6px 0 0" : 6, transition: "all .3s", position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${accent}55, transparent)`, opacity: open ? 1 : 0, transition: "opacity .3s" }}/>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ width: 42, height: 42, borderRadius: "50%", border: `2px solid ${accent}55`, display: "flex", alignItems: "center", justifyContent: "center", background: `${accent}0e`, fontFamily: "var(--font-hud)", fontSize: 17, color: accent, ...(open ? { animation: "glow 2s ease-in-out infinite" } : {}) }}>
            {level.order}
          </div>
          <div>
            <div style={{ fontFamily: "var(--font-hud)", fontSize: 16, color: "#dfffd4", fontWeight: 700 }}>{level.name}</div>
            <div style={{ color: "var(--text-dim)", fontSize: 12, marginTop: 2 }}>{level.description.slice(0, 75)}...</div>
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 3 }}>
          <div style={{ fontFamily: "var(--font-hud)", fontSize: 13, color: complete ? "#00ff41" : accent }}>{solved}/{total} {complete ? "✓" : ""}</div>
          <div style={{ color: "var(--text-dim)", fontSize: 10 }}>{level.max_points} pts max</div>
          <div style={{ fontSize: 16, transition: "transform .3s", transform: open ? "rotate(180deg)" : "none" }}>▾</div>
        </div>
      </div>

      {/* Progress bar */}
      {open && <div style={{ height: 4, background: "rgba(0,255,65,0.06)", borderLeft: `1px solid ${accent}30`, borderRight: `1px solid ${accent}30` }}><div style={{ height: "100%", width: `${pct}%`, background: complete ? `linear-gradient(90deg, ${accent}, #ffffffaa)` : accent, boxShadow: complete ? `0 0 10px ${accent}` : "none", transition: "width 1.2s ease" }}/></div>}

      {/* Content */}
      {open && (
        <div style={{ border: `1px solid ${accent}28`, borderTop: "none", borderRadius: "0 0 6px 6px", animation: "fadeIn .3s ease", overflow: "hidden" }}>
          {!robotDone && <RobotGuide text={ROBOT_INTROS[level.slug] ?? ROBOT_INTROS.default} accent={accent} onDone={() => setRobotDone(true)}/>}
          {complete && (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 22px", margin: "16px 22px 0", background: "rgba(0,255,65,0.05)", border: "1px solid rgba(0,255,65,0.28)", borderRadius: 6, animation: "glow 2.5s ease-in-out infinite" }}>
              <div>
                <div style={{ color: "#00ff41", fontFamily: "var(--font-hud)", fontSize: 13 }}>🏆 NIVEAU COMPLÉTÉ !</div>
                <div style={{ color: "var(--text-dim)", fontSize: 11, marginTop: 2 }}>Générez votre certificat officiel H4CKR</div>
              </div>
              <button className="hud-btn primary" onClick={downloadCert} disabled={genCert} style={{ fontSize: 10 }}>
                {genCert ? "Génération..." : "⬇ Télécharger Certificat"}
              </button>
            </div>
          )}
          <div style={{ padding: "18px 22px" }}>
            {enigmas.map((e, i) => (
              <EnigmaCard key={e.id} enigma={e} index={i} isLocked={i > 0 && !enigmas[i - 1].solved} onSolve={handleSolve(i)}/>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// BADGE POPUP
// ═══════════════════════════════════════════════════════════════════
function BadgePopup({ badge, onClose }: { badge: BadgeOut; onClose: () => void }) {
  useEffect(() => { const t = setTimeout(onClose, 5000); return () => clearTimeout(t); }, []);
  return (
    <div style={{ position: "fixed", top: 24, right: 24, zIndex: 9999, minWidth: 275, background: "rgba(0,10,0,0.97)", border: `2px solid ${badge.color}`, borderRadius: 8, padding: "18px 22px", boxShadow: `0 0 40px ${badge.color}38, 0 0 80px ${badge.color}12`, animation: "badgePop 5s ease forwards" }}>
      <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
        <div style={{ fontSize: 38, filter: `drop-shadow(0 0 8px ${badge.color})`, animation: "pulse 1s ease-in-out infinite" }}>{badge.icon}</div>
        <div>
          <div style={{ color: badge.color, fontFamily: "var(--font-hud)", fontSize: 10, letterSpacing: 3 }}>BADGE DÉBLOQUÉ !</div>
          <div style={{ color: "#dfffd4", fontSize: 15, fontWeight: 700, marginTop: 2 }}>{badge.name}</div>
          <div style={{ color: "var(--text-dim)", fontSize: 12, marginTop: 2 }}>{badge.description}</div>
          <div style={{ color: badge.color, fontFamily: "var(--font-hud)", fontSize: 11, marginTop: 5 }}>+{badge.points_reward} pts</div>
        </div>
      </div>
      <button onClick={onClose} style={{ position: "absolute", top: 8, right: 10, background: "none", border: "none", color: "rgba(255,255,255,.3)", cursor: "pointer", fontSize: 16 }}>×</button>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// LEADERBOARD
// ═══════════════════════════════════════════════════════════════════
function Leaderboard() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => { gameApi.leaderboard().then(setEntries).finally(() => setLoading(false)); }, []);
  if (loading) return <div style={{ textAlign: "center", padding: 60, color: "var(--green-dim)", fontFamily: "var(--font-mono)" }}><div style={{ fontSize: 28, marginBottom: 12, animation: "pulse 1.5s ease infinite" }}>⚡</div>Chargement...</div>;
  return (
    <div style={{ animation: "fadeUp .3s ease" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <span style={{ fontSize: 28 }}>🏆</span>
        <h2 style={{ fontFamily: "var(--font-hud)", fontSize: 20, color: "#00ff41" }}>CLASSEMENT MONDIAL</h2>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "50px 1fr 120px 80px 100px", gap: 8, padding: "8px 14px", color: "var(--text-dim)", fontFamily: "var(--font-hud)", fontSize: 9, letterSpacing: 2, borderBottom: "1px solid rgba(0,255,65,0.1)", marginBottom: 8 }}>
        <span>#</span><span>AGENT</span><span>NIVEAU</span><span>BADGES</span><span style={{ textAlign: "right" }}>SCORE</span>
      </div>
      {entries.map((e, i) => (
        <div key={e.user_id} style={{ display: "grid", gridTemplateColumns: "50px 1fr 120px 80px 100px", gap: 8, padding: "13px 14px", marginBottom: 4, background: i < 3 ? `rgba(0,255,65,${0.065 - i * 0.018})` : "rgba(0,4,0,0.5)", border: `1px solid rgba(0,255,65,${i < 3 ? 0.22 : 0.06})`, borderRadius: 5, alignItems: "center", animation: `fadeUp .3s ease ${i * .04}s both`, cursor: "default", transition: "transform .2s, box-shadow .2s" }}
          onMouseEnter={ev => { ev.currentTarget.style.transform = "translateX(5px)"; ev.currentTarget.style.boxShadow = "0 0 14px rgba(0,255,65,0.08)"; }}
          onMouseLeave={ev => { ev.currentTarget.style.transform = ""; ev.currentTarget.style.boxShadow = ""; }}>
          <span style={{ fontFamily: "var(--font-hud)", fontSize: 15, color: i === 0 ? "#ffd700" : i === 1 ? "#c0c0c0" : i === 2 ? "#cd7f32" : "var(--text-dim)" }}>
            {i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : e.rank}
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 30, height: 30, borderRadius: "50%", background: "rgba(0,255,65,0.08)", border: "1px solid rgba(0,255,65,0.25)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, color: "#00ff41" }}>{e.pseudo[0]?.toUpperCase()}</div>
            <span style={{ color: "#dfffd4", fontSize: 14, fontWeight: 600 }}>{e.pseudo}</span>
          </div>
          <span style={{ color: "var(--text-dim)", fontSize: 12 }}>{e.level_reached}</span>
          <span style={{ color: "var(--text-dim)", fontSize: 12 }}>🏅 {e.badges_count}</span>
          <span style={{ fontFamily: "var(--font-hud)", fontSize: 15, color: "#00ff41", textAlign: "right" }}>{e.total_points.toLocaleString()}</span>
        </div>
      ))}
      {entries.length === 0 && <div style={{ textAlign: "center", padding: 40, color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>Aucun agent classé pour le moment...</div>}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// BADGES PAGE
// ═══════════════════════════════════════════════════════════════════
function BadgesPage() {
  const [my, setMy] = useState<BadgeOut[]>([]);
  const [all, setAll] = useState<BadgeOut[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => { Promise.all([gameApi.myBadges(), gameApi.allBadges()]).then(([m, a]) => { setMy(m); setAll(a); }).finally(() => setLoading(false)); }, []);
  if (loading) return <div style={{ textAlign: "center", padding: 60, color: "var(--green-dim)" }}>Chargement...</div>;
  const owned = new Set(my.map(b => b.id));
  return (
    <div style={{ animation: "fadeUp .3s ease" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
        <span style={{ fontSize: 28 }}>🏅</span>
        <h2 style={{ fontFamily: "var(--font-hud)", fontSize: 20, color: "#00ff41" }}>COLLECTION</h2>
      </div>
      <p style={{ color: "var(--text-dim)", marginBottom: 20 }}>{my.length} / {all.length} badges obtenus</p>
      <div style={{ height: 6, background: "rgba(0,255,65,0.07)", borderRadius: 3, marginBottom: 28 }}>
        <div style={{ height: "100%", width: `${(my.length / Math.max(all.length, 1)) * 100}%`, background: "linear-gradient(90deg, #00ff41, #00e5ff)", borderRadius: 3, transition: "width 1.2s ease", boxShadow: "0 0 8px rgba(0,255,65,.35)" }}/>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(210px, 1fr))", gap: 12 }}>
        {all.map((b, i) => {
          const got = owned.has(b.id);
          return (
            <div key={b.id} style={{ padding: 20, borderRadius: 8, textAlign: "center", background: got ? `${b.color}07` : "rgba(0,0,0,0.3)", border: `1px solid ${got ? b.color + "38" : "rgba(0,255,65,0.04)"}`, filter: got ? "none" : "grayscale(.9) opacity(.35)", animation: `fadeUp .3s ease ${i * .035}s both`, transition: "transform .2s" }}
              onMouseEnter={e => got && (e.currentTarget.style.transform = "translateY(-4px)")}
              onMouseLeave={e => (e.currentTarget.style.transform = "")}>
              <div style={{ fontSize: 34, marginBottom: 10, filter: got ? `drop-shadow(0 0 7px ${b.color})` : "none" }}>{b.icon}</div>
              <div style={{ fontFamily: "var(--font-hud)", fontSize: 11, color: got ? b.color : "var(--text-dim)", fontWeight: 700 }}>{b.name}</div>
              <div style={{ color: "var(--text-dim)", fontSize: 11, marginTop: 4, lineHeight: 1.5 }}>{b.description}</div>
              <div style={{ fontFamily: "var(--font-hud)", fontSize: 10, color: got ? b.color : "rgba(255,255,255,.1)", marginTop: 7 }}>+{b.points_reward} pts</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// GUIDE PAGE
// ═══════════════════════════════════════════════════════════════════
function GuidePage() {
  const sections = [
    { icon: "🎮", title: "Comment jouer", content: "H4CKR est un escape game de cybersécurité. Vous êtes un hacker éthique recruté par une agence secrète. Chaque niveau est une mission : analyser des fichiers suspects, déchiffrer des messages, infiltrer des serveurs fictifs. Résolvez les énigmes dans l'ordre pour débloquer la suivante." },
    { icon: "🔢", title: "Encodage Base64", content: "Un message Base64 ressemble à : SGVsbG8gQWdlbnQu...\nPour décoder : utilisez notre terminal (commande 'decode <texte>') ou un site comme base64decode.org.\nTuyau : les réponses sont insensibles à la casse — essayez MAJUSCULES et minuscules." },
    { icon: "🔄", title: "Chiffrement de César / ROT13", content: "ROT13 = chaque lettre décalée de 13 positions. A→N, H→U, etc.\nDans le terminal : caesar <texte> 13\nOu utilisez rot13.com. Le texte chiffré contient souvent '_' entre les mots." },
    { icon: "🖼️", title: "Stéganographie & Métadonnées", content: "Les indices sont cachés dans les métadonnées EXIF des images (Author, Comment, GPS...).\nDans le terminal : extract <fichier.png>\nOu avec ExifTool (gratuit) : exiftool fichier.png\nCherchez le champ 'Comment' — c'est souvent là que se cache le secret." },
    { icon: "🎧", title: "Analyse Audio", content: "Les messages audio sont prononcés à l'envers ou cachés dans le spectrogramme.\nOutil recommandé : Audacity (gratuit, multiplateforme)\n1. Importez le fichier WAV\n2. Sélectionnez toute la piste → Effect → Reverse\n3. Écoutez le message révélé" },
    { icon: "💻", title: "Terminal interactif", content: "Commandes disponibles :\n• help — liste des commandes\n• ls — fichiers disponibles\n• cat <fichier> — affiche le contenu\n• decode <texte> — décode Base64\n• caesar <texte> <n> — déchiffre César\n• extract <fichier> — métadonnées EXIF\n• scan <ip> — scan de ports\n• connect <host> <port> — connexion SSH\n• clear — efface l'écran\n↑/↓ pour naviguer dans l'historique" },
    { icon: "🏅", title: "Badges & Classement", content: "Gagnez des badges en accomplissant des actions spéciales :\n🩸 First Blood — première énigme résolue\n🔓 Déchiffreur — Base64 ou César résolu\n🖼️ Stega Master — stéganographie maîtrisée\n🎧 Détective Audio — message audio trouvé\n🦅 Sans Filet — niveau sans indices\n🎩 Black Hat — niveau Expert complété\n⚡ Speed Hacker — niveau rapide" },
    { icon: "💡", title: "Conseils de pro", content: "• Lisez TOUT le texte — les indices sont dans la description\n• Essayez la réponse en majuscules, minuscules et avec/sans espaces\n• L'historique du terminal : flèche ↑ pour les commandes précédentes\n• 3ème indice = réponse révélée (mais -30 pts au total)\n• Le certificat PDF est téléchargeable dès qu'un niveau est 100% complété\n• La clé finale du niveau Expert assemble vos 3 découvertes précédentes" },
  ];
  return (
    <div style={{ animation: "fadeUp .3s ease" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 30 }}>
        <div style={{ animation: "robotFloat 3s ease-in-out infinite" }}>
          <svg width="50" height="62" viewBox="0 0 72 88" fill="none">
            <circle cx="36" cy="3" r="3" fill="#00ff41" style={{ filter: "drop-shadow(0 0 4px #00ff41)" }}/>
            <line x1="36" y1="0" x2="36" y2="10" stroke="#00ff41" strokeWidth="2"/>
            <rect x="12" y="10" width="48" height="36" rx="6" fill="#050d05" stroke="#00ff41" strokeWidth="1.5"/>
            <rect x="19" y="20" width="14" height="10" rx="2" fill="#00ff41" style={{ filter: "drop-shadow(0 0 6px #00ff41)" }}/>
            <rect x="39" y="20" width="14" height="10" rx="2" fill="#00ff41" style={{ filter: "drop-shadow(0 0 6px #00ff41)" }}/>
            <rect x="22" y="36" width="28" height="4" rx="2" fill="rgba(0,255,65,0.25)" stroke="#00ff41" strokeWidth="1"/>
            <rect x="8" y="52" width="56" height="32" rx="6" fill="#050d05" stroke="#00ff41" strokeWidth="1.5"/>
          </svg>
        </div>
        <div>
          <h2 style={{ fontFamily: "var(--font-hud)", fontSize: 22, color: "#00ff41" }}>GUIDE DE JEU</h2>
          <p style={{ color: "var(--text-dim)", marginTop: 4, fontSize: 13 }}>Tout ce qu'il faut savoir pour devenir un vrai hacker</p>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 14 }}>
        {sections.map((s, i) => (
          <div key={i} className="game-card" style={{ padding: 22, animation: `fadeUp .3s ease ${i * .05}s both` }}>
            <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
              <span style={{ fontSize: 26, flexShrink: 0 }}>{s.icon}</span>
              <div>
                <h3 style={{ fontFamily: "var(--font-hud)", fontSize: 12, color: "#00ff41", letterSpacing: 2, marginBottom: 9 }}>{s.title.toUpperCase()}</h3>
                <p style={{ color: "var(--text)", fontSize: 13, lineHeight: 1.75, whiteSpace: "pre-line" }}>{s.content}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// CONTACT PAGE
// ═══════════════════════════════════════════════════════════════════
function ContactPage() {
  const [form, setForm] = useState({ subject: "", message: "", category: "bug" });
  const [status, setStatus] = useState<{ text: string; ok: boolean } | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setStatus(null);
    try {
      await gameApi.contact(form.subject, form.message, form.category);
      setStatus({ text: "✓ Message envoyé ! Notre équipe vous répondra sous 48h.", ok: true });
      setForm(f => ({ ...f, subject: "", message: "" }));
    } catch { setStatus({ text: "Erreur d'envoi. Réessayez.", ok: false }); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ animation: "fadeUp .3s ease", maxWidth: 660, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 28 }}>
        <span style={{ fontSize: 28 }}>📡</span>
        <div>
          <h2 style={{ fontFamily: "var(--font-hud)", fontSize: 22, color: "#00ff41" }}>SUPPORT H4CKR</h2>
          <p style={{ color: "var(--text-dim)", marginTop: 4, fontSize: 13 }}>Un bug ? Une question ? L'équipe vous répond sous 48h.</p>
        </div>
      </div>
      <div style={{ marginBottom: 28 }}>
        {[
          { q: "Ma réponse n'est pas acceptée", a: "Les réponses sont insensibles à la casse. Essayez sans espaces, en MAJUSCULES, en minuscules, et sans accents." },
          { q: "Le terminal ne répond pas", a: "Tapez 'help' pour voir les commandes disponibles. Toutes les commandes sont en minuscules." },
          { q: "L'image ou l'audio ne se charge pas", a: "Les fichiers doivent être générés via la commande generate_assets dans le backend. Consultez le README pour les instructions." },
          { q: "Comment récupérer mon certificat ?", a: "Le certificat se génère automatiquement quand vous avez résolu TOUTES les énigmes d'un niveau. Un bouton apparaît alors en haut du niveau." },
        ].map((f, i) => (
          <details key={i} style={{ marginBottom: 8, background: "rgba(0,4,0,0.55)", border: "1px solid rgba(0,255,65,0.1)", borderRadius: 5, overflow: "hidden" }}>
            <summary style={{ padding: "13px 16px", cursor: "pointer", color: "#00ff41", fontFamily: "var(--font-hud)", fontSize: 11, letterSpacing: 1, userSelect: "none" }}>❓ {f.q}</summary>
            <div style={{ padding: "10px 16px 14px", color: "var(--text)", fontSize: 13, lineHeight: 1.7, borderTop: "1px solid rgba(0,255,65,0.07)" }}>{f.a}</div>
          </details>
        ))}
      </div>
      <div className="game-card" style={{ padding: 26 }}>
        <h3 style={{ fontFamily: "var(--font-hud)", fontSize: 13, color: "#00ff41", letterSpacing: 2, marginBottom: 18 }}>ENVOYER UN MESSAGE</h3>
        <form onSubmit={submit}>
          <div style={{ marginBottom: 14 }}>
            <div style={{ color: "var(--text-dim)", fontFamily: "var(--font-hud)", fontSize: 9, letterSpacing: 2, marginBottom: 7 }}>CATÉGORIE</div>
            <div style={{ display: "flex", gap: 7 }}>
              {[{ v: "bug", l: "🐛 Bug" }, { v: "suggestion", l: "💡 Suggestion" }, { v: "other", l: "📝 Autre" }].map(o => (
                <button key={o.v} type="button" className={`hud-btn ${form.category === o.v ? "active" : ""}`} onClick={() => setForm(f => ({ ...f, category: o.v }))} style={{ fontSize: 10 }}>{o.l}</button>
              ))}
            </div>
          </div>
          <div style={{ marginBottom: 14 }}>
            <div style={{ color: "var(--text-dim)", fontFamily: "var(--font-hud)", fontSize: 9, letterSpacing: 2, marginBottom: 6 }}>SUJET</div>
            <input className="game-input" value={form.subject} onChange={e => setForm(f => ({ ...f, subject: e.target.value }))} placeholder="Décrivez brièvement le problème..." required/>
          </div>
          <div style={{ marginBottom: 18 }}>
            <div style={{ color: "var(--text-dim)", fontFamily: "var(--font-hud)", fontSize: 9, letterSpacing: 2, marginBottom: 6 }}>MESSAGE</div>
            <textarea className="game-input" value={form.message} onChange={e => setForm(f => ({ ...f, message: e.target.value }))} placeholder="Détaillez votre problème..." rows={5} required style={{ resize: "vertical", minHeight: 110 }}/>
          </div>
          <button type="submit" className="hud-btn primary" disabled={loading} style={{ width: "100%", padding: 12 }}>
            {loading ? "Envoi..." : "📤 ENVOYER LE MESSAGE"}
          </button>
        </form>
        {status && <div style={{ marginTop: 14, padding: "10px 14px", borderRadius: 4, fontSize: 13, background: status.ok ? "rgba(0,255,65,0.06)" : "rgba(255,0,60,0.06)", border: `1px solid ${status.ok ? "rgba(0,255,65,.28)" : "rgba(255,0,60,.28)"}`, color: status.ok ? "#00ff41" : "#ff4060" }}>{status.text}</div>}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// MAIN GAME PAGE
// ═══════════════════════════════════════════════════════════════════
export default function GamePage() {
  const { user, logout } = useAuth();
  const [tab, setTab] = useState<"game"|"leaderboard"|"badges"|"guide"|"contact">("game");
  const [levels, setLevels] = useState<LevelOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [badge, setBadge] = useState<BadgeOut | null>(null);
  const [badgesCount, setBadgesCount] = useState(0);

  useEffect(() => {
    gameApi.getLevels().then(setLevels).finally(() => setLoading(false));
    gameApi.myBadges().then(b => setBadgesCount(b.length)).catch(() => {});
  }, []);

  const totalSolved = levels.reduce((a, l) => a + l.enigmas.filter(e => e.solved).length, 0);
  const totalEnigmas = levels.reduce((a, l) => a + l.enigmas.length, 0);
  const pct = totalEnigmas > 0 ? Math.round((totalSolved / totalEnigmas) * 100) : 0;

  const tabs = [
    { id: "game",        label: "> JEU",       icon: "🎮" },
    { id: "leaderboard", label: "> CLASSEMENT", icon: "🏆" },
    { id: "badges",      label: "> BADGES",     icon: "🏅" },
    { id: "guide",       label: "> GUIDE",      icon: "📖" },
    { id: "contact",     label: "> SUPPORT",    icon: "📡" },
  ] as const;

  return (
    <>
      <style>{GLOBAL_STYLES}</style>
      {badge && <BadgePopup badge={badge} onClose={() => setBadge(null)}/>}
      <CyberBackground/>
      <div style={{ position: "fixed", inset: 0, zIndex: 1, pointerEvents: "none", background: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,65,0.01) 2px, rgba(0,255,65,0.01) 4px)" }}/>

      <div style={{ position: "relative", zIndex: 2, minHeight: "100vh" }}>
        {/* NAVBAR */}
        <nav style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 28px", height: 58, background: "rgba(2,10,2,0.96)", borderBottom: "1px solid rgba(0,255,65,0.13)", position: "sticky", top: 0, zIndex: 200, backdropFilter: "blur(12px)" }}>
          <div style={{ fontFamily: "var(--font-hud)", fontSize: 21, fontWeight: 900, color: "#00ff41", letterSpacing: 6, textShadow: "0 0 18px rgba(0,255,65,.35)" }}>
            H4CKR<span style={{ fontSize: 10, color: "rgba(0,255,65,.3)", marginLeft: 6, letterSpacing: 1 }}>v2</span>
          </div>
          <div style={{ display: "flex", gap: 3 }}>
            {tabs.map(t => <button key={t.id} className={`hud-btn ${tab === t.id ? "active" : ""}`} onClick={() => setTab(t.id)} style={{ fontSize: 10 }}>{t.label}</button>)}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ textAlign: "right" }}>
              <div style={{ color: "#00ff41", fontFamily: "var(--font-hud)", fontSize: 12 }}>{user?.pseudo}</div>
              <div style={{ color: "var(--text-dim)", fontSize: 10 }}>{badgesCount} badges</div>
            </div>
            <button className="hud-btn danger" onClick={logout} style={{ fontSize: 10 }}>✕ LOGOUT</button>
          </div>
        </nav>

        {/* HUD BAR */}
        {tab === "game" && (
          <div style={{ display: "flex", padding: "0 28px", background: "rgba(0,4,0,0.8)", borderBottom: "1px solid rgba(0,255,65,0.07)" }}>
            {[
              { label: "PROGRESSION", value: `${pct}%`, sub: `${totalSolved}/${totalEnigmas} énigmes` },
              { label: "NIVEAUX",     value: levels.length, sub: "chargés" },
              { label: "BADGES",      value: badgesCount, sub: "obtenus" },
              { label: "AGENT",       value: user?.pseudo?.slice(0, 12), sub: user?.auth_provider },
            ].map((s, i) => (
              <div key={i} style={{ padding: "10px 24px", borderRight: "1px solid rgba(0,255,65,0.07)" }}>
                <div style={{ color: "rgba(0,255,65,0.38)", fontSize: 9, letterSpacing: 2, fontFamily: "var(--font-hud)" }}>{s.label}</div>
                <div style={{ color: "#00ff41", fontFamily: "var(--font-hud)", fontSize: 17, fontWeight: 700 }}>{s.value}</div>
                <div style={{ color: "var(--text-dim)", fontSize: 10 }}>{s.sub}</div>
              </div>
            ))}
            <div style={{ flex: 1, padding: "10px 24px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
              <div style={{ height: 5, background: "rgba(0,255,65,0.07)", borderRadius: 3, overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${pct}%`, background: "linear-gradient(90deg, #00ff41, #00e5ff)", borderRadius: 3, transition: "width 1.5s ease", boxShadow: pct > 0 ? "0 0 7px rgba(0,255,65,.35)" : "none" }}/>
              </div>
            </div>
          </div>
        )}

        {/* CONTENT */}
        <main style={{ maxWidth: 880, margin: "0 auto", padding: "32px 20px" }}>
          {tab === "game" && (
            loading
              ? <div style={{ textAlign: "center", padding: 80 }}><div style={{ fontSize: 34, marginBottom: 14, animation: "pulse 1.5s ease infinite" }}>⚡</div><div style={{ color: "var(--green-dim)", fontFamily: "var(--font-mono)" }}>Chargement des missions...</div></div>
              : levels.length === 0
                ? <div style={{ textAlign: "center", padding: 60, color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>Aucun niveau disponible. Vérifiez que le backend est démarré et la base seeded.</div>
                : levels.map(l => <LevelSection key={l.id} level={l} onBadge={b => { setBadge(b); setBadgesCount(c => c + 1); }}/>)
          )}
          {tab === "leaderboard" && <Leaderboard/>}
          {tab === "badges" && <BadgesPage/>}
          {tab === "guide" && <GuidePage/>}
          {tab === "contact" && <ContactPage/>}
        </main>

        <footer style={{ textAlign: "center", padding: "18px", borderTop: "1px solid rgba(0,255,65,0.06)", color: "rgba(0,255,65,0.2)", fontFamily: "var(--font-mono)", fontSize: 10 }}>
          H4CKR © 2025 — Escape Game Cybersécurité — <span style={{ color: "rgba(0,255,65,0.35)" }}>ALL SYSTEMS OPERATIONAL</span>
        </footer>
      </div>
    </>
  );
}
