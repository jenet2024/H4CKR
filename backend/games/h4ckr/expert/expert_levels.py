"""6 niveaux Expert — basés sur le terminal interactif."""
import base64
import hashlib
import subprocess
import math
import pygame
from client.games.h4ckr.base_level import BaseLevel
from client.games.h4ckr.expert.terminal_screen import TerminalScreen
from client.core.settings import Settings


# ─────────────────────────────────────────────────────────────────────────────────
class ExpertBaseLevel(BaseLevel):
    """Extension de BaseLevel pour les niveaux expert avec terminal."""
    POINTS_BASE = 250

    def __init__(self, screen, settings, num, title, desc, hint,
                 mission_title, mission_desc, objectives, custom_cmds=None):
        super().__init__(screen, settings, num, title, desc, hint)
        self.terminal = TerminalScreen(
            screen, settings,
            mission_title, mission_desc, objectives,
            custom_commands=custom_cmds or {}
        )

    def handle_event(self, event):
        self.terminal.handle_event(event)

    def update(self, dt):
        self.time_spent += dt
        self.terminal.update(dt)

    def draw(self):
        W, H = self.screen.get_size()
        self.draw_background()
        self.draw_level_header(self.settings.COLOR_DANGER)
        self.terminal.draw()
        if self._solved:
            self.draw_solved_overlay()


# ─── Niveau E1 — Reconnaissance réseau ───────────────────────────────────────────
TARGET_IP_E1 = "8.8.8.8"

class LevelE01(ExpertBaseLevel):
    def __init__(self, screen, settings):
        self._validated = False
        cmds = {
            "scan": (self._scan, "scan <ip> — analyse la cible"),
            "identify": (self._identify, "identify <ip> — identifie si c'est la cible"),
        }
        super().__init__(screen, settings, 1,
            "🌐 Reconnaissance",
            "Utilisez les outils réseau pour identifier l'IP cible.",
            hint_text="Essayez 'nslookup dns.google' pour trouver l'IP de Google DNS.\nPuis 'identify 8.8.8.8' pour valider.",
            mission_title="Operation Ghost Ping",
            mission_desc="Nos capteurs détectent un signal non identifié. Résolvez l'adresse IP du serveur DNS public de Google.",
            objectives=["Résoudre dns.google → IP", "Identifier l'IP cible avec identify"],
            custom_cmds=cmds)

    def _scan(self, args):
        ip = args[0] if args else "?"
        return [f"[SCAN] Analyse de {ip}...", f"[SCAN] Host actif : {ip}", f"[SCAN] Ports ouverts : 53/udp (DNS)"]

    def _identify(self, args):
        if args and args[0] == TARGET_IP_E1:
            self.terminal.history.append("[SUCCESS] ✓ Cible identifiée ! Mission accomplie.")
            self._solved = True
            return [f"[SUCCESS] {args[0]} = Google DNS Public. CIBLE CONFIRMÉE !"]
        return [f"[INFO] {args[0] if args else '?'} n'est pas la cible. Continuez les recherches."]


# ─── Niveau E2 — Analyse de logs ─────────────────────────────────────────────────
FAKE_LOG = [
    "2024-01-15 08:23:11 INFO  User admin logged in from 192.168.1.10",
    "2024-01-15 08:24:05 INFO  File /etc/passwd accessed",
    "2024-01-15 08:24:07 ERROR Failed login attempt from 10.0.0.99",
    "2024-01-15 08:24:08 ERROR Failed login attempt from 10.0.0.99",
    "2024-01-15 08:24:09 ERROR Failed login attempt from 10.0.0.99",
    "2024-01-15 08:24:10 WARN  Brute-force detected from 10.0.0.99",
    "2024-01-15 08:25:01 INFO  Service nginx started",
    "2024-01-15 08:26:44 ERROR SQL injection attempt detected: ' OR 1=1",
    "2024-01-15 08:27:00 INFO  Backup completed successfully",
]
ATTACK_IP = "10.0.0.99"

