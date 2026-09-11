#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère allodj-pages-legales.xml, importable dans WordPress.

    python tools/build-wxr.py

Outils → Importer → WordPress → téléverser le fichier. Les cinq pages sont
créées d'un coup, avec le bon slug, le bon titre et le modèle « Page légale »
déjà sélectionné.

Le contenu vient des pages statiques déjà générées : on retire l'ossature
(titre, date, liens de bas de page) que `page-legal.php` fournit lui-même,
pour ne garder que le corps du texte.

Format WXR 1.2 — le même que l'export natif de WordPress.
"""

import html
import os
import re
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "allodj-pages-legales.xml")
SITE = "https://allodeejay.com"

# fichier source -> (titre de la page, slug WordPress, ordre dans le menu)
PAGES = [
    ("cgu.html", "Conditions générales d'utilisation", "cgu", 1),
    ("confidentialite.html", "Politique de confidentialité", "confidentialite", 2),
    ("mentions-legales.html", "Mentions légales", "mentions-legales", 3),
    ("suppression-de-compte.html", "Suppression de compte", "suppression-de-compte", 4),
    ("support.html", "Aide et support", "support", 5),
]


def corps(fichier):
    """Extrait le texte de l'article, sans l'ossature fournie par le gabarit."""
    s = open(os.path.join(RACINE, fichier), encoding="utf-8").read()

    m = re.search(r'<article class="legal">(.*?)</article>', s, re.S)
    if not m:
        sys.exit(f"{fichier} : bloc <article class=\"legal\"> introuvable")
    corps_html = m.group(1)

    # page-legal.php pose déjà le titre, la date et les liens de bas de page
    corps_html = re.sub(r"<h1>.*?</h1>", "", corps_html, flags=re.S)
    corps_html = re.sub(r'<p class="maj">.*?</p>', "", corps_html, flags=re.S)
    corps_html = re.sub(r'<div class="fin">.*?</div>', "", corps_html, flags=re.S)

    # les liens entre pages deviennent des chemins WordPress
    # « cgu.html#annulation-… » doit devenir « /cgu/#annulation-… »
    for f, _, slug, _o in PAGES:
        corps_html = re.sub(
            r'href="' + re.escape(f) + r'(#[\w-]+)?"',
            lambda m: 'href="/' + slug + '/' + (m.group(1) or "") + '"',
            corps_html,
        )
    corps_html = corps_html.replace('href="/"', f'href="{SITE}/"')

    # désindentation, lignes vides compressées
    corps_html = re.sub(r"^\s+", "", corps_html, flags=re.M)
    corps_html = re.sub(r"\n{3,}", "\n\n", corps_html)
    return corps_html.strip()


def item(titre, slug, contenu, ordre, date):
    return f"""	<item>
		<title>{html.escape(titre)}</title>
		<link>{SITE}/{slug}/</link>
		<pubDate>{date.strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
		<dc:creator><![CDATA[admin]]></dc:creator>
		<guid isPermaLink="false">{SITE}/?page_id={1000 + ordre}</guid>
		<description></description>
		<content:encoded><![CDATA[{contenu}]]></content:encoded>
		<excerpt:encoded><![CDATA[]]></excerpt:encoded>
		<wp:post_id>{1000 + ordre}</wp:post_id>
		<wp:post_date><![CDATA[{date.strftime('%Y-%m-%d %H:%M:%S')}]]></wp:post_date>
		<wp:post_date_gmt><![CDATA[{date.strftime('%Y-%m-%d %H:%M:%S')}]]></wp:post_date_gmt>
		<wp:comment_status><![CDATA[closed]]></wp:comment_status>
		<wp:ping_status><![CDATA[closed]]></wp:ping_status>
		<wp:post_name><![CDATA[{slug}]]></wp:post_name>
		<wp:status><![CDATA[publish]]></wp:status>
		<wp:post_parent>0</wp:post_parent>
		<wp:menu_order>{ordre}</wp:menu_order>
		<wp:post_type><![CDATA[page]]></wp:post_type>
		<wp:post_password><![CDATA[]]></wp:post_password>
		<wp:is_sticky>0</wp:is_sticky>
		<wp:postmeta>
			<wp:meta_key><![CDATA[_wp_page_template]]></wp:meta_key>
			<wp:meta_value><![CDATA[page-legal.php]]></wp:meta_value>
		</wp:postmeta>
	</item>"""


def main():
    date = datetime.now(timezone.utc)
    items = []
    for fichier, titre, slug, ordre in PAGES:
        contenu = corps(fichier)
        items.append(item(titre, slug, contenu, ordre, date))
        print(f"  {slug:24} {len(contenu):>6} octets")

    xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<!--
  Pages légales AlloDJ — généré par tools/build-wxr.py
  Import : Outils → Importer → WordPress
  Le modèle « Page légale » est déjà sélectionné sur chaque page.
-->
<rss version="2.0"
	xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
	xmlns:content="http://purl.org/rss/1.0/modules/content/"
	xmlns:wfw="http://wellformedweb.org/CommentAPI/"
	xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
	<title>AlloDJ</title>
	<link>{SITE}</link>
	<description>Pages légales</description>
	<pubDate>{date.strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
	<language>fr-FR</language>
	<wp:wxr_version>1.2</wp:wxr_version>
	<wp:base_site_url>{SITE}</wp:base_site_url>
	<wp:base_blog_url>{SITE}</wp:base_blog_url>
	<wp:author>
		<wp:author_id>1</wp:author_id>
		<wp:author_login><![CDATA[admin]]></wp:author_login>
		<wp:author_email><![CDATA[contact@allodeejay.com]]></wp:author_email>
		<wp:author_display_name><![CDATA[AlloDJ]]></wp:author_display_name>
	</wp:author>

{chr(10).join(items)}
</channel>
</rss>
"""
    open(SORTIE, "w", encoding="utf-8").write(xml)

    import xml.dom.minidom
    xml.dom.minidom.parse(SORTIE)   # échoue si le XML est mal formé

    print(f"\nallodj-pages-legales.xml — {len(PAGES)} pages, "
          f"{os.path.getsize(SORTIE) // 1024} Ko, XML valide")


if __name__ == "__main__":
    main()
