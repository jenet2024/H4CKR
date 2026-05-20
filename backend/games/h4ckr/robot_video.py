"""
Robot hacker animé — généré entièrement en Pygame (pas de fichier vidéo).
Visage robot hexagonal, yeux LED, bouche animée, scanlines CRT, voix pyttsx3.
"""
import math
import random
import threading
import pygame
from typing import List
from client.core.settings import Settings



class RobotVideoScreen:
    """
    Écran d'introduction animé avec robot hacker qui parle.
    Le texte défile en sous-titres pendant que la voix TTS joue.
    """

    def __init__(self, screen: pygame.Surface, settings: Settings,
                 message: str, title: str = "TRANSMISSION REÇUE",
                 mode: str = "debutant"):
        self.screen   = screen
        self.settings = settings
        self.message  = message
        self.title    = title
        self.mode     = mode   # "debutant" | "expert" | "badge" | "warning"
        self.clock    = pygame.time.Clock()
        self.running  = True
        self.t        = 0.0
        self.done     = False

        # TTS
        self._speaking   = False
        self._speak_done = False
        self._start_tts()

        # Subtitle
        self.words        = message.split()
        self.word_idx     = 0
        self.subtitle_txt = ""
        self.subtitle_t   = 0.0
        self.WORD_SPEED   = 0.18   # secondes par mot

        # Fonts
        self.font_title  = settings.load_font(20)
        self.font_sub    = settings.load_font(16)
        self.font_small  = settings.load_font(14)
        self.font_hint   = settings.load_font(13)

        # Scanlines noise
        self.noise_frames = []
        self._prebuild_noise()

        # Particles
        self.particles: List[dict] = []

        # Mode couleurs
        self.color = {
            "debutant": (0, 230, 120),
            "expert":   (255, 60, 60),
            "badge":    (255, 190, 50),
            "warning":  (255, 80, 200),
        }.get(mode, (0, 230, 120))

    def _start_tts(self):
        def _speak():
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty("rate", 155)
                engine.setProperty("volume", 0.9)
                voices = engine.getProperty("voices")
                if voices:
                    engine.setProperty("voice", voices[0].id)
                self._speaking = True
                engine.say(self.message)
                engine.runAndWait()
            except Exception:
                pass
            finally:
                self._speaking = False
                self._speak_done = True

        threading.Thread(target=_speak, daemon=True).start()

    def _prebuild_noise(self):
        """Prépare quelques frames de bruit pour scanlines CRT."""
        for _ in range(4):
            W, H = self.screen.get_size()
            surf = pygame.Surface((W, H), pygame.SRCALPHA)
            for _ in range(200):
                x = random.randint(0, W)
                y = random.randint(0, H)
                w = random.randint(10, 80)
                pygame.draw.line(surf, (0, 255, 100, random.randint(5, 25)), (x, y), (x + w, y))
            self.noise_frames.append(surf)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 0.05)
            self.t += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    import sys; pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key in (
                        pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.running = False

            self._update_subtitle(dt)
            self._draw()
            pygame.display.flip()

            if self._speak_done and self.t > 3.0:
                import time; time.sleep(1.5)
                self.running = False

    def _update_subtitle(self, dt: float):
        self.subtitle_t += dt
        if self.word_idx < len(self.words) and self.subtitle_t >= self.WORD_SPEED:
            self.subtitle_t = 0.0
            # Ajoute le prochain mot
            line_words = self.subtitle_txt.split()
            if len(line_words) >= 8:
                self.subtitle_txt = self.words[self.word_idx]
            else:
                self.subtitle_txt += (" " if self.subtitle_txt else "") + self.words[self.word_idx]
            self.word_idx += 1

    def _draw(self):
        W, H = self.screen.get_size()
        t = self.t
        col = self.color

        # Fond CRT sombre
        self.screen.fill((4, 8, 4))

        # Grille hexagonale bg
        self._draw_hex_grid(W, H, col)

        # Bruit scanline
        if self.noise_frames:
            nf = self.noise_frames[int(t * 6) % len(self.noise_frames)]
            nf.set_alpha(int(18 + 8 * math.sin(t * 3)))
            self.screen.blit(nf, (0, 0))

        # Panneau terminal
        self._draw_terminal_frame(W, H, col)

        # Robot face
        robot_cx = W // 2
        robot_cy = H // 2 - 40
        self._draw_robot(robot_cx, robot_cy, col)

        # Titre transmission
        self._draw_transmission_header(W, H, col)

        # Sous-titres
        self._draw_subtitle(W, H)

        # Hint
        hint = self.font_hint.render("[ ESPACE / CLIC pour passer ]", True, (0, 100, 50))
        hint.set_alpha(int(80 + 60 * math.sin(t * 2)))
        self.screen.blit(hint, hint.get_rect(center=(W // 2, H - 18)))

    def _draw_hex_grid(self, W: int, H: int, col: tuple):
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        size = 30
        for row in range(-1, H // (size * 2) + 2):
            for c in range(-1, W // (int(size * 1.73)) + 2):
                offset_x = (size * 0.87) if row % 2 else 0
                cx = c * size * 1.73 + offset_x
                cy = row * size * 1.5
                alpha = int(8 + 5 * math.sin(self.t * 0.5 + c + row))
                points = [
                    (cx + size * math.cos(math.radians(60 * i)),
                     cy + size * math.sin(math.radians(60 * i)))
                    for i in range(6)
                ]
                pygame.draw.polygon(surf, (*col, alpha), points, 1)
        self.screen.blit(surf, (0, 0))

    def _draw_terminal_frame(self, W: int, H: int, col: tuple):
        """Cadre terminal centré."""
        fw, fh = min(700, W - 40), min(500, H - 80)
        fx, fy = (W - fw) // 2, (H - fh) // 2

        frame = pygame.Surface((fw, fh), pygame.SRCALPHA)
        frame.fill((0, 12, 0, 190))
        self.screen.blit(frame, (fx, fy))

        # Border clignotant
        alpha = int(150 + 80 * math.sin(self.t * 3))
        border = pygame.Surface((fw, fh), pygame.SRCALPHA)
        pygame.draw.rect(border, (*col, alpha), (0, 0, fw, fh), 2, border_radius=4)
        self.screen.blit(border, (fx, fy))

        # Corner brackets
        sz = 18
        for dx, dy in [(0,0),(fw-sz,0),(0,fh-sz),(fw-sz,fh-sz)]:
            pygame.draw.rect(self.screen, col, (fx+dx, fy+dy, sz, 2))
            pygame.draw.rect(self.screen, col, (fx+dx, fy+dy, 2, sz))

    def _draw_robot(self, cx: int, cy: int, col: tuple):
        t = self.t
        speaking = self._speaking

        # Tête hexagonale
        head_r = 75
        hex_pts = [
            (cx + head_r * math.cos(math.radians(60 * i - 30)),
             cy + head_r * math.sin(math.radians(60 * i - 30)))
            for i in range(6)
        ]
        # Shadow
        shadow_surf = pygame.Surface((head_r*2+20, head_r*2+20), pygame.SRCALPHA)
        pygame.draw.polygon(shadow_surf, (*col, 30),
            [(p[0]-cx+head_r+10, p[1]-cy+head_r+10) for p in hex_pts])
        self.screen.blit(shadow_surf, (cx-head_r-10, cy-head_r-10))

        # Corps métal
        body_surf = pygame.Surface((head_r*2+4, head_r*2+4), pygame.SRCALPHA)
        pts_local = [(p[0]-cx+head_r+2, p[1]-cy+head_r+2) for p in hex_pts]
        pygame.draw.polygon(body_surf, (15, 30, 15, 230), pts_local)
        pygame.draw.polygon(body_surf, (*col, 200), pts_local, 2)
        self.screen.blit(body_surf, (cx-head_r-2, cy-head_r-2))

        # Yeux LED (2 cercles lumineux)
        eye_y   = cy - 18
        eye_gap = 26
        for sign, blink_phase in [(-1, 0), (1, 1.2)]:
            ex = cx + sign * eye_gap
            # Blink aléatoire
            blink = int(t * 3 + blink_phase) % 20 == 0
            eye_col = (20, 20, 20) if blink else col
            eye_r = 10
            # Glow
            glow = pygame.Surface((eye_r*4, eye_r*4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*col, 50), (eye_r*2, eye_r*2), eye_r*2)
            self.screen.blit(glow, (ex - eye_r*2, eye_y - eye_r*2))
            # Eye
            pygame.draw.circle(self.screen, eye_col, (ex, eye_y), eye_r)
            pygame.draw.circle(self.screen, col, (ex, eye_y), eye_r, 1)
            # Pupille
            if not blink:
                pygame.draw.circle(self.screen, (255, 255, 255), (ex, eye_y), 3)

        # Bouche animée (s'ouvre quand parle)
        mouth_y  = cy + 22
        mouth_w  = 36
        mouth_h  = 8 + (int(10 * abs(math.sin(t * 8))) if speaking else 2)
        mouth_r  = pygame.Rect(cx - mouth_w // 2, mouth_y - mouth_h // 2, mouth_w, mouth_h)
        pygame.draw.rect(self.screen, (0, 0, 0), mouth_r, border_radius=4)
        pygame.draw.rect(self.screen, col, mouth_r, 2, border_radius=4)

        # Antenne
        ant_base = (cx, cy - head_r - 2)
        ant_top  = (cx + int(8 * math.sin(t * 2)), cy - head_r - 24)
        pygame.draw.line(self.screen, col, ant_base, ant_top, 2)
        # Signal
        signal_alpha = int(150 + 100 * math.sin(t * 5))
        sg = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(sg, (*col, signal_alpha), (6, 6), 5)
        self.screen.blit(sg, (ant_top[0]-6, ant_top[1]-6))

        # Circuits décoratifs
        for i, (offset_x, offset_y, length, vert) in enumerate([
            (-head_r-2, -20, 18, False),
            (-head_r-2, 10,  12, False),
            (head_r+2,  -20, 18, False),
            (head_r+2,  10,  12, False),
        ]):
            x1 = cx + offset_x
            y1 = cy + offset_y
            x2 = x1 - length if offset_x < 0 else x1 + length
            col_alpha = int(100 + 80 * math.sin(t * 2 + i))
            line_surf = pygame.Surface((abs(x2-x1)+4, 4), pygame.SRCALPHA)
            pygame.draw.line(line_surf, (*col, col_alpha), (0, 2), (abs(x2-x1), 2), 2)
            self.screen.blit(line_surf, (min(x1, x2), y1))

    def _draw_transmission_header(self, W: int, H: int, col: tuple):
        fw, fh = min(700, W - 40), min(500, H - 80)
        fx, fy = (W - fw) // 2, (H - fh) // 2

        # Barre titre
        bar = pygame.Surface((fw, 28), pygame.SRCALPHA)
        bar.fill((*col, 40))
        self.screen.blit(bar, (fx, fy))

        # Type animation
        char_count = min(len(self.title), int(self.t * 20))
        typed_title = self.title[:char_count] + ("_" if int(self.t * 4) % 2 == 0 else "")
        title_surf = self.font_title.render(f"[ {typed_title} ]", True, col)
        self.screen.blit(title_surf, title_surf.get_rect(center=(W // 2, fy + 14)))

    def _draw_subtitle(self, W: int, H: int):
        fw, fh = min(700, W - 40), min(500, H - 80)
        fx, fy = (W - fw) // 2, (H - fh) // 2

        # Zone sous-titre en bas du frame
        sub_y = fy + fh - 55
        sub_box = pygame.Surface((fw - 20, 46), pygame.SRCALPHA)
        sub_box.fill((0, 20, 0, 160))
        self.screen.blit(sub_box, (fx + 10, sub_y))

        if self.subtitle_txt:
            sub = self.font_sub.render(self.subtitle_txt, True, (180, 255, 180))
            self.screen.blit(sub, sub.get_rect(center=(W // 2, sub_y + 23)))
