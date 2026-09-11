#!/usr/bin/env python3
"""Captures d'écran fidèles du site, via le protocole DevTools de Chrome.

    python tools/capture.py                    # tout, dans tools/captures/
    python tools/capture.py --url http://127.0.0.1:8899/en/
    python tools/capture.py --seul mobile

Pourquoi pas `chrome --headless --screenshot` : sous Windows, Chrome refuse
toute fenêtre de moins de 500 px de large. Une capture demandée à 390 px est
en réalité rendue à 500 px puis rognée — la mise en page mobile n'est jamais
celle qu'on croit voir. On passe donc par CDP et
`Emulation.setDeviceMetricsOverride`, qui impose la vraie largeur de viewport
et le mode tactile.

Dépendances : websockets, requests (déjà installées).
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time

import requests
import websockets

RACINE = pathlib.Path(__file__).resolve().parent
SORTIE = RACINE / "captures"

CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

# nom : (largeur, hauteur, dpr, tactile)
APPAREILS = {
    "mobile": (390, 844, 2, True),      # iPhone 14
    "petit": (360, 780, 2, True),       # Android d'entrée de gamme
    "tablette": (768, 1024, 2, True),
    "desktop": (1440, 900, 1, False),
}


def _chrome() -> str:
    for c in CHROME:
        if pathlib.Path(c).exists():
            return c
    sys.exit("Chrome introuvable.")


def _port_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Navigateur:
    def __init__(self) -> None:
        self.port = _port_libre()
        self.profil = tempfile.mkdtemp(prefix="allodj-capture-")
        self.proc = subprocess.Popen(
            [
                _chrome(),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={self.profil}",
                "--no-first-run",
                "--no-default-browser-check",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.base = f"http://127.0.0.1:{self.port}"
        for _ in range(100):
            try:
                requests.get(f"{self.base}/json/version", timeout=0.5)
                return
            except requests.RequestException:
                time.sleep(0.1)
        sys.exit("Chrome n'a pas ouvert son port de débogage.")

    def onglet(self) -> str:
        r = requests.put(f"{self.base}/json/new?about:blank", timeout=5)
        if r.status_code >= 400:  # anciennes versions : GET
            r = requests.get(f"{self.base}/json/new?about:blank", timeout=5)
        return r.json()["webSocketDebuggerUrl"]

    def fermer(self) -> None:
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        shutil.rmtree(self.profil, ignore_errors=True)


class Session:
    """Un onglet CDP, avec numérotation des messages."""

    def __init__(self, ws) -> None:
        self.ws = ws
        self.n = 0

    async def cmd(self, methode: str, **params):
        self.n += 1
        await self.ws.send(json.dumps({"id": self.n, "method": methode, "params": params}))
        while True:
            msg = json.loads(await self.ws.recv())
            if msg.get("id") == self.n:
                if "error" in msg:
                    raise RuntimeError(f"{methode} : {msg['error']}")
                return msg.get("result", {})


async def capturer(nav: Navigateur, url: str, appareil: str, dest: pathlib.Path) -> None:
    largeur, hauteur, dpr, tactile = APPAREILS[appareil]
    async with websockets.connect(nav.onglet(), max_size=200 * 1024 * 1024) as ws:
        s = Session(ws)
        await s.cmd("Page.enable")
        # mobile=False à dessein : le drapeau « mobile » de Chrome impose une
        # fenêtre de mise en page de 980 px dès qu'on dépasse ~700 px de large
        # (une tablette demandée à 768 px se retrouvait rendue à 977). Le
        # tactile s'active séparément, ci-dessous.
        await s.cmd(
            "Emulation.setDeviceMetricsOverride",
            width=largeur,
            height=hauteur,
            deviceScaleFactor=dpr,
            mobile=False,
            screenWidth=largeur,
            screenHeight=hauteur,
        )
        if tactile:
            await s.cmd("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
        await s.cmd("Page.navigate", url=url)

        # Laisse le temps aux polices, aux images et aux compteurs animés.
        await asyncio.sleep(4.5)

        m = await s.cmd("Page.getLayoutMetrics")
        contenu = m["cssContentSize"]
        total = int(contenu["height"])

        # Vérité mesurée, pas supposée : le viewport a-t-il bien la largeur voulue,
        # et la page déborde-t-elle horizontalement ?
        r = await s.cmd(
            "Runtime.evaluate",
            expression=(
                "JSON.stringify({vw:innerWidth,"
                "scrollW:document.documentElement.scrollWidth,"
                "docH:document.documentElement.scrollHeight})"
            ),
            returnByValue=True,
        )
        mesure = json.loads(r["result"]["value"])

        # Capture pleine page : on force le viewport à la hauteur du document.
        await s.cmd(
            "Emulation.setDeviceMetricsOverride",
            width=largeur,
            height=min(total, 30000),
            deviceScaleFactor=dpr,
            mobile=False,
            screenWidth=largeur,
            screenHeight=hauteur,
        )
        await asyncio.sleep(1.2)

        shot = await s.cmd(
            "Page.captureScreenshot",
            format="png",
            captureBeyondViewport=True,
            clip={"x": 0, "y": 0, "width": largeur, "height": min(total, 30000), "scale": 1},
        )
        dest.write_bytes(base64.b64decode(shot["data"]))

        debord = "OUI ⚠" if mesure["scrollW"] > mesure["vw"] + 1 else "non"
        print(
            f"  {appareil:9s} {dest.name:28s} viewport {mesure['vw']:4d} px · "
            f"page {mesure['docH']:5d} px · débordement horizontal : {debord}"
        )


async def principal() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8899/")
    ap.add_argument("--seul", choices=list(APPAREILS), help="un seul appareil")
    ap.add_argument("--suffixe", default="", help="ajouté au nom des fichiers")
    args = ap.parse_args()

    SORTIE.mkdir(exist_ok=True)
    appareils = [args.seul] if args.seul else list(APPAREILS)

    nav = Navigateur()
    try:
        print(f"Capture de {args.url}")
        for a in appareils:
            dest = SORTIE / f"{a}{args.suffixe}.png"
            await capturer(nav, args.url, a, dest)
    finally:
        nav.fermer()
    print(f"\n→ {SORTIE}")


if __name__ == "__main__":
    asyncio.run(principal())
