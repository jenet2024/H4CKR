"""
Génère une animation robot hacker (visage) directement en Pygame.
Remplace les fichiers MP4 avec une animation procédurale immersive.
Le robot parle avec une voix synthétique (pyttsx3).
"""
import pygame
import math
import random
import threading
import time
from config import *
from src.utils.renderer import get_font, draw_text

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


# ── Palette robot ─────────────────────────────────────────────────────────────
R_GREEN  = (57,  255, 20)
R_DARK   = (5,   15,  5)
R_BORDER = (30,  80,  30)
R_RED    = (255, 30,  60)
R_CYAN   = (0,   200, 220)
R_DIM    = (20,  60,  20)


class RobotFace:
    """
    Visage de robot animé dessiné en Pygame (cercles, rectangles, lignes).
    Bouche animée selon si le robot "parle".
    """
    def __init__(self, cx, cy, scale=1.0):
        self.cx    = cx
        self.cy    = cy
        self.s     = scale
        self._t    = 0.0
        self.talking = False
        self._mouth_open = 0.0
        self._eye_blink  = 1.0
        self._blink_t    = 0.0
        self._glitch_t   = 0.0
        self._scan_y     = 0.0

    def _sc(self, v):
        return int(v * self.s)

    def update(self, dt, talking=False):
        self._t        += dt
        self.talking    = talking
        self._scan_y    = (self._scan_y + dt * 80) % (self._sc(200))

        # Blink
        self._blink_t += dt
        if self._blink_t > 3.5:
            self._eye_blink = max(0.0, 1.0 - (self._blink_t - 3.5) * 10)
            if self._blink_t > 3.6:
                self._eye_blink = min(1.0, (self._blink_t - 3.6) * 10)
            if self._blink_t > 3.7:
                self._eye_blink = 1.0
                self._blink_t   = 0

        # Mouth animation
        if talking:
            self._mouth_open = abs(math.sin(self._t * 8)) * 0.8 + 0.2
        else:
            self._mouth_open = max(0.0, self._mouth_open - dt * 4)

        # Glitch
        self._glitch_t += dt
        if self._glitch_t > random.uniform(4, 8):
            self._glitch_t = 0

    def draw(self, surf):
        cx, cy = self.cx, self.cy
        s = self.s
        t = self._t

        def sc(v):
            return int(v * s)

        # Floating bob
        bob = math.sin(t * 1.2) * sc(4)
        cy += int(bob)

        # ── Fond hexagonal / carré arrondi ────────────────────────────────────
        face_rect = pygame.Rect(cx - sc(90), cy - sc(100), sc(180), sc(200))
        pygame.draw.rect(surf, R_DARK,  face_rect, border_radius=sc(20))
        pygame.draw.rect(surf, R_BORDER, face_rect, 2, border_radius=sc(20))

        # Scanline interne
        scan_surf = pygame.Surface((sc(180), sc(200)), pygame.SRCALPHA)
        sy = int(self._scan_y)
        pygame.draw.line(scan_surf, (*R_GREEN, 40), (0, sy), (sc(180), sy), 2)
        surf.blit(scan_surf, (cx - sc(90), cy - sc(100)))

        # ── Oreilles / antennes ───────────────────────────────────────────────
        for side in (-1, 1):
            ex = cx + side * sc(95)
            pygame.draw.rect(surf, R_BORDER,
                             pygame.Rect(ex - sc(5 if side < 0 else 0), cy - sc(30), sc(5), sc(20)),
                             border_radius=sc(2))
            # Clignotant
            if int(t * 2) % 2 == 0:
                pygame.draw.circle(surf, R_RED if side < 0 else R_CYAN,
                                   (ex + side * sc(2), cy - sc(35)), sc(4))

        # Antenne centrale
        pygame.draw.line(surf, R_BORDER,
                         (cx, cy - sc(100)), (cx, cy - sc(130)), 2)
        blink = abs(math.sin(t * 3))
        col = (int(R_GREEN[0] * blink), int(R_GREEN[1] * blink), int(R_GREEN[2] * blink))
        pygame.draw.circle(surf, col, (cx, cy - sc(133)), sc(5))

        # ── Front / bandeau haut ──────────────────────────────────────────────
        band_rect = pygame.Rect(cx - sc(85), cy - sc(95), sc(170), sc(20))
        pygame.draw.rect(surf, (15, 40, 15), band_rect, border_radius=sc(4))
        # Petits pixels clignotants
        for i in range(5):
            px = cx - sc(70) + i * sc(32)
            col2 = R_GREEN if random.random() > 0.3 else R_DIM
            pygame.draw.rect(surf, col2,
                             pygame.Rect(px, cy - sc(91), sc(8), sc(12)),
                             border_radius=2)

        # ── Yeux ──────────────────────────────────────────────────────────────
        for side, ex in [(-1, cx - sc(32)), (1, cx + sc(32))]:
            ey = cy - sc(30)
            ew, eh_full = sc(40), sc(28)
            eh = int(eh_full * self._eye_blink)

            # Socket
            socket_rect = pygame.Rect(ex - ew // 2, ey - sc(18), ew, eh_full)
            pygame.draw.rect(surf, (8, 20, 8), socket_rect, border_radius=sc(6))
            pygame.draw.rect(surf, R_BORDER, socket_rect, 1, border_radius=sc(6))

            if eh > 2:
                # Iris
                eye_surf = pygame.Surface((ew, eh), pygame.SRCALPHA)
                pygame.draw.rect(eye_surf, (*R_GREEN, 180),
                                 eye_surf.get_rect(), border_radius=sc(5))
                # Pupille
                pygame.draw.circle(eye_surf, R_DARK,
                                   (ew // 2, eh // 2), int(sc(8) * self._eye_blink))
                # Reflet
                pygame.draw.circle(eye_surf, (*C_WHITE, 200),
                                   (ew // 2 - sc(4), max(2, eh // 2 - sc(4))), sc(3))
                surf.blit(eye_surf, (ex - ew // 2, ey - sc(18) + (eh_full - eh) // 2))

            # Scan animé dans l'œil
            scan_col = int(abs(math.sin(t * 3 + side)) * 255)
            scan_rect = pygame.Rect(ex - ew // 2, ey - sc(18), ew, 2)
            scan_pos  = int((math.sin(t * 4 + side * 1.5) + 1) / 2 * eh_full)
            scan_rect.y = ey - sc(18) + scan_pos
            pygame.draw.rect(surf, (0, scan_col, 0, 100), scan_rect)

        # ── Nez (LED) ──────────────────────────────────────────────────────────
        nose_glow = abs(math.sin(t * 2))
        nc = (int(R_CYAN[0] * nose_glow), int(R_CYAN[1] * nose_glow), int(R_CYAN[2] * nose_glow))
        pygame.draw.circle(surf, nc, (cx, cy + sc(5)), sc(4))

        # ── Bouche ────────────────────────────────────────────────────────────
        mw = sc(60)
        mh_max = sc(20)
        mh = int(mh_max * self._mouth_open)
        mouth_rect = pygame.Rect(cx - mw // 2, cy + sc(25) - mh // 2, mw, max(4, mh))
        pygame.draw.rect(surf, (8, 20, 8), mouth_rect, border_radius=sc(4))
        pygame.draw.rect(surf, R_GREEN, mouth_rect, 2, border_radius=sc(4))

        # Dents (grille LED)
        if mh > sc(8):
            tooth_w = mw // 5
            for i in range(5):
                tx = cx - mw // 2 + i * tooth_w + 2
                col3 = R_GREEN if i % 2 == 0 else R_DIM
                pygame.draw.rect(surf, col3,
                                 pygame.Rect(tx, mouth_rect.y + 2, tooth_w - 4, mh - 4),
                                 border_radius=2)

        # ── Menton / circuit ──────────────────────────────────────────────────
        chin_y = cy + sc(75)
        for i, (ox, oy, ow) in enumerate([(-sc(40), 0, sc(25)),
                                           (sc(15),  0, sc(25)),
                                           (-sc(15), sc(10), sc(30))]):
            col4 = R_GREEN if (int(t * 2 + i) % 3 != 0) else R_DIM
            pygame.draw.rect(surf, col4,
                             pygame.Rect(cx + ox, chin_y + oy, ow, sc(4)),
                             border_radius=2)

        # ── Glitch ────────────────────────────────────────────────────────────
        if self._glitch_t < 0.08:
            gl = pygame.Surface((sc(180), sc(200)), pygame.SRCALPHA)
            for _ in range(3):
                gy = random.randint(0, sc(200))
                gh = random.randint(2, sc(8))
                pygame.draw.rect(gl, (*R_RED, random.randint(40, 120)),
                                 (0, gy, sc(180), gh))
            surf.blit(gl, (cx - sc(90), cy - sc(100) + int(bob)))


class HackerVideoScreen:
    """
    Écran complet d'introduction niveau avec robot animé + texte + voix.
    """
    SCRIPT = {
        "beginner": [
            "INITIALISATION DU SYSTÈME...",
            "Agent, bienvenue dans H4CKR.",
            "Vous allez commencer le niveau DÉBUTANT.",
            "10 étapes vous attendent.",
            "Les 5 premières vous enseigneront les bases :",
            "décodage Base64, chiffre de César,",
            "stéganographie et analyse de fichiers.",
            "À la fin des 5 premières étapes,",
            "un badge de vérification vous sera remis.",
            "Restez concentré. Bonne chance, Agent.",
        ],
        "beginner_midpoint": [
            "FÉLICITATIONS, AGENT.",
            "Vous venez de terminer les 5 premières étapes.",
            "Vous obtenez le badge : INITIÉ CYBER.",
            "Il vous reste 5 étapes avant la certification.",
            "Les prochains défis seront plus complexes.",
            "Préparez-vous. La mission continue.",
        ],
        "expert": [
            "CONNEXION SÉCURISÉE ÉTABLIE.",
            "Agent confirmé. Niveau EXPERT activé.",
            "6 missions de haute difficulté vous attendent.",
            "Terminal interactif, analyse de logs,",
            "extraction de métadonnées, exploits zero-day.",
            "Chaque action sera tracée et notée.",
            "Ici, les erreurs coûtent des points.",
            "Montrez ce que vous savez faire.",
            "L'accès au terminal est maintenant actif.",
            "Commencez. Le chrono tourne.",
        ],
    }

    def __init__(self, screen, level_key="beginner"):
        self.screen    = screen
        self.level_key = level_key
        self.w, self.h = screen.get_size()

        self.robot  = RobotFace(self.w // 2, self.h // 2 - 40, scale=1.3)
        self.lines  = self.SCRIPT.get(level_key, self.SCRIPT["beginner"])
        self._line_idx  = 0
        self._char_idx  = 0
        self._displayed = ""
        self._char_t    = 0.0
        self._char_speed = 0.04
        self._line_pause = 0.0
        self._talking   = False
        self._done      = False
        self._skip_held = False
        self._bg_stars  = [(random.randint(0, self.w),
                            random.randint(0, self.h),
                            random.uniform(0.3, 1.0)) for _ in range(80)]
        self._t = 0.0

        # Démarrer TTS en thread
        self._tts_thread = threading.Thread(target=self._speak_all, daemon=True)
        self._tts_thread.start()

    def _speak_all(self):
        if not TTS_AVAILABLE:
            return
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 155)
            engine.setProperty("volume", 0.9)
            # Cherche une voix française si dispo
            voices = engine.getProperty("voices")
            for v in voices:
                if "fr" in v.id.lower() or "french" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            for line in self.lines:
                self._talking = True
                engine.say(line)
                engine.runAndWait()
                time.sleep(0.3)
            self._talking = False
        except Exception:
            pass

    def handle_event(self, event):
        """Interface standard — reçoit les events de main.py."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                self._done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._done = True

    def update(self, dt):
        self._t += dt
        self.robot.update(dt, talking=self._talking)

        # Avancement du texte
        if self._line_idx < len(self.lines):
            current_line = self.lines[self._line_idx]
            if self._char_idx < len(current_line):
                self._char_t += dt
                while self._char_t >= self._char_speed:
                    self._char_idx += 1
                    self._char_t   -= self._char_speed
                self._displayed = current_line[:self._char_idx]
            else:
                self._line_pause += dt
                if self._line_pause > 1.8:
                    self._line_idx  += 1
                    self._char_idx   = 0
                    self._displayed  = ""
                    self._char_t     = 0.0
                    self._line_pause = 0.0
        else:
            self._done = True

        return self._done

    def draw(self):
        """Interface standard — dessine sur self.screen."""
        surf = self.screen
        surf.fill(C_BG)

        # Étoiles
        for sx, sy, alpha in self._bg_stars:
            blink = abs(math.sin(self._t * alpha + sx * 0.01))
            col = (int(C_GREEN_DIM[0] * blink),
                   int(C_GREEN_DIM[1] * blink),
                   int(C_GREEN_DIM[2] * blink))
            pygame.draw.circle(surf, col, (int(sx), int(sy)), 1)

        # Grille fond
        for gx in range(0, self.w, 60):
            pygame.draw.line(surf, (10, 25, 10), (gx, 0), (gx, self.h))
        for gy in range(0, self.h, 60):
            pygame.draw.line(surf, (10, 25, 10), (0, gy), (self.w, gy))

        # Robot
        self.robot.draw(surf)

        # Bandeau titre
        label = {"beginner": "NIVEAU 1 — DÉBUTANT",
                 "beginner_midpoint": "MI-PARCOURS DÉBUTANT",
                 "expert": "NIVEAU 2 — EXPERT"}.get(self.level_key, "H4CKR")
        font_title = get_font(22, bold=True)
        t_surf = font_title.render(label, True, C_GREEN)
        surf.blit(t_surf, (self.w // 2 - t_surf.get_width() // 2, 30))

        # Zone texte robot en bas
        box_rect = pygame.Rect(60, self.h - 200, self.w - 120, 130)
        pygame.draw.rect(surf, C_BG2, box_rect, border_radius=10)
        pygame.draw.rect(surf, C_GREEN, box_rect, 2, border_radius=10)

        # Lignes précédentes (grisées)
        start_line = max(0, self._line_idx - 2)
        for i, li in enumerate(self.lines[start_line:self._line_idx]):
            draw_text(surf, li, box_rect.x + 16,
                      box_rect.y + 12 + i * 22, C_GREEN_DIM, 14)

        # Ligne courante (typée)
        if self._line_idx < len(self.lines):
            cursor = "█" if (int(self._t * 3) % 2 == 0) else " "
            draw_text(surf, self._displayed + cursor,
                      box_rect.x + 16,
                      box_rect.y + 12 + min(2, self._line_idx - start_line) * 22,
                      C_GREEN, 15, bold=True)

        # Prompt robot
        draw_text(surf, "> ROBOT_H4CKR :", box_rect.x + 16, box_rect.y - 22,
                  C_GREEN_MID, 13)

        # Skip hint
        draw_text(surf, "[ ESPACE / CLIC pour passer ]",
                  self.w // 2, self.h - 50, C_GRAY, 13, center=True)

        # Scanlines
        scan_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        for ly in range(0, self.h, 4):
            pygame.draw.line(scan_surf, (0, 0, 0, 15), (0, ly), (self.w, ly))
        surf.blit(scan_surf, (0, 0))
