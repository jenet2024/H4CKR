// Centralise tous les appels API vers le backend FastAPI
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// ── Auth token helpers ────────────────────────────────────────────────────────
export function getToken(): string | null {
  return localStorage.getItem("access_token");
}
export function setTokens(access: string, refresh: string) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}
export function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

// ── Base fetch ────────────────────────────────────────────────────────────────
async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  withAuth = true
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (withAuth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  // Token expiré → tente un refresh automatique
  if (res.status === 401 && withAuth) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${getToken()}`;
      const retry = await fetch(`${API_URL}${path}`, { ...options, headers });
      if (!retry.ok) throw await retry.json();
      return retry.json() as Promise<T>;
    } else {
      clearTokens();
      window.location.href = "/";
    }
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Erreur réseau" }));
    throw err;
  }

  return res.json() as Promise<T>;
}

async function tryRefresh(): Promise<boolean> {
  const refresh = localStorage.getItem("refresh_token");
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export interface UserOut {
  id: number;
  pseudo: string;
  email: string;
  avatar_url?: string;
  is_admin: boolean;
  auth_provider: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserOut;
}

export const authApi = {
  register: (pseudo: string, email: string, password: string) =>
    apiFetch<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ pseudo, email, password }),
    }, false),

  login: (email: string, password: string) =>
    apiFetch<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }, false),

  me: () => apiFetch<UserOut>("/auth/me"),

  googleUrl: () => `${API_URL}/auth/google`,
  twitterUrl: () => `${API_URL}/auth/twitter`,
};

// ── Game types ────────────────────────────────────────────────────────────────
export interface EnigmaOut {
  id: number;
  slug: string;
  title: string;
  description: string;
  type: string;
  file_path?: string;
  points: number;
  order: number;
  solved: boolean;
  hints_used: number;
}

export interface LevelOut {
  id: number;
  slug: string;
  name: string;
  description: string;
  order: number;
  video_file?: string;
  max_points: number;
  enigmas: EnigmaOut[];
}

export interface AnswerResponse {
  correct: boolean;
  message: string;
  points_earned: number;
  hint?: string;
  badge_earned?: BadgeOut;
}

export interface BadgeOut {
  id: number;
  slug: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  points_reward: number;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  pseudo: string;
  avatar_url?: string;
  total_points: number;
  badges_count: number;
  level_reached: string;
}

export interface CertificateOut {
  id: number;
  level: string;
  score: number;
  issued_at: string;
  unique_code: string;
  pdf_path?: string;
}

export interface TerminalResponse {
  output: string;
  success: boolean;
  points_earned: number;
}

// ── Game API ──────────────────────────────────────────────────────────────────
export const gameApi = {
  getLevels: () => apiFetch<LevelOut[]>("/game/levels"),
  getLevel: (slug: string) => apiFetch<LevelOut>(`/game/levels/${slug}`),

  submitAnswer: (enigma_id: number, answer: string) =>
    apiFetch<AnswerResponse>("/game/answer", {
      method: "POST",
      body: JSON.stringify({ enigma_id, answer }),
    }),

  requestHint: (enigma_id: number) =>
    apiFetch<{ hint: string; message: string }>(`/game/hint/${enigma_id}`, {
      method: "POST",
    }),

  terminal: (command: string, enigma_id?: number) =>
    apiFetch<TerminalResponse>("/game/terminal", {
      method: "POST",
      body: JSON.stringify({ command, enigma_id }),
    }),

  leaderboard: () => apiFetch<LeaderboardEntry[]>("/game/leaderboard"),

  myBadges: () => apiFetch<BadgeOut[]>("/game/my-badges"),
  allBadges: () => apiFetch<BadgeOut[]>("/game/badges"),

  generateCertificate: (level_slug: string) =>
    apiFetch<CertificateOut>(`/game/certificate/${level_slug}`, { method: "POST" }),

  downloadCertificate: (unique_code: string) =>
    `${API_URL}/game/certificate/download/${unique_code}?token=${getToken()}`,

  contact: (subject: string, message: string, category: string) =>
    apiFetch("/game/contact", {
      method: "POST",
      body: JSON.stringify({ subject, message, category }),
    }),
};
