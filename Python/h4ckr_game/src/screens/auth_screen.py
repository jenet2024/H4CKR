"""Écran d'authentification — Login / Register / OAuth."""
import pygame
import threading
from config import *
from src.utils.renderer import (
    draw_text, draw_button, draw_input, draw_rect_fill, draw_rect_border,
    MatrixRain, GlitchText, ScanlineOverlay, get_font,
)
from src.utils.api import api
from src.utils.oauth import oauth_login_google, oauth_login_twitter


class AuthScreen:
    def __init__(self, screen):
        self.screen = screen
        self.w, self.h = screen.get_size()

        # Mode : "login" | "register"
        self.mode = "login"

        # Champs
        self.fields = {
            "pseudo":    "",
            "email":     "",
            "password":  "",
            "password2": "",
        }
        self.active_field = "email"

        # UI state
        self.error_msg   = ""
        self.success_msg = ""
        self.loading     = False
        self._done       = False
        self._tab_order_login    = ["email", "password"]
        self._tab_order_register = ["pseudo", "email", "password", "password2"]

        # Effets
        self.matrix   = MatrixRain(self.w, self.h)
        self.title    = GlitchText("H4CKR", self.w // 2 - 70, 50, size=56)
        self.scanline = ScanlineOverlay(self.w, self.h)
        self._t = 0.0

        # Rects boutons
        self._btn_submit  = pygame.Rect(self.w // 2 - 160, 0, 320, 44)
        self._btn_google  = pygame.Rect(self.w // 2 - 160, 0, 152, 40)
        self._btn_twitter = pygame.Rect(self.w // 2 + 8,   0, 152, 40)
        self._btn_toggle  = pygame.Rect(self.w // 2 - 160, 0, 320, 36)
        self._mouse_pos   = (0, 0)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _get_field_rect(self, name):
        cx = self.w // 2
        fields_order = (self._tab_order_register
                        if self.mode == "register"
                        else self._tab_order_login)
        idx = fields_order.index(name) if name in fields_order else 0
        y_start = 200 if self.mode == "login" else 180
        return pygame.Rect(cx - 160, y_start + idx * 68, 320, 42)

    def _layout(self):
        fields_order = (self._tab_order_register
                        if self.mode == "register"
                        else self._tab_order_login)
        last_field = fields_order[-1]
        last_rect  = self._get_field_rect(last_field)
        base_y = last_rect.bottom + 24
        self._btn_submit.top    = base_y
        self._btn_google.top    = base_y + 60
        self._btn_twitter.top   = base_y + 60
        self._btn_toggle.top    = base_y + 120

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._mouse_pos = event.pos

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._on_click(event.pos)

        if event.type == pygame.KEYDOWN:
            self._on_key(event)

    def _on_click(self, pos):
        self._layout()
        # Champs
        for name in (self._tab_order_register
                     if self.mode == "register"
                     else self._tab_order_login):
            if self._get_field_rect(name).collidepoint(pos):
                self.active_field = name
                return

        if self._btn_submit.collidepoint(pos):
            self._submit()
        elif self._btn_google.collidepoint(pos):
            self._oauth("google")
        elif self._btn_twitter.collidepoint(pos):
            self._oauth("twitter")
        elif self._btn_toggle.collidepoint(pos):
            self._toggle_mode()

    def _on_key(self, event):
        if event.key == pygame.K_TAB:
            order = (self._tab_order_register
                     if self.mode == "register"
                     else self._tab_order_login)
            idx = order.index(self.active_field) if self.active_field in order else 0
            self.active_field = order[(idx + 1) % len(order)]
        elif event.key == pygame.K_RETURN:
            self._submit()
        elif event.key == pygame.K_BACKSPACE:
            self.fields[self.active_field] = self.fields[self.active_field][:-1]
        elif event.unicode and event.key != pygame.K_ESCAPE:
            if len(self.fields[self.active_field]) < 80:
                self.fields[self.active_field] += event.unicode

    # ── Actions ───────────────────────────────────────────────────────────────

    def _toggle_mode(self):
        self.mode = "register" if self.mode == "login" else "login"
        self.error_msg   = ""
        self.success_msg = ""

    def _submit(self):
        if self.loading:
            return
        self.error_msg = ""
        email    = self.fields["email"].strip()
        password = self.fields["password"]

        if self.mode == "login":
            if not email or not password:
                self.error_msg = "Remplissez tous les champs."
                return
            self.loading = True
            threading.Thread(target=self._do_login,
                             args=(email, password), daemon=True).start()
        else:
            pseudo   = self.fields["pseudo"].strip()
            password2 = self.fields["password2"]
            if not pseudo or not email or not password:
                self.error_msg = "Remplissez tous les champs."
                return
            if password != password2:
                self.error_msg = "Les mots de passe ne correspondent pas."
                return
            if len(password) < 8:
                self.error_msg = "Mot de passe trop court (8 caractères min)."
                return
            self.loading = True
            threading.Thread(target=self._do_register,
                             args=(pseudo, email, password), daemon=True).start()

    def _do_login(self, email, password):
        data, code = api.login(email, password)
        self.loading = False
        if code == 200:
            self._done = True
        elif code == 0:
            self.error_msg = data.get("detail", "Serveur inaccessible.")
        elif code == 401:
            self.error_msg = "Email ou mot de passe incorrect."
        else:
            self.error_msg = data.get("detail", f"Erreur serveur ({code}).")

    def _do_register(self, pseudo, email, password):
        data, code = api.register(pseudo, email, password)
        self.loading = False
        if code == 201:
            self._done = True
        elif code == 0:
            self.error_msg = data.get("detail", "Serveur inaccessible.")
        elif code == 400:
            detail = data.get("detail", "")
            if "Email" in detail:
                self.error_msg = "Cet email est deja utilise."
            elif "Pseudo" in detail:
                self.error_msg = "Ce pseudo est deja pris."
            else:
                self.error_msg = detail or "Donnees invalides."
        else:
            self.error_msg = data.get("detail", f"Erreur serveur ({code}).")

    def _oauth(self, provider):
        if self.loading:
            return
        self.loading = True
        self.success_msg = f"Ouverture du navigateur {provider.capitalize()}..."

        def do_oauth():
            if provider == "google":
                data, err = oauth_login_google()
            else:
                data, err = oauth_login_twitter()

            self.loading = False
            if err:
                self.error_msg   = err
                self.success_msg = ""
            elif data:
                api.token   = data["access_token"]
                api.refresh = data["refresh_token"]
                api.user    = data["user"]
                self._done = True

        threading.Thread(target=do_oauth, daemon=True).start()

    # ── Update / Draw ─────────────────────────────────────────────────────────

    def update(self, dt):
        self._t += dt
        self.title.update(dt)
        return self._done

    def draw(self):
        surf = self.screen
        surf.fill(C_BG)

        # Matrix rain (transparent)
        self.matrix.update(surf)

        # Titre glitch
        self.title.draw(surf)
        draw_text(surf, "HACKING SIMULATION GAME",
                  self.w // 2, 115, C_GREEN_DIM, 13, center=True)

        # Card centrale
        card_w, card_h = 400, 560 if self.mode == "register" else 460
        card_x = self.w // 2 - card_w // 2
        card_y = 140
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        pygame.draw.rect(surf, C_BG2, card_rect, border_radius=12)
        pygame.draw.rect(surf, C_BORDER, card_rect, 1, border_radius=12)

        # Titre card
        mode_label = "[ CONNEXION ]" if self.mode == "login" else "[ INSCRIPTION ]"
        draw_text(surf, mode_label, self.w // 2, card_y + 22,
                  C_GREEN, 16, bold=True, center=True)

        # Séparateur
        pygame.draw.line(surf, C_BORDER,
                         (card_x + 20, card_y + 48),
                         (card_x + card_w - 20, card_y + 48))

        self._layout()

        # Champs
        fields_order = (self._tab_order_register
                        if self.mode == "register"
                        else self._tab_order_login)
        labels = {
            "pseudo":    "PSEUDO",
            "email":     "EMAIL",
            "password":  "MOT DE PASSE",
            "password2": "CONFIRMER MOT DE PASSE",
        }
        placeholders = {
            "pseudo":    "votre_pseudo",
            "email":     "agent@h4ckr.io",
            "password":  "••••••••",
            "password2": "••••••••",
        }
        for name in fields_order:
            rect = self._get_field_rect(name)
            draw_input(
                surf, rect,
                self.fields[name],
                label=labels[name],
                active=(self.active_field == name),
                placeholder=placeholders[name],
                password=(name in ("password", "password2")),
            )

        # Bouton submit
        hover_sub = self._btn_submit.collidepoint(self._mouse_pos)
        label_sub = ("CONNEXION" if self.mode == "login" else "CRÉER UN COMPTE")
        draw_button(surf, self._btn_submit, label_sub,
                    color=C_GREEN, hover=hover_sub, size=15, bold=True)

        # Loading spinner
        if self.loading:
            dots = "." * (int(self._t * 3) % 4)
            draw_text(surf, f"CHARGEMENT{dots}",
                      self.w // 2, self._btn_submit.bottom + 8,
                      C_GREEN_MID, 13, center=True)

        # Séparateur OAuth
        sep_y = self._btn_google.top - 12
        pygame.draw.line(surf, C_BORDER,
                         (card_x + 20, sep_y), (card_x + card_w - 20, sep_y))
        draw_text(surf, "ou continuer avec", self.w // 2, sep_y - 14,
                  C_GRAY, 12, center=True)

        # Boutons OAuth
        hov_g = self._btn_google.collidepoint(self._mouse_pos)
        hov_t = self._btn_twitter.collidepoint(self._mouse_pos)

        pygame.draw.rect(surf, C_BG2 if not hov_g else (20, 40, 20),
                         self._btn_google, border_radius=8)
        pygame.draw.rect(surf, (66, 133, 244) if not hov_g else (100, 160, 255),
                         self._btn_google, 2, border_radius=8)
        draw_text(surf, "G  Google", self._btn_google.centerx,
                  self._btn_google.centery, (66, 133, 244), 13, center=True)

        pygame.draw.rect(surf, C_BG2 if not hov_t else (20, 40, 20),
                         self._btn_twitter, border_radius=8)
        pygame.draw.rect(surf, (29, 161, 242) if not hov_t else (80, 190, 255),
                         self._btn_twitter, 2, border_radius=8)
        draw_text(surf, "X  Twitter", self._btn_twitter.centerx,
                  self._btn_twitter.centery, (29, 161, 242), 13, center=True)

        # Toggle login/register
        toggle_txt = ("Pas encore de compte ? S'inscrire"
                      if self.mode == "login"
                      else "Déjà un compte ? Se connecter")
        hov_tog = self._btn_toggle.collidepoint(self._mouse_pos)
        draw_text(surf, toggle_txt, self.w // 2, self._btn_toggle.centery,
                  C_CYAN if hov_tog else C_GRAY, 13, center=True)

        # Messages erreur / succès
        if self.error_msg:
            draw_text(surf, f"⚠ {self.error_msg}",
                      self.w // 2, card_y + card_h + 16,
                      C_RED, 13, center=True)
        if self.success_msg:
            draw_text(surf, f"✓ {self.success_msg}",
                      self.w // 2, card_y + card_h + 16,
                      C_GREEN, 13, center=True)

        # Scanlines CRT
        self.scanline.draw(surf)
