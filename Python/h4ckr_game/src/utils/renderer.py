"""
Utilitaires de rendu Pygame.
Fournit tous les composants UI utilisés dans les écrans :
draw_text, draw_button, draw_input, MatrixRain, GlitchText, ScanlineOverlay,
ProgressBar, Notification, draw_text_wrapped, get_font.
"""
import pygame
import math
import random
import time
from config import *


# ── Font ──────────────────────────────────────────────────────────────────────

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Retourne une police monospace à la taille donnée."""
    name = pygame.font.match_font(
        "couriernew,courier,dejavusansmono,monospace,liberationmono"
    )
    try:
        return pygame.font.Font(name, size)
    except Exception:
        return pygame.font.SysFont(FONT_MONO, size, bold=bold)


# ── Texte ─────────────────────────────────────────────────────────────────────

def draw_text(surf, text: str, x, y, color, size: int = 14,
              bold: bool = False, center: bool = False) -> pygame.Rect:
    """Affiche une ligne de texte. Si center=True, x est le centre horizontal."""
    font = get_font(size, bold)
    s    = font.render(str(text), True, color)
    if center:
        rect = s.get_rect(centerx=x, top=y)
    else:
        rect = s.get_rect(topleft=(x, y))
    surf.blit(s, rect)
    return rect


def draw_text_wrapped(surf, text: str, x, y, max_width: int,
                      color, size: int = 14, line_height: int = 22) -> int:
    """Affiche du texte avec retour à la ligne automatique. Retourne le y final."""
    font  = get_font(size)
    words = text.split()
    lines = []
    cur   = ""
    for word in words:
        test = (cur + " " + word).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)

    for i, line in enumerate(lines):
        surf.blit(font.render(line, True, color), (x, y + i * line_height))
    return y + len(lines) * line_height


# ── Rectangles ────────────────────────────────────────────────────────────────

def draw_rect_fill(surf, rect: pygame.Rect, color, radius: int = 6):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def draw_rect_border(surf, rect: pygame.Rect, color, width: int = 1, radius: int = 6):
    pygame.draw.rect(surf, color, rect, width, border_radius=radius)


def draw_glow_rect(surf, rect: pygame.Rect, color, glow: int = 10, radius: int = 8):
    """Dessine un rectangle avec halo lumineux."""
    glow_surf = pygame.Surface((rect.w + glow * 2, rect.h + glow * 2), pygame.SRCALPHA)
    for i in range(glow, 0, -3):
        alpha = int(70 * (i / glow))
        c = (*color[:3], alpha)
        pygame.draw.rect(
            glow_surf, c,
            (glow - i, glow - i, rect.w + i * 2, rect.h + i * 2),
            border_radius=radius + i,
        )
    surf.blit(glow_surf, (rect.x - glow, rect.y - glow))
    pygame.draw.rect(surf, C_BG2, rect, border_radius=radius)
    pygame.draw.rect(surf, color, rect, 1, border_radius=radius)


# ── Bouton ────────────────────────────────────────────────────────────────────

def draw_button(surf, rect: pygame.Rect, label: str,
                color=None, hover: bool = False,
                size: int = 14, bold: bool = False) -> bool:
    """
    Dessine un bouton et retourne True si la souris est dessus.
    color : couleur de la bordure/texte (défaut C_GREEN).
    """
    if color is None:
        color = C_GREEN

    bg_color = (20, 50, 20) if hover else (10, 25, 10)
    pygame.draw.rect(surf, bg_color, rect, border_radius=8)

    if hover:
        draw_glow_rect(surf, rect, color, glow=8)
    else:
        pygame.draw.rect(surf, color, rect, 1, border_radius=8)

    font = get_font(size, bold)
    txt  = font.render(label, True, color)
    surf.blit(txt, txt.get_rect(center=rect.center))

    return hover


# ── Champ de saisie ───────────────────────────────────────────────────────────

def draw_input(surf, rect: pygame.Rect, value: str,
               label: str = "", active: bool = False,
               placeholder: str = "", password: bool = False,
               error: bool = False):
    """Dessine un champ de saisie avec label au-dessus."""
    border_color = C_RED if error else (C_GREEN if active else C_BORDER)
    bg_color     = (15, 32, 15) if active else (8, 18, 8)

    # Label
    if label:
        font_lbl = get_font(11)
        surf.blit(font_lbl.render(label, True, C_GREEN_MID if active else C_GRAY),
                  (rect.x, rect.y - 16))

    pygame.draw.rect(surf, bg_color, rect, border_radius=6)
    if active:
        draw_glow_rect(surf, rect, border_color, glow=6)
    else:
        pygame.draw.rect(surf, border_color, rect, 1, border_radius=6)

    display = "*" * len(value) if password else value
    font    = get_font(14)

    if display:
        txt_surf = font.render(display, True, C_WHITE)
    else:
        txt_surf = font.render(placeholder, True, C_GRAY)

    # Clip + affichage texte
    clip = pygame.Rect(rect.x + 10, rect.y, rect.w - 20, rect.h)
    surf.set_clip(clip)
    surf.blit(txt_surf, (rect.x + 10, rect.y + (rect.h - txt_surf.get_height()) // 2))
    surf.set_clip(None)

    # Curseur clignotant
    if active and int(time.time() * 2) % 2 == 0:
        cx = rect.x + 10 + font.size(display)[0] + 2
        cy = rect.centery
        pygame.draw.line(surf, C_GREEN, (cx, cy - 10), (cx, cy + 10), 2)


# ── Progress bar ──────────────────────────────────────────────────────────────

class ProgressBar:
    def __init__(self, x, y, width, height,
                 color=None, bg=None):
        self.rect  = pygame.Rect(x, y, width, height)
        self.color = color or C_GREEN
        self.bg    = bg    or C_DARK
        self._val  = 0.0

    def set_value(self, v: float):
        self._val = max(0.0, min(1.0, v))

    def draw(self, surf):
        pygame.draw.rect(surf, self.bg,    self.rect, border_radius=4)
        if self._val > 0:
            fill = pygame.Rect(self.rect.x, self.rect.y,
                               int(self.rect.w * self._val), self.rect.h)
            pygame.draw.rect(surf, self.color, fill, border_radius=4)
        pygame.draw.rect(surf, C_BORDER, self.rect, 1, border_radius=4)
        pct = int(self._val * 100)
        font = get_font(10)
        lbl  = font.render(f"{pct}%", True, self.color)
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))


# ── Notification flottante ────────────────────────────────────────────────────

class Notification:
    def __init__(self, message: str, color=None, duration: float = 3.0):
        self.message  = message
        self.color    = color or C_GREEN
        self.duration = duration
        self._t       = 0.0
        self.done     = False

    def update(self, dt):
        self._t += dt
        if self._t >= self.duration:
            self.done = True

    def draw(self, surf, cx, y):
        """Affiche la notification centrée horizontalement en (cx, y)."""
        alpha = 255
        if self._t > self.duration - 0.5:
            alpha = int(255 * (self.duration - self._t) / 0.5)

        font    = get_font(14, bold=True)
        txt     = font.render(self.message, True, self.color)
        padding = 16
        w = txt.get_width() + padding * 2
        h = txt.get_height() + 12

        notif = pygame.Surface((w, h), pygame.SRCALPHA)
        notif.fill((*C_BG2, min(alpha, 220)))
        border = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(border, (*self.color[:3], alpha), border.get_rect(),
                         2, border_radius=8)
        notif.blit(border, (0, 0))
        notif.blit(txt, (padding, 6))
        surf.blit(notif, (cx - w // 2, y))


# ── Matrix rain ───────────────────────────────────────────────────────────────

class MatrixRain:
    """Effet pluie de caractères style Matrix."""
    CHARS = "01ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@#$%&><|/\\"

    def __init__(self, w: int, h: int, density: int = 40):
        self.w = w
        self.h = h
        col_w  = 18
        n_cols  = max(1, w // col_w)
        self.columns = []
        for i in range(n_cols):
            self.columns.append({
                "x":     i * col_w + random.randint(0, col_w),
                "y":     random.randint(-h, 0),
                "speed": random.uniform(60, 180),
                "chars": [random.choice(self.CHARS) for _ in range(20)],
                "len":   random.randint(6, 20),
                "t":     0.0,
            })
        self._font = None
        self._dt   = 0.0

    def _get_font(self):
        if self._font is None:
            self._font = get_font(14)
        return self._font

    def update(self, surf):
        font = self._get_font()
        dt   = 1 / 60

        for col in self.columns:
            col["y"]  += col["speed"] * dt
            col["t"]  += dt
            if col["t"] > 0.1:
                col["t"] = 0
                col["chars"] = [random.choice(self.CHARS)
                                 for _ in range(col["len"])]

            if col["y"] > self.h + 200:
                col["y"]     = random.randint(-200, -20)
                col["speed"] = random.uniform(60, 180)
                col["len"]   = random.randint(6, 20)

            for j, ch in enumerate(col["chars"][:col["len"]]):
                cy = int(col["y"]) - j * 18
                if cy < 0 or cy > self.h:
                    continue
                if j == 0:
                    color = (200, 255, 200)   # tête brillante
                elif j < 3:
                    color = C_GREEN
                else:
                    alpha_factor = 1 - j / col["len"]
                    color = (int(C_GREEN_DIM[0] * alpha_factor),
                             int(C_GREEN_DIM[1] * alpha_factor),
                             int(C_GREEN_DIM[2] * alpha_factor))

                s = font.render(ch, True, color)
                surf.blit(s, (col["x"], cy))


# ── Glitch text ───────────────────────────────────────────────────────────────

class GlitchText:
    """Titre animé avec effet glitch périodique."""
    def __init__(self, text: str, x: int, y: int, size: int = 48, color=None):
        self.text  = text
        self.x     = x
        self.y     = y
        self.size  = size
        self.color = color or C_GREEN
        self._t     = 0.0
        self._glitch_t = 0.0
        self._glitching = False

    def update(self, dt):
        self._t        += dt
        self._glitch_t += dt
        if self._glitch_t > random.uniform(3.0, 5.0):
            self._glitching = True
            self._glitch_t  = 0.0
        if self._glitching and self._glitch_t > 0.12:
            self._glitching = False

    def draw(self, surf):
        font = get_font(self.size, bold=True)

        if self._glitching:
            # Canal rouge décalé
            r_surf = font.render(self.text, True, (255, 0, 60))
            surf.blit(r_surf, (self.x + random.randint(-4, 4),
                                self.y + random.randint(-2, 2)))
            # Canal cyan décalé
            c_surf = font.render(self.text, True, (0, 200, 255))
            surf.blit(c_surf, (self.x + random.randint(-4, 4),
                                self.y + random.randint(-2, 2)))

        # Texte principal
        txt_surf = font.render(self.text, True, self.color)
        surf.blit(txt_surf, (self.x, self.y))

        # Lueur pulsée
        glow_alpha = int(abs(math.sin(self._t * 1.5)) * 60 + 20)
        glow_surf  = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
        glow_surf.fill((*self.color[:3], glow_alpha))
        surf.blit(glow_surf, (self.x, self.y), special_flags=pygame.BLEND_ADD)


# ── Scanline overlay ──────────────────────────────────────────────────────────

class ScanlineOverlay:
    """Effet scanlines CRT à superposer sur l'écran."""
    def __init__(self, w: int, h: int, alpha: int = 18):
        self._surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 4):
            pygame.draw.line(self._surf, (0, 0, 0, alpha), (0, y), (w, y))
        # Vignette sur les bords
        for i in range(30):
            a = int(80 * (1 - i / 30))
            pygame.draw.rect(self._surf, (0, 0, 0, a), (i, i, w - i * 2, h - i * 2), 1)

    def draw(self, surf):
        surf.blit(self._surf, (0, 0))
