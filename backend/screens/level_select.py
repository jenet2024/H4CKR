"""
Écran de sélection : Débutant | Expert | Guide | Contact | Leaderboard
"""
import math
import random
import sys
import pygame
from typing import Optional

from client.core.settings import Settings
from client.core.api_client import APIClient
from client.core.auth_manager import AuthManager


class LevelSelectScreen:
    def __init__(self, screen: pygame.Surface, settings: Settings,
                 api: APIClient, auth: AuthManager):
        self.screen   = screen
        self.settings = settings
        self.api      = api
        self.auth     = auth
        self.clock    = pygame.time.Clock()
        self.running  = True
        self.choice   = None   # "debutant" | "expert" | "guide" | "contact" | "leaderboard" | "quit"
        self.time_t   = 0.0

        self.font_title  = settings.load_font(48)
        self.font_sub    = settings.load_font(18)
        self.font_card   = settings.load_font(26)
        self.font_desc   = settings.load_font(15)
        self.font_small  = settings.load_font(13)
        self.font_name   = settings.load_font(22)

        # Particules hexagonales
        self.particles = [self._make_particle() for _ in range(40)]

        # Cartes principales
        self._build_cards()

    def _make_particle(self) -> dict:
        W, H = self.screen.get_size()
        return {
            "x": random.uniform(0, W),
            "y": random.uniform(0, H),
            "vx": random.uniform(-15, 15),
            "vy": random.uniform(-15, 15),
            "size": random.randint(2, 5),
            "color": random.choice([
                self.settings.COLOR_PRIMARY,
                self.settings.COLOR_ACCENT,
                self.settings.COLOR_SECONDARY,
            ]),
            "alpha": random.randint(60, 180),
            "life": random.uniform(0.3, 1.0),
        }

    def _build_cards(self):
        W, H = self.screen.get_size()
        card_w = 340
        card_h = 200
        gap    = 40
        total  = card_w * 2 + gap
        cx     = W // 2
        cy     = H // 2 - 30

        self.cards = [
            {
                "id": "debutant",
                "label": "DÉBUTANT",
                "icon": "🎓",
                "desc": "10 niveaux • Notions cyber de base\nEnigmes, images, audio, stégano",
                "color": self.settings.COLOR_PRIMARY,
                "rect": pygame.Rect(cx - total // 2, cy - card_h // 2, card_w, card_h),
                "hover": 0.0,
            },
            {
                "id": "expert",
                "label": "EXPERT",
                "icon": "💀",
                "desc": "6 niveaux • Interface hacker pro\nVrai terminal · CTF · Injection SQL",
                "color": self.settings.COLOR_DANGER,
                "rect": pygame.Rect(cx - total // 2 + card_w + gap, cy - card_h // 2, card_w, card_h),
                "hover": 0.0,
            },
        ]

        # Boutons secondaires
        btn_y = cy + card_h // 2 + 30
        btn_w = 180
        btn_h = 44
        spacing = 20
        total_btns = btn_w * 3 + spacing * 2
        bx = cx - total_btns // 2

        self.side_btns = [
            {"id": "leaderboard", "label": "🏆 Classement",
             "rect": pygame.Rect(bx, btn_y, btn_w, btn_h),
             "color": self.settings.COLOR_WARNING, "hover": 0.0},
            {"id": "guide", "label": "📖 Guide",
             "rect": pygame.Rect(bx + btn_w + spacing, btn_y, btn_w, btn_h),
             "color": self.settings.COLOR_ACCENT, "hover": 0.0},
            {"id": "contact", "label": "✉ Contact",
             "rect": pygame.Rect(bx + (btn_w + spacing) * 2, btn_y, btn_w, btn_h),
             "color": self.settings.COLOR_SECONDARY, "hover": 0.0},
        ]

        # Bouton quitter
        self.btn_quit = {
            "label": "⏻ Quitter",
            "rect": pygame.Rect(W - 130, H - 46, 120, 36),
            "color": (100, 40, 40),
        }
        self.btn_logout = {
            "label": "🔓 Déconnexion",
            "rect": pygame.Rect(10, H - 46, 160, 36),
            "color": (40, 40, 80),
        }

    def run(self) -> Optional[str]:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 0.05)
            self.time_t += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_event(event)

            self._update(dt)
            self._draw()
            pygame.display.flip()

        return self.choice

    def _handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for card in self.cards:
                if card["rect"].collidepoint(pos):
                    self.choice = card["id"]
                    self.running = False
            for btn in self.side_btns:
                if btn["rect"].collidepoint(pos):
                    self.choice = btn["id"]
                    self.running = False
            if self.btn_quit["rect"].collidepoint(pos):
                pygame.quit()
                sys.exit()
            if self.btn_logout["rect"].collidepoint(pos):
                self.auth.logout()
                self.choice = "logout"
                self.running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    def _update(self, dt: float):
        pos = pygame.mouse.get_pos()
        W, H = self.screen.get_size()

        for card in self.cards:
            target = 1.0 if card["rect"].collidepoint(pos) else 0.0
            card["hover"] += (target - card["hover"]) * 10 * dt

        for btn in self.side_btns:
            target = 1.0 if btn["rect"].collidepoint(pos) else 0.0
            btn["hover"] += (target - btn["hover"]) * 10 * dt

        # Particles
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p["x"] < 0 or p["x"] > W or p["y"] < 0 or p["y"] > H:
                p.update(self._make_particle())

    def _draw(self):
        W, H = self.screen.get_size()
        self.screen.fill(self.settings.COLOR_BG)

        self._draw_grid(W, H)
        self._draw_particles()
        self._draw_header(W, H)
        self._draw_cards(W, H)
        self._draw_side_btns()
        self._draw_footer(W, H)

    def _draw_grid(self, W: int, H: int):
        """Grille cyber en arrière-plan."""
        t = self.time_t
        grid_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        spacing = 60
        alpha = int(15 + 5 * math.sin(t * 0.5))
        for x in range(0, W + spacing, spacing):
            pygame.draw.line(grid_surf, (*self.settings.COLOR_PRIMARY, alpha), (x, 0), (x, H))
        for y in range(0, H + spacing, spacing):
            pygame.draw.line(grid_surf, (*self.settings.COLOR_PRIMARY, alpha), (0, y), (W, y))
        self.screen.blit(grid_surf, (0, 0))

    def _draw_particles(self):
        for p in self.particles:
            s = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["color"], p["alpha"]), (p["size"], p["size"]), p["size"])
            self.screen.blit(s, (int(p["x"]) - p["size"], int(p["y"]) - p["size"]))

    def _draw_header(self, W: int, H: int):
        t = self.time_t
        glitch = random.randint(-1, 1) if int(t * 8) % 20 == 0 else 0

        # Logo
        glow = self.font_title.render("h4ckR", True, self.settings.COLOR_PRIMARY)
        glow.set_alpha(50)
        cx = W // 2
        self.screen.blit(glow, glow.get_rect(center=(cx + 4, 58 + 4)))
        title = self.font_title.render("h4ckR", True, self.settings.COLOR_TEXT)
        self.screen.blit(title, title.get_rect(center=(cx + glitch, 58)))

        # Welcome
        welcome = self.font_name.render(
            f"Bienvenue, {self.auth.username} 👾", True, self.settings.COLOR_PRIMARY
        )
        self.screen.blit(welcome, welcome.get_rect(center=(cx, 100)))

        sub = self.font_desc.render("Choisis ton mode de jeu :", True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(sub, sub.get_rect(center=(cx, 128)))

    def _draw_cards(self, W: int, H: int):
        for card in self.cards:
            h = card["hover"]
            r = card["rect"]
            color = card["color"]

            # Shadow (decalé si hover)
            offset_y = -6 if h > 0.5 else 0
            shadow = pygame.Surface((r.w + 10, r.h + 10), pygame.SRCALPHA)
            shadow.fill((*color, int(20 * h)))
            self.screen.blit(shadow, (r.x - 5, r.y - 5 + offset_y))

            # Background
            bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            bg.fill((5, 20, 5, int(160 + 60 * h)))
            self.screen.blit(bg, (r.x, r.y + offset_y))

            # Border glow
            border_alpha = int(100 + 155 * h)
            border_surf = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            pygame.draw.rect(border_surf, (*color, border_alpha), (0, 0, r.w, r.h), 2, border_radius=10)
            self.screen.blit(border_surf, (r.x, r.y + offset_y))

            # Icon
            icon_fnt = pygame.font.SysFont("Segoe UI Emoji", 48)
            icon_surf = icon_fnt.render(card["icon"], True, color)
            self.screen.blit(icon_surf, icon_surf.get_rect(center=(r.centerx, r.y + 55 + offset_y)))

            # Label
            lbl = self.font_card.render(card["label"], True, color if h > 0.3 else self.settings.COLOR_TEXT)
            self.screen.blit(lbl, lbl.get_rect(center=(r.centerx, r.y + 105 + offset_y)))

            # Desc
            for i, line in enumerate(card["desc"].split("\n")):
                d = self.font_desc.render(line, True, self.settings.COLOR_TEXT_DIM)
                d.set_alpha(int(180 + 75 * h))
                self.screen.blit(d, d.get_rect(center=(r.centerx, r.y + 138 + i * 22 + offset_y)))

    def _draw_side_btns(self):
        for btn in self.side_btns:
            h = btn["hover"]
            r = btn["rect"]
            color = btn["color"]

            bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            bg.fill((*color, int(20 + 80 * h)))
            self.screen.blit(bg, r.topleft)
            pygame.draw.rect(self.screen, color, r, 2, border_radius=6)

            lbl = self.font_desc.render(btn["label"], True, self.settings.COLOR_TEXT)
            self.screen.blit(lbl, lbl.get_rect(center=r.center))

    def _draw_footer(self, W: int, H: int):
        for btn_data in [self.btn_quit, self.btn_logout]:
            r = btn_data["rect"]
            bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            bg.fill((*btn_data["color"], 120))
            self.screen.blit(bg, r.topleft)
            pygame.draw.rect(self.screen, btn_data["color"], r, 1, border_radius=4)
            lbl = self.font_small.render(btn_data["label"], True, self.settings.COLOR_TEXT_DIM)
            self.screen.blit(lbl, lbl.get_rect(center=r.center))
