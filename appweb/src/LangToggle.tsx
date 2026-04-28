import type { Lang } from "./config/translations";
import styles from "./LangToggle.module.css";

interface Props {
  lang: Lang;
  setLang: (l: Lang) => void;
}

export default function LangToggle({ lang, setLang }: Props) {
  return (
    <div className={styles.wrapper}>
      {(["fr", "en"] as Lang[]).map((l) => (
        <button
          key={l}
          className={`${styles.btn} ${lang === l ? styles.active : ""}`}
          onClick={() => setLang(l)}
        >
          {l.toUpperCase()}
        </button>
      ))}
    </div>
  );
}