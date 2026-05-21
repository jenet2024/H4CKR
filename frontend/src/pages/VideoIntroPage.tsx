import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function VideoIntroPage() {
  const navigate = useNavigate();

  const onVideoEnd = () => {
    navigate("/intro"); // retour à la page d’intro
  };

  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        background: "black",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <video
        src="/video/intro.mp4"
        autoPlay
        controls={false}
        onEnded={onVideoEnd}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />
    </div>
  );
}
