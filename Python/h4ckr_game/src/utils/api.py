"""
Client HTTP vers le backend FastAPI.
Gère l'authentification JWT et toutes les requêtes jeu.
"""
import requests
from typing import Optional, Tuple
from config import API_BASE_URL


class APIClient:
    def __init__(self):
        self.base_url  = API_BASE_URL
        self.token     = None
        self.refresh   = None
        self.user: Optional[dict] = None
        self._session  = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _h(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _post(self, path, json=None, auth=False) -> Tuple[dict, int]:
        try:
            r = self._session.post(
                f"{self.base_url}{path}",
                json=json or {},
                headers=self._h() if auth else {},
                timeout=10,
            )
            return r.json(), r.status_code
        except requests.exceptions.ConnectionError:
            return {"detail": "Serveur inaccessible — lancez le backend (voir DEMARRER.bat)"}, 0
        except requests.exceptions.Timeout:
            return {"detail": "Timeout — le serveur ne repond pas"}, 0
        except Exception as e:
            return {"detail": f"Erreur reseau : {type(e).__name__}"}, 0

    def _get(self, path, auth=True) -> Tuple[dict, int]:
        try:
            r = self._session.get(
                f"{self.base_url}{path}",
                headers=self._h() if auth else {},
                timeout=10,
            )
            return r.json(), r.status_code
        except requests.exceptions.ConnectionError:
            return {"detail": "Serveur inaccessible — lancez le backend (voir DEMARRER.bat)"}, 0
        except requests.exceptions.Timeout:
            return {"detail": "Timeout — le serveur ne repond pas"}, 0
        except Exception as e:
            return {"detail": f"Erreur reseau : {type(e).__name__}"}, 0

    def is_backend_online(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def _set(self, data: dict):
        self.token   = data.get("access_token")
        self.refresh = data.get("refresh_token")
        self.user    = data.get("user")

    # ── Auth ──────────────────────────────────────────────────────────────────

    def login(self, email: str, password: str) -> Tuple[dict, int]:
        data, code = self._post("/auth/login", {"email": email, "password": password})
        if code == 200:
            self._set(data)
        return data, code

    def register(self, pseudo: str, email: str, password: str) -> Tuple[dict, int]:
        data, code = self._post(
            "/auth/register",
            {"pseudo": pseudo, "email": email, "password": password},
        )
        if code == 201:
            self._set(data)
        return data, code

    def logout(self):
        self.token  = None
        self.refresh = None
        self.user   = None

    # ── Game ──────────────────────────────────────────────────────────────────

    def get_levels(self) -> Tuple[list, int]:
        data, code = self._get("/game/levels")
        if code == 200:
            return data, 200
        return [], code

    def submit_answer(self, enigma_id: int, answer: str) -> Tuple[dict, int]:
        return self._post("/game/answer",
                          {"enigma_id": enigma_id, "answer": answer}, auth=True)

    def get_hint(self, enigma_id: int) -> Tuple[dict, int]:
        return self._post(f"/game/hint/{enigma_id}", auth=True)

    def terminal_command(self, command: str,
                         enigma_id: int = None) -> Tuple[dict, int]:
        return self._post("/game/terminal",
                          {"command": command, "enigma_id": enigma_id}, auth=True)

    def get_leaderboard(self) -> Tuple[list, int]:
        data, code = self._get("/game/leaderboard")
        if code == 200:
            return data, 200
        return [], code

    def get_my_badges(self) -> Tuple[list, int]:
        data, code = self._get("/game/my-badges")
        if code == 200:
            return data, 200
        return [], code

    def generate_certificate(self, level_slug: str) -> Tuple[dict, int]:
        return self._post(f"/game/certificate/{level_slug}", auth=True)

    def contact(self, subject: str, message: str,
                category: str = "bug") -> Tuple[dict, int]:
        return self._post("/game/contact",
                          {"subject": subject, "message": message, "category": category},
                          auth=True)


# Singleton global partagé par tous les écrans
api = APIClient()
