#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Injecte les verbatims réels de data/verbatims.json dans index.html.

    python tools/build-verbatims.py

Écrit entre les marqueurs <!-- VERBATIMS:début --> et <!-- VERBATIMS:fin -->
d'index.html, puis émet le balisage schema.org Review correspondant.

Trois refus volontaires — ce script ne publiera jamais :
  · une citation vide ou un auteur vide ;
  · une entrée dont `consentement` n'est pas exactement true ;
  · une entrée dont la `source` (trace de provenance) est vide.

Pourquoi cette rigidité : un faux avis client est une pratique commerciale
trompeuse (directive Omnibus 2019/2161, contrôles DGCCRF) et une violation des
règles anti-spam de Google sur les données structurées, qui coûte le rich
snippet et peut coûter le classement. Sur un site dont l'argument est
« on ne réserve plus au bouche-à-oreille », c'est aussi une contradiction.

Liste vide = section absente de la page. C'est l'état correct tant qu'aucun
verbatim réel n'a été collecté (voir docs/collecte-verbatims.md).
"""

import html
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.path.join(RACINE, "data", "verbatims.json")
CIBLE = os.path.join(RACINE, "index.html")
DEBUT, FIN = "<!-- VERBATIMS:début -->", "<!-- VERBATIMS:fin -->"


def valider(v, i):
    """Renvoie la liste des raisons de refus."""
    fautes = []
    if not (v.get("citation") or "").strip():
        fautes.append("citation vide")
    if not (v.get("auteur") or "").strip():
        fautes.append("auteur vide")
    if v.get("consentement") is not True:
        fautes.append("consentement absent ou différent de true")
    if not (v.get("source") or "").strip():
        fautes.append("source (trace de provenance) vide")
    texte = (v.get("citation") or "").lower()
    for piege in ("lorem", "exemple", "placeholder", "à remplir", "todo"):
        if piege in texte:
            fautes.append(f"citation contenant « {piege} »")
    return fautes


def carte(v):
    e = html.escape
    meta = " · ".join(x for x in (v.get("role"), v.get("ville"), v.get("evenement")) if x)
    return (
        '        <figure class="verb">\n'
        f'          <blockquote><p>{e(v["citation"])}</p></blockquote>\n'
        f'          <figcaption><b>{e(v["auteur"])}</b><span>{e(meta)}</span></figcaption>\n'
        "        </figure>"
    )


def section(verbatims):
    cartes = "\n".join(carte(v) for v in verbatims)
    return f"""{DEBUT}
  <!-- Généré par tools/build-verbatims.py depuis data/verbatims.json. Ne pas éditer ici. -->
  <section id="b6">
    <div class="wrap">
      <div class="slate"><span class="tk">Face B · B6</span><span class="ttl">Les retours</span><span class="rt">{len(verbatims)} témoignage{'s' if len(verbatims) > 1 else ''}</span></div>
      <h2 class="big rv">Ce qu'en disent ceux qui ont réservé</h2>
      <div class="verbs rvg">
{cartes}
      </div>
    </div>
  </section>
  {FIN}"""


def json_ld(verbatims):
    """Reviews rattachées au Service — uniquement si de vrais avis existent."""
    return [
        {
            "@type": "Review",
            "reviewBody": v["citation"],
            "author": {"@type": "Person", "name": v["auteur"]},
            "datePublished": v.get("date", ""),
            "itemReviewed": {"@id": "https://allodeejay.com/#service"},
        }
        for v in verbatims
    ]


def main():
    d = json.load(open(DONNEES, encoding="utf-8"))
    bruts = d.get("verbatims", [])

    refuses = []
    valides = []
    for i, v in enumerate(bruts, 1):
        fautes = valider(v, i)
        if fautes:
            refuses.append((i, v.get("auteur") or "(sans auteur)", fautes))
        else:
            valides.append(v)

    if refuses:
        print("REFUS — ces entrées ne seront pas publiées :\n")
        for i, qui, fautes in refuses:
            print(f"  entrée {i} ({qui}) : {', '.join(fautes)}")
        print()

    s = open(CIBLE, encoding="utf-8").read()
    if DEBUT not in s or FIN not in s:
        sys.exit(
            f"Marqueurs absents d'index.html.\n"
            f"Ajouter {DEBUT} et {FIN} à l'endroit voulu."
        )

    bloc = section(valides) if valides else f"{DEBUT}\n  {FIN}"
    s = re.sub(re.escape(DEBUT) + r".*?" + re.escape(FIN), lambda _: bloc, s, flags=re.S)

    # schema.org : on injecte (ou on retire) les Review du graphe
    m = re.search(r'(<script type="application/ld\+json">\s*)(.*?)(\s*</script>)', s, re.S)
    g = json.loads(m.group(2))
    g["@graph"] = [n for n in g["@graph"] if n.get("@type") != "Review"]
    g["@graph"].extend(json_ld(valides))
    s = s[: m.start(2)] + json.dumps(g, ensure_ascii=False, indent=2) + s[m.end(2):]

    open(CIBLE, "w", encoding="utf-8").write(s)

    if valides:
        print(f"{len(valides)} verbatim(s) publié(s) + {len(valides)} Review dans le JSON-LD.")
        print("Penser à relancer build-en.py et build-villes.py.")
    else:
        print("Aucun verbatim valide : la section reste absente de la page.")
        print("C'est l'état correct tant que rien de réel n'a été collecté.")
        print("→ docs/collecte-verbatims.md")


if __name__ == "__main__":
    main()
