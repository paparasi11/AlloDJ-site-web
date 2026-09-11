"""Rend la barre du haut cliquable sur les pages autres que l'accueil.

Le problème, constaté sur les huit pages secondaires : l'en-tête est recopié
tel quel depuis index.html, donc le logo pointe sur « #a1 » et les sept onglets
sur « #a2 », « #a3 »… Sur l'accueil ces ancres font défiler la page. Ailleurs
elles ne mènent nulle part — la barre entière est inerte et il ne reste, pour
revenir à l'accueil, qu'un « ← Accueil » en bas de l'article.

Deux traitements, selon ce que la page contient réellement :

  pages légales     aucune section A/B : le logo ET les onglets doivent
                    renvoyer vers l'accueil, ancre comprise.
  pages ville       les sections A/B sont là, les onglets fonctionnent ;
                    seul le logo, qui visait « #a1 » absent, est à corriger.

Le logo ne renvoie pas vers « accueil#a1 » mais vers l'accueil tout court :
un logo qui ramène en haut de la page d'accueil, c'est ce que tout le monde
attend en cliquant dessus.
"""

from __future__ import annotations

import re

ANCRES = r"a[123]|b[1-7]"


def logo(html: str, accueil: str = "index.html") -> tuple[str, int]:
    """Le logo de la barre du haut ramène à l'accueil."""
    html, n = re.subn(
        r'(<a href=")#a1(" class="logo")',
        lambda m: m.group(1) + accueil + m.group(2),
        html,
    )
    return html, n


def onglets(html: str, accueil: str = "index.html") -> tuple[str, int]:
    """Les onglets de section renvoient vers la section, sur l'accueil."""
    return re.subn(
        rf'href="#({ANCRES})"',
        lambda m: f'href="{accueil}#{m.group(1)}"',
        html,
    )


def page_sans_sections(html: str, accueil: str = "index.html") -> str:
    """Page légale : logo et onglets renvoient tous vers l'accueil."""
    html, n1 = logo(html, accueil)
    html, n2 = onglets(html, accueil)
    if not n1:
        raise SystemExit("retour_accueil : logo introuvable dans l'en-tête.")
    if n2 < 7:
        raise SystemExit(f"retour_accueil : {n2} onglets réécrits, 7 attendus.")
    return html


def page_avec_sections(html: str, accueil: str = "index.html") -> str:
    """Page ville : seul le logo change, les onglets défilent sur place."""
    html, n = logo(html, accueil)
    if not n:
        raise SystemExit("retour_accueil : logo introuvable dans l'en-tête.")
    return html
