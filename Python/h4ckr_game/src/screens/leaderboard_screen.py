"""Écrans secondaires : Leaderboard, Guide, Contact, Certificat."""
import pygame
import threading
from config import *
from src.utils.renderer import (
    draw_text, draw_button, draw_input, draw_text_wrapped,
    ScanlineOverlay, get_font, ProgressBar,
)
from src.utils.api import api


# ═══════════════════════════════════════════════════════════════════════════════
# Leaderboard
# ═══════════════════════════════════════════════════════════════════════════════

class LeaderboardScreen:
    def __init__(self, screen):
        self.screen   = screen
        self.w, self.h = screen.get_size()
        self.scanline = ScanlineOverlay(self.w, self.h)
        self._action  = None
        self._mouse   = (0, 0)
        self._t       = 0.0
        self._entries = []
        self._loading = True
        self._btn_back = pygame.Rect(20, 16, 110, 34)
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        data, code = api.get_leaderboard()
        if code == 200:
            self._entries = data
        self._loading = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._mouse = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._btn_back.collidepoint(event.pos):
                self._action = "menu"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._action = "menu"

    def update(self, dt):
        self._t += dt
        action = self._action
        self._action = None
        return action

    def draw(self):
        surf = self.screen
        surf.fill(C_BG)
        for gx in range(0, self.w, 50):
            pygame.draw.line(surf, (8, 18, 8), (gx, 0), (gx, self.h))

        pygame.draw.rect(surf, C_BG2, (0, 0, self.w, 56))
        draw_text(surf, "🏆 CLASSEMENT GÉNÉRAL",
                  self.w // 2, 20, C_GOLD, 20, bold=True, center=True)
        hov = self._btn_back.collidepoint(self._mouse)
        draw_button(surf, self._btn_back, "◀ MENU", C_GRAY, hover=hov, size=13)

        if self._loading:
            dots = "." * (int(self._t * 3) % 4)
            draw_text(surf, f"Chargement{dots}", self.w // 2, self.h // 2,
                      C_GREEN_MID, 18, center=True)
            self.scanline.draw(surf)
            return

        # Header tableau
        headers = ["#", "AGENT", "POINTS", "BADGES", "NIVEAU"]
        cols    = [80, 300, 500, 680, 860]
        header_y = 80
        for txt, cx in zip(headers, cols):
            draw_text(surf, txt, cx, header_y, C_GREEN_MID, 13, bold=True, center=True)
        pygame.draw.line(surf, C_BORDER, (40, header_y + 24), (self.w - 40, header_y + 24))

        # Lignes
        medal_cols = {1: C_GOLD, 2: (192, 192, 192), 3: (205, 127, 50)}
        current_id = (api.user or {}).get("id")

        for i, entry in enumerate(self._entries[:20]):
            row_y  = 120 + i * 36
            rank   = entry.get("rank", i + 1)
            is_me  = entry.get("user_id") == current_id

            if is_me:
                pygame.draw.rect(surf, (10, 30, 10),
                                 pygame.Rect(40, row_y - 6, self.w - 80, 32),
                                 border_radius=4)
                pygame.draw.rect(surf, C_GREEN_DIM,
                                 pygame.Rect(40, row_y - 6, self.w - 80, 32),
                                 1, border_radius=4)

            col_r  = medal_cols.get(rank, C_WHITE if not is_me else C_GREEN)
            rank_s = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, str(rank))

            values = [
                rank_s,
                entry.get("pseudo", "?")[:20],
                str(entry.get("total_points", 0)),
                str(entry.get("badges_count", 0)),
                entry.get("level_reached", "-"),
            ]
            for txt, cx in zip(values, cols):
                draw_text(surf, txt, cx, row_y, col_r, 14, center=True)

            pygame.draw.line(surf, (15, 30, 15),
                             (40, row_y + 22), (self.w - 40, row_y + 22))

        self.scanline.draw(surf)


# ═══════════════════════════════════════════════════════════════════════════════
# Guide du jeu
# ═══════════════════════════════════════════════════════════════════════════════

