"""Badge et Certificat screens — générés en Pygame."""
import math
import datetime
import pygame
from client.core.settings import Settings


class BadgeScreen:
    """Écran badge mi-parcours (après niveau 5 débutant)."""

    def __init__(self, screen: pygame.Surface, settings: Settings,
                 username: str, badge_name: str, levels_remaining: int):
        self.screen          = screen
        self.settings        = settings
        self.username        = username
        self.badge_name      = badge_name
        self.levels_remaining= levels_remaining
        self.clock           = pygame.time.Clock()
        self.running         = True
        self.t               = 0.0

        self.font_title = settings.load_font(38)
        self.font_body  = settings.load_font(22)
        self.font_small = settings.load_font(16)
        self.font_hint  = settings.load_font(14)

        # Particules étoiles
        self.stars = [
            {"x": __import__("random").uniform(0, 1280),
             "y": __import__("random").uniform(0, 720),
             "spd": __import__("random").uniform(40, 120),
             "size": __import__("random").randint(2, 5)}
            for _ in range(60)
        ]

    def run(self):
        import random
        W, H = self.screen.get_size()
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 0.05)
            self.t += dt

            for event in pygame.event.get():
                import sys
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self.running = False

            # Update stars
            for s in self.stars:
                s["y"] += s["spd"] * dt
                if s["y"] > H:
                    s["y"] = 0
                    s["x"] = random.uniform(0, W)

            self._draw(W, H)
            pygame.display.flip()

    def _draw(self, W: int, H: int):
        self.screen.fill((4, 8, 4))
        t = self.t

        # Stars
        for s in self.stars:
            alpha = int(80 + 60 * math.sin(t * 2 + s["x"]))
            star = pygame.Surface((s["size"]*2, s["size"]*2), pygame.SRCALPHA)
            pygame.draw.circle(star, (50, 255, 130, alpha), (s["size"], s["size"]), s["size"])
            self.screen.blit(star, (int(s["x"]), int(s["y"])))

        cx, cy = W // 2, H // 2

        # Badge hexagonal doré
        self._draw_badge(cx, cy - 80, t)

        # Texte
        glow_txt = self.font_title.render("🏆 BADGE OBTENU !", True, self.settings.COLOR_WARNING)
        glow_txt.set_alpha(60)
        self.screen.blit(glow_txt, glow_txt.get_rect(center=(cx+3, cy+100+3)))
        title = self.font_title.render("🏆 BADGE OBTENU !", True, self.settings.COLOR_WARNING)
        self.screen.blit(title, title.get_rect(center=(cx, cy+100)))

        badge_s = self.font_body.render(f'"{self.badge_name}"', True, self.settings.COLOR_TEXT)
        self.screen.blit(badge_s, badge_s.get_rect(center=(cx, cy+148)))

        user_s = self.font_small.render(
            f"Félicitations {self.username} ! Tu viens de terminer les 5 premiers niveaux.",
            True, self.settings.COLOR_TEXT_DIM
        )
        self.screen.blit(user_s, user_s.get_rect(center=(cx, cy+185)))

        rem_s = self.font_body.render(
            f"Il te reste {self.levels_remaining} niveaux avant le certificat final !",
            True, self.settings.COLOR_PRIMARY
        )
        self.screen.blit(rem_s, rem_s.get_rect(center=(cx, cy+220)))

        hint = self.font_hint.render("[ Appuie sur ESPACE ou clique pour continuer ]",
                                     True, self.settings.COLOR_TEXT_DIM)
        hint.set_alpha(int(150 + 80 * math.sin(t * 2)))
        self.screen.blit(hint, hint.get_rect(center=(cx, H - 30)))

    def _draw_badge(self, cx: int, cy: int, t: float):
        """Badge hexagonal animé doré."""
        r = 70
        gold = (255, 190, 50)
        dark_gold = (180, 120, 20)

        # Glow rotatif
        for i in range(6):
            angle = t * 60 + i * 60
            gx = cx + int((r + 20) * math.cos(math.radians(angle)))
            gy = cy + int((r + 20) * math.sin(math.radians(angle)))
            g = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(g, (*gold, int(80 + 60 * math.sin(t * 3 + i))), (8, 8), 7)
            self.screen.blit(g, (gx - 8, gy - 8))

        # Corps hexagonal
        hex_pts = [(cx + r * math.cos(math.radians(60*i - 30)),
                    cy + r * math.sin(math.radians(60*i - 30))) for i in range(6)]
        pygame.draw.polygon(self.screen, dark_gold, hex_pts)
        pygame.draw.polygon(self.screen, gold, hex_pts, 4)

        # Étoile intérieure
        inner_r = 35
        shine_pts = []
        for i in range(5):
            angle_out = math.radians(i * 72 - 90)
            shine_pts.append((cx + inner_r * math.cos(angle_out),
                               cy + inner_r * math.sin(angle_out)))
            angle_in = math.radians(i * 72 - 90 + 36)
            shine_pts.append((cx + 14 * math.cos(angle_in),
                               cy + 14 * math.sin(angle_in)))
        pygame.draw.polygon(self.screen, gold, shine_pts)

        # Texte dans le badge
        fnt = pygame.font.SysFont("Consolas", 13, bold=True)
        num = fnt.render("LVL 5", True, (20, 10, 0))
        self.screen.blit(num, num.get_rect(center=(cx, cy)))


