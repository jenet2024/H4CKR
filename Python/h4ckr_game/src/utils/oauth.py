"""
Serveur HTTP local pour capturer les callbacks OAuth.
Ouvre le navigateur → l'utilisateur se connecte → callback reçu → token JWT récupéré.
"""
import threading
import webbrowser
import urllib.parse
import http.server
import requests
from config import (
    API_BASE_URL,
    GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URI,
    TWITTER_CLIENT_ID, TWITTER_REDIRECT_URI,
)

_callback_result = {"code": None, "provider": None, "done": False}


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            _callback_result["code"] = params["code"][0]
            _callback_result["done"] = True
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
            <html><body style="background:#060b06;color:#39ff14;
                               font-family:monospace;text-align:center;padding:60px">
            <h1>H4CKR</h1>
            <p>Authentification r&#233;ussie !</p>
            <p>Vous pouvez fermer cet onglet et retourner dans le jeu.</p>
            </body></html>""")
        else:
            _callback_result["done"] = True
            self.send_response(400)
            self.end_headers()

    def log_message(self, *args):
        pass   # silence les logs HTTP


def _run_server(port=8765):
    server = http.server.HTTPServer(("localhost", port), _CallbackHandler)
    server.handle_request()   # attend une seule requête


def oauth_login_google():
    """Ouvre Google OAuth dans le navigateur et attend le code."""
    if GOOGLE_CLIENT_ID == "YOUR_GOOGLE_CLIENT_ID":
        return None, "Google OAuth non configuré. Ajoutez GOOGLE_CLIENT_ID dans .env"

    _callback_result.update({"code": None, "done": False, "provider": "google"})
    t = threading.Thread(target=_run_server, daemon=True)
    t.start()

    params = urllib.parse.urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": "google_auth",
    })
    webbrowser.open(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")

    # Attend le callback (timeout 120s)
    import time
    for _ in range(240):
        if _callback_result["done"]:
            break
        time.sleep(0.5)

    code = _callback_result.get("code")
    if not code:
        return None, "Authentification annulée ou expirée."

    # Échange le code via l'API backend
    try:
        r = requests.get(f"{API_BASE_URL}/auth/google/callback?code={code}", timeout=10)
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Erreur serveur")
    except Exception as e:
        return None, str(e)


def oauth_login_twitter():
    """Ouvre Twitter/X OAuth dans le navigateur et attend le code."""
    if TWITTER_CLIENT_ID == "YOUR_TWITTER_CLIENT_ID":
        return None, "Twitter OAuth non configuré. Ajoutez TWITTER_CLIENT_ID dans .env"

    _callback_result.update({"code": None, "done": False, "provider": "twitter"})
    t = threading.Thread(target=_run_server, daemon=True)
    t.start()

    params = urllib.parse.urlencode({
        "client_id": TWITTER_CLIENT_ID,
        "redirect_uri": TWITTER_REDIRECT_URI,
        "response_type": "code",
        "scope": "tweet.read users.read offline.access",
        "code_challenge": "challenge",
        "code_challenge_method": "plain",
        "state": "twitter_auth",
    })
    webbrowser.open(f"https://twitter.com/i/oauth2/authorize?{params}")

    import time
    for _ in range(240):
        if _callback_result["done"]:
            break
        time.sleep(0.5)

    code = _callback_result.get("code")
    if not code:
        return None, "Authentification annulée ou expirée."

    try:
        r = requests.get(f"{API_BASE_URL}/auth/twitter/callback?code={code}", timeout=10)
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Erreur serveur")
    except Exception as e:
        return None, str(e)
