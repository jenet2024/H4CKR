import { useState, useEffect, useRef } from "react";
import { gameApi, type LevelOut, type EnigmaOut, type LeaderboardEntry, type BadgeOut } from "../api/client";
import { useAuth } from "../hooks/useAuth";
import robotPhantom from "../assets/robot_phantom.png";
import CyberpunkRobotImage from "../components/CyberpunkRobotImage";
import Robot from "../asset/robot.png"; // ← nouvea
import Guide from "../asset/guide.png";


type Theme = "dark" | "light";

function buildStyles(t: Theme): string {
  const isDark = t === "dark";
  return `
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@400;600;700&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --green:       ${isDark ? "#00ff41" : "#009922"};
  --green-dim:   ${isDark ? "rgba(0,255,65,0.55)" : "rgba(0,153,34,0.65)"};
  --green-faint: ${isDark ? "rgba(0,255,65,0.08)" : "rgba(0,153,34,0.09)"};
  --red:         ${isDark ? "#ff003c" : "#cc0022"};
  --cyan:        ${isDark ? "#00e5ff" : "#0077cc"};
  --gold:        ${isDark ? "#ffd700" : "#b07700"};
  --bg:          ${isDark ? "#020c02" : "#f2f6f2"};
  --nav-bg:      ${isDark ? "rgba(2,10,2,0.97)" : "rgba(242,246,242,0.97)"};
  --hud-bg:      ${isDark ? "rgba(0,4,0,0.85)" : "rgba(230,240,230,0.92)"};
  --card:        ${isDark ? "rgba(3,14,3,0.93)" : "rgba(255,255,255,0.96)"};
  --border:      ${isDark ? "rgba(0,255,65,0.18)" : "rgba(0,153,34,0.22)"};
  --border-nav:  ${isDark ? "rgba(0,255,65,0.13)" : "rgba(0,153,34,0.18)"};
  --border-hud:  ${isDark ? "rgba(0,255,65,0.07)" : "rgba(0,153,34,0.1)"};
  --text:        ${isDark ? "#d4ffd4" : "#0d260d"};
  --text-dim:    ${isDark ? "rgba(212,255,212,0.52)" : "rgba(13,38,13,0.5)"};
  --font-mono: 'Share Tech Mono', monospace;
  --font-hud:  'Orbitron', sans-serif;
  --font-body: 'Rajdhani', sans-serif;
}
html, body { background: var(--bg); color: var(--text); font-family: var(--font-body); font-size: 16px; min-height: 100vh; overflow-x: hidden; transition: background .35s, color .35s; }
::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-track { background: transparent; } ::-webkit-scrollbar-thumb { background: var(--green-dim); border-radius: 3px; }
@keyframes fadeUp    { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn    { from{opacity:0} to{opacity:1} }
@keyframes blink     { 0%,100%{opacity:1} 50%{opacity:0} }
@keyframes spin      { to{transform:rotate(360deg)} }
@keyframes pulse     { 0%,100%{opacity:.6;transform:scale(1)} 50%{opacity:1;transform:scale(1.02)} }
@keyframes glow      { 0%,100%{box-shadow:0 0 8px var(--green-faint)} 50%{box-shadow:0 0 22px var(--green-dim)} }
@keyframes shake     { 0%,100%{transform:translateX(0)} 20%{transform:translateX(-5px)} 40%{transform:translateX(5px)} 60%{transform:translateX(-3px)} 80%{transform:translateX(3px)} }
@keyframes eyeBlink  { 0%,90%,100%{transform:scaleY(1)} 95%{transform:scaleY(0.05)} }
@keyframes typeBar   { 0%,100%{opacity:1} 50%{opacity:0} }
@keyframes badgePop  { 0%{transform:translateX(120px) scale(.8);opacity:0} 15%{transform:translateX(0) scale(1.05);opacity:1} 85%{transform:translateX(0) scale(1);opacity:1} 100%{transform:translateX(120px);opacity:0} }
@keyframes countUp   { from{transform:scale(1.35)} to{transform:scale(1)} }
@keyframes scanbeam  { from{top:-3px} to{top:100%} }
@keyframes levelIn   { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
@keyframes robotFloat{ 0%,100%{transform:translateY(0) rotate(-.5deg)} 50%{transform:translateY(-7px) rotate(.5deg)} }
@keyframes themeSwitch { 0%{transform:scale(1.2) rotate(-15deg)} 100%{transform:scale(1) rotate(0)} }
@keyframes glowPulse { 0%,100%{opacity:0.55} 50%{opacity:1} }
@keyframes shadowPulse { 0%,100%{transform:scale(1);opacity:0.45} 50%{transform:scale(1.25);opacity:0.85} }
.hud-btn { position:relative; background:transparent; border:1px solid var(--green-dim); color:var(--green-dim); font-family:var(--font-hud); font-size:11px; letter-spacing:2px; padding:8px 18px; cursor:pointer; text-transform:uppercase; transition:all .2s; overflow:hidden; }
.hud-btn::before { content:''; position:absolute; inset:0; background:linear-gradient(90deg,transparent,var(--green-faint),transparent); transform:translateX(-100%); transition:transform .4s; }
.hud-btn:hover::before { transform:translateX(100%); }
.hud-btn:hover { border-color:var(--green); color:var(--green); }
.hud-btn.active { border-color:var(--green); color:var(--green); background:var(--green-faint); }
.hud-btn.danger { border-color:rgba(204,0,34,.35); color:rgba(204,0,34,.55); }
.hud-btn.danger:hover { border-color:var(--red); color:var(--red); }
.hud-btn.primary { border-color:var(--green); color:${isDark ? "#000" : "#fff"}; background:var(--green); font-weight:700; }
.hud-btn.primary:hover { filter:brightness(1.1); }
.nav-arrow { background:transparent; border:1px solid var(--border); color:var(--green-dim); font-size:18px; width:44px; height:44px; cursor:pointer; display:flex; align-items:center; justify-content:center; border-radius:4px; transition:all .2s; flex-shrink:0; }
.nav-arrow:hover:not(:disabled) { border-color:var(--green); color:var(--green); background:var(--green-faint); }
.nav-arrow:disabled { opacity:.2; cursor:not-allowed; }
.game-card { background:var(--card); border:1px solid var(--border); border-radius:6px; position:relative; overflow:hidden; transition:border-color .3s,box-shadow .3s,background .35s; }
.game-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,transparent,var(--green-dim),transparent); opacity:0; transition:opacity .3s; }
.game-card:hover::before { opacity:1; }
.game-card.solved { border-color:var(--green-dim); }
.game-card.solved::before { opacity:1; }
.game-input { background:var(--green-faint); border:1px solid var(--border); border-radius:3px; padding:10px 14px; color:var(--green); font-family:var(--font-mono); font-size:13px; outline:none; width:100%; transition:border-color .2s; }
.game-input:focus { border-color:var(--green); }
.game-input::placeholder { color:var(--green-dim); opacity:.4; }
.tag { display:inline-block; padding:2px 8px; border-radius:3px; font-size:10px; letter-spacing:2px; text-transform:uppercase; font-family:var(--font-hud); border:1px solid; }
.image-container:hover .stegano-overlay { opacity: 1 !important; }
.image-container:hover img { filter: brightness(1.15) !important; }
details summary { list-style:none; } details summary::-webkit-details-marker { display:none; }
`;
}

