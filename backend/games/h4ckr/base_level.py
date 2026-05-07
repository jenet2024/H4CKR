"""Classe de base pour tous les niveaux h4ckR."""
import pygame
from abc import ABC, abstractmethod
from client.core.settings import Settings


class BaseLevel(ABC):
    """
    Tous les niveaux héritent de cette classe.
    Gestion unifiée : solved, points, hint, dessin de fond.
    """
    POINTS_BASE = 100   # overridable par niveau

    def __init__(self, screen: pygame.Surface, settings: Settings,
                 level_num: int, title: str, description: str,
                 hint_text: str = "Aucun indice disponible."):
        self.screen      = screen
        self.settings    = settings
        self.level_num   = level_num
        self.title       = title
        self.description = description
        self.hint_text   = hint_text
        self._solved     = False
        self.time_spent  = 0.0

        self.font_title = settings.load_font(26)
        self.font_body  = settings.load_font(16)
        self.font_small = settings.load_font(14)
        self.font_input = settings.load_font(20)

    @abstractmethod
    def handle_event(self, event: pygame.event.Event): ...

    @abstractmethod
    def update(self, dt: float): ...

    @abstractmethod
    def draw(self): ...

    def is_solved(self) -> bool:
        return self._solved

    def get_hint(self) -> str:
        return self.hint_text

    def get_points(self) -> int:
        return self.POINTS_BASE

    def draw_background(self):
        """Fond commun : gradient sombre + grid."""
        W, H = self.screen.get_size()
        self.screen.fill(self.settings.COLOR_BG)
        # Subtle grid
        import math
        t = self.time_spent
        gs = pygame.Surface((W, H), pygame.SRCALPHA)
        for x in range(0, W, 40):
            a = int(6 + 3 * math.sin(t * 0.4 + x / 80))
            pygame.draw.line(gs, (*self.settings.COLOR_PRIMARY, a), (x, 0), (x, H))
        for y in range(0, H, 40):
            a = int(6 + 3 * math.sin(t * 0.4 + y / 80))
            pygame.draw.line(gs, (*self.settings.COLOR_PRIMARY, a), (0, y), (W, y))
        self.screen.blit(gs, (0, 0))

    def draw_level_header(self, color: tuple = None):
        """Bandeau de titre du niveau."""
        W, _ = self.screen.get_size()
        col  = color or self.settings.COLOR_PRIMARY
        bar  = pygame.Surface((W, 56), pygame.SRCALPHA)
        bar.fill((0, 20, 0, 180))
        self.screen.blit(bar, (0, 48))
        pygame.draw.line(self.screen, col, (0, 104), (W, 104), 1)

        num_surf = self.font_small.render(f"NIVEAU {self.level_num}", True, col)
        self.screen.blit(num_surf, (14, 58))
        title_surf = self.font_title.render(self.title, True, self.settings.COLOR_TEXT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(W // 2, 80)))

    def draw_panel(self, x: int, y: int, w: int, h: int, color: tuple = None, alpha: int = 190):
        """Panneau glassmorphism général."""
        col  = color or self.settings.COLOR_PRIMARY
        bg   = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((5, 18, 5, alpha))
        self.screen.blit(bg, (x, y))
        border = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(border, (*col, 160), (0, 0, w, h), 2, border_radius=8)
        self.screen.blit(border, (x, y))

    def draw_solved_overlay(self):
        """Overlay 'RÉSOLU !' quand un niveau est terminé."""
        W, H = self.screen.get_size()
        import math
        t = self.time_spent
        alpha = min(220, int(180 + 40 * math.sin(t * 4)))
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 40, 0, 80))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 440, 100
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((0, 30, 0, 210))
        pygame.draw.rect(box, (*self.settings.COLOR_SUCCESS, 220), (0, 0, box_w, box_h), 2, border_radius=10)
        self.screen.blit(box, box.get_rect(center=(W // 2, H // 2 + 60)))

        ok = self.font_title.render("✓ NIVEAU RÉUSSI !", True, self.settings.COLOR_SUCCESS)
        self.screen.blit(ok, ok.get_rect(center=(W // 2, H // 2 + 60 - 14)))
        hint = self.font_small.render("[ ESPACE pour continuer ]", True, self.settings.COLOR_TEXT_DIM)
        hint.set_alpha(alpha)
        self.screen.blit(hint, hint.get_rect(center=(W // 2, H // 2 + 60 + 22)))
