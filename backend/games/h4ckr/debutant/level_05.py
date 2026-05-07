"""Niveau 5 — Stéganographie : texte caché dans une image (pixels LSB)."""
import pygame
import random
from client.games.h4ckr.base_level import BaseLevel
from client.core.settings import Settings

SECRET_WORD = "CYPHER"


class Level05(BaseLevel):
    POINTS_BASE = 120

    def __init__(self, screen, settings):
        super().__init__(screen, settings, 5,
            "🖼️  Stéganographie",
            "Un message est caché dans cette image. Survole les pixels pour trouver l'indice !",
            hint_text="Regarde dans le coin en bas à droite de l'image.\nLes pixels légèrement différents révèlent le message caché.")
        self.img_surf   = None
        self.img_rect   = None
        self.hidden_rects = []
        self.revealed   = [False] * len(SECRET_WORD)
        self.t          = 0.0
        self.input_text = ""
        self.shake      = 0.0
        self._generate_image()

    def _generate_image(self):
        """Génère une image avec le mot caché dans les pixels du coin BR."""
        W, H = self.screen.get_size()
        iw, ih = 500, 320
        surf = pygame.Surface((iw, ih))

        # Fond : dégradé bleu nuit avec noise
        for x in range(iw):
            for y in range(ih):
                noise = random.randint(-8, 8)
                r = max(0, 5  + int(x/iw * 20) + noise)
                g = max(0, 10 + int(y/ih * 15) + noise)
                b = max(0, 40 + int((x+y)/(iw+ih) * 60) + noise)
                surf.set_at((x, y), (r, g, b))

        # Dessiner des "artéfacts" qui ressemblent à du bruit
        for _ in range(2000):
            px = random.randint(0, iw-1)
            py = random.randint(0, ih-1)
            shade = random.randint(20, 80)
            surf.set_at((px, py), (shade, shade+10, shade+30))

        # Cacher les lettres du mot secret dans le coin bas-droit
        zone_w, zone_h = len(SECRET_WORD) * 32 + 10, 32
        zx = iw - zone_w - 10
        zy = ih - zone_h - 10

        fnt_hidden = pygame.font.SysFont("Consolas", 22, bold=True)
        for i, char in enumerate(SECRET_WORD):
            # Couleur très légèrement différente (stégano)
            char_x = zx + i * 32
            # Zone cliquable
            # On dessine le char en couleur proche du fond (quasi-invisible)
            char_surf = fnt_hidden.render(char, True, (18, 25, 68))
            surf.blit(char_surf, (char_x, zy + 4))

        self.img_surf = surf
        self.img_rect = surf.get_rect()

        # Zones de chaque lettre cachée
        self.hidden_rects = []
        for i in range(len(SECRET_WORD)):
            rx = zx + i * 32
            self.hidden_rects.append(pygame.Rect(rx, zy, 30, 30))

    def handle_event(self, event):
        if self._solved: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                if self.input_text.upper().strip() == SECRET_WORD:
                    self._solved = True
                else:
                    self.shake = 0.4
                    self.input_text = ""
            elif event.unicode.isprintable() and len(self.input_text) < 10:
                self.input_text += event.unicode.upper()

    def update(self, dt):
        self.time_spent += dt
        self.t = self.time_spent
        self.shake = max(0.0, self.shake - dt * 4)

        # Détecter survol des zones cachées
        if self.img_rect:
            W, H = self.screen.get_size()
            img_x = (W - self.img_surf.get_width()) // 2
            img_y = 155
            mouse = pygame.mouse.get_pos()
            for i, r in enumerate(self.hidden_rects):
                abs_r = pygame.Rect(img_x + r.x, img_y + r.y, r.w, r.h)
                if abs_r.collidepoint(mouse):
                    self.revealed[i] = True

    def draw(self):
        import math
        W, H = self.screen.get_size()
        self.draw_background()
        self.draw_level_header()

        desc = self.font_small.render(self.description, True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(desc, desc.get_rect(center=(W//2, 130)))

        # Image
        img_x = (W - self.img_surf.get_width()) // 2
        img_y = 155
        self.screen.blit(self.img_surf, (img_x, img_y))
        pygame.draw.rect(self.screen, self.settings.COLOR_PRIMARY,
                         (img_x-2, img_y-2,
                          self.img_surf.get_width()+4,
                          self.img_surf.get_height()+4), 2)

        # Afficher les lettres trouvées au survol
        fnt_reveal = pygame.font.SysFont("Consolas", 22, bold=True)
        for i, revealed in enumerate(self.revealed):
            if revealed:
                rx = img_x + self.hidden_rects[i].x
                ry = img_y + self.hidden_rects[i].y
                # Highlight
                hl = pygame.Surface((30, 30), pygame.SRCALPHA)
                hl.fill((0, 255, 100, 120))
                self.screen.blit(hl, (rx, ry))
                char_s = fnt_reveal.render(SECRET_WORD[i], True, self.settings.COLOR_SUCCESS)
                self.screen.blit(char_s, (rx + 4, ry + 4))

        # Compteur trouvé
        found_count = sum(self.revealed)
        counter = self.font_small.render(
            f"Lettres découvertes : {found_count}/{len(SECRET_WORD)}  — Survole le coin bas-droit !",
            True, self.settings.COLOR_ACCENT
        )
        counter.set_alpha(int(160 + 80 * math.sin(self.t * 2)))
        self.screen.blit(counter, counter.get_rect(center=(W//2, img_y + self.img_surf.get_height() + 16)))

        # Input
        shake_x = int(6 * math.sin(self.t * 30)) if self.shake > 0.1 else 0
        inp_y = img_y + self.img_surf.get_height() + 42
        inp_w, inp_h = 340, 50
        inp_r = pygame.Rect((W-inp_w)//2 + shake_x, inp_y, inp_w, inp_h)
        inp_bg = pygame.Surface((inp_w, inp_h), pygame.SRCALPHA)
        inp_bg.fill((5, 20, 5, 200))
        self.screen.blit(inp_bg, inp_r.topleft)
        bc = self.settings.COLOR_ERROR if self.shake > 0.1 else self.settings.COLOR_PRIMARY
        pygame.draw.rect(self.screen, bc, inp_r, 2, border_radius=6)

        fnt_big = pygame.font.SysFont("Consolas", 24)
        cursor = "▌" if int(self.t * 2) % 2 == 0 else ""
        ts = fnt_big.render(self.input_text + cursor, True, self.settings.COLOR_TEXT)
        self.screen.blit(ts, ts.get_rect(center=inp_r.center))

        h2 = self.font_small.render("Entrez le mot secret + ENTRÉE", True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(h2, h2.get_rect(center=(W//2, inp_y + inp_h + 14)))

        if self._solved:
            self.draw_solved_overlay()
