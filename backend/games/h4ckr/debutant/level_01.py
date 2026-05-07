"""
Niveau 1 — Mot de passe fort
QCM : le joueur doit identifier le mot de passe le plus sécurisé.
"""
import pygame
from client.games.h4ckr.base_level import BaseLevel
from client.core.settings import Settings


PASSWORDS = [
    ("123456",           False, "❌ Trop court, aucun caractère spécial"),
    ("MonChat2024",      False, "⚠️ Pas de caractère spécial"),
    ("P@ssw0rd!2024#Zx", True,  "✅ Long, majuscules, chiffres, symboles"),
    ("password",         False, "❌ Mot commun dans les dictionnaires"),
]


class Level01(BaseLevel):
    POINTS_BASE = 100

    def __init__(self, screen: pygame.Surface, settings: Settings):
        super().__init__(
            screen, settings,
            level_num=1,
            title="🔑 Le Mot de Passe Fort",
            description="Identifie le mot de passe le plus sécurisé parmi les 4 propositions.",
            hint_text="Un bon mot de passe : +12 chars, majuscules, chiffres ET symboles spéciaux.",
        )
        self.selected    = None
        self.answered    = False
        self.feedback    = ""
        self.correct_idx = next(i for i, (_, ok, _) in enumerate(PASSWORDS) if ok)
        self.btn_rects   = []
        self.t           = 0.0

    def handle_event(self, event: pygame.event.Event):
        if self._solved:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.answered:
            for i, r in enumerate(self.btn_rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    self.answered = True
                    pwd, ok, fb   = PASSWORDS[i]
                    self.feedback = fb
                    if ok:
                        self._solved = True

    def update(self, dt: float):
        self.time_spent += dt
        self.t = self.time_spent

    def draw(self):
        W, H = self.screen.get_size()
        self.draw_background()
        self.draw_level_header()

        # Description
        desc = self.font_body.render(self.description, True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(desc, desc.get_rect(center=(W // 2, 130)))

        # Sous-titre règles
        rules = [
            "Un mot de passe fort doit :",
            "• Avoir au moins 12 caractères",
            "• Contenir Majuscules + Minuscules",
            "• Inclure des chiffres (0-9)",
            "• Contenir des symboles (! @ # $ ...)",
        ]
        self.draw_panel(W // 2 - 250, 155, 500, 130, self.settings.COLOR_ACCENT)
        for i, rule in enumerate(rules):
            color = self.settings.COLOR_ACCENT if i == 0 else self.settings.COLOR_TEXT
            rs = self.font_small.render(rule, True, color)
            self.screen.blit(rs, (W // 2 - 235, 165 + i * 22))

        # Boutons de choix
        self.btn_rects = []
        btn_w, btn_h = 560, 54
        start_y = 310
        for i, (pwd, correct, _) in enumerate(PASSWORDS):
            r = pygame.Rect((W - btn_w) // 2, start_y + i * 66, btn_w, btn_h)
            self.btn_rects.append(r)

            # Couleur selon état
            if not self.answered:
                hover = r.collidepoint(pygame.mouse.get_pos())
                col = self.settings.COLOR_PRIMARY if hover else (0, 80, 40)
                alpha = 180 if hover else 100
            else:
                if i == self.correct_idx:
                    col, alpha = self.settings.COLOR_SUCCESS, 200
                elif i == self.selected and not correct:
                    col, alpha = self.settings.COLOR_ERROR, 200
                else:
                    col, alpha = (0, 60, 30), 80

            bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            bg.fill((*col, alpha))
            self.screen.blit(bg, r.topleft)
            pygame.draw.rect(self.screen, col, r, 2, border_radius=6)

            # Texte password monospace
            fnt_mono = pygame.font.SysFont("Consolas", 20)
            ps = fnt_mono.render(pwd, True, self.settings.COLOR_TEXT)
            self.screen.blit(ps, ps.get_rect(midleft=(r.x + 20, r.centery)))

        # Feedback
        if self.feedback:
            fb = self.font_body.render(self.feedback, True,
                self.settings.COLOR_SUCCESS if self._solved else self.settings.COLOR_ERROR)
            self.screen.blit(fb, fb.get_rect(center=(W // 2, start_y + 4 * 66 + 30)))

        if self._solved:
            self.draw_solved_overlay()