GUIDE_SECTIONS = [
    ("🎮 Bienvenue dans H4CKR", """
H4CKR est un jeu de simulation de hacking éducatif.
Vous incarnez un hacker qui résout des énigmes de cybersécurité
pour progresser dans deux niveaux : Débutant et Expert.
"""),
    ("📋 Comment jouer", """
1. Choisissez un niveau dans le menu principal.
2. Regardez la vidéo d'introduction du Robot H4CKR.
3. Résolvez les énigmes les unes après les autres.
4. Entrez votre réponse dans le champ prévu et validez.
5. Récupérez les indices si vous êtes bloqué (-10 pts).
6. Obtenez votre certificat à la fin du niveau.
"""),
    ("🔰 Niveau Débutant (10 étapes)", """
Notions abordées :
• Encodage Base64 — décodez des messages cachés
• Chiffre de César / ROT13 — décalez les lettres
• Stéganographie — trouvez des indices dans des images
• Analyse audio — messages inversés dans des sons
• Métadonnées — informations cachées dans des fichiers

Après les 5 premières étapes, vous recevez un badge.
À la fin des 10 étapes : certificat de niveau Débutant.
"""),
    ("🎩 Niveau Expert (6 étapes)", """
Notions avancées :
• Analyse de logs serveur — trouvez l'intrus
• Terminal interactif — tapez de vraies commandes
• Extraction de métadonnées avancée
• Décodage via terminal (Base64, hex...)
• Mission finale — assemblez tous les indices

Toutes les commandes du terminal : tapez 'help'.
À la fin : certificat de niveau Expert.
"""),
    ("⭐ Système de points et badges", """
Points :
• Chaque énigme rapporte entre 100 et 250 points.
• Utiliser un indice coûte -10 points.
• Plus vous êtes rapide, plus votre score est élevé.

Badges disponibles :
🩸 First Blood — première énigme résolue
🔓 Déchiffreur — Base64 ou César résolus
🖼️ Stega Master — stéganographie résolue
🎧 Détective Audio — énigme audio résolue
🦅 Sans Filet — niveau sans indices
⚡ Speed Hacker — Débutant en < 10 min
🎩 Black Hat — niveau Expert complété
🏆 Top Hacker — top 3 du classement
"""),
    ("💡 Conseils", """
• Lisez attentivement la description de chaque énigme.
• Les indices sont là pour vous aider, utilisez-les !
• Pour le terminal : tapez 'help' pour voir les commandes.
• Les réponses sont insensibles à la casse.
• Prenez le temps de bien analyser les fichiers.
• Consultez le classement pour vous motiver !
"""),
]


