#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les quatre pages légales à partir de la coquille de index.html.

    python tools/build-legal.py

Sortie : cgu.html · confidentialite.html · mentions-legales.html ·
         suppression-de-compte.html

Le contenu vient du dépôt Flutter (`lib/core/data/legal_content.dart` et
`web/confidentialite.html`), pas d'un modèle générique.

⚠️ Le fichier source Flutter porte lui-même la mention « brouillon […] à faire
relire par un juriste avant mise en production ». Ces pages reprennent cet
avertissement tant qu'une relecture n'a pas eu lieu. Les champs que je ne peux
pas connaître (RCCM, hébergeur, directeur de publication) sont marqués
À COMPLÉTER et le script REFUSE de considérer les pages comme finies tant
qu'ils sont là — voir le récapitulatif en fin d'exécution.
"""

import os
import re
import sys
import unicodedata
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retour_accueil  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RACINE, "index.html")
BASE = "https://allodeejay.com/"
APP = "https://appli.allodeejay.com/#/home"
MAJ = "8 septembre 2026"
TODO = '<mark class="todo">À COMPLÉTER</mark>'

AVERTISSEMENT = (
    '<p class="avis"><b>Document en cours de validation juridique.</b> '
    "Ce texte a été rédigé en interne pour décrire le fonctionnement réel de la "
    "plateforme. Il n'a pas encore été relu par un juriste. En cas de doute sur "
    'un point précis, écrivez à <a href="mailto:contact@allodeejay.com">'
    "contact@allodeejay.com</a>.</p>"
)

SIMULE = (
    '<p class="avis"><b>Paiement en phase de test.</b> Dans la version actuelle '
    "de l'application, le paiement est <b>simulé à des fins de démonstration</b> : "
    "aucune transaction bancaire réelle n'est effectuée et aucun montant n'est "
    "débité. Les montants, statuts et notifications reproduisent fidèlement ce que "
    "sera un paiement réel. Cette page sera mise à jour dès l'ouverture des "
    "paiements effectifs.</p>"
)

# ── Contenu ────────────────────────────────────────────────────────────────
PAGES = {
    "cgu.html": {
        "titre": "Conditions générales d'utilisation | AlloDJ",
        "desc": "Conditions générales d'utilisation d'AlloDJ : réservation, acompte de 10 %, solde, politique d'annulation sous 48 h, rôle de la plateforme.",
        "h1": "Conditions générales d'utilisation",
        "intro": "Ces conditions encadrent l'utilisation d'AlloDJ, plateforme de mise en relation entre des clients organisant un événement et des DJs, avec possibilité d'ajouter sonorisation et éclairage.",
        "avis": [AVERTISSEMENT, SIMULE],
        "sections": [
            ("1. Présentation du service", [
                "AlloDJ est une plateforme de mise en relation entre des clients organisant un événement et des DJs professionnels, avec possibilité d'ajouter des prestations de sonorisation et d'éclairage.",
                "AlloDJ <b>n'est pas l'employeur</b> des DJs référencés : la plateforme met en relation l'offre et la demande, et facilite la réservation et le paiement.",
            ]),
            ("2. Compte et éligibilité", [
                "L'utilisation du service nécessite un compte, ou une session visiteur temporaire. Les informations fournies doivent être exactes.",
                "Le service n'est pas destiné aux personnes de moins de 13 ans.",
            ]),
            ("3. Déroulement d'une réservation", [
                "Le client renseigne les informations de son événement — date, lieu, budget, type d'événement. Il reçoit une recommandation de DJ, ou en choisit un librement.",
                "Un devis est ensuite construit automatiquement à partir du tarif réel du DJ et des options choisies.",
                "<b>La réservation n'est confirmée qu'après paiement de l'acompte</b>, soit 10 % du montant total. Tant que l'acompte n'est pas réglé, aucune date n'est bloquée.",
            ]),
            ("4. Prix et paiement", [
                "Le montant total de la prestation figure sur le devis. Il se décompose en :",
                "<ul><li>un <b>acompte de 10 %</b> du montant total, payable à la confirmation de la réservation ;</li>"
                "<li>un <b>solde de 90 %</b>, payable au plus tard <b>3 jours avant</b> la date de l'événement.</li></ul>",
                "Le paiement s'effectue au sein de l'application.",
                "Si le solde n'est pas réglé avant l'échéance, la prestation pourra être suspendue ou annulée.",
            ]),
            ("5. Annulation et remboursement", [
                "Vous disposez d'un délai de <b>48 heures</b> après la confirmation de votre réservation pour l'annuler et obtenir le <b>remboursement intégral de votre acompte</b>.",
                "Passé ce délai de 48 heures, l'acompte de 10 % devient définitivement non remboursable, quelle que soit la raison de l'annulation.",
            ]),
            ("6. Obligations du DJ", [
                "Le DJ s'engage à être présent sur le lieu de la prestation à l'heure convenue, avec le matériel inclus dans son offre — packs Sonorisation et Éclairage éventuellement sélectionnés compris — en état de fonctionnement.",
            ]),
            ("7. Obligations du client", [
                "Le client s'engage à garantir l'accès au lieu de l'événement, une alimentation électrique suffisante, et à régler le solde dans les délais indiqués.",
            ]),
            ("8. Entrée des DJs sur la plateforme", [
                "Les DJs ne postulent pas librement. Un nouveau profil rejoint le roster <b>sur recommandation d'au moins 3 DJs déjà actifs</b>, qui se portent garants de son niveau et de son sérieux.",
                "Chaque prestation est notée après réalisation ; ces notes alimentent les recommandations suivantes.",
            ]),
            ("9. Responsabilité", [
                "AlloDJ agit en tant qu'intermédiaire de mise en relation entre le client et le DJ. Sa responsabilité ne saurait être engagée au-delà de ce rôle d'intermédiaire, sauf faute qui lui serait directement imputable.",
            ]),
            ("10. Force majeure", [
                "Aucune des parties ne pourra être tenue responsable d'une inexécution due à un cas de force majeure : catastrophe naturelle, décision administrative, coupure d'électricité prolongée, entre autres.",
            ]),
            ("11. Litiges", [
                "Tout désaccord relatif à une réservation peut faire l'objet d'une demande auprès de l'équipe AlloDJ, qui statuera au cas par cas.",
                "Les présentes conditions sont soumises au <b>droit OHADA</b> et, à titre supplétif, au <b>droit camerounais</b>. À défaut de résolution amiable, les tribunaux compétents sont ceux de <b>Yaoundé</b>, siège de la société.",
            ]),
            ("12. Modification des conditions", [
                "Ces conditions peuvent évoluer. <b>La version en vigueur au moment de la réservation s'applique.</b> La date de dernière mise à jour figure en haut de cette page.",
            ]),
        ],
    },

    "confidentialite.html": {
        "titre": "Politique de confidentialité | AlloDJ",
        "desc": "Quelles données AlloDJ collecte, pourquoi, avec qui elles sont partagées, combien de temps elles sont conservées et comment exercer vos droits.",
        "h1": "Politique de confidentialité",
        "intro": "AlloDJ met en relation des clients avec des DJs et du matériel de sonorisation au Cameroun. Cette page explique quelles données sont collectées, pourquoi, et quels sont vos droits.",
        "avis": [],
        "sections": [
            ("1. Données collectées", [
                "<ul>"
                "<li><b>Compte</b> — nom, adresse e-mail, numéro de téléphone.</li>"
                "<li><b>Contenu que vous fournissez</b> — photos, publications, commentaires, messages, avis.</li>"
                "<li><b>Localisation</b> — ville ou zone et lieu de l'événement, pour afficher les DJs proches. Uniquement avec votre autorisation.</li>"
                "<li><b>Données techniques d'usage</b> — identifiant de compte, journaux d'erreurs.</li>"
                "</ul>",
            ]),
            ("2. Finalités", [
                "<ul>"
                "<li>Créer et gérer votre compte.</li>"
                "<li>Traiter les demandes de devis, les réservations et les locations.</li>"
                "<li>Permettre la messagerie, les avis et le fil d'actualité.</li>"
                "<li>Vous envoyer les notifications liées à vos réservations.</li>"
                "<li>Assurer la sécurité et la modération du service.</li>"
                "</ul>",
            ]),
            ("3. Cookies et mesure d'audience", [
                "Le site ne dépose <b>aucun cookie de mesure ni de publicité tant que vous ne l'avez pas accepté</b>. Aucun script Google n'est même chargé avant votre choix : la bannière s'affiche à la première visite, et refuser prend un seul clic, exactement comme accepter.",
                "<ul>"
                "<li><b>Nécessaires</b> — la langue que vous choisissez est mémorisée dans votre navigateur. Aucun identifiant, aucune transmission à un tiers. Exemptés de consentement.</li>"
                "<li><b>Mesure d'audience</b> — Google Analytics 4, pour comprendre quelles pages sont consultées. Déposés uniquement après acceptation. Adresse IP anonymisée.</li>"
                "<li><b>Publicité</b> — Google Ads, pour mesurer l'efficacité de nos campagnes. Déposés uniquement après acceptation.</li>"
                "</ul>",
                "Nous utilisons le <b>Consent Mode v2</b> de Google : tant que vous n'avez pas accepté, les quatre signaux de consentement publicitaire et statistique sont transmis comme refusés.",
                'Vous pouvez revenir sur votre choix à tout moment via le lien <b>« Gérer mes cookies »</b> en bas de chaque page. Votre décision est conservée <b>13 mois</b>, puis la question vous est reposée.',
            ]),
            ("4. Partage des données", [
                "<b>Nous ne vendons pas vos données.</b> Elles sont traitées via nos sous-traitants techniques, principalement <b>Google Firebase</b> — authentification, base de données, notifications, hébergement — qui agissent pour notre compte.",
                "Aucun suivi publicitaire inter-applications n'est effectué.",
                "<b>Transfert hors Union européenne</b> — Google Firebase et, le cas échéant, Google Analytics et Google Ads hébergent des données aux <b>États-Unis</b>. Ces transferts s'appuient sur les clauses contractuelles types de la Commission européenne, intégrées aux conditions de Google.",
            ]),
            ("5. Conservation", [
                "Vos données sont conservées tant que votre compte est actif. À la suppression du compte, elles sont effacées ou anonymisées, sauf obligation légale de conservation.",
                'Voir la page <a href="suppression-de-compte.html">Suppression de compte</a>.',
            ]),
            ("6. Vos droits", [
                "Vous pouvez accéder à vos données, les corriger, ou demander la suppression de votre compte et de vos données en nous contactant.",
                "Depuis l'application, vous pouvez modifier votre profil, signaler un contenu et bloquer un utilisateur.",
            ]),
            ("7. Modération et contenu utilisateur", [
                "Les publications, commentaires et messages sont générés par les utilisateurs. Tout contenu inapproprié peut être <b>signalé</b> depuis l'application, et tout utilisateur peut être <b>bloqué</b>.",
                "Les signalements sont examinés sous 24 heures et les contenus contraires à nos conditions sont retirés.",
            ]),
            ("8. Sécurité", [
                "Les échanges sont chiffrés en transit (HTTPS) et l'accès aux données est restreint par des règles de sécurité côté serveur.",
            ]),
            ("9. Mineurs", [
                "Le service n'est pas destiné aux personnes de moins de 13 ans. Si vous constatez qu'un compte a été créé par un mineur de moins de 13 ans, signalez-le à l'adresse de contact ci-dessous.",
            ]),
            ("10. Modifications", [
                "Cette politique peut être mise à jour. La date en haut de page indique la dernière révision.",
            ]),
        ],
    },

    "support.html": {
        "titre": "Aide et support | AlloDJ",
        "desc": "Contacter le support AlloDJ : e-mail, téléphone, WhatsApp. Réponses aux problèmes courants de réservation, de paiement et de compte.",
        "h1": "Aide et support",
        "intro": "Une question sur une réservation, un paiement ou votre compte ? Cette page réunit les moyens de nous joindre et les réponses aux situations les plus fréquentes.",
        "avis": [],
        "sections": [
            ("Nous contacter", [
                "<ul>"
                '<li><b>E-mail</b> — <a href="mailto:contact@allodeejay.com">contact@allodeejay.com</a>, réponse sous 24 heures ouvrées</li>'
                '<li><b>Téléphone et WhatsApp</b> — <a href="tel:+237699806672">+237 699 80 66 72</a></li>'
                '<li><b>Facebook</b> — <a href="https://www.facebook.com/profile.php?id=100092519151625" target="_blank" rel="noopener">page AlloDJ</a></li>'
                "</ul>",
                "Pour une prestation ayant lieu dans les 48 heures, privilégiez le téléphone.",
            ]),
            ("Ce qu'il faut nous indiquer", [
                "Pour traiter une demande liée à une réservation, précisez la <b>date de l'événement</b>, la <b>ville</b> et le <b>nom du DJ</b> concerné. Sans ces trois éléments, il faut un aller-retour de plus.",
            ]),
            ("Le DJ ne répond pas", [
                "Passez par la messagerie intégrée à l'application plutôt que par un numéro personnel : les échanges y sont tracés, ce qui permet de trancher en cas de désaccord. Sans réponse sous 24 heures, écrivez-nous.",
            ]),
            ("Annuler une réservation", [
                "L'annulation est sans frais dans les <b>48 heures</b> qui suivent la réservation. Passé ce délai, l'acompte reste acquis au DJ qui a bloqué sa date.",
                'Détail dans les <a href="cgu.html">conditions générales</a>.',
            ]),
            ("Problème de paiement", [
                "Le paiement est actuellement en <b>phase de test</b> : aucune transaction bancaire réelle n'est effectuée. Si un montant apparaît anormal dans l'application, signalez-le, cela ne correspond à aucun débit.",
            ]),
            ("Mot de passe oublié", [
                "Utilisez « Mot de passe oublié » sur l'écran de connexion. Le lien de réinitialisation part sur l'adresse e-mail du compte. Vérifiez vos indésirables avant de nous écrire.",
            ]),
            ("Supprimer votre compte", [
                'Depuis <b>Profil</b>, tout en bas. Marche à suivre complète sur la page <a href="suppression-de-compte.html">Suppression de compte</a>.',
            ]),
            ("Devenir DJ sur AlloDJ", [
                "L'entrée se fait sur recommandation d'au moins 3 DJs déjà actifs. Il n'y a pas de formulaire de candidature ouvert — mais vous pouvez nous écrire pour poser vos questions.",
            ]),
            ("Signaler un contenu ou un utilisateur", [
                "Depuis l'application : bouton <b>Signaler</b> sur la publication ou le profil concerné. Les signalements sont examinés sous 24 heures.",
                'Vous pouvez aussi écrire à <a href="mailto:contact@allodeejay.com?subject=Signalement">contact@allodeejay.com</a>.',
            ]),
        ],
    },

    "mentions-legales.html": {
        "titre": "Mentions légales | AlloDJ",
        "desc": "Éditeur, directeur de publication, hébergeur et coordonnées de contact du site AlloDJ.",
        "h1": "Mentions légales",
        "intro": "Informations légales relatives à l'éditeur et à l'hébergement du site allodeejay.com et de l'application AlloDJ.",
        # L'avertissement « page incomplète » a sauté : plus aucun champ n'est
        # marqué À COMPLÉTER. Le laisser ferait douter d'une page qui est juste.
        "avis": [],
        "sections": [
            ("Éditeur du site", [
                f"<ul>"
                f"<li><b>Dénomination sociale</b> — ALLO DJ SARL</li>"
                f"<li><b>Forme juridique</b> — Société à responsabilité limitée (SARL)</li>"
                f"<li><b>Numéro Identifiant Unique (NIU)</b> — M012317865859Z</li>"
                f"<li><b>Centre des impôts</b> — CDI Yaoundé 2</li>"
                f"<li><b>Capital social</b> — 1 000 000 FCFA</li>"
                f"<li><b>Numéro RCCM</b> — CM-NSI-02-2023B13-00329</li>"
                f"<li><b>Siège social</b> — Ngousso, Yaoundé, Cameroun</li>"
                f"<li><b>Téléphone</b> — <a href=\"tel:+237699806672\">+237 699 80 66 72</a></li>"
                f"<li><b>E-mail</b> — <a href=\"mailto:contact@allodeejay.com\">contact@allodeejay.com</a></li>"
                f"</ul>",
            ]),
            ("Directeur de la publication", [
                "Njewa Ngangue Serge, cofondateur d'ALLO DJ SARL.",
            ]),
            ("Hébergement", [
                f"<ul>"
                f"<li><b>Site vitrine et nom de domaine</b> — Hostinger International Ltd, 61 Lordou Vironos Street, 6023 Larnaca, Chypre. "
                f"Numéro de TVA intracommunautaire CY10301365E. "
                f"Assistance&nbsp;: <a href=\"https://www.hostinger.fr/contact\" target=\"_blank\" rel=\"noopener\">hostinger.fr/contact</a></li>"
                f"<li><b>Application et base de données</b> — Google Firebase, Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043, États-Unis</li>"
                f"</ul>",
                "Le nom de domaine allodeejay.com est enregistré auprès de Hostinger depuis le <b>14 décembre 2022</b>.",
            ]),
            ("Droit applicable et juridiction", [
                "Le site et l'application sont régis par le <b>droit OHADA</b> et, à titre supplétif, par le <b>droit camerounais</b>.",
                "Tout litige relatif à leur utilisation relève des <b>tribunaux de Yaoundé</b>, siège de la société, après recherche d'une solution amiable auprès de <a href=\"mailto:contact@allodeejay.com\">contact@allodeejay.com</a>.",
            ]),
            ("Propriété intellectuelle", [
                "La marque AlloDJ, le logo et l'ensemble des éléments graphiques du site sont la propriété de leur éditeur. Toute reproduction sans autorisation est interdite.",
                "Les photographies de DJs publiées sur ce site représentent des personnes réelles et sont utilisées avec leur accord. Les pochettes de compiles sont des créations originales.",
            ]),
            ("Données personnelles", [
                'Le traitement des données personnelles est décrit dans la <a href="confidentialite.html">politique de confidentialité</a>.',
            ]),
            ("Signaler un contenu", [
                'Pour signaler un contenu illicite présent sur le site ou dans l\'application : <a href="mailto:contact@allodeejay.com?subject=Signalement%20de%20contenu">contact@allodeejay.com</a>.',
            ]),
        ],
    },

    "suppression-de-compte.html": {
        "titre": "Supprimer votre compte AlloDJ | AlloDJ",
        "desc": "Comment supprimer votre compte AlloDJ et vos données : depuis l'application ou par e-mail, ce qui est effacé, ce qui est conservé et sous quel délai.",
        "h1": "Supprimer votre compte",
        "intro": "Vous pouvez demander à tout moment la suppression de votre compte AlloDJ et des données associées. Cette page décrit la marche à suivre, ce qui est effacé et ce qui est conservé.",
        "avis": [],
        "sections": [
            ("Depuis l'application", [
                f'Ouvrez <a href="{APP}" target="_blank" rel="noopener">AlloDJ</a>, allez dans '
                f"<b>Profil</b> et faites défiler jusqu'en bas : le lien "
                f"<b>« Supprimer mon compte »</b> se trouve sous le bouton Déconnexion. "
                f"Confirmez, et c'est fait.",
            ]),
            ("Par e-mail", [
                'Si vous n\'avez plus accès à l\'application, écrivez à <a href="mailto:contact@allodeejay.com?subject=Suppression%20de%20compte">contact@allodeejay.com</a> depuis <b>l\'adresse e-mail associée au compte</b>, avec pour objet « Suppression de compte ».',
                "Cette vérification par l'adresse d'origine évite qu'un tiers fasse supprimer votre compte à votre place.",
            ]),
            ("Ce qui est supprimé", [
                "<ul>"
                "<li>Votre profil : nom, e-mail, numéro de téléphone, photo.</li>"
                "<li>Vos publications, commentaires et messages.</li>"
                "<li>Vos avis et vos notes.</li>"
                "<li>Vos préférences et l'historique de vos recherches.</li>"
                "</ul>",
            ]),
            ("Ce qui est conservé, et pourquoi", [
                "Certaines données liées à des réservations passées peuvent être conservées sous forme <b>anonymisée</b> — sans lien avec votre identité — lorsqu'une obligation comptable ou légale l'impose, ou pour maintenir la cohérence des historiques de prestation d'un DJ.",
                "Ces données ne permettent plus de vous identifier.",
            ]),
            ("Délai", [
                "Depuis l'application, la suppression est <b>immédiate</b> : votre profil, vos publications, vos commentaires et vos avis sont effacés, puis votre compte d'authentification est supprimé dans la foulée.",
                "Par e-mail, comptez <b>30 jours au maximum</b>. Une confirmation vous est envoyée une fois l'opération effectuée.",
            ]),
            ("Réservation en cours", [
                "Si une réservation est en cours au moment de la demande, contactez-nous d'abord : la suppression du compte n'annule pas automatiquement une prestation réservée, et n'ouvre pas droit au remboursement d'un acompte devenu non remboursable.",
                'Voir la <a href="cgu.html#annulation-et-remboursement">politique d\'annulation</a>.',
            ]),
        ],
    },
}

CSS = """
/* ══ PAGES LÉGALES ══ */
.legal{max-width:76ch;padding:38px 0 20px;}
/* le H1 hérite de .big : sans taille ni marge propres, les mots découpés
   par l'animation viennent chevaucher la ligne de mise à jour. */