class LevelE02(ExpertBaseLevel):
    def __init__(self, screen, settings):
        cmds = {
            "showlog": (self._showlog, "showlog — affiche les logs système"),
            "grep": (self._grep, "grep <pattern> — filtre les logs"),
            "report": (self._report, "report <ip> — signale une IP suspecte"),
        }
        super().__init__(screen, settings, 2,
            "🔍 Analyse de Logs",
            "Analysez les logs système et identifiez l'attaquant.",
            hint_text="Utilisez 'showlog' puis 'grep ERROR' pour filtrer les erreurs.\nL'IP répétée dans les ERROR est l'attaquant.",
            mission_title="Log Hunter",
            mission_desc="Notre serveur a été attaqué. Les logs contiennent des traces de l'intrusion. Trouvez l'IP de l'attaquant.",
            objectives=["Afficher les logs (showlog)", "Filtrer les erreurs (grep ERROR)", "Signaler l'IP (report <ip>)"],
            custom_cmds=cmds)

    def _showlog(self, args):
        return ["[LOG] " + l for l in FAKE_LOG]

    def _grep(self, args):
        pattern = args[0].upper() if args else ""
        return ["[GREP] " + l for l in FAKE_LOG if pattern in l.upper()] or ["[GREP] Aucun résultat"]

    def _report(self, args):
        ip = args[0] if args else ""
        if ip == ATTACK_IP:
            self._solved = True
            return [f"[SUCCESS] ✓ {ip} est l'attaquant ! Brute-force + SQLi détectés. Bloqué !"]
        return [f"[INFO] {ip} ne semble pas être l'attaquant principal. Cherchez les ERRORs répétées."]


# ─── Niveau E3 — XOR / Base64 ────────────────────────────────────────────────────
SECRET_B64 = base64.b64encode(b"INFILTRATE_NOW").decode()
CORRECT_E3 = "INFILTRATE_NOW"

class LevelE03(ExpertBaseLevel):
    def __init__(self, screen, settings):
        cmds = {
            "decode64": (self._decode64, "decode64 <string> — décode une chaîne base64"),
            "submit": (self._submit, "submit <message> — soumet le message déchiffré"),
        }
        super().__init__(screen, settings, 3,
            "🔓 Déchiffrement Base64",
            "Décodez le message intercepté chiffré en Base64.",
            hint_text="Base64 encode des données binaires en texte ASCII.\n"
                      "Utilisez 'decode64 " + SECRET_B64[:20] + "...' pour décoder.",
            mission_title="Intercept & Decode",
            mission_desc=f"Message intercepté (Base64) :\n{SECRET_B64}\nDécodez-le et soumettez le texte clair.",
            objectives=["Intercepter le message encodé", f"Decoder : {SECRET_B64}", "Soumettre le texte clair"],
            custom_cmds=cmds)
        self.terminal.history.append(f"[INTERCEPT] Message : {SECRET_B64}")

    def _decode64(self, args):
        try:
            decoded = base64.b64decode(args[0]).decode("utf-8")
            return [f"[DECODED] → {decoded}"]
        except Exception:
            return ["[ERREUR] Chaîne base64 invalide"]

    def _submit(self, args):
        msg = " ".join(args).upper()
        if msg == CORRECT_E3:
            self._solved = True
            return [f"[SUCCESS] ✓ Message déchiffré : '{msg}'. Ordre confirmé !"]
        return [f"[ERREUR] '{msg}' incorrect. Vérifiez le décodage."]


# ─── Niveau E4 — SQL Injection simulée ───────────────────────────────────────────
DB_USERS = {"admin": "h4ckr_secret", "user1": "pass123", "alice": "wonderland42"}

