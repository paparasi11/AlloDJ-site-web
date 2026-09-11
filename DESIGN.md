# AlloDJ — système visuel et mouvement

Ce que `index.html` applique. À respecter pour toute nouvelle section, sinon la
cohérence se perd — c'est précisément le reproche que Malcom a formulé.

---

## 1. Le concept

**La page est un instrument de DJ, pas un site SaaS.**

Le vocabulaire vient du métier : table de mixage, faces d'un vinyle, pistes, playhead,
BPM, crates (bacs à disques), tracklist, fiche technique, liner notes. C'est ce qui rend
le site atypique sans tomber dans le décoratif : chaque device visuel *dit* quelque chose
du produit.

Traductions retenues :

| Élément de page | Vocabulaire console |
|---|---|
| Sections | **Pistes** numérotées `A1 → B5`, réparties en **Face A / Face B** |
| En-tête de section | **Ardoise** (`FACE A · A2 — La méthode — 3 temps`) |
| Barre de progression | **Playhead** sur un rail canal + compteur **BPM** |
| Types d'événement | **Crates** que l'on feuillette |
| Compiles | **Tracklist** numérotée avec durées |
| Comparatif | **Fiche technique** |
| Footer | **Liner notes** |

---

## 2. Couleurs

Déclarées en tokens CSS dans `:root`. **Ne jamais écrire un hex en dur dans un composant.**

```
--void   #0A0A0B   fond général (plus profond que l'ancien #131314)
--panel  #141416   surfaces
--panel-2 #1C1C1F  surfaces élevées
--line   #26262B   filets
--line-2 #3A3A42   filets marqués / bordures d'éléments interactifs

--blue   #2E5BFF   marque — CTA principaux, index de navigation
--rose   #E10181   marque — accents, dégradés d'ambiance
--peak   #C6F24E   « signal live » — playhead, BPM, numéros de piste, survol

--ink    #F2F2F3   texte principal
--ink-2  #A8A8B0   texte secondaire
--ink-3  #82828C   micro-labels (jamais sous 11px)
```

Le **vert acide `--peak`** est l'ingrédient nouveau : c'est la couleur d'un pic de
VU-mètre. Il ne sert **qu'à ce qui est vivant ou actif** (playhead, BPM, état de survol,
numéro de piste, seuil de cooptation). Ne pas l'utiliser comme couleur décorative.

Contrastes vérifiés sur `--void` : `--ink` ≈ 18:1, `--ink-2` ≈ 9:1, `--ink-3` ≈ 5:1.

---

## 3. Typographie

| Rôle | Police | Usage |
|---|---|---|
| Display | **Sora** 700/800 | Titres, très serré (`-.03em` à `-.045em`), souvent en capitales |
| Corps | **Hanken Grotesk** 400/600 | Paragraphes, `lede` à 16,5px |
| Console | **JetBrains Mono** 400/700 | Ardoises, labels, BPM, durées, numéros, boutons |

Règle : **tout ce qui est une donnée ou une étiquette passe en mono, en capitales, avec
`letter-spacing` entre `.06em` et `.12em`.** C'est ce contraste mono/display qui donne
l'identité — ne pas y renoncer par confort.

Chiffres alignés en colonne → `font-variant-numeric: tabular-nums`.

---

## 4. Mouvement — une seule grammaire

**Une courbe, trois durées, un pas de décalage.** Tout le reste en découle.

```
--e       cubic-bezier(.22,1,.36,1)   ← la seule courbe utilisée
--t-fast  180ms   micro-interactions (survol, focus, pression)
--t-med   420ms   changements d'état, cartes
--t-slow  700ms   révélations au scroll
stagger   70ms    pas de décalage entre éléments d'une même grille
```

Ce qui bouge, et pourquoi :

| Animation | Rôle |
|---|---|
| Logo : 7 rayons en apparition décalée au chargement, pulsation au survol | Signature de marque |
| Titre héro : lignes qui remontent l'une après l'autre | Séquence d'ouverture |
| Colonnes de DJs : défilement vertical infini, sens opposés, **pause au survol** | Vie, densité du roster |
| Playhead + BPM suivant le scroll | Repère de position, métaphore console |
| Ardoises : filet qui se trace de gauche à droite | Entrée de section |
| Révélations : fondu + montée, cascade sur les grilles | Rythme de lecture |
| Compteurs (10 %, 48 h, 3) | Attire l'œil sur les chiffres qui comptent |
| Cartes au survol : lift + bordure `--peak` + zoom image | Réponse tactile unifiée |
| Boutons : pression physique (`translateY` + ombre qui s'écrase) | Sensation de pad de console |

**Trois interdits :**
1. Aucune animation purement décorative — chacune doit exprimer une cause/effet.
2. Aucun élément parqué en `opacity:0` en attente d'un observateur. Les révélations sont
   conditionnées à la classe `.js` sur `<html>` : **sans JS, tout est visible**. Un filet
   de sécurité révèle tout au bout de 2,8 s quoi qu'il arrive.
3. `prefers-reduced-motion` coupe **tout** (`transition` et `animation`), et remet les
   éléments dans leur état final.

---

## 5. Formes et espacements

```
--r-s  4px    boutons, petits blocs
--r-m  14px   cartes, panneaux
--r-l  22px   cartes photo du héro
```

Rythme vertical : `section { padding: 104px 0 }`, `wrap { max-width: 1180px }`.
Ruptures : `1080px` (le rail disparaît, les grilles passent en 1 colonne) et `720px`.

Zones tactiles : **44px minimum** partout (boutons, flèches du carrousel, liens de contact).

---

## 6. Ce qu'on ne fait pas

- Pas de fond blanc : Cueup a un corps de page blanc, **on garde le sombre** — cohérence
  avec l'app Flutter, qui est sombre par défaut.
- Pas d'emoji en guise d'icône : SVG inline uniquement (logo, épingles de localisation,
  Apple, Google Play).
- Pas de bandeau de texte défilant (essayé, retiré sur demande).
- Pas de mockup de téléphone en héro (essayé en CSS puis en vidéo 3D, retiré sur demande).
- Pas d'étoiles de notation en héro (proposé, refusé).
