import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { authApi, setTokens, clearTokens, getToken, type UserOut } from "../api/client";

interface AuthCtx {
  user: UserOut | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (pseudo: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Vérifie si un token existe au chargement
    clearTokens(); // <<< FORCE LA DECONNEXION AU DEMARRAGE
    if (getToken()) {
      authApi.me()
        .then(setUser)
        .catch(() => clearTokens())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const data = await authApi.login(email, password);
    setTokens(data.access_token, data.refresh_token);
    setUser(data.user);
    sessionStorage.setItem("justLoggedIn", "true");

  };

  const register = async (pseudo: string, email: string, password: string) => {
    const data = await authApi.register(pseudo, email, password);
    setTokens(data.access_token, data.refresh_token);
    setUser(data.user);
    sessionStorage.setItem("justLoggedIn", "true");

  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