.legal h1{font-size:clamp(28px,4.4vw,46px);line-height:1.14;letter-spacing:-.025em;margin:0 0 16px;text-transform:none;}
.legal .intro{font-size:17px;color:var(--ink-2);line-height:1.65;margin:0 0 10px;}
.legal h2{font-size:20px;font-weight:700;margin:44px 0 12px;letter-spacing:-.01em;}
.legal h2:first-of-type{margin-top:34px;}
.legal p{color:var(--ink-2);font-size:15px;line-height:1.7;margin:0 0 12px;}
.legal b{color:var(--ink);font-weight:600;}
.legal ul{margin:0 0 12px;padding-left:20px;color:var(--ink-2);font-size:15px;line-height:1.7;}
.legal li{margin-bottom:7px;}
.legal a{color:var(--peak);text-decoration:underline;text-underline-offset:3px;}
.legal .avis{border-left:2px solid var(--blue);background:var(--panel);padding:16px 18px;margin:0 0 18px;border-radius:0 var(--r-s) var(--r-s) 0;}
.legal .maj{font-family:var(--f-mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin:0 0 26px;}
.legal .todo{background:#4A2A00;color:#FFC46B;padding:1px 7px;border-radius:3px;font-family:var(--f-mono);font-size:11px;font-weight:700;letter-spacing:.06em;}
.legal .fin{margin-top:52px;padding-top:22px;border-top:1px solid var(--line);display:flex;gap:20px;flex-wrap:wrap;font-family:var(--f-mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;}

@media (max-width:720px){
  .legal{padding-top:26px;}
}

/* Au doigt : la ligne de mise à jour redevient lisible et les liens de bas de
   page atteignent les 44 px. Ces règles vivent ici et non dans site.css —
   legal.css est chargée après, elle gagnerait sur une spécificité égale.
   Même couple de requêtes que site.css : une largeur OU un pointeur grossier. */
@media (max-width:1000px), (pointer:coarse){
  .legal .maj{font-size:11px;}
  .legal .fin{gap:4px 20px;}
  .legal .fin a{display:inline-block;padding:13px 0;}
}
"""


def slug(titre):
    """« 5. Annulation et remboursement » -> « annulation-et-remboursement ».

    Les accents sont translittérés avant le nettoyage : sans ça, « Présentation »
    donnait « pr-sentation », une ancre laide et fragile à partager.
    """
    t = unicodedata.normalize("NFKD", titre)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"^\d+\.\s*", "", t.lower())
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def coquille():
    """Reprend l'en-tête, le rail et le pied de page de l'accueil."""
    s = open(SRC, encoding="utf-8").read()
    haut = s[: s.index("<main") if "<main" in s else s.index('<div class="shell">')]
    # le shell commence juste après la barre supérieure
    i = s.index('<div class="shell">')
    j = s.index("<!-- A1 -->") if "<!-- A1 -->" in s else s.index("<section")
    entete = s[i:j]
    k = s.index("<footer>")
    pied = s[k:]
    return haut, entete, pied


def page(fichier, d, haut, entete, pied):
    url = BASE + fichier
    h = haut

    h = re.sub(r"<title>.*?</title>", f'<title>{d["titre"]}</title>', h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="{d["desc"]}">', h)
    h = h.replace(f'<link rel="canonical" href="{BASE}">',
                  f'<link rel="canonical" href="{url}">')
    h = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', "", h)
    h = h.replace(f'<meta property="og:url" content="{BASE}">',
                  f'<meta property="og:url" content="{url}">')
    for b in ("og:title", "twitter:title"):
        h = re.sub(rf'(<meta (?:property|name)="{b}" content=")[^"]*(">)',
                   rf'\1{d["h1"]} — AlloDJ\2', h)
    for b in ("og:description", "twitter:description"):
        h = re.sub(rf'(<meta (?:property|name)="{b}" content=")[^"]*(">)',
                   rf'\1{d["desc"]}\2', h)
    # une page légale n'a pas besoin des données structurées de l'accueil
    h = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", h, flags=re.S)
    h += '<link rel="stylesheet" href="assets/legal.css">\n'

    # entête sans la bannière de langue ni le sélecteur
    e = re.sub(r'<div class="langbar".*?</div>\n\n', "", entete, flags=re.S)
    e = re.sub(r'<p class="lang".*?</p>\n\s*', "", e, flags=re.S)
    # une page légale ne contient aucune section A/B : sans ça, le logo et les
    # sept onglets pointent sur des ancres absentes et ne font rien.
    e = retour_accueil.page_sans_sections(e)

    corps = [f'<section id="doc">\n  <div class="wrap">',
             f'    <div class="slate"><span class="tk">Légal</span>'
             f'<span class="ttl">{d["h1"]}</span>'
             f'<span class="rt">Mise à jour · {MAJ}</span></div>',
             f'    <article class="legal">',
             f'      <h1>{d["h1"]}</h1>',
             f'      <p class="maj">Dernière mise à jour : {MAJ}</p>']
    for a in d["avis"]:
        corps.append("      " + a)
    corps.append(f'      <p class="intro">{d["intro"]}</p>')
    for titre, paras in d["sections"]:
        ancre = slug(titre)
        corps.append(f'      <h2 id="{ancre}">{titre}</h2>')
        for p in paras:
            corps.append("      " + (p if p.startswith("<ul") else f"<p>{p}</p>"))
    corps.append('      <div class="fin">'
                 '<a href="/">← Accueil</a>'
                 '<a href="support.html">Support</a>'
                 '<a href="cgu.html">CGU</a>'
                 '<a href="confidentialite.html">Confidentialité</a>'
                 '<a href="mentions-legales.html">Mentions légales</a>'
                 '<a href="suppression-de-compte.html">Suppression de compte</a>'
                 '</div>')
    corps.append("    </article>\n  </div>\n</section>\n")

    # le pied de page reprend la colonne « Faces » : mêmes ancres mortes.
    p, n = retour_accueil.onglets(pied)
    if n < 4:
        raise SystemExit(f"build-legal : {n} liens de pied réécrits, 4 attendus.")

    return h + e + "\n".join(corps) + p


def main():
    haut, entete, pied = coquille()
    open(os.path.join(RACINE, "assets", "legal.css"), "w", encoding="utf-8").write(CSS.strip() + "\n")

    restants = 0
    for fichier, d in PAGES.items():
        html = page(fichier, d, haut, entete, pied)
        open(os.path.join(RACINE, fichier), "w", encoding="utf-8").write(html)
        n = html.count("À COMPLÉTER")
        restants += n
        etat = f"{n} champ(s) À COMPLÉTER" if n else "complète"
        print(f"{fichier:30} {len(html)//1024:>3} Ko  ·  {etat}")

    print()
    if restants:
        print(f"/!\\ {restants} champs restent à renseigner avant mise en ligne.")
        print("    Ils apparaissent en surbrillance orange sur les pages.")


if __name__ == "__main__":
    main()
