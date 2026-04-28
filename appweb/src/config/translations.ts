export type Lang = "fr" | "en";

export interface Translation {
  nav_download: string;
  tag: string;
  title_sub: string;
  desc: string;
  lv1_tag: string;
  lv1_name: string;
  lv1_title: string;
  lv1_desc: string;
  lv2_tag: string;
  lv2_name: string;
  lv2_title: string;
  lv2_desc: string;
  stat1_label: string;
  stat2_label: string;
  stat3_label: string;
  dl_main: string;
  dl_sub: string;
  footer: string;
  terminal_lines: { type: "cmd" | "out" | "warn" | "success"; text: string }[];
}

export const translations: Record<Lang, Translation> = {
  fr: {
    nav_download: "Télécharger",
    tag: "SIMULATION · STRATÉGIE · INFILTRATION",
    title_sub: "JEU DE SIMULATION DE HACKING",
    desc: "Plongez dans la peau d'un hacker d'élite. Infiltrez des réseaux, déchiffrez des systèmes et déjouez des pare-feu dans une simulation ultra-réaliste. Deux modes pour tous les profils.",
    lv1_tag: "NIVEAU 01",
    lv1_name: "Débutant",
    lv1_title: "Apprenti Hacker",
    lv1_desc: "Missions guidées, tutoriels intégrés et outils simplifiés pour apprendre les bases de l'infiltration.",
    lv2_tag: "NIVEAU 02",
    lv2_name: "Expert",
    lv2_title: "Black Hat Mode",
    lv2_desc: "Sandbox libre, contre-mesures avancées et exploits zero-day pour les hackers confirmés.",
    stat1_label: "MISSIONS",
    stat2_label: "NIVEAUX",
    stat3_label: "SIMULATION",
    dl_main: "TÉLÉCHARGER H4CHR.EXE",
    dl_sub: "Windows 64-bit · Gratuit · v2.1.0",
    footer: "© 2025 H4CHR — Usage éducatif uniquement. Simulation fictive.",
    terminal_lines: [
      { type: "cmd",     text: "h4chr --init" },
      { type: "out",     text: "[ OK ] Chargement des modules..." },
      { type: "cmd",     text: "scan --target 192.168.1.1" },
      { type: "out",     text: "[ OK ] 3 ports ouverts trouvés" },
      { type: "cmd",     text: "exploit --port 22 --method ssh" },
      { type: "warn",    text: "[ !! ] Pare-feu détecté" },
      { type: "cmd",     text: "bypass --mode stealth" },
      { type: "success", text: "[ ** ] Accès autorisé !" },
    ],
  },
  en: {
    nav_download: "Download",
    tag: "SIMULATION · STRATEGY · INFILTRATION",
    title_sub: "HACKING SIMULATION GAME",
    desc: "Step into the shoes of an elite hacker. Infiltrate networks, crack systems and bypass firewalls in an ultra-realistic simulation. Two modes for every profile.",
    lv1_tag: "LEVEL 01",
    lv1_name: "Beginner",
    lv1_title: "Rookie Hacker",
    lv1_desc: "Guided missions, built-in tutorials and simplified tools to learn the basics of infiltration.",
    lv2_tag: "LEVEL 02",
    lv2_name: "Expert",
    lv2_title: "Black Hat Mode",
    lv2_desc: "Open sandbox, advanced countermeasures and zero-day exploits for confirmed hackers.",
    stat1_label: "MISSIONS",
    stat2_label: "LEVELS",
    stat3_label: "SIMULATION",
    dl_main: "DOWNLOAD H4CHR.EXE",
    dl_sub: "Windows 64-bit · Free · v2.1.0",
    footer: "© 2025 H4CHR — Educational use only. Fictional simulation.",
    terminal_lines: [
      { type: "cmd",     text: "h4chr --init" },
      { type: "out",     text: "[ OK ] Loading modules..." },
      { type: "cmd",     text: "scan --target 192.168.1.1" },
      { type: "out",     text: "[ OK ] 3 open ports found" },
      { type: "cmd",     text: "exploit --port 22 --method ssh" },
      { type: "warn",    text: "[ !! ] Firewall detected" },
      { type: "cmd",     text: "bypass --mode stealth" },
      { type: "success", text: "[ ** ] Access granted !" },
    ],
  },
};