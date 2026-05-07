import { useState, useEffect, useRef } from "react";
import { useAuth } from "../hooks/useAuth";
import { authApi } from "../api/client";

// ── Glitch text effect ────────────────────────────────────────────────────────
function GlitchTitle({ text }: { text: string }) {
  return (
    <div className="glitch-wrap" data-text={text}>
      <span className="glitch-main">{text}</span>
      <span className="glitch-clone1" aria-hidden>{text}</span>
      <span className="glitch-clone2" aria-hidden>{text}</span>
    </div>
  );
}

// ── Animated matrix rain ──────────────────────────────────────────────────────
function MatrixRain() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const chars = "01アイウエオカキクケコH4CKR@#$%^&*";
    const fontSize = 13;
    const cols = Math.floor(canvas.width / fontSize);
    const drops = Array(cols).fill(1);

    const draw = () => {
      ctx.fillStyle = "rgba(0,0,0,0.05)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#00ff41";
      ctx.font = `${fontSize}px 'Courier New', monospace`;
      drops.forEach((y, i) => {
        const char = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(char, i * fontSize, y * fontSize);
        if (y * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
      });
    };

    const interval = setInterval(draw, 45);
    const onResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener("resize", onResize);
    return () => { clearInterval(interval); window.removeEventListener("resize", onResize); };
  }, []);

  return <canvas ref={canvasRef} style={{
    position: "fixed", inset: 0, zIndex: 0, opacity: 0.18, pointerEvents: "none"
  }} />;
}

// ── Typing animation ──────────────────────────────────────────────────────────
function TypedText({ lines }: { lines: string[] }) {
  const [displayed, setDisplayed] = useState("");
  const [lineIdx, setLineIdx] = useState(0);
  const [charIdx, setCharIdx] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (done) return;
    if (lineIdx >= lines.length) { setDone(true); return; }
    const line = lines[lineIdx];
    if (charIdx < line.length) {
      const t = setTimeout(() => {
        setDisplayed(prev => prev + line[charIdx]);
        setCharIdx(c => c + 1);
      }, 28);
      return () => clearTimeout(t);
    } else {
      const t = setTimeout(() => {
        setDisplayed(prev => prev + "\n");
        setLineIdx(l => l + 1);
        setCharIdx(0);
      }, 300);
      return () => clearTimeout(t);
    }
  }, [charIdx, lineIdx, lines, done]);

  return (
    <pre style={{
      color: "#00ff41", fontSize: "11px", fontFamily: "monospace",
      margin: "0 0 24px", minHeight: "72px", opacity: 0.7,
      whiteSpace: "pre-wrap"
    }}>
      {displayed}<span style={{ animation: "blink 1s step-end infinite" }}>█</span>
    </pre>
  );
}

