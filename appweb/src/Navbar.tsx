import LangToggle from "./LangToggle";
import type { Lang, Translation } from "./config/translations";
import styles from "./Navbar.module.css";

interface Props {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: Translation;
  onDownload: () => void;
}

export default function Navbar({ lang, setLang, t, onDownload }: Props) {
  return (
    <nav className={styles.nav}>
      <div className={styles.logo}>
        <svg width="28" height="28" viewBox="0 0 36 36" fill="none">
          <circle cx="18" cy="18" r="17" stroke="#39ff14" strokeWidth="1.2" strokeDasharray="4 2" />
          <rect x="9" y="11" width="18" height="14" rx="2" stroke="#39ff14" strokeWidth="1.2" fill="none" />
          <line x1="9" y1="15" x2="27" y2="15" stroke="#39ff14" strokeWidth="0.8" />
          <circle cx="12" cy="13" r="0.8" fill="#39ff14" />
          <circle cx="14.5" cy="13" r="0.8" fill="#39ff14" opacity="0.5" />
          <text x="18" y="23.5" textAnchor="middle" fill="#39ff14" fontSize="7" fontFamily="monospace" fontWeight="700">&gt;_</text>
        </svg>
        <span className={styles.logoText}>H4CHR</span>
      </div>
      <div className={styles.actions}>
        <LangToggle lang={lang} setLang={setLang} />
        <button className={styles.dlBtn} onClick={onDownload}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 3v13M7 11l5 5 5-5" />
            <path d="M4 20h16" />
          </svg>
          <span>{t.nav_download}</span>
        </button>
      </div>
    </nav>
  );
}
