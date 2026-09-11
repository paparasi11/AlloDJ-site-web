#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère une page par ville à partir de index.html.

    python tools/build-villes.py

Sortie : dj-douala.html, dj-yaounde.html

Pourquoi des pages séparées : une seule page ne peut pas répondre aussi bien à
« booker un DJ à Douala » et à « booker un DJ à Yaoundé ». Chaque requête a
besoin de son URL, son titre, son H1 et son balisage. L'accueil garde le terme
national (« Cameroun »), les villes prennent les termes locaux.

Ce ne sont PAS des copies : chaque page ne montre que les DJs de sa ville, a sa
propre FAQ et son propre `areaServed`. Ce qui est commun (méthode, comparatif)
reste commun — c'est légitime, c'est le même service.
"""

import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retour_accueil  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RACINE, "index.html")
BASE = "https://allodeejay.com/"
APP = "https://appli.allodeejay.com/#/home"

# Les DJs réellement rattachés à chaque ville (mêmes données que site.js).
DJS = {
    "douala": [
        ("real-dj-01", "Afrobeats"), ("real-dj-05", "Club"),
        ("real-dj-06", "Zouk"), ("real-dj-07", "Vinyle"),
        ("real-dj-02", "Corporate"),
    ],
    "yaounde": [
        ("real-dj-03", "Amapiano"), ("real-dj-04", "Rap FR"),
        ("real-dj-08", "Ambiance"),
    ],
}

VILLES = {
    "douala": {
        "nom": "Douala",
        "fichier": "dj-douala.html",
        "autre": ("Yaoundé", "dj-yaounde.html"),
        "titre": "Booking DJ Douala — Réserver un DJ à Douala | AlloDJ",
        "h1": ("Réserver", "un DJ", "à Douala."),
        "desc": (
            "Booking de DJ à Douala : mariage, soirée d'entreprise, anniversaire, club. "
            "AlloDJ désigne le DJ disponible à Douala pour votre date et votre budget. "
            "10 % d'acompte, annulation sans frais sous 48 h."
        ),
        "chapo": (
            "AlloDJ réserve des DJs à <b>Douala</b> pour les mariages, les cérémonies "
            "traditionnelles, les soirées d'entreprise, les anniversaires et les nuits "
            "de club. Indiquez la date, le quartier et votre budget&nbsp;: la plateforme "
            "désigne un DJ disponible plutôt que de diffuser votre demande à une liste."
        ),
        "roster": (
            "Les DJs rattachés à <b>Douala</b> couvrent l'afrobeats, le zouk, le vinyle, "
            "le club et les prestations corporate. Chacun est entré sur recommandation "
            "d'au moins 3 DJs déjà actifs, et chaque prestation est notée ensuite."
        ),
    },
    "yaounde": {
        "nom": "Yaoundé",
        "fichier": "dj-yaounde.html",
        "autre": ("Douala", "dj-douala.html"),
        "titre": "Booking DJ Yaoundé — Réserver un DJ à Yaoundé | AlloDJ",
        "h1": ("Réserver", "un DJ", "à Yaoundé."),
        "desc": (
            "Booking de DJ à Yaoundé : mariage, dot, soirée d'entreprise, remise de "
            "diplôme. AlloDJ désigne le DJ disponible à Yaoundé pour votre date et votre "
            "budget. 10 % d'acompte, annulation sans frais sous 48 h."
        ),
        "chapo": (
            "AlloDJ réserve des DJs à <b>Yaoundé</b> pour les mariages, les cérémonies "
            "traditionnelles et la dot, les soirées d'entreprise, les remises de diplôme "
            "et les fêtes privées. Indiquez la date, le quartier et votre budget&nbsp;: "
            "la plateforme désigne un DJ disponible plutôt que de diffuser votre demande."
        ),
        "roster": (
            "Les DJs rattachés à <b>Yaoundé</b> couvrent l'amapiano, le rap français et "
            "les sets d'ambiance. Chacun est entré sur recommandation d'au moins 3 DJs "
            "déjà actifs, et chaque prestation est notée ensuite."
        ),
    },
}


def faq_ville(v):
    """Questions propres à la ville — pas les mêmes que l'accueil."""
    n, autre = v["nom"], v["autre"][0]
    return [
        (f"Comment réserver un DJ à {n}&nbsp;?",
         f"Indiquez la date, le lieu dans {n} et votre budget dans "
         f'<a href="{APP}" target="_blank" rel="noopener">l\'application AlloDJ</a>. '
         f"La plateforme désigne un DJ disponible à {n} pour cette date, adapté à votre "
         f"type d'événement. La réservation est confirmée par un acompte de <b>10&nbsp;%</b>."),
        (f"Combien coûte un DJ à {n}&nbsp;?",
         f"C'est vous qui annoncez le budget&nbsp;: AlloDJ cherche un DJ de {n} dans cette "
         f"fourchette plutôt que de vous faire comparer des devis. La seule règle fixe est "
         f"l'<b>acompte de 10&nbsp;%</b>, le solde étant réglé 3&nbsp;jours avant "
         f"l'événement. Le tarif dépend du DJ, de la durée et du matériel demandé."),
        (f"Peut-on réserver un DJ à {n} au dernier moment&nbsp;?",
         f"Cela dépend des disponibilités du soir demandé. La plateforme ne propose que "
         f"des DJs réellement libres à cette date&nbsp;: si aucun ne l'est à {n}, elle ne "
         f"vous fera pas patienter sur une promesse."),
        (f"AlloDJ loue-t-il aussi la sonorisation à {n}&nbsp;?",
         f"Oui. La location de matériel de sonorisation se réserve depuis l'application, "
         f"au même endroit que le DJ, pour les prestations à {n}."),
        (f"Et si mon événement a lieu à {autre}&nbsp;?",
         f'AlloDJ couvre aussi {autre} — voir la page '
         f'<a href="{v["autre"][1]}">booking DJ à {autre}</a>. Le fonctionnement est '
         f"identique&nbsp;: date, lieu, budget, puis un DJ désigné."),
        ("Comment devient-on DJ sur AlloDJ&nbsp;?",
         "On ne postule pas. L'entrée se fait <b>sur recommandation d'au moins 3 DJs "
         "déjà actifs</b> sur la plateforme. Ce sont eux qui se portent garants du "
         "niveau et du sérieux du nouveau profil."),
    ]


