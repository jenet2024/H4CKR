"""
Terminal interactif style TryHackMe pour le mode Expert.
Panel gauche : mission + contexte
Panel droite : vrai terminal Pygame avec subprocess
"""
import subprocess
import threading
import math
import pygame
from typing import List
from client.core.settings import Settings

# Commandes autorisées (whitelist sécurité)
ALLOWED_CMDS = {"echo", "ping", "nslookup", "ipconfig", "whoami",
                "dir", "ls", "cat", "type", "base64", "python",
                "h4ckr"}  # commandes custom du jeu


class TerminalScreen:
    """
    Terminal interactif avec historique, prompt animé, sortie colorisée.
    Intégré dans les niveaux Expert.
    """
    def __init__(self, screen: pygame.Surface, settings: Settings,
                 mission_title: str, mission_desc: str,
                 objectives: List[str], custom_commands: dict = None):
        self.screen      = screen
        self.settings    = settings
        self.mission     = mission_title
        self.desc        = mission_desc
        self.objectives  = objectives
        self.custom_cmds = custom_commands or {}  # cmd_name → (func, help_text)

        self.font_mono   = pygame.font.SysFont("Consolas", 15)
        self.font_title  = settings.load_font(18)
        self.font_small  = settings.load_font(13)

        self.history:     List[str] = [
            "h4ckR Terminal v1.0 — Mode Elite Hacker",
            "Tapez 'help' pour la liste des commandes",
            "─" * 50,
        ]
        self.input_line  = ""
        self.cmd_history: List[str] = []
        self.hist_idx    = -1
        self.scroll_off  = 0
        self.t           = 0.0
        self._running_cmd = False

        # Layout
        W, H = screen.get_size()
        panel_top  = 50
        panel_bot  = H - 16
        self.mission_rect  = pygame.Rect(0, panel_top, W // 3, panel_bot - panel_top)
        self.terminal_rect = pygame.Rect(W // 3 + 4, panel_top, W - W // 3 - 4, panel_bot - panel_top)

        # Visible lines
        line_h = 18
        self.max_visible = (self.terminal_rect.h - 44) // line_h

    # ── Event ────────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._execute(self.input_line.strip())
                if self.input_line.strip():
                    self.cmd_history.insert(0, self.input_line.strip())
                self.input_line = ""
                self.hist_idx   = -1
            elif event.key == pygame.K_BACKSPACE:
                self.input_line = self.input_line[:-1]
            elif event.key == pygame.K_UP:
                if self.cmd_history:
                    self.hist_idx = min(self.hist_idx + 1, len(self.cmd_history) - 1)
                    self.input_line = self.cmd_history[self.hist_idx]
            elif event.key == pygame.K_DOWN:
                if self.hist_idx > 0:
                    self.hist_idx -= 1
                    self.input_line = self.cmd_history[self.hist_idx]
                else:
                    self.hist_idx = -1
                    self.input_line = ""
            elif event.key == pygame.K_PAGEUP:
                self.scroll_off = min(self.scroll_off + 5, max(0, len(self.history) - self.max_visible))
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_off = max(0, self.scroll_off - 5)
            elif event.unicode.isprintable():
                self.input_line += event.unicode

    def update(self, dt: float):
        self.t += dt

    # ── Execute ──────────────────────────────────────────────────────────────────

    def _execute(self, cmd: str):
        if not cmd:
            return
        self.history.append(f"$ {cmd}")

        parts = cmd.split()
        base  = parts[0].lower() if parts else ""

        # Commandes custom du jeu
        if base in self.custom_cmds:
            func, _ = self.custom_cmds[base]
            result  = func(parts[1:])
            if isinstance(result, list):
                self.history.extend(result)
            else:
                self.history.append(str(result))
            return

        # Aide
        if base == "help":
            self.history.extend([
                "Commandes disponibles :",
                "  echo <texte>        — affiche du texte",
                "  ping <host>         — teste la connectivité",
                "  nslookup <host>     — résolution DNS",
                "  base64 <texte>      — encode en base64",
                "  ipconfig / whoami   — infos système",
                "  clear               — efface le terminal",
            ])
            for cmd_name, (_, help_txt) in self.custom_cmds.items():
                self.history.append(f"  {cmd_name:<20} — {help_txt}")
            return

        if base == "clear":
            self.history = ["Terminal effacé. 'help' pour les commandes.", "─"*50]
            return

        # Whitelist
        if base not in ALLOWED_CMDS:
            self.history.append(f"[ERREUR] Commande '{base}' non autorisée dans ce terminal.")
            return

        # Exécution réelle
        threading.Thread(target=self._run_subprocess, args=(cmd,), daemon=True).start()

    def _run_subprocess(self, cmd: str):
        try:
            self._running_cmd = True
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10,
                encoding="cp850", errors="replace"
            )
            lines = (result.stdout + result.stderr).splitlines()
            self.history.extend(lines[:50])  # max 50 lignes de sortie
        except subprocess.TimeoutExpired:
            self.history.append("[TIMEOUT] La commande a pris trop de temps.")
        except Exception as e:
            self.history.append(f"[ERREUR] {e}")
        finally:
            self._running_cmd = False

    # ── Draw ─────────────────────────────────────────────────────────────────────

    def draw(self):
        W, H = self.screen.get_size()
        self._draw_mission_panel()
        self._draw_terminal_panel()
        self._draw_separator(W)

    def _draw_mission_panel(self):
        r = self.mission_rect
        bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        bg.fill((4, 12, 4, 220))
        self.screen.blit(bg, r.topleft)
        pygame.draw.rect(self.screen, self.settings.COLOR_DANGER, r, 1)

        y = r.y + 10

        # Title
        title = self.font_title.render("[ MISSION ]", True, self.settings.COLOR_DANGER)
        self.screen.blit(title, (r.x + 10, y)); y += 32

        # Mission name
        lines = self._wrap(self.mission, r.w - 20, self.font_small)
        for line in lines:
            s = self.font_small.render(line, True, self.settings.COLOR_TEXT)
            self.screen.blit(s, (r.x + 10, y)); y += 18

        y += 10
        sep = self.font_small.render("─" * (r.w // 8), True, self.settings.COLOR_DANGER)
        self.screen.blit(sep, (r.x + 5, y)); y += 14

        # Description
        lines = self._wrap(self.desc, r.w - 20, self.font_small)
        for line in lines:
            s = self.font_small.render(line, True, self.settings.COLOR_TEXT_DIM)
            self.screen.blit(s, (r.x + 10, y)); y += 16

        y += 12
        obj_title = self.font_small.render("OBJECTIFS :", True, self.settings.COLOR_WARNING)
        self.screen.blit(obj_title, (r.x + 10, y)); y += 20

        for i, obj in enumerate(self.objectives):
            icon = "✓" if getattr(obj, '_done', False) else "◻"
            col  = self.settings.COLOR_SUCCESS if getattr(obj, '_done', False) else self.settings.COLOR_TEXT_DIM
            for line in self._wrap(f"{icon} {obj}", r.w - 20, self.font_small):
                s = self.font_small.render(line, True, col)
                self.screen.blit(s, (r.x + 10, y)); y += 16

    def _draw_terminal_panel(self):
        r = self.terminal_rect
        bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        bg.fill((2, 8, 2, 235))
        self.screen.blit(bg, r.topleft)
        pygame.draw.rect(self.screen, self.settings.COLOR_PRIMARY, r, 1)

        # Terminal title bar
        tbar = pygame.Surface((r.w, 22), pygame.SRCALPHA)
        tbar.fill((*self.settings.COLOR_PRIMARY, 40))
        self.screen.blit(tbar, r.topleft)
        title_s = self.font_small.render("root@h4ckr:~#", True, self.settings.COLOR_PRIMARY)
        self.screen.blit(title_s, (r.x + 8, r.y + 4))

        # History lines
        line_h = 18
        max_h  = r.h - 46

        visible_lines = self.history[-(self.max_visible + self.scroll_off):]
        if self.scroll_off:
            visible_lines = self.history[-(self.max_visible + self.scroll_off):-self.scroll_off]
        else:
            visible_lines = self.history[-self.max_visible:]

        for i, line in enumerate(visible_lines[-self.max_visible:]):
            y  = r.y + 24 + i * line_h
            if y > r.y + max_h:
                break
            col = self._line_color(line)
            surf = self.font_mono.render(line[:120], True, col)
            self.screen.blit(surf, (r.x + 6, y))

        # Loading dots
        if self._running_cmd:
            dots = "." * (int(self.t * 4) % 4)
            ls = self.font_mono.render(f"$ [En cours{dots}]", True, self.settings.COLOR_WARNING)
            self.screen.blit(ls, (r.x + 6, r.y + r.h - 38))
        else:
            # Prompt input
            cursor = "█" if int(self.t * 2) % 2 == 0 else " "
            prompt = f"$ {self.input_line}{cursor}"
            ps = self.font_mono.render(prompt, True, self.settings.COLOR_PRIMARY)
            self.screen.blit(ps, (r.x + 6, r.y + r.h - 38))

        pygame.draw.line(self.screen, self.settings.COLOR_PRIMARY,
                         (r.x, r.y + r.h - 44), (r.x + r.w, r.y + r.h - 44), 1)

    def _draw_separator(self, W: int):
        sx = self.mission_rect.right + 2
        pygame.draw.line(self.screen, self.settings.COLOR_BORDER,
                         (sx, 50), (sx, self.screen.get_height() - 16), 1)

    def _line_color(self, line: str) -> tuple:
        if line.startswith("$"):    return self.settings.COLOR_PRIMARY
        if "[ERREUR]" in line:      return self.settings.COLOR_ERROR
        if "[SUCCESS]" in line:     return self.settings.COLOR_SUCCESS
        if line.startswith("─"):    return self.settings.COLOR_TEXT_DIM
        if "Commandes" in line:     return self.settings.COLOR_ACCENT
        return (180, 220, 180)

    def _wrap(self, text: str, max_w: int, font) -> List[str]:
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = cur + (" " if cur else "") + w
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines or [""]

    def add_output(self, text: str):
        """Ajoute une ligne à la sortie depuis le code de niveau."""
        self.history.append(text)