// ── Main Auth Page ─────────────────────────────────────────────────────────────
export default function AuthPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [form, setForm] = useState({ pseudo: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [shake, setShake] = useState(false);

  const terminalLines = mode === "login"
    ? ["> Système H4CKR initialisé...", "> Authentification requise.", "> Entrez vos identifiants pour accéder au réseau."]
    : ["> Création de compte hacker...", "> Choisissez votre pseudonyme.", "> Bienvenue dans la matrice."];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); setSuccess(""); setLoading(true);
    try {
      if (mode === "login") {
        await login(form.email, form.password);
        setSuccess("Accès accordé. Redirection...");
      } else {
        await register(form.pseudo, form.email, form.password);
        setSuccess("Compte créé. Connexion en cours...");
      }
    } catch (err: any) {
      setError(typeof err?.detail === "string" ? err.detail : "Erreur de connexion");
      setShake(true);
      setTimeout(() => setShake(false), 600);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body { background: #000; color: #e0ffe0; font-family: 'Share Tech Mono', monospace; }

        .auth-root {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
          background: #000;
          overflow: hidden;
        }

        .auth-scanlines {
          position: fixed; inset: 0; z-index: 1; pointer-events: none;
          background: repeating-linear-gradient(
            0deg, transparent, transparent 2px,
            rgba(0,255,65,0.015) 2px, rgba(0,255,65,0.015) 4px
          );
        }

        .auth-vignette {
          position: fixed; inset: 0; z-index: 1; pointer-events: none;
          background: radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.85) 100%);
        }

        .auth-card {
          position: relative; z-index: 10;
          width: 420px;
          background: rgba(0, 12, 0, 0.92);
          border: 1px solid rgba(0,255,65,0.3);
          border-radius: 4px;
          padding: 40px;
          box-shadow:
            0 0 30px rgba(0,255,65,0.08),
            0 0 60px rgba(0,255,65,0.04),
            inset 0 0 30px rgba(0,255,65,0.03);
          animation: fadeIn 0.6s ease forwards;
        }

        .auth-card.shake {
          animation: shake 0.5s ease;
        }

        .auth-corner {
          position: absolute;
          width: 12px; height: 12px;
          border-color: #00ff41;
          border-style: solid;
        }
        .auth-corner.tl { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
        .auth-corner.tr { top: -1px; right: -1px; border-width: 2px 2px 0 0; }
        .auth-corner.bl { bottom: -1px; left: -1px; border-width: 0 0 2px 2px; }
        .auth-corner.br { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

        .glitch-wrap {
          position: relative;
          display: inline-block;
          margin-bottom: 8px;
        }
        .glitch-main {
          font-family: 'Orbitron', sans-serif;
          font-size: 36px;
          font-weight: 900;
          color: #00ff41;
          letter-spacing: 6px;
          text-shadow: 0 0 20px rgba(0,255,65,0.5);
        }
        .glitch-clone1, .glitch-clone2 {
          font-family: 'Orbitron', sans-serif;
          font-size: 36px;
          font-weight: 900;
          letter-spacing: 6px;
          position: absolute; inset: 0;
          animation: glitch1 4s infinite steps(1);
          overflow: hidden;
        }
        .glitch-clone1 { color: #ff0040; clip-path: polygon(0 30%, 100% 30%, 100% 50%, 0 50%); }
        .glitch-clone2 { color: #00e5ff; clip-path: polygon(0 60%, 100% 60%, 100% 80%, 0 80%); }

        .auth-subtitle {
          color: rgba(0,255,65,0.5);
          font-size: 11px;
          letter-spacing: 4px;
          margin-bottom: 28px;
        }

        .auth-tabs {
          display: flex;
          margin-bottom: 24px;
          border-bottom: 1px solid rgba(0,255,65,0.2);
        }
        .auth-tab {
          flex: 1;
          background: none;
          border: none;
          color: rgba(0,255,65,0.4);
          font-family: 'Share Tech Mono', monospace;
          font-size: 12px;
          letter-spacing: 2px;
          padding: 10px;
          cursor: pointer;
          text-transform: uppercase;
          transition: all 0.2s;
          position: relative;
        }
        .auth-tab.active {
          color: #00ff41;
        }
        .auth-tab.active::after {
          content: '';
          position: absolute;
          bottom: -1px; left: 0; right: 0;
          height: 2px;
          background: #00ff41;
          box-shadow: 0 0 8px #00ff41;
        }
        .auth-tab:hover { color: #00ff41; }

        .auth-field {
          position: relative;
          margin-bottom: 16px;
        }
        .auth-label {
          display: block;
          font-size: 10px;
          letter-spacing: 2px;
          color: rgba(0,255,65,0.5);
          margin-bottom: 6px;
          text-transform: uppercase;
        }
        .auth-input {
          width: 100%;
          background: rgba(0,255,65,0.04);
          border: 1px solid rgba(0,255,65,0.2);
          border-radius: 2px;
          padding: 10px 14px;
          color: #00ff41;
          font-family: 'Share Tech Mono', monospace;
          font-size: 14px;
          outline: none;
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        .auth-input::placeholder { color: rgba(0,255,65,0.2); }
        .auth-input:focus {
          border-color: #00ff41;
          box-shadow: 0 0 12px rgba(0,255,65,0.15), inset 0 0 8px rgba(0,255,65,0.05);
        }

        .auth-btn {
          width: 100%;
          margin-top: 8px;
          padding: 14px;
          background: transparent;
          border: 1px solid #00ff41;
          color: #00ff41;
          font-family: 'Orbitron', sans-serif;
          font-size: 13px;
          font-weight: 700;
          letter-spacing: 4px;
          text-transform: uppercase;
          cursor: pointer;
          position: relative;
          overflow: hidden;
          transition: all 0.3s;
        }
        .auth-btn::before {
          content: '';
          position: absolute;
          inset: 0;
          background: #00ff41;
          transform: translateX(-100%);
          transition: transform 0.3s ease;
          z-index: -1;
        }
        .auth-btn:hover::before { transform: translateX(0); }
        .auth-btn:hover { color: #000; box-shadow: 0 0 20px rgba(0,255,65,0.4); }
        .auth-btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .auth-btn:disabled::before { transform: none; }

        .auth-btn-loading {
          display: inline-flex; align-items: center; gap: 8px;
        }
        .auth-spinner {
          width: 14px; height: 14px;
          border: 2px solid rgba(0,255,65,0.3);
          border-top-color: currentColor;
          border-radius: 50%;
          animation: spin 0.7s linear infinite;
        }

        .auth-error {
          margin-top: 12px;
          padding: 10px 14px;
          background: rgba(255,0,64,0.1);
          border: 1px solid rgba(255,0,64,0.4);
          border-radius: 2px;
          color: #ff4060;
          font-size: 12px;
          animation: fadeIn 0.3s ease;
        }
        .auth-success {
          margin-top: 12px;
          padding: 10px 14px;
          background: rgba(0,255,65,0.08);
          border: 1px solid rgba(0,255,65,0.4);
          border-radius: 2px;
          color: #00ff41;
          font-size: 12px;
          animation: fadeIn 0.3s ease;
        }

        .auth-oauth {
          margin-top: 24px;
          padding-top: 20px;
          border-top: 1px solid rgba(0,255,65,0.1);
        }
        .auth-oauth-label {
          text-align: center;
          font-size: 10px;
          letter-spacing: 2px;
          color: rgba(0,255,65,0.3);
          margin-bottom: 12px;
        }
        .auth-oauth-btns { display: flex; gap: 10px; }
        .auth-oauth-btn {
          flex: 1;
          padding: 10px;
          background: rgba(0,255,65,0.04);
          border: 1px solid rgba(0,255,65,0.15);
          color: rgba(0,255,65,0.6);
          font-family: 'Share Tech Mono', monospace;
          font-size: 11px;
          letter-spacing: 1px;
          cursor: pointer;
          transition: all 0.2s;
          border-radius: 2px;
        }
        .auth-oauth-btn:hover {
          border-color: rgba(0,255,65,0.4);
          color: #00ff41;
          background: rgba(0,255,65,0.08);
        }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
        @keyframes shake {
          0%,100% { transform: translateX(0); }
          20% { transform: translateX(-8px); }
          40% { transform: translateX(8px); }
          60% { transform: translateX(-5px); }
          80% { transform: translateX(5px); }
        }
        @keyframes glitch1 {
          0%,90%,100% { transform: translate(0); opacity: 0; }
          92% { transform: translate(-3px, 1px); opacity: 1; }
          94% { transform: translate(3px, -1px); opacity: 1; }
          96% { transform: translate(0); opacity: 0; }
        }
      `}</style>

      <div className="auth-root">
        <MatrixRain />
        <div className="auth-scanlines" />
        <div className="auth-vignette" />

        <div className={`auth-card ${shake ? "shake" : ""}`}>
          <div className="auth-corner tl" />
          <div className="auth-corner tr" />
          <div className="auth-corner bl" />
          <div className="auth-corner br" />

          <GlitchTitle text="H4CKR" />
          <div className="auth-subtitle">ESCAPE GAME // CYBERSÉCURITÉ</div>

          <TypedText key={mode} lines={terminalLines} />

          <div className="auth-tabs">
            <button
              className={`auth-tab ${mode === "login" ? "active" : ""}`}
              onClick={() => { setMode("login"); setError(""); setSuccess(""); }}
            >
              &gt; Connexion
            </button>
            <button
              className={`auth-tab ${mode === "register" ? "active" : ""}`}
              onClick={() => { setMode("register"); setError(""); setSuccess(""); }}
            >
              &gt; Inscription
            </button>
          </div>

          <form onSubmit={handleSubmit} style={{ animation: "fadeIn 0.3s ease" }} key={mode}>
            {mode === "register" && (
              <div className="auth-field">
                <label className="auth-label">Pseudonyme</label>
                <input
                  className="auth-input"
                  type="text"
                  placeholder="votre_pseudo_hacker"
                  value={form.pseudo}
                  onChange={e => setForm(f => ({ ...f, pseudo: e.target.value }))}
                  required minLength={3} maxLength={50}
                  autoComplete="username"
                />
              </div>
            )}

            <div className="auth-field">
              <label className="auth-label">Email</label>
              <input
                className="auth-input"
                type="email"
                placeholder="hacker@matrix.net"
                value={form.email}
                onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                required
                autoComplete="email"
              />
            </div>

            <div className="auth-field">
              <label className="auth-label">Mot de passe</label>
              <input
                className="auth-input"
                type="password"
                placeholder="••••••••"
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                required minLength={8}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
              />
            </div>

            <button className="auth-btn" type="submit" disabled={loading}>
              {loading ? (
                <span className="auth-btn-loading">
                  <span className="auth-spinner" />
                  Authentification...
                </span>
              ) : mode === "login" ? "> ACCÉDER AU RÉSEAU" : "> CRÉER LE COMPTE"}
            </button>

            {error && <div className="auth-error">⚠ {error}</div>}
            {success && <div className="auth-success">✓ {success}</div>}
          </form>

          <div className="auth-oauth">
            <div className="auth-oauth-label">── OU SE CONNECTER VIA ──</div>
            <div className="auth-oauth-btns">
              <a className="auth-oauth-btn" href={authApi.googleUrl()}>
                ⬡ Google
              </a>
              <a className="auth-oauth-btn" href={authApi.twitterUrl()}>
                ✕ Twitter/X
              </a>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
