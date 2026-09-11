#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère en/index.html à partir de index.html.

    python tools/build-en.py

La version anglaise est un DÉRIVÉ : on ne l'édite jamais à la main, on modifie
le français puis on relance ce script. Sinon les deux versions divergent et le
balisage hreflang ment.

Le script échoue bruyamment si une chaîne française attendue a disparu — c'est
voulu : mieux vaut une erreur qu'une page à moitié traduite mise en ligne.
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RACINE, "index.html")
DEST_DIR = os.path.join(RACINE, "en")
DEST = os.path.join(DEST_DIR, "index.html")

FR_URL = "https://allodeejay.com/"
EN_URL = "https://allodeejay.com/en/"

# ── Traductions du contenu visible ──────────────────────────────────────────
# La table est appliquée triée par longueur décroissante (voir main), donc
# l'ordre d'écriture ici n'a pas d'importance : une chaîne courte ne peut pas
# manger un morceau d'une chaîne longue.
TEXTES = [
    # JSON-LD — phrases entières (FAQ, noms de Service, descriptions).
    # Le JSON-LD paraphrase le contenu visible avec ses propres phrases (pas
    # de &nbsp;, pas de tournures "vous/votre" dans les réponses) : les
    # fragments ci-dessous ne les recouvrent qu'en partie, d'où du franglais
    # si on ne traduit pas la phrase JSON entière. Chaque entrée est
    # enveloppée dans sa clé JSON ("name": / "description": / "text": ) pour
    # ne jamais matcher le texte visible, seulement le JSON-LD.
    ('"name": "Booking DJ Cameroun — Réserver un DJ à Douala et Yaoundé"',
     '"name": "DJ Booking in Cameroon — Book a DJ in Douala and Yaoundé"'),
    ('"description": "Trouver et réserver un DJ à Douala, Yaoundé et partout au Cameroun : AlloDJ désigne le DJ adapté à la date, au lieu et au budget de l\'événement, puis verrouille la réservation avec un acompte de 10 %. Location de sonorisation incluse au catalogue."',
     '"description": "Find and book a DJ in Douala, Yaoundé and across Cameroon: AlloDJ picks the DJ that fits the event\'s date, venue and budget, then locks the booking in with a 10% deposit. Sound-system rental included in the catalogue."'),
    ('"description": "Application de booking de DJ et de location de sonorisation à Douala et Yaoundé, au Cameroun. Permet aussi d\'écouter la musique des DJs de la plateforme avant de réserver."',
     '"description": "DJ booking and sound-system rental app for Douala and Yaoundé, Cameroon. Also lets you listen to the platform\'s DJs\' music before booking."'),

    ('"name": "DJ pour mariage"', '"name": "Wedding DJ"'),
    ('"name": "DJ pour cérémonie traditionnelle et dot"', '"name": "Traditional ceremony & dowry DJ"'),
    ('"name": "DJ pour soirée d\'entreprise"', '"name": "Company party DJ"'),
    ('"name": "DJ pour anniversaire"', '"name": "Birthday DJ"'),
    ('"name": "DJ pour baptême"', '"name": "Christening DJ"'),
    ('"name": "DJ pour remise de diplôme"', '"name": "Graduation DJ"'),
    ('"name": "DJ pour fête privée"', '"name": "Private party DJ"'),
    ('"name": "DJ pour concert et club"', '"name": "Concert & club DJ"'),
    ('"name": "Location de sonorisation"', '"name": "Sound-system rental"'),

    ('"name": "Comment réserver un DJ à Douala ?"', '"name": "How do I book a DJ in Douala?"'),
    ('"text": "Indiquez la date, le lieu et votre budget dans l\'application AlloDJ. La plateforme désigne un DJ disponible à Douala pour cette date, adapté au type d\'événement. La réservation est confirmée par un acompte de 10 %."',
     '"text": "Enter the date, the venue and your budget in the AlloDJ app. The platform picks a DJ available in Douala for that date, suited to the type of event. The booking is confirmed with a 10% deposit."'),

    ('"name": "Comment trouver un DJ à Yaoundé ?"', '"name": "How do I find a DJ in Yaoundé?"'),
    ('"text": "Le fonctionnement est le même qu\'à Douala : le booking se fait depuis l\'application, et le DJ proposé est choisi parmi ceux qui couvrent Yaoundé. Pas de mise en concurrence, pas de devis à comparer."',
     '"text": "It works exactly as in Douala: booking happens in the app, and the DJ offered is chosen among those covering Yaoundé. No bidding war, no quotes to compare."'),

    ('"name": "Combien coûte le booking d\'un DJ au Cameroun ?"', '"name": "How much does booking a DJ in Cameroon cost?"'),
    ('"text": "L\'organisateur annonce son budget et AlloDJ cherche le DJ dans cette fourchette, plutôt que de faire comparer des devis. La seule règle fixe est l\'acompte de 10 % à la réservation, le solde étant réglé 3 jours avant l\'événement. Le tarif dépend du DJ, de la durée et du matériel demandé."',
     '"text": "The organiser states the budget and AlloDJ looks for a DJ within that range, rather than comparing quotes. The only fixed rule is the 10% deposit at booking, with the balance settled 3 days before the event. The price depends on the DJ, the duration and the equipment requested."'),

    ('"name": "Peut-on écouter la musique des DJs AlloDJ avant de réserver ?"', '"name": "Can I listen to AlloDJ DJs\' music before booking?"'),
    ('"text": "Oui. Les compiles et les sets des DJs de la plateforme sont en écoute libre, ce qui donne un aperçu direct de ce que l\'on réserve. L\'écoute complète se fait dans l\'application."',
     '"text": "Yes. The platform\'s mixtapes and sets are free to listen to, giving a direct preview of what you\'re booking. Full listening happens in the app."'),

    ('"name": "Comment AlloDJ choisit-il le DJ ?"', '"name": "How does AlloDJ pick the DJ?"'),
    ('"text": "La plateforme croise trois critères : la date (le DJ doit être libre), le lieu (Douala ou Yaoundé aujourd\'hui) et le budget annoncé. Elle désigne ensuite un profil précis — la demande n\'est pas diffusée à une liste de DJs."',
     '"text": "The platform crosses three criteria: the date (the DJ must be free), the venue (Douala or Yaoundé today) and the budget stated. It then picks one specific profile — the request isn\'t broadcast to a list of DJs."'),

    ('"name": "Combien faut-il payer à la réservation ?"', '"name": "How much do I pay when booking?"'),
    ('"text": "Un acompte de 10 % du montant convenu valide la réservation. Le solde se règle 3 jours avant l\'événement. Aucun autre frais n\'est prélevé au moment de la réservation."',
     '"text": "A deposit of 10% of the agreed amount confirms the booking. The balance is settled 3 days before the event. No other fee is charged at booking time."'),

    ('"name": "Peut-on annuler une réservation AlloDJ ?"', '"name": "Can I cancel an AlloDJ booking?"'),
    ('"text": "Oui, sans frais dans les 48 heures qui suivent la réservation. Passé ce délai, l\'acompte reste acquis au DJ qui a bloqué sa date."',
     '"text": "Yes, free within 48 hours of booking. After that, the deposit stays with the DJ who blocked their date."'),

    ('"name": "Comment devient-on DJ sur AlloDJ ?"', '"name": "How do you become a DJ on AlloDJ?"'),
    ('"text": "On ne postule pas. L\'entrée se fait sur recommandation d\'au moins 3 DJs déjà actifs sur la plateforme, qui se portent garants du niveau du nouveau profil."',
     '"text": "You don\'t apply. Entry happens on the recommendation of at least 3 DJs already active on the platform, who vouch for the level of the new profile."'),

    ('"name": "Dans quelles villes AlloDJ intervient-il ?"', '"name": "Which cities does AlloDJ cover?"'),
    ('"text": "Douala et Yaoundé, au Cameroun. D\'autres villes suivront à mesure que le roster s\'étoffe."',
     '"text": "Douala and Yaoundé, in Cameroon. More cities will follow as the roster grows."'),

    ('"name": "Pour quels types d\'événements peut-on réserver un DJ ?"', '"name": "For which types of event can I book a DJ?"'),
    ('"text": "Mariage, cérémonie traditionnelle et dot, soirée d\'entreprise, anniversaire, baptême, remise de diplôme, retour au pays, concert et club."',
     '"text": "Weddings, traditional ceremonies and dowry, company parties, birthdays, christenings, graduations, homecomings, concerts and clubs."'),

    ('"name": "Peut-on aussi louer la sonorisation ?"', '"name": "Can I rent the sound system too?"'),
    ('"text": "Oui. La location de matériel de sonorisation se réserve depuis l\'application, au même endroit que le DJ."',
     '"text": "Yes. Sound-system rental is booked in the app, in the same place as the DJ."'),

    ('"name": "AlloDJ a-t-il une application mobile ?"', '"name": "Does AlloDJ have a mobile app?"'),
    ('"text": "AlloDJ fonctionne dès aujourd\'hui dans le navigateur sur appli.allodeejay.com. Les versions App Store et Google Play sont en préparation."',
     '"text": "AlloDJ works in the browser today at appli.allodeejay.com. The App Store and Google Play versions are being prepared."'),

    # Migré depuis traduire_json_ld() : ces libellés fonctionnaient déjà via
    # un .replace() séquentiel non trié, mais silencieux en cas de chaîne
    # obsolète (voir l'entrée "Booking DJ Douala & Yaoundé…" supprimée, qui
    # ne correspondait plus au JSON-LD actuel et ne faisait donc plus rien).
    # Ici la chaîne bénéficie du même filet que le reste : la table est
    # triée par longueur et build-en.py échoue bruyamment si le FR disparaît.
    ('"name": "Accueil"', '"name": "Home"'),
    ('"name": "Booking DJ à Douala"', '"name": "DJ booking in Douala"'),
    ('"name": "Types d\'événements"', '"name": "Event types"'),
    ('"name": "Roster de DJs"', '"name": "DJ roster"'),
    ('"name": "Questions fréquentes"', '"name": "Frequently asked questions"'),
    ('"description": "Plateforme de booking et de réservation de DJ à Douala, Yaoundé et partout au Cameroun, avec location de sonorisation."',
     '"description": "DJ booking platform for Douala, Yaoundé and the rest of Cameroon, with sound-system rental."'),
    ('"name": "Booking et réservation de DJ à Douala, Yaoundé et au Cameroun"',
     '"name": "DJ booking in Douala, Yaoundé and Cameroon"'),
    ('"serviceType": "Réservation de DJ pour événement"', '"serviceType": "Event DJ booking"'),
    ('"name": "Cameroun"', '"name": "Cameroon"'),
    ('"name": "Types d\'événements couverts"', '"name": "Event types covered"'),

    # Chapôs et paragraphes longs
    ("AlloDJ ne diffuse pas votre demande à toute une liste : la plateforme désigne le DJ qui colle à votre date, votre lieu et votre budget — puis verrouille la réservation avec un acompte.",
     "AlloDJ doesn't broadcast your request to a list. The platform picks the DJ who fits your date, your venue and your budget — then locks the booking in with a deposit."),
    ("Booking et réservation de DJ à Douala, Yaoundé et partout au Cameroun.",
     "DJ booking in Douala, Yaoundé and across Cameroon."),
    ("Réserver un DJ sur AlloDJ tient en trois étapes&nbsp;: décrire l'événement, recevoir une recommandation avec le tarif affiché, puis bloquer la date avec",
     "Booking a DJ on AlloDJ takes three steps: describe the event, get a recommendation with the price shown up front, then lock the date with"),
    ("10&nbsp;% d'acompte", "a 10% deposit"),
    (". Le solde se règle", ". The balance is due"),
    ("3 jours avant", "3 days before"),
    ("l'événement et l'annulation reste sans frais pendant", "the event, and cancellation stays free for"),
    ("48 heures", "48 hours"),
    ("Date, lieu, budget, style. Deux minutes dans l'app — pas dix messages restés sans réponse.",
     "Date, venue, budget, style. Two minutes in the app — not ten messages left unanswered."),
    ("Un DJ désigné, tarif réel affiché avant que vous ne réserviez. Vous restez libre d'en choisir un autre.",
     "One DJ picked for you, real price shown before you book. You stay free to choose another."),
    ("10 % pour bloquer la date, le solde 3 jours avant. Annulation sans frais dans les 48 h.",
     "10% to lock the date, balance 3 days before. Free cancellation within 48 h."),
    ("AlloDJ couvre", "AlloDJ covers"),
    ("huit types d'événements", "eight types of event"),
    ("à Douala et Yaoundé&nbsp;: mariage, cérémonie traditionnelle et dot, soirée d'entreprise, anniversaire, baptême, remise de diplôme, fête privée, concert et club. Le type d'événement détermine le déroulé, les moments-clés et le répertoire — la recommandation en tient compte.",
     "in Douala and Yaoundé: weddings, traditional ceremonies and dowry, company parties, birthdays, christenings, graduations, private parties, concerts and clubs. The type of event drives the running order, the key moments and the repertoire — the recommendation takes that into account."),
    ("Un DJ n'entre pas dans le roster AlloDJ en postulant&nbsp;: il lui faut la recommandation d'",
     "A DJ doesn't join the AlloDJ roster by applying: they need a recommendation from "),
    ("au moins 3 DJs déjà actifs", "at least 3 DJs already active"),
    ("sur la plateforme. Chaque prestation est ensuite notée, et ces notes pèsent sur les recommandations suivantes. La sélection est portée par les DJs eux-mêmes, pas par un formulaire ouvert.",
     "on the platform. Every booking is rated afterwards, and those ratings weigh on later recommendations. Selection is carried by the DJs themselves, not by an open form."),
    ("Les compiles des DJs AlloDJ s'écoutent avant de réserver.",
     "You can listen to AlloDJ DJs' mixtapes before booking."),
    ("Sept compiles", "Seven mixtapes"),
    ("signées DJ&nbsp;Fab, cofondateur de la plateforme, couvrent l'amapiano, le zouk, le rap français des années&nbsp;90 et le R&amp;B des années&nbsp;2000.",
     "by DJ Fab, co-founder of the platform, cover amapiano, zouk, 90s French rap and 2000s R&amp;B."),
    ("L'écoute complète se fait dans l'application", "Full listening happens in the app"),
    ("Réserver un DJ par bouche-à-oreille laisse le tarif, l'annulation et le recours à la négociation. Sur AlloDJ, le tarif est affiché avant réservation, l'acompte est fixé à",
     "Booking a DJ by word of mouth leaves the price, the cancellation and any recourse up to negotiation. On AlloDJ the price is shown before booking, the deposit is set at"),
    ("10&nbsp;%", "10%"),
    (", l'annulation est sans frais pendant", ", cancellation is free for"),
    ("48&nbsp;heures", "48 hours"),
    ("et chaque prestation est notée.", "and every booking is rated."),
    ("Rejoindre le roster AlloDJ passe par la cooptation&nbsp;: il faut qu'",
     "Joining the AlloDJ roster runs through co-optation: it takes "),
    ("se portent garants du nouveau profil. Il n'existe pas de formulaire de candidature ouvert — la réputation de ceux qui recommandent engage celle du DJ recommandé, et l'inverse.",
     "to vouch for the new profile. There is no open application form — the reputation of those who recommend is tied to that of the DJ they recommend, and the other way round."),
    ("«&nbsp;Un DJ n'entre pas parce qu'il le demande. Il entre parce que trois DJs déjà en place engagent leur réputation sur la sienne.&nbsp;»",
     "&ldquo;A DJ doesn't get in because they ask. They get in because three DJs already on board stake their reputation on theirs.&rdquo;"),
    ("AlloDJ — règle de cooptation", "AlloDJ — co-optation rule"),
    ("DJs déjà actifs doivent recommander un nouveau profil pour qu'il rejoigne la plateforme.",
     "DJs already active must recommend a new profile for it to join the platform."),
    ("AlloDJ tourne déjà dans votre navigateur. Les versions App Store et Google Play arrivent.",
     "AlloDJ already runs in your browser. The App Store and Google Play versions are on the way."),
    ("Booking de DJ et location de sonorisation à Douala, Yaoundé et partout au Cameroun.",
     "DJ booking and sound-system rental in Douala, Yaoundé and across Cameroon."),

    ("Voir les DJs par ville&nbsp;:", "See DJs by city:"),
    ('<li><a href="dj-douala.html">Booking DJ à Douala</a></li><li><a href="dj-yaounde.html">Booking DJ à Yaoundé</a></li>',
     '<li><a href="../dj-douala.html">DJ booking in Douala</a></li><li><a href="../dj-yaounde.html">DJ booking in Yaoundé</a></li>'),

    ("© 2026 ALLO DJ SARL — Tous droits réservés", "© 2026 ALLO DJ SARL — All rights reserved"),
    ("Design — Kawai IT", "Design — Kawai IT"),

    # FAQ — questions
    ("Comment réserver un DJ à Douala&nbsp;?", "How do I book a DJ in Douala?"),
    ("Comment trouver un DJ à Yaoundé&nbsp;?", "How do I find a DJ in Yaoundé?"),
    ("Combien coûte le booking d'un DJ au Cameroun&nbsp;?", "How much does booking a DJ in Cameroon cost?"),
    ("Peut-on écouter la musique des DJs AlloDJ avant de réserver&nbsp;?", "Can I listen to AlloDJ DJs' music before booking?"),
    ("Comment AlloDJ choisit-il le DJ&nbsp;?", "How does AlloDJ pick the DJ?"),
    ("Combien faut-il payer à la réservation&nbsp;?", "How much do I pay when booking?"),
    ("Puis-je annuler&nbsp;?", "Can I cancel?"),
    ("Comment devient-on DJ sur AlloDJ&nbsp;?", "How do you become a DJ on AlloDJ?"),
    ("Dans quelles villes AlloDJ intervient-il&nbsp;?", "Which cities does AlloDJ cover?"),
    ("Pour quels types d'événements&nbsp;?", "For which types of event?"),
    ("Peut-on aussi louer la sonorisation&nbsp;?", "Can I rent the sound system too?"),
    ("Y a-t-il une application mobile&nbsp;?", "Is there a mobile app?"),

    # FAQ — réponses
    ("Indiquez la date, le lieu et votre budget dans", "Enter the date, the venue and your budget in"),
    ("l'application AlloDJ", "the AlloDJ app"),
    (". La plateforme vous désigne un DJ disponible à", ". The platform picks a DJ available in"),
    ("pour cette date, adapté à votre type d'événement. La réservation est confirmée par un acompte de 10&nbsp;%.",
     "on that date, suited to your type of event. The booking is confirmed with a 10% deposit."),
    ("Le fonctionnement est le même qu'à Douala&nbsp;: le booking se fait depuis l'application, et le DJ proposé est choisi parmi ceux qui couvrent",
     "It works exactly as in Douala: booking happens in the app, and the DJ offered is chosen among those covering"),
    (". Pas de mise en concurrence, pas de devis à comparer.", ". No bidding war, no quotes to compare."),
    ("C'est vous qui annoncez le budget&nbsp;: AlloDJ cherche le DJ dans cette fourchette plutôt que de vous faire comparer des devis. La seule règle fixe est l'",
     "You state the budget: AlloDJ looks for a DJ within that range rather than making you compare quotes. The only fixed rule is the "),
    ("acompte de 10&nbsp;%", "10% deposit"),
    ("à la réservation, le solde étant réglé 3&nbsp;jours avant l'événement. Le tarif dépend du DJ, de la durée et du matériel demandé.",
     "at booking, with the balance settled 3 days before the event. The price depends on the DJ, the duration and the equipment requested."),
    ("Oui. Les compiles et les sets des DJs de la plateforme sont en écoute libre&nbsp;: c'est le meilleur aperçu de ce que vous réservez. L'écoute complète se fait dans l'application.",
     "Yes. The platform's mixtapes and sets are free to listen to — the best preview of what you're booking. Full listening happens in the app."),
    ("La plateforme croise trois critères&nbsp;: la", "The platform crosses three criteria: the"),
    ("(le DJ doit être libre), le", "(the DJ must be free), the"),
    ("(Douala ou Yaoundé aujourd'hui) et le", "(Douala or Yaoundé today) and the"),
    ("annoncé. Elle désigne ensuite un profil précis — votre demande n'est pas diffusée à une liste de DJs qui vous rappelleraient tous.",
     "you state. It then picks one specific profile — your request isn't broadcast to a list of DJs who would all call you back."),
    ("Un acompte de", "A deposit of"),
    ("du montant convenu valide la réservation. Le solde se règle", "of the agreed amount confirms the booking. The balance is settled"),
    ("l'événement. Aucun autre frais n'est prélevé au moment de la réservation.",
     "the event. No other fee is charged at booking time."),
    ("Oui. L'annulation est", "Yes. Cancellation is"),
    ("sans frais dans les 48 heures", "free within 48 hours"),
    ("qui suivent la réservation. Passé ce délai, l'acompte reste acquis au DJ qui a bloqué sa date.",
     "of booking. After that, the deposit stays with the DJ who blocked their date."),
    ("On ne postule pas. L'entrée se fait", "You don't apply. Entry happens"),
    ("sur recommandation d'au moins 3 DJs déjà actifs", "on the recommendation of at least 3 DJs already active"),
    ("sur la plateforme. Ce sont eux qui se portent garants du niveau et du sérieux du nouveau profil.",
     "on the platform. They vouch for the level and the reliability of the new profile."),
    (", au Cameroun. D'autres villes suivront à mesure que le roster s'étoffe.",
     ", in Cameroon. More cities will follow as the roster grows."),
    ("Mariage, cérémonie traditionnelle et dot, soirée d'entreprise, anniversaire, baptême, remise de diplôme, retour au pays, concert et club. Le type d'événement change le déroulé et le répertoire&nbsp;: la recommandation en tient compte.",
     "Weddings, traditional ceremonies and dowry, company parties, birthdays, christenings, graduations, homecomings, concerts and clubs. The type of event changes the running order and the repertoire — the recommendation takes that into account."),
    ("Oui. La location de matériel de sonorisation se réserve depuis l'application, au même endroit que le DJ.",
     "Yes. Sound-system rental is booked in the app, in the same place as the DJ."),
    ("AlloDJ fonctionne dès aujourd'hui dans le navigateur, sur", "AlloDJ works in the browser today, at"),
    (". Les versions App&nbsp;Store et Google&nbsp;Play arrivent.", ". App Store and Google Play versions are coming."),

    # Titres de section
    ("Trois temps,", "Three steps,"),
    ("zéro bouche-à-oreille", "zero word of mouth"),
    ("Un DJ pour chaque événement, à Douala comme à Yaoundé", "A DJ for every event, in Douala as in Yaoundé"),
    ("Des DJs vérifiés à Douala et Yaoundé", "Vetted DJs in Douala and Yaoundé"),
    ("Écouter la musique AlloDJ avant de réserver", "Listen to AlloDJ music before booking"),
    ("Booker un DJ sur AlloDJ ou par bouche-à-oreille", "Booking a DJ on AlloDJ versus word of mouth"),
    ("L'entrée se fait par recommandation, pas par candidature", "Entry is by recommendation, not application"),
    ("Ce qu'on nous demande le plus", "What we get asked most"),
    ("Disponible dès maintenant", "Available right now"),
    ("Le bon DJ.", "The right DJ."),
    ("Au bon", "For the"),
    ("événement.", "right event."),

    # Ardoises et étiquettes
    ("Booking DJ · Douala / Yaoundé", "DJ booking · Douala / Yaoundé"),
    ("Ouverture", "Opening"),
    ("La méthode", "The method"),
    ("3 temps", "3 steps"),
    ("Les événements", "The events"),
    ("Le roster", "The roster"),
    ("Sur cooptation", "By co-optation"),
    ("Les compiles", "The mixtapes"),
    ("L'écart", "The gap"),
    ("Comparatif", "Comparison"),
    ("Cooptation", "Co-optation"),
    ("Les questions", "The questions"),
    ("Sortie", "Outro"),
    ("Contact", "Contact"),

    # Étapes
    ("Votre événement", "Your event"),
    ("Une recommandation", "One recommendation"),
    ("Acompte &amp; solde", "Deposit &amp; balance"),

    # Cartes d'événements
    ("01 — Cérémonie", "01 — Ceremony"),
    ("02 — Cérémonie", "02 — Ceremony"),
    ("03 — Corporate", "03 — Corporate"),
    ("04 — Privé", "04 — Private"),
    ("05 — Famille", "05 — Family"),
    ("06 — Privé", "06 — Private"),
    ("07 — Privé", "07 — Private"),
    ("08 — Scène", "08 — Stage"),
    ("Du cocktail à la fin de soirée, entrée des mariés et ouverture du bal respectées.",
     "From the cocktail to the last dance, with the couple's entrance and first dance handled properly."),
    ("Traditionnel &amp; dot", "Traditional &amp; dowry"),
    ("Un DJ qui connaît le déroulé et alterne répertoire du terroir et sons actuels.",
     "A DJ who knows the running order and alternates local repertoire with current sounds."),
    ("Entreprise", "Company"),
    ("Lancements, séminaires, fin d'année. Calibré pour l'image de la boîte.",
     "Launches, seminars, year-end parties. Calibrated for the company's image."),
    ("Anniversaire", "Birthday"),
    ("Une playlist qui parle à la génération présente et fait danser tout le monde.",
     "A playlist that speaks to the generation in the room and gets everyone dancing."),
    ("Baptême", "Christening"),
    ("Ambiance familiale, puis montée en énergie une fois les enfants couchés.",
     "Family mood first, then energy climbing once the children are in bed."),
    ("Remise de diplôme", "Graduation"),
    ("Célébration jeune et rythmée pour marquer le coup avec la promo.",
     "A young, up-tempo celebration to mark the moment with the class."),
    ("Retour au pays", "Homecoming"),
    ("Retrouvailles de la diaspora, fêtes à la maison, soirées entre proches.",
     "Diaspora reunions, house parties, evenings among close friends."),
    ("Concert &amp; club", "Concert &amp; club"),
    ("Warm-up, première partie ou set principal, avec le matériel qu'il faut.",
     "Warm-up, support slot or headline set, with the right equipment."),
    ("Mariage", "Wedding"),

    # Tableau comparatif
    ("Critère", "Criterion"),
    ("Bouche-à-oreille", "Word of mouth"),
    ("Tarif", "Price"),
    ("Négocié à l'aveugle", "Negotiated blind"),
    ("Affiché avant de réserver", "Shown before booking"),
    ("Paiement", "Payment"),
    ("Espèces, rien d'écrit", "Cash, nothing in writing"),
    ("Acompte 10 % + solde, dans l'app", "10% deposit + balance, in the app"),
    ("Annulation", "Cancellation"),
    ("Au cas par cas", "Case by case"),
    ("48 h pour annuler sans frais", "48 h to cancel free of charge"),
    ("Sélection", "Selection"),
    ("Le DJ qu'on connaît", "Whichever DJ you know"),
    ("Recommandation + profils à comparer", "Recommendation + profiles to compare"),
    ("Aperçu", "Preview"),
    ("Aucun avant le jour J", "None before the day itself"),
    ("Compiles en écoute libre", "Mixtapes free to listen to"),
    ("Avis", "Reviews"),
    ("Réputation orale", "Word-of-mouth reputation"),
    ("Notes après chaque prestation", "Ratings after every booking"),
    ("Échanges", "Messaging"),
    ("Messages éparpillés", "Messages scattered everywhere"),
    ("Messagerie intégrée, tout tracé", "Built-in messaging, everything logged"),

    # Formulaire, boutons, navigation
    ("Ouvrir l'app", "Open the app"),
    ("Ouvrir AlloDJ", "Open AlloDJ"),
    ("Localisation", "Location"),
    ("Date de l'événement", "Event date"),
    ("Lancer", "Search"),
    ("d'acompte", "deposit"),
    ("pour annuler", "to cancel"),
    ("Notés", "Rated"),
    ("après chaque prestation", "after every booking"),
    ("Écouter la suite dans l'app", "Keep listening in the app"),
    ("Une question ? Écrivez-nous", "A question? Write to us"),
    ("Seuil de cooptation", "Co-optation threshold"),
    ("Bientôt sur", "Coming soon to"),
    ("Téléphone", "Phone"),
    ("Basé à", "Based in"),
    # Le siège a changé avec l'immatriculation de la SARL. L'ancienne valeur
    # « Douala, Cameroun » est restée en ligne côté anglais faute d'avoir
    # relancé ce script : l'adresse affichée y était fausse.
    ("Ngousso, Yaoundé — Cameroun", "Ngousso, Yaoundé — Cameroon"),
    ("Votre évènement, notre passion", "Your event, our passion"),

    # Pied de page
    ("A2 — Méthode", "A2 — Method"),
    ("A3 — Événements", "A3 — Events"),
    ("B2 — Compiles", "B2 — Mixtapes"),
    ("Villes", "Cities"),
    ("DJ pour mariage au Cameroun", "Wedding DJ in Cameroon"),
    ("Écouter la musique AlloDJ", "Listen to AlloDJ music"),
    ("Suivre", "Follow"),
    ("Légal", "Legal"),
    ("CGU", "Terms of use"),
    ("Confidentialité", "Privacy"),
    ("Mentions légales", "Legal notice"),
    ("Suppression de compte", "Delete account"),

    # Étiquettes de nav (les codes de piste restent)
    (">Méthode<", ">Method<"),
    (">Événements<", ">Events<"),
    (">Écart<", ">Gap<"),
    (">Rejoindre<", ">Join<"),

    # Sélecteur de langue : l'état actif bascule sur EN
    ('<a href="/" hreflang="fr" lang="fr" class="on" aria-current="true">FR</a>',
     '<a href="/" hreflang="fr" lang="fr">FR</a>'),
    ('<a href="/en/" hreflang="en" lang="en">EN</a>',
     '<a href="/en/" hreflang="en" lang="en" class="on" aria-current="true">EN</a>'),
    ('aria-label="Langue du site"', 'aria-label="Site language"'),

    # Bannière : elle propose le français aux visiteurs francophones
    ('<b>This site is also available in English.</b> Switch language?',
     '<b>Ce site existe aussi en français.</b> Changer de langue&nbsp;?'),
    ('<a href="/en/" class="btn btn-peak" id="langgo">Read in English</a>',
     '<a href="/" class="btn btn-peak" id="langgo">Lire en français</a>'),

    # Attributs
    ('aria-label="AlloDJ, accueil"', 'aria-label="AlloDJ, home"'),
    ('aria-label="Index des sections"', 'aria-label="Section index"'),
    ('aria-label="Recherche rapide de DJ"', 'aria-label="Quick DJ search"'),
    ('aria-label="Précédent"', 'aria-label="Previous"'),
    ('aria-label="Suivant"', 'aria-label="Next"'),
    ('alt="DJ vérifié AlloDJ"', 'alt="Vetted AlloDJ DJ"'),
    ('alt="Ouverture du bal lors d\'un mariage, DJ en fond de salle"', 'alt="First dance at a wedding, DJ at the back of the room"'),
    ('alt="Cérémonie traditionnelle et dot, familles réunies sous la tente"', 'alt="Traditional dowry ceremony, families gathered under the canopy"'),
    ('alt="Soirée de fin d\'année en entreprise, tables et scène éclairée"', 'alt="Company year-end party, tables and a lit stage"'),
    ('alt="Anniversaire, gâteau et bougies au milieu des invités"', 'alt="Birthday party, cake and candles among the guests"'),
    ('alt="Réception de baptême, table dressée sous des guirlandes lumineuses"', 'alt="Christening reception, table set under string lights"'),
    ('alt="Remise de diplôme, chapeaux lancés au crépuscule"', 'alt="Graduation, caps thrown at dusk"'),
    ('alt="Fête privée sur une terrasse, invités en train de danser"', 'alt="Private party on a terrace, guests dancing"'),
    ('alt="Set en club, foule et faisceaux lumineux"', 'alt="Club set, crowd and light beams"'),
]

