"""Niveau 3 — Chiffrement César : déchiffrer un message."""
import pygame
from client.games.h4ckr.base_level import BaseLevel
from client.core.settings import Settings

SECRET  = "HACKEZ LE SYSTEME"
SHIFT   = 13
CIPHER  = "".join(
    chr((ord(c) - 65 + SHIFT) % 26 + 65) if c.isalpha() else c
    for c in SECRET
)


class Level03(BaseLevel):
    POINTS_BASE = 100

    def __init__(self, screen, settings):
        super().__init__(screen, settings, 3,
            "🔐 Le Chiffre César",
            f"Décryptez ce message (décalage : {SHIFT}). Entrez la réponse :",
            hint_text=f"César ROT-{SHIFT} : chaque lettre est décalée de {SHIFT} positions.\n"
                      f"A→{'chr(65+SHIFT)'}, B→... Essayez de décaler en sens inverse !")
        self.input_text = ""
        self.shake      = 0.0
        self.t          = 0.0

    def handle_event(self, event):
        if self._solved: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                if self.input_text.upper().strip() == SECRET:
                    self._solved = True
                else:
                    self.shake = 0.4
            elif event.unicode.isprintable() and len(self.input_text) < 30:
                self.input_text += event.unicode.upper()

    def update(self, dt):
        self.time_spent += dt
        self.t = self.time_spent
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt * 4)

    def draw(self):
        W, H = self.screen.get_size()
        import math, random
        self.draw_background()
        self.draw_level_header()

        # Description
        d = self.font_body.render(self.description, True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(d, d.get_rect(center=(W//2, 132)))

        # Explication
        info_lines = [
            "Le chiffrement de César remplace chaque lettre par celle qui est",
            f"décalée de {SHIFT} positions dans l'alphabet.",
            "ROT-13 : A=N, B=O, C=P, ...  DECRYPTEZ EN SENS INVERSE !",
        ]
        self.draw_panel(W//2-340, 150, 680, 80)
        for i, line in enumerate(info_lines):
            col = self.settings.COLOR_ACCENT if i == 2 else self.settings.COLOR_TEXT_DIM
            s = self.font_small.render(line, True, col)
            self.screen.blit(s, (W//2-325, 160 + i*24))

        # Alphabet reference
        alpha_y = 250
        self.draw_panel(W//2-340, alpha_y, 680, 50)
        ref = "A→N  B→O  C→P  D→Q  E→R  F→S  G→T  H→U  I→V  J→W  K→X  L→Y  M→Z"
        fnt = pygame.font.SysFont("Consolas", 14)
        rs = fnt.render(ref, True, (0, 180, 0))
        self.screen.blit(rs, rs.get_rect(center=(W//2, alpha_y+25)))

        # Message chiffré
        msg_y = 320
        self.draw_panel(W//2-300, msg_y, 600, 60, self.settings.COLOR_WARNING)
        lbl = self.font_small.render("MESSAGE CHIFFRÉ :", True, self.settings.COLOR_WARNING)
        self.screen.blit(lbl, (W//2-285, msg_y+6))
        fnt_big = pygame.font.SysFont("Consolas", 28, bold=True)
        cipher_surf = fnt_big.render(CIPHER, True, self.settings.COLOR_TEXT)
        self.screen.blit(cipher_surf, cipher_surf.get_rect(center=(W//2, msg_y+44)))

        # Input zone
        shake_x = int(8 * math.sin(self.t * 30)) if self.shake > 0.1 else 0
        inp_y = 420
        inp_w, inp_h = 500, 54
        inp_r = pygame.Rect((W-inp_w)//2 + shake_x, inp_y, inp_w, inp_h)
        inp_bg = pygame.Surface((inp_w, inp_h), pygame.SRCALPHA)
        inp_bg.fill((5, 25, 5, 200))
        self.screen.blit(inp_bg, inp_r.topleft)
        border_col = self.settings.COLOR_ERROR if self.shake > 0.1 else self.settings.COLOR_PRIMARY
        pygame.draw.rect(self.screen, border_col, inp_r, 2, border_radius=6)

        cursor = "▌" if int(self.t * 2) % 2 == 0 else ""
        display = self.input_text + cursor
        inp_surf = fnt_big.render(display, True, self.settings.COLOR_TEXT)
        self.screen.blit(inp_surf, inp_surf.get_rect(center=inp_r.center))

        lbl2 = self.font_small.render("Tapez votre réponse et appuyez sur ENTRÉE", True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(lbl2, lbl2.get_rect(center=(W//2, inp_y+70)))

        if self._solved:
            self.draw_solved_overlay()
