"""Niveau 4 — Reconnaître un hash SHA-256 (QCM avec 4 empreintes)."""
import hashlib
import pygame
from client.games.h4ckr.base_level import BaseLevel
from client.core.settings import Settings

TARGET_WORD = "h4ckR"
CORRECT_HASH = hashlib.sha256(TARGET_WORD.encode()).hexdigest()

CHOICES = [
    ("5d41402abc4b2a76b9719d911017c592", False, "MD5 — seulement 32 hex (128 bits)"),
    (CORRECT_HASH, True, "✅ SHA-256 — 64 hex (256 bits), correct !"),
    ("aaf4c61ddcc5e8a2dabede0f3b482cd9", False, "SHA-1 — seulement 40 hex (160 bits)"),
    ("$2b$12$K8Zx1qy7W9X3vN2mL5P4Oe", False, "bcrypt — format spécial avec $, non hex pur"),
]


class Level04(BaseLevel):
    POINTS_BASE = 100

    def __init__(self, screen, settings):
        super().__init__(screen, settings, 4,
            "#  Le Hash SHA-256",
            f"Trouve le hash SHA-256 correct du mot '{TARGET_WORD}'",
            hint_text="SHA-256 produit exactement 64 caractères hexadécimaux (0-9, a-f).\nIl commence souvent par des chiffres et lettres minuscules.")
        self.selected = None
        self.answered = False
        self.btn_rects = []
        self.t = 0.0

    def handle_event(self, event):
        if self._solved: return
        if event.type == pygame.MOUSEBUTTONDOWN and not self.answered:
            for i, r in enumerate(self.btn_rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    self.answered = True
                    if CHOICES[i][1]:
                        self._solved = True

    def update(self, dt):
        self.time_spent += dt
        self.t = self.time_spent

    def draw(self):
        W, H = self.screen.get_size()
        self.draw_background()
        self.draw_level_header()

        desc = self.font_body.render(self.description, True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(desc, desc.get_rect(center=(W//2, 130)))

        # Info panel
        self.draw_panel(W//2-320, 152, 640, 75, self.settings.COLOR_ACCENT)
        info = [
            "Un hash cryptographique transforme n'importe quel texte",
            "en une empreinte de taille fixe. SHA-256 → 64 caractères hex.",
            f"Mot ciblé : '{TARGET_WORD}'",
        ]
        for i, line in enumerate(info):
            c = self.settings.COLOR_ACCENT if i == 2 else self.settings.COLOR_TEXT_DIM
            s = self.font_small.render(line, True, c)
            self.screen.blit(s, (W//2-305, 160 + i*22))

        # Boutons choix hash
        self.btn_rects = []
        fnt_mono = pygame.font.SysFont("Consolas", 12)
        btn_w, btn_h = 700, 65
        start_y = 252

        for i, (h_val, correct, explanation) in enumerate(CHOICES):
            r = pygame.Rect((W-btn_w)//2, start_y + i*78, btn_w, btn_h)
            self.btn_rects.append(r)

            if not self.answered:
                hover = r.collidepoint(pygame.mouse.get_pos())
                col = self.settings.COLOR_PRIMARY if hover else (0, 50, 25)
                alpha = 170 if hover else 90
            else:
                if correct:
                    col, alpha = self.settings.COLOR_SUCCESS, 200
                elif i == self.selected and not correct:
                    col, alpha = self.settings.COLOR_ERROR, 200
                else:
                    col, alpha = (0, 30, 15), 60

            bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            bg.fill((*col, alpha))
            self.screen.blit(bg, r.topleft)
            pygame.draw.rect(self.screen, col, r, 2, border_radius=4)

            # Hash value (petite police monospace)
            hash_surf = fnt_mono.render(h_val[:72], True, self.settings.COLOR_TEXT)
            self.screen.blit(hash_surf, (r.x+10, r.y+10))

            # Longueur
            len_s = self.font_small.render(f"Longueur : {len(h_val)} chars", True, self.settings.COLOR_TEXT_DIM)
            self.screen.blit(len_s, (r.x+10, r.y+32))

            # Explication si répondu
            if self.answered:
                ex = self.font_small.render(explanation, True,
                    self.settings.COLOR_SUCCESS if correct else self.settings.COLOR_TEXT_DIM)
                self.screen.blit(ex, (r.x+10, r.y+48))

        if self._solved:
            self.draw_solved_overlay()
