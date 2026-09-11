const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const PIN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>';

/* Langue : on SUGGÈRE la version anglaise, on ne redirige jamais.
   Une redirection automatique empêche les moteurs de voir les deux versions
   (doc Google, « Managing multi-regional and multilingual sites »). */
(function () {
  const ICI = (document.documentElement.lang || 'fr').slice(0, 2);
  const AUTRE = ICI === 'fr' ? 'en' : 'fr';
  let choix = null;
  try { choix = localStorage.getItem('allodj-lang'); } catch (e) {}
  if (choix === ICI) return;

  const bar = document.getElementById('langbar');
  if (!bar) return;
  const veutAutre = (navigator.languages || [navigator.language || ''])
    .some((l) => String(l).toLowerCase().startsWith(AUTRE));
  if (!veutAutre) return;

  bar.hidden = false;
  const memo = (v) => { try { localStorage.setItem('allodj-lang', v); } catch (e) {} };
  document.getElementById('langgo').addEventListener('click', () => memo(AUTRE));
  document.getElementById('langno').addEventListener('click', () => { memo(ICI); bar.hidden = true; });
})();

/* Colonnes de DJs — set dupliqué pour une boucle sans couture */
(function () {
  const TOUS = [
    ['real-dj-01','Douala','Afrobeats'], ['real-dj-03','Yaoundé','Amapiano'],
    ['real-dj-05','Douala','Club'],      ['real-dj-07','Douala','Vinyle'],
    ['real-dj-02','Douala','Corporate'], ['real-dj-04','Yaoundé','Rap FR'],
    ['real-dj-06','Douala','Zouk'],      ['real-dj-08','Yaoundé','Ambiance'],
  ];
  // Une page ville ne montre que ses DJs : afficher Yaoundé sur /dj-douala
  // contredirait la page elle-même.
  const ville = document.querySelector('.cols')?.dataset.ville;
  let liste = ville ? TOUS.filter((d) => d[1] === ville) : TOUS;
  // il faut assez de cartes pour que la boucle verticale reste continue
  while (liste.length < 4) liste = liste.concat(liste);
  const moitie = Math.ceil(liste.length / 2);
  const A = liste.slice(0, moitie);
  const B = liste.slice(moitie).concat(liste.slice(0, Math.max(0, moitie - (liste.length - moitie))));
  const card = ([f, city, gen]) =>
    `<div class="kard"><img src="assets/photos/${f}.jpg" alt="" loading="lazy"><span class="loc">${PIN}${city}</span><span class="gen">${gen}</span></div>`;
  const fill = (id, list) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = list.map(card).join('') + list.map(card).join('');
  };
  fill('col-a', A); fill('col-b', B);
})();

/* Un seul écouteur de défilement pour tout ce qui suit la position :
   playhead, BPM, VU-mètre, jauge de lecture, parallaxe, lien actif. */
(function () {
  const secs = [...document.querySelectorAll('section[id]')];
  const links = [...document.querySelectorAll('#nav a')];
  const head = document.getElementById('head');
  const bpm = document.getElementById('bpm');
  const vu = document.getElementById('vu');
  const rail = document.querySelector('.rail');
  const top = document.querySelector('.top');
  const cols = document.querySelector('.cols');
  const marks = () => [...document.querySelectorAll('.rail-tk .marks i')];

  let last = window.scrollY, vitesse = 0, pending = false;

  const frame = () => {
    pending = false;
    const y = window.scrollY;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const p = max > 0 ? Math.min(Math.max(y / max, 0), 1) : 0;

    // vitesse lissée, normalisée sur ~60 px par frame
    const brut = Math.min(Math.abs(y - last) / 60, 1);
    vitesse += (brut - vitesse) * (brut > vitesse ? 0.6 : 0.12);
    last = y;

    if (head) head.style.top = (p * 100).toFixed(2) + '%';
    if (bpm) bpm.textContent = Math.round(112 + p * 28);
    if (top) {
      top.style.setProperty('--p', p.toFixed(4));
      top.classList.toggle('compact', y > 90);
    }
    if (!REDUCED) {
      if (vu) vu.style.setProperty('--v', vitesse.toFixed(3));
      if (rail) rail.classList.toggle('hot', vitesse > 0.25);
      if (cols) cols.style.setProperty('--par', (Math.min(y, 900) * -0.06).toFixed(1) + 'px');
    }

    if (secs.length) {
      let cur = secs[0];
      for (const s of secs) if (s.getBoundingClientRect().top <= 140) cur = s;
      links.forEach((a) => a.classList.toggle('on', a.getAttribute('href') === '#' + cur.id));
      const idx = secs.indexOf(cur);
      marks().forEach((m, i) => m.classList.toggle('on', i === idx));
    }

    // le VU redescend tout seul quand le défilement s'arrête
    if (vitesse > 0.01 && !REDUCED) schedule();
  };
  const schedule = () => { if (!pending) { pending = true; requestAnimationFrame(frame); } };

  document.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  frame();
})();

