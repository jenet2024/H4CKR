"""
Niveau 2 — Phishing
Affiche un faux email. Le joueur doit cliquer sur les zones suspectes.
"""
import pygame
from client.games.h4ckr.base_level import BaseLevel
from client.core.settings import Settings


# Zones suspectes (x_rel, y_rel, w, h, description)
SUSPICIOUS_ZONES = [
    (0.08, 0.25, 0.45, 0.035, "Expéditeur : adresse falsifiée !"),
    (0.05, 0.60, 0.90, 0.035, "Lien suspect : URL ne correspond pas à PayPal !"),
    (0.30, 0.75, 0.40, 0.05,  "Bouton : dirige vers un site malveillant"),
]

EMAIL_LINES = [
    ("", ""),
    ("De :", "service@paypa1-securite.com"),
    ("À :", "vous@email.com"),
    ("Objet :", "⚠ URGENT : Votre compte a été compromis !"),
    ("", ""),
    ("Cher(e) client(e),", ""),
    ("", ""),
    ("Nous avons détecté une activité suspecte sur votre compte.", ""),
    ("Cliquez immédiatement sur le lien ci-dessous", ""),
    ("pour vérifier votre identité :", ""),
    ("", ""),
    ("→ http://paypa1-secure-login.ru/verify", ""),
    ("", ""),
    ("  [ VÉRIFIER MON COMPTE ]  ", "BUTTON"),
]


class Level02(BaseLevel):
    POINTS_BASE = 100

    def __init__(self, screen: pygame.Surface, settings: Settings):
        super().__init__(
            screen, settings,
            level_num=2,
            title="📧 Détection de Phishing",
            description="Clique sur TOUTES les zones suspectes de cet email.",
            hint_text="Vérifie l'adresse email de l'expéditeur, l'URL du lien\net le bouton d'action.",
        )
        self.found   = set()
        self.rects   = []
        self.t       = 0.0
        self.msg     = ""

    def handle_event(self, event: pygame.event.Event):
        if self._solved:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, r in enumerate(self.rects):
                if r.collidepoint(pos):
                    self.found.add(i)
                    self.msg = f"🔍 {SUSPICIOUS_ZONES[i][4]}"
            if len(self.found) >= len(SUSPICIOUS_ZONES):
                self._solved = True
                self.msg = "✅ Tu as identifié toutes les zones suspectes !"

    def update(self, dt: float):
        self.time_spent += dt
        self.t = self.time_spent

    def draw(self):
        W, H = self.screen.get_size()
        self.draw_background()
        self.draw_level_header()

        desc = self.font_small.render(
            self.description + f"  ({len(self.found)}/{len(SUSPICIOUS_ZONES)} trouvées)",
            True, self.settings.COLOR_TEXT_DIM
        )
        self.screen.blit(desc, desc.get_rect(center=(W // 2, 130)))

        # Email panel
        ew, eh = 700, 380
        ex, ey = (W - ew) // 2, 150
        self.draw_panel(ex, ey, ew, eh, (200, 200, 200))

        # En-tête email
        eh_bar = pygame.Surface((ew, 30), pygame.SRCALPHA)
        eh_bar.fill((200, 200, 200, 40))
        self.screen.blit(eh_bar, (ex, ey))
        hdr = self.font_small.render("📬  Boîte de réception — h4ckR Mail", True, (150, 150, 150))
        self.screen.blit(hdr, (ex + 8, ey + 8))

        fnt_mono = pygame.font.SysFont("Consolas", 16)
        fnt_btn  = pygame.font.SysFont("Consolas", 18, bold=True)

        self.rects = []
        y_cur = ey + 38
        for label, value in EMAIL_LINES:
            if value == "BUTTON":
                r_abs = pygame.Rect(ex + 220, y_cur - 2, 260, 30)
                self.rects.append(r_abs)
                # Check for this zone
                zone_idx = 2
                found_k = zone_idx in self.found
                bt_col = self.settings.COLOR_DANGER if found_k else (50, 120, 200)
                bt_bg  = pygame.Surface((260, 30), pygame.SRCALPHA)
                bt_bg.fill((*bt_col, 200))
                self.screen.blit(bt_bg, (ex + 220, y_cur - 2))
                bt_txt = fnt_btn.render(label, True, (255, 255, 255))
                self.screen.blit(bt_txt, bt_txt.get_rect(center=(ex + 350, y_cur + 13)))
                y_cur += 36
            else:
                line_txt = f"{label}  {value}" if label else value
                # Colorier les lignes suspectes en rouge si trouvées
                col = self.settings.COLOR_TEXT
                if "paypa1" in line_txt.lower() and 0 in self.found:
                    col = self.settings.COLOR_DANGER
                elif "paypa1-secure-login" in line_txt.lower() and 1 in self.found:
                    col = self.settings.COLOR_DANGER
                elif "URGENT" in line_txt:
                    col = self.settings.COLOR_WARNING

                s = fnt_mono.render(line_txt, True, col)
                self.screen.blit(s, (ex + 10, y_cur))

                # Ajouter rect pour l'expéditeur et le lien
                if "paypa1-securite" in line_txt:
                    r = pygame.Rect(ex + 10, y_cur - 2, ew - 20, 22)
                    self.rects.append(r)
                    if 0 in self.found:
                        pygame.draw.rect(self.screen, self.settings.COLOR_DANGER, r, 2, border_radius=3)
                elif "paypa1-secure-login" in line_txt:
                    r = pygame.Rect(ex + 10, y_cur - 2, ew - 20, 22)
                    self.rects.append(r)
                    if 1 in self.found:
                        pygame.draw.rect(self.screen, self.settings.COLOR_DANGER, r, 2, border_radius=3)

                y_cur += 22

        # Instructions hover
        hover_txt = self.font_small.render("👆 Clique sur les zones suspectes", True, self.settings.COLOR_ACCENT)
        hover_txt.set_alpha(int(150 + 80 * abs(__import__('math').sin(self.t * 2))))
        self.screen.blit(hover_txt, hover_txt.get_rect(center=(W // 2, ey + eh + 18)))

        # Message feedback
        if self.msg:
            fb_col = self.settings.COLOR_SUCCESS if self._solved else self.settings.COLOR_WARNING
            fb = self.font_body.render(self.msg, True, fb_col)
            self.screen.blit(fb, fb.get_rect(center=(W // 2, ey + eh + 42)))

        if self._solved:
            self.draw_solved_overlay()
