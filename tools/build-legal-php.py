#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère inc/legal-content.php pour un thème, depuis build-legal.py.

    python tools/build-legal-php.py --theme ../allodj-theme
    python tools/build-legal-php.py --theme ../allodj-theme-v2

Le contenu des pages légales vivait à deux endroits qui ne se parlaient
jamais : les fichiers statiques (via build-legal.py) et un copier-coller
manuel dans l'éditeur WordPress, que page-legal.php lisait avec
the_content(). Corriger le RCCM ou l'adresse dans build-legal.py ne
changeait donc RIEN sur le site en ligne — quelqu'un devait recoller le
texte à la main, et personne ne l'a fait : le site a affiché « À COMPLÉTER »
pendant des semaines après que le dépôt était corrigé.

Ce script élimine le copier-coller : il relit PAGES depuis build-legal.py —
la même source que les pages statiques — et écrit inc/legal-content.php, un
fichier de données pur que le thème charge directement (inc/legal.php).
Le contenu se déploie donc avec le thème ; il n'y a plus de base WordPress
à tenir à jour à la main pour que ces cinq pages soient justes.

Les liens internes (href="cgu.html"…) et les coordonnées (téléphone,
e-mail) sont remplacés par des jetons — {{LIEN:slug}}, {{TEL}},
{{TEL_HREF}}, {{EMAIL}} — résolus à l'affichage par
inc/legal.php:allodj_legal_resoudre_jetons(), pour rester justes sous
n'importe quel permalien WordPress et suivre les Réglages du Customizer.
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = pathlib.Path(__file__).resolve().parent
RACINE = ICI.parent


def charger_build_legal():
    """Importe build-legal.py par chemin (le tiret interdit `import build-legal`).

    Charger le module exécute ses définitions (PAGES, MAJ, slug()…) sans
    déclencher main() : le fichier protège son écriture disque derrière
    `if __name__ == "__main__"`, et ce chargement lui donne un autre nom.
    """
    chemin = ICI / "build-legal.py"
    spec = importlib.util.spec_from_file_location("allodj_build_legal", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


# ── Jetons ───────────────────────────────────────────────────────────────
# Un lien interne vers une autre page légale : href="cgu.html" ou
# href="cgu.html#fragment" → href="{{LIEN:cgu}}" (le fragment, s'il existe,
# reste tel quel juste après le jeton — inc/legal.php n'a pas à le connaître).
RE_LIEN = re.compile(r'href="([a-z-]+)\.html(#[a-z0-9-]+)?"')

TEL_HREF = "tel:+237699806672"
TEL_AFFICHE = "+237 699 80 66 72"
EMAIL = "contact@allodeejay.com"


def _remplacer_lien(m: re.Match) -> str:
    # Concaténation plutôt que f-string : compter des accolades imbriquées
    # à l'œil (f'{{{{...}}}}') est une source d'erreur inutile.
    # Le fragment (#ancre) va AVANT le guillemet fermant : la regex l'a
    # capturé à l'intérieur de l'attribut, il doit y rester.
    return 'href="' + "{{LIEN:" + m.group(1) + "}}" + (m.group(2) or "") + '"'


def tokeniser(html: str) -> str:
    html = RE_LIEN.sub(_remplacer_lien, html)
    html = html.replace(f'href="{TEL_HREF}"', 'href="{{TEL_HREF}}"')
    html = html.replace(f">{TEL_AFFICHE}<", ">{{TEL}}<")
    html = html.replace(f"mailto:{EMAIL}", "mailto:{{EMAIL}}")
    html = html.replace(f">{EMAIL}<", ">{{EMAIL}}<")
    return html


def contenu_page(bl, fichier: str, d: dict) -> str:
    """Le HTML entre <p class="maj"> et <div class="fin"> — avis, intro,
    sections — exactement l'assemblage de bl.page(), sans le h1/la date
    (page-legal.php les rend lui-même depuis le titre WordPress) ni le pied
    (déjà géré dynamiquement par allodj_liens_legaux())."""
    morceaux = []
    for a in d["avis"]:
        morceaux.append(a)
    morceaux.append(f'<p class="intro">{d["intro"]}</p>')
    for titre, paras in d["sections"]:
        ancre = bl.slug(titre)
        morceaux.append(f'<h2 id="{ancre}">{titre}</h2>')
        for p in paras:
            morceaux.append(p if p.startswith("<ul") else f"<p>{p}</p>")
    return tokeniser("\n      ".join(morceaux))


def php_chaine(s: str) -> str:
    """Chaîne PHP entre guillemets simples — seuls \\ et ' s'échappent."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", required=True)
    args = ap.parse_args()

    theme = pathlib.Path(args.theme)
    if not theme.is_absolute():
        theme = (RACINE / theme).resolve()
    if not theme.is_dir():
        sys.exit(f"{theme} introuvable.")

    bl = charger_build_legal()

    entrees = {}
    for fichier, d in bl.PAGES.items():
        slug = fichier[: -len(".html")]
        entrees[slug] = {"maj": bl.MAJ, "html": contenu_page(bl, fichier, d)}

    # Vérité mesurée : aucun jeton non résolu ne doit rester une fois toutes
    # les entrées assemblées, et aucune trace de l'ancien codage en dur.
    tout = "\n".join(e["html"] for e in entrees.values())
    fuites = {
        "href=\"...html\" oublié": bool(re.search(r'href="[a-z-]+\.html', tout)),
        "tel: en dur": TEL_HREF in tout,
        "téléphone affiché en dur": TEL_AFFICHE in tout,
        "mailto: en dur": f"mailto:{EMAIL}" in tout,
        "e-mail affiché en dur": f">{EMAIL}<" in tout,
    }
    en_fuite = [nom for nom, present in fuites.items() if present]
    if en_fuite:
        sys.exit("build-legal-php : substitution incomplète — " + ", ".join(en_fuite))

    lignes = [
        "<?php",
        "/**",
        " * Contenu des pages légales — GÉNÉRÉ, ne pas éditer à la main.",
        " *",
        " * Source : allodj-website-html/tools/build-legal.py (le dict PAGES),",
        " * régénéré ici par tools/build-legal-php.py. Pour changer ce texte,",
        " * modifier PAGES là-bas puis relancer les deux scripts.",
        " *",
        " * Jetons résolus à l'affichage par allodj_legal_resoudre_jetons()",
        " * (voir inc/legal.php) : {{LIEN:slug}}, {{TEL}}, {{TEL_HREF}}, {{EMAIL}}.",
        " *",
        " * @package AlloDJ",
        " */",
        "",
        "if ( ! defined( 'ABSPATH' ) ) {",
        "\texit;",
        "}",
        "",
        "return array(",
    ]
    for slug, e in entrees.items():
        lignes.append(f"\t{php_chaine(slug)} => array(")
        lignes.append(f"\t\t'maj'  => {php_chaine(e['maj'])},")
        lignes.append(f"\t\t'html' => {php_chaine(e['html'])},")
        lignes.append("\t),")
    lignes.append(");")

    sortie = "\n".join(lignes) + "\n"
    cible = theme / "inc" / "legal-content.php"
    cible.write_text(sortie, encoding="utf-8", newline="\n")
    print(f"{cible} — {len(entrees)} pages, {len(sortie) // 1024} Ko")
    for slug in entrees:
        print(f"  ok  {slug}")


if __name__ == "__main__":
    main()
