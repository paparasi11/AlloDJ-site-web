# AlloDJ — site vitrine · état du projet

Point d'entrée pour reprendre le travail dans une nouvelle conversation.
Lire aussi `DESIGN.md` (système visuel) et `HISTORIQUE.md` (décisions déjà prises).

Dernière mise à jour : 2026-09-08 (soir).

---

## 1. Ce que c'est

Site vitrine **statique** pour **AlloDJ** — marketplace de réservation de DJs et de
location de sonorisation au Cameroun (Douala / Yaoundé). HTML/CSS/JS écrits à la main,
**aucun framework, aucun build**.

Ne pas confondre avec deux autres dossiers :

| Chemin | Quoi |
|---|---|
| `C:\Users\Malcom\Claude\Projects\allo dj app` | L'app **Flutter** — le vrai produit |
| `C:\Users\Malcom\Documents\claude\allodj-website` | Scaffold **Next.js** jamais commité, abandonné |
| `C:\Users\Malcom\Documents\claude\allodj-business` | Business plan, pitch deck, plan marketing |

---

## 2. Arborescence

```
allodj-website-html/
├── index.html            ← accueil FR — cible le terme NATIONAL « Cameroun »
├── dj-douala.html        ← généré par tools/build-villes.py — NE PAS ÉDITER
├── dj-yaounde.html       ← idem
├── en/index.html         ← généré par tools/build-en.py — NE PAS ÉDITER
├── site.webmanifest
├── console.html          ← direction alternative « table de mixage », gardée en archive
├── index.html.bak-*      ← sauvegardes horodatées avant refonte
├── robots.txt  sitemap.xml  llms.txt   ← couche SEO / GEO / AEO
├── tools/
│   ├── build-en.py                ← index.html → en/index.html
│   ├── build-villes.py            ← index.html → dj-douala / dj-yaounde
│   ├── gen-gemini.py              ← visuels via Gemini (à privilégier)
│   └── gen-evenements.py          ← visuels via pollinations (repli gratuit)
├── NOTES.md  DESIGN.md  HISTORIQUE.md
└── assets/
    ├── site.css  site.js     ← CSS et JS PARTAGÉS par les 4 pages
    ├── favicon.svg .ico -16 -32 -48, apple-touch-icon, icon-192/512
    ├── logo.png              logo PNG (nettoyé : l'original avait un halo gris)
    ├── logo-source.svg       SVG d'origine fourni par Malcom (avec plaque de fond)
    ├── logo-inline.svg       fragment nettoyé, prêt à inliner
    ├── logos/                les 7 variantes fournies (voir §5)
    ├── photos/
    │   ├── real-dj-01..08.jpg    VRAIES photos de 8 DJs — fournies par Malcom
    │   ├── evt-*.jpg             images d'ambiance générées par IA
    │   ├── crowd-wedding.jpg, birthday-balloons.jpg   idem
    │   └── dj-hero.jpg, dj-corporate.jpg   IA, plus référencées
    ├── covers/               7 pochettes de compiles générées par IA
    ├── phone-hero.mp4        rendu 3D du téléphone — RETIRÉ du site sur demande
    └── phone-poster.jpg
```

---

## 3. Faits produit — ne pas réinventer

Sourcés dans le dépôt Flutter et confirmés par Malcom :

- Acompte **10 %** à la réservation, solde **3 jours avant** l'événement
- **48 h** pour annuler sans frais
- Les DJs **ne postulent pas** : entrée sur **recommandation d'au moins 3 DJs déjà actifs**
- L'app web tourne déjà : **`https://appli.allodeejay.com/#/home`** ← cible de tous les CTA
- App Store / Google Play : **pas encore publiés** → badges « bientôt », jamais de faux lien
- Villes couvertes aujourd'hui : **Douala** et **Yaoundé**
- Contact : `contact@allodeejay.com` · `+237 699 80 66 72` · Kawai IT, Douala
- Compiles réelles de **DJ Fab** (= Serge Njewa, cofondateur) : Amafabiano Soweto,
  Careless Vibes, To Ibiza Club Mix, MCM For Ever, Rap Français 90,
  R&B Rap 2000's Oldschool, Zouk Miel