def bloc(html, ouverture, fermeture="</section>"):
    """Extrait une section entière depuis sa balise d'ouverture."""
    i = html.index(ouverture)
    j = html.index(fermeture, i) + len(fermeture)
    return html[i:j]


def construire(cle, v, source):
    h = source

    # ── En-tête ────────────────────────────────────────────────────────────
    url = BASE + v["fichier"]
    h = re.sub(r"<title>.*?</title>", f'<title>{v["titre"]}</title>', h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="{v["desc"]}">', h)
    h = h.replace('<link rel="canonical" href="' + BASE + '">',
                  '<link rel="canonical" href="' + url + '">')
    # une page ville n'a pas de version anglaise : on retire les hreflang
    h = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', '', h)
    h = h.replace('<meta property="og:url" content="' + BASE + '">',
                  '<meta property="og:url" content="' + url + '">')
    for balise in ('og:title', 'twitter:title'):
        h = re.sub(rf'(<meta (?:property|name)="{balise}" content=")[^"]*(">)',
                   rf'\1Booking DJ {v["nom"]} — Réserver un DJ à {v["nom"]}\2', h)
    for balise in ('og:description', 'twitter:description'):
        h = re.sub(rf'(<meta (?:property|name)="{balise}" content=")[^"]*(">)',
                   rf'\1{v["desc"]}\2', h)
    h = h.replace('<meta name="geo.placename" content="Douala, Yaoundé">',
                  f'<meta name="geo.placename" content="{v["nom"]}">')

    # ── Héros ──────────────────────────────────────────────────────────────
    h = h.replace('<span class="rt">Booking DJ · Douala / Yaoundé</span>',
                  f'<span class="rt">Booking DJ · {v["nom"]}</span>')
    h = re.sub(r'<h1>.*?</h1>',
               '<h1>\n            <span class="ln"><span>%s</span></span>\n'
               '            <span class="ln"><span class="hot">%s</span></span>\n'
               '            <span class="ln"><span class="out">%s</span></span>\n          </h1>'
               % v["h1"], h, flags=re.S)
    h = re.sub(r'<p class="lede"><b>Booking et réservation.*?</p>',
               f'<p class="lede">{v["chapo"]}</p>', h, flags=re.S)
    # le sélecteur de ville du formulaire est verrouillé sur la ville de la page
    h = re.sub(r'<select id="q-ville" name="ville">.*?</select>',
               f'<select id="q-ville" name="ville"><option>{v["nom"]}</option></select>',
               h, flags=re.S)

    h = h.replace(
        '<h2 class="big rv">Un DJ pour chaque événement, à Douala comme à Yaoundé</h2>',
        f'<h2 class="big rv">Un DJ pour chaque événement à {v["nom"]}</h2>')
    h = h.replace(
        "AlloDJ couvre <b>huit types d'événements</b> à Douala et Yaoundé",
        f"AlloDJ couvre <b>huit types d'événements</b> à {v['nom']}")

    h = h.replace('<div class="cols" aria-hidden="true">',
                  f'<div class="cols" data-ville="{v["nom"]}" aria-hidden="true">')

    # ── Roster : seulement les DJs de la ville ─────────────────────────────
    h = h.replace('<h2 class="big rv">Des DJs vérifiés à Douala et Yaoundé</h2>',
                  f'<h2 class="big rv">Des DJs vérifiés à {v["nom"]}</h2>')
    h = re.sub(r'<p class="lede rv">Un DJ n\'entre pas dans le roster.*?</p>',
               f'<p class="lede rv">{v["roster"]}</p>', h, flags=re.S)
    figures = "\n        ".join(
        f'<figure class="rost" style="margin:0"><img src="assets/photos/{f}.jpg" '
        f'alt="DJ vérifié AlloDJ à {v["nom"]}" loading="lazy">'
        f'<figcaption class="meta"><b>{g}</b>{v["nom"]}</figcaption></figure>'
        for f, g in DJS[cle]
    )
    h = re.sub(r'(<div class="roster rvg"[^>]*>).*?(</div>)', r'\1\n        ' + figures + r'\n      \2',
               h, flags=re.S, count=1)
    h = h.replace('<span class="rt">Sur cooptation</span>',
                  f'<span class="rt">{len(DJS[cle])} DJs · {v["nom"]}</span>')

    # ── FAQ propre à la ville ──────────────────────────────────────────────
    qs = faq_ville(v)
    faq = "\n        ".join(
        '<details name="faq"%s>\n          <summary><h3>%s</h3></summary>\n'
        '          <p>%s</p>\n        </details>' % (' open' if i == 0 else '', q, r)
        for i, (q, r) in enumerate(qs)
    )
    h = re.sub(r'(<div class="faq rvg">).*?(\n      </div>)', r'\1\n        ' + faq + r'\2',
               h, flags=re.S, count=1)
    h = h.replace('<h2 class="big rv">Ce qu\'on nous demande le plus</h2>',
                  f'<h2 class="big rv">Réserver un DJ à {v["nom"]}, en pratique</h2>')

    # ── Liens croisés : chaque page pointe vers l'autre et vers l'accueil ──
    autre_nom, autre_url = v["autre"]
    h = h.replace(
        '<div><h4>Villes</h4><ul><li><a href="#a1">Booking DJ à Douala</a></li>'
        '<li><a href="#a1">Booking DJ à Yaoundé</a></li>',
        f'<div><h4>Villes</h4><ul><li><a href="/">Booking DJ au Cameroun</a></li>'
        f'<li><a href="{autre_url}">Booking DJ à {autre_nom}</a></li>')
    # les ancres de section deviennent absolues depuis une page ville
    h = h.replace('<a href="#a3">DJ pour mariage au Cameroun</a>',
                  f'<a href="#a3">DJ pour mariage à {v["nom"]}</a>')
    # le sélecteur de langue n'a pas de cible ici
    h = re.sub(r'<p class="lang".*?</p>\n\s*', '', h, flags=re.S)
    h = re.sub(r'<div class="langbar".*?</div>\n\n', '', h, flags=re.S)
    # les sections A/B sont bien présentes ici : seul le logo, qui visait « #a1 »
    # — l'ouverture de l'accueil, absente d'une page ville — est à rebrancher.
    h = retour_accueil.page_avec_sections(h)

    # ── Données structurées ───────────────────────────────────────────────
    h = json_ld(h, cle, v, url)

    return h


def json_ld(h, cle, v, url):
    brut = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', h, re.S).group(1)
    g = json.loads(brut)

    ancre = {
        "Organization": BASE + "#org",
        "WebSite": BASE + "#site",
    }
    garde = []
    for n in g["@graph"]:
        t = n["@type"]
        if t in ("Organization", "WebSite"):
            garde.append(n)  # entités partagées : même @id sur toutes les pages
        elif t == "Service":
            n["@id"] = url + "#service"
            n["name"] = f'Booking et réservation de DJ à {v["nom"]}'
            n["areaServed"] = {"@type": "City", "name": v["nom"], "addressCountry": "CM"}
            n["description"] = (
                f'Trouver et réserver un DJ à {v["nom"]} : AlloDJ désigne le DJ adapté à '
                f"la date, au lieu et au budget de l'événement, puis verrouille la "
                f"réservation avec un acompte de 10 %. Location de sonorisation incluse."
            )
            garde.append(n)
        elif t == "WebPage":
            n["@id"] = url + "#webpage"
            n["url"] = url
            n["name"] = v["titre"]
            n["breadcrumb"] = {"@id": url + "#fil"}
            garde.append(n)
        elif t == "BreadcrumbList":
            garde.append({
                "@type": "BreadcrumbList",
                "@id": url + "#fil",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Accueil", "item": BASE},
                    {"@type": "ListItem", "position": 2,
                     "name": f'Booking DJ à {v["nom"]}', "item": url},
                ],
            })
        elif t == "FAQPage":
            garde.append({
                "@type": "FAQPage",
                "@id": url + "#faq",
                "isPartOf": {"@id": ancre["WebSite"]},
                "mainEntity": [
                    {"@type": "Question",
                     "name": re.sub(r'&nbsp;|<[^>]+>', ' ', q).strip(),
                     "acceptedAnswer": {
                         "@type": "Answer",
                         "text": re.sub(r'\s+', ' ', re.sub(r'&nbsp;|<[^>]+>', ' ', r)).strip()}}
                    for q, r in faq_ville(v)
                ],
            })
        # WebApplication : inutile de la répéter sur chaque page ville

    sortie = json.dumps({"@context": "https://schema.org", "@graph": garde},
                        ensure_ascii=False, indent=2)
    return re.sub(r'(<script type="application/ld\+json">\s*).*?(\s*</script>)',
                  lambda m: m.group(1) + sortie + m.group(2), h, flags=re.S)


def main():
    source = open(SRC, encoding="utf-8").read()
    for cle, v in VILLES.items():
        html = construire(cle, v, source)
        chemin = os.path.join(RACINE, v["fichier"])
        open(chemin, "w", encoding="utf-8").write(html)
        json.loads(re.search(r'application/ld\+json">\s*(.*?)\s*</script>', html, re.S).group(1))
        print(f'{v["fichier"]:20} {len(html)//1024} Ko  ·  {len(DJS[cle])} DJs  ·  JSON-LD valide')


if __name__ == "__main__":
    main()
