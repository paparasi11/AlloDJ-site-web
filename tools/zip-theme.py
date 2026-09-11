#!/usr/bin/env python3
"""Archive installable d'un thème AlloDJ.

    python tools/zip-theme.py allodj-theme-v2
    python tools/zip-theme.py allodj-theme          # la v1, inchangée

Le nom du dossier dans l'archive devient l'identifiant du thème côté
WordPress : deux dossiers différents = deux thèmes installables côte à côte,
qu'on active à tour de rôle sans rien perdre.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = pathlib.Path(r"C:\Users\Malcom\Documents\claude")
EXCLUS_DOSSIERS = {".git", "__pycache__", "node_modules", "captures"}

REQUIS = (
    "style.css",
    "index.php",
    "functions.php",
    "front-page.php",
    "page-legal.php",
    "inc/seo.php",
    "inc/faq.php",
    "inc/i18n.php",
    "inc/llms.txt",
    "assets/js/site.js",
    "assets/js/consent.js",
    "assets/img/favicon.svg",
    "languages/en_US.mo",
    "template-parts/b5-faq.php",
    "template-parts/b7-sortie.php",
    "screenshot.png",
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("theme", help="nom du dossier du thème, sous " + str(BASE))
    args = ap.parse_args()

    src = args.theme.rstrip("/\\")
    dossier = BASE / src
    if not dossier.is_dir():
        sys.exit(f"{dossier} introuvable.")

    archive = BASE / f"{src}.zip"
    os.chdir(BASE)
    if archive.exists():
        archive.unlink()

    n = 0
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for racine, dossiers, fichiers in os.walk(src):
            dossiers[:] = [d for d in dossiers if d not in EXCLUS_DOSSIERS]
            for f in sorted(fichiers):
                if f.endswith((".pyc", ".DS_Store")) or f.startswith("."):
                    continue
                chemin = os.path.join(racine, f)
                z.write(chemin, chemin.replace(os.sep, "/"))
                n += 1

    print(f"{archive.name} — {n} fichiers · {archive.stat().st_size // 1024} Ko")

    with zipfile.ZipFile(archive) as z:
        mauvais = z.testzip()
        print("archive :", ("corrompue à " + mauvais) if mauvais else "intègre")
        noms = set(z.namelist())

    manquants = 0
    for requis in REQUIS:
        present = f"{src}/{requis}" in noms
        manquants += not present
        print(f"  {'ok      ' if present else 'MANQUANT'} {requis}")

    if manquants:
        sys.exit(f"\n{manquants} fichier(s) manquant(s) — NE PAS LIVRER.")


if __name__ == "__main__":
    main()