---

## 4. Règles d'honnêteté tenues jusqu'ici

À ne pas casser sans décision explicite de Malcom :

- **Aucun chiffre de notoriété inventé.** Cueup affiche « 4320 avis 5 étoiles » — c'est
  leur vrai chiffre, on ne le copie pas et on n'en invente pas un équivalent.
- **Aucun faux nom de DJ** collé sur une vraie photo. Les 8 photos sont de vraies
  personnes dont on ne connaît pas les noms de scène → étiquetées par **ville + style**.
- Les pochettes IA sont des **créations originales** inspirées du genre de chaque titre,
  pas des copies des vraies pochettes de DJ Fab.
- Les durées des compiles sont **illustratives**, pas des données réelles.

---

## 5. Logo

7 variantes fournies (`assets/logos/`). Contraste mesuré sur fond `#0A0A0B` :

| Variante | Découpe ? | Contraste |
|---|---|---|
| **Noir Alpha** ← **retenue** | oui (28 % opaque) | **19,3:1** |
| Rose | non, plaque pleine | 15,3:1 |
| Bleu | non, plaque pleine | 11,5:1 |
| Principal / Rose alpha / Bleu apla | non, plaque pleine | 10–11:1 |
| Noir | oui | 1,06:1 — invisible sur fond sombre |

Le SVG source contenait un `<rect>` de fond `#1d1d1b` : **retiré**. Le logo est inliné
dans `index.html` avec `fill:currentColor` → pilotable en CSS, et ses **7 rayons sont
animés** individuellement (apparition décalée au chargement, pulsation au survol).

---

## 6. Environnement — pièges connus

- **L'aperçu intégré ne charge aucune image locale.** La page y est servie en `data:`,
  donc `assets/...` ne résout pas. Ce n'est *jamais* un bug du site — vérifié plusieurs fois.
- **La bonne façon de prévisualiser** — servir le dossier en HTTP, les chemins relatifs
  résolvent alors normalement :
  ```bash
  cd C:/Users/Malcom/Documents/claude/allodj-website-html
  python -m http.server 8899 --bind 127.0.0.1
  # puis http://127.0.0.1:8899/
  ```
  Contrôle rapide dans la console du navigateur :
  `[...document.images].filter(i=>i.complete&&!i.naturalWidth).length` doit valoir 0.
- Le double-clic sur `index.html` marche aussi (`file://` résout les chemins relatifs).
- **Chrome garde l'onglet en cache.** Relancer le fichier ne recharge pas le disque →
  faire **Ctrl+Maj+R**, sinon on croit à tort que rien n'a changé.
- **Malcom ne peut pas transmettre d'images par le chat** (elles ne sont pas écrites sur
  le disque). Méthode qui marche : il dépose les fichiers dans un dossier, ou une archive
  `.rar` (WinRAR est installé : `C:\Program Files\WinRAR\UnRAR.exe`).
- **CLI Claude hors PATH** : `C:\Users\Malcom\AppData\Roaming\Claude\claude-code\2.1.260\claude.exe`
- **MCP `magic` (21st.dev) : branché et fonctionnel** depuis le 2026-09-07, dans
  `~/.claude.json` scope user. ⚠️ Les ~18 autres serveurs sont déclarés dans
  `~/.claude/settings.json` → **mauvais fichier**, Claude Code n'y lit pas les MCP.
  Sauvegarde avant modif : `C:\Users\Malcom\.claude.json.bak-20260907-221707`

---

## 7. Vérification avant publication

Pas de build, donc contrôles manuels :

```bash
# équilibre des balises + syntaxe JS + assets manquants
python -c "import html.parser, re, os; ..."   # cf. historique des commandes
node --check <script extrait>
```

Attention : un validateur naïf signale de faux `errors` sur les balises SVG
auto-fermantes (`<path/>`). Le signal fiable est **`unclosed: []`**.

