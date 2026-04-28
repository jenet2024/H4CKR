"""Écran de jeu principal — énigmes, terminal, progression, points."""
import pygame
import math
import time
from config import *
from src.utils.renderer import (
    draw_text, draw_button, draw_input, draw_text_wrapped,
    ScanlineOverlay, ProgressBar, Notification, get_font,
)
from src.utils.api import api


class GameScreen:
    def __init__(self, screen, level_slug="beginner"):
        self.screen      = screen
        self.w, self.h   = screen.get_size()
        self.level_slug  = level_slug
        self.scanline    = ScanlineOverlay(self.w, self.h)

        # State
        self._action     = None
        self._mouse      = (0, 0)
        self._t          = 0.0
        self._start_time = time.time()

        # Level data
        self.level        = None
        self.enigmas      = []
        self.current_idx  = 0
        self.total_points = 0
        self._notifications = []

        # Answer input
        self.answer_input = ""
        self.answer_active = False
        self.answer_feedback = ""
        self.answer_correct = False
        self._feedback_t = 0.0

        # Terminal (expert)
        self.terminal_history = [
            ("output", "H4CKR Terminal v2.1 — Tapez 'help' pour les commandes."),
        ]
        self.terminal_input   = ""
        self.terminal_active  = False
        self._terminal_scroll = 0

        # Progression bar
        self.progress_bar = ProgressBar(20, self.h - 30, self.w - 40, 12)

        # Sidebar
        self._show_hint   = False
        self._hint_text   = ""
        self._hint_used   = 0

        # Boutons
        self._btn_submit  = pygame.Rect(0, 0, 180, 40)
        self._btn_hint    = pygame.Rect(0, 0, 120, 36)
        self._btn_menu    = pygame.Rect(self.w - 130, 10, 120, 34)

        # Midpoint badge (beginner seulement)
        self._midpoint_shown = False
        self._midpoint_anim  = 0.0
        self._show_midpoint  = False

        self._load_level()

    def _load_level(self):
        data, code = api.get_levels()
        if code != 200:
            return
        for lvl in data:
            if lvl["slug"] == self.level_slug:
                self.level   = lvl
                self.enigmas = [e for e in lvl.get("enigmas", []) if not e.get("solved")]
                # Points déjà acquis
                for e in lvl.get("enigmas", []):
                    if e.get("solved"):
                        self.total_points += e.get("points", 0)
                break
        self._update_progress()

    def _update_progress(self):
        if not self.enigmas:
            return
        total   = len(self.level.get("enigmas", [])) if self.level else len(self.enigmas)
        solved  = total - len(self.enigmas) + self.current_idx
        self.progress_bar.set_value(solved / max(total, 1))

    @property
    def current_enigma(self):
        idx = self.current_idx
        unsolved = [e for e in self.enigmas if not e.get("solved")]
        if idx < len(unsolved):
            return unsolved[idx]
        return None

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._mouse = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._on_click(event.pos)
        if event.type == pygame.KEYDOWN:
            self._on_key(event)

    def _on_click(self, pos):
        # Fermer midpoint
        if self._show_midpoint:
            self._show_midpoint = False
            return

        if self._btn_menu.collidepoint(pos):
            self._action = "menu"
            return

        enigma = self.current_enigma
        if not enigma:
            return

        is_terminal = self.level_slug == "expert" and enigma.get("type") == "terminal"

        if is_terminal:
            term_rect = self._get_terminal_rect()
            if term_rect.collidepoint(pos):
                self.terminal_active = True
                self.answer_active   = False
            else:
                self.terminal_active = False
        else:
            ans_rect = self._get_answer_rect()
            if ans_rect.collidepoint(pos):
                self.answer_active = True
            else:
                self.answer_active = False

        if self._btn_submit.collidepoint(pos):
            self._submit_answer()
        elif self._btn_hint.collidepoint(pos):
            self._request_hint()

    def _on_key(self, event):
        if self._show_midpoint:
            self._show_midpoint = False
            return

        enigma = self.current_enigma
        if not enigma:
            return
        is_terminal = self.level_slug == "expert" and enigma.get("type") == "terminal"

        if is_terminal and self.terminal_active:
            if event.key == pygame.K_RETURN:
                self._run_terminal_command()
            elif event.key == pygame.K_BACKSPACE:
                self.terminal_input = self.terminal_input[:-1]
            elif event.unicode:
                self.terminal_input += event.unicode
        elif self.answer_active or not is_terminal:
            if event.key == pygame.K_RETURN:
                self._submit_answer()
            elif event.key == pygame.K_BACKSPACE:
                self.answer_input = self.answer_input[:-1]
            elif event.unicode and event.key != pygame.K_ESCAPE:
                self.answer_input += event.unicode

    # ── API calls ─────────────────────────────────────────────────────────────

    def _submit_answer(self):
        enigma = self.current_enigma
        if not enigma or not self.answer_input.strip():
            return
        data, code = api.submit_answer(enigma["id"], self.answer_input.strip())
        if code == 200:
            correct = data.get("correct", False)
            msg     = data.get("message", "")
            pts     = data.get("points_earned", 0)
            badge   = data.get("badge_earned")
            if correct:
                self.total_points   += pts
                self.answer_input    = ""
                self.answer_feedback = msg
                self.answer_correct  = True
                self._feedback_t     = 0.0
                notif_text = msg
                if badge:
                    notif_text += f"  🏆 Badge : {badge['name']}"
                self._notifications.append(
                    Notification(notif_text, C_GREEN, duration=4.0))

                # Avance à l'énigme suivante
                self.current_idx += 1
                self._update_progress()
                self._hint_text = ""
                self._hint_used = 0

                # Midpoint débutant (après enigme 5)
                if (self.level_slug == "beginner"
                        and self.current_idx == 5
                        and not self._midpoint_shown):
                    self._midpoint_shown = True
                    self._show_midpoint  = True

                # Niveau terminé
                if self.current_idx >= len([e for e in self.enigmas if not e.get("solved")]):
                    self._action = f"finished_{self.level_slug}"
            else:
                self.answer_feedback = msg
                self.answer_correct  = False
                self._feedback_t     = 0.0
                hint = data.get("hint")
                if hint:
                    self._hint_text = hint
                self._notifications.append(
                    Notification(msg, C_RED, duration=3.0))

    def _request_hint(self):
        enigma = self.current_enigma
        if not enigma:
            return
        data, code = api.get_hint(enigma["id"])
        if code == 200:
            hint = data.get("hint")
            if hint:
                self._hint_text = hint
                self._hint_used += 1
                self._notifications.append(
                    Notification(f"Indice {self._hint_used}/3 (-10 pts)", C_YELLOW, 3.0))
            else:
                self._notifications.append(
                    Notification("Plus d'indices disponibles.", C_GRAY, 2.0))

    def _run_terminal_command(self):
        cmd = self.terminal_input.strip()
        if not cmd:
            return
        self.terminal_history.append(("input", f"$ {cmd}"))
        self.terminal_input = ""

        if cmd.lower() == "clear":
            self.terminal_history = []
            return

        data, code = api.terminal_command(cmd, enigma_id=self.current_enigma["id"]
                                          if self.current_enigma else None)
        if code == 200:
            output = data.get("output", "")
            pts    = data.get("points_earned", 0)
            if output == "__CLEAR__":
                self.terminal_history = []
            else:
                for line in output.split("\n"):
                    self.terminal_history.append(("output", line))
            if pts > 0:
                self.total_points += pts
                self._notifications.append(
                    Notification(f"+{pts} pts", C_GREEN, 2.0))
        else:
            self.terminal_history.append(("error", "Erreur de connexion au serveur."))

        self._terminal_scroll = max(0, len(self.terminal_history) - 18)

    # ── Layout helpers ────────────────────────────────────────────────────────

    def _get_answer_rect(self):
        return pygame.Rect(self.w // 2 - 240, self.h - 160, 360, 42)

    def _get_terminal_rect(self):
        return pygame.Rect(20, 320, self.w - 40, self.h - 380)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        self._t          += dt
        self._feedback_t += dt
        self._midpoint_anim = min(1.0, self._midpoint_anim + dt * 3)

        # Notifications
        for n in self._notifications[:]:
            n.update(dt)
            if n.done:
                self._notifications.remove(n)

        action = self._action
        self._action = None
        return action

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self):
        surf = self.screen
        surf.fill(C_BG)

        # Grille fond
        for gx in range(0, self.w, 50):
            pygame.draw.line(surf, (8, 18, 8), (gx, 0), (gx, self.h))
        for gy in range(0, self.h, 50):
            pygame.draw.line(surf, (8, 18, 8), (0, gy), (self.w, gy))

        # ── Header ────────────────────────────────────────────────────────────
        pygame.draw.rect(surf, C_BG2, (0, 0, self.w, 56))
        pygame.draw.line(surf, C_BORDER, (0, 56), (self.w, 56))

        level_label = "DÉBUTANT" if self.level_slug == "beginner" else "EXPERT"
        col_label   = C_GREEN   if self.level_slug == "beginner" else C_RED
        draw_text(surf, f"H4CKR — NIVEAU {level_label}",
                  20, 18, col_label, 16, bold=True)

        # Timer
        elapsed = int(time.time() - self._start_time)
        mins, secs = divmod(elapsed, 60)
        draw_text(surf, f"⏱ {mins:02d}:{secs:02d}",
                  self.w // 2, 20, C_GREEN_MID, 14, center=True)

        # Points
        draw_text(surf, f"⭐ {self.total_points} pts",
                  self.w - 160, 20, C_YELLOW, 15, bold=True)

        # Bouton menu
        hov_menu = self._btn_menu.collidepoint(self._mouse)
        draw_button(surf, self._btn_menu, "◀ MENU", C_GRAY, hover=hov_menu, size=13)

        # ── Progress bar ──────────────────────────────────────────────────────
        self.progress_bar.draw(surf)
        enigma_list = self.level.get("enigmas", []) if self.level else self.enigmas
        total_e  = len(enigma_list)
        solved_e = sum(1 for e in enigma_list if e.get("solved"))
        draw_text(surf, f"PROGRESSION : {solved_e + self.current_idx}/{total_e}",
                  20, self.h - 48, C_GREEN_MID, 12)

        enigma = self.current_enigma
        if not enigma:
            # Niveau terminé
            draw_text(surf, "✓ NIVEAU TERMINÉ !",
                      self.w // 2, self.h // 2, C_GREEN, 28, bold=True, center=True)
            draw_text(surf, "Retournez au menu pour obtenir votre certificat.",
                      self.w // 2, self.h // 2 + 50, C_WHITE, 16, center=True)
            self.scanline.draw(surf)
            return

        is_terminal = (self.level_slug == "expert"
                       and enigma.get("type") == "terminal")

        # ── Sidebar énigme ────────────────────────────────────────────────────
        sidebar_w = 340
        sidebar   = pygame.Rect(self.w - sidebar_w - 10, 66, sidebar_w, self.h - 110)
        pygame.draw.rect(surf, C_BG2, sidebar, border_radius=8)
        pygame.draw.rect(surf, C_BORDER, sidebar, 1, border_radius=8)

        # Numéro
        all_enigmas   = self.level.get("enigmas", []) if self.level else self.enigmas
        unsolved      = [e for e in all_enigmas if not e.get("solved")]
        enigma_num    = self.current_idx + 1
        enigma_total  = len(unsolved)
        type_colors   = {
            "base64": C_CYAN, "caesar": C_YELLOW, "stegano": C_GREEN,
            "audio": C_ORANGE, "logs": C_RED, "terminal": C_RED,
            "metadata": C_CYAN,
        }
        type_col = type_colors.get(enigma.get("type", ""), C_WHITE)

        draw_text(surf, f"ÉNIGME {enigma_num}/{enigma_total}",
                  sidebar.x + 12, sidebar.y + 12, C_GREEN_MID, 12)
        draw_text(surf, enigma.get("title", ""), sidebar.x + 12, sidebar.y + 32,
                  C_GREEN, 16, bold=True)

        # Tag type
        tag_rect = pygame.Rect(sidebar.x + 12, sidebar.y + 58, 100, 22)
        pygame.draw.rect(surf, (10, 25, 10), tag_rect, border_radius=4)
        pygame.draw.rect(surf, type_col, tag_rect, 1, border_radius=4)
        draw_text(surf, enigma.get("type", "").upper(),
                  tag_rect.centerx, tag_rect.centery, type_col, 11, center=True)

        # Description
        draw_text_wrapped(surf, enigma.get("description", ""),
                          sidebar.x + 12, sidebar.y + 92,
                          sidebar_w - 24, C_WHITE, 13, line_height=20)

        # Indice
        if self._hint_text:
            hint_y = sidebar.y + 280
            pygame.draw.rect(surf, (15, 30, 10),
                             pygame.Rect(sidebar.x + 8, hint_y, sidebar_w - 16, 80),
                             border_radius=6)
            pygame.draw.rect(surf, C_YELLOW,
                             pygame.Rect(sidebar.x + 8, hint_y, sidebar_w - 16, 80),
                             1, border_radius=6)
            draw_text(surf, "💡 INDICE :", sidebar.x + 16, hint_y + 8, C_YELLOW, 12)
            draw_text_wrapped(surf, self._hint_text,
                              sidebar.x + 16, hint_y + 26,
                              sidebar_w - 32, C_YELLOW, 12)

        # Bouton indice
        self._btn_hint.topleft = (sidebar.x + 12, sidebar.bottom - 100)
        hov_hint = self._btn_hint.collidepoint(self._mouse)
        draw_button(surf, self._btn_hint, "💡 INDICE", C_YELLOW, hover=hov_hint, size=13)
        draw_text(surf, f"({self._hint_used}/3 utilisés, -10 pts)",
                  sidebar.x + 140, sidebar.bottom - 94, C_GRAY, 11)

        # ── Zone principale ───────────────────────────────────────────────────
        main_w = self.w - sidebar_w - 40
        main_rect = pygame.Rect(10, 66, main_w, self.h - 110)

        if is_terminal:
            self._draw_terminal(surf, main_rect)
        else:
            self._draw_enigma_zone(surf, main_rect, enigma)

        # ── Notifications ─────────────────────────────────────────────────────
        for i, notif in enumerate(self._notifications):
            notif.draw(surf, self.w // 2, 80 + i * 50)

        # ── Midpoint popup ────────────────────────────────────────────────────
        if self._show_midpoint:
            self._draw_midpoint_popup(surf)

        self.scanline.draw(surf)

    def _draw_enigma_zone(self, surf, rect, enigma):
        pygame.draw.rect(surf, C_BG2, rect, border_radius=8)
        pygame.draw.rect(surf, C_BORDER, rect, 1, border_radius=8)

        draw_text(surf, "> SAISISSEZ VOTRE RÉPONSE",
                  rect.x + 16, rect.y + 16, C_GREEN_MID, 13)

        # Fichier lié
        if enigma.get("file_path"):
            fp = enigma["file_path"].split("/")[-1]
            draw_text(surf, f"📎 Fichier : {fp}",
                      rect.x + 16, rect.y + 50, C_CYAN, 14)
            draw_text(surf, "(Téléchargez le fichier depuis le menu — voir guide)",
                      rect.x + 16, rect.y + 72, C_GRAY, 12)

        # Input réponse
        ans_rect = pygame.Rect(rect.x + 16, rect.bottom - 130, rect.w - 32, 44)
        draw_input(surf, ans_rect, self.answer_input, "VOTRE RÉPONSE",
                   active=self.answer_active, placeholder="Entrez le mot/code trouvé...")

        # Bouton soumettre
        self._btn_submit.topleft = (ans_rect.right - 188, ans_rect.bottom + 12)
        hov_sub = self._btn_submit.collidepoint(self._mouse)
        draw_button(surf, self._btn_submit, "✓  VALIDER", C_GREEN, hover=hov_sub, size=14)

        # Feedback
        if self._feedback_t < 3.0 and self.answer_feedback:
            col = C_GREEN if self.answer_correct else C_RED
            draw_text(surf, self.answer_feedback,
                      rect.centerx, ans_rect.top - 20,
                      col, 14, center=True)

    def _draw_terminal(self, surf, rect):
        pygame.draw.rect(surf, (3, 8, 3), rect, border_radius=8)
        pygame.draw.rect(surf, C_GREEN, rect, 2, border_radius=8)

        # Barre titre terminal
        title_rect = pygame.Rect(rect.x, rect.y, rect.w, 32)
        pygame.draw.rect(surf, (8, 20, 8), title_rect, border_radius=8)
        for i, (cx_, col_) in enumerate([(rect.x+14, C_RED), (rect.x+30, C_YELLOW), (rect.x+46, C_GREEN_MID)]):
            pygame.draw.circle(surf, col_, (cx_, rect.y+16), 6)
        draw_text(surf, "root@h4ckr:~#",
                  rect.x + 70, rect.y + 10, C_GREEN_MID, 14)

        # Historique
        line_h  = 20
        visible = (rect.h - 80) // line_h
        start   = max(0, len(self.terminal_history) - visible - self._terminal_scroll)
        end     = start + visible

        for i, (kind, line) in enumerate(self.terminal_history[start:end]):
            col = C_GREEN if kind == "output" else (C_WHITE if kind == "input" else C_RED)
            # Tronque si trop long
            font = get_font(14)
            max_chars = (rect.w - 24) // max(font.size("A")[0], 1)
            draw_text(surf, line[:max_chars],
                      rect.x + 12,
                      rect.y + 38 + i * line_h,
                      col, 14)

        # Input
        input_rect = pygame.Rect(rect.x + 1, rect.bottom - 44, rect.w - 2, 42)
        pygame.draw.rect(surf, (5, 12, 5), input_rect)
        pygame.draw.line(surf, C_GREEN_DIM,
                         (rect.x, rect.bottom - 44),
                         (rect.right, rect.bottom - 44))

        cursor = "█" if (int(self._t * 2) % 2 == 0) else " "
        draw_text(surf, f"$ {self.terminal_input}{cursor}",
                  rect.x + 12, rect.bottom - 30, C_GREEN, 14)

        # Bouton valider terminal
        self._btn_submit.topleft = (rect.right - 200, rect.bottom - 38)
        hov = self._btn_submit.collidepoint(self._mouse)
        draw_button(surf, self._btn_submit, "↵  ENTRÉE", C_GREEN, hover=hov, size=13)

    def _draw_midpoint_popup(self, surf):
        """Badge midpoint débutant (après 5 énigmes)."""
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        pw, ph = 520, 360
        popup = pygame.Rect(self.w // 2 - pw // 2, self.h // 2 - ph // 2, pw, ph)
        pygame.draw.rect(surf, C_BG2, popup, border_radius=14)
        pygame.draw.rect(surf, C_GOLD, popup, 3, border_radius=14)

        # Étoiles animées
        for i in range(5):
            sx = popup.x + 60 + i * 80
            sy = popup.y + 40
            scale = abs(math.sin(self._t * 2 + i)) * 4
            draw_text(surf, "★", sx, sy, C_GOLD, int(24 + scale), center=True)

        draw_text(surf, "FÉLICITATIONS !",
                  self.w // 2, popup.y + 80, C_GOLD, 26, bold=True, center=True)
        draw_text(surf, "Vous avez terminé les 5 premières étapes.",
                  self.w // 2, popup.y + 120, C_WHITE, 15, center=True)

        # Badge
        badge_rect = pygame.Rect(self.w // 2 - 60, popup.y + 150, 120, 80)
        pygame.draw.rect(surf, (20, 40, 10), badge_rect, border_radius=10)
        pygame.draw.rect(surf, C_GOLD, badge_rect, 2, border_radius=10)
        draw_text(surf, "🎖", self.w // 2, popup.y + 172, C_GOLD, 28, center=True)
        draw_text(surf, "INITIÉ CYBER",
                  self.w // 2, popup.y + 207, C_GOLD, 13, bold=True, center=True)

        draw_text(surf, f"Il vous reste {5} étapes avant la certification.",
                  self.w // 2, popup.y + 260, C_GREEN, 14, center=True)
        draw_text(surf, "[ Cliquez pour continuer ]",
                  self.w // 2, popup.y + 300, C_GRAY, 13, center=True)