/* Titres : découpe en mots pour les faire monter un par un.
   On parcourt les nœuds enfants afin de conserver les <br> d'origine. */
(function () {
  if (REDUCED) return;
  document.querySelectorAll('.big').forEach((h) => {
    if (h.querySelector('.w')) return;
    const sortie = document.createDocumentFragment();
    let i = 0;

    [...h.childNodes].forEach((noeud) => {
      if (noeud.nodeType === 1 && noeud.tagName === 'BR') {
        sortie.appendChild(document.createElement('br'));
        return;
      }
      const texte = (noeud.textContent || '').trim();
      if (!texte) return;
      texte.split(/\s+/).forEach((mot, k, tous) => {
        const w = document.createElement('span');
        w.className = 'w';
        w.style.setProperty('--i', i++);
        const inner = document.createElement('i');
        inner.textContent = mot;
        w.appendChild(inner);
        sortie.appendChild(w);
        if (k < tous.length - 1) sortie.appendChild(document.createTextNode(' '));
      });
    });

    h.textContent = '';
    h.appendChild(sortie);
    h.classList.add('split');
    h.classList.add('rv'); // pour que l'observateur le déclenche
  });
})();

/* Inclinaison magnétique des cartes — transform uniquement */
(function () {
  if (REDUCED || !window.matchMedia('(hover:hover)').matches) return;
  const AMPL = 7;
  document.querySelectorAll('.crate, .kard').forEach((el) => {
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      el.classList.add('tilting');
      el.style.setProperty('--ry', (x * AMPL).toFixed(2) + 'deg');
      el.style.setProperty('--rx', (-y * AMPL).toFixed(2) + 'deg');
    });
    el.addEventListener('pointerleave', () => {
      el.classList.remove('tilting');
      el.style.removeProperty('--rx');
      el.style.removeProperty('--ry');
    });
  });
})();

/* Carrousel */
(function () {
  const box = document.getElementById('crates');
  if (!box) return;
  const step = () => Math.min(box.clientWidth * 0.8, 620);
  const beh = REDUCED ? 'auto' : 'smooth';
  document.getElementById('prev')?.addEventListener('click', () => box.scrollBy({ left: -step(), behavior: beh }));
  document.getElementById('next')?.addEventListener('click', () => box.scrollBy({ left: step(), behavior: beh }));
})();

/* Le rail devient un index de pistes cliquable */
(function () {
  const tk = document.querySelector('.rail-tk');
  const secs = [...document.querySelectorAll('section[id]')];
  if (!tk || !secs.length) return;

  // autant de repères que de sections : le rail ne peut plus se désynchroniser
  const marques = tk.querySelector('.marks');
  if (marques) {
    marques.innerHTML = secs.map(() => '<i></i>').join('');
  }

  const nav = document.createElement('div');
  nav.className = 'rail-nav';
  secs.forEach((sec) => {
    const titre = sec.querySelector('.slate .ttl')?.textContent.trim() || sec.id.toUpperCase();
    const b = document.createElement('button');
    b.type = 'button';
    b.dataset.cible = sec.id;
    b.setAttribute('aria-label', 'Aller à ' + titre);
    b.title = sec.id.toUpperCase() + ' — ' + titre;
    b.addEventListener('click', () => {
      sec.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth', block: 'start' });
    });
    nav.appendChild(b);
  });
  tk.appendChild(nav);
})();

/* Volet à l'entrée des visuels de section */
(function () {
  if (REDUCED) return;
  document.querySelectorAll('.crate .ph img, .roster img, .out img').forEach((img) => img.classList.add('wipe'));
})();

/* Révélations + ardoises + compteurs — un seul observateur */
(function () {
  const targets = [...document.querySelectorAll('.rv, .rvg, .slate, [data-count], .wipe')];
  const reveal = (el) => {
    el.classList.add('in');
    if (el.hasAttribute('data-count')) runCount(el);
    // le volet rend la main : sans ça son transform bloquerait le zoom au survol
    if (el.classList.contains('wipe')) {
      setTimeout(() => el.classList.remove('wipe', 'in'), 1000);
    }
  };
  function runCount(el) {
    const target = parseInt(el.dataset.count, 10);
    const suffix = el.dataset.suffix || '';
    if (REDUCED) { el.textContent = target + suffix; return; }
    const t0 = performance.now(), dur = 1000;
    const tick = (now) => {
      const p = Math.min((now - t0) / dur, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }
  if (REDUCED || !('IntersectionObserver' in window)) { targets.forEach(reveal); return; }
  setTimeout(() => targets.forEach((el) => el.classList.contains('in') || reveal(el)), 2800);
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { reveal(e.target); io.unobserve(e.target); } });
  }, { threshold: 0.14, rootMargin: '0px 0px -50px 0px' });
  targets.forEach((el) => io.observe(el));
})();