class CertificateScreen:
    """Écran certificat de fin de mode."""

    def __init__(self, screen: pygame.Surface, settings: Settings,
                 username: str, mode: str, score: int, cert_code: str):
        self.screen    = screen
        self.settings  = settings
        self.username  = username
        self.mode      = mode
        self.score     = score
        self.cert_code = cert_code
        self.clock     = pygame.time.Clock()
        self.running   = True
        self.t         = 0.0
        self.date      = datetime.datetime.now().strftime("%d/%m/%Y")

        self.font_title = settings.load_font(32)
        self.font_sub   = settings.load_font(20)
        self.font_body  = settings.load_font(17)
        self.font_small = settings.load_font(14)
        self.font_code  = pygame.font.SysFont("Consolas", 16)

    def run(self):
        W, H = self.screen.get_size()
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.t += dt
            for event in pygame.event.get():
                import sys
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self.running = False
            self._draw(W, H)
            pygame.display.flip()

    def _draw(self, W: int, H: int):
        t = self.t

        # Fond matrix
        self.screen.fill((3, 8, 3))
        for i in range(30):
            x = (i * 67 + int(t * 30)) % W
            y = (i * 113 + int(t * 60)) % H
            fnt = pygame.font.SysFont("Consolas", 14)
            ch = chr(0x30A0 + (i * 7 + int(t * 8)) % 96)
            s = fnt.render(ch, True, (0, 120, 0))
            s.set_alpha(40)
            self.screen.blit(s, (x, y))

        # Parchemin certificat
        cw, ch = 720, 460
        cx, cy = (W - cw) // 2, (H - ch) // 2

        # Background parchemin
        parch = pygame.Surface((cw, ch), pygame.SRCALPHA)
        parch.fill((8, 25, 8, 240))
        self.screen.blit(parch, (cx, cy))

        # Bordure animée
        border_alpha = int(180 + 60 * math.sin(t * 2))
        mode_color = self.settings.COLOR_PRIMARY if self.mode == "debutant" else self.settings.COLOR_DANGER
        border = pygame.Surface((cw, ch), pygame.SRCALPHA)
        pygame.draw.rect(border, (*mode_color, border_alpha), (0, 0, cw, ch), 3, border_radius=10)
        # Coins dorés
        for dx, dy in [(0,0),(cw-20,0),(0,ch-20),(cw-20,ch-20)]:
            pygame.draw.rect(border, (255, 190, 50, 200), (dx, dy, 20, 3))
            pygame.draw.rect(border, (255, 190, 50, 200), (dx, dy, 3, 20))
        self.screen.blit(border, (cx, cy))

        # Zigzag haut/bas
        for x in range(cx, cx+cw, 20):
            y_top = cy + 8
            y_bot = cy + ch - 8
            pygame.draw.line(self.screen, (*mode_color, 100), (x, y_top), (x+10, y_top+6))
            pygame.draw.line(self.screen, (*mode_color, 100), (x, y_bot), (x+10, y_bot-6))

        # Contenu
        yy = cy + 28

        # En-tête
        header = self.font_title.render("h4ckR — CERTIFICAT DE COMPLÉTION", True, mode_color)
        self.screen.blit(header, header.get_rect(center=(W//2, yy + 16))); yy += 52

        sep = self.font_code.render("═" * 70, True, (*mode_color, 120))
        self.screen.blit(sep, sep.get_rect(center=(W//2, yy))); yy += 20

        # Corps
        self.screen.blit(self.font_body.render("Ce certificat est décerné à :", True,
                         self.settings.COLOR_TEXT_DIM), (cx+40, yy)); yy += 28
        name_s = self.font_title.render(self.username, True, self.settings.COLOR_WARNING)
        self.screen.blit(name_s, name_s.get_rect(center=(W//2, yy + 8))); yy += 44

        mode_txt = "DÉBUTANT" if self.mode == "debutant" else "EXPERT"
        for line, color in [
            (f"Pour avoir complété le mode {mode_txt}", self.settings.COLOR_TEXT),
            (f"avec un score de : {self.score:,} points", self.settings.COLOR_WARNING),
            (f"Date : {self.date}", self.settings.COLOR_TEXT_DIM),
        ]:
            s = self.font_body.render(line, True, color)
            self.screen.blit(s, s.get_rect(center=(W//2, yy + 8))); yy += 36

        sep2 = self.font_code.render("═" * 70, True, (*mode_color, 80))
        self.screen.blit(sep2, sep2.get_rect(center=(W//2, yy))); yy += 18

        # Code certificat
        code_lbl = self.font_small.render("Code de vérification :", True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(code_lbl, code_lbl.get_rect(center=(W//2, yy))); yy += 20
        code_s = self.font_code.render(self.cert_code, True, self.settings.COLOR_ACCENT)
        self.screen.blit(code_s, code_s.get_rect(center=(W//2, yy))); yy += 30

        # Hint
        hint = self.font_small.render("[ ESPACE pour continuer ]", True, self.settings.COLOR_TEXT_DIM)
        hint.set_alpha(int(150 + 80 * math.sin(t * 2)))
        self.screen.blit(hint, hint.get_rect(center=(W//2, cy + ch - 20)))