class LevelE04(ExpertBaseLevel):
    def __init__(self, screen, settings):
        cmds = {
            "login": (self._login, "login <user> <pass> — tente une connexion"),
            "inject": (self._inject, "inject <payload> — test d'injection SQL"),
        }
        super().__init__(screen, settings, 4,
            "💉 Injection SQL",
            "Utilisez une injection SQL pour bypasser l'authentification.",
            hint_text="Essayez : inject ' OR 1=1 --\n"
                      "Cette payload court-circuite la condition WHERE du SQL.",
            mission_title="SQL Bypass Challenge",
            mission_desc="Un système d'auth vulnérable est en ligne. Bypassez la connexion sans connaître le mot de passe.",
            objectives=["Tenter login normal", "Appliquer payload SQL injection", "Accéder au compte admin"],
            custom_cmds=cmds)

    def _login(self, args):
        user = args[0] if len(args) > 0 else ""
        pwd  = args[1] if len(args) > 1 else ""
        if DB_USERS.get(user) == pwd:
            return [f"[AUTH] Connexion réussie pour '{user}'"]
        return [f"[AUTH] Erreur : identifiants incorrects pour '{user}'"]

    def _inject(self, args):
        payload = " ".join(args)
        if "' OR" in payload.upper() or "OR 1=1" in payload.upper() or "--" in payload:
            self._solved = True
            return [
                f"[SQL] Requête : SELECT * FROM users WHERE name='{payload}'",
                "[SQL] → Condition toujours vraie !",
                "[SUCCESS] ✓ BYPASS RÉUSSI ! Accès admin obtenu sans mot de passe !",
                "[DATA] admin | h4ckr_secret | role=superuser",
            ]
        return [f"[SQL] Payload '{payload}' n'a pas bypassé l'authentification. Essayez avec des guillemets !"]


# ─── Niveau E5 — Stéganographie avancée ──────────────────────────────────────────
HIDDEN_AUDIO_MSG = "OMEGA_PROTOCOL"

class LevelE05(ExpertBaseLevel):
    def __init__(self, screen, settings):
        cmds = {
            "analyze": (self._analyze, "analyze audio.wav — analyse le fichier audio"),
            "extract": (self._extract, "extract audio.wav — extrait les données cachées"),
            "submit": (self._submit, "submit <code> — soumet le code extrait"),
        }
        super().__init__(screen, settings, 5,
            "🎵 Stégano Audio",
            "Extrayez le message caché dans le fichier audio.",
            hint_text=f"Le message est encodé dans les métadonnées LSB du fichier.\n"
                      f"Utilisez 'analyze' puis 'extract' pour le révéler.",
            mission_title="Silent Signal",
            mission_desc="Un fichier audio (audio.wav) contient un message caché dans ses données binaires. Trouvez-le.",
            objectives=["Analyser le fichier audio", "Extraire les données LSB", "Soumettre le code caché"],
            custom_cmds=cmds)

    def _analyze(self, args):
        fname = args[0] if args else "audio.wav"
        return [
            f"[ANALYZE] Fichier : {fname}",
            "[ANALYZE] Format : WAV 44100Hz stereo 16bit",
            "[ANALYZE] Taille : 2.4 MB",
            "[ANALYZE] ⚠ Anomalie détectée dans les bits LSB du canal droit !",
            "[ANALYZE] Données suspectes : 14 octets non-audio détectés",
        ]

    def _extract(self, args):
        fname = args[0] if args else "audio.wav"
        return [
            f"[EXTRACT] Lecture LSB de {fname}...",
            "[EXTRACT] Bits extraits : 01001111 01001101 01000101 01000111 01000001",
            "[EXTRACT] Décodage ASCII : OMEGA_PROTOCOL",
            f"[EXTRACT] Message caché : {HIDDEN_AUDIO_MSG}",
        ]

    def _submit(self, args):
        code = " ".join(args).upper()
        if code == HIDDEN_AUDIO_MSG:
            self._solved = True
            return [f"[SUCCESS] ✓ Code '{code}' correct ! Mission Omega déverrouillée !"]
        return [f"[ERREUR] '{code}' incorrect. Extrayez et lisez le message caché."]