---

## 7 bis. SEO / GEO / AEO — ce qui est en place

- `<head>` : canonical, robots, Open Graph (10 balises), Twitter card, geo.region CM
- **JSON-LD** unique en `@graph` : Organization (+ `sameAs` Facebook), WebSite
  (+ SearchAction), Service (+ catalogue des 9 prestations), WebApplication, FAQPage
- **Section FAQ visible** (piste B5) : 8 questions/réponses en `<details>` — c'est
  ce que les moteurs de réponse extraient. La sortie est passée en B6.
- `robots.txt` autorise explicitement GPTBot, ClaudeBot, PerplexityBot,
  Google-Extended, Applebot, meta-externalagent…
- `llms.txt` : brief factuel pour les IA, avec une section « précisions pour une
  citation exacte » qui interdit d'inventer des chiffres de notoriété.

⚠️ **Domaine à confirmer** : tout est écrit sur `https://allodeejay.com/`.
Si le site vitrine part sur une autre adresse, faire un chercher/remplacer sur
`index.html`, `robots.txt`, `sitemap.xml` et `llms.txt`.

## 7 ter. Génération des visuels d'événements

`python tools/gen-evenements.py [--force] [clés…]` — service pollinations.ai,
gratuit, sans clé. Leçons apprises en trois passes :

1. Les gros plans de visages sortent déformés → cadrer large, de profil ou de dos.
2. Mais « plan large + pas de visage » produit des **salles vides**. Pour les scènes
   de foule il faut le style `STYLE_FOULE`, qui lève les négatifs anti-visage.
3. Les graines rendent chaque image reproductible ; les images écartées sont dans
   `assets/photos/_avant-refonte-evt/`.

Images désormais orphelines (les 2 premières sont celles que l'audit a signalées
comme cassées) : `crowd-wedding.jpg`, `birthday-balloons.jpg`, `dj-corporate.jpg`,
`dj-hero.jpg`.

## 7 quater. Architecture des pages — règle à ne pas casser

**Une seule source : `index.html`.** Les trois autres pages en sont dérivées par
script. Modifier le français, puis relancer :

```bash
python tools/build-villes.py && python tools/build-en.py
```

Les scripts **échouent bruyamment** si une chaîne attendue a disparu — c'est
voulu. Éditer `dj-douala.html`, `dj-yaounde.html` ou `en/index.html` à la main,
c'est garantir que la prochaine génération écrase le travail.

| URL | Requête visée |
|---|---|
| `/` | booking DJ **Cameroun** |
| `/dj-douala.html` | booking / réserver un DJ **Douala** |
| `/dj-yaounde.html` | booking / réserver un DJ **Yaoundé** |
| `/en/` | DJ booking Cameroon (anglais) |
| `/cgu.html` · `/confidentialite.html` · `/mentions-legales.html` · `/suppression-de-compte.html` | pages légales, générées par `tools/build-legal.py` |

Le CSS et le JS sont sortis dans `assets/site.css` et `assets/site.js` : 4 pages
les partagent, le navigateur ne les télécharge qu'une fois.

**Langue** : pas de redirection automatique. Google la déconseille explicitement
(elle empêche les moteurs de voir les deux versions). Le site affiche un
sélecteur FR/EN permanent et, si `navigator.language` diffère, une bannière qui
*propose* l'autre version et retient le choix dans `localStorage`.

## 7 quinquies. Ce que dit la recherche GEO (et ce qu'on en a fait)

Étude de référence : *GEO: Generative Engine Optimization*, Princeton / IIT Delhi
/ Georgia Tech / Allen Institute — <https://arxiv.org/abs/2311.09735>

