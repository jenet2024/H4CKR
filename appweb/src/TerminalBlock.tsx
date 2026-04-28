import { useState, useEffect } from "react";
import type { Translation } from "./config/translations";
import styles from "./TerminalBlock.module.css";

interface Props {
  lines: Translation["terminal_lines"];
}

export default function TerminalBlock({ lines }: Props) {
  const [visible, setVisible] = useState(0);

  useEffect(() => {
    setVisible(0);
    const timers = lines.map((_, i) =>
      setTimeout(() => setVisible(i + 1), 400 + i * 520)
    );
    return () => timers.forEach(clearTimeout);
  }, [lines]);

  return (
    <div className={styles.terminal}>
      <div className={styles.titleBar}>
        <span className={`${styles.dot} ${styles.red}`} />
        <span className={`${styles.dot} ${styles.yellow}`} />
        <span className={`${styles.dot} ${styles.green}`} />
        <span className={styles.titleText}>H4CHR — terminal v2.1</span>
      </div>
      <div className={styles.body}>
        {lines.slice(0, visible).map((line, i) => (
          <div key={i} className={styles.line}>
            {line.type === "cmd" && <span className={styles.prompt}>$</span>}
            <span
              className={`${styles.text} ${styles[line.type]}`}
              style={line.type !== "cmd" ? { paddingLeft: 20 } : {}}
            >
              {line.text}
            </span>
          </div>
        ))}
        {visible <= lines.length && (
          <div className={styles.line}>
            <span className={styles.prompt}>$</span>
            <span className={styles.cursor} />
          </div>
        )}
      </div>
      <div className={styles.protocols}>
        {["SSH", "FTP", "HTTP", "SQL", "DNS", "VPN"].map((proto, i) => (
          <span key={proto} className={`${styles.proto} ${i % 2 === 0 ? styles.protoActive : ""}`}>
            {proto}
          </span>
        ))}
      </div>
    </div>
  );
}