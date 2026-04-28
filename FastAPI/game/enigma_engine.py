"""
Moteur de validation des énigmes.
Chaque type d'énigme a sa propre logique de vérification.
"""
import base64
import hashlib
from passlib.context import CryptContext
from models.level import Enigma

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def normalize(s: str) -> str:
    """Normalise une réponse : minuscules, strip, sans espaces multiples."""
    return " ".join(s.strip().lower().split())


def check_answer(enigma: Enigma, user_answer: str) -> bool:
    """
    Vérifie la réponse d'un joueur.
    La réponse correcte est stockée sous forme de hash bcrypt dans enigma.answer_hash.
    On compare le hash de la réponse normalisée.
    """
    normalized = normalize(user_answer)
    return pwd_context.verify(normalized, enigma.answer_hash)


def get_hint(enigma: Enigma, hints_used: int) -> str | None:
    """Retourne l'indice suivant disponible."""
    hints = [enigma.hint1, enigma.hint2, enigma.hint3]
    available = [h for h in hints if h]
    if hints_used < len(available):
        return available[hints_used]
    return None


def hash_answer(answer: str) -> str:
    """Hash une réponse pour la stocker en base (à utiliser dans le seeder)."""
    return pwd_context.hash(normalize(answer))


# ── Helpers pour le terminal (niveau expert) ──────────────────────────────────

TERMINAL_COMMANDS = {
    "help": (
        "Commandes disponibles :\n"
        "  scan <target>          — Scanne les ports d'une cible\n"
        "  decode <text>          — Décode du Base64\n"
        "  caesar <text> <shift>  — Décode un chiffre de César\n"
        "  extract <file>         — Extrait les métadonnées d'un fichier\n"
        "  connect <host> <port>  — Tente une connexion\n"
        "  ls                     — Liste les fichiers disponibles\n"
        "  cat <file>             — Affiche le contenu d'un fichier\n"
        "  clear                  — Efface le terminal\n"
        "  hint                   — Affiche un indice (-10 pts)\n"
    ),
    "ls": (
        "total 4\n"
        "drwxr-xr-x  mission_files/\n"
        "-rw-r--r--  readme.txt\n"
        "-rw-r--r--  suspect.png\n"
        "-rw-r--r--  logs_serveur.txt\n"
        "-rw-r--r--  message_chiffre.b64\n"
    ),
    "cat readme.txt": (
        "=== MISSION EXPERT ===\n"
        "Agent, vous avez accès au système.\n"
        "Votre objectif : trouver le mot de passe caché dans les fichiers.\n"
        "Commencez par analyser les logs et les fichiers suspects.\n"
        "Bonne chance.\n"
        ">> ALERTE : Vous avez 30 minutes avant la déconnexion automatique.\n"
    ),
    "cat logs_serveur.txt": (
        "[2024-01-15 03:42:11] WARN  — Tentative connexion échouée : user=admin\n"
        "[2024-01-15 03:42:45] WARN  — Tentative connexion échouée : user=root\n"
        "[2024-01-15 03:43:02] INFO  — Connexion réussie : user=s3cur1ty_t3am\n"
        "[2024-01-15 03:43:15] INFO  — Accès fichier : /var/secret/vault.key\n"
        "[2024-01-15 03:44:00] WARN  — Fichier modifié : /etc/passwd\n"
        "[2024-01-15 03:44:30] ERROR — Intrusion détectée — IP: 192.168.42.13\n"
        "...\n"
        "[ Indice : le nom d'utilisateur qui a réussi à se connecter est la clé ]\n"
    ),
    "cat message_chiffre.b64": (
        "SGVsbG8gQWdlbnQsIGxlIG1vdCBkZSBwYXNzZSBlc3QgOiBIQUNLRVIyMDI1\n"
    ),
}


def process_terminal_command(command: str) -> tuple[str, bool, int]:
    """
    Traite une commande terminal.
    Retourne : (output, success, points_earned)
    """
    cmd = command.strip().lower()

    # Commandes statiques
    if cmd in TERMINAL_COMMANDS:
        return TERMINAL_COMMANDS[cmd], False, 0

    # decode base64
    if cmd.startswith("decode "):
        text = command[7:].strip()
        try:
            decoded = base64.b64decode(text).decode("utf-8")
            return f"Décodé : {decoded}", False, 0
        except Exception:
            return "Erreur : texte Base64 invalide.", False, 0

    # caesar cipher
    if cmd.startswith("caesar "):
        parts = command.split()
        if len(parts) >= 3:
            try:
                shift = int(parts[-1])
                text = " ".join(parts[1:-1])
                decoded = "".join(
                    chr((ord(c) - 65 - shift) % 26 + 65) if c.isupper()
                    else chr((ord(c) - 97 - shift) % 26 + 97) if c.islower()
                    else c
                    for c in text
                )
                return f"Déchiffré (César -{shift}) : {decoded}", False, 0
            except ValueError:
                return "Usage : caesar <texte> <décalage>", False, 0

    # scan
    if cmd.startswith("scan "):
        target = command[5:].strip()
        return (
            f"Scan de {target}...\n"
            f"PORT    STATE  SERVICE\n"
            f"22/tcp  open   ssh\n"
            f"80/tcp  open   http\n"
            f"443/tcp open   https\n"
            f"3306/tcp closed mysql\n"
            f"\nScan terminé. 3 ports ouverts détectés.\n"
            f"[ Indice : le port SSH utilise une clé non standard ]",
            False, 0,
        )

    # connect
    if cmd.startswith("connect "):
        parts = command.split()
        if len(parts) >= 3:
            host, port = parts[1], parts[2]
            return (
                f"Connexion à {host}:{port}...\n"
                f"Authentification requise.\n"
                f"login: _\n"
                f"[ Utilisez la commande avec les credentials trouvés ]",
                False, 0,
            )

    # extract metadata
    if cmd.startswith("extract "):
        filename = command[8:].strip()
        return (
            f"Extraction des métadonnées de {filename}...\n"
            f"Author     : Unknown\n"
            f"Created    : 2024-01-15 03:41:00\n"
            f"Comment    : p4ssw0rd_h1dd3n_h3r3\n"
            f"GPS        : 48.8566° N, 2.3522° E\n"
            f"Software   : GIMP 2.10\n"
            f"[ Indice : les métadonnées contiennent un commentaire suspect ]",
            False, 0,
        )

    # clear
    if cmd == "clear":
        return "__CLEAR__", False, 0

    # commande inconnue
    return f"Commande inconnue : '{command}'. Tapez 'help' pour la liste des commandes.", False, 0
