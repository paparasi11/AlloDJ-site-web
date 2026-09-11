# Prompts — section « Un DJ pour chaque événement »

> **État au 2026-09-09.** 6 des 8 visuels sont posés (images Gemini de
> `Downloads.rar`) : entreprise, anniversaire, baptême, remise de diplôme,
> retour au pays, concert & club. **Il reste `mariage` et `tradi`** — c'est
> l'objet de cette page. Les prompts sont calés sur le style des 6 déjà en
> place (fond sombre, foule, lumière ambre, mélange de tenues).

8 visuels du carrousel A3. AlloDJ est une **application camerounaise** : les
images le sont aussi. Des Noirs, oui — mais habillés comme dans la vraie vie :
costumes, robes de soirée, jeans, vestes, pagne, boubou, quelques tenues
traditionnelles. **Un mélange**, pas un défilé folklorique.

- **Ratio** : 5:4 ou 4:3 paysage (le conteneur `.crate .ph` est en 5/4).
  En pratique **1280 × 1024** ou **1200 × 900**.
- **Nom de fichier** attendu par le site : `evt-<clé>.jpg`, dans `assets/photos/`.
- Remplace les 8 fichiers existants, garde les mêmes noms, le HTML ne bouge pas.

---

## Style commun — à coller à la fin de CHAQUE prompt

> Photorealistic editorial photograph, Cameroon, Central Africa. Everyone in
> frame is Black Cameroonian — deep brown to dark skin tones rendered richly and
> accurately, no lightening. The guests dress in a realistic MIX, not a costume
> parade: some in tailored suits and blazers, some in cocktail and evening
> dresses, some in jeans and sneakers, some in ankara / wax-print outfits, some
> in boubou or agbada, a few in traditional cloth — a modern cosmopolitan
> African crowd. Natural, braided and locs hair, durags, gold jewellery. Deep
> near-black background, warm amber and coral practical lighting, shallow depth
> of field, 35mm lens, subtle film grain, cinematic colour grade. Candid
> documentary feel, not a stock photo, not a Western party. No text, no logos,
> no watermarks. Anatomically correct hands and faces.

Sur Midjourney : ajoute `--ar 5:4 --style raw`.
Négatifs (SD / Ideogram) : `white people, caucasian, lightened skin, everyone in
matching traditional dress, western wedding, stock photo, text, watermark,
distorted hands`.

---

## 1 — `evt-mariage.jpg` · Mariage (01 — Cérémonie)

> An evening Cameroonian wedding reception. The bride in a white gown, the groom
> in a sharp suit, dancing inside a circle of guests dressed every way — cocktail
> dresses, tailored suits, ankara ensembles, a few in traditional cloth — who
> clap and ululate. String lights overhead, a DJ booth glowing in the
> background, a spray of banknotes mid-air in the njangi money-dance.

## 2 — `evt-tradi.jpg` · Traditionnel & dot (02 — Cérémonie)

> A Cameroonian dowry ceremony (la dot) in late-afternoon golden light. The
> families lean traditional — ndop and toghu cloth, kaba ngondo, boubou — but
> younger relatives mix in modern dresses and blazers. Elders seated under a
> decorated canopy, women dancing bikutsi mid-step, calabashes and kola nuts on
> a mat.

## 3 — `evt-entreprise.jpg` · Entreprise (03 — Corporate)

> A crowded end-of-year company gala in a Douala hotel ballroom. Cameroonian
> colleagues in suits, blazers, evening dresses and a few ankara-accent outfits,
> standing and applauding toward a brightly lit stage. Round tables full, a DJ
> setup with laptop and controller discreetly at the side.

## 4 — `evt-anniversaire.jpg` · Anniversaire (04 — Privé)

> A night birthday party on a Yaoundé terrace. A cake with sparkler candles on
> the table, young Cameroonian friends in a mix of streetwear, print dresses and
> smart-casual, leaning in and laughing, balloons and confetti in the air,
> bottles of Fanta and beer between them.

## 5 — `evt-bapteme.jpg` · Baptême (05 — Famille)

> A Cameroonian christening reception in a decorated compound courtyard. A long
> table with white and gold decor; guests in a range of dress — Sunday-best
> dresses and suits, some aunties in bright kaba, men in shirts or boubou —
> standing and talking. Plates of jollof and grilled fish, plastic chairs, soft
> late-afternoon light, a modest sound system in the corner.

## 6 — `evt-diplome.jpg` · Remise de diplôme (06 — Privé)

> A graduation celebration on a Cameroonian university campus, seen from behind
> the crowd. Black graduates in gowns and mortarboards throwing their caps into
> the evening sky; families cheering in a mix of Sunday dresses, suits and wax
> print, low campus buildings and palm trees behind.

## 7 — `evt-prive.jpg` · Retour au pays (07 — Privé)

> A crowded rooftop house party at night in Douala — the diaspora home for the
> holidays. A dozen Cameroonian adults dancing coupé-décalé shoulder to shoulder
> in jeans, dresses, jackets and a few print outfits, under string lights. A
> table of grilled soya, plantain and drinks to one side, corrugated-roof
> neighbourhood and city lights behind.

## 8 — `evt-club.jpg` · Concert & club (08 — Scène)

> A packed Douala nightclub. A Cameroonian DJ silhouetted behind the decks with
> one hand raised, a dense Black crowd in club wear — dresses, shirts, chains,
> durags — with phones in the air. Haze and coloured beams cutting through the
> room, a stack of line-array speakers, bottles with sparklers carried overhead.

---

## Ce qui rate le plus souvent

- **Tout le monde en tenue traditionnelle assortie** → répéter « a MIX of dress,
  suits and dresses and jeans, only a few in traditional cloth » dans le prompt,
  pas seulement dans le style.
- **Gros plans de visages** → déformés. Cadrer large, de profil ou de dos.
- **« Wide shot » seul** → salles vides. Pour une foule : « dense crowd filling
  the frame », « seen from behind the crowd ».
- **Peau éclaircie / personnes non africaines** → répéter « Black Cameroonian,
  dark skin » dans chaque prompt + les négatifs ci-dessus.
- Garder le **fond très sombre** partout : c'est ce qui tient la série ensemble.

Après avoir remplacé les fichiers :
`python -m http.server 8899 --bind 127.0.0.1` puis `http://127.0.0.1:8899/#a3`
