import { AuthProvider, useAuth } from "./hooks/useAuth";
import AuthPage from "./pages/AuthPage";
import GamePage from "./pages/GamePage";
import AdminPage from "./pages/AdminPage";

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ minHeight:"100vh", display:"flex", alignItems:"center", justifyContent:"center", background:"#000" }}>
        <div style={{ fontFamily:"Orbitron, sans-serif", color:"#00ff41", fontSize:14, letterSpacing:4, animation:"pulse 1.5s ease infinite" }}>
          INITIALISATION...
        </div>
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
          @keyframes pulse { 0%,100% { opacity: 0.4; } 50% { opacity: 1; } }
        `}</style>
      </div>
    );
  }

  if (!user) return <AuthPage />;

  // ← Si admin ET URL contient /admin → AdminPage
  if (user.is_admin && window.location.pathname === "/admin") return <AdminPage />;

  return <GamePage />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}