class GuideScreen:
    def __init__(self, screen):
        self.screen   = screen
        self.w, self.h = screen.get_size()
        self.scanline = ScanlineOverlay(self.w, self.h)
        self._action  = None
        self._mouse   = (0, 0)
        self._section = 0
        self._scroll  = 0
        self._btn_back  = pygame.Rect(20, 16, 110, 34)
        self._btn_prev  = pygame.Rect(self.w // 2 - 200, self.h - 60, 90, 36)
        self._btn_next  = pygame.Rect(self.w // 2 + 110, self.h - 60, 90, 36)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._mouse = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self._btn_back.collidepoint(pos):
                self._action = "menu"
            elif self._btn_prev.collidepoint(pos) and self._section > 0:
                self._section -= 1
            elif self._btn_next.collidepoint(pos) and self._section < len(GUIDE_SECTIONS) - 1:
                self._section += 1
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._action = "menu"
            elif event.key == pygame.K_RIGHT:
                self._section = min(self._section + 1, len(GUIDE_SECTIONS) - 1)
            elif event.key == pygame.K_LEFT:
                self._section = max(self._section - 1, 0)

    def update(self, dt):
        action = self._action
        self._action = None
        return action

    def draw(self):
        surf = self.screen
        surf.fill(C_BG)

        pygame.draw.rect(surf, C_BG2, (0, 0, self.w, 56))
        draw_text(surf, "📖 GUIDE DU JEU",
                  self.w // 2, 20, C_GREEN, 20, bold=True, center=True)
        hov = self._btn_back.collidepoint(self._mouse)
        draw_button(surf, self._btn_back, "◀ MENU", C_GRAY, hover=hov, size=13)

        # Tabs
        tab_w = (self.w - 80) // len(GUIDE_SECTIONS)
        for i, (title, _) in enumerate(GUIDE_SECTIONS):
            tx    = 40 + i * tab_w
            t_rect = pygame.Rect(tx, 64, tab_w - 4, 28)
            active = i == self._section
            pygame.draw.rect(surf, (15, 35, 15) if active else C_BG2, t_rect, border_radius=4)
            pygame.draw.rect(surf, C_GREEN if active else C_BORDER, t_rect, 1, border_radius=4)
            short = title.split(" ", 1)[0]
            draw_text(surf, short, t_rect.centerx, t_rect.centery,
                      C_GREEN if active else C_GRAY, 13, center=True)

        # Contenu
        title, content = GUIDE_SECTIONS[self._section]
        content_rect = pygame.Rect(60, 106, self.w - 120, self.h - 180)
        pygame.draw.rect(surf, C_BG2, content_rect, border_radius=10)
        pygame.draw.rect(surf, C_BORDER, content_rect, 1, border_radius=10)

        draw_text(surf, title, content_rect.x + 20, content_rect.y + 18,
                  C_GREEN, 18, bold=True)
        pygame.draw.line(surf, C_BORDER,
                         (content_rect.x + 16, content_rect.y + 46),
                         (content_rect.right - 16, content_rect.y + 46))

        y = content_rect.y + 58
        for line in content.strip().split("\n"):
            col  = C_GREEN if line.startswith("•") else (C_YELLOW if line.startswith("🏆") or line.endswith(":") else C_WHITE)
            sz   = 14
            draw_text_wrapped(surf, line, content_rect.x + 20, y,
                              content_rect.w - 40, col, sz, 22)
            y += 24

        # Nav
        hov_p = self._btn_prev.collidepoint(self._mouse)
        hov_n = self._btn_next.collidepoint(self._mouse)
        if self._section > 0:
            draw_button(surf, self._btn_prev, "◀ PRÉC", C_GREEN_MID, hover=hov_p, size=13)
        if self._section < len(GUIDE_SECTIONS) - 1:
            draw_button(surf, self._btn_next, "SUIV ▶", C_GREEN_MID, hover=hov_n, size=13)

        # Indicateur
        draw_text(surf, f"{self._section + 1} / {len(GUIDE_SECTIONS)}",
                  self.w // 2, self.h - 46, C_GREEN_DIM, 13, center=True)

        self.scanline.draw(surf)


# ═══════════════════════════════════════════════════════════════════════════════
# Contact
# ═══════════════════════════════════════════════════════════════════════════════

class ContactScreen:
    def __init__(self, screen):
        self.screen   = screen
        self.w, self.h = screen.get_size()
        self.scanline = ScanlineOverlay(self.w, self.h)
        self._action  = None
        self._mouse   = (0, 0)
        self._fields  = {"subject": "", "message": ""}
        self._active  = "subject"
        self._category = "bug"
        self._categories = ["bug", "suggestion", "other"]
        self._error   = ""
        self._success = ""
        self._loading = False
        self._t       = 0.0
        self._btn_back   = pygame.Rect(20, 16, 110, 34)
        self._btn_submit = pygame.Rect(self.w // 2 - 160, 560, 320, 44)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._mouse = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self._btn_back.collidepoint(pos):
                self._action = "menu"
                return
            # Champs
            subj_rect = pygame.Rect(self.w // 2 - 220, 220, 440, 42)
            msg_rect  = pygame.Rect(self.w // 2 - 220, 340, 440, 140)
            if subj_rect.collidepoint(pos):
                self._active = "subject"
            elif msg_rect.collidepoint(pos):
                self._active = "message"
            # Catégories
            for i, cat in enumerate(self._categories):
                cr = pygame.Rect(self.w // 2 - 220 + i * 152, 290, 144, 34)
                if cr.collidepoint(pos):
                    self._category = cat
            if self._btn_submit.collidepoint(pos):
                self._send()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._action = "menu"
            elif event.key == pygame.K_TAB:
                self._active = "message" if self._active == "subject" else "subject"
            elif event.key == pygame.K_BACKSPACE:
                self._fields[self._active] = self._fields[self._active][:-1]
            elif event.unicode:
                if self._active == "subject" and len(self._fields["subject"]) < 100:
                    self._fields["subject"] += event.unicode
                elif self._active == "message" and len(self._fields["message"]) < 500:
                    self._fields["message"] += event.unicode

    def _send(self):
        if not self._fields["subject"] or not self._fields["message"]:
            self._error = "Remplissez le sujet et le message."
            return
        self._loading = True
        def do():
            data, code = api.contact(
                self._fields["subject"],
                self._fields["message"],
                self._category,
            )
            self._loading = False
            if code == 201:
                self._success = "Message envoyé ! Nous vous répondrons rapidement."
                self._fields  = {"subject": "", "message": ""}
                self._error   = ""
            else:
                self._error = data.get("detail", "Erreur d'envoi.")
        threading.Thread(target=do, daemon=True).start()

    def update(self, dt):
        self._t += dt
        action = self._action
        self._action = None
        return action

    def draw(self):
        surf = self.screen
        surf.fill(C_BG)
        pygame.draw.rect(surf, C_BG2, (0, 0, self.w, 56))
        draw_text(surf, "✉ NOUS CONTACTER",
                  self.w // 2, 20, C_GREEN, 20, bold=True, center=True)
        hov = self._btn_back.collidepoint(self._mouse)
        draw_button(surf, self._btn_back, "◀ MENU", C_GRAY, hover=hov, size=13)

        draw_text(surf, "Un problème dans le jeu ? Une suggestion ?",
                  self.w // 2, 80, C_WHITE, 15, center=True)
        draw_text(surf, "Contactez-nous via ce formulaire.",
                  self.w // 2, 104, C_GREEN_MID, 13, center=True)

        # Sujet
        subj_rect = pygame.Rect(self.w // 2 - 220, 220, 440, 42)
        draw_input(surf, subj_rect, self._fields["subject"], "SUJET",
                   active=self._active == "subject", placeholder="Décrivez brièvement le problème")

        # Catégorie
        cat_labels = {"bug": "🐛 Bug", "suggestion": "💡 Suggestion", "other": "✉ Autre"}
        for i, cat in enumerate(self._categories):
            cr = pygame.Rect(self.w // 2 - 220 + i * 152, 290, 144, 34)
            active = self._category == cat
            pygame.draw.rect(surf, (15, 35, 15) if active else C_BG2, cr, border_radius=6)
            pygame.draw.rect(surf, C_GREEN if active else C_BORDER, cr, 2, border_radius=6)
            draw_text(surf, cat_labels[cat], cr.centerx, cr.centery,
                      C_GREEN if active else C_GRAY, 13, center=True)

        # Message
        msg_rect = pygame.Rect(self.w // 2 - 220, 340, 440, 140)
        draw_input(surf, msg_rect, self._fields["message"], "MESSAGE",
                   active=self._active == "message",
                   placeholder="Décrivez le problème en détail...")

        # Bouton
        hov_s = self._btn_submit.collidepoint(self._mouse)
        draw_button(surf, self._btn_submit, "✓  ENVOYER", C_GREEN, hover=hov_s)

        if self._error:
            draw_text(surf, f"⚠ {self._error}", self.w // 2, 615, C_RED, 13, center=True)
        if self._success:
            draw_text(surf, f"✓ {self._success}", self.w // 2, 615, C_GREEN, 13, center=True)
        if self._loading:
            dots = "." * (int(self._t * 3) % 4)
            draw_text(surf, f"Envoi{dots}", self.w // 2, 615, C_GREEN_MID, 13, center=True)

        self.scanline.draw(surf)


# ═══════════════════════════════════════════════════════════════════════════════
# Certificat
# ═══════════════════════════════════════════════════════════════════════════════

class CertificateScreen:
    def __init__(self, screen, level_slug):
        self.screen     = screen
        self.w, self.h  = screen.get_size()
        self.level_slug = level_slug
        self.scanline   = ScanlineOverlay(self.w, self.h)
        self._action    = None
        self._mouse     = (0, 0)
        self._t         = 0.0
        self._cert      = None
        self._loading   = True
        self._error     = ""
        self._btn_back  = pygame.Rect(20, 16, 110, 34)
        self._btn_dl    = pygame.Rect(self.w // 2 - 180, 560, 360, 48)
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        data, code = api.generate_certificate(self.level_slug)
        self._loading = False
        if code == 200:
            self._cert = data
        else:
            self._error = data.get("detail", "Impossible de générer le certificat.")

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._mouse = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._btn_back.collidepoint(event.pos):
                self._action = "menu"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._action = "menu"

    def update(self, dt):
        self._t += dt
        action = self._action
        self._action = None
        return action

    def draw(self):
        import math
        surf = self.screen
        surf.fill(C_BG)

        # Fond décoratif
        for i in range(20):
            y = i * 40
            pygame.draw.line(surf, (8, 20, 8), (0, y), (self.w, y))

        pygame.draw.rect(surf, C_BG2, (0, 0, self.w, 56))
        draw_text(surf, "🏆 CERTIFICAT DE COMPLÉTION",
                  self.w // 2, 20, C_GOLD, 20, bold=True, center=True)
        hov = self._btn_back.collidepoint(self._mouse)
        draw_button(surf, self._btn_back, "◀ MENU", C_GRAY, hover=hov, size=13)

        if self._loading:
            dots = "." * (int(self._t * 3) % 4)
            draw_text(surf, f"Génération du certificat{dots}",
                      self.w // 2, self.h // 2, C_GREEN_MID, 18, center=True)
            self.scanline.draw(surf)
            return

        if self._error:
            draw_text(surf, f"⚠ {self._error}",
                      self.w // 2, self.h // 2, C_RED, 16, center=True)
            self.scanline.draw(surf)
            return

        # Carte certificat
        cert_rect = pygame.Rect(self.w // 2 - 280, 80, 560, 440)
        pygame.draw.rect(surf, (5, 15, 5), cert_rect, border_radius=16)
        pygame.draw.rect(surf, C_GOLD, cert_rect, 3, border_radius=16)

        # Coins
        for cx_, cy_ in [(cert_rect.x + 16, cert_rect.y + 16),
                          (cert_rect.right - 16, cert_rect.y + 16),
                          (cert_rect.x + 16, cert_rect.bottom - 16),
                          (cert_rect.right - 16, cert_rect.bottom - 16)]:
            pygame.draw.circle(surf, C_GOLD, (cx_, cy_), 6)

        # Étoiles animées
        for i in range(5):
            sx   = cert_rect.x + 80 + i * 100
            sy   = cert_rect.y + 36
            sc_s = abs(math.sin(self._t * 2 + i)) * 4
            draw_text(surf, "★", sx, sy, C_GOLD, int(20 + sc_s), center=True)

        draw_text(surf, "H4CKR", cert_rect.centerx, cert_rect.y + 80,
                  C_GREEN, 38, bold=True, center=True)
        draw_text(surf, "CERTIFICAT DE COMPLÉTION",
                  cert_rect.centerx, cert_rect.y + 130, C_GOLD, 18, center=True)

        pygame.draw.line(surf, C_GOLD,
                         (cert_rect.x + 40, cert_rect.y + 158),
                         (cert_rect.right - 40, cert_rect.y + 158))

        draw_text(surf, "Ce certificat atteste que",
                  cert_rect.centerx, cert_rect.y + 178, C_WHITE, 14, center=True)

        pseudo = (api.user or {}).get("pseudo", "AGENT")
        draw_text(surf, pseudo.upper(), cert_rect.centerx, cert_rect.y + 208,
                  C_GREEN, 28, bold=True, center=True)

        level_label = "DÉBUTANT" if self.level_slug == "beginner" else "EXPERT"
        draw_text(surf, f"a complété avec succès le niveau {level_label}",
                  cert_rect.centerx, cert_rect.y + 260, C_WHITE, 15, center=True)

        score = self._cert.get("score", 0) if self._cert else 0
        draw_text(surf, f"Score final : {score} points",
                  cert_rect.centerx, cert_rect.y + 294, C_YELLOW, 18, bold=True, center=True)

        if self._cert:
            code = self._cert.get("unique_code", "")[:16]
            draw_text(surf, f"Code : {code}",
                      cert_rect.centerx, cert_rect.y + 340, C_GRAY, 12, center=True)

        # Bouton télécharger
        hov_dl = self._btn_dl.collidepoint(self._mouse)
        draw_button(surf, self._btn_dl, "⬇  TÉLÉCHARGER LE PDF", C_GOLD, hover=hov_dl, size=15)
        draw_text(surf, "(Le PDF est généré automatiquement par le serveur)",
                  self.w // 2, self._btn_dl.bottom + 14, C_GRAY, 12, center=True)

        self.scanline.draw(surf)