# ─── Niveau E6 — CTF Boss ─────────────────────────────────────────────────────────
E6_STEPS = set()
E6_HASH_SECRET = hashlib.sha256(b"ELITE_HACKER").hexdigest()[:16]

class LevelE06(ExpertBaseLevel):
    def __init__(self, screen, settings):
        self._steps_done = set()
        cmds = {
            "crack": (self._crack, "crack <hash> — tente de cracker un hash"),
            "pivot": (self._pivot, "pivot <ip> — pivote vers un autre réseau"),
            "exfil": (self._exfil, "exfil <file> — exfiltre un fichier"),
            "submit": (self._submit, "submit <flag> — soumet le flag final"),
        }
        super().__init__(screen, settings, 6,
            "⚡ CTF BOSS — Multi-étapes",
            "Combine toutes tes compétences pour accéder au serveur final.",
            hint_text="Étape 1 : crack le hash\nÉtape 2 : pivot vers 10.10.10.1\n"
                      "Étape 3 : exfil flag.txt\nÉtape 4 : submit le flag",
            mission_title="FINAL BOSS — Operation ELITE",
            mission_desc=f"Hash cible : {E6_HASH_SECRET}\n3 serveurs à pirater en cascade.\nFlag final dans flag.txt.",
            objectives=["Crack le hash (crack)", "Pivot réseau (pivot 10.10.10.1)", "Exfiltrer flag.txt (exfil flag.txt)", "Soumettre le flag"],
            custom_cmds=cmds)
        self.terminal.history.append(f"[INTEL] Hash intercepté : {E6_HASH_SECRET}")

    def _crack(self, args):
        h = args[0] if args else ""
        if h == E6_HASH_SECRET:
            self._steps_done.add("crack")
            return ["[CRACK] Attaque dictionnaire...", "[CRACK] Match trouvé !", "[SUCCESS] Password : ELITE_HACKER"]
        return ["[CRACK] Hash non reconnu. Utilisez le hash intercepté."]

    def _pivot(self, args):
        ip = args[0] if args else ""
        if "crack" in self._steps_done and ip == "10.10.10.1":
            self._steps_done.add("pivot")
            return ["[PIVOT] Tunnel établi vers 10.10.10.1", "[PIVOT] Accès réseau interne : OK", "[INFO] Fichiers détectés : flag.txt, passwords.db"]
        if "crack" not in self._steps_done:
            return ["[ERREUR] Credentials nécessaires. Crackez d'abord le hash !"]
        return [f"[ERREUR] IP invalide ou non accessible : {ip}"]

    def _exfil(self, args):
        fname = args[0] if args else ""
        if "pivot" in self._steps_done and fname == "flag.txt":
            self._steps_done.add("exfil")
            return ["[EXFIL] Transfert sécurisé...", "[EXFIL] flag.txt reçu (24 bytes)", "[DATA] CTF{ELITE_H4CKER_PWNED}"]
        if "pivot" not in self._steps_done:
            return ["[ERREUR] Pivotez d'abord vers le réseau cible !"]
        return [f"[ERREUR] Fichier '{fname}' introuvable ou accès refusé."]

    def _submit(self, args):
        flag = " ".join(args).upper()
        if "exfil" in self._steps_done and "ELITE_H4CKER_PWNED" in flag:
            self._solved = True
            return [
                "[SUCCESS] ✓✓✓ FLAG CORRECT !",
                "[SYSTEM] ELITE HACKER CONFIRMÉ",
                "[AWARD]  Certificat Expert h4ckR débloqué !",
            ]
        return [f"[ERREUR] Flag '{flag}' incorrect. Récupérez-le avec exfil flag.txt"]
