"""Screens Guide et Contact."""
import math
import sys
import pygame
from client.core.settings import Settings
from client.core.api_client import APIClient
from client.core.auth_manager import AuthManager


# ─── Guide du jeu ────────────────────────────────────────────────────────────────
GUIDE_SECTIONS = [
    ("🎮 Comment jouer", [
        "h4ckR est un jeu de cybersécurité à deux niveaux de difficulté.",
        "Chaque niveau te présente une énigme liée à la sécurité informatique.",
        "Tu dois résoudre l'énigme pour passer au niveau suivant.",
        "Utilise le bouton 💡 INDICE si tu bloques (pénalité de 30 pts).",
    ]),
    ("🎓 Mode Débutant", [
        "10 niveaux progressifs sur les bases de la cybersécurité.",
        "Niveaux 1-5 : Notions fondamentales (mots de passe, phishing, chiffrement...)",
        "Après niveau 5 : Badge 'Cyber Initié' + vidéo de félicitations !",
        "Niveaux 6-10 : Concepts avancés (firewall, URLs, morse, stégano, boss)",
        "Fin : Certificat de complétion généré avec ton score.",
    ]),
    ("💀 Mode Expert", [
        "6 missions critiques avec un vrai terminal interactif.",
        "Interface style TryHackMe : panel mission + terminal subprocess.",
        "Commandes réelles : ping, nslookup, base64, commandes custom du jeu.",
        "Missions : reconnaissance, logs, déchiffrement, SQL injection, stégano, CTF boss.",
        "Fin : Certificat Elite Hacker avec code unique vérifiable.",
    ]),
    ("🏆 Scoring", [
        "Chaque niveau vaut 100 pts (250 pts en mode Expert).",
        "Utiliser un indice coûte 30 pts.",
        "Un résumé de tes points est affiché en continu dans le HUD.",
        "Tes scores sont sauvegardés en ligne si connecté au serveur.",
    ]),
    ("🔧 Problèmes", [
        "Si le jeu plante, relance-le simplement.",
        "Si le serveur est hors ligne, le jeu fonctionne en mode offline.",
        "Pour tout bug, utilise l'écran 'Contact' pour nous informer.",
        "Le terminal Expert nécessite Windows et l'invite de commande.",
    ]),
]


