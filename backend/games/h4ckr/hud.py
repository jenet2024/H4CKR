"""
HUD h4ckR — affiche : niveau, points, timer, indice, barre de progression.
"""
import math
import pygame
from client.core.settings import Settings


class GameHUD:
    def __init__(self, screen: pygame.Surface, settings: Settings,
                 mode: str, total_levels: int, session_id: int = None):
        self.screen       = screen
        self.settings     = settings
        self.mode         = mode          # "debutant" | "expert"
        self.total_levels = total_levels
        self.session_id   = session_id

        self.current_level = 1
        self.score         = 0
        self.hint_used     = False
        self.elapsed       = 0.0
        self.hint_alpha    = 0.0
        self.hint_text     = ""

        self.font_hud   = settings.load_font(16)
        self.font_score = settings.load_font(22)
        self.font_hint  = settings.load_font(14)

        self.col = settings.COLOR_PRIMARY if mode == "debutant" else settings.COLOR_DANGER

    def update(self, dt: float):
        self.elapsed += dt
        if self.hint_alpha > 0:
            self.hint_alpha = max(0.0, self.hint_alpha - dt * 0.3)

    def show_hint(self, text: str):
        self.hint_text  = text
        self.hint_alpha = 1.0
        self.hint_used  = True

    def add_points(self, pts: int):
        self.score += pts

    def draw(self):
        W, H = self.screen.get_size()
        t = self.elapsed

        # ── Top bar ──────────────────────────────────────────────────────────────
        bar = pygame.Surface((W, 46), pygame.SRCALPHA)
        bar.fill((4, 12, 4, 210))
        self.screen.blit(bar, (0, 0))
        pygame.draw.line(self.screen, self.col, (0, 46), (W, 46), 1)

        # Mode badge
        mode_txt = "DÉBUTANT" if self.mode == "debutant" else "EXPERT"
        mode_surf = self.font_hud.render(f"[ {mode_txt} ]", True, self.col)
        self.screen.blit(mode_surf, (10, 14))

        # Niveau
        lvl_txt = f"NIVEAU {self.current_level}/{self.total_levels}"
        lvl_surf = self.font_hud.render(lvl_txt, True, self.settings.COLOR_ACCENT)
        self.screen.blit(lvl_surf, lvl_surf.get_rect(midleft=(180, 23)))

        # Score
        score_surf = self.font_score.render(f"◆ {self.score:,} pts", True, self.settings.COLOR_WARNING)
        self.screen.blit(score_surf, score_surf.get_rect(center=(W // 2, 23)))

        # Timer
        mins = int(self.elapsed) // 60
        secs = int(self.elapsed) % 60
        timer_col = self.settings.COLOR_DANGER if mins >= 25 else self.settings.COLOR_TEXT_DIM
        timer_surf = self.font_hud.render(f"⏱ {mins:02d}:{secs:02d}", True, timer_col)
        self.screen.blit(timer_surf, timer_surf.get_rect(midright=(W - 120, 23)))

        # Hint button
        hint_btn_r = pygame.Rect(W - 105, 8, 95, 30)
        hint_bg = pygame.Surface((95, 30), pygame.SRCALPHA)
        hint_bg.fill((50, 50, 0, 160))
        self.screen.blit(hint_bg, hint_btn_r.topleft)
        pygame.draw.rect(self.screen, self.settings.COLOR_WARNING, hint_btn_r, 1, border_radius=4)
        h_lbl = self.font_hint.render("💡 INDICE", True, self.settings.COLOR_WARNING)
        self.screen.blit(h_lbl, h_lbl.get_rect(center=hint_btn_r.center))

        # ── Barre de progression ──────────────────────────────────────────────────
        prog_y = H - 8
        bar_w  = W - 40
        bar_h  = 5
        filled = int(bar_w * (self.current_level - 1) / self.total_levels)

        bg_bar = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        bg_bar.fill((0, 60, 0, 120))
        self.screen.blit(bg_bar, (20, prog_y))

        if filled > 0:
            fill_surf = pygame.Surface((filled, bar_h), pygame.SRCALPHA)
            fill_surf.fill((*self.col, 220))
            self.screen.blit(fill_surf, (20, prog_y))

        pygame.draw.rect(self.screen, self.col, (20, prog_y, bar_w, bar_h), 1)

        # Marqueurs milestones débutant
        if self.mode == "debutant":
            mid_x = 20 + bar_w // 2
            pygame.draw.rect(self.screen, self.settings.COLOR_WARNING,
                             (mid_x - 1, prog_y - 4, 2, bar_h + 8))

        # ── Hint tooltip ──────────────────────────────────────────────────────────
        if self.hint_alpha > 0.01 and self.hint_text:
            alpha = int(self.hint_alpha * 220)
            lines = self.hint_text.split("\n")
            box_h = len(lines) * 24 + 16
            box_w = 500
            box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            box.fill((10, 30, 10, 200))
            pygame.draw.rect(box, (255, 190, 50, alpha), (0, 0, box_w, box_h), 2, border_radius=6)
            for i, line in enumerate(lines):
                ls = self.font_hint.render(f"💡 {line}", True, (255, 230, 120))
                box.blit(ls, (12, 8 + i * 24))
            box.set_alpha(alpha)
            self.screen.blit(box, box.get_rect(center=(W // 2, H // 2 + 160)))

    def get_hint_button_rect(self) -> pygame.Rect:
        W, _ = self.screen.get_size()
        return pygame.Rect(W - 105, 8, 95, 30)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.get_hint_button_rect().collidepoint(event.pos)
        return False
