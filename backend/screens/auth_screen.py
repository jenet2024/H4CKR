"""
Écran d'authentification h4ckR — Login / Inscription / OAuth Google & Twitter
Ambiance cyberpunk : glitch, scanlines, particles vertes, glassmorphism.
"""
import math
import random
import time
import threading
import webbrowser
import sys
import pygame
from typing import Optional, List

from client.core.settings import Settings
from client.core.api_client import APIClient
from client.core.auth_manager import AuthManager


# ─── Constantes UI ──────────────────────────────────────────────────────────────
PANEL_W = 500
PANEL_H = 620
INPUT_H = 52
BTN_H   = 52


# ─── Particle matrice ───────────────────────────────────────────────────────────
class MatrixChar:
    def __init__(self, w: int, h: int):
        self.x = random.randint(0, w)
        self.y = random.uniform(-h, 0)
        self.speed = random.uniform(60, 200)
        self.char = chr(random.choice(
            list(range(0x30A0, 0x30FF)) + list(range(0x41, 0x5B)) + list(range(0x30, 0x3A))
        ))
        self.alpha = random.randint(40, 180)
        self.size = random.choice([14, 16, 18])
        self.color = (random.randint(0, 60), random.randint(180, 255), random.randint(80, 160))

    def update(self, dt: float, h: int):
        self.y += self.speed * dt
        if self.y > h:
            self.y = random.uniform(-200, 0)
            self.x = random.randint(0, 1280)

    def draw(self, screen: pygame.Surface):
        fnt = pygame.font.SysFont("Consolas", self.size)
        s = fnt.render(self.char, True, self.color)
        s.set_alpha(self.alpha)
        screen.blit(s, (self.x, int(self.y)))


# ─── Champ de saisie ────────────────────────────────────────────────────────────
class InputField:
    def __init__(self, x: int, y: int, w: int, label: str, password: bool = False):
        self.rect    = pygame.Rect(x, y, w, INPUT_H)
        self.label   = label
        self.password = password
        self.text    = ""
        self.focused = False
        self.cursor_t = 0.0
        self.error   = ""

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.focused = self.rect.collidepoint(event.pos)
            return self.focused
        if event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (pygame.K_RETURN, pygame.K_TAB, pygame.K_ESCAPE):
                if len(self.text) < 80 and event.unicode.isprintable():
                    self.text += event.unicode
        return False

    def draw(self, screen: pygame.Surface, settings: Settings, font_lbl, font_inp):
        # Label
        lbl = font_lbl.render(self.label, True, settings.COLOR_TEXT_DIM)
        screen.blit(lbl, (self.rect.x, self.rect.y - 22))

        # Panel
        bg = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.focused:
            bg.fill((0, 40, 0, 180))
        else:
            bg.fill((5, 20, 5, 140))
        screen.blit(bg, self.rect.topleft)

        border_col = settings.COLOR_PRIMARY if self.focused else (0, 80, 40)
        pygame.draw.rect(screen, border_col, self.rect, 2, border_radius=6)

        # Texte
        display = "*" * len(self.text) if self.password else self.text
        self.cursor_t += 0.02
        if self.focused and int(self.cursor_t * 2) % 2 == 0:
            display += "▌"
        txt = font_inp.render(display, True, settings.COLOR_TEXT)
        screen.blit(txt, txt.get_rect(midleft=(self.rect.x + 14, self.rect.centery)))

        # Error
        if self.error:
            err = font_lbl.render(self.error, True, settings.COLOR_ERROR)
            screen.blit(err, (self.rect.x, self.rect.bottom + 4))


# ─── Bouton ─────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, x: int, y: int, w: int, h: int, label: str, color: tuple, icon: str = ""):
        self.rect  = pygame.Rect(x, y, w, h)
        self.label = label
        self.color = color
        self.icon  = icon
        self.hover = 0.0

    def update(self, dt: float):
        target = 1.0 if self.rect.collidepoint(pygame.mouse.get_pos()) else 0.0
        self.hover += (target - self.hover) * 10 * dt

    def draw(self, screen: pygame.Surface, font):
        h = self.hover
        r, g, b = self.color
        bg = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        bg.fill((r, g, b, int(40 + 120 * h)))
        screen.blit(bg, self.rect.topleft)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=8)

        lbl = self.icon + " " + self.label if self.icon else self.label
        txt = font.render(lbl, True, (220, 255, 220))
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