| Levier | Gain mesuré | État |
|---|---|---|
| Quotation Addition | **+41 %** | Partiel — une citation attribuée (règle de cooptation). **Il manque de vrais verbatims clients/DJs.** |
| Statistics Addition | **+40 %** | Fait — chaque chapô porte des chiffres réels (10 %, 48 h, 3 DJs, 8 types, 7 compiles) |
| Cite Sources | **+30 %** | Partiel — liens vers l'app. **Bloqué tant que les pages légales n'existent pas.** |
| Fluency / Easy-to-understand | +15 à 30 % | Fait — chapôs autoportants de 40-60 mots |
| **Keyword stuffing** | **≈ 0 %** | Évité — densités mesurées entre 0,6 et 2,9 % |

Le dernier point compte : bourrer de mots-clés **ne sert à rien** pour les
moteurs génératifs. Les mots-clés restent utiles pour Google classique, d'où leur
placement en titre, H1/H2, première phrase et ancres — pas en `<meta keywords>`,
balise morte depuis 2009.

## 7 sexies. ⚠️ Le paiement est simulé — et le site ne le dit pas

Vérifié dans le dépôt Flutter le 2026-09-08 :

- `cart_page.dart` affiche « Paiement simulé (test) — aucun débit réel »
- `quote_service.dart` : `paid` est un booléen posé côté client
- **aucun prestataire de paiement intégré** (ni Stripe, ni CinetPay, ni Monetbil,
  ni Campay, ni Flutterwave)

Or le site vitrine écrit « verrouille la réservation avec un acompte de 10 % ».
Les CGU générées le disent maintenant explicitement (encadré « Paiement en phase
de test »), mais **la page d'accueil, elle, ne le dit toujours pas**. Décision à
prendre par Malcom : soit ouvrir de vrais paiements, soit nuancer la formulation
du héros. En l'état il y a un écart entre la promesse et le produit.

## 7 septies. Verbatims — dispositif prêt, contenu à collecter

`data/verbatims.json` est **vide, et c'est l'état correct**. Tant qu'il l'est, la
section n'apparaît pas sur le site.

`tools/build-verbatims.py` refuse de publier une entrée sans `consentement: true`,
sans `source`, sans auteur, ou dont la citation contient un mot de gabarit
(« exemple », « à remplir »…). Testé : les deux cas ont bien été rejetés.

Raison de cette rigidité : un faux avis client est une pratique commerciale
trompeuse (directive Omnibus 2019/2161) et une violation des règles anti-spam de
Google sur les données structurées — le rich snippet saute pour tout le domaine.
Sur un site dont l'argument est « on ne réserve plus au bouche-à-oreille », c'est
aussi une contradiction frontale.

**Marche à suivre : `docs/collecte-verbatims.md`** — message WhatsApp prêt à
envoyer, trois questions, critères de tri, gestion du consentement. Six verbatims
suffisent (4 clients + 2 DJs).

## 7 octies. ⚠️ Les notes des DJs affichées dans l'app sont inventées

Vérifié le 2026-09-09 dans `lib/core/data/dj_data.dart` : les 10 DJs y portent
une note **écrite en dur**, entre 4,5 et 5,0.

| DJ Boul | DJ Batigoal | DJ Guyzo | DJ Landro | DJ Leslo |
|---|---|---|---|---|
| 4.9 | 4.8 | 5.0 | 4.7 | 4.9 |

| DJ René | DJ Next | Jay Crystal | DJ Macari | DJ Guty |
|---|---|---|---|---|
| 4.6 | 4.8 | 5.0 | 4.7 | 4.5 |

Aucune ne vient de la collection `reviews`. Ce sont des littéraux, sur des DJs
réels et nommés, **affichés aux utilisateurs en production**.

C'est plus grave que la question du site vitrine : ces notes influencent un choix
de prestataire. Deux issues possibles — calculer la note depuis `ratingAvg` /
`ratingCount` (le `ReviewService` sait déjà le faire), ou ne rien afficher tant
qu'un DJ n'a pas d'avis. **Ne surtout pas reprendre ces notes sur le site.**

Vérifié aussi : la collection `reviews` contient **2 documents**, tous deux issus
de comptes de test (`paparazzi → djmalcom`, `muketee2005 → DJ`). Aucun avis
client réel à ce jour. `tools/import-avis.py` les écarte automatiquement.