# ── En-tête : titre, description, partage, hreflang ─────────────────────────
TETE = [
    ("<title>Booking DJ Cameroun — Réserver un DJ à Douala et Yaoundé | AlloDJ</title>",
     "<title>DJ Booking in Cameroon — Book a DJ in Douala and Yaoundé | AlloDJ</title>"),
    ('content="Booking et réservation de DJ à Douala, Yaoundé et partout au Cameroun. Trouvez un DJ pour mariage, soirée d\'entreprise ou club : AlloDJ désigne le DJ adapté à votre date, votre lieu et votre budget. 10 % d\'acompte, annulation sous 48 h."',
     'content="DJ booking in Douala, Yaoundé and across Cameroon. Find a DJ for a wedding, a company party or a club night: AlloDJ picks the DJ that fits your date, your venue and your budget. 10% deposit, free cancellation within 48 h."'),
    ('<meta property="og:title" content="Booking DJ Cameroun — Réserver un DJ à Douala et Yaoundé">',
     '<meta property="og:title" content="DJ Booking in Cameroon — Book a DJ in Douala and Yaoundé">'),
    ('<meta property="og:description" content="Trouvez un DJ à Douala ou Yaoundé sans passer par le bouche-à-oreille. AlloDJ désigne le DJ qui colle à votre date, votre lieu et votre budget.">',
     '<meta property="og:description" content="Find a DJ in Douala or Yaoundé without relying on word of mouth. AlloDJ picks the DJ who fits your date, your venue and your budget.">'),
    ('<meta name="twitter:title" content="Booking DJ Cameroun — Réserver un DJ à Douala et Yaoundé">',
     '<meta name="twitter:title" content="DJ Booking in Cameroon — Book a DJ in Douala and Yaoundé">'),
    ('<meta name="twitter:description" content="Réservation de DJ à Douala, Yaoundé et au Cameroun. Le DJ désigné selon votre date, votre lieu et votre budget.">',
     '<meta name="twitter:description" content="DJ booking in Douala, Yaoundé and Cameroon. The DJ picked for your date, your venue and your budget.">'),
    ('<html lang="fr">', '<html lang="en">'),
    ('<meta property="og:locale" content="fr_CM">', '<meta property="og:locale" content="en">'),
    ('<link rel="canonical" href="https://allodeejay.com/">',
     '<link rel="canonical" href="https://allodeejay.com/en/">'),
    ('<meta property="og:url" content="https://allodeejay.com/">',
     '<meta property="og:url" content="https://allodeejay.com/en/">'),
    ('<meta name="geo.placename" content="Douala, Yaoundé">',
     '<meta name="geo.placename" content="Douala, Yaounde">'),
]

