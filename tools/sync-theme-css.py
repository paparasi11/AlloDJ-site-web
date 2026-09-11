#!/usr/bin/env python3
"""Reconstruit la feuille de style d'un thème WordPress AlloDJ.

    python tools/sync-theme-css.py --theme ../allodj-theme-v2
    python tools/sync-theme-css.py --theme ../allodj-theme-v2 --extraire

`style.css` d'un thème = quatre morceaux, dans cet ordre :

  1. l'en-tête de thème (les métadonnées que lit WordPress) ;
  2. `assets/site.css` — le design, identique au site statique ;
  3. une palette de rechange, facultative (`--palette assets/palette-v1.css`) ;
  4. `tools/theme-wordpress.css` — ce que WordPress seul exige : classes du
     cœur (`alignwide`, `screen-reader-text`, pagination), la prose des pages
     éditoriales et les pages légales.

La palette est ce qui sépare la v1 de la v2 : même feuille de mise en page,
même responsive, mêmes cibles tactiles, vingt-cinq jetons de couleur qui
changent. Les deux thèmes ne peuvent donc plus diverger sur le responsive.

Avant, ces trois morceaux étaient recopiés à la main dans le thème. Le thème a
dérivé : sa version mobile masquait purement et simplement la navigation
(`.nav{display:none}`) alors que le site statique la faisait défiler. Un
script rend la copie reproductible et la dérive impossible.

`--extraire` relit la queue WordPress depuis le style.css existant et la
réécrit dans tools/theme-wordpress.css : à n'utiliser qu'une fois, pour
amorcer le fichier.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
SITE_CSS = RACINE / "assets" / "site.css"
QUEUE_WP = RACINE / "tools" / "theme-wordpress.css"

# La bannière qui ouvre la partie WordPress du style.css.
MARQUE = "/* " + "═" * 3

SEPARATEUR = """

/* ══════════════════════════════════════════════════════
   WORDPRESS — classes du cœur et gabarits internes
   ══════════════════════════════════════════════════════ */
"""


def entete(style: pathlib.Path) -> str:
    """Le commentaire de métadonnées, tel quel — c'est lui qui identifie le thème."""
    css = style.read_text(encoding="utf-8")
    if not css.startswith("/*"):
        sys.exit(f"{style} ne commence pas par un en-tête de thème.")
    return css[: css.index("*/") + 2]


def extraire_queue(style: pathlib.Path) -> str:
    css = style.read_text(encoding="utf-8")
    corps = css[css.index("*/") + 2 :]
    i = corps.find(MARQUE)
    if i < 0:
        sys.exit("Bannière WordPress introuvable dans le style.css.")
    # On repart après la bannière : le script la réécrit lui-même.
    reste = corps[i:]
    fin = reste.index("*/", reste.index("WORDPRESS")) + 2
    return reste[fin:].lstrip("\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", required=True, help="dossier du thème à mettre à jour")
    ap.add_argument("--extraire", action="store_true", help="amorcer tools/theme-wordpress.css")
    ap.add_argument("--version", help="nouvelle valeur du champ Version:")
    ap.add_argument("--nom", help="nouvelle valeur du champ Theme Name:")
    ap.add_argument("--palette", help="feuille de jetons à charger après site.css")
    args = ap.parse_args()

    theme = pathlib.Path(args.theme)
    if not theme.is_absolute():
        theme = (RACINE / theme).resolve()
    style = theme / "style.css"
    if not style.exists():
        sys.exit(f"{style} introuvable.")

    if args.extraire:
        QUEUE_WP.write_text(extraire_queue(style), encoding="utf-8", newline="\n")
        print(f"queue WordPress extraite → {QUEUE_WP} ({QUEUE_WP.stat().st_size} octets)")
        return

    if not QUEUE_WP.exists():
        sys.exit(f"{QUEUE_WP} manquant — lancez d'abord --extraire.")

    tete = entete(style)
    if args.version:
        tete, n = re.subn(r"(?m)^Version:.*$", f"Version: {args.version}", tete)
        if not n:
            sys.exit("Champ Version: introuvable dans l'en-tête.")
    if args.nom:
        tete, n = re.subn(r"(?m)^Theme Name:.*$", f"Theme Name: {args.nom}", tete)
        if not n:
            sys.exit("Champ Theme Name: introuvable dans l'en-tête.")

    design = SITE_CSS.read_text(encoding="utf-8").strip("\n")
    queue = QUEUE_WP.read_text(encoding="utf-8").strip("\n")

    palette = ""
    if args.palette:
        p = pathlib.Path(args.palette)
        if not p.is_absolute():
            p = (RACINE / p).resolve()
        if not p.exists():
            sys.exit(f"{p} introuvable.")
        palette = "\n\n" + p.read_text(encoding="utf-8").strip("\n") + "\n"

    sortie = f"{tete}\n\n{design}\n{palette}{SEPARATEUR}\n{queue}\n"
    style.write_text(sortie, encoding="utf-8", newline="\n")

    # Vérité mesurée : les jetons et les points de rupture ont bien suivi.
    # L'accent attendu n'est pas une couleur figée dans ce script — sinon ce
    # contrôle devient lui-même périmé au premier changement de palette (vécu :
    # il attendait encore le vert citron après le passage à l'indigo du logo).
    # On relit plutôt la DERNIÈRE déclaration de --peak dans la source qui doit
    # gagner la cascade (la palette si elle existe, sinon design), et on vérifie
    # que c'est bien elle qui l'emporte dans le fichier final.
    source_accent = palette if args.palette else design
    attendues = re.findall(r"--peak:\s*(#[0-9A-Fa-f]{6})", source_accent)
    accent = attendues[-1].upper() if attendues else None
    declares = re.findall(r"--peak:\s*(#[0-9A-Fa-f]{6})", sortie)
    controles = {
        "--cream": "--cream:" in sortie,
        f"accent {accent}": bool(accent) and bool(declares) and declares[-1].upper() == accent,
        "nav qui déroule sous 1000 px": ".nav{order:3" in sortie,
        "cibles 44 px": "min-height:44px;padding:0 13px" in sortie,
        "règles au doigt": "(max-width:1000px), (pointer:coarse)" in sortie,
        "queue WordPress": ".screen-reader-text" in sortie,
        "pages légales": ".legal{" in sortie,
    }
    print(f"{style} — {len(sortie) // 1024} Ko")
    for k, ok in controles.items():
        print(f"  {'ok ' if ok else 'MANQUE'}  {k}")
    if not all(controles.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
