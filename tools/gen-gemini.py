#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les visuels de la section A3 avec Gemini (remplace pollinations.ai).

    python tools/gen-gemini.py                 # les 8 manquants
    python tools/gen-gemini.py --force         # tout régénérer
    python tools/gen-gemini.py mariage club    # seulement ces clés
    python tools/gen-gemini.py --modele gemini-2.5-flash-image   # moins cher

Clé lue dans la variable d'environnement GEMINI_API_KEY. Jamais en dur ici.

Pourquoi Gemini plutôt que pollinations : les trois passes de gen-evenements.py
ont montré que le service gratuit rate les visages et vide les salles dès qu'on
demande une foule. Gemini tient les deux.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RACINE, "assets", "photos")
MODELE = "gemini-3-pro-image"

# Socle commun : c'est lui qui tient la cohérence de la série.
# Calé sur les tokens du site — fond très sombre, lumières ambre et corail.
STYLE = (
    "Photorealistic editorial photograph, Cameroon, Central Africa. "
    "Everyone in frame is Black Cameroonian — deep brown to dark skin tones "
    "rendered richly and accurately, no lightening. "
    "The guests dress in a realistic MIX, not a costume parade: some in tailored "
    "suits and blazers, some in cocktail and evening dresses, some in jeans and "
    "sneakers, some in ankara / wax-print outfits, some in boubou or agbada, a "
    "few in traditional cloth — a modern cosmopolitan African crowd. "
    "Natural, braided and locs hair, durags, gold jewellery. "
    "Deep near-black background, warm amber and coral practical lighting, "
    "shallow depth of field, 35mm lens, subtle film grain, cinematic colour grade. "
    "Candid documentary feel, not a stock photo, not a Western party. "
    "No text, no logos, no watermarks anywhere in the frame. "
    "Anatomically correct hands and faces."
)

# État au 2026-09-09 : entreprise, anniversaire, bapteme, diplome, prive, club
# sont posées (images Gemini fournies par Malcom, Downloads.rar). Restent
# « mariage » et « tradi » à générer — les prompts ci-dessous sont à jour.
EVENEMENTS = {
    "mariage": (
        "Mariage",
        "An evening Cameroonian wedding reception. The bride in a white gown, the "
        "groom in a sharp suit, dancing inside a circle of guests dressed every way — "
        "cocktail dresses, tailored suits, ankara ensembles, a few in traditional "
        "cloth — who clap and ululate. String lights overhead, a DJ booth glowing in "
        "the background, a spray of banknotes mid-air in the njangi money-dance.",
    ),
    "tradi": (
        "Traditionnel & dot",
        "A Cameroonian dowry ceremony (la dot) in late-afternoon golden light. The "
        "families lean traditional — ndop and toghu cloth, kaba ngondo, boubou — but "
        "younger relatives mix in modern dresses and blazers. Elders seated under a "
        "decorated canopy, women dancing bikutsi mid-step, calabashes and kola nuts "
        "on a mat.",
    ),
    "entreprise": (
        "Entreprise",
        "A crowded end-of-year company gala in a Douala hotel ballroom. Cameroonian "
        "colleagues in suits, blazers, evening dresses and a few ankara-accent "
        "outfits, standing and applauding toward a brightly lit stage. Round tables "
        "full, a DJ setup with laptop and controller discreetly at the side.",
    ),
    "anniversaire": (
        "Anniversaire",
        "A night birthday party on a Yaoundé terrace. A cake with sparkler candles on "
        "the table, young Cameroonian friends in a mix of streetwear, print dresses "
        "and smart-casual, leaning in and laughing, balloons and confetti in the air, "
        "bottles of Fanta and beer between them.",
    ),
    "bapteme": (
        "Baptême",
        "A Cameroonian christening reception in a decorated compound courtyard. A long "
        "table with white and gold decor; guests in a range of dress — Sunday-best "
        "dresses and suits, some aunties in bright kaba, men in shirts or boubou — "
        "standing and talking. Plates of jollof and grilled fish, plastic chairs, "
        "soft late-afternoon light, a modest sound system in the corner.",
    ),
    "diplome": (
        "Remise de diplôme",
        "A graduation celebration on a Cameroonian university campus, seen from behind "
        "the crowd. Black graduates in gowns and mortarboards throwing their caps into "
        "the evening sky; families cheering in a mix of Sunday dresses, suits and wax "
        "print, low campus buildings and palm trees behind.",
    ),
    "prive": (
        "Retour au pays",
        "A crowded rooftop house party at night in Douala — the diaspora home for the "
        "holidays. A dozen Cameroonian adults dancing coupé-décalé shoulder to "
        "shoulder in jeans, dresses, jackets and a few print outfits, under string "
        "lights. A table of grilled soya, plantain and drinks to one side, "
        "corrugated-roof neighbourhood and city lights behind.",
    ),
    "club": (
        "Concert & club",
        "A packed Douala nightclub. A Cameroonian DJ silhouetted behind the decks with "
        "one hand raised, a dense Black crowd in club wear — dresses, shirts, chains, "
        "durags — with phones in the air. Haze and coloured beams cutting through the "
        "room, a stack of line-array speakers, bottles with sparklers carried "
        "overhead.",
    ),
}