## 7 nonies. Thème WordPress — synchronisé (v1.1.0, 2026-09-09)

`C:\Users\Malcom\Documents\claude\allodj-theme` · archive `allodj-theme.zip`
(60 fichiers, 2 Mo). Thème **classique**, pas un thème bloc : le CSS et le JS sur
mesure se battraient avec l'éditeur de blocs.

Ce que le thème apporte par rapport au site statique :

| Élément | Où |
|---|---|
| FAQ (12 questions), source unique | `inc/faq.php` → alimente le gabarit **et** le JSON-LD, impossible de désynchroniser |
| SEO complet | `inc/seo.php` — titre, meta, OG/Twitter, JSON-LD `@graph`, favicons, manifeste |
| `robots.txt` | filtre `robots_txt`, respecte le réglage « décourager les moteurs » |
| `/llms.txt` | route réécrite, gabarit `inc/llms.txt` avec substitution des réglages |
| `/site.webmanifest` | route réécrite, `start_url` calculée depuis `home_url()` |
| Verbatims | `template-parts/b6-verbatims.php`, filtre `allodj_verbatims`, **vide = section absente** |
| Pages légales | modèle `page-legal.php`, à choisir dans Attributs de page |

**Le thème s'efface devant une extension SEO.** `allodj_seo_delegue()` détecte
Yoast, Rank Math, SEOPress et AIOSEO : si l'une est active, le thème n'émet ni
canonical ni JSON-LD. Deux balises valent moins bien qu'une.

Numérotation des pistes : A1 A2 A3 · B1 B2 B3 B4 · **B5 FAQ** · **B6 verbatims**
· **B7 sortie**. Ne pas la casser sans mettre à jour `front-page.php`, la nav de
repli dans `functions.php` et les ardoises.

⚠️ **Après activation**, passer une fois par Réglages → Permaliens et
enregistrer, sinon `/llms.txt` et `/site.webmanifest` renvoient 404. Le thème le
fait via `after_switch_theme`, mais pas lors d'une simple mise à jour du thème
déjà actif.

Le thème n'embarque **pas** de pages villes : sur WordPress ce sont des pages à
créer. Le contenu est dans `tools/build-villes.py` du site statique.

## 7 decies. Consentement (RGPD) — dispositif complet

Depuis l'ajout de Google Analytics et des campagnes publicitaires, le site
dépose des traceurs : une bannière est devenue obligatoire.

**Fichiers** : `assets/consent.js` (site statique) et `assets/js/consent.js`
(thème), styles dans la feuille partagée.

**Parti pris : rien de Google n'est chargé avant le choix.** Pas même
`gtag.js` — une requête vers googletagmanager.com transmet déjà l'IP, ce qu'on
venait justement de supprimer en rapatriant les polices. Google propose un mode
« avancé » (tag chargé, consentements refusés, pings sans cookie) qui permet la
modélisation des conversions ; il est documenté en tête du fichier, activable en
une ligne, mais contesté par plusieurs autorités européennes.

**Consent Mode v2** : les quatre signaux (`ad_storage`, `ad_user_data`,
`ad_personalization`, `analytics_storage`) sont posés en `denied` avant toute
commande `config`. L'ordre est imposé par Google, un `default` après un `config`
ne prend pas.

**Conformité CNIL** : refuser prend un clic, comme accepter ; les deux boutons
ont la même taille et le même style. Choix conservé 13 mois, puis la question
est reposée. Lien « Gérer mes cookies » en pied de page pour revenir dessus.

**Configuration** — site statique : bloc `window.AlloDJConsent` dans le `<head>`
d'`index.html`. Thème : Apparence → Personnaliser, champs *Google Analytics 4*
et *Google Ads*. **Tant que les identifiants sont vides, aucun tag n'existe et
la bannière ne s'affiche pas** : c'est l'état correct, pas un oubli.