class GuideScreen:
    def __init__(self, screen: pygame.Surface, settings: Settings):
        self.screen  = screen
        self.settings = settings
        self.clock   = pygame.time.Clock()
        self.running = True
        self.t       = 0.0
        self.scroll  = 0
        self.max_scroll = 0

        self.font_title = settings.load_font(26)
        self.font_sec   = settings.load_font(20)
        self.font_body  = settings.load_font(15)
        self.font_small = settings.load_font(13)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.t += dt
            W, H = self.screen.get_size()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_DOWN:
                        self.scroll = min(self.scroll + 30, self.max_scroll)
                    elif event.key == pygame.K_UP:
                        self.scroll = max(0, self.scroll - 30)
                if event.type == pygame.MOUSEWHEEL:
                    self.scroll = max(0, min(self.scroll - event.y * 20, self.max_scroll))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    W2, H2 = self.screen.get_size()
                    if pygame.Rect(W2-120, H2-46, 110, 36).collidepoint(event.pos):
                        self.running = False
            self._draw(W, H)
            pygame.display.flip()

    def _draw(self, W: int, H: int):
        self.screen.fill(self.settings.COLOR_BG)

        # Grid bg
        gs = pygame.Surface((W, H), pygame.SRCALPHA)
        for x in range(0, W, 50):
            pygame.draw.line(gs, (*self.settings.COLOR_PRIMARY, 8), (x, 0), (x, H))
        for y in range(0, H, 50):
            pygame.draw.line(gs, (*self.settings.COLOR_PRIMARY, 8), (0, y), (W, y))
        self.screen.blit(gs, (0, 0))

        # Header
        bar = pygame.Surface((W, 48), pygame.SRCALPHA); bar.fill((0, 20, 0, 200))
        self.screen.blit(bar, (0, 0))
        pygame.draw.line(self.screen, self.settings.COLOR_PRIMARY, (0, 48), (W, 48), 1)
        title = self.font_title.render("📖  GUIDE DU JEU h4ckR", True, self.settings.COLOR_PRIMARY)
        self.screen.blit(title, title.get_rect(center=(W//2, 24)))

        # Content
        content_y = 62 - self.scroll
        pw = 720
        px = (W - pw) // 2
        total_h = 0

        for section_title, items in GUIDE_SECTIONS:
            # Section title
            if content_y + 36 > 48 and content_y < H:
                sec_bg = pygame.Surface((pw, 36), pygame.SRCALPHA)
                sec_bg.fill((*self.settings.COLOR_PRIMARY, 30))
                self.screen.blit(sec_bg, (px, content_y))
                sec_s = self.font_sec.render(section_title, True, self.settings.COLOR_PRIMARY)
                self.screen.blit(sec_s, (px + 12, content_y + 8))
            content_y += 44
            total_h   += 44

            for item in items:
                if content_y > 48 and content_y < H:
                    bullet = self.font_body.render(f"  • {item}", True, self.settings.COLOR_TEXT)
                    self.screen.blit(bullet, (px + 8, content_y))
                content_y += 22
                total_h   += 22

            content_y += 14
            total_h   += 14

        self.max_scroll = max(0, total_h - (H - 100))

        # Footer
        foot = pygame.Surface((W, 46), pygame.SRCALPHA); foot.fill((0, 12, 0, 200))
        self.screen.blit(foot, (0, H - 46))
        pygame.draw.line(self.screen, self.settings.COLOR_BORDER, (0, H-46), (W, H-46), 1)
        scroll_info = self.font_small.render("↑↓ ou molette pour défiler", True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(scroll_info, (14, H - 29))

        # Close button
        close_r = pygame.Rect(W-120, H-42, 108, 32)
        cl_bg = pygame.Surface((108, 32), pygame.SRCALPHA)
        cl_bg.fill((80, 0, 0, 160))
        self.screen.blit(cl_bg, close_r.topleft)
        pygame.draw.rect(self.screen, self.settings.COLOR_DANGER, close_r, 1, border_radius=4)
        cl = self.font_small.render("✕ Fermer", True, self.settings.COLOR_TEXT)
        self.screen.blit(cl, cl.get_rect(center=close_r.center))


# ─── Contact ─────────────────────────────────────────────────────────────────────
class ContactScreen:
    def __init__(self, screen: pygame.Surface, settings: Settings,
                 api: APIClient, auth: AuthManager):
        self.screen  = screen
        self.settings = settings
        self.api      = api
        self.auth     = auth
        self.clock   = pygame.time.Clock()
        self.running = True
        self.t       = 0.0

        self.font_title = settings.load_font(28)
        self.font_lbl   = settings.load_font(15)
        self.font_inp   = settings.load_font(17)
        self.font_small = settings.load_font(13)

        self._build_form()
        self.msg = ""; self.msg_color = settings.COLOR_SUCCESS
        self.sent = False

    def _build_form(self):
        W, H = self.screen.get_size()
        cx, fw = W//2, 560
        px = cx - fw//2
        by = 130

        prefill_email = self.auth.email or ""

        self.fields = [
            {"label": "Votre email",        "text": prefill_email, "rect": pygame.Rect(px, by,      fw, 46), "pw": False},
            {"label": "Sujet",              "text": "",            "rect": pygame.Rect(px, by+66,   fw, 46), "pw": False},
            {"label": "Message",            "text": "",            "rect": pygame.Rect(px, by+132,  fw, 130),"pw": False, "multiline": True},
        ]
        self.focused_idx = 0
        self.fields[0]["focused"] = True

        self.btn_send  = pygame.Rect(px,       by+282, fw//2-8, 46)
        self.btn_close = pygame.Rect(px+fw//2+8, by+282, fw//2-8, 46)

    def run(self):
        while self.running:
            dt = self.clock.tick(60)/1000.0
            self.t += dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self._handle(event)
            self._draw()
            pygame.display.flip()

    def _handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_TAB:
                self.focused_idx = (self.focused_idx + 1) % len(self.fields)
            elif event.key == pygame.K_BACKSPACE:
                f = self.fields[self.focused_idx]
                f["text"] = f["text"][:-1]
            elif event.unicode.isprintable():
                f = self.fields[self.focused_idx]
                max_len = 500 if f.get("multiline") else 100
                if len(f["text"]) < max_len:
                    f["text"] += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, f in enumerate(self.fields):
                if f["rect"].collidepoint(pos):
                    self.focused_idx = i
            if self.btn_send.collidepoint(pos) and not self.sent:
                self._send()
            if self.btn_close.collidepoint(pos):
                self.running = False

    def _send(self):
        email   = self.fields[0]["text"].strip()
        subject = self.fields[1]["text"].strip()
        message = self.fields[2]["text"].strip()
        if not email or not subject or not message:
            self.msg = "⚠ Tous les champs sont requis."; self.msg_color = self.settings.COLOR_ERROR; return
        resp = self.api.send_contact(email, subject, message, self.auth.user_id)
        if resp and "error" not in resp:
            self.msg = "✓ Message envoyé ! Nous vous répondrons sous 48h."; self.sent = True
        else:
            self.msg = "⚠ Erreur d'envoi (serveur hors ligne ?). Notez votre message."; self.msg_color = self.settings.COLOR_WARNING

    def _draw(self):
        W, H = self.screen.get_size()
        self.screen.fill(self.settings.COLOR_BG)
        gs = pygame.Surface((W, H), pygame.SRCALPHA)
        for x in range(0, W, 50):
            pygame.draw.line(gs, (*self.settings.COLOR_SECONDARY, 6), (x,0),(x,H))
        self.screen.blit(gs,(0,0))

        # Header
        bar = pygame.Surface((W, 48), pygame.SRCALPHA); bar.fill((10,0,20,210))
        self.screen.blit(bar,(0,0))
        pygame.draw.line(self.screen, self.settings.COLOR_SECONDARY,(0,48),(W,48),1)
        title = self.font_title.render("✉  NOUS CONTACTER", True, self.settings.COLOR_SECONDARY)
        self.screen.blit(title, title.get_rect(center=(W//2,24)))

        sub = self.font_lbl.render("Un problème dans le jeu ? Signalez-le ici.", True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(sub, sub.get_rect(center=(W//2,115)))

        # Fields
        fnt_inp = pygame.font.SysFont("Consolas", 17)
        for i, f in enumerate(self.fields):
            lbl = self.font_lbl.render(f["label"], True, self.settings.COLOR_TEXT_DIM)
            self.screen.blit(lbl, (f["rect"].x, f["rect"].y - 22))
            focused = (i == self.focused_idx)
            bg = pygame.Surface((f["rect"].w, f["rect"].h), pygame.SRCALPHA)
            bg.fill((8, 0, 18, 180))
            self.screen.blit(bg, f["rect"].topleft)
            bc = self.settings.COLOR_SECONDARY if focused else (60, 0, 80)
            pygame.draw.rect(self.screen, bc, f["rect"], 2, border_radius=6)
            cur = "▌" if focused and int(self.t*2)%2==0 else ""
            display = f["text"] + cur
            if f.get("multiline"):
                lines = (display if display else " ").split("\n") + [""]
                for li, line in enumerate(lines[:5]):
                    ls = fnt_inp.render(line[:60], True, self.settings.COLOR_TEXT)
                    self.screen.blit(ls, (f["rect"].x+10, f["rect"].y+8+li*24))
            else:
                ts = fnt_inp.render(display[-46:], True, self.settings.COLOR_TEXT)
                self.screen.blit(ts, ts.get_rect(midleft=(f["rect"].x+10, f["rect"].centery)))

        # Buttons
        for btn, label, col in [
            (self.btn_send,  "📤 Envoyer",  self.settings.COLOR_PRIMARY),
            (self.btn_close, "✕ Annuler",   (80,0,0)),
        ]:
            bg = pygame.Surface((btn.w, btn.h), pygame.SRCALPHA)
            bg.fill((*col, 80))
            self.screen.blit(bg, btn.topleft)
            pygame.draw.rect(self.screen, col, btn, 2, border_radius=6)
            bs = self.font_lbl.render(label, True, self.settings.COLOR_TEXT)
            self.screen.blit(bs, bs.get_rect(center=btn.center))

        # Message feedback
        if self.msg:
            ms = self.font_lbl.render(self.msg, True, self.msg_color)
            self.screen.blit(ms, ms.get_rect(center=(W//2, self.btn_send.bottom+22)))
