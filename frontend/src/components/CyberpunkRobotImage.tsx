import React from "react";

type Theme = "dark" | "light";

export default function CyberpunkRobotImage({
  src,
  theme = "dark",
  size = 380,
  animate = true,
}: {
  src: string;
  theme?: Theme;
  size?: number;
  animate?: boolean;
}) {
  const glow = "rgba(120, 0, 30, 0.55)";
  const glowSoft = "rgba(120, 0, 30, 0.25)";
  const shadow = "rgba(90, 0, 20, 0.55)";

  return (
    <div
      style={{
        width: size,
        height: size * 1.35,
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        filter: `drop-shadow(0 0 22px ${glow})`,
        animation: animate ? "robotFloat 4s ease-in-out infinite" : "none",
        margin: "0 auto",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: 20,
          background: glowSoft,
          filter: "blur(35px)",
          animation: "glowPulse 4s ease-in-out infinite",
        }}
      />

      <img
        src={src}
        alt="Cyber Robot"
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          zIndex: 2,
          userSelect: "none",
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          position: "absolute",
          bottom: -12,
          width: "70%",
          height: 28,
          background: shadow,
          filter: "blur(18px)",
          borderRadius: "50%",
          animation: animate ? "shadowPulse 3s ease-in-out infinite" : "none",
        }}
      />

      <style>
        {`
          @keyframes robotFloat {
            0%, 100% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-12px) scale(1.02); }
          }

          @keyframes glowPulse {
            0%, 100% { opacity: 0.55; }
            50% { opacity: 1; }
          }

          @keyframes shadowPulse {
            0%, 100% { transform: scale(1); opacity: 0.45; }
            50% { transform: scale(1.25); opacity: 0.85; }
          }
        `}
      </style>
    </div>
  );
}
