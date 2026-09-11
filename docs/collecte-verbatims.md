# Collecter de vrais verbatims

L'étude GEO ([Princeton / Allen Institute](https://arxiv.org/abs/2311.09735)) mesure
**+41 % de visibilité** dans les réponses d'IA pour les pages qui contiennent des
citations attribuées — le levier le plus fort des neuf testés. C'est aussi le seul
qu'on ne peut pas fabriquer : un faux avis client est une pratique commerciale
trompeuse (directive Omnibus 2019/2161) et une violation directe des règles
anti-spam de Google sur les données structurées.

Bonne nouvelle : il en faut **six**, pas soixante. Et tu as déjà les gens sous la main.

---

## 1. Qui solliciter, dans cet ordre

| Priorité | Qui | Pourquoi eux |
|---|---|---|
| 1 | Les **3 à 5 derniers clients** ayant réservé via l'app | Souvenir frais, gratitude encore chaude |
| 2 | Les **DJs du roster** (les 8 du site) | Ils ont un intérêt direct à ce que la plateforme marche |
| 3 | **DJ Fab** en tant que cofondateur | Une citation sur le *pourquoi* de la cooptation |

Vise **4 clients + 2 DJs**. Trois colonnes sur le site, deux rangées.

---

## 2. Le message à envoyer

WhatsApp marche mieux que l'e-mail au Cameroun. Envoie-le **le lendemain de la
prestation**, jamais une semaine après.

> Bonjour {Prénom} 👋
>
> C'était comment, la soirée de samedi avec {DJ} ?
>
> On refait le site AlloDJ et j'aimerais y mettre quelques retours de vrais
> clients — pas des trucs inventés. Est-ce que tu accepterais qu'on publie une
> phrase de toi, avec ton prénom et l'initiale de ton nom (ex. « Sandrine M. »),
> la ville et le type d'événement ?
>
> Trois questions, réponds comme ça te vient, même en vocal :
>
> 1. Avant AlloDJ, comment tu trouvais un DJ ? Qu'est-ce qui était pénible ?
> 2. Qu'est-ce qui t'a surpris en utilisant l'app ?
> 3. Tu le dirais comment à un ami qui cherche un DJ ?
>
> Pas de souci si tu préfères pas, dis-le-moi simplement.

**Pourquoi ces trois questions :** la 1 fait ressortir le problème (le
bouche-à-oreille), la 2 fait ressortir la différence, la 3 sort la phrase la plus
naturelle — c'est presque toujours celle-là qu'on garde.

---

## 3. Ce qui fait un verbatim utilisable

| ✅ Garde | ❌ Jette |
|---|---|
| « J'avais appelé quatre DJs, deux m'ont jamais rappelé. Là j'ai eu un nom en dix minutes. » | « Super service, je recommande ! » |
| « Le prix était affiché, j'ai pas eu à négocier devant ma belle-famille. » | « AlloDJ est la meilleure plateforme du Cameroun. » |
| « Il connaissait le déroulé de la dot, il a pas fallu lui expliquer. » | Toute phrase que tu as écrite toi-même |

Règles :
- **Un fait concret** (un chiffre, un moment, un détail) vaut mieux qu'un adjectif.
- **Ne réécris pas.** Corrige l'orthographe, coupe si c'est trop long, mais garde
  les mots de la personne. Une phrase un peu bancale est plus crédible qu'un slogan.
- **Pas de superlatif** que la personne n'a pas dit.

---

## 4. Le consentement

Une capture d'écran du « oui » suffit. Garde-la — c'est la trace qui te protège si
quelqu'un conteste plus tard.

Formulation qui vaut accord :

> « Oui tu peux publier », « pas de souci », « vas-y »

Note la provenance dans le champ `source` du fichier JSON (ex. `WhatsApp 2026-09-12`).
Ce champ n'est **pas** publié, il sert de trace.

---

## 4 bis. Raccourci : les avis déjà dans l'app

L'application a un vrai système d'avis (`reviews` dans Firestore) : note sur 5,
commentaire libre, réponse du DJ, modération, un avis par réservation. La
collection est en **lecture publique**, donc récupérable sans clé privée :

```bash
python tools/import-avis.py
```

Le script écarte automatiquement les comptes de test, les avis masqués, les notes
sous 4 et les commentaires de moins de 40 caractères, puis écrit les candidats
dans `data/avis-candidats.json` avec `consentement: false`.

**État au 2026-09-09 : 0 candidat.** Les 2 avis en base viennent des comptes
`paparazzi` et `muketee2005` — des tests.

Un avis laissé dans l'app **n'est pas** un accord pour figurer sur la page
d'accueil avec un nom, en argument commercial. Demande-le quand même, avec le
message du §2 : « Tu as laissé un avis sur {DJ} dans l'app, est-ce que je peux
le reprendre sur le site ? »

## 5. Les mettre en ligne

Ouvre `data/verbatims.json` et remplis le tableau `verbatims` :

```json
{
  "verbatims": [
    {
      "citation": "J'avais appelé quatre DJs, deux m'ont jamais rappelé. Là j'ai eu un nom en dix minutes.",
      "auteur": "Sandrine M.",
      "role": "Cliente",
      "ville": "Douala",
      "evenement": "Mariage",
      "date": "2026-09-12",
      "consentement": true,
      "source": "WhatsApp 2026-09-13"
    }
  ]
}
```

Puis :

```bash
python tools/build-verbatims.py && python tools/build-en.py && python tools/build-villes.py
```

Le script **refuse** de publier une entrée dont `consentement` n'est pas `true`,
dont la citation ou l'auteur est vide, ou dont la `source` manque. Tant que la
liste est vide, la section n'apparaît pas du tout — c'est l'état correct
aujourd'hui.

Chaque verbatim publié génère aussi un `Review` schema.org rattaché au service,
c'est-à-dire exactement ce que les moteurs de réponse citent.

---

## 6. Ce qu'il ne faut pas faire

- **Pas d'`aggregateRating`** tant que tu n'as pas un vrai système d'avis avec un
  vrai décompte. Une note moyenne inventée est le premier truc que Google
  sanctionne, et le rich snippet saute pour tout le site.
- **Pas de photo de la personne** sans accord séparé — le consentement pour la
  citation ne couvre pas l'image.
- **Pas de traduction** des verbatims en anglais sans le dire. Si tu les traduis
  pour `/en/`, garde le français en `lang="fr"` dans le balisage.
