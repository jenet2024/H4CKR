"""Menu principal — choix du niveau, pseudo affiché, stats."""
import pygame
import math
from config import *
from src.utils.renderer import (
    draw_text, draw_button, draw_rect_fill, draw_rect_border,
    MatrixRain, GlitchText, ScanlineOverlay, ProgressBar, get_font,
)
from src.utils.api import api


class MenuScreen:
    def __init__(self, screen):
        self.screen   = screen
        self.w, self.h = screen.get_size()

        self.matrix   = MatrixRain(self.w, self.h, density=30)
        self.title    = GlitchText("H4CKR", self.w // 2 - 90, 30, size=64)
        self.scanline = ScanlineOverlay(self.w, self.h)
        self._t       = 0.0

        self._action  = None   # "beginner" | "expert" | "leaderboard" | "guide" | "contact" | "quit"
        self._mouse   = (0, 0)
        self._badges  = []
        self._points  = 0

        # Boutons
        bw, bh = 340, 56
        cx = self.w // 2
        self._btn_beginner    = pygame.Rect(cx - bw // 2, 280, bw, bh)
        self._btn_expert      = pygame.Rect(cx - bw // 2, 356, bw, bh)
        self._btn_leaderboard = pygame.Rect(cx - bw // 2, 440, bw, bh)
        self._btn_guide       = pygame.Rect(cx - bw // 2, 514, bw, bh)
        self._btn_contact     = pygame.Rect(cx - bw // 2, 588, bw, bh)
        self._btn_quit        = pygame.Rect(cx - bw // 2, 662, bw, 40)

        self._load_stats()

    def _load_stats(self):
        data, code = api.get_my_badges()
        if code == 200:
            self._badges = data
        pts = 0
        lvl_data, code2 = api.get_levels()
        if code2 == 200:
            for lvl in lvl_data:
                for e in lvl.get("enigmas", []):
                    if e.get("solved"):
                        pts += e.get("points", 0)
        self._points = pts

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._mouse = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._on_click(event.pos)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._action = "quit"

    def _on_click(self, pos):
        if self._btn_beginner.collidepoint(pos):
            self._action = "beginner"
        elif self._btn_expert.collidepoint(pos):
            self._action = "expert"
        elif self._btn_leaderboard.collidepoint(pos):
            self._action = "leaderboard"
        elif self._btn_guide.collidepoint(pos):
            self._action = "guide"
        elif self._btn_contact.collidepoint(pos):
            self._action = "contact"
        elif self._btn_quit.collidepoint(pos):
            self._action = "quit"

    def update(self, dt):
        self._t += dt
        self.title.update(dt)
        action = self._action
        self._action = None
        return action

    def draw(self):
        surf = self.screen
        surf.fill(C_BG)
        self.matrix.update(surf)
        self.title.draw(surf)

        draw_text(surf, "HACKING SIMULATION GAME",
                  self.w // 2, 108, C_GREEN_DIM, 14, center=True)

        # ── Carte utilisateur ──────────────────────────────────────────────────
        user = api.user or {}
        pseudo = user.get("pseudo", "AGENT")
        card = pygame.Rect(self.w // 2 - 200, 150, 400, 110)
        pygame.draw.rect(surf, C_BG2, card, border_radius=10)
        pygame.draw.rect(surf, C_GREEN, card, 2, border_radius=10)

        # Avatar cercle
        av_cx, av_cy = card.x + 55, card.centery
        pygame.draw.circle(surf, C_GREEN_DIM, (av_cx, av_cy), 32)
        pygame.draw.circle(surf, C_GREEN, (av_cx, av_cy), 32, 2)
        draw_text(surf, pseudo[:2].upper(), av_cx, av_cy,
                  C_GREEN, 22, bold=True, center=True)

        draw_text(surf, pseudo.upper(), card.x + 100, card.y + 22, C_GREEN, 17, bold=True)
        draw_text(surf, f"POINTS : {self._points}", card.x + 100, card.y + 50, C_WHITE, 14)
        draw_text(surf, f"BADGES : {len(self._badges)}", card.x + 100, card.y + 74, C_YELLOW, 13)

        # Badges icons
        for i, badge in enumerate(self._badges[:5]):
            bx = card.x + 270 + i * 26
            draw_text(surf, badge.get("icon", "?"), bx, card.centery,
                      C_GOLD, 18, center=True)

        # ── Boutons menu ──────────────────────────────────────────────────────
        buttons = [
            (self._btn_beginner,    "▶  NIVEAU DÉBUTANT",    C_GREEN),
            (self._btn_expert,      "▶  NIVEAU EXPERT",      C_RED),
            (self._btn_leaderboard, "⬛  CLASSEMENT",         C_CYAN),
            (self._btn_guide,       "?  GUIDE DU JEU",        C_YELLOW),
            (self._btn_contact,     "✉  NOUS CONTACTER",      C_WHITE),
            (self._btn_quit,        "✕  QUITTER",             C_GRAY),
        ]
        for rect, label, col in buttons:
            hover = rect.collidepoint(self._mouse)
            draw_button(surf, rect, label, color=col, hover=hover)

            # Badge "NOUVEAU" sur expert si débutant complété
            if label.startswith("▶  NIVEAU EXPERT"):
                tag = pygame.Rect(rect.right - 90, rect.y + 6, 82, 22)
                pygame.draw.rect(surf, C_RED, tag, border_radius=4)
                draw_text(surf, "NIVEAU 2", tag.centerx, tag.centery,
                          C_WHITE, 11, bold=True, center=True)

        # ── Décoration latérale ────────────────────────────────────────────────
        for i in range(8):
            y = 200 + i * 70
            blink = abs(math.sin(self._t * 1.5 + i * 0.8))
            col = (int(C_GREEN[0] * blink * 0.4),
                   int(C_GREEN[1] * blink * 0.4),
                   int(C_GREEN[2] * blink * 0.4))
            pygame.draw.rect(surf, col, (40, y, 8, 8), border_radius=2)
            pygame.draw.rect(surf, col, (self.w - 48, y, 8, 8), border_radius=2)

        self.scanline.draw(surf)
