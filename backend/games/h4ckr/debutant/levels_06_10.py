"""Niveaux 6-10 débutant (fichier groupé pour la compacité — chaque classe est séparée)."""
import math, random, pygame
from client.games.h4ckr.base_level import BaseLevel
from client.core.settings import Settings


# ─── Niveau 6 — Firewall : ports ────────────────────────────────────────────────
PORTS = [
    (22,   "SSH",    True,  "Accès shell distant — RISQUE si exposé"),
    (80,   "HTTP",   False, "Web non chiffré — OK si serveur"),
    (443,  "HTTPS",  False, "Web chiffré — sécurisé"),
    (3389, "RDP",    True,  "Bureau à distance Windows — TRÈS risqué"),
    (1433, "MSSQL",  True,  "Base de données SQL — ne jamais exposer"),
    (8080, "AltHTTP",False, "Port alternatif web — surveillé"),
]
ANSWER_DANGEROUS = {22, 3389, 1433}


class Level06(BaseLevel):
    POINTS_BASE = 100
    def __init__(self, screen, settings):
        super().__init__(screen, settings, 6,
            "🔥 Firewall — Ports dangereux",
            "Clique sur tous les ports qui représentent un risque de sécurité.",
            hint_text="Les ports SSH (22), RDP (3389) et bases de données (1433)\nsont généralement les plus ciblés par les attaquants.")
        self.selected = set()
        self.validated = False
        self.t = 0.0
        self.btn_rects = {}
        self.msg = ""

    def handle_event(self, event):
        if self._solved: return
        if event.type == pygame.MOUSEBUTTONDOWN and not self.validated:
            for port, r in self.btn_rects.items():
                if r.collidepoint(event.pos):
                    if port in self.selected:
                        self.selected.remove(port)
                    else:
                        self.selected.add(port)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.selected == ANSWER_DANGEROUS:
                self._solved = True
            else:
                missing = ANSWER_DANGEROUS - self.selected
                wrong   = self.selected - ANSWER_DANGEROUS
                self.msg = f"❌ Manque: {missing}  Faux: {wrong}. Réessaie !"

    def update(self, dt):
        self.time_spent += dt; self.t = self.time_spent

    def draw(self):
        W, H = self.screen.get_size()
        self.draw_background()
        self.draw_level_header()
        d = self.font_small.render(self.description + " Puis appuyez ENTRÉE.", True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(d, d.get_rect(center=(W//2, 130)))

        self.btn_rects = {}
        cols = 3
        btn_w, btn_h = 280, 80
        gap = 20
        total_w = cols * btn_w + (cols-1)*gap
        sx = (W - total_w)//2
        sy = 160
        for i, (port, name, dangerous, desc) in enumerate(PORTS):
            row, col = divmod(i, cols)
            x = sx + col*(btn_w+gap)
            y = sy + row*(btn_h+gap)
            r = pygame.Rect(x, y, btn_w, btn_h)
            self.btn_rects[port] = r
            selected = port in self.selected
            color = self.settings.COLOR_DANGER if (dangerous and selected) else \
                    self.settings.COLOR_WARNING if selected else \
                    (0, 60, 30)
            bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            bg.fill((*color, 160 if selected else 80))
            self.screen.blit(bg, r.topleft)
            pygame.draw.rect(self.screen, color, r, 2, border_radius=6)
            port_s = self.font_body.render(f":{port}", True, color)
            self.screen.blit(port_s, (x+10, y+8))
            name_s = self.font_small.render(name, True, self.settings.COLOR_TEXT)
            self.screen.blit(name_s, (x+10, y+32))
            desc_s = self.font_small.render(desc[:30], True, self.settings.COLOR_TEXT_DIM)
            self.screen.blit(desc_s, (x+10, y+52))

        ent = self.font_small.render("ENTRÉE pour valider", True, self.settings.COLOR_ACCENT)
        ent.set_alpha(int(150+80*math.sin(self.t*2)))
        self.screen.blit(ent, ent.get_rect(center=(W//2, sy + 2*(btn_h+gap) + btn_h + 14)))
        if self.msg:
            ms = self.font_body.render(self.msg, True, self.settings.COLOR_ERROR)
            self.screen.blit(ms, ms.get_rect(center=(W//2, sy + 2*(btn_h+gap) + btn_h + 40)))
        if self._solved:
            self.draw_solved_overlay()


# ─── Niveau 7 — URL masquée ──────────────────────────────────────────────────────
SAFE_URLS = [
    "https://www.google.com/search?q=cyber",
    "https://fr.wikipedia.org/wiki/Cybersécurité",
]
DANGER_URLS = [
    "http://g00gle.com.securit-login.ru/auth",
    "https://paypal.com.login-verify789.xyz/account",
    "https://amazon.secure-payment.evil.cc/",
]
ALL_URLS = SAFE_URLS + DANGER_URLS
CORRECT_DANGER = set(DANGER_URLS)


class Level07(BaseLevel):
    POINTS_BASE = 100
    def __init__(self, screen, settings):
        super().__init__(screen, settings, 7,
            "🔗 URL Malveillante",
            "Identifie les URLs dangereuses parmi ces liens.",
            hint_text="Vérifie le domaine PRINCIPAL (avant le premier /).\n"
                      "Les sous-domaines trompeurs comme 'paypal.com.evil.com'\n"
                      "appartiennent en réalité à 'evil.com' !")
        self.selected = set()
        self.btn_rects = {}
        self.msg = ""
        self.t = 0.0

    def handle_event(self, event):
        if self._solved: return
        if event.type == pygame.MOUSEBUTTONDOWN:
            for url, r in self.btn_rects.items():
                if r.collidepoint(event.pos):
                    if url in self.selected: self.selected.remove(url)
                    else: self.selected.add(url)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.selected == CORRECT_DANGER:
                self._solved = True
            else:
                self.msg = "❌ Pas tout à fait. Réexamine chaque domaine !"

    def update(self, dt): self.time_spent += dt; self.t = self.time_spent

    def draw(self):
        W, H = self.screen.get_size()
        self.draw_background(); self.draw_level_header()
        d = self.font_small.render(self.description+" (ENTRÉE pour valider)", True, self.settings.COLOR_TEXT_DIM)
        self.screen.blit(d, d.get_rect(center=(W//2, 130)))

        self.btn_rects = {}
        fnt_mono = pygame.font.SysFont("Consolas", 15)
        btn_h = 44; gap = 10; btn_w = 680; sx = (W-btn_w)//2; sy = 155
        for i, url in enumerate(ALL_URLS):
            r = pygame.Rect(sx, sy+i*(btn_h+gap), btn_w, btn_h)
            self.btn_rects[url] = r
            sel = url in self.selected
            col = self.settings.COLOR_DANGER if sel else (0,60,30)
            bg = pygame.Surface((btn_w,btn_h),pygame.SRCALPHA)
            bg.fill((*col, 170 if sel else 80))
            self.screen.blit(bg, r.topleft)
            pygame.draw.rect(self.screen, col, r, 2, border_radius=5)
            u = fnt_mono.render(url, True, self.settings.COLOR_TEXT)
            self.screen.blit(u, u.get_rect(midleft=(sx+12, r.centery)))

        if self.msg:
            ms = self.font_body.render(self.msg, True, self.settings.COLOR_ERROR)
            self.screen.blit(ms, ms.get_rect(center=(W//2, sy+len(ALL_URLS)*(btn_h+gap)+20)))
        if self._solved: self.draw_solved_overlay()


# ─── Niveau 8 — Morse audio ──────────────────────────────────────────────────────
MORSE_CODE = {
    'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---',
    'K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-',
    'U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..',
    '0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.'
}
SECRET_MSG = "HACK"
MORSE_SECRET = " ".join(MORSE_CODE[c] for c in SECRET_MSG)


class Level08(BaseLevel):
    POINTS_BASE = 100
    def __init__(self, screen, settings):
        super().__init__(screen, settings, 8,
            "📡 Code Morse",
            "Déchiffrez ce message en code Morse et entrez le mot original.",
            hint_text="Chaque lettre est séparée par un espace.\n'.' = point court  '-' = tiret long\n"
                      "A=.-  H=....  C=-.-.  K=-.-")
        self.input_text = ""; self.shake = 0.0; self.t = 0.0

    def handle_event(self, event):
        if self._solved: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                if self.input_text.upper().strip() == SECRET_MSG: self._solved = True
                else: self.shake = 0.4; self.input_text = ""
            elif event.unicode.isprintable() and len(self.input_text)<10:
                self.input_text += event.unicode.upper()

    def update(self, dt):
        self.time_spent += dt; self.t = self.time_spent
        self.shake = max(0.0, self.shake - dt*4)

    def draw(self):
        W, H = self.screen.get_size()
        self.draw_background(); self.draw_level_header()

        # Table Morse simplifiée
        self.draw_panel(W//2-340, 150, 680, 90, self.settings.COLOR_ACCENT)
        lbl = self.font_small.render("TABLE MORSE (extrait) :", True, self.settings.COLOR_ACCENT)
        self.screen.blit(lbl, (W//2-325, 158))
        fnt_mono = pygame.font.SysFont("Consolas", 14)
        ref_lines = ["A=.-   B=-...  C=-.-.  D=-..   E=.    F=..-.", "G=--.  H=....  I=..    J=.---  K=-.-  L=.-.."]
        for i, line in enumerate(ref_lines):
            s = fnt_mono.render(line, True, self.settings.COLOR_TEXT_DIM)
            self.screen.blit(s, (W//2-325, 178+i*22))

        # Message Morse
        self.draw_panel(W//2-300, 258, 600, 65, self.settings.COLOR_WARNING)
        ml = self.font_small.render("MESSAGE MORSE À DÉCODER :", True, self.settings.COLOR_WARNING)
        self.screen.blit(ml, (W//2-285, 266))
        fnt_big = pygame.font.SysFont("Consolas", 30, bold=True)
        ms = fnt_big.render(MORSE_SECRET, True, self.settings.COLOR_TEXT)
        self.screen.blit(ms, ms.get_rect(center=(W//2, 302)))

        # "Audio" visuel (barre animée)
        self._draw_morse_anim(W, 345)

        # Input
        sx = int(6*math.sin(self.t*30)) if self.shake>0.1 else 0
        inp_y=395; inp_w,inp_h=340,52
        inp_r=pygame.Rect((W-inp_w)//2+sx, inp_y, inp_w, inp_h)
        bg=pygame.Surface((inp_w,inp_h),pygame.SRCALPHA); bg.fill((5,20,5,200))
        self.screen.blit(bg,inp_r.topleft)
        bc=self.settings.COLOR_ERROR if self.shake>0.1 else self.settings.COLOR_PRIMARY
        pygame.draw.rect(self.screen,bc,inp_r,2,border_radius=6)
        cur="▌" if int(self.t*2)%2==0 else ""
        ts=fnt_big.render(self.input_text+cur,True,self.settings.COLOR_TEXT)
        self.screen.blit(ts,ts.get_rect(center=inp_r.center))
        h2=self.font_small.render("Tapez le mot déchiffré + ENTRÉE",True,self.settings.COLOR_TEXT_DIM)
        self.screen.blit(h2,h2.get_rect(center=(W//2,inp_y+inp_h+14)))
        if self._solved: self.draw_solved_overlay()

    def _draw_morse_anim(self, W, y):
        """Visualisation graphique du morse (barres courtes/longues)."""
        symbols = MORSE_SECRET.replace(" ", "")
        x = W//2 - len(symbols)*12
        for s in symbols:
            w = 30 if s=="-" else 10
            col = self.settings.COLOR_PRIMARY
            alpha = int(150+80*math.sin(self.t*3))
            bar=pygame.Surface((w,14),pygame.SRCALPHA); bar.fill((*col,alpha))
            self.screen.blit(bar,(x,y))
            pygame.draw.rect(self.screen,col,(x,y,w,14),1,border_radius=3)
            x += w + 8


# ─── Niveau 9 — Fichier caché ────────────────────────────────────────────────────
FAKE_FS = {
    "/": ["home", "etc", "var", "tmp"],
    "/home": ["user", ".hidden_agent"],
    "/home/user": ["documents", "images", "readme.txt"],
    "/home/.hidden_agent": ["secret.txt"],
    "/home/user/documents": ["rapport.pdf", "notes.txt"],
    "/etc": ["passwd", "hosts", "nginx.conf"],
    "/var": ["log", "www"],
    "/tmp": ["temp_file.tmp"],
}
TARGET_PATH = "/home/.hidden_agent/secret.txt"
TARGET_CONTENT = "CODE_FINAL: FIREWALL_7"


class Level09(BaseLevel):
    POINTS_BASE = 120
    def __init__(self, screen, settings):
        super().__init__(screen, settings, 9,
            "📁 Fichier Caché",
            "Explorez le système de fichiers et trouvez le fichier secret.",
            hint_text="Les dossiers commençant par '.' sont cachés sous Linux.\n"
                      "Regardez dans /home : il y a un dossier qui commence par un point !")
        self.current_path="/"
        self.content_view=None
        self.history=["/"]
        self.msg=""
        self.t=0.0

    def handle_event(self, event):
        if self._solved: return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            pos=event.pos
            for item, r in self._item_rects.items():
                if r.collidepoint(pos):
                    full=self.current_path.rstrip("/")+"/"+item
                    if not full.startswith("/"): full="/"+item
                    if item in FAKE_FS.get(self.current_path,[]):
                        sub=self.current_path.rstrip("/")+"/"+item
                        if sub in FAKE_FS:
                            self.history.append(self.current_path)
                            self.current_path=sub
                        else:
                            self.content_view=sub
                            if sub==TARGET_PATH:
                                self._solved=True
        if event.type == pygame.KEYDOWN and event.key==pygame.K_BACKSPACE:
            if len(self.history)>1:
                self.current_path=self.history.pop()
                self.content_view=None

    def update(self, dt): self.time_spent+=dt; self.t=self.time_spent; self._item_rects={}

    def draw(self):
        W,H=self.screen.get_size()
        self._item_rects={}
        self.draw_background(); self.draw_level_header()
        d=self.font_small.render(self.description,True,self.settings.COLOR_TEXT_DIM)
        self.screen.blit(d,d.get_rect(center=(W//2,130)))

        # Panel FS
        pw,ph=700,380; px,py=(W-pw)//2,148
        self.draw_panel(px,py,pw,ph)

        # Chemin actuel
        fnt_mono=pygame.font.SysFont("Consolas",16)
        path_s=fnt_mono.render(f"📂 {self.current_path}", True, self.settings.COLOR_ACCENT)
        self.screen.blit(path_s,(px+10,py+8))
        pygame.draw.line(self.screen,self.settings.COLOR_BORDER,(px,py+28),(px+pw,py+28),1)

        # Contenu FS
        items=FAKE_FS.get(self.current_path,[])
        for i,item in enumerate(items):
            is_dir=(self.current_path.rstrip("/")+"/"+item) in FAKE_FS
            is_hidden=item.startswith(".")
            color=self.settings.COLOR_WARNING if is_hidden else \
                  self.settings.COLOR_PRIMARY if is_dir else self.settings.COLOR_TEXT
            icon="📁" if is_dir else "📄"
            ir=pygame.Rect(px+20, py+36+i*34, pw-40, 30)
            self._item_rects[item]=ir
            hover=ir.collidepoint(pygame.mouse.get_pos())
            if hover:
                hbg=pygame.Surface((pw-40,30),pygame.SRCALPHA); hbg.fill((0,80,0,100))
                self.screen.blit(hbg,ir.topleft)
            s=fnt_mono.render(f"{icon} {item}", True, color)
            self.screen.blit(s,(px+24,py+40+i*34))

        # Contenu fichier ouvert
        if self.content_view:
            content=TARGET_CONTENT if self.content_view==TARGET_PATH else "[Fichier vide]"
            col=self.settings.COLOR_SUCCESS if self.content_view==TARGET_PATH else self.settings.COLOR_TEXT_DIM
            cs=fnt_mono.render(f">> {content}",True,col)
            self.screen.blit(cs,cs.get_rect(center=(W//2,py+ph-24)))

        bk=self.font_small.render("⬅ BACKSPACE pour remonter",True,self.settings.COLOR_TEXT_DIM)
        self.screen.blit(bk,bk.get_rect(center=(W//2,py+ph+14)))
        if self._solved: self.draw_solved_overlay()


# ─── Niveau 10 — Boss : combinaison ──────────────────────────────────────────────
CLUES = ["FIREWALL_7", "CYPHER", "H4CKR"]
FINAL_CODE = "FW7-CPH-H4K"


class Level10(BaseLevel):
    POINTS_BASE = 200
    def __init__(self, screen, settings):
        super().__init__(screen, settings, 10,
            "⚡ Le Code Final — BOSS",
            "Combine les 3 indices récupérés pour former le code de déverrouillage.",
            hint_text="Prends les 3 premiers caractères significatifs de chaque indice\n"
                      "et assemble-les avec des tirets.\n"
                      "Indices : FIREWALL_7 / CYPHER / H4CKR")
        self.input_text=""; self.shake=0.0; self.t=0.0; self.attempts=0

    def handle_event(self, event):
        if self._solved: return
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_BACKSPACE: self.input_text=self.input_text[:-1]
            elif event.key==pygame.K_RETURN:
                self.attempts+=1
                if self.input_text.upper().strip()==FINAL_CODE: self._solved=True
                else: self.shake=0.4
            elif event.unicode.isprintable() and len(self.input_text)<20:
                self.input_text+=event.unicode.upper()

    def update(self, dt):
        self.time_spent+=dt; self.t=self.time_spent
        self.shake=max(0.0,self.shake-dt*4)

    def draw(self):
        W,H=self.screen.get_size()
        self.draw_background(); self.draw_level_header(self.settings.COLOR_WARNING)
        d=self.font_body.render(self.description,True,self.settings.COLOR_TEXT_DIM)
        self.screen.blit(d,d.get_rect(center=(W//2,130)))

        # Display clues
        for i,(clue,icon) in enumerate(zip(CLUES,["🔥","🖼️","🔑"])):
            cx=W//4*(i+1)
            clue_p=self.draw_panel(cx-130,165,260,80,self.settings.COLOR_WARNING)
            ic_s=pygame.font.SysFont("Segoe UI Emoji",28).render(icon,True,self.settings.COLOR_WARNING)
            self.screen.blit(ic_s,(cx-13,172))
            fnt_c=pygame.font.SysFont("Consolas",18,bold=True)
            cs=fnt_c.render(clue,True,self.settings.COLOR_TEXT)
            self.screen.blit(cs,cs.get_rect(center=(cx,220)))

        arrow=self.font_title.render("= ???", True, self.settings.COLOR_ACCENT)
        self.screen.blit(arrow,arrow.get_rect(center=(W//2,272)))

        # Input
        sx=int(6*math.sin(self.t*30)) if self.shake>0.1 else 0
        inp_y=310; inp_w,inp_h=400,58
        inp_r=pygame.Rect((W-inp_w)//2+sx,inp_y,inp_w,inp_h)
        bg=pygame.Surface((inp_w,inp_h),pygame.SRCALPHA); bg.fill((5,25,0,220))
        self.screen.blit(bg,inp_r.topleft)
        bc=self.settings.COLOR_ERROR if self.shake>0.1 else self.settings.COLOR_WARNING
        pygame.draw.rect(self.screen,bc,inp_r,2,border_radius=8)
        fnt_big=pygame.font.SysFont("Consolas",28,bold=True)
        cur="▌" if int(self.t*2)%2==0 else ""
        ts=fnt_big.render(self.input_text+cur,True,self.settings.COLOR_TEXT)
        self.screen.blit(ts,ts.get_rect(center=inp_r.center))
        lbl=self.font_small.render("CODE DE DÉVERROUILLAGE → ENTRÉE",True,self.settings.COLOR_TEXT_DIM)
        self.screen.blit(lbl,lbl.get_rect(center=(W//2,inp_y+inp_h+16)))

        if self.attempts>2:
            hint=self.font_small.render("Format : XXX-XXX-XXX avec tirets",True,self.settings.COLOR_ACCENT)
            self.screen.blit(hint,hint.get_rect(center=(W//2,inp_y+inp_h+38)))
        if self._solved: self.draw_solved_overlay()