# ── Commentaires de code (bandeau de consentement, hors JSON-LD) ───────────
# Hors sujet JSON-LD, mais le script de diagnostic ne fait pas la différence
# entre du français dans le contenu et du français dans un commentaire de
# script : ces deux blocs traînaient dans en/index.html et remontaient comme
# faux positifs. Seul le commentaire est traduit ; `forcer` reste le nom réel
# de la clé lue par le code plus bas et ne doit pas changer.
SCRIPTS = [
    ("/* Consent Mode v2 — DOIT rester le premier script de la page. Google ignore\n"
     "   un `default` posé après un `config`, et une extension qui charge gtag avant\n"
     "   nous traquerait sans consentement. Ne pas déplacer, ne pas différer. */",
     "/* Consent Mode v2 — MUST stay the first script on the page. Google ignores\n"
     "   a `default` set after a `config`, and an extension loading gtag before\n"
     "   us would track without consent. Do not move it, do not defer it. */"),
    ("/* Identifiants Google. La bannière s'affiche dès qu'un traceur est présent —\n"
     "   soit renseigné ici, soit détecté dans la page (extension, balise collée).\n"
     "   `forcer: true` l'affiche en toutes circonstances. */",
     "/* Google IDs. The banner shows as soon as a tracker is present —\n"
     "   either set here, or detected on the page (extension, pasted tag).\n"
     "   `forcer: true` shows it in all circumstances. */"),
]


