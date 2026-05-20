"""
Moteur principal FSM pour les modes Débutant et Expert.
Gère : intro_video → niveaux → badge (débutant) → vidéo mid → suite → certificat
"""
import threading
import sys
import pygame
from client.core.settings import Settings
from client.core.api_client import APIClient
from client.core.auth_manager import AuthManager
from client.games.h4ckr.hud import GameHUD
from client.games.h4ckr.robot_video import RobotVideoScreen
from client.games.h4ckr.badge_certificate import BadgeScreen, CertificateScreen

# ── Textes robot ──────────────────────────────────────────────────────────────────
ROBOT_INTROS = {
    "debutant": (
        "MISSION ACCES CYBER INITIATION",
        "Agent, bienvenue dans le programme h4ckR. Tu vas traverser dix épreuves de cybersécurité. "
        "Chaque niveau teste tes connaissances sur les menaces numériques. "
        "Mots de passe, phishing, chiffrement, et bien plus t'attendent. "
        "Concentration maximale. Commence quand tu es prêt.",
        "debutant"
    ),
    "expert": (
        "TRANSMISSION CHIFFRÉE — NIVEAU OMEGA",
        "Agent infiltré. Le réseau est compromis. Les systèmes tombent un à un. "
        "Tu es notre dernière ligne de défense. Six missions critiques t'attendent. "
        "Reconnaissance, analyse de logs, injection, exfiltration de données. "
        "Tu n'as pas droit à l'erreur. Le terminal est ton arme. "
        "Le temps tourne. Commence maintenant.",
        "expert"
    ),
    "badge_mid": (
        "FÉLICITATIONS — BADGE INTERMÉDIAIRE",
        "Impressionnant. Tu as surmonté les cinq premières épreuves. "
        "Tu viens d'obtenir le badge Cyber Initié. "
        "Mais la vraie menace commence maintenant. "
        "Cinq nouveaux niveaux te séparent du certificat final. "
        "Continue l'infiltration. Ne faiblis pas.",
        "badge"
    ),
    
}

# ── Import des niveaux ────────────────────────────────────────────────────────────
def _load_debutant_levels(screen, settings):
    from client.games.h4ckr.debutant.level_01 import Level01
    from client.games.h4ckr.debutant.level_02 import Level02
    from client.games.h4ckr.debutant.level_03 import Level03
    from client.games.h4ckr.debutant.level_04 import Level04
    from client.games.h4ckr.debutant.level_05 import Level05
    from client.games.h4ckr.debutant.levels_06_10 import (
        Level06, Level07, Level08, Level09, Level10)
    return [
        Level01(screen, settings),
        Level02(screen, settings),
        Level03(screen, settings),
        Level04(screen, settings),
        Level05(screen, settings),
        Level06(screen, settings),
        Level07(screen, settings),
        Level08(screen, settings),
        Level09(screen, settings),
        Level10(screen, settings),
    ]


def _load_expert_levels(screen, settings):
    from client.games.h4ckr.expert.expert_levels import (
        LevelE01, LevelE02, LevelE03, LevelE04, LevelE05, LevelE06)
    return [
        LevelE01(screen, settings),
        LevelE02(screen, settings),
        LevelE03(screen, settings),
        LevelE04(screen, settings),
        LevelE05(screen, settings),
        LevelE06(screen, settings),
    ]


