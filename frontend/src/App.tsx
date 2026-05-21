import { AuthProvider, useAuth } from "./hooks/useAuth";
import AuthPage from "./pages/AuthPage";
import GamePage from "./pages/GamePage";
import { useState, useEffect } from "react";

function AppContent() {
  const { user, loading } = useAuth();

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

  // Connecté → Page NEXUS (GamePage)
  return <GamePage />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
