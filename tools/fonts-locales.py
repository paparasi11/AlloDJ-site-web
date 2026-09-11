#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rapatrie les polices Google en local et écrit assets/fonts.css.

    python tools/fonts-locales.py

Pourquoi : charger une police depuis fonts.googleapis.com transmet l'adresse IP
du visiteur à Google **avant** toute interaction et sans base légale. Le tribunal
de Munich l'a jugé illicite en janvier 2022 (LG München I, 3 O 17493/20), et
c'est depuis le motif de mise en demeure le plus courant en Europe. Héberger les
fichiers supprime le problème à la racine — aucune bannière ne le règle, puisque
la requête part avant même que la bannière s'affiche.

Sora, Hanken Grotesk et JetBrains Mono sont toutes trois sous licence SIL Open
Font License : l'auto-hébergement est explicitement autorisé.

Bénéfice secondaire : une requête DNS et une connexion TLS de moins vers un
domaine tiers, donc un rendu plus rapide — surtout sur les connexions lentes.
"""

import os
import re
import sys
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RACINE, "assets", "fonts")
CSS = os.path.join(RACINE, "assets", "fonts.css")

# Même requête que celle du <link> actuel.
URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Sora:wght@600;700;800"
    "&family=Hanken+Grotesk:wght@400;500;600"
    "&family=JetBrains+Mono:wght@400;500;700"
    "&display=swap"
)

# Un UA moderne obtient du woff2 ; un UA ancien obtient du ttf, quatre fois plus lourd.
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# On ne garde que ce dont le site a besoin : latin (accents français inclus)
# et latin-ext. Cyrillique, grec et vietnamien seraient du poids mort.
SOUS_ENSEMBLES = ("latin", "latin-ext")


def recuperer(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    os.makedirs(DEST, exist_ok=True)
    css = recuperer(URL).decode("utf-8")

    # Google commente chaque bloc par son sous-ensemble : /* latin */
    blocs = re.split(r"/\*\s*([\w-]+)\s*\*/", css)
    sortie = [
        "/* Polices auto-hébergées — voir tools/fonts-locales.py.",
        "   Sora, Hanken Grotesk, JetBrains Mono · SIL Open Font License.",
        "   Aucune requête vers Google : l'IP du visiteur ne sort pas du site. */",
        "",
    ]

    telecharges, ignores = 0, 0
    for i in range(1, len(blocs), 2):
        nom, bloc = blocs[i], blocs[i + 1]
        if nom not in SOUS_ENSEMBLES:
            ignores += bloc.count("@font-face")
            continue

        for face in re.findall(r"@font-face\s*\{[^}]+\}", bloc):
            famille = re.search(r"font-family:\s*'([^']+)'", face).group(1)
            graisse = re.search(r"font-weight:\s*(\d+)", face).group(1)
            lien = re.search(r"url\((https://[^)]+\.woff2)\)", face)
            if not lien:
                continue

            fichier = f"{famille.replace(' ', '-').lower()}-{graisse}-{nom}.woff2"
            chemin = os.path.join(DEST, fichier)
            if not os.path.exists(chemin):
                with open(chemin, "wb") as f:
                    f.write(recuperer(lien.group(1)))
            telecharges += 1

            local = face.replace(lien.group(1), f"fonts/{fichier}")
            # font-display: swap — le texte reste lisible pendant le chargement
            if "font-display" not in local:
                local = local.replace("@font-face {", "@font-face {\n  font-display: swap;")
            sortie.append(local.strip())
            sortie.append("")

    open(CSS, "w", encoding="utf-8").write("\n".join(sortie))

    poids = sum(
        os.path.getsize(os.path.join(DEST, f)) for f in os.listdir(DEST) if f.endswith(".woff2")
    )
    print(f"{telecharges} fichiers woff2 -> assets/fonts/ ({poids // 1024} Ko)")
    print(f"{ignores} variantes ignorees (sous-ensembles inutiles ici)")
    print(f"assets/fonts.css ecrit ({os.path.getsize(CSS)} o)")


if __name__ == "__main__":
    main()
