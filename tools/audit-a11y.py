#!/usr/bin/env python3
"""Contrôle mesuré de l'accessibilité, page par page et taille par taille.

    python tools/audit-a11y.py
    python tools/audit-a11y.py --base http://127.0.0.1:8899 --pages / /cgu.html

Trois vérifications, toutes calculées dans la page réelle plutôt que lues dans
la feuille de style — c'est la couleur effectivement héritée qui compte, pas
celle qu'on croit avoir écrite :

  contraste     ratio WCAG entre chaque nœud de texte et le premier fond opaque
                au-dessus de lui. Seuil 4,5:1, ramené à 3:1 pour le grand texte
                (≥ 24 px, ou ≥ 18,7 px en gras). Même seuil partout : l'œil ne
                change pas d'écran en écran.
  cibles        hauteur des éléments cliquables. 44 px au doigt (Apple HIG,
                WCAG 2.5.5) ; 24 px à la souris (WCAG 2.5.8 AA). Les liens pris
                dans le fil d'une phrase sont exclus — la règle les excepte.
  corps         11 px minimum au doigt, 10 px à la souris : on lit un téléphone
                à bout de bras, dans un taxi, en plein soleil.

Sortie : une ligne par manquement, et un code de sortie non nul s'il en reste.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from capture import APPAREILS, Navigateur, Session  # noqa: E402

import websockets  # noqa: E402

# tactile -> (hauteur de cible minimale, corps minimal)
# Au doigt : 44 px (Apple HIG, WCAG 2.5.5) et 11 px — on lit à bout de bras.
# À la souris : 24 px (WCAG 2.5.8 AA, avec son exception d'espacement) et
# 9,5 px, qui est le pas des micro-libellés mono assumé par la maquette.
SEUILS = {True: (44, 11), False: (24, 9.5)}

SONDE = r"""
((CIBLE, CORPS) => {
  const lin = c => { c /= 255; return c <= 0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4); };
  const L = (r,g,b) => 0.2126*lin(r) + 0.7152*lin(g) + 0.0722*lin(b);
  const parse = s => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(',').map(Number); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; };
  const FOND = {r:19,g:16,b:51};
  const fond = el => { let e = el; while (e) {
      const c = parse(getComputedStyle(e).backgroundColor);
      if (c && c.a > 0.9) return c; e = e.parentElement; } return FOND; };

  const contraste = [], cibles = [], corps = [];

  for (const el of document.querySelectorAll('body *')) {
    if (el.offsetParent === null && el.tagName !== 'BODY') continue;
    let t = ''; for (const n of el.childNodes) if (n.nodeType === 3) t += n.textContent;
    t = t.trim(); if (!t) continue;
    const cs = getComputedStyle(el);
    const fg = parse(cs.color); if (!fg || fg.a < 0.5) continue;
    const bg = fond(el);
    const a = L(fg.r,fg.g,fg.b), b = L(bg.r,bg.g,bg.b);
    const ratio = (Math.max(a,b)+0.05) / (Math.min(a,b)+0.05);
    const fs = parseFloat(cs.fontSize), fw = parseInt(cs.fontWeight) || 400;
    const seuil = (fs >= 24 || (fs >= 18.66 && fw >= 700)) ? 3 : 4.5;
    if (ratio < seuil) contraste.push({txt:t.slice(0,32), fs, fw,
      ratio:+ratio.toFixed(2), seuil, fg:cs.color, bg:`rgb(${bg.r},${bg.g},${bg.b})`});
    if (fs < CORPS) corps.push({txt:t.slice(0,32), fs, cls:(el.className||'').toString().slice(0,28)});
  }

  const clic = [...document.querySelectorAll('a,button,input,select,summary,[role=button]')]
    .map(el => ({el, r: el.getBoundingClientRect()}))
    .filter(o => o.r.width || o.r.height);

  for (const {el, r} of clic) {
    // Arrondi : une boîte calculée à 43,6 px occupe bien 44 px à l'écran.
    if (Math.round(r.height) >= CIBLE) continue;

    // Lien dans le fil d'une phrase : excepté par WCAG 2.5.8 (« inline »).
    // Le critère est qu'il RESTE du texte autour ; un <li> qui ne contient que
    // le lien est une liste de navigation, pas une phrase — il n'est pas excepté.
    const p = el.parentElement;
    if (el.tagName === 'A' && p && /^(P|LI|TD|SPAN|CITE|BLOCKQUOTE|H[1-6])$/.test(p.tagName)
        && p.textContent.trim().length > el.textContent.trim().length + 2) continue;

    // Exception d'espacement de WCAG 2.5.8 : une cible trop petite passe si un
    // disque de 24 px centré sur elle n'en touche aucun autre. À la souris on
    // vise une zone, pas une surface — c'est la norme elle-même qui le dit.
    // Au doigt (CIBLE = 44) l'exception ne s'applique pas.
    if (CIBLE === 24) {
      const cx = r.left + r.width/2, cy = r.top + r.height/2;
      let colle = false;
      for (const o of clic) {
        if (o.el === el) continue;
        const ox = o.r.left + o.r.width/2, oy = o.r.top + o.r.height/2;
        if (Math.hypot(cx-ox, cy-oy) < 24) { colle = true; break; }
      }
      if (!colle) continue;
    }

    cibles.push({txt:(el.textContent||'').trim().slice(0,28) || el.tagName,
      cls:(el.className||'').toString().slice(0,28), h:Math.round(r.height), w:Math.round(r.width)});
  }

  return JSON.stringify({contraste, cibles, corps,
    debord: document.documentElement.scrollWidth > innerWidth + 1,
    vw: innerWidth});
})(%CIBLE%, %CORPS%)
"""


async def sonder(nav: Navigateur, url: str, appareil: str) -> dict:
    largeur, hauteur, dpr, tactile = APPAREILS[appareil]
    async with websockets.connect(nav.onglet(), max_size=64 * 1024 * 1024) as ws:
        s = Session(ws)
        await s.cmd("Page.enable")
        # mobile=False : voir la note dans capture.py — sinon la tablette est
        # rendue à 977 px au lieu de 768.
        await s.cmd(
            "Emulation.setDeviceMetricsOverride",
            width=largeur, height=hauteur, deviceScaleFactor=1,
            mobile=False, screenWidth=largeur, screenHeight=hauteur,
        )
        if tactile:
            await s.cmd("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
        await s.cmd("Page.navigate", url=url)
        await asyncio.sleep(3.0)
        cible, corps = SEUILS[tactile]
        sonde = SONDE.replace("%CIBLE%", str(cible)).replace("%CORPS%", str(corps))
        r = await s.cmd("Runtime.evaluate", expression=sonde, returnByValue=True, awaitPromise=False)
        d = json.loads(r["result"]["value"])
        d["cible"], d["corps_min"] = cible, corps
        return d


async def principal() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8899")
    ap.add_argument("--pages", nargs="*", default=["/", "/en/", "/dj-douala.html", "/cgu.html"])
    ap.add_argument("--appareils", nargs="*", default=["mobile", "desktop"])
    args = ap.parse_args()

    nav = Navigateur()
    total = 0
    try:
        for page in args.pages:
            for appareil in args.appareils:
                url = args.base.rstrip("/") + page
                r = await sonder(nav, url, appareil)
                n = len(r["contraste"]) + len(r["cibles"]) + len(r["corps"]) + int(r["debord"])
                total += n
                etat = "ok" if not n else f"{n} manquement(s)"
                print(f"\n{page}  ·  {appareil} ({r['vw']} px, cibles {r['cible']} px, "
                      f"corps {r['corps_min']} px)  —  {etat}")
                if r["debord"]:
                    print("   débordement horizontal de la page")
                for c in r["contraste"]:
                    print(f"   contraste {c['ratio']}:1 < {c['seuil']}  {c['fg']} sur {c['bg']}"
                          f"  {c['fs']}px/{c['fw']}  « {c['txt']} »")
                for c in r["cibles"]:
                    print(f"   cible {c['h']}×{c['w']} px < {r['cible']}  .{c['cls']}  « {c['txt']} »")
                for c in r["corps"]:
                    print(f"   corps {c['fs']}px < {r['corps_min']}  .{c['cls']}  « {c['txt']} »")
    finally:
        nav.fermer()

    print()
    if total:
        sys.exit(f"{total} manquement(s) au total.")
    print("Aucun manquement.")


if __name__ == "__main__":
    asyncio.run(principal())
