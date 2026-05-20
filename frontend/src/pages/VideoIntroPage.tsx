import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function VideoIntroPage() {
  const navigate = useNavigate();

  const onVideoEnd = () => {
    navigate("/game"); // redirection vers GamePage
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
        src="/video/intro.mp4"   // <<< mets ta vidéo ici
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