# ─── Écran d'authentification ────────────────────────────────────────────────────
class AuthScreen:
    MODE_LOGIN    = "login"
    MODE_REGISTER = "register"

    def __init__(self, screen: pygame.Surface, settings: Settings,
                 api_client: APIClient, auth_manager: AuthManager):
        self.screen       = screen
        self.settings     = settings
        self.api          = api_client
        self.auth         = auth_manager
        self.clock        = pygame.time.Clock()
        self.running      = True
        self.mode         = self.MODE_LOGIN
        self.time_t       = 0.0
        self.error_msg    = ""
        self.success_msg  = ""
        self.loading      = False
        self._oauth_state: Optional[str] = None
        self._oauth_thread: Optional[threading.Thread] = None

        # Fonts
        self.font_title = settings.load_font(42)
        self.font_sub   = settings.load_font(16)
        self.font_lbl   = settings.load_font(14)
        self.font_inp   = settings.load_font(20)
        self.font_btn   = settings.load_font(18)
        self.font_small = settings.load_font(13)

        # Matrice de chars
        W, H = screen.get_size()
        self.matrix: List[MatrixChar] = [MatrixChar(W, H) for _ in range(60)]

        self._build_ui()

    # ── Construction UI ──────────────────────────────────────────────────────────

    def _build_ui(self):
        W, H = self.screen.get_size()
        cx = W // 2
        px = cx - PANEL_W // 2

        if self.mode == self.MODE_LOGIN:
            py = (H - 480) // 2
            self.fields = [
                InputField(px + 30, py + 120, PANEL_W - 60, "Identifiant ou Email"),
                InputField(px + 30, py + 220, PANEL_W - 60, "Mot de passe", password=True),
            ]
            self.btn_submit = Button(px + 30, py + 310, PANEL_W - 60, BTN_H,
                                     "SE CONNECTER", self.settings.COLOR_PRIMARY)
            self.btn_google  = Button(px + 30, py + 375, (PANEL_W - 75) // 2, BTN_H - 10,
                                      "Google", (66, 133, 244), "🔵")
            self.btn_twitter = Button(cx + 8, py + 375, (PANEL_W - 75) // 2, BTN_H - 10,
                                      "Twitter/X", (29, 161, 242), "🐦")
            self.btn_switch  = Button(px + 30, py + 435, PANEL_W - 60, 36,
                                      "Pas encore de compte ? S'inscrire",
                                      self.settings.COLOR_TEXT_DIM)
            self.all_buttons = [self.btn_submit, self.btn_google, self.btn_twitter, self.btn_switch]
        else:
            py = (H - 620) // 2
            self.fields = [
                InputField(px + 30, py + 110, PANEL_W - 60, "Nom d'utilisateur"),
                InputField(px + 30, py + 200, PANEL_W - 60, "Email"),
                InputField(px + 30, py + 290, PANEL_W - 60, "Mot de passe", password=True),
                InputField(px + 30, py + 380, PANEL_W - 60, "Confirmer le mot de passe", password=True),
            ]
            self.btn_submit = Button(px + 30, py + 460, PANEL_W - 60, BTN_H,
                                     "CRÉER MON COMPTE", self.settings.COLOR_PRIMARY)
            self.btn_google  = Button(px + 30, py + 525, (PANEL_W - 75) // 2, BTN_H - 10,
                                      "Google", (66, 133, 244), "🔵")
            self.btn_twitter = Button(cx + 8, py + 525, (PANEL_W - 75) // 2, BTN_H - 10,
                                      "Twitter/X", (29, 161, 242), "🐦")
            self.btn_switch  = Button(px + 30, py + 582, PANEL_W - 60, 30,
                                      "Déjà un compte ? Se connecter",
                                      self.settings.COLOR_TEXT_DIM)
            self.all_buttons = [self.btn_submit, self.btn_google, self.btn_twitter, self.btn_switch]

    # ── Boucle principale ────────────────────────────────────────────────────────

    def run(self) -> bool:
        """Retourne True si l'utilisateur est authentifié, False s'il quitte."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 0.05)
            self.time_t += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_event(event)

            self._update(dt)
            self._draw()
            pygame.display.flip()

            if self.auth.is_logged_in:
                return True

        return self.auth.is_logged_in

    def _handle_event(self, event: pygame.event.Event):
        for field in self.fields:
            field.handle_event(event)

        if self.btn_submit.is_clicked(event) and not self.loading:
            self._submit()
        elif self.btn_google.is_clicked(event) and not self.loading:
            self._start_oauth("google")
        elif self.btn_twitter.is_clicked(event) and not self.loading:
            self._start_oauth("twitter")
        elif self.btn_switch.is_clicked(event):
            self.mode = self.MODE_REGISTER if self.mode == self.MODE_LOGIN else self.MODE_LOGIN
            self.error_msg = ""
            self.success_msg = ""
            self._build_ui()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and not self.loading:
            self._submit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            focused = next((i for i, f in enumerate(self.fields) if f.focused), -1)
            for f in self.fields:
                f.focused = False
            if focused >= 0:
                self.fields[(focused + 1) % len(self.fields)].focused = True

    def _update(self, dt: float):
        W, H = self.screen.get_size()
        for m in self.matrix:
            m.update(dt, H)
        for btn in self.all_buttons:
            btn.update(dt)

        # Polling OAuth
        if self._oauth_state:
            result = self.api.poll_oauth(self._oauth_state)
            if result.get("status") == "success":
                self._on_auth_success(result)
                self._oauth_state = None
                self.loading = False

    def _draw(self):
        W, H = self.screen.get_size()
        self.screen.fill(self.settings.COLOR_BG)

        # Rain matrix
        for m in self.matrix:
            m.draw(self.screen)

        # Scanlines overlay
        self._draw_scanlines(W, H)

        # Panel glassmorphism
        self._draw_panel(W, H)

        # Title
        self._draw_header(W, H)

        # Fields
        for field in self.fields:
            field.draw(self.screen, self.settings, self.font_lbl, self.font_inp)

        # Buttons
        for btn in self.all_buttons:
            btn.draw(self.screen, self.font_btn)

        # Divider OAuth
        self._draw_divider(W, H)

        # Messages
        if self.error_msg:
            err = self.font_sub.render("⚠ " + self.error_msg, True, self.settings.COLOR_ERROR)
            err.set_alpha(220)
            self.screen.blit(err, err.get_rect(center=(W // 2, self._panel_y(H) + self._panel_h() - 20)))

        if self.success_msg:
            ok = self.font_sub.render("✓ " + self.success_msg, True, self.settings.COLOR_SUCCESS)
            self.screen.blit(ok, ok.get_rect(center=(W // 2, self._panel_y(H) + self._panel_h() - 20)))

        if self.loading:
            dots = "." * (int(self.time_t * 3) % 4)
            ld = self.font_sub.render(f"Connexion en cours{dots}", True, self.settings.COLOR_ACCENT)
            self.screen.blit(ld, ld.get_rect(center=(W // 2, self._panel_y(H) + self._panel_h() - 20)))

    def _draw_scanlines(self, W: int, H: int):
        scan = pygame.Surface((W, H), pygame.SRCALPHA)
        for y in range(0, H, 4):
            pygame.draw.line(scan, (0, 0, 0, 30), (0, y), (W, y))
        self.screen.blit(scan, (0, 0))

    def _panel_y(self, H: int) -> int:
        ph = self._panel_h()
        return (H - ph) // 2

    def _panel_h(self) -> int:
        return 620 if self.mode == self.MODE_REGISTER else 490

    def _draw_panel(self, W: int, H: int):
        ph = self._panel_h()
        py = self._panel_y(H)
        px = W // 2 - PANEL_W // 2

        panel = pygame.Surface((PANEL_W, ph), pygame.SRCALPHA)
        panel.fill((5, 18, 5, 210))
        self.screen.blit(panel, (px, py))

        # Glow border
        t = self.time_t
        glow_alpha = int(120 + 60 * math.sin(t * 2))
        border_surf = pygame.Surface((PANEL_W, ph), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, (*self.settings.COLOR_PRIMARY, glow_alpha),
                         (0, 0, PANEL_W, ph), 2, border_radius=12)
        self.screen.blit(border_surf, (px, py))

        # Corner accents
        acc = self.settings.COLOR_ACCENT
        size = 20
        for dx, dy in [(0, 0), (PANEL_W - size, 0), (0, ph - size), (PANEL_W - size, ph - size)]:
            pygame.draw.rect(self.screen, acc, (px + dx, py + dy, size, 2))
            pygame.draw.rect(self.screen, acc, (px + dx, py + dy, 2, size))

    def _draw_header(self, W: int, H: int):
        py = self._panel_y(H)
        t = self.time_t

        # Glitch effect on title
        title_txt = "h4ckR" if int(t * 10) % 20 != 0 else "h@ckR"
        glitch_offset = random.randint(-2, 2) if int(t * 8) % 15 == 0 else 0

        title = self.font_title.render(title_txt, True, self.settings.COLOR_PRIMARY)
        glow  = self.font_title.render(title_txt, True, self.settings.COLOR_ACCENT)
        glow.set_alpha(40)
        cx = W // 2
        self.screen.blit(glow, glow.get_rect(center=(cx + 3 + glitch_offset, py + 45)))
        self.screen.blit(title, title.get_rect(center=(cx + glitch_offset, py + 45)))

        mode_txt = "CONNEXION" if self.mode == self.MODE_LOGIN else "INSCRIPTION"
        sub = self.font_sub.render(f"── {mode_txt} ──", True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(sub, sub.get_rect(center=(cx, py + 85)))

    def _draw_divider(self, W: int, H: int):
        # Small "ou" divider between btn_submit and OAuth buttons
        cy = self.btn_google.rect.top - 12
        cx = W // 2
        pygame.draw.line(self.screen, (0, 80, 40), (cx - 80, cy), (cx - 30, cy), 1)
        pygame.draw.line(self.screen, (0, 80, 40), (cx + 30, cy), (cx + 80, cy), 1)
        ou = self.font_small.render("ou", True, (0, 120, 60))
        self.screen.blit(ou, ou.get_rect(center=(cx, cy)))

    # ── Actions ──────────────────────────────────────────────────────────────────

    def _submit(self):
        values = [f.text.strip() for f in self.fields]
        for f in self.fields:
            f.error = ""
        self.error_msg = ""

        if self.mode == self.MODE_LOGIN:
            if not values[0] or not values[1]:
                self.error_msg = "Veuillez remplir tous les champs."
                return
            self.loading = True
            threading.Thread(target=self._do_login,
                             args=(values[0], values[1]), daemon=True).start()
        else:
            if not all(values):
                self.error_msg = "Veuillez remplir tous les champs."
                return
            if values[2] != values[3]:
                self.error_msg = "Les mots de passe ne correspondent pas."
                return
            if len(values[2]) < 6:
                self.error_msg = "Mot de passe trop court (6 caractères min)."
                return
            self.loading = True
            threading.Thread(target=self._do_register,
                             args=(values[0], values[1], values[2], values[3]),
                             daemon=True).start()

    def _do_login(self, identifier: str, password: str):
        result = self.api.login(identifier, password)
        self.loading = False
        if "error" in result:
            self.error_msg = result["error"]
        else:
            self._on_auth_success(result)

    def _do_register(self, username: str, email: str, password: str, confirm: str):
        result = self.api.register(username, email, password, confirm)
        self.loading = False
        if "error" in result:
            self.error_msg = result["error"]
        else:
            self._on_auth_success(result)

    def _start_oauth(self, provider: str):
        result = self.api.get_oauth_url(provider)
        if not result or "error" in (result or {}):
            self.error_msg = f"OAuth {provider} non configuré. Ajoutez vos clés dans .env"
            return
        auth_url = result.get("auth_url", "")
        state    = result.get("state", "")
        if auth_url:
            webbrowser.open(auth_url)
            self._oauth_state = state
            self.loading = True
            self.success_msg = f"Navigateur ouvert — Connectez-vous avec {provider.capitalize()}..."

    def _on_auth_success(self, data: dict):
        self.auth.login(
            token=data.get("access_token", ""),
            user_id=data.get("user_id", 0),
            username=data.get("username", ""),
            email=data.get("email", ""),
            avatar_url=data.get("avatar_url"),
        )
        self.api.token = self.auth.token
        self.success_msg = f"Bienvenue {self.auth.username} !"
        self.running = False
