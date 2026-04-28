"""
H4CKR — Point d'entrée principal du jeu.
Lance avec : python main.py
Build exe  : pyinstaller build.spec
"""
import pygame
import sys
import time
import threading
from config import *
from src.utils.api import api
from src.screens.auth_screen        import AuthScreen
from src.screens.menu_screen        import MenuScreen
from src.screens.game_screen        import GameScreen
from src.screens.leaderboard_screen import (
    LeaderboardScreen, GuideScreen, ContactScreen, CertificateScreen,
)
from src.utils.robot_video import HackerVideoScreen


# ── Écran de vérification backend ─────────────────────────────────────────────

class BackendCheckScreen:
    """
    Vérifie que le backend FastAPI est accessible avant de démarrer.
    Affiche une erreur claire si le serveur n'est pas lancé.
    """
    def __init__(self, screen):
        self.screen    = screen
        self.w, self.h = screen.get_size()
        self._status   = "checking"   # "checking" | "ok" | "error"
        self._t        = 0.0
        self._attempt  = 0
        self._max_attempts = 3
        self._done     = False
        self._skip     = False
        threading.Thread(target=self._check, daemon=True).start()

    def _check(self):
        for i in range(self._max_attempts):
            self._attempt = i + 1
            if api.is_backend_online():
                self._status = "ok"
                self._done   = True
                return
            time.sleep(1.5)
        self._status = "error"

    def handle_event(self, event):
        if self._status == "error":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Réessayer
                    self._status = "checking"
                    self._attempt = 0
                    threading.Thread(target=self._check, daemon=True).start()
                elif event.key == pygame.K_ESCAPE:  # Ignorer et continuer quand même
                    self._skip = True
                    self._done = True

    def update(self, dt):
        self._t += dt
        if self._done:
            return True
        return None

    def draw(self):
        surf = self.screen
        surf.fill(C_BG)

        # Grille fond
        for gx in range(0, self.w, 50):
            pygame.draw.line(surf, (8, 18, 8), (gx, 0), (gx, self.h))
        for gy in range(0, self.h, 50):
            pygame.draw.line(surf, (8, 18, 8), (0, gy), (self.w, gy))

        cx = self.w // 2

        # Logo
        font_big  = pygame.font.SysFont(FONT_MONO, 52, bold=True)
        font_med  = pygame.font.SysFont(FONT_MONO, 18, bold=True)
        font_sm   = pygame.font.SysFont(FONT_MONO, 14)
        font_xs   = pygame.font.SysFont(FONT_MONO, 12)

        title = font_big.render("H4CKR", True, C_GREEN)
        surf.blit(title, title.get_rect(centerx=cx, top=80))

        sub = font_sm.render("HACKING SIMULATION GAME", True, C_GREEN_DIM)
        surf.blit(sub, sub.get_rect(centerx=cx, top=148))

        # Box de statut
        box = pygame.Rect(cx - 320, 200, 640, 320)
        pygame.draw.rect(surf, C_BG2, box, border_radius=12)

        if self._status == "checking":
            pygame.draw.rect(surf, C_GREEN_DIM, box, 1, border_radius=12)

            dots = "." * (int(self._t * 3) % 4)
            lbl = font_med.render(f"Connexion au serveur{dots}", True, C_GREEN)
            surf.blit(lbl, lbl.get_rect(centerx=cx, top=240))

            info = font_sm.render(
                f"Tentative {self._attempt}/{self._max_attempts} — {API_BASE_URL}",
                True, C_GRAY
            )
            surf.blit(info, info.get_rect(centerx=cx, top=280))

            # Spinner animé
            angle = self._t * 200
            for i in range(8):
                a = angle + i * 45
                import math
                rx = int(cx + 30 * math.cos(math.radians(a)))
                ry = int(340 + 15 * math.sin(math.radians(a)))
                alpha = int(255 * (i / 8))
                pygame.draw.circle(surf, (*C_GREEN[:3],), (rx, ry), 4 - i // 3)

        elif self._status == "ok":
            pygame.draw.rect(surf, C_GREEN_DIM, box, 2, border_radius=12)
            ok = font_med.render("Serveur connecte !", True, C_GREEN)
            surf.blit(ok, ok.get_rect(centerx=cx, top=240))
            sub2 = font_sm.render("Demarrage du jeu...", True, C_GREEN_DIM)
            surf.blit(sub2, sub2.get_rect(centerx=cx, top=280))

        elif self._status == "error":
            pygame.draw.rect(surf, C_RED, box, 2, border_radius=12)

            err_title = font_med.render("SERVEUR INACCESSIBLE", True, C_RED)
            surf.blit(err_title, err_title.get_rect(centerx=cx, top=220))

            lines = [
                ("Le backend FastAPI n'est pas demarré.", C_WHITE),
                ("", C_WHITE),
                ("Pour corriger :", C_YELLOW),
                ("1. Ouvrez un terminal", C_WHITE),
                ("2. Allez dans le dossier  backend/", C_WHITE),
                ("3. Tapez la commande :", C_WHITE),
                ("   uvicorn main:app --reload --port 8000", C_GREEN),
                ("", C_WHITE),
                ("Ou double-cliquez sur  DEMARRER_BACKEND.bat", C_CYAN),
            ]
            y = 262
            for line, col in lines:
                if line:
                    s = font_xs.render(line, True, col)
                    surf.blit(s, s.get_rect(centerx=cx, top=y))
                y += 20

            # Boutons
            btn_retry = pygame.Rect(cx - 200, box.bottom - 52, 180, 36)
            btn_skip  = pygame.Rect(cx + 20,  box.bottom - 52, 180, 36)
            mx, my    = pygame.mouse.get_pos()

            for btn, label, col in [
                (btn_retry, "REINESSAYER [ENTREE]", C_GREEN),
                (btn_skip,  "IGNORER [ECHAP]",      C_GRAY),
            ]:
                hov = btn.collidepoint(mx, my)
                pygame.draw.rect(surf, (20, 40, 20) if hov else C_BG2, btn, border_radius=6)
                pygame.draw.rect(surf, col, btn, 1, border_radius=6)
                s = font_xs.render(label, True, col)
                surf.blit(s, s.get_rect(center=btn.center))

            # Clic souris
            if pygame.mouse.get_pressed()[0]:
                if btn_retry.collidepoint(mx, my):
                    self._status = "checking"
                    self._attempt = 0
                    threading.Thread(target=self._check, daemon=True).start()
                elif btn_skip.collidepoint(mx, my):
                    self._skip = True
                    self._done = True

        # URL en bas
        url_txt = font_xs.render(f"API : {API_BASE_URL}", True, C_GRAY)
        surf.blit(url_txt, url_txt.get_rect(centerx=cx, top=self.h - 30))


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    # Icône
    icon = pygame.Surface((32, 32))
    icon.fill(C_BG)
    pygame.draw.rect(icon, C_GREEN, (4, 4, 24, 24), 2)
    icon_font = pygame.font.SysFont(FONT_MONO, 14, bold=True)
    icon.blit(icon_font.render(">_", True, C_GREEN), (6, 8))
    pygame.display.set_icon(icon)

    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock  = pygame.time.Clock()

    # ── State machine ─────────────────────────────────────────────────────────
    state          = "backend_check"
    current_screen = BackendCheckScreen(screen)

    def switch(new_state):
        nonlocal state, current_screen
        state = new_state
        if new_state == "backend_check":
            current_screen = BackendCheckScreen(screen)
        elif new_state == "auth":
            current_screen = AuthScreen(screen)
        elif new_state == "menu":
            current_screen = MenuScreen(screen)
        elif new_state == "video_beginner":
            current_screen = HackerVideoScreen(screen, "beginner")
        elif new_state == "video_expert":
            current_screen = HackerVideoScreen(screen, "expert")
        elif new_state == "video_beginner_mid":
            current_screen = HackerVideoScreen(screen, "beginner_midpoint")
        elif new_state == "beginner":
            current_screen = GameScreen(screen, "beginner")
        elif new_state == "expert":
            current_screen = GameScreen(screen, "expert")
        elif new_state == "leaderboard":
            current_screen = LeaderboardScreen(screen)
        elif new_state == "guide":
            current_screen = GuideScreen(screen)
        elif new_state == "contact":
            current_screen = ContactScreen(screen)
        elif new_state == "cert_beginner":
            current_screen = CertificateScreen(screen, "beginner")
        elif new_state == "cert_expert":
            current_screen = CertificateScreen(screen, "expert")

    running = True
    while running:
        dt     = clock.tick(FPS) / 1000.0
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            current_screen.handle_event(event)

        action = current_screen.update(dt)

        # Transitions
        if action:
            if action == "quit" or action is False:
                running = False
            elif action is True:
                if state == "backend_check":
                    switch("auth")
                elif state == "auth":
                    switch("menu")
                elif state == "video_beginner":
                    switch("beginner")
                elif state == "video_expert":
                    switch("expert")
                elif state == "video_beginner_mid":
                    switch("beginner")
            elif action == "menu":
                switch("menu")
            elif action == "beginner":
                switch("video_beginner")
            elif action == "expert":
                switch("video_expert")
            elif action == "leaderboard":
                switch("leaderboard")
            elif action == "guide":
                switch("guide")
            elif action == "contact":
                switch("contact")
            elif action == "finished_beginner":
                switch("cert_beginner")
            elif action == "finished_expert":
                switch("cert_expert")

        current_screen.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