# ── Moteur principal ──────────────────────────────────────────────────────────────
class H4ckRGame:
    STATE_ROBOT_INTRO = "robot_intro"
    STATE_LEVEL       = "level"
    STATE_BADGE       = "badge"
    STATE_ROBOT_MID   = "robot_mid"
    STATE_CERTIFICATE = "certificate"
    STATE_DONE        = "done"

    def __init__(self, screen: pygame.Surface, settings: Settings,
                 api: APIClient, auth: AuthManager, mode: str):
        self.screen   = screen
        self.settings = settings
        self.api      = api
        self.auth     = auth
        self.mode     = mode
        self.clock    = pygame.time.Clock()
        self.running  = True
        self.state    = self.STATE_ROBOT_INTRO

        # Chargement des niveaux
        if mode == "debutant":
            self.levels      = _load_debutant_levels(screen, settings)
            self.total_levels = 10
        else:
            self.levels      = _load_expert_levels(screen, settings)
            self.total_levels = 6

        self.current_idx = 0
        self.session_id  = None
        self.cert_code   = "H4CKR-OFFLINE"

        # HUD
        self.hud = GameHUD(screen, settings, mode, self.total_levels)

        # Démarrer session API
        threading.Thread(target=self._start_session, daemon=True).start()

    def _start_session(self):
        if not self.auth.user_id:
            return
        resp = self.api.start_session(self.auth.user_id, self.mode)
        if resp and "session_id" in resp:
            self.session_id = resp["session_id"]
            self.hud.session_id = self.session_id

    def run(self):
        while self.running:
            dt   = self.clock.tick(60) / 1000.0
            dt   = min(dt, 0.05)
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            self._handle_state(events, dt)
            pygame.display.flip()

    def _handle_state(self, events, dt):
        if self.state == self.STATE_ROBOT_INTRO:
            self._run_robot_intro()
            self.state = self.STATE_LEVEL

        elif self.state == self.STATE_LEVEL:
            level = self.levels[self.current_idx]
            for event in events:
                # HUD hint button
                if self.hud.handle_event(event):
                    self.hud.show_hint(level.get_hint())
                level.handle_event(event)
                if level.is_solved():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self._advance()
            level.update(dt)
            self.hud.update(dt)
            level.draw()
            self.hud.draw()

        elif self.state == self.STATE_BADGE:
            self._run_badge()
            self._run_robot_mid()
            self.state = self.STATE_LEVEL

        elif self.state == self.STATE_CERTIFICATE:
            self._run_certificate()
            self.running = False

    def _advance(self):
        level = self.levels[self.current_idx]
        pts   = level.get_points()
        if self.hud.hint_used:
            pts = max(0, pts - 30)

        self.hud.add_points(pts)

        # API
        if self.session_id:
            threading.Thread(target=self.api.complete_level, daemon=True, kwargs={
                "session_id": self.session_id,
                "level_num":  self.current_idx + 1,
                "points":     pts,
                "hint_used":  self.hud.hint_used,
                "time_taken": int(level.time_spent),
            }).start()

        self.hud.hint_used = False
        self.current_idx  += 1

        # Badge mi-parcours débutant après niveau 5
        if self.mode == "debutant" and self.current_idx == 5:
            self.state = self.STATE_BADGE
            self.hud.current_level = self.current_idx + 1
            return

        if self.current_idx >= self.total_levels:
            self._complete_game()
        else:
            self.hud.current_level = self.current_idx + 1

    def _complete_game(self):
        if self.session_id:
            resp = self.api.complete_session(self.session_id)
            if resp:
                self.cert_code = resp.get("certificate_code", "H4CKR-OFFLINE")
        self.state = self.STATE_CERTIFICATE

    def _run_robot_intro(self):
        title, msg, mode_key = ROBOT_INTROS[self.mode]
        robot = RobotVideoScreen(self.screen, self.settings, msg, title, mode_key)
        robot.run()

    def _run_robot_mid(self):
        title, msg, mode_key = ROBOT_INTROS["badge_mid"]
        remaining = self.total_levels - self.current_idx
        msg_full  = msg + f" Il te reste {remaining} niveaux."
        robot = RobotVideoScreen(self.screen, self.settings, msg_full, title, mode_key)
        robot.run()

    def _run_badge(self):
        badge_screen = BadgeScreen(
            self.screen, self.settings,
            self.auth.username or "Agent",
            "Cyber Initié",
            levels_remaining=self.total_levels - self.current_idx,
        )
        badge_screen.run()

    def _run_certificate(self):
        cert_screen = CertificateScreen(
            self.screen, self.settings,
            self.auth.username or "Agent",
            self.mode,
            self.hud.score,
            self.cert_code,
        )
        cert_screen.run()
