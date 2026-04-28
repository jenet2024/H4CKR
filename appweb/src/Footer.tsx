import type { Translation } from "./config/translations";
import styles from "./Footer.module.css";

interface Props {
  t: Translation;
}

export default function Footer({ t }: Props) {
  return (
    <footer className={styles.footer}>
      <span className={styles.copy}>{t.footer}</span>
      <div className={styles.badges}>
        {["WINDOWS", "64-BIT", "FREE"].map((b) => (
          <span key={b} className={styles.badge}>{b}</span>
        ))}
      </div>
    </footer>
  );
}