def cle():
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    if not k:
        sys.exit(
            "GEMINI_API_KEY absente.\n"
            "PowerShell : [Environment]::SetEnvironmentVariable('GEMINI_API_KEY','…','User')\n"
            "puis rouvrir le terminal."
        )
    return k


def generer(prompt, modele, essais=3):
    """Renvoie les octets de l'image, ou lève."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent"
    corps = json.dumps(
        {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {"aspectRatio": "4:3"},
            },
        }
    ).encode("utf-8")

    for n in range(1, essais + 1):
        try:
            req = urllib.request.Request(
                url,
                data=corps,
                headers={
                    "x-goog-api-key": cle(),
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=240) as r:
                rep = json.load(r)

            cands = rep.get("candidates") or []
            if not cands:
                raise ValueError("réponse sans candidat : " + json.dumps(rep)[:300])

            for part in cands[0].get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    return base64.b64decode(inline["data"])

            motif = cands[0].get("finishReason", "?")
            raise ValueError(f"aucune image renvoyée (finishReason={motif})")

        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            if e.code in (400, 401, 403, 404):
                raise SystemExit(f"HTTP {e.code} — {detail}")  # inutile de réessayer
            if n == essais:
                raise
            print(f"      HTTP {e.code}, nouvelle tentative…")
            time.sleep(8 * n)
        except Exception as e:
            if n == essais:
                raise
            print(f"      échec ({e}) — nouvelle tentative…")
            time.sleep(8 * n)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cles", nargs="*", help="clés à générer (défaut : toutes)")
    ap.add_argument("--force", action="store_true", help="écraser les fichiers existants")
    ap.add_argument("--modele", default=MODELE, help=f"modèle Gemini (défaut : {MODELE})")
    args = ap.parse_args()

    cles = args.cles or list(EVENEMENTS)
    inconnues = [c for c in cles if c not in EVENEMENTS]
    if inconnues:
        sys.exit(f"Clé inconnue : {', '.join(inconnues)}\nDisponibles : {', '.join(EVENEMENTS)}")

    os.makedirs(DEST, exist_ok=True)
    faits = ignores = 0

    for i, c in enumerate(cles, 1):
        titre, scene = EVENEMENTS[c]
        chemin = os.path.join(DEST, f"evt-{c}.jpg")

        if os.path.exists(chemin) and not args.force:
            print(f"[{i}/{len(cles)}] {titre} — déjà là, ignoré")
            ignores += 1
            continue

        print(f"[{i}/{len(cles)}] {titre} — génération…")
        data = generer(f"{scene}\n\n{STYLE}", args.modele)

        # Gemini rend du PNG : on convertit en JPEG pour le poids
        try:
            from PIL import Image
            import io

            im = Image.open(io.BytesIO(data)).convert("RGB")
            im.save(chemin, "JPEG", quality=86, optimize=True, progressive=True)
            taille, dims = os.path.getsize(chemin), im.size
        except ImportError:
            open(chemin, "wb").write(data)
            taille, dims = len(data), "?"

        print(f"      evt-{c}.jpg  {dims}  {taille // 1024} Ko")
        faits += 1
        time.sleep(1)

    print(f"\n{faits} generee(s), {ignores} ignoree(s) -> assets/photos/")


if __name__ == "__main__":
    main()
