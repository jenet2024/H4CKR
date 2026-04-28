import { useState, useEffect } from "react";
import styles from "./GlitchText.module.css";

interface Props {
  text: string;
}

export default function GlitchText({ text }: Props) {
  const [glitch, setGlitch] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setGlitch(true);
      setTimeout(() => setGlitch(false), 120);
    }, 3500);
    return () => clearInterval(interval);
  }, []);

  return (
    <span className={`${styles.title} ${glitch ? styles.glitch : ""}`}>
      {text}
    </span>
  );
}