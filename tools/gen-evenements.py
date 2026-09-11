#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les 8 visuels de la section A3 « Un DJ pour chaque événement ».

    python tools/gen-evenements.py              # ne régénère que les manquants
    python tools/gen-evenements.py --force      # tout régénérer
    python tools/gen-evenements.py mariage club # seulement ces clés
    python tools/gen-evenements.py --seed 7     # décale toutes les graines

Sortie : assets/photos/evt-<clé>.jpg — le service rend ~886x665, largement
suffisant pour les cartes .crate (264 px de large, même en écran 2x).

Service : image.pollinations.ai (gratuit, sans clé). Il RENVOIE 403 sans
User-Agent de navigateur — d'où l'en-tête ci-dessous, découvert à la dure.
La graine rend chaque image reproductible : même graine = même image.
"""

import argparse
import os
import sys
import time
import urllib.parse
import urllib.request

# la console Windows est en cp1252 : sans ça, un simple "→" fait planter le script
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RACINE, "assets", "photos")

LARGEUR, HAUTEUR = 1200, 900
MODELE = "flux"

# Socle commun : c'est lui qui fait la cohérence de la série.
# Palette calée sur les tokens du site (encre #0A0A0B, accent chaud).
STYLE = (
    "cinematic editorial photography, Cameroon, West African setting, "
    "real people celebrating, natural warm skin tones, "
    "deep near-black background, warm amber and coral practical lights, "
    "wide establishing shot, faces in profile or turned away, "
    "shallow depth of field, 35mm lens, slight film grain, "
    "no text, no logo, no watermark, no close-up faces, "
    "no distorted hands, no extra limbs, no children in foreground"
)

# Variante « foule » : les négatifs anti-visage du socle produisent des salles
# vides dès qu'on demande du monde. Ici on les lève et on cadre de dos.
STYLE_FOULE = (
    "cinematic editorial photography, Cameroon, West African setting, "
    "dense crowd filling the frame, shot from behind the crowd, "
    "natural warm skin tones, warm amber and coral practical lights, "
    "shallow depth of field, 35mm lens, slight film grain, "
    "no text, no logo, no watermark, no distorted hands, no extra limbs"
)

# clé -> (titre, description, graine[, style])  — style par défaut : STYLE
EVENEMENTS = {
    "mariage": (
        "Mariage",
        "elegant wedding reception at night, couple dancing in the middle of a circle "
        "of guests clapping, string lights overhead, DJ booth glowing in the background",
        1101,
    ),
    "tradi": (
        "Traditionnel & dot",
        "traditional Cameroonian dowry ceremony, families in colourful wax print "
        "and kaba ngondo, elders seated under a decorated canopy, dancers mid-step, "
        "daylight turning golden",
        1102,
    ),
    "entreprise": (
        "Entreprise",
        "crowded corporate gala dinner seen from behind the guests, every round table "
        "full of people, colleagues standing and applauding toward a brightly lit stage, "
        "hotel ballroom packed",
        4403,
        STYLE_FOULE,
    ),
    "anniversaire": (
        "Anniversaire",
        "birthday party at night, balloons and sparkler candles on a cake, "
        "friends laughing around the table, confetti in the air",
        1104,
    ),
    "bapteme": (
        "Baptême",
        "christening reception in a decorated courtyard, long table set with white "
        "and gold decor, adult guests standing and talking, flowers and candles, "
        "soft late-afternoon light",
        2205,
    ),
    "diplome": (
        "Remise de diplôme",
        "graduation ceremony seen from behind, a crowd of graduates in gowns "
        "throwing mortarboard caps into the evening sky, campus buildings, wide angle",
        2206,
    ),
    "prive": (
        "Retour au pays",
        "crowded rooftop house party at night seen from behind the dancers, "
        "a dozen adults dancing shoulder to shoulder, string lights overhead, "
        "city skyline behind, packed terrace",
        4407,
        STYLE_FOULE,
    ),
    "club": (
        "Concert & club",
        "packed nightclub, DJ silhouetted behind the decks with hands raised, "
        "crowd with phones in the air, haze and beams of coloured light, "
        "line array speakers visible",
        1108,
    ),
}

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def url_de(desc, graine, style=None):
    prompt = urllib.parse.quote(f"{desc}, {style or STYLE}", safe="")
    params = urllib.parse.urlencode(
        {
            "width": LARGEUR,
            "height": HAUTEUR,
            "seed": graine,
            "model": MODELE,
            "nologo": "true",
            "enhance": "true",
        }
    )
    return f"https://image.pollinations.ai/prompt/{prompt}?{params}"


def telecharger(url, chemin, essais=3):
    for n in range(1, essais + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            if len(data) < 20_000:
                raise ValueError(f"réponse trop courte ({len(data)} o)")
            with open(chemin, "wb") as f:
                f.write(data)
            return len(data)
        except Exception as e:
            if n == essais:
                raise
            attente = 6 * n
            print(f"      échec ({e}) — nouvelle tentative dans {attente}s")
            time.sleep(attente)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cles", nargs="*", help="clés à générer (défaut : toutes)")
    ap.add_argument("--force", action="store_true", help="écraser les fichiers existants")
    ap.add_argument("--seed", type=int, default=0, help="décalage de graine, pour varier")
    args = ap.parse_args()

    cles = args.cles or list(EVENEMENTS)
    inconnues = [c for c in cles if c not in EVENEMENTS]
    if inconnues:
        sys.exit(f"Clé inconnue : {', '.join(inconnues)}\nDisponibles : {', '.join(EVENEMENTS)}")

    os.makedirs(DEST, exist_ok=True)
    faits = ignores = 0

    for i, cle in enumerate(cles, 1):
        titre, desc, graine, *reste = EVENEMENTS[cle]
        style = reste[0] if reste else None
        chemin = os.path.join(DEST, f"evt-{cle}.jpg")

        if os.path.exists(chemin) and not args.force:
            print(f"[{i}/{len(cles)}] {titre} — déjà là, ignoré")
            ignores += 1
            continue

        print(f"[{i}/{len(cles)}] {titre} — génération…")
        taille = telecharger(url_de(desc, graine + args.seed, style), chemin)
        print(f"      evt-{cle}.jpg  {taille // 1024} Ko")
        faits += 1
        time.sleep(2)  # on ne martèle pas un service gratuit

    print(f"\n{faits} générée(s), {ignores} ignorée(s) → assets/photos/")
    if faits:
        print("Vérifier le rendu : python -m http.server 8899 --bind 127.0.0.1")


if __name__ == "__main__":
    main()
