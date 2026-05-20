import { AuthProvider, useAuth } from "./hooks/useAuth";
import AuthPage from "./pages/AuthPage";
import GamePage from "./pages/GamePage";
import { useState, useEffect } from "react";

function AppContent() {
  const { user, loading } = useAuth();
  const [showIntro, setShowIntro] = useState(false);

  useEffect(() => {
    // Si l'utilisateur vient JUSTE de se connecter → jouer la vidéo
    if (user && sessionStorage.getItem("justLoggedIn") === "true") {
      setShowIntro(true);
    }
  }, [user]);

  if (loading) {
    return (
      <div style={{
        minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
        background: "#000",
      }}>
        <div style={{
          fontFamily: "Orbitron, sans-serif", color: "#00ff41",
          fontSize: 14, letterSpacing: 4, animation: "pulse 1.5s ease infinite",
        }}>
          INITIALISATION...
        </div>
      </div>
    );
  }

  // Pas connecté → AuthPage
  if (!user) return <AuthPage />;

  // Connecté ET vient juste de se connecter → vidéo
  if (showIntro) {
    return (
      <div style={{
        width: "100vw",
        height: "100vh",
        background: "black",
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}>
        <video
          src="/video/intro.mp4"
          autoPlay
          onEnded={() => {
            sessionStorage.setItem("justLoggedIn", "false");
            setShowIntro(false);
          }}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover"
          }}
        />
      </div>
    );
  }

  // Connecté normalement → GamePage
  return <GamePage />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
