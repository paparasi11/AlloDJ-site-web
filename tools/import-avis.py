#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Récupère les avis réels de Firestore et prépare les candidats verbatims.

    python tools/import-avis.py              # écrit data/avis-candidats.json
    python tools/import-avis.py --tout       # sans filtre, pour inspection

La collection `reviews` du projet Firebase est en lecture publique
(`allow read: if true` dans firestore.rules), donc aucune clé privée n'est
nécessaire : la clé cliente est lue dans firebase_options.dart et n'est jamais
affichée.

Ce script n'écrit JAMAIS dans data/verbatims.json. Il produit une liste de
candidats avec `consentement: false`. Un avis laissé dans l'application n'est
pas un accord pour figurer sur la page d'accueil, avec un nom, en argument
commercial : il faut le demander. Une fois le oui obtenu, recopier l'entrée
dans verbatims.json en passant `consentement` à true et en renseignant
`source`, puis lancer build-verbatims.py.

Critères de sélection par défaut :
  · non masqué par la modération (`hidden`)
  · note >= 4
  · commentaire d'au moins 40 caractères — en dessous, ça ne dit rien
  · auteur hors liste de comptes de test
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "data", "avis-candidats.json")
OPTIONS = r"C:\Users\Malcom\Claude\Projects\allo dj app\app\lib\firebase_options.dart"
PROJET = "psychic-heading-276413"

# Comptes ayant servi aux tests — leurs avis ne sont pas des avis clients.
COMPTES_TEST = {"paparazzi", "muketee2005", "malcom", "test", "client"}
DJS_TEST = {"djmalcom", "dj", "test"}

MIN_CARACTERES = 40
MIN_NOTE = 4


def cle_cliente():
    if not os.path.exists(OPTIONS):
        sys.exit(f"firebase_options.dart introuvable : {OPTIONS}")
    src = open(OPTIONS, encoding="utf-8").read()
    m = re.search(r"apiKey:\s*'([^']+)'", src)
    if not m:
        sys.exit("apiKey introuvable dans firebase_options.dart")
    return m.group(1)


def valeur(champs, nom, defaut=""):
    v = champs.get(nom, {})
    for k in ("stringValue", "integerValue", "booleanValue", "timestampValue"):
        if k in v:
            return v[k]
    return defaut


def lire_avis():
    url = (
        f"https://firestore.googleapis.com/v1/projects/{PROJET}/databases/(default)"
        f"/documents/reviews?pageSize=300&key={cle_cliente()}"
    )
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} — {e.read().decode('utf-8', 'replace')[:300]}")

    avis = []
    for doc in d.get("documents", []):
        f = doc.get("fields", {})
        avis.append({
            "id": doc["name"].rsplit("/", 1)[-1],
            "note": int(valeur(f, "rating", 0) or 0),
            "client": valeur(f, "clientName", "Client"),
            "dj": valeur(f, "djName"),
            "commentaire": valeur(f, "comment").strip(),
            "attentes": valeur(f, "expectations").strip(),
            "recommande": valeur(f, "recommend", ""),
            "masque": str(valeur(f, "hidden", "false")).lower() == "true",
            "date": valeur(f, "createdAt", "")[:10],
        })
    return avis


def refus(a):
    r = []
    if a["masque"]:
        r.append("masqué par la modération")
    if a["note"] < MIN_NOTE:
        r.append(f'note {a["note"]}/5')
    if len(a["commentaire"]) < MIN_CARACTERES:
        r.append(f'commentaire trop court ({len(a["commentaire"])} car.)')
    if a["client"].lower() in COMPTES_TEST:
        r.append(f'compte de test « {a["client"]} »')
    if a["dj"].lower() in DJS_TEST:
        r.append(f'DJ de test « {a["dj"]} »')
    return r


def anonymiser(nom):
    """« Sandrine Mballa » → « Sandrine M. » — usage courant pour un avis."""
    bouts = nom.strip().split()
    if len(bouts) >= 2:
        return f"{bouts[0]} {bouts[1][0].upper()}."
    return bouts[0] if bouts else "Client"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tout", action="store_true", help="ignorer les filtres")
    args = ap.parse_args()

    avis = lire_avis()
    print(f"{len(avis)} avis dans la collection `reviews`\n")

    gardes, ecartes = [], []
    for a in avis:
        raisons = [] if args.tout else refus(a)
        (ecartes if raisons else gardes).append((a, raisons))

    if ecartes:
        print("Écartés :")
        for a, raisons in ecartes:
            print(f'  {a["client"]:<18} → {a["dj"]:<14} {", ".join(raisons)}')
        print()

    if not gardes:
        print("Aucun avis exploitable comme verbatim aujourd'hui.")
        print("Les avis existants viennent des comptes de test.")
        print("→ docs/collecte-verbatims.md pour en obtenir de vrais.")
        return

    candidats = [{
        "citation": a["commentaire"],
        "auteur": anonymiser(a["client"]),
        "role": "Client",
        "ville": "",                      # absent de l'avis, à renseigner
        "evenement": "",                  # idem
        "date": a["date"],
        "consentement": False,            # à passer à true APRÈS accord explicite
        "source": f'Avis in-app {a["id"]} du {a["date"]}',
        "_dj": a["dj"],
        "_note": a["note"],
    } for a, _ in gardes]

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(
        {
            "_lisez_moi": [
                "CANDIDATS, pas des verbatims publiables.",
                "Un avis laissé dans l'app n'est pas un accord pour figurer sur la",
                "page d'accueil avec un nom, en argument commercial. Demandez-le.",
                "",
                "Une fois le oui obtenu : recopier l'entrée dans data/verbatims.json,",
                "passer consentement à true, compléter ville et evenement, retirer",
                "les champs commençant par _, puis lancer build-verbatims.py.",
            ],
            "candidats": candidats,
        },
        open(SORTIE, "w", encoding="utf-8"),
        ensure_ascii=False, indent=2,
    )
    print(f"{len(candidats)} candidat(s) → data/avis-candidats.json")
    for c in candidats:
        print(f'  {c["auteur"]:<16} {c["_note"]}/5  « {c["citation"][:70]} »')
    print("\nAucun n'est publié tant que consentement n'est pas passé à true.")


if __name__ == "__main__":
    main()