⚠️ **Si Analytics est aussi posé ailleurs** (Site Kit, extension d'insertion de
code, balise collée dans l'en-tête), il se chargera **avant** la bannière et la
contournera. Il faut le retirer de ces endroits — un seul point d'entrée.

Vérifié le 2026-09-09 : refus → aucun tag chargé, quatre signaux `denied`, zéro
requête externe. Acceptation → gtag chargé, `config` GA4 et Ads, quatre signaux
`granted`. Choix partiel → `analytics_storage: granted` seul.

## 7 undecies. Identité juridique — ALLO DJ SARL (2026-09-09)

Source : attestation de conformité fiscale + infos fournies par Malcom.

| Champ | Valeur |
|---|---|
| Dénomination | ALLO DJ SARL |
| Forme | SARL |
| Capital | 1 000 000 FCFA |
| RCCM | CM-NSI-02-2023B13-00329 |
| NIU | M012317865859Z |
| Centre des impôts | CDI Yaoundé 2 |
| **Siège social** | **Ngousso, Yaoundé** |
| Directeur de la publication | Njewa Ngangue Serge (= DJ Fab, cofondateur) |
| Droit applicable | OHADA + droit camerounais supplétif, tribunaux de Yaoundé |
| Hébergeur site | Hostinger International Ltd, Larnaca, Chypre |
| Hébergeur app | Google Firebase (USA) |

⚠️ **Le siège est Yaoundé, pas Douala.** Malcom avait d'abord dit « siège
Douala », puis a fourni l'adresse Ngousso/Yaoundé — cohérente avec l'attestation
fiscale (CDI Yaoundé 2). C'est Yaoundé qui a été retenu partout : mentions
légales, JSON-LD (`addressLocality`), bloc contact, défaut du Customizer.

**Le marketing reste Douala-first** (page `dj-douala.html` en premier, colonnes
du héros, ordre du pied de page) — c'est un choix commercial séparé de l'adresse
du siège, non modifié.

Les 5 pages légales sont **complètes**, plus aucun champ `À COMPLÉTER`.

## 7 duodecies. Visuels d'événements (A3) — 6/8 posés (2026-09-09)

`Downloads.rar` de Malcom contenait 9 images Gemini + les 8 portraits DJ
(identiques à ceux déjà en ligne, rien à changer là).

**Posées, recadrées en 1000×800 (5:4), q80 :**

| clé | source | note |
|---|---|---|
| entreprise | nano-banana | gala hôtel, DJ + MacBook visibles |
| anniversaire | vpyjro | gâteau bougies-cierge, terrasse |
| bapteme | idsn94 | cour, chaises bleues, jollof + poisson |
| mariage | vwlvtk | réception dansante, njangi (billets en l'air), DJ en fond |
| tradi | c12kop | la dot complète : notables, cartons, marmites, enclos à chèvres, poulet |
| diplome | r38e7y | toques en l'air, écharpes drapeau — **bannière « University of Yaoundé II · Promotion 2024 » gardée sur choix de Malcom** |
| prive | 11amru | rooftop, soya + plantain, skyline |
| club | lbegell | boîte, écran « DJ KAMELEON », bouteilles à cierges |

Les 6 sont cohérentes : fond sombre, foule, lumière ambre, mélange de tenues
(costumes, robes, jeans, quelques pagnes) — Malcom voulait éviter le cliché
« tout le monde en traditionnel ».

**Les 8 sont posées.** Série cohérente : fond sombre, foule, lumière ambre,
mélange de tenues (costumes, robes, jeans, pagnes) — pas de cliché folklorique. Prompts à jour dans `docs/prompts-evenements.md` et
`tools/gen-gemini.py`. Anciennes sauvegardées dans
`assets/photos/_avant-downloads-rar/`.

## 7 terdecies. Version anglaise sur WordPress (thème 1.9.0, 2026-09-09)

Servie sous **`/en/`**, sans extension multilingue.

- `tools/build-i18n.py` génère `languages/en_US.po` + `.mo` (240 chaînes) à
  partir des `__()` du thème. Réutilise la table de `../allodj-website-html/
  tools/build-en.py`. **Échoue si une chaîne n'a pas de traduction** — pas
  d'anglais à moitié.
- `inc/i18n.php` force la locale `en_US` quand l'URL commence par `/en/`,
  réécrit `/en/` → accueil et `/en/<slug>/` → page, préfixe les liens internes,
  pose `<html lang="en">`, l'`og:locale`, le `hreflang` réciproque et le
  sélecteur FR/EN (statique, pas de redirection — reco Google).
- `inc/seo.php` : `og:locale`, `inLanguage`, `manifest.lang` deviennent
  dynamiques via `allodj_lang()`.

**Régénérer après toute modif de texte du thème :**
```
python tools/build-i18n.py && python tools/verifier-theme.php
```

**Limite assumée** : traduit l'ossature du thème (nav, sections, FAQ, 404…),
**pas** le contenu éditorial. Sur `/en/cgu/` l'habillage est anglais mais le
texte des CGU reste français — c'est du contenu de page, pas des `__()`. Pour
des pages légales anglaises, les créer dans WordPress avec les slugs
`en/cgu` etc. Pour un vrai site bilingue à contenu éditorial double : Polylang.

⚠️ **Après activation** : Réglages → Permaliens → Enregistrer (les règles
`/en/` en dépendent). Le thème le fait via `after_switch_theme`.

## 8. Reste à faire

- [x] ~~Pages légales~~ — faites le 2026-09-08 depuis le contenu du dépôt Flutter
- [ ] Renseigner GA4 / Google Ads dans le Personnalisateur, et retirer Analytics de Site Kit
- [x] ~~Champs administratifs des mentions légales~~ — tous renseignés le 2026-09-09 dans `mentions-legales.html` (7) et `cgu.html` (1) :
      forme juridique, capital, RCCM, n° contribuable, adresse complète, directeur
      de publication, hébergeur du site vitrine, droit applicable. Ils s'affichent
      en orange sur la page — impossible de les oublier
- [ ] **Faire relire les CGU par un juriste.** Le fichier source Flutter porte
      lui-même la mention « brouillon à faire relire avant mise en production »
- [x] ~~Les 8 visuels du carrousel A3~~ — posés le 2026-09-09 (images Gemini)
- [ ] **Répercuter la FAQ et la couche SEO dans le thème WordPress** — le thème
      `../allodj-theme` est resté sur 8 sections, sans FAQ ni JSON-LD
- [ ] Image `assets/og-allodj.jpg` (1200×630) — référencée en Open Graph, pas encore créée
- [ ] **Retirer ou recalculer les notes en dur de `dj_data.dart`** (voir 7 octies)
- [ ] **Collecter 6 vrais verbatims** — voir `docs/collecte-verbatims.md`. Levier
      GEO le plus fort (+41 %), dispositif technique déjà en place
- [ ] **Recharger les crédits Gemini** — `tools/gen-gemini.py` est prêt mais l'API
      renvoie « prepayment credits are depleted » (clé valide, compte à sec)
- [ ] Versions anglaises des pages villes, si le trafic anglophone le justifie
- [x] ~~Répercuter FAQ, SEO, animations, favicons, consentement, i18n dans le thème~~ — v1.9.0
- [ ] Traduire les pages légales en anglais si besoin (slugs `en/cgu`…)
- [ ] Créer les 4 pages légales dans WordPress avec le modèle « Page légale »
- [ ] Créer les 2 pages villes dans WordPress (contenu dans `tools/build-villes.py`)
- [ ] Section « photos rondes de DJ éparpillées » façon Cueup — demandée, jamais faite
- [ ] 2 photos jamais exploitées dans `Downloads` (`00.59.38`, `01.00.32`) — d'autres DJs ?
- [ ] Trancher le sort de `console.html` (archive ou suppression)
- [ ] ⚠️ **Révoquer la clé API Figma** — elle a fuité en clair dans une conversation
      (elle est en `args` au lieu de `env` dans `~/.claude/settings.json`)
