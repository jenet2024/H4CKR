import GlitchText from "./GlitchText";
import TerminalBlock from "./TerminalBlock";
import type { Translation } from "./config/translations";
import styles from "./Hero.module.css";

interface Props {
  t: Translation;
  onDownload: () => void;
}

export default function Hero({ t, onDownload }: Props) {
  const levels = [
    { tag: t.lv1_tag, name: t.lv1_name, title: t.lv1_title, desc: t.lv1_desc, accent: false },
    { tag: t.lv2_tag, name: t.lv2_name, title: t.lv2_title, desc: t.lv2_desc, accent: true },
  ];

  const stats = [
    { val: "42+",  label: t.stat1_label },
    { val: "2",    label: t.stat2_label },
    { val: "100%", label: t.stat3_label },
  ];

  return (
    <section className={styles.section}>
      <div className={styles.grid}>

        {/* Left */}
        <div className={styles.left}>
          <span className={styles.tag}>{t.tag}</span>

          <div className={styles.titleBlock}>
            <GlitchText text="H4CKR" />
            <p className={styles.subtitle}>{t.title_sub}</p>
          </div>

          <p className={styles.desc}>{t.desc}</p>

          <div className={styles.levels}>
            {levels.map((lv) => (
              <div
                key={lv.tag}
                className={`${styles.levelCard} ${lv.accent ? styles.levelAccent : ""}`}
              >
                <div className={styles.levelTag}>
                  {lv.tag} · <span className={styles.levelName}>{lv.name}</span>
                </div>
                <div className={styles.levelTitle}>{lv.title}</div>
                <div className={styles.levelDesc}>{lv.desc}</div>
              </div>
            ))}
          </div>

          <div className={styles.stats}>
            {stats.map((s) => (
              <div key={s.label} className={styles.stat}>
                <span className={styles.statVal}>{s.val}</span>
                <span className={styles.statLabel}>{s.label}</span>
              </div>
            ))}
          </div>

          <button className={styles.dlBtn} onClick={onDownload}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 3v13M7 11l5 5 5-5" />
              <path d="M4 20h16" />
            </svg>
            {t.dl_main}
          </button>
          <p className={styles.dlSub}>{t.dl_sub}</p>
        </div>

        {/* Right */}
        <div className={styles.right}>
          <TerminalBlock lines={t.terminal_lines} />
        </div>

      </div>
    </section>
  );
}