def traduire_json_ld(html):
    """Bascule les URLs et la langue déclarée du JSON-LD vers /en/.

    Les libellés (name/description/text) sont traduits en amont, dans
    TEXTES, où la table triée par longueur et le contrôle `manquantes`
    de main() détectent une chaîne FR disparue. Ici on ne fait que de la
    réécriture d'URL, purement mécanique — un replace() simple suffit.
    """
    paires = [
        ('"inLanguage": "fr-CM"', '"inLanguage": "en"'),
        ('"inLanguage": "fr"', '"inLanguage": "en"'),
        ('"https://allodeejay.com/#', '"https://allodeejay.com/en/#'),
        ('"url": "https://allodeejay.com/"', '"url": "https://allodeejay.com/en/"'),
        ('"item": "https://allodeejay.com/"', '"item": "https://allodeejay.com/en/"'),
        ('"item": "https://allodeejay.com/#', '"item": "https://allodeejay.com/en/#'),
    ]
    for a, b in paires:
        html = html.replace(a, b)
    return html


def main():
    source = open(SRC, encoding="utf-8").read()
    html = source
    manquantes = []

    regles = sorted(TETE + TEXTES + SCRIPTS, key=lambda c: len(c[0]), reverse=True)
    for fr, en in regles:
        if fr not in html:
            manquantes.append(fr)
            continue
        html = html.replace(fr, en)

    if manquantes:
        print("ÉCHEC — chaînes françaises introuvables dans index.html :\n")
        for m in manquantes:
            print("  ·", m[:110])
        print("\nLe français a bougé : mettre à jour la table de traduction.")
        sys.exit(1)

    html = traduire_json_ld(html)

    # les assets remontent d'un cran depuis /en/
    html = re.sub(r'(src|href)="assets/', r'\1="../assets/', html)
    html = html.replace('src="assets/photos/${f}.jpg"', 'src="../assets/photos/${f}.jpg"')
    html = html.replace('`<div class="kard"><img src="assets/', '`<div class="kard"><img src="../assets/')

    # toutes les pages sœurs vivent à la racine : depuis /en/ on remonte d'un cran
    html = re.sub(
        r'href="(?!\.\./|https?:|mailto:|tel:|/|#)([\w-]+\.html)',
        lambda m: 'href="../' + m.group(1),
        html,
    )

    os.makedirs(DEST_DIR, exist_ok=True)
    open(DEST, "w", encoding="utf-8").write(html)

    # on ne compte que les chemins RELATIFS : les URL absolues sont légitimes
    restes = len(re.findall(r'(?<![:/.])(?<!\.\./)assets/', html))
    print(f"en/index.html écrit — {len(TETE) + len(TEXTES) + len(SCRIPTS)} chaînes traduites")
    if restes:
        print(f"/!\\ {restes} chemin(s) assets/ non préfixé(s) — à vérifier")


if __name__ == "__main__":
    main()
