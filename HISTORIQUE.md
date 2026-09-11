# AlloDJ — historique des décisions

Pourquoi le site est ce qu'il est. **Lire avant de proposer quoi que ce soit** : la
plupart des idées « évidentes » ont déjà été essayées et tranchées.

---

## 1. Trajectoire des directions visuelles

| Étape | Référence donnée | Résultat |
|---|---|---|
| 1 | `void.sbs` | Site crypto/messagerie. Sombre, néon, mockup téléphone. Servi de point de départ, **dépassé** |
| 2 | `cueup.io` | **Le bon repère** — vrai concurrent, même métier. Structure et mécaniques de conversion reprises |
| 3 | Captures « MusicaNow » | Demande de sections photographiques → photos réelles et images d'ambiance |
| 4 | « design révolutionnaire et atypique » | Direction **« La console »** créée dans `console.html` |
| 5 | « fusionner les deux » | **État actuel** : structure Cueup + langage console, dans `index.html` |

**`cueup.io` opère déjà au Cameroun** — son pied de page liste Douala, Yaoundé, Bamenda,
Garoua, Maroua. Ce n'est pas qu'une inspiration : c'est un concurrent direct. Information
donnée à Malcom, jamais commentée par lui.

---

## 2. Essayé puis retiré — ne pas y revenir sans demande

| Élément | Sort |
|---|---|
| Mockup de téléphone en CSS (perspective, parallaxe souris) | Jugé « mauvais » → remplacé |
| **Vidéo 3D du téléphone** (générée par IA à partir de mes prompts) | Intégrée, puis **retirée** (« enlève ça »). Fichier conservé : `assets/phone-hero.mp4` |
| **Bandeau de texte défilant** (ticker villes/promesses) | Ajouté, puis **retiré** au même moment |
| **Étoiles de notation** façon Cueup en héro | Proposé, **refusé** (« pas besoin des étoiles ») |
| Widget de recherche **blanc** comme celui de Cueup | Essayé, **refusé** : « mets une cohérence avec le thème sombre du site » |
| Section `/tarifs` | **Supprimée** sur demande, remplacée par la section Compiles |
| Pages `/a-propos`, `/devenir-dj`, `/contact` séparées | **Fusionnées** dans la page unique |

---

## 3. Corrections de fond apportées par Malcom

- **Les DJs ne postulent pas.** Le site affichait « Postuler par e-mail » → faux.
  L'entrée se fait **sur recommandation d'au moins 3 DJs déjà actifs**. Reformulé.
- **« Écouter la suite dans l'app »** doit pointer **directement** sur
  `https://appli.allodeejay.com/#/home`, pas sur une ancre interne.
- **Le logo doit être le vrai**, en version à meilleur contraste → `Noir Alpha`.
- **Animation du héro** : ce n'est pas un flottement, c'est un **défilement vertical
  continu** avec des DJs qui changent. Corrigé.

---

## 4. Problèmes réels trouvés et réglés

- **Logo d'origine mal détouré** : halo gris rectangulaire visible sur fond sombre.
  Nettoyé par flood-fill depuis les bords (`assets/logo.png`).
- **SVG du logo** : contenait une plaque de fond `<rect>` `#1d1d1b`. Retirée avant inline.
- **`privacy.html` dans le dépôt Flutter** : doublon obsolète de `confidentialite.html`,
  jamais référencé, mentionne des « paiements simulés » — faux depuis le flux acompte/solde
  du 2026-07-24. **Suppression proposée, jamais confirmée par Malcom.**
- **Révélations au scroll** : première version parquait le contenu en `opacity:0` en
  attendant l'observateur → page blanche si le JS ne tournait pas. Corrigé (classe `.js`
  + filet de sécurité).

---

## 5. Façon de travailler de Malcom

Observations utiles pour la suite :

- **Messages courts, souvent en plusieurs morceaux**, parfois coupés en cours de phrase.
  Attendre la suite plutôt que sur-interpréter un fragment.
- **Itère vite et corrige vite.** Il vaut mieux produire puis se faire rediriger que
  poser trois questions avant d'agir. Exception : les vraies bifurcations (choix de
  direction visuelle, structure du site) méritent une question.
- **Vérifie visuellement dans son navigateur**, pas dans l'aperçu intégré. Quand il dit
  « c'est toujours pareil », penser **cache Chrome** avant de douter du code.
- **Fournit de vrais assets** (photos de DJs, pochettes, logo officiel, vidéo 3D générée
  par lui à partir de prompts que je lui donne). Quand un asset manque, lui donner un
  prompt prêt à l'emploi fonctionne bien — il revient avec le fichier.
- N'a jamais répondu sur : le comparatif Cueup au Cameroun, la suppression de
  `privacy.html`, le branchement de `mcpollinations`. Ne pas insister, mais ne pas
  supposer que c'est validé.

---

## 6. Sources de contenu

| Besoin | Où |
|---|---|
| Textes légaux (CGU, confidentialité, suppression de compte) | Dépôt Flutter : `app/web/*.html`, `core/data/legal_content.dart` |
| Positionnement, vision, problème/solution | `allodj-business/BUSINESS-PLAN.md` (13 sections) |
| Fonctionnalités détaillées | Dépôt Flutter : `allodjv1.md` |
| Charte d'origine du site | `allodj-website/DESIGN.md` (projet Next.js abandonné) |

**Ne pas republier sur le site public** : projections financières (§11), analyse de
risques (§12), dimensionnement de marché (§5) du business plan. Ça reste dans le pitch deck.