// ── Cyber Background ─────────────────────────────────────────────
function CyberBackground({ theme }: { theme: Theme }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isDark = theme === "dark";
  const col = isDark ? "0,255,65" : "0,120,40";
  useEffect(() => {
    const c = canvasRef.current!; const ctx = c.getContext("2d")!; let raf: number;
    const resize = () => { c.width = window.innerWidth; c.height = window.innerHeight; };
    resize(); window.addEventListener("resize", resize);
    const pts = Array.from({ length: isDark ? 55 : 35 }, () => ({
      x: Math.random() * window.innerWidth, y: Math.random() * window.innerHeight,
      vx: (Math.random() - .5) * .25, vy: (Math.random() - .5) * .25, r: Math.random() * 1.3 + .3,
    }));
    const draw = () => {
      ctx.clearRect(0, 0, c.width, c.height);
      ctx.strokeStyle = `rgba(${col},${isDark ? "0.022" : "0.04"})`; ctx.lineWidth = 1;
      for (let x = 0; x < c.width; x += 64) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, c.height); ctx.stroke(); }
      for (let y = 0; y < c.height; y += 64) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(c.width, y); ctx.stroke(); }
      pts.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > c.width) p.vx *= -1;
        if (p.y < 0 || p.y > c.height) p.vy *= -1;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${col},${isDark ? "0.42" : "0.28"})`; ctx.fill();
      });
      pts.forEach((a, i) => pts.slice(i + 1).forEach(b => {
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d < 100) { ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.strokeStyle = `rgba(${col},${(.12*(1-d/100)).toFixed(3)})`; ctx.lineWidth=.5; ctx.stroke(); }
      }));
      raf = requestAnimationFrame(draw);
    };
    draw(); return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", resize); };
  }, [theme]);
  return <canvas ref={canvasRef} style={{ position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none" }} />;
}

// ── Theme Toggle ─────────────────────────────────────────────────
function ThemeToggle({ theme, onToggle }: { theme: Theme; onToggle: () => void }) {
  const isDark = theme === "dark";
  return (
    <button onClick={onToggle} title={isDark ? "Passer en mode clair" : "Passer en mode sombre"}
      style={{ display: "flex", alignItems: "center", gap: 7, padding: "5px 10px", background: "var(--green-faint)", border: "1px solid var(--border)", borderRadius: 20, cursor: "pointer", transition: "all .3s", fontFamily: "var(--font-hud)", fontSize: 9, letterSpacing: 1.5, color: "var(--green)", flexShrink: 0 }}>
      <span style={{ fontSize: 14, lineHeight: 1, animation: "themeSwitch .4s ease", display: "inline-block" }}>{isDark ? "🌙" : "☀️"}</span>
    </button>
  );
}

// ── Robot Guide avec vidéo ────────────────────────────────────────
function RobotGuide({ text, onDone, accent = "#00ff41", theme, videoFile }: {
  text: string; onDone?: () => void; accent?: string; theme: Theme; videoFile?: string;
}) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  const [showVideo, setShowVideo] = useState(false);
  const idx = useRef(0);
  const isDark = theme === "dark";

  useEffect(() => {
    idx.current = 0; setDisplayed(""); setDone(false);
    const id = setInterval(() => {
      if (idx.current < text.length) { setDisplayed(text.slice(0, ++idx.current)); }
      else { clearInterval(id); setDone(true); }
    }, 18);
    return () => clearInterval(id);
  }, [text]);

  // Lecteur vidéo plein écran
  if (showVideo && videoFile) {
    return (
      <div style={{ position: "fixed", inset: 0, zIndex: 9998, background: "#000", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <video
          src={`/video/${videoFile}`}
          autoPlay
          controls
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
          onEnded={() => { setShowVideo(false); onDone?.(); }}
        />
        <button
          onClick={() => { setShowVideo(false); onDone?.(); }}
          style={{ position: "absolute", top: 20, right: 20, background: "rgba(0,0,0,0.7)", border: "1px solid rgba(255,255,255,0.3)", color: "#fff", padding: "8px 16px", cursor: "pointer", borderRadius: 4, fontFamily: "var(--font-hud)", fontSize: 11, letterSpacing: 2 }}>
          PASSER ✕
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", gap: 20, alignItems: "flex-start", padding: "20px 28px", background: isDark ? "rgba(0,20,0,0.6)" : "rgba(230,248,230,0.85)", borderBottom: "1px solid var(--border-hud)", animation: "fadeIn .4s ease" }}>
      <div style={{ flexShrink: 0, animation: "robotFloat 3s ease-in-out infinite" }}>
        <svg width="68" height="84" viewBox="0 0 72 88" fill="none">
          <line x1="36" y1="0" x2="36" y2="10" stroke={accent} strokeWidth="2" />
          <circle cx="36" cy="3" r="3" fill={accent} />
          <rect x="12" y="10" width="48" height="36" rx="6" fill={isDark ? "#050d05" : "#e8f4e8"} stroke={accent} strokeWidth="1.5" />
          <rect x="19" y="20" width="14" height="10" rx="2" fill={accent} style={{ animation: "eyeBlink 4s ease-in-out infinite", transformOrigin: "26px 25px" }} />
          <rect x="39" y="20" width="14" height="10" rx="2" fill={accent} style={{ animation: "eyeBlink 4s ease-in-out infinite .15s", transformOrigin: "46px 25px" }} />
          <rect x="22" y="36" width="28" height="4" rx="2" fill={`${accent}30`} stroke={accent} strokeWidth="1" />
          {[24,29,34,39,44].map(x => <rect key={x} x={x} y="37" width="2" height="2" rx="1" fill={accent} />)}
          <rect x="30" y="46" width="12" height="6" rx="2" fill={isDark ? "#050d05" : "#e8f4e8"} stroke={accent} strokeWidth="1" />
          <rect x="8" y="52" width="56" height="32" rx="6" fill={isDark ? "#050d05" : "#e8f4e8"} stroke={accent} strokeWidth="1.5" />
          <rect x="16" y="58" width="16" height="12" rx="2" fill={`${accent}08`} stroke={accent} strokeWidth="1" />
          <rect x="40" y="58" width="16" height="12" rx="2" fill={`${accent}08`} stroke={accent} strokeWidth="1" />
          {[0,1,2].map(i => <rect key={i} x={18+i*4} y={60} width="2" height={4+i*2} rx="1" fill={accent} opacity="0.8" />)}
          <polyline points="40,64 44,60 46,68 50,58 52,68 54,64 56,64" stroke={accent} strokeWidth="1.5" fill="none" />
          <rect x="0" y="54" width="8" height="20" rx="4" fill={isDark ? "#050d05" : "#e8f4e8"} stroke={accent} strokeWidth="1" />
          <rect x="64" y="54" width="8" height="20" rx="4" fill={isDark ? "#050d05" : "#e8f4e8"} stroke={accent} strokeWidth="1" />
        </svg>
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ color: accent, fontFamily: "var(--font-hud)", fontSize: 10, letterSpacing: 3, marginBottom: 8, opacity: 0.7 }}>● NEXUS-7 — IA GUIDE</div>
        <div style={{ background: isDark ? "rgba(0,255,65,0.04)" : "rgba(0,153,34,0.05)", border: `1px solid ${isDark ? "rgba(0,255,65,0.18)" : "rgba(0,153,34,0.2)"}`, borderRadius: "4px 12px 12px 12px", padding: "14px 18px", color: "var(--text)", fontFamily: "var(--font-body)", fontSize: 15, lineHeight: 1.7, minHeight: 50 }}>
          {displayed}{!done && <span style={{ animation: "typeBar .8s step-end infinite", color: accent }}>█</span>}
        </div>
        {done && (
          <div style={{ display: "flex", gap: 10, marginTop: 10, flexWrap: "wrap" }}>
            {videoFile && (
              <button className="hud-btn" onClick={() => setShowVideo(true)} style={{ fontSize: 10 }}>
                ▶ Voir la vidéo d'intro
              </button>
            )}
            <button className="hud-btn primary" onClick={() => onDone?.()} style={{ fontSize: 10 }}>
              Commencer la mission →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Terminal ─────────────────────────────────────────────────────
function Terminal({ enigmaId, accent = "#00ff41", theme }: { enigmaId?: number; accent?: string; theme: Theme }) {
  const [history, setHistory] = useState<Array<{ type: "input"|"output"|"error"|"success"; text: string }>>([{ type: "output", text: "H4CKR Terminal v2.0 — Système actif\nTapez 'help' pour la liste des commandes.\n─────────────────────────────────────────" }]);
  const [input, setInput] = useState(""); const [loading, setLoading] = useState(false);
  const [cmdHist, setCmdHist] = useState<string[]>([]); const [histIdx, setHistIdx] = useState(-1);
  const endRef = useRef<HTMLDivElement>(null); const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [history]);
  const run = async (e?: React.FormEvent) => {
    e?.preventDefault(); const cmd = input.trim(); if (!cmd || loading) return;
    setInput(""); setHistIdx(-1); setCmdHist(h => [cmd, ...h.slice(0, 49)]);
    setHistory(h => [...h, { type: "input", text: cmd }]);
    if (cmd.toLowerCase() === "clear") { setHistory([]); return; }
    setLoading(true);
    try { const res = await gameApi.terminal(cmd, enigmaId); setHistory(h => [...h, { type: res.success ? "success" : "output", text: res.output }]); }
    catch { setHistory(h => [...h, { type: "error", text: "Commande non reconnue. Tapez 'help'." }]); }
    finally { setLoading(false); setTimeout(() => inputRef.current?.focus(), 50); }
  };
  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowUp") { const ni = Math.min(histIdx+1, cmdHist.length-1); setHistIdx(ni); setInput(cmdHist[ni]??""); }
    else if (e.key === "ArrowDown") { const ni = Math.max(histIdx-1, -1); setHistIdx(ni); setInput(ni===-1?"":cmdHist[ni]); }
  };
  const isDark = theme === "dark";
  const col = { input: accent, output: isDark ? "rgba(200,255,200,0.75)" : "rgba(0,60,0,0.8)", error: "#cc2222", success: isDark ? "#80ff80" : "#007722" };
  return (
    <div style={{ background: isDark ? "#000" : "#f0f6f0", border: `1px solid ${accent}35`, borderRadius: 6, overflow: "hidden" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 14px", background: `${accent}08`, borderBottom: `1px solid ${accent}15` }}>
        {["#ff5f57","#febc2e","#28c840"].map((c,i) => <div key={i} style={{ width:10, height:10, borderRadius:"50%", background:c, opacity:.7 }}/>)}
        <span style={{ marginLeft:6, color:`${accent}60`, fontFamily:"var(--font-mono)", fontSize:11 }}>h4ckr@terminal:~$</span>
      </div>
      <div style={{ padding:"14px 16px", minHeight:200, maxHeight:320, overflowY:"auto", fontFamily:"var(--font-mono)", fontSize:12.5 }} onClick={() => inputRef.current?.focus()}>
        {history.map((h,i) => (
          <div key={i} style={{ marginBottom:3 }}>
            {h.type==="input" ? <div><span style={{ color:`${accent}55` }}>$ </span><span style={{ color:accent }}>{h.text}</span></div> : <pre style={{ color:col[h.type], margin:0, whiteSpace:"pre-wrap", lineHeight:1.6 }}>{h.text}</pre>}
          </div>
        ))}
        {loading && <div style={{ color:`${accent}55` }}><span style={{ animation:"blink .6s step-end infinite" }}>▐ </span>traitement...</div>}
        <div ref={endRef}/>
      </div>
      <form onSubmit={run} style={{ display:"flex", alignItems:"center", padding:"8px 16px", borderTop:`1px solid ${accent}12`, gap:8 }}>
        <span style={{ color:`${accent}55`, fontFamily:"var(--font-mono)", fontSize:12 }}>$</span>
        <input ref={inputRef} value={input} onChange={e => setInput(e.target.value)} onKeyDown={onKey}
          style={{ flex:1, background:"none", border:"none", outline:"none", color:accent, fontFamily:"var(--font-mono)", fontSize:12.5, caretColor:accent }}
          placeholder="commande..." spellCheck={false} autoComplete="off" disabled={loading}/>
        {loading && <div style={{ width:11, height:11, border:`2px solid ${accent}30`, borderTopColor:accent, borderRadius:"50%", animation:"spin .6s linear infinite" }}/>}
      </form>
    </div>
  );
}

// ── Enigma Card ───────────────────────────────────────────────────
const TYPE_CFG: Record<string, { label: string; color: string; colorLight: string; icon: string; placeholder: string }> = {
  base64:   { label:"BASE64",         color:"#00e5ff", colorLight:"#0077cc", icon:"🔢", placeholder:"Mot de passe décodé..." },
  caesar:   { label:"CHIFFREMENT",    color:"#ff9900", colorLight:"#995500", icon:"🔄", placeholder:"Message déchiffré..." },
  stegano:  { label:"STÉGANOGRAPHIE", color:"#cc44ff", colorLight:"#7711cc", icon:"🖼️", placeholder:"Commentaire trouvé..." },
  audio:    { label:"AUDIO",          color:"#ff6b35", colorLight:"#cc3300", icon:"🎧", placeholder:"Mot prononcé à l'envers..." },
  logs:     { label:"ANALYSE LOGS",   color:"#ffd700", colorLight:"#886600", icon:"📋", placeholder:"Adresse IP ou valeur..." },
  terminal: { label:"TERMINAL",       color:"#00ff41", colorLight:"#009922", icon:"💻", placeholder:"" },
  metadata: { label:"METADATA",       color:"#ff4488", colorLight:"#cc1155", icon:"🔍", placeholder:"Valeur trouvée..." },
  default:  { label:"ÉNIGME",         color:"#00ff41", colorLight:"#009922", icon:"❓", placeholder:"Votre réponse..." },
};

function EnigmaCard({ enigma, index, isLocked, onSolve, theme }: {
  enigma: EnigmaOut; index: number; isLocked: boolean; onSolve: (b?: BadgeOut) => void; theme: Theme;
}) {
  const [answer, setAnswer] = useState("");
  const [msg, setMsg] = useState<{ text: string; ok: boolean }|null>(null);
  const [hint, setHint] = useState("");
  const [loading, setLoading] = useState(false);
  const [solved, setSolved] = useState(enigma.solved);
  const [shake, setShake] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const cfgBase = TYPE_CFG[enigma.type] ?? TYPE_CFG.default;
  const color = theme === "dark" ? cfgBase.color : cfgBase.colorLight;
  const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
  const isDark = theme === "dark";

  if (isLocked) return (
    <div style={{ background: isDark ? "rgba(0,0,0,0.35)" : "rgba(200,220,200,0.4)", border:"1px solid var(--border)", borderRadius:6, padding:"18px 22px", opacity:0.4, display:"flex", alignItems:"center", gap:14, marginBottom:12 }}>
      <span style={{ fontSize:22 }}>🔒</span>
      <div>
        <div style={{ color:"var(--green-dim)", fontFamily:"var(--font-hud)", fontSize:12 }}>Énigme {index+1} — {enigma.title}</div>
        <div style={{ color:"var(--text-dim)", fontSize:11, marginTop:2 }}>Résolvez l'énigme précédente pour débloquer</div>
      </div>
    </div>
  );

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); if (!answer.trim()||loading) return;
    setLoading(true); setMsg(null);
    try {
      const res = await gameApi.submitAnswer(enigma.id, answer);
      setMsg({ text:res.message, ok:res.correct });
      if (res.correct) { setSolved(true); onSolve(res.badge_earned??undefined); }
      else { setShake(true); setTimeout(()=>setShake(false),500); setShowHint(true); if(res.hint) setHint(res.hint); }
    } catch(err: any) { setMsg({ text:err?.detail??"Erreur", ok:false }); }
    finally { setLoading(false); }
  };

  const askHint = async () => { try { const r = await gameApi.requestHint(enigma.id); setHint(r.hint); } catch {} };

  return (
    <div className={`game-card ${solved?"solved":""}`}
      style={{ padding:24, marginBottom:14, animation:`fadeUp .35s ease ${index*.08}s both`, ...(shake?{animation:"shake .4s ease"}:{}) }}>
      <div style={{ position:"absolute", top:0, left:0, right:0, height:2, background:`linear-gradient(90deg,transparent,${color}55,transparent)`, opacity:solved?1:0.3 }}/>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:14, flexWrap:"wrap", gap:8 }}>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <span className="tag" style={{ color, borderColor:`${color}45`, background:`${color}12` }}>{cfgBase.icon} {cfgBase.label}</span>
          <h3 style={{ fontFamily:"var(--font-hud)", fontSize:14, color:"var(--text)" }}>{index+1}. {enigma.title}</h3>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          {solved && <span style={{ color:"var(--green)", fontFamily:"var(--font-hud)", fontSize:10, letterSpacing:2, animation:"countUp .4s ease" }}>✓ RÉSOLU</span>}
          <span style={{ fontFamily:"var(--font-hud)", fontSize:17, color }}>{enigma.points}<span style={{ fontSize:9, opacity:0.5, marginLeft:2 }}>PTS</span></span>
        </div>
      </div>
      <div style={{ background:isDark?"rgba(0,0,0,0.3)":"rgba(220,240,220,0.5)", borderLeft:`3px solid ${color}40`, borderRadius:"0 4px 4px 0", padding:"12px 16px", marginBottom:16, color:"var(--text)", fontFamily:"var(--font-mono)", fontSize:12.5, lineHeight:1.8, whiteSpace:"pre-wrap" }}>
        {enigma.description}
      </div>

      {/* IMAGE STEGANO */}
      {enigma.type === "stegano" && enigma.file_path && (
        <div className="image-container" style={{ position:"relative", display:"inline-block", maxWidth:"100%", cursor:"pointer", marginBottom:16 }}>
          <img src={`${API}/assets/${enigma.file_path}`} alt="Fichier suspect"
            style={{ maxWidth:"100%", maxHeight:280, objectFit:"contain", border:`2px solid ${color}40`, borderRadius:4, display:"block", filter:"brightness(0.9)", transition:"filter 0.3s ease" }}/>
          <div style={{ position:"absolute", top:0, left:0, right:0, height:3, background:`linear-gradient(90deg,transparent,${color}80,transparent)`, animation:"scanbeam 3s linear infinite", zIndex:5 }}/>
          <div className="stegano-overlay"
            style={{ position:"absolute", inset:0, display:"flex", alignItems:"center", justifyContent:"center", background:"rgba(0,0,0,0.75)", color:"#ff0040", fontFamily:"Orbitron, sans-serif", fontSize:"22px", letterSpacing:"3px", opacity:0, transition:"opacity 0.4s ease", borderRadius:"8px", zIndex:10 }}>
            GHOST_PROTOCOL
          </div>
          <div style={{ position:"absolute", bottom:8, left:0, right:0, textAlign:"center", color:`${color}90`, fontFamily:"var(--font-hud)", fontSize:9, letterSpacing:2, pointerEvents:"none", zIndex:6 }}>
            SURVOLEZ POUR RÉVÉLER
          </div>
        </div>
      )}

      {/* IMAGE STANDARD */}
      {enigma.file_path?.match(/\.(png|jpg|jpeg|gif)$/i) && enigma.type !== "stegano" && (
        <div style={{ marginBottom:16 }}>
          <div style={{ color:"var(--green-dim)", fontSize:10, letterSpacing:2, marginBottom:8, fontFamily:"var(--font-hud)" }}>🖼️ FICHIER IMAGE</div>
          <img src={`${API}/assets/${enigma.file_path}`} alt="Image de l'énigme"
            style={{ maxWidth:"100%", borderRadius:6, border:`1px solid ${color}40`, display:"block" }}/>
        </div>
      )}

      {/* AUDIO */}
      {enigma.file_path?.match(/\.(wav|mp3|ogg|flac)$/i) && (
        <div style={{ marginBottom:16 }}>
          <div style={{ color:"var(--green-dim)", fontSize:10, letterSpacing:2, marginBottom:8, fontFamily:"var(--font-hud)" }}>🎧 SIGNAL AUDIO — Analysez attentivement</div>
          <div style={{ background:isDark?"rgba(0,0,0,0.5)":"rgba(220,240,220,0.6)", border:`1px solid ${color}30`, borderRadius:8, padding:"16px 20px" }}>
            <div style={{ display:"flex", alignItems:"center", gap:14, marginBottom:10 }}>
              <div style={{ fontSize:28, animation:"pulse 2s ease-in-out infinite", flexShrink:0 }}>📻</div>
              <div style={{ flex:1 }}>
                <div style={{ color, fontFamily:"var(--font-hud)", fontSize:10, letterSpacing:2, marginBottom:8 }}>{enigma.file_path.split("/").pop()?.toUpperCase()}</div>
                <audio controls preload="metadata" src={`${API}/assets/${enigma.file_path}`}
                  style={{ width:"100%", height:40, accentColor:color, display:"block" }}/>
              </div>
            </div>
            <div style={{ color:isDark?"rgba(255,165,0,0.65)":"rgba(150,80,0,0.8)", fontSize:11, fontFamily:"var(--font-mono)", lineHeight:1.5 }}>
              💡 Écoutez attentivement les syllabes — reconstituez le mot dans le bon ordre.
            </div>
          </div>
        </div>
      )}

      {/* FICHIER TEXTE */}
      {enigma.file_path?.match(/\.(txt|log|b64)$/i) && (
        <div style={{ marginBottom:16 }}>
          <div style={{ color:"var(--green-dim)", fontSize:10, letterSpacing:2, marginBottom:8, fontFamily:"var(--font-hud)" }}>📄 FICHIER DE DONNÉES</div>
          <a href={`${API}/assets/${enigma.file_path}`} target="_blank" rel="noopener noreferrer" className="hud-btn" style={{ display:"inline-block", textDecoration:"none", fontSize:10 }}>
            ⬇ Télécharger {enigma.file_path.split("/").pop()}
          </a>
        </div>
      )}

      {/* TERMINAL */}
      {enigma.type === "terminal" && !solved && (
        <div style={{ marginBottom:16 }}><Terminal enigmaId={enigma.id} accent={color} theme={theme}/></div>
      )}

      {/* FORMULAIRE */}
      {!solved && enigma.type !== "terminal" && (
        <form onSubmit={submit}>
          <div style={{ color:"var(--green-dim)", fontSize:10, letterSpacing:2, marginBottom:6, fontFamily:"var(--font-hud)" }}>VOTRE RÉPONSE</div>
          <div style={{ display:"flex", gap:8 }}>
            <input className="game-input" value={answer} onChange={e => setAnswer(e.target.value)} placeholder={cfgBase.placeholder} autoComplete="off"/>
            <button type="submit" className="hud-btn" disabled={loading} style={{ whiteSpace:"nowrap", fontFamily:"var(--font-hud)", fontSize:10 }}>
              {loading ? <span style={{ width:13, height:13, border:"2px solid var(--green-dim)", borderTopColor:"var(--green)", borderRadius:"50%", display:"inline-block", animation:"spin .6s linear infinite" }}/> : "VALIDER ▶"}
            </button>
          </div>
        </form>
      )}

      {msg && <div style={{ marginTop:10, padding:"9px 13px", borderRadius:4, fontSize:13, background:msg.ok?"var(--green-faint)":isDark?"rgba(255,0,60,0.07)":"rgba(200,0,30,0.07)", border:`1px solid ${msg.ok?"var(--green-dim)":isDark?"rgba(255,0,60,.3)":"rgba(180,0,20,.3)"}`, color:msg.ok?"var(--green)":"var(--red)", fontFamily:"var(--font-mono)", animation:"fadeIn .2s ease" }}>{msg.text}</div>}
      {hint && <div style={{ marginTop:8, padding:"9px 13px", borderRadius:4, fontSize:12, background:isDark?"rgba(255,200,0,0.04)":"rgba(180,140,0,0.07)", border:isDark?"1px solid rgba(255,200,0,0.2)":"1px solid rgba(140,100,0,0.25)", color:isDark?"#ffc800":"#7a5c00", fontFamily:"var(--font-mono)", animation:"fadeIn .3s ease" }}>💡 {hint}</div>}
      {showHint && !solved && (
        <button onClick={askHint} style={{ marginTop:8, background:"none", border:"none", color:"var(--text-dim)", fontSize:11, cursor:"pointer", padding:0, fontFamily:"var(--font-mono)" }}
          onMouseEnter={e => (e.currentTarget.style.color="var(--green)")}
          onMouseLeave={e => (e.currentTarget.style.color="var(--text-dim)")}>
          → Obtenir un indice (-10 pts)
        </button>
      )}
    </div>
  );
}

// ── Level View ────────────────────────────────────────────────────
const ROBOT_INTROS: Record<string, string> = {
  beginner: "Bienvenue Agent. Je suis NEXUS-7, votre IA de soutien tactique. Ce niveau va tester vos bases : mots de passe forts, détection de phishing, stéganographie et analyse audio. Chaque énigme se débloque quand vous résolvez la précédente. Restez concentré — le réseau vous observe.",
  expert: "Agent. Niveau EXPERT chargé. Ici on simule un vrai pentest : analyse de logs serveur compromis, intrusion réseau SSH, extraction de métadonnées cachées, et terminal interactif live. Les erreurs coûtent des points. Bonne chance.",
  default: "Nouvelle mission opérationnelle. Des indices sont cachés dans des fichiers, images et sons. Lisez chaque énigme attentivement.",
};
const LEVEL_COLORS_DARK  = ["#00ff41","#00e5ff","#ff9900","#cc44ff","#ff003c"];
const LEVEL_COLORS_LIGHT = ["#009922","#0077cc","#996600","#7711cc","#cc0022"];

function LevelView({ level, levelIndex, onBadge, theme }: { level: LevelOut; levelIndex: number; onBadge: (b: BadgeOut) => void; theme: Theme }) {
  const [robotDone, setRobotDone] = useState(false);
  const [enigmas, setEnigmas] = useState<EnigmaOut[]>([...level.enigmas].sort((a,b) => a.order-b.order));
  const [genCert, setGenCert] = useState(false);
  const isDark = theme === "dark";
  const accent = (isDark ? LEVEL_COLORS_DARK : LEVEL_COLORS_LIGHT)[levelIndex % 5];
  const solved = enigmas.filter(e => e.solved).length;
  const total = enigmas.length;
  const complete = solved === total && total > 0;
  const pct = total > 0 ? (solved/total)*100 : 0;

  const handleSolve = (i: number) => (badge?: BadgeOut) => {
    setEnigmas(prev => prev.map((e,j) => j===i ? {...e, solved:true} : e));
    if (badge) onBadge(badge);
  };

  const downloadCert = async () => {
    setGenCert(true);
    try { const cert = await gameApi.generateCertificate(level.slug); window.open(gameApi.downloadCertificate(cert.unique_code), "_blank"); }
    catch(e: any) { alert(e?.detail??"Impossible de générer le certificat"); }
    finally { setGenCert(false); }
  };

  return (
    <div style={{ animation:"levelIn .5s ease" }}>
      <div style={{ display:"flex", gap:24, alignItems:"flex-start" }}>
        <div style={{ flex:1, minWidth:0 }}>
          {/* Header niveau */}
          <div style={{ display:"flex", alignItems:"center", gap:14, marginBottom:18, padding:"16px 20px", background:isDark?"rgba(0,6,0,0.9)":"rgba(240,250,240,0.95)", border:`1px solid ${accent}35`, borderRadius:8, position:"relative", overflow:"hidden" }}>
            <div style={{ position:"absolute", top:0, left:0, right:0, height:2, background:`linear-gradient(90deg,transparent,${accent}70,transparent)` }}/>
            <div style={{ width:46, height:46, borderRadius:"50%", border:`2px solid ${accent}65`, display:"flex", alignItems:"center", justifyContent:"center", background:`${accent}12`, fontFamily:"var(--font-hud)", fontSize:18, color:accent, animation:"glow 2s ease-in-out infinite", flexShrink:0 }}>{level.order}</div>
            <div style={{ flex:1 }}>
              <div style={{ fontFamily:"var(--font-hud)", fontSize:17, color:"var(--text)", fontWeight:700, marginBottom:3 }}>{level.name}</div>
              <div style={{ color:"var(--text-dim)", fontSize:13, lineHeight:1.5 }}>{level.description}</div>
            </div>
            <div style={{ textAlign:"right", flexShrink:0 }}>
              <div style={{ fontFamily:"var(--font-hud)", fontSize:15, color:complete?"var(--green)":accent, marginBottom:2 }}>{solved}/{total}{complete?" ✓":""}</div>
              <div style={{ color:"var(--text-dim)", fontSize:11 }}>{level.max_points} pts max</div>
            </div>
          </div>

          {/* Progress bar */}
          <div style={{ height:5, background:isDark?"rgba(0,255,65,0.06)":"rgba(0,100,30,0.1)", borderRadius:3, marginBottom:18, overflow:"hidden" }}>
            <div style={{ height:"100%", width:`${pct}%`, background:`linear-gradient(90deg,${accent},${accent}99)`, transition:"width 1.2s ease", borderRadius:3 }}/>
          </div>

          {/* Certificat */}
          {complete && (
            <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"14px 22px", marginBottom:18, background:"var(--green-faint)", border:"1px solid var(--green-dim)", borderRadius:6, animation:"glow 2.5s ease-in-out infinite" }}>
              <div>
                <div style={{ color:"var(--green)", fontFamily:"var(--font-hud)", fontSize:13 }}>🏆 NIVEAU COMPLÉTÉ !</div>
                <div style={{ color:"var(--text-dim)", fontSize:11, marginTop:2 }}>Générez votre certificat officiel H4CKR</div>
              </div>
              <button className="hud-btn primary" onClick={downloadCert} disabled={genCert} style={{ fontSize:10 }}>{genCert?"Génération...":"⬇ Télécharger Certificat"}</button>
            </div>
          )}

          {/* Robot guide */}
          {!robotDone && (
            <div style={{ marginBottom:18, background:isDark?"rgba(0,6,0,0.9)":"rgba(240,250,240,0.95)", border:`1px solid ${accent}25`, borderRadius:8, overflow:"hidden" }}>
              <RobotGuide
                text={ROBOT_INTROS[level.slug] ?? ROBOT_INTROS.default}
                accent={accent}
                onDone={() => setRobotDone(true)}
                theme={theme}
                videoFile={level.video_file}
              />
            </div>
          )}

          {/* Enigmas */}
          {enigmas.map((e,i) => <EnigmaCard key={e.id} enigma={e} index={i} isLocked={i>0&&!enigmas[i-1].solved} onSolve={handleSolve(i)} theme={theme}/>)}
        </div>

        {/* Robot colonne droite */}
        <div style={{ width:225, flexShrink:0, position:"sticky", top:76, display:"flex", flexDirection:"column", alignItems:"center", gap:14 }}>
          <div style={{ padding:"18px 8px", background:isDark?"rgba(0,6,0,0.7)":"rgba(240,250,240,0.9)", border:`1px solid ${accent}22`, borderRadius:12, width:"100%", display:"flex", justifyContent:"center", position:"relative", overflow:"hidden" }}>
            {/* Fond radial */}
            <div style={{ position:"absolute", inset:0, background:`radial-gradient(ellipse at center bottom,${accent}07 0%,transparent 70%)` }}/>

            {/* Paillettes animées */}
            <div style={{ position:"absolute", inset:0, pointerEvents:"none", overflow:"hidden" }}>
              {[
                { top:"8%",  left:"12%", size:4, delay:0,    dur:2.1 },
                { top:"15%", left:"78%", size:3, delay:0.4,  dur:1.8 },
                { top:"30%", left:"88%", size:5, delay:0.8,  dur:2.4 },
                { top:"55%", left:"6%",  size:3, delay:1.2,  dur:1.9 },
                { top:"70%", left:"82%", size:4, delay:0.6,  dur:2.2 },
                { top:"85%", left:"20%", size:3, delay:1.5,  dur:2.0 },
                { top:"22%", left:"45%", size:2, delay:0.3,  dur:1.7 },
                { top:"60%", left:"55%", size:3, delay:1.0,  dur:2.3 },
                { top:"42%", left:"92%", size:2, delay:1.8,  dur:1.6 },
                { top:"75%", left:"35%", size:4, delay:0.9,  dur:2.5 },
              ].map((p, i) => (
                <div key={i} style={{
                  position:"absolute", top:p.top, left:p.left,
                  width:p.size, height:p.size,
                  borderRadius:"50%",
                  background: i % 3 === 0 ? "rgba(120,0,30,0.9)" : i % 3 === 1 ? "rgba(0,255,65,0.8)" : "rgba(255,215,0,0.7)",
                  boxShadow: i % 3 === 0 ? "0 0 4px rgba(120,0,30,0.8)" : i % 3 === 1 ? "0 0 4px rgba(0,255,65,0.6)" : "0 0 4px rgba(255,215,0,0.6)",
                  animation:`sparkle ${p.dur}s ease-in-out ${p.delay}s infinite`,
                }}/>
              ))}
            </div>

            <CyberpunkRobotImage src={Robot} theme={theme} size={260} animate={true}/>

            {/* Keyframes paillettes */}
            <style>{`
              @keyframes sparkle {
                0%,100% { opacity:0; transform:scale(0.5) rotate(0deg); }
                50% { opacity:1; transform:scale(1.3) rotate(180deg); }
              }
            `}</style>
          </div>
          <div style={{ width:"100%", background:isDark?"rgba(0,4,0,0.8)":"rgba(240,250,240,0.9)", border:"1px solid var(--border)", borderRadius:8, padding:"12px 14px" }}>
            <div style={{ color:"var(--green-dim)", fontFamily:"var(--font-hud)", fontSize:8, letterSpacing:3, marginBottom:7, opacity:0.7 }}>● AGENT DE MISSION</div>
            <div style={{ color:"var(--text-dim)", fontSize:11, fontFamily:"var(--font-mono)", lineHeight:1.9 }}>
              <div>STATUS: <span style={{ color:complete?"var(--green)":accent }}>{complete?"MISSION OK":"EN COURS"}</span></div>
              <div>ENIGMES: <span style={{ color:accent }}>{solved}/{total}</span></div>
              <div>NIVEAU: <span style={{ color:accent }}>{level.name.slice(0,14).toUpperCase()}</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Game Tab ──────────────────────────────────────────────────────
function GameTab({ levels, onBadge, theme }: { levels: LevelOut[]; onBadge: (b: BadgeOut) => void; theme: Theme }) {
  const [cur, setCur] = useState(0);
  if (levels.length === 0) return <div style={{ textAlign:"center", padding:60, color:"var(--text-dim)", fontFamily:"var(--font-mono)" }}>Aucun niveau disponible. Vérifiez le backend.</div>;
  const level = levels[cur];
  const isDark = theme === "dark";
  const accent = (isDark ? LEVEL_COLORS_DARK : LEVEL_COLORS_LIGHT)[cur % 5];
  return (
    <div>
      <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:26, padding:"12px 16px", background:isDark?"rgba(0,6,0,0.88)":"rgba(236,248,236,0.95)", border:"1px solid var(--border-nav)", borderRadius:8 }}>
        <button className="nav-arrow" onClick={() => setCur(i => i-1)} disabled={cur===0}>‹</button>
        <div style={{ flex:1, display:"flex", gap:6, justifyContent:"center", flexWrap:"wrap" }}>
          {levels.map((l,i) => {
            const lc = (isDark ? LEVEL_COLORS_DARK : LEVEL_COLORS_LIGHT)[i%5];
            const ls = l.enigmas.filter(e => e.solved).length, lt = l.enigmas.length;
            const lk = ls===lt && lt>0; const active = i===cur;
            return (
              <button key={l.id} onClick={() => setCur(i)}
                style={{ padding:"5px 11px", background:active?`${lc}14`:"transparent", border:`1px solid ${active?lc:`${lc}30`}`, borderRadius:4, color:active?lc:`${lc}55`, fontFamily:"var(--font-hud)", fontSize:8, letterSpacing:2, cursor:"pointer", transition:"all .2s", display:"flex", flexDirection:"column", alignItems:"center", gap:2 }}
                onMouseEnter={e => { if(!active){(e.currentTarget as HTMLButtonElement).style.borderColor=lc;(e.currentTarget as HTMLButtonElement).style.color=lc;} }}
                onMouseLeave={e => { if(!active){(e.currentTarget as HTMLButtonElement).style.borderColor=`${lc}30`;(e.currentTarget as HTMLButtonElement).style.color=`${lc}55`;} }}>
                <span>{lk?"✓":`L${l.order}`}</span>
                <span style={{ fontSize:6, opacity:0.7 }}>{ls}/{lt}</span>
              </button>
            );
          })}
        </div>
        <div style={{ textAlign:"center", minWidth:90 }}>
          <div style={{ color:accent, fontFamily:"var(--font-hud)", fontSize:10, letterSpacing:2 }}>LEVEL {cur+1}/{levels.length}</div>
          <div style={{ color:"var(--text-dim)", fontSize:9, marginTop:1 }}>{level.name.slice(0,14)}</div>
        </div>
        <button className="nav-arrow" onClick={() => setCur(i => i+1)} disabled={cur===levels.length-1}>›</button>
      </div>
      <LevelView key={level.id} level={level} levelIndex={cur} onBadge={onBadge} theme={theme}/>
    </div>
  );
}

// ── Badge Popup ───────────────────────────────────────────────────
function BadgePopup({ badge, onClose, theme }: { badge: BadgeOut; onClose: () => void; theme: Theme }) {
  useEffect(() => { const t = setTimeout(onClose, 5000); return () => clearTimeout(t); }, []);
  const isDark = theme === "dark";
  return (
    <div style={{ position:"fixed", top:24, right:24, zIndex:9999, minWidth:275, background:isDark?"rgba(0,10,0,0.97)":"rgba(240,252,240,0.98)", border:`2px solid ${badge.color}`, borderRadius:8, padding:"18px 22px", boxShadow:`0 0 40px ${badge.color}35`, animation:"badgePop 5s ease forwards" }}>
      <div style={{ display:"flex", gap:14, alignItems:"center" }}>
        <div style={{ fontSize:38, filter:`drop-shadow(0 0 8px ${badge.color})`, animation:"pulse 1s ease-in-out infinite" }}>{badge.icon}</div>
        <div>
          <div style={{ color:badge.color, fontFamily:"var(--font-hud)", fontSize:10, letterSpacing:3 }}>BADGE DÉBLOQUÉ !</div>
          <div style={{ color:"var(--text)", fontSize:15, fontWeight:700, marginTop:2 }}>{badge.name}</div>
          <div style={{ color:"var(--text-dim)", fontSize:12, marginTop:2 }}>{badge.description}</div>
          <div style={{ color:badge.color, fontFamily:"var(--font-hud)", fontSize:11, marginTop:5 }}>+{badge.points_reward} pts</div>
        </div>
      </div>
      <button onClick={onClose} style={{ position:"absolute", top:8, right:10, background:"none", border:"none", color:"var(--text-dim)", cursor:"pointer", fontSize:16 }}>×</button>
    </div>
  );
}

// ── Leaderboard ───────────────────────────────────────────────────
function Leaderboard({ theme }: { theme: Theme }) {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]); const [loading, setLoading] = useState(true);
  useEffect(() => {
    gameApi.leaderboard()
      .then(data => setEntries([...data].sort((a,b) => (b.total_points??0)-(a.total_points??0))))
      .finally(() => setLoading(false));
  }, []);
  const isDark = theme === "dark";
  if (loading) return <div style={{ textAlign:"center", padding:60, color:"var(--green-dim)", fontFamily:"var(--font-mono)" }}><div style={{ fontSize:28, marginBottom:12, animation:"pulse 1.5s ease infinite" }}>⚡</div>Chargement...</div>;
  return (
    <div style={{ animation:"fadeUp .3s ease" }}>

      {/* ── Robot bannière animée ── */}
      <div style={{
        position:"relative", display:"flex", alignItems:"center", justifyContent:"center",
        marginBottom:32, padding:"28px 0 0", overflow:"hidden",
      }}>
        {/* Halo de fond */}
        <div style={{
          position:"absolute", top:"50%", left:"50%",
          transform:"translate(-50%,-50%)",
          width:320, height:160,
          background: isDark
            ? "radial-gradient(ellipse, rgba(0,255,65,0.12) 0%, transparent 70%)"
            : "radial-gradient(ellipse, rgba(0,153,34,0.10) 0%, transparent 70%)",
          pointerEvents:"none",
        }}/>

        {/* Robot image */}
        <div style={{
          position:"relative",
          animation:"leaderRobotFloat 3.5s ease-in-out infinite",
          filter: isDark
            ? "drop-shadow(0 0 28px rgba(0,255,65,0.5)) drop-shadow(0 18px 18px rgba(0,0,0,0.7))"
            : "drop-shadow(0 0 20px rgba(0,153,34,0.4)) drop-shadow(0 16px 16px rgba(0,0,0,0.25))",
        }}>
          <img
            src={robotPhantom}
            alt="Robot classement"
            style={{ width:160, height:160, objectFit:"contain", userSelect:"none", pointerEvents:"none" }}
          />
          {/* Ombre au sol */}
          <div style={{
            position:"absolute", bottom:-14, left:"50%",
            transform:"translateX(-50%)",
            width:90, height:18,
            background: isDark ? "rgba(0,255,65,0.22)" : "rgba(0,100,30,0.18)",
            filter:"blur(10px)",
            borderRadius:"50%",
            animation:"leaderShadow 3.5s ease-in-out infinite",
          }}/>
        </div>

        {/* Titre à droite du robot */}
        <div style={{ marginLeft:28, display:"flex", flexDirection:"column", gap:6 }}>
          <div style={{ color:"var(--green-dim)", fontFamily:"var(--font-hud)", fontSize:9, letterSpacing:4 }}>
            ● CLASSEMENT EN DIRECT
          </div>
          <h2 style={{ fontFamily:"var(--font-hud)", fontSize:26, fontWeight:900, color:"var(--green)", letterSpacing:4, lineHeight:1, textShadow: isDark ? "0 0 20px rgba(0,255,65,0.4)" : "none" }}>
            CLASSEMENT
          </h2>
          <div style={{ fontFamily:"var(--font-hud)", fontSize:14, color:"var(--cyan)", letterSpacing:3 }}>
            MONDIAL
          </div>
          <div style={{ color:"var(--text-dim)", fontSize:11, fontFamily:"var(--font-mono)", marginTop:4 }}>
            {entries.length} agent{entries.length > 1 ? "s" : ""} classé{entries.length > 1 ? "s" : ""}
          </div>
        </div>

        {/* Keyframes inline */}
        <style>{`
          @keyframes leaderRobotFloat {
            0%,100% { transform: translateY(0px) rotate(-0.5deg); }
            50%      { transform: translateY(-12px) rotate(0.5deg); }
          }
          @keyframes leaderShadow {
            0%,100% { transform: translateX(-50%) scale(1);   opacity: 0.8; }
            50%      { transform: translateX(-50%) scale(0.7); opacity: 0.4; }
          }
        `}</style>
      </div>

      <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:24 }}><span style={{ fontSize:28 }}>🏆</span><h2 style={{ fontFamily:"var(--font-hud)", fontSize:20, color:"var(--green)" }}>CLASSEMENT MONDIAL</h2></div>
      <div style={{ display:"grid", gridTemplateColumns:"50px 1fr 120px 80px 100px", gap:8, padding:"8px 14px", color:"var(--text-dim)", fontFamily:"var(--font-hud)", fontSize:9, letterSpacing:2, borderBottom:"1px solid var(--border)", marginBottom:8 }}>
        <span>#</span><span>AGENT</span><span>NIVEAU</span><span>BADGES</span><span style={{ textAlign:"right" }}>SCORE</span>
      </div>
      {entries.map((e,i) => (
        <div key={e.user_id} style={{ display:"grid", gridTemplateColumns:"50px 1fr 120px 80px 100px", gap:8, padding:"13px 14px", marginBottom:4, background:i<3?`rgba(0,${isDark?255:150},65,${0.07-i*0.02})`:isDark?"rgba(0,4,0,0.5)":"rgba(240,248,240,0.7)", border:"1px solid var(--border)", borderRadius:5, alignItems:"center", animation:`fadeUp .3s ease ${i*.04}s both`, transition:"transform .2s" }}
          onMouseEnter={ev => { ev.currentTarget.style.transform="translateX(5px)"; }}
          onMouseLeave={ev => { ev.currentTarget.style.transform=""; }}>
          <span style={{ fontFamily:"var(--font-hud)", fontSize:15, color:i===0?"#b07700":i===1?"#808080":i===2?"#7f5020":"var(--text-dim)" }}>{i===0?"🥇":i===1?"🥈":i===2?"🥉":e.rank}</span>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <div style={{ width:30, height:30, borderRadius:"50%", background:"var(--green-faint)", border:"1px solid var(--border)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:13, color:"var(--green)" }}>{e.pseudo[0]?.toUpperCase()}</div>
            <span style={{ color:"var(--text)", fontSize:14, fontWeight:600 }}>{e.pseudo}</span>
          </div>
          <span style={{ color:"var(--text-dim)", fontSize:12 }}>{e.level_reached}</span>
          <span style={{ color:"var(--text-dim)", fontSize:12 }}>🏅 {e.badges_count}</span>
          <span style={{ fontFamily:"var(--font-hud)", fontSize:15, color:"var(--green)", textAlign:"right" }}>{e.total_points.toLocaleString()}</span>
        </div>
      ))}
      {entries.length===0 && <div style={{ textAlign:"center", padding:40, color:"var(--text-dim)", fontFamily:"var(--font-mono)" }}>Aucun agent classé pour le moment...</div>}
    </div>
  );
}

// ── Badges ────────────────────────────────────────────────────────
function BadgesPage({ theme }: { theme: Theme }) {
  const [my, setMy] = useState<BadgeOut[]>([]); const [all, setAll] = useState<BadgeOut[]>([]); const [loading, setLoading] = useState(true);
  useEffect(() => { Promise.all([gameApi.myBadges(), gameApi.allBadges()]).then(([m,a]) => { setMy(m); setAll(a); }).finally(() => setLoading(false)); }, []);
  if (loading) return <div style={{ textAlign:"center", padding:60, color:"var(--green-dim)" }}>Chargement...</div>;
  const owned = new Set(my.map(b => b.id));
  return (
    <div style={{ animation:"fadeUp .3s ease" }}>
      <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:8 }}><span style={{ fontSize:28 }}>🏅</span><h2 style={{ fontFamily:"var(--font-hud)", fontSize:20, color:"var(--green)" }}>COLLECTION</h2></div>
      <p style={{ color:"var(--text-dim)", marginBottom:20 }}>{my.length} / {all.length} badges obtenus</p>
      <div style={{ height:6, background:"var(--green-faint)", borderRadius:3, marginBottom:28 }}>
        <div style={{ height:"100%", width:`${(my.length/Math.max(all.length,1))*100}%`, background:"linear-gradient(90deg,var(--green),var(--cyan))", borderRadius:3, transition:"width 1.2s ease" }}/>
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(210px,1fr))", gap:12 }}>
        {all.map((b,i) => {
          const got = owned.has(b.id);
          return (
            <div key={b.id} style={{ padding:20, borderRadius:8, textAlign:"center", background:got?`${b.color}08`:theme==="dark"?"rgba(0,0,0,0.3)":"rgba(220,235,220,0.5)", border:`1px solid ${got?b.color+"38":"var(--border)"}`, filter:got?"none":"grayscale(.8) opacity(.35)", animation:`fadeUp .3s ease ${i*.035}s both`, transition:"transform .2s" }}
              onMouseEnter={e => got&&(e.currentTarget.style.transform="translateY(-4px)")}
              onMouseLeave={e => (e.currentTarget.style.transform="")}>
              <div style={{ fontSize:34, marginBottom:10 }}>{b.icon}</div>
              <div style={{ fontFamily:"var(--font-hud)", fontSize:11, color:got?b.color:"var(--text-dim)", fontWeight:700 }}>{b.name}</div>
              <div style={{ color:"var(--text-dim)", fontSize:11, marginTop:4, lineHeight:1.5 }}>{b.description}</div>
              <div style={{ fontFamily:"var(--font-hud)", fontSize:10, color:got?b.color:"var(--text-dim)", marginTop:7, opacity:got?1:0.3 }}>+{b.points_reward} pts</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Guide ─────────────────────────────────────────────────────────
function GuidePage({ theme }: { theme: Theme }) {
  const isDark = theme === "dark";
  const [activeCard, setActiveCard] = useState<number | null>(null);
  const [typedText, setTypedText] = useState("");
  const fullText = "NEXUS-7 > Bienvenue Agent. Ce guide contient tout ce qu'il faut savoir pour compléter vos missions. Lisez attentivement chaque section avant de commencer.";

  useEffect(() => {
    let i = 0; setTypedText("");
    const id = setInterval(() => { if (i < fullText.length) { setTypedText(fullText.slice(0, ++i)); } else clearInterval(id); }, 22);
    return () => clearInterval(id);
  }, []);

  const sections = [
    { icon:"🎮", title:"Comment jouer", color:"#00ff41", colorLight:"#009922",
      content:"H4CKR est un escape game de cybersécurité. Vous êtes un hacker éthique recruté par une agence secrète. Chaque niveau est une mission : analyser des fichiers suspects, déchiffrer des messages, infiltrer des serveurs fictifs. Résolvez les énigmes dans l'ordre pour débloquer la suivante.",
      tip:"Lisez toujours la description complète de chaque énigme." },
    { icon:"🔒", title:"Mots de passe forts", color:"#00e5ff", colorLight:"#0077cc",
      content:"Un bon mot de passe : 12+ caractères, majuscules, minuscules, chiffres ET symboles spéciaux.\nExemple fort : P@ssw0rd!2024#Zx\nExemple faible : 123456 ou password",
      tip:"Cherchez le mot de passe qui respecte TOUTES les règles." },
    { icon:"🎣", title:"Phishing", color:"#ff9900", colorLight:"#996600",
      content:"Vérifiez toujours l'adresse email de l'expéditeur.\nUn domaine falsifié remplace une lettre par un chiffre (paypa1 au lieu de paypal).\nNe cliquez jamais sur un lien urgent sans vérifier.",
      tip:"Regardez chaque caractère du domaine — un seul suffit à trahir l'arnaque." },
    { icon:"🔄", title:"Chiffrement César / ROT13", color:"#cc44ff", colorLight:"#7711cc",
      content:"ROT13 = chaque lettre décalée de 13 positions. A→N, H→U, etc.\nDans le terminal : caesar <texte> 13\nOu utilisez rot13.com.",
      tip:"Appliquez ROT13 deux fois pour revenir au texte d'origine." },
    { icon:"🖼️", title:"Stéganographie", color:"#ff4488", colorLight:"#cc1155",
      content:"Un indice est caché dans l'image — survolez-la avec la souris pour le révéler.\nLa zone encadrée indique où chercher.",
      tip:"Passez lentement la souris sur toute la surface de l'image." },
    { icon:"🎧", title:"Analyse Audio", color:"#ff6b35", colorLight:"#cc3300",
      content:"Écoutez attentivement les syllabes prononcées.\nReconstituez le mot dans le bon ordre et entrez-le en majuscules.",
      tip:"Notez chaque syllabe sur papier avant de les assembler." },
    { icon:"💻", title:"Terminal interactif", color:"#00ff41", colorLight:"#009922",
      content:"Commandes : help · ls · cat <f> · decode <t> · caesar <t> <n> · extract <f> · scan <ip> · connect <h> <p> · clear\n↑/↓ pour naviguer dans l'historique",
      tip:"Tapez 'help' pour voir toutes les commandes disponibles." },
    { icon:"💡", title:"Conseils de pro", color:"#ffd700", colorLight:"#997700",
      content:"• Lisez TOUT le texte — les indices sont dans la description\n• Essayez majuscules, minuscules, sans espaces\n• 3ème indice = -30 pts au total\n• Le certificat PDF se génère quand le niveau est 100% complété",
      tip:"Les réponses sont insensibles à la casse — essayez plusieurs variantes." },
  ];

  return (
    <div style={{ animation:"fadeUp .3s ease" }}>

      {/* ── HERO ── */}
      <div style={{ position:"relative", marginBottom:36, padding:"28px 24px", background:isDark?"rgba(0,6,0,0.92)":"rgba(236,250,236,0.95)", border:"1px solid var(--border)", borderRadius:12, overflow:"hidden" }}>
        <div style={{ position:"absolute", inset:0, backgroundImage:`linear-gradient(var(--border-hud) 1px,transparent 1px),linear-gradient(90deg,var(--border-hud) 1px,transparent 1px)`, backgroundSize:"32px 32px", pointerEvents:"none" }}/>
        <div style={{ position:"absolute", top:0, left:0, right:0, height:2, background:"linear-gradient(90deg,transparent,var(--green),transparent)" }}/>
        <div style={{ display:"flex", alignItems:"center", gap:28, position:"relative", zIndex:1, flexWrap:"wrap" }}>
          {/* Robot phantom avec ombre rouge — même que page Jeu */}
          <div style={{ flexShrink:0, position:"relative" }}>
            {/* Halo rouge derrière */}
            <div style={{ position:"absolute", inset:0, background:"rgba(120,0,30,0.25)", filter:"blur(30px)", borderRadius:20, animation:"glowPulse 4s ease-in-out infinite" }}/>
            {/* Image robot */}
            <div style={{ position:"relative", animation:"robotFloat 3.5s ease-in-out infinite", filter:"drop-shadow(0 0 22px rgba(120,0,30,0.6)) drop-shadow(0 0 8px rgba(0,255,65,0.2))" }}>
              <img src={Guide} alt="NEXUS-7" style={{ width:160, height:160, objectFit:"contain", userSelect:"none", pointerEvents:"none" }}/>
            </div>
            {/* Ombre au sol */}
            <div style={{ position:"absolute", bottom:-10, left:"50%", transform:"translateX(-50%)", width:90, height:18, background:"rgba(120,0,30,0.35)", filter:"blur(10px)", borderRadius:"50%", animation:"shadowPulse 3.5s ease-in-out infinite" }}/>
          </div>
          <div style={{ flex:1, minWidth:260 }}>
            <div style={{ color:"var(--green)", fontFamily:"var(--font-hud)", fontSize:9, letterSpacing:4, marginBottom:6, opacity:0.7 }}>● NEXUS-7 — MODULE FORMATION</div>
            <h2 style={{ fontFamily:"var(--font-hud)", fontSize:24, fontWeight:900, color:"var(--green)", letterSpacing:4, marginBottom:12, textShadow:isDark?"0 0 20px rgba(0,255,65,.35)":"none" }}>GUIDE DE JEU</h2>
            <div style={{ background:isDark?"rgba(0,0,0,0.4)":"rgba(220,240,220,0.6)", border:"1px solid var(--border)", borderRadius:6, padding:"11px 14px", fontFamily:"var(--font-mono)", fontSize:12, color:"var(--text)", lineHeight:1.7, minHeight:48 }}>
              <span style={{ color:"var(--green)" }}>&gt; </span>{typedText}
              <span style={{ animation:"typeBar .8s step-end infinite", color:"var(--green)" }}>█</span>
            </div>
          </div>
          <div style={{ display:"flex", flexDirection:"column", gap:8, flexShrink:0 }}>
            {[{ label:"SECTIONS", value:sections.length, color:"var(--green)" },{ label:"NIVEAUX", value:"2", color:"var(--cyan)" },{ label:"ÉNIGMES", value:"9+", color:"var(--gold)" }].map((s,i) => (
              <div key={i} style={{ background:isDark?"rgba(0,0,0,0.4)":"rgba(220,240,220,0.6)", border:`1px solid ${s.color}30`, borderRadius:6, padding:"8px 16px", textAlign:"center", minWidth:78 }}>
                <div style={{ fontFamily:"var(--font-hud)", fontSize:20, fontWeight:900, color:s.color }}>{s.value}</div>
                <div style={{ fontFamily:"var(--font-hud)", fontSize:8, color:"var(--text-dim)", letterSpacing:2 }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── CARDS ── */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(340px,1fr))", gap:14 }}>
        {sections.map((s,i) => {
          const col = isDark ? s.color : s.colorLight;
          const isActive = activeCard === i;
          return (
            <div key={i} className="game-card"
              onMouseEnter={() => setActiveCard(i)} onMouseLeave={() => setActiveCard(null)}
              style={{ padding:22, animation:`fadeUp .35s ease ${i*.06}s both`, cursor:"pointer", transition:"transform .2s,box-shadow .2s,border-color .2s", transform:isActive?"translateY(-4px)":"translateY(0)", boxShadow:isActive?`0 8px 28px ${col}20`:"none", borderColor:isActive?`${col}40`:"var(--border)" }}>
              <div style={{ position:"absolute", top:0, left:0, right:0, height:3, background:`linear-gradient(90deg,transparent,${col},transparent)`, opacity:isActive?1:0.3, transition:"opacity .2s" }}/>
              <div style={{ display:"flex", gap:14, alignItems:"flex-start" }}>
                <div style={{ width:46, height:46, borderRadius:10, background:`${col}12`, border:`1px solid ${col}35`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:22, flexShrink:0, boxShadow:isActive?`0 0 14px ${col}30`:"none", transition:"box-shadow .2s" }}>
                  {s.icon}
                </div>
                <div style={{ flex:1 }}>
                  <h3 style={{ fontFamily:"var(--font-hud)", fontSize:11, color:col, letterSpacing:2, marginBottom:10 }}>{s.title.toUpperCase()}</h3>
                  <p style={{ color:"var(--text)", fontSize:12.5, lineHeight:1.75, whiteSpace:"pre-line", marginBottom:12 }}>{s.content}</p>
                  <div style={{ display:"flex", gap:8, alignItems:"flex-start", padding:"9px 12px", background:`${col}08`, border:`1px solid ${col}20`, borderRadius:5, borderLeft:`3px solid ${col}` }}>
                    <span style={{ fontSize:12, flexShrink:0 }}>💡</span>
                    <span style={{ fontSize:11, color:col, fontFamily:"var(--font-mono)", lineHeight:1.5, opacity:0.9 }}>{s.tip}</span>
                  </div>
                </div>
              </div>
              <div style={{ position:"absolute", bottom:8, right:14, fontFamily:"var(--font-hud)", fontSize:40, fontWeight:900, color:col, opacity:0.04, lineHeight:1, userSelect:"none" }}>
                {String(i+1).padStart(2,"0")}
              </div>
            </div>
          );
        })}
      </div>

      {/* ── FOOTER ── */}
      <div style={{ marginTop:30, padding:"18px 22px", background:isDark?"rgba(0,6,0,0.8)":"rgba(236,250,236,0.9)", border:"1px solid var(--border)", borderRadius:8, display:"flex", alignItems:"center", gap:16, flexWrap:"wrap" }}>
        <div style={{ animation:"robotFloat 3s ease-in-out infinite", flexShrink:0 }}>
          <svg width="34" height="42" viewBox="0 0 72 88" fill="none">
            <circle cx="36" cy="3" r="3" fill="var(--green)"/>
            <line x1="36" y1="0" x2="36" y2="10" stroke="var(--green)" strokeWidth="2"/>
            <rect x="12" y="10" width="48" height="36" rx="6" fill={isDark?"#050d05":"#e8f4e8"} stroke="var(--green)" strokeWidth="1.5"/>
            <rect x="19" y="20" width="14" height="10" rx="2" fill="var(--green)"/>
            <rect x="39" y="20" width="14" height="10" rx="2" fill="var(--green)"/>
            <rect x="8" y="52" width="56" height="32" rx="6" fill={isDark?"#050d05":"#e8f4e8"} stroke="var(--green)" strokeWidth="1.5"/>
          </svg>
        </div>
        <div style={{ flex:1 }}>
          <div style={{ fontFamily:"var(--font-hud)", fontSize:9, color:"var(--green)", letterSpacing:2, marginBottom:4 }}>NEXUS-7 — CONSEIL FINAL</div>
          <div style={{ fontFamily:"var(--font-mono)", fontSize:12, color:"var(--text-dim)", lineHeight:1.6, fontStyle:"italic" }}>
            "La patience est la première compétence d'un bon hacker. Lisez, observez, analysez — les réponses sont toujours dans les détails."
          </div>
        </div>
        <div style={{ display:"flex", gap:8 }}>
          {["🔐","🎯","⚡","🏆"].map((e,i) => (
            <div key={i} style={{ width:36, height:36, borderRadius:8, background:"var(--green-faint)", border:"1px solid var(--border)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:18, animation:`pulse ${1.5+i*.3}s ease-in-out infinite` }}>{e}</div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Contact ───────────────────────────────────────────────────────
function ContactPage({ theme }: { theme: Theme }) {
  const [form, setForm] = useState({ subject:"", message:"", category:"bug" });
  const [status, setStatus] = useState<{ text: string; ok: boolean }|null>(null);
  const [loading, setLoading] = useState(false);
  const isDark = theme === "dark";
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setLoading(true); setStatus(null);
    try { await gameApi.contact(form.subject, form.message, form.category); setStatus({ text:"✓ Message envoyé ! Notre équipe vous répondra sous 48h.", ok:true }); setForm(f => ({...f, subject:"", message:""})); }
    catch { setStatus({ text:"Erreur d'envoi. Réessayez.", ok:false }); }
    finally { setLoading(false); }
  };
  return (
    <div style={{ animation:"fadeUp .3s ease", maxWidth:660, margin:"0 auto" }}>
      <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:28 }}>
        <span style={{ fontSize:28 }}>📡</span>
        <div>
          <h2 style={{ fontFamily:"var(--font-hud)", fontSize:22, color:"var(--green)" }}>SUPPORT H4CKR</h2>
          <p style={{ color:"var(--text-dim)", marginTop:4, fontSize:13 }}>Un bug ? Une question ? L'équipe vous répond sous 48h.</p>
        </div>
      </div>
      <div style={{ marginBottom:28 }}>
        {[
          { q:"Ma réponse n'est pas acceptée", a:"Les réponses sont insensibles à la casse. Essayez sans espaces, en MAJUSCULES, en minuscules, et sans accents." },
          { q:"Le terminal ne répond pas", a:"Tapez 'help' pour voir les commandes disponibles." },
          { q:"L'image ou l'audio ne se charge pas", a:"Vérifiez que le backend est démarré et que les fichiers sont dans assets/enigmas/." },
          { q:"Comment récupérer mon certificat ?", a:"Le certificat se génère quand vous avez résolu TOUTES les énigmes d'un niveau." },
        ].map((f,i) => (
          <details key={i} style={{ marginBottom:8, background:isDark?"rgba(0,4,0,0.55)":"rgba(232,248,232,0.8)", border:"1px solid var(--border)", borderRadius:5, overflow:"hidden" }}>
            <summary style={{ padding:"13px 16px", cursor:"pointer", color:"var(--green)", fontFamily:"var(--font-hud)", fontSize:11, letterSpacing:1, userSelect:"none" }}>❓ {f.q}</summary>
            <div style={{ padding:"10px 16px 14px", color:"var(--text)", fontSize:13, lineHeight:1.7, borderTop:"1px solid var(--border-hud)" }}>{f.a}</div>
          </details>
        ))}
      </div>
      <div className="game-card" style={{ padding:26 }}>
        <h3 style={{ fontFamily:"var(--font-hud)", fontSize:13, color:"var(--green)", letterSpacing:2, marginBottom:18 }}>ENVOYER UN MESSAGE</h3>
        <form onSubmit={submit}>
          <div style={{ marginBottom:14 }}>
            <div style={{ color:"var(--text-dim)", fontFamily:"var(--font-hud)", fontSize:9, letterSpacing:2, marginBottom:7 }}>CATÉGORIE</div>
            <div style={{ display:"flex", gap:7 }}>
              {[{v:"bug",l:"🐛 Bug"},{v:"suggestion",l:"💡 Suggestion"},{v:"other",l:"📝 Autre"}].map(o =>
                <button key={o.v} type="button" className={`hud-btn ${form.category===o.v?"active":""}`} onClick={() => setForm(f => ({...f, category:o.v}))} style={{ fontSize:10 }}>{o.l}</button>
              )}
            </div>
          </div>
          <div style={{ marginBottom:14 }}>
            <div style={{ color:"var(--text-dim)", fontFamily:"var(--font-hud)", fontSize:9, letterSpacing:2, marginBottom:6 }}>SUJET</div>
            <input className="game-input" value={form.subject} onChange={e => setForm(f => ({...f, subject:e.target.value}))} placeholder="Décrivez brièvement le problème..." required/>
          </div>
          <div style={{ marginBottom:18 }}>
            <div style={{ color:"var(--text-dim)", fontFamily:"var(--font-hud)", fontSize:9, letterSpacing:2, marginBottom:6 }}>MESSAGE</div>
            <textarea className="game-input" value={form.message} onChange={e => setForm(f => ({...f, message:e.target.value}))} placeholder="Détaillez votre problème..." rows={5} required style={{ resize:"vertical", minHeight:110 }}/>
          </div>
          <button type="submit" className="hud-btn primary" disabled={loading} style={{ width:"100%", padding:12 }}>{loading?"Envoi...":"📤 ENVOYER LE MESSAGE"}</button>
        </form>
        {status && <div style={{ marginTop:14, padding:"10px 14px", borderRadius:4, fontSize:13, background:status.ok?"var(--green-faint)":isDark?"rgba(255,0,60,0.07)":"rgba(200,0,30,0.07)", border:`1px solid ${status.ok?"var(--green-dim)":"var(--red)"}`, color:status.ok?"var(--green)":"var(--red)" }}>{status.text}</div>}
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
  const [badge, setBadge] = useState<BadgeOut|null>(null);
  const [badgesCount, setBadgesCount] = useState(0);
  const [theme, setTheme] = useState<Theme>(() => {
    try { return (localStorage.getItem("h4ckr-theme") as Theme) || "dark"; } catch { return "dark"; }
  });

  const toggleTheme = () => {
    const next: Theme = theme === "dark" ? "light" : "dark";
    setTheme(next);
    try { localStorage.setItem("h4ckr-theme", next); } catch {}
  };

  useEffect(() => {
    gameApi.getLevels().then(setLevels).finally(() => setLoading(false));
    gameApi.myBadges().then(b => setBadgesCount(b.length)).catch(() => {});
  }, []);

  const totalSolved = levels.reduce((a,l) => a + l.enigmas.filter(e => e.solved).length, 0);
  const totalEnigmas = levels.reduce((a,l) => a + l.enigmas.length, 0);
  const pct = totalEnigmas > 0 ? Math.round((totalSolved/totalEnigmas)*100) : 0;
  const isDark = theme === "dark";
  const tabs = [
    { id:"game",        label:"> JEU" },
    { id:"leaderboard", label:"> CLASSEMENT" },
    { id:"badges",      label:"> BADGES" },
    { id:"guide",       label:"> GUIDE" },
    { id:"contact",     label:"> SUPPORT" },
  ] as const;

  return (
    <>
      <style>{buildStyles(theme)}</style>
      {badge && <BadgePopup badge={badge} onClose={() => setBadge(null)} theme={theme}/>}
      <CyberBackground theme={theme}/>
      {isDark && <div style={{ position:"fixed", inset:0, zIndex:1, pointerEvents:"none", background:"repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,65,0.01) 2px,rgba(0,255,65,0.01) 4px)" }}/>}

      <div style={{ position:"relative", zIndex:2, minHeight:"100vh" }}>
        <nav style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"0 20px", height:58, background:"var(--nav-bg)", borderBottom:"1px solid var(--border-nav)", position:"sticky", top:0, zIndex:200, backdropFilter:"blur(12px)", gap:12 }}>
          <div style={{ fontFamily:"var(--font-hud)", fontSize:19, fontWeight:900, color:"var(--green)", letterSpacing:5, textShadow:isDark?"0 0 14px rgba(0,255,65,.3)":"none", flexShrink:0 }}>
            H4CKR<span style={{ fontSize:9, color:"var(--green-dim)", marginLeft:5, letterSpacing:1 }}>v2</span>
          </div>
          <div style={{ display:"flex", gap:3, flexWrap:"wrap", justifyContent:"center" }}>
            {tabs.map(t => <button key={t.id} className={`hud-btn ${tab===t.id?"active":""}`} onClick={() => setTab(t.id)} style={{ fontSize:9 }}>{t.label}</button>)}
          </div>
          <div style={{ display:"flex", alignItems:"center", gap:10, flexShrink:0 }}>
            <ThemeToggle theme={theme} onToggle={toggleTheme}/>
            <div style={{ textAlign:"right" }}>
              <div style={{ color:"var(--green)", fontFamily:"var(--font-hud)", fontSize:11 }}>{user?.pseudo}</div>
              <div style={{ color:"var(--text-dim)", fontSize:10 }}>{badgesCount} badges</div>
            </div>
            <button className="hud-btn danger" onClick={logout} style={{ fontSize:9 }}>✕</button>
          </div>
        </nav>

        {tab === "game" && (
          <div style={{ display:"flex", padding:"0 28px", background:"var(--hud-bg)", borderBottom:"1px solid var(--border-hud)" }}>
            {[
              { label:"PROGRESSION", value:`${pct}%`,        sub:`${totalSolved}/${totalEnigmas} énigmes` },
              { label:"NIVEAUX",     value:levels.length,     sub:"chargés" },
              { label:"BADGES",      value:badgesCount,       sub:"obtenus" },
              { label:"AGENT",       value:user?.pseudo?.slice(0,12), sub:user?.auth_provider },
            ].map((s,i) => (
              <div key={i} style={{ padding:"10px 22px", borderRight:"1px solid var(--border-hud)" }}>
                <div style={{ color:"var(--green-dim)", fontSize:9, letterSpacing:2, fontFamily:"var(--font-hud)", opacity:0.7 }}>{s.label}</div>
                <div style={{ color:"var(--green)", fontFamily:"var(--font-hud)", fontSize:16, fontWeight:700 }}>{s.value}</div>
                <div style={{ color:"var(--text-dim)", fontSize:10 }}>{s.sub}</div>
              </div>
            ))}
            <div style={{ flex:1, padding:"10px 24px", display:"flex", flexDirection:"column", justifyContent:"center" }}>
              <div style={{ height:5, background:"var(--green-faint)", borderRadius:3, overflow:"hidden" }}>
                <div style={{ height:"100%", width:`${pct}%`, background:"linear-gradient(90deg,var(--green),var(--cyan))", borderRadius:3, transition:"width 1.5s ease" }}/>
              </div>
            </div>
          </div>
        )}

        <main style={{ maxWidth:1100, margin:"0 auto", padding:"32px 20px" }}>
          {tab==="game" && (
            loading
              ? <div style={{ textAlign:"center", padding:80 }}><div style={{ fontSize:34, marginBottom:14, animation:"pulse 1.5s ease infinite" }}>⚡</div><div style={{ color:"var(--green-dim)", fontFamily:"var(--font-mono)" }}>Chargement des missions...</div></div>
              : <GameTab levels={levels} onBadge={b => { setBadge(b); setBadgesCount(c => c+1); }} theme={theme}/>
          )}
          {tab==="leaderboard" && <Leaderboard theme={theme}/>}
          {tab==="badges"      && <BadgesPage theme={theme}/>}
          {tab==="guide"       && <GuidePage theme={theme}/>}
          {tab==="contact"     && <ContactPage theme={theme}/>}
        </main>

        <footer style={{ textAlign:"center", padding:"18px", borderTop:"1px solid var(--border-nav)", color:"var(--text-dim)", fontFamily:"var(--font-mono)", fontSize:10 }}>
          H4CKR © 2025 — Escape Game Cybersécurité — <span style={{ color:"var(--green-dim)" }}>ALL SYSTEMS OPERATIONAL</span>
        </footer>
      </div>
    </>
  );
}