/* Consentement — AlloDJ
 *
 * Rien de Google n'est chargé tant que le visiteur n'a pas choisi. Pas même
 * gtag.js : une requête vers googletagmanager.com transmet déjà l'IP, ce qui
 * est précisément ce qu'on a supprimé en rapatriant les polices.
 *
 * Google propose un mode « avancé » où le tag se charge avec tous les
 * consentements refusés (pings sans cookie, modélisation des conversions).
 * On ne le retient pas : il fait partir la requête avant le choix, et
 * plusieurs autorités européennes le contestent. Pour l'activer malgré tout,
 * il suffirait d'appeler charger() dès le départ au lieu de l'appeler après
 * appliquer() — voir la fin du fichier.
 *
 * Consent Mode v2 : les quatre signaux sont posés en `denied` AVANT toute
 * commande config, comme l'exige la documentation Google. L'ordre compte.
 */
(function () {
  'use strict';

  var CLE = 'allodj-consent';
  var VERSION = 1;
  var DUREE = 13 * 30 * 24 * 3600 * 1000;  // 13 mois (recommandation CNIL)

  var cfg = window.AlloDJConsent || {};
  var GA4 = cfg.ga4 || '';        // G-XXXXXXXXXX
  var ADS = cfg.ads || '';        // AW-XXXXXXXXX
  var textes = cfg.i18n || {};

  function t(cle, defaut) {
    return textes[cle] || defaut;
  }

  /* ── Mémoire du choix ───────────────────────────────────────────────── */

  function lire() {
    try {
      var brut = localStorage.getItem(CLE);
      if (!brut) return null;
      var d = JSON.parse(brut);
      if (d.v !== VERSION) return null;
      if (Date.now() - d.t > DUREE) return null;   // consentement périmé
      return d;
    } catch (e) {
      return null;
    }
  }

  function ecrire(mesure, pub) {
    try {
      localStorage.setItem(CLE, JSON.stringify({
        v: VERSION, t: Date.now(), mesure: !!mesure, pub: !!pub,
      }));
    } catch (e) {}
  }

  /* ── Consent Mode v2 ────────────────────────────────────────────────── */

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  // Les défauts sont normalement posés par le snippet inline du <head> : ils
  // DOIVENT précéder tout gtag chargé par une extension, et ce fichier est
  // différé. Filet de sécurité si le snippet manque.
  var dejaPose = window.dataLayer.some(function (a) {
    return a && a[0] === 'consent' && a[1] === 'default';
  });
  if (!dejaPose) {
    gtag('consent', 'default', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'denied',
      functionality_storage: 'granted',
      security_storage: 'granted',
      wait_for_update: 500,
    });
  }

  function appliquer(mesure, pub) {
    gtag('consent', 'update', {
      analytics_storage: mesure ? 'granted' : 'denied',
      ad_storage: pub ? 'granted' : 'denied',
      ad_user_data: pub ? 'granted' : 'denied',
      ad_personalization: pub ? 'granted' : 'denied',
    });
  }

  var charge = false;
  function charger() {
    if (charge || (!GA4 && !ADS)) return;
    charge = true;
    var id = GA4 || ADS;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(s);
    gtag('js', new Date());
    if (GA4) gtag('config', GA4, { anonymize_ip: true });
    if (ADS) gtag('config', ADS);
  }

  /* ── Bannière ───────────────────────────────────────────────────────── */

  function construire() {
    var b = document.createElement('div');
    b.className = 'cc';
    b.setAttribute('role', 'dialog');
    b.setAttribute('aria-modal', 'false');
    b.setAttribute('aria-label', t('titre', 'Gestion des cookies'));
    b.innerHTML =
      '<div class="cc-in">' +
        '<div class="cc-txt">' +
          '<b>' + t('titre', 'Cookies') + '</b>' +
          '<p>' + t('corps',
            'Nous utilisons des cookies de mesure d’audience et, si vous l’acceptez, ' +
            'de publicité. Rien n’est déposé sans votre accord.') +
            ' <a href="' + (cfg.politique || 'confidentialite.html') + '">' +
            t('lien', 'En savoir plus') + '</a>' +
          '</p>' +
          '<div class="cc-opt" hidden>' +
            '<label><input type="checkbox" id="cc-mesure"> ' +
              t('mesure', 'Mesure d’audience — comprendre comment le site est utilisé') +
            '</label>' +
            '<label><input type="checkbox" id="cc-pub"> ' +
              t('pub', 'Publicité — mesurer l’efficacité de nos campagnes') +
            '</label>' +
          '</div>' +
        '</div>' +
        '<div class="cc-btn">' +
          '<button type="button" class="btn btn-ghost" data-cc="refus">' +
            t('refuser', 'Tout refuser') + '</button>' +
          '<button type="button" class="btn btn-ghost" data-cc="perso">' +
            t('personnaliser', 'Personnaliser') + '</button>' +
          // Même style que « Tout refuser » : la CNIL exige que refuser soit
          // aussi simple qu'accepter. Un bouton vert face à un bouton terne
          // est le nudge que ses délibérations de 2022 ont sanctionné.
          '<button type="button" class="btn btn-ghost cc-oui" data-cc="tout">' +
            t('accepter', 'Tout accepter') + '</button>' +
        '</div>' +
      '</div>';
    return b;
  }

  var banniere = null;

  function fermer() {
    if (banniere) { banniere.remove(); banniere = null; }
  }

  function decider(mesure, pub) {
    ecrire(mesure, pub);
    appliquer(mesure, pub);
    if (mesure || pub) charger();
    fermer();
  }

  function ouvrir() {
    if (banniere) return;
    banniere = construire();
    document.body.appendChild(banniere);

    var opt = banniere.querySelector('.cc-opt');
    var cbM = banniere.querySelector('#cc-mesure');
    var cbP = banniere.querySelector('#cc-pub');

    banniere.addEventListener('click', function (e) {
      var b = e.target.closest('[data-cc]');
      if (!b) return;
      var action = b.dataset.cc;

      if (action === 'tout') return decider(true, true);
      if (action === 'refus') return decider(false, false);

      // « Personnaliser » : premier clic déplie, second enregistre
      if (opt.hidden) {
        opt.hidden = false;
        b.textContent = t('enregistrer', 'Enregistrer mes choix');
        cbM.focus();
      } else {
        decider(cbM.checked, cbP.checked);
      }
    });
  }

  /* ── Réouverture depuis le pied de page ─────────────────────────────── */

  document.addEventListener('click', function (e) {
    var lien = e.target.closest('[data-cookies]');
    if (!lien) return;
    e.preventDefault();
    try { localStorage.removeItem(CLE); } catch (err) {}
    ouvrir();
  });

  /* ── Démarrage ──────────────────────────────────────────────────────── */

  /* Un tag Google posé par une extension (Site Kit, injecteur de code) ne
     passe pas par notre configuration : sans cette détection, il traquerait
     sans bannière. On regarde ce qui est réellement chargé dans la page. */
  function traceurPresent() {
    if (GA4 || ADS || cfg.forcer) return true;
    if (document.querySelector('script[src*="googletagmanager.com"],' +
                               'script[src*="google-analytics.com"],' +
                               'script[src*="googlesyndication.com"]')) return true;
    return window.dataLayer.some(function (a) {
      return a && (a[0] === 'config' || a[0] === 'js');
    });
  }

  var choix = lire();
  if (choix) {
    appliquer(choix.mesure, choix.pub);
    if (choix.mesure || choix.pub) charger();
  } else if (traceurPresent()) {
    // Aucun tag n'est chargé par nous ici : c'est le choix qui déclenche.
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', ouvrir);
    } else {
      ouvrir();
    }
  }
})();
