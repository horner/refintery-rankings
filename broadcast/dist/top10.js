'use strict';

(() => {
  const $ = (id) => document.getElementById(id);
  const state = { data: null, selected: 0, cycle: null, exporting: false, statusTimer: null, hashPrefix: 'team' };
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  const num = (value, places = 0) => Number.isFinite(Number(value)) && value !== null && value !== '' ? Number(value).toLocaleString('en-US', { minimumFractionDigits: places, maximumFractionDigits: places }) : '—';
  const date = (value) => /^\d{4}-\d{2}-\d{2}$/.test(String(value)) ? new Date(`${value}T12:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'date not recorded';
  function safeUrl(value) {
    try {
      const url = new URL(value);
      return ['https:', 'http:'].includes(url.protocol) ? url.href : '';
    } catch { return ''; }
  }
  function asset(value) {
    return typeof value === 'string' && /^assets\/[a-zA-Z0-9_./-]+$/.test(value) && !value.split('/').includes('..') ? value : '';
  }
  const external = (url, label) => safeUrl(url) ? `<a href="${esc(safeUrl(url))}" target="_blank" rel="noopener noreferrer">${esc(label)} ↗</a>` : '';
  const selected = () => state.data.top10[state.selected];
  const schoolLabel = (team) => String(team.school || team.name).split(' / ')[0].replace(/\s*\(community team\)$/, '');
  const standing = (team) => state.data.standings?.find((item) => Number(item.number) === Number(team.number)) || {};
  const matchFor = (team) => state.data.matchHighlights?.teams?.find((item) => item.program === 'FRC' && Number(item.number) === Number(team.number))?.main || standing(team).closestMatch;
  const thumbnailFor = (match) => asset(state.data.videoThumbnails?.[match?.videoUrl]?.file);
  function logoFor(team, kind = 'team') {
    const logo = team.logos?.[kind];
    return asset(state.data.displayAssets?.[logo?.file]?.file || logo?.file);
  }
  const evidenceDate = (value) => !value ? 'Undated source' : /^\d{4}-\d{2}-\d{2}$/.test(String(value)) ? date(value) : String(value).replace(/^(\d{4})-(\d{4})$/, '$1–$2');
  const evidenceLine = (person) => `${evidenceDate(person.date)} · ${person.status || 'Status not recorded'}`;
  function peopleFor(team) {
    const students = team.students || [];
    const representatives = team.representatives || [];
    const student = students.find((person) => person.name === team.spotlight?.name) || students[0] || representatives.find((person) => /student/i.test(person.role)) || representatives[0];
    const adult = team.adults?.[0];
    return [
      { label: student && !/student/i.test(student.role) && !students.includes(student) ? 'Team representative' : 'Student / team representative', person: student, gap: 'Student captain not verified.' },
      { label: 'Adult / mentor', person: adult, gap: 'Adult coach or spokesperson not verified.' },
    ];
  }
  function logoHtml(team, kind) {
    const logo = team.logos?.[kind];
    const file = logoFor(team, kind);
    const label = kind === 'school' ? 'School / organization' : 'Robotics team';
    return `<figure class="identity-mark"><div class="mark-frame${logo?.background === 'dark' ? ' dark-logo' : ''}">${file ? `<img src="${esc(file)}" alt="${esc(logo?.label || `${kind === 'school' ? team.school : team.name} logo`)}" decoding="async">` : '<span>Logo not verified</span>'}</div><figcaption>${label}</figcaption></figure>`;
  }
  function peopleHtml(team) {
    const cards = peopleFor(team).map(({ label, person, gap }) => `<div class="person-summary"><h4>${esc(label)}</h4>${person ? `<p><strong>${esc(person.name)}</strong><span class="person-role">${esc(person.role)}</span></p><p class="person-evidence">${esc(evidenceLine(person))}${external(person.sourceUrls?.find(safeUrl), 'Source')}</p>` : `<p class="person-gap">${esc(gap)}</p>`}</div>`).join('');
    const groups = [['Students', team.students], ['Adults / mentors', team.adults], ['Representatives', team.representatives]];
    const full = groups.filter(([, people]) => people?.length).map(([label, people]) => `<section><h4>${label}</h4>${people.map((person) => `<article class="person-detail"><h5>${esc(person.name)}</h5><p>${esc(person.role)}</p><p class="person-evidence">${esc(evidenceLine(person))}<br>${esc(person.season || '')}${person.dateBasis ? `<br>${esc(person.dateBasis)}` : ''}</p><p>${esc(person.note || '')}</p><div class="person-sources">${(person.sourceUrls || []).map((url, i) => external(url, `Source ${i + 1}`)).join('')}</div></article>`).join('')}</section>`).join('');
    const credits = ['school', 'team'].map((kind) => { const logo = team.logos?.[kind]; return logo ? `<p><strong>${kind === 'school' ? 'School / organization' : 'Robotics team'} mark:</strong> ${esc(logo.label)}. ${esc(logo.note || '')} ${logo.retrievedDate ? `Retrieved ${esc(date(logo.retrievedDate))}.` : ''} ${external(logo.pageUrl || logo.sourceUrl, 'Logo source')}</p>` : ''; }).join('');
    return `<section class="people"><h3>PEOPLE IN THE RESEARCH</h3><div class="people-summary">${cards}</div><p class="people-caution">Published evidence; current appointments are not confirmed.</p><details class="people-details"><summary>All people, evidence notes &amp; logo credits</summary><div>${full}${team.gaps?.length ? `<section><h4>Research gaps</h4><ul>${team.gaps.map((gap) => `<li>${esc(gap)}</li>`).join('')}</ul></section>` : ''}<section><h4>Logo credits</h4>${credits}</section></div></details></section>`;
  }
  function announce(message) {
    clearTimeout(state.statusTimer);
    $('status').textContent = message;
    state.statusTimer = setTimeout(() => { $('status').textContent = ''; }, 6000);
  }
  function renderRows() {
    $('ranking-rows').innerHTML = state.data.top10.map((team, index) => `<button type="button" class="rank-row" data-team="${index}" aria-current="${index === state.selected}" aria-label="Regional power rank ${esc(team.rank)}, team ${esc(team.number)}, ${esc(team.name)}, ${esc(team.school)}, ${esc(team.city)}, EPA ${num(team.epa, 2)}"><span class="rank">${String(team.rank).padStart(2, '0')}</span><span class="row-marks" aria-hidden="true">${['school', 'team'].map((kind) => logoFor(team, kind) ? `<img class="${team.logos?.[kind]?.background === 'dark' ? 'dark-logo' : ''}" src="${esc(logoFor(team, kind))}" alt="">` : '<span></span>').join('')}</span><span class="team-copy"><span class="school-name">${esc(schoolLabel(team))}</span><span class="team-name">${esc(team.name)} · ${esc(team.number)}</span></span><span class="epa">${num(team.epa, 2)}</span></button>`).join('');
  }
  function renderSpotlight() {
    const team = selected();
    const stats = standing(team);
    const match = matchFor(team);
    const thumbnail = thumbnailFor(match);
    const video = safeUrl(match?.videoUrl);
    const record = stats.record ? `${num(stats.record.wins)}–${num(stats.record.losses)}–${num(stats.record.ties)}` : '—';
    const district = stats.district?.rank ? `#${num(stats.district.rank)}` : '—';
    const replay = match ? `<div class="replay-heading"><h3>CLOSEST FINISH / REPLAY</h3><span>Final alliance scores</span></div>${video && thumbnail ? `<a class="replay-image-link" href="${esc(video)}" target="_blank" rel="noopener noreferrer" aria-label="Watch ${esc(team.name)} in ${esc(match.eventName)}, ${esc(match.matchLabel)} (opens YouTube)"><img class="replay-image" src="${esc(thumbnail)}" alt="Replay thumbnail for ${esc(match.videoTitle || `${match.eventName}, ${match.matchLabel}`)}" decoding="async"><span class="play-cta"><b aria-hidden="true">▶</b> WATCH THE MATCH ↗</span></a>` : `<div class="no-replay"><strong>${video ? 'Match replay available' : 'Match result preserved'}</strong><p>${video ? external(video, 'Watch the match') : 'A verified replay is not available for this match.'}</p></div>`}<div class="match-caption"><p>${esc(match.eventName)}<br>${esc(match.phase)} · ${esc(match.matchLabel)} · ${esc(match.dateLabel || date(match.playedDate))}</p><div class="match-score"><span class="red">${num(match.redScore)}</span>–<span class="blue">${num(match.blueScore)}</span><small>Team ${esc(team.number)}: ${esc(match.teamAlliance)} · ${esc(match.outcome)}</small></div></div>` : '<div class="no-replay"><strong>Replay research in progress</strong><p>No verified match replay is included for this team.</p></div>';
    $('spotlight').innerHTML = `<p class="spotlight-kicker">POWER RANK ${esc(team.rank)} / TEAM ${esc(team.number)}</p><div class="identity"><div class="identity-copy"><h2 id="team-title">${esc(team.school)}</h2><p class="team-school">${esc(team.name)} · Team ${esc(team.number)}<br>${esc(team.city)}, Indiana</p></div><div class="identity-marks">${logoHtml(team, 'school')}${logoHtml(team, 'team')}</div></div><div class="stats"><div class="stat"><strong class="stat-value">${num(team.epa, 2)}</strong><span class="stat-label">Statbotics EPA · 2026</span></div><div class="stat"><strong class="stat-value">${record}</strong><span class="stat-label">2026 season W–L–T</span></div><div class="stat"><strong class="stat-value">${district}</strong><span class="stat-label">FIRST IN district${stats.district?.points != null ? ` · ${num(stats.district.points)} pts` : ''}</span></div></div>${peopleHtml(team)}<div class="replay">${replay}</div><div class="spotlight-links"><a class="back-to-rankings" href="#rankings">↑ Back to the Top 10</a>${external(team.profileUrl || stats.links?.statbotics, 'EPA source')}${external(stats.links?.tba || team.sourceUrls?.find((url) => url.includes('thebluealliance.com')), 'Season results')}${match ? external(match.officialUrl, 'Official match') : ''}<a href="index.html#team/${esc(team.number)}">Full team profile ↗</a></div>`;
    document.querySelectorAll('[data-team]').forEach((row) => row.setAttribute('aria-current', String(Number(row.dataset.team) === state.selected)));
    document.title = `${team.school} · Power Top 10 · The REFINERY`;
  }
  function stopCycle(message = '') {
    if (!state.cycle) return;
    clearInterval(state.cycle);
    state.cycle = null;
    $('cycle').setAttribute('aria-pressed', 'false');
    $('cycle').textContent = 'Auto-cycle: off';
    if (message) announce(message);
  }
  function selectTeam(index, { automatic = false, updateHash = true, prefix = state.hashPrefix } = {}) {
    if (!state.data) return;
    if (!automatic) stopCycle();
    state.selected = (index + state.data.top10.length) % state.data.top10.length;
    state.hashPrefix = prefix;
    renderSpotlight();
    const keepSection = automatic && location.hash && !/^#(?:team|spotlight)\/\d+$/.test(location.hash);
    if (updateHash && !keepSection) history.replaceState(null, '', `#${prefix}/${selected().number}`);
    if (!automatic) announce(`Power rank ${selected().rank}: ${selected().name}, team ${selected().number}.`);
  }
  function applyHash({ initial = false } = {}) {
    const match = location.hash.match(/^#(team|spotlight)\/(\d+)$/);
    if (!match || !state.data) return;
    const index = state.data.top10.findIndex((team) => String(team.number) === match[2]);
    if (index < 0) {
      announce(`Team ${match[2]} is outside this Power Top 10. See the complete standings for all 13 teams.`);
      return;
    }
    state.hashPrefix = match[1];
    state.selected = index;
    if (!initial) { stopCycle(); renderSpotlight(); }
    if (match[1] === 'spotlight' && window.matchMedia('(max-width: 900px)').matches) requestAnimationFrame(() => $('spotlight').scrollIntoView({ block: 'start', behavior: 'instant' }));
  }
  function toggleCycle() {
    if (state.cycle) { stopCycle('Auto-cycle stopped.'); return; }
    if (document.hidden) return;
    $('cycle').setAttribute('aria-pressed', 'true');
    $('cycle').textContent = 'Auto-cycle: 12 sec';
    state.cycle = setInterval(() => selectTeam(state.selected + 1, { automatic: true }), 12000);
    announce('Auto-cycle enabled. Advances every 12 seconds. Interacting with the page stops it.');
  }
  async function toggleFullscreen() {
    stopCycle();
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (document.fullscreenEnabled !== false && $('broadcast').requestFullscreen) await $('broadcast').requestFullscreen();
      else announce('Full screen is unavailable in this browser. You can use the browser’s full screen or landscape view.');
    } catch { announce('The browser could not enter full screen. Use its full screen command or landscape view.'); }
  }

  // Draw a dedicated 1920×1080 graphic rather than stretching a phone screenshot.
  // Only same-origin, checked-in images are used, so the canvas stays exportable.
  async function exportPng() {
    if (state.exporting || !state.data) return;
    stopCycle();
    state.exporting = true;
    $('export').disabled = true;
    $('export').textContent = 'Preparing PNG…';
    const team = selected();
    const stats = standing(team);
    const match = matchFor(team);
    try {
      await document.fonts.ready;
      await Promise.all([document.fonts.load('800 66px "Barlow Condensed"'), document.fonts.load('700 30px "Barlow Condensed"'), document.fonts.load('500 22px Inter')]);
      const loadImage = (file) => new Promise((resolve) => {
        if (!asset(file)) { resolve(null); return; }
        const image = new Image();
        image.onload = () => resolve(image);
        image.onerror = () => resolve(null);
        image.src = file;
      });
      const [thumbnail, schoolLogo, teamLogo] = await Promise.all([loadImage(thumbnailFor(match)), loadImage(logoFor(team, 'school')), loadImage(logoFor(team, 'team'))]);
      const rowLogos = await Promise.all(state.data.top10.map((item) => Promise.all(['school', 'team'].map((kind) => loadImage(logoFor(item, kind))))));
      const canvas = document.createElement('canvas');
      canvas.width = 1920; canvas.height = 1080;
      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error('Canvas unavailable');
      const rectangle = (x, y, w, h, color) => { ctx.fillStyle = color; ctx.fillRect(x, y, w, h); };
      const write = (text, x, y, font, color, align = 'left') => { ctx.font = font; ctx.fillStyle = color; ctx.textAlign = align; ctx.fillText(String(text), x, y); };
      const lines = (text, x, y, width, lineHeight, maxLines, font, color) => {
        ctx.font = font; ctx.textAlign = 'left'; ctx.fillStyle = color;
        const words = String(text || '').split(/\s+/); const result = []; let line = '';
        for (const word of words) {
          if (line && ctx.measureText(`${line} ${word}`).width > width) { result.push(line); line = word; }
          else line = line ? `${line} ${word}` : word;
        }
        if (line) result.push(line);
        result.slice(0, maxLines).forEach((value, i) => ctx.fillText(value, x, y + i * lineHeight));
        return Math.min(result.length, maxLines) * lineHeight;
      };
      const imageContain = (image, x, y, w, h) => {
        rectangle(x, y, w, h, '#09283d');
        const scale = Math.min(w / image.width, h / image.height);
        const width = image.width * scale; const height = image.height * scale;
        ctx.drawImage(image, x + (w - width) / 2, y + (h - height) / 2, width, height);
      };
      rectangle(0, 0, 1920, 1080, '#f7f9fa');
      rectangle(0, 0, 1920, 76, '#0d3550'); rectangle(0, 72, 1920, 4, '#a1d18b');
      write('THE REFINERY', 48, 50, '800 36px "Barlow Condensed"', '#fff');
      write('NORTHEAST INDIANA ROBOTICS', 1872, 47, '600 19px Inter', '#a1d18b', 'right');
      write('2026 FRC / THE REGIONAL REWIND', 48, 118, '700 20px "Barlow Condensed"', '#2b7252');
      write('THE POWER TOP 10', 48, 190, '800 78px "Barlow Condensed"', '#0d3550');
      write('Last season’s EPA. This season’s baseline.', 1872, 178, '500 22px Inter', '#536072', 'right');
      write('REGIONAL POWER RANK', 58, 235, '700 18px "Barlow Condensed"', '#536072');
      write('EPA', 990, 235, '700 18px "Barlow Condensed"', '#536072', 'right');
      state.data.top10.forEach((item, index) => {
        const y = 250 + index * 69; const active = Number(item.number) === Number(team.number);
        rectangle(48, y, 968, 65, active ? '#0d3550' : '#ffffff');
        rectangle(48, y, 5, 65, active ? '#a1d18b' : '#dce4e8');
        write(String(item.rank).padStart(2, '0'), 84, y + 43, '800 37px "Barlow Condensed"', active ? '#a1d18b' : '#2b7252', 'center');
        rowLogos[index].forEach((mark, markIndex) => {
          if (!mark) return;
          const kind = markIndex === 0 ? 'school' : 'team';
          const [x, width, height] = markIndex === 0 ? [116, 58, 44] : [182, 28, 30];
          rectangle(x, y + (65 - height) / 2, width, height, item.logos?.[kind]?.background === 'dark' ? '#09283d' : '#ffffff');
          const scale = Math.min((width - 4) / mark.width, (height - 4) / mark.height);
          ctx.drawImage(mark, x + (width - mark.width * scale) / 2, y + (65 - mark.height * scale) / 2, mark.width * scale, mark.height * scale);
        });
        write(schoolLabel(item), 224, y + 31, '700 31px "Barlow Condensed"', active ? '#ffffff' : '#0f172a');
        write(`${item.name} · ${item.number}`, 225, y + 53, '500 17px Inter', active ? '#c6d5df' : '#536072');
        write(num(item.epa, 2), 990, y + 44, '700 42px "Barlow Condensed"', active ? '#ffffff' : '#0d3550', 'right');
      });
      rectangle(1052, 218, 820, 770, '#0d3550'); rectangle(1052, 218, 820, 5, '#a1d18b');
      write(`POWER RANK ${team.rank} / TEAM ${team.number}`, 1080, 258, '700 20px "Barlow Condensed"', '#a1d18b');
      const titleSize = team.school.length > 38 ? 42 : 48;
      lines(team.school, 1080, 302, 545, 43, 2, `800 ${titleSize}px "Barlow Condensed"`, '#ffffff');
      [[schoolLogo, 'school', 'SCHOOL / ORG.'], [teamLogo, 'team', 'ROBOTICS TEAM']].forEach(([logo, kind, label], index) => {
        const x = index === 0 ? 1648 : 1792;
        const width = index === 0 ? 132 : 52;
        const height = index === 0 ? 80 : 52;
        rectangle(x, 276, width, height, team.logos?.[kind]?.background === 'dark' ? '#09283d' : '#ffffff');
        if (logo) {
          const scale = Math.min((width - 10) / logo.width, (height - 10) / logo.height);
          ctx.drawImage(logo, x + (width - logo.width * scale) / 2, 276 + (height - logo.height * scale) / 2, logo.width * scale, logo.height * scale);
        } else write('UNVERIFIED', x + width / 2, 306, '700 10px "Barlow Condensed"', '#536072', 'center');
        write(label, x + width / 2, 372, '500 9px Inter', '#c6d5df', 'center');
      });
      lines(`${team.name} · Team ${team.number} · ${team.city}, Indiana`, 1080, 380, 545, 20, 1, '500 17px Inter', '#d6e2e9');
      rectangle(1080, 410, 764, 1, '#46657a'); rectangle(1080, 503, 764, 1, '#46657a');
      const statsList = [[num(team.epa, 2), 'STATBOTICS EPA · 2026'], [stats.record ? `${num(stats.record.wins)}–${num(stats.record.losses)}–${num(stats.record.ties)}` : '—', '2026 SEASON W–L–T'], [stats.district?.rank ? `#${num(stats.district.rank)}` : '—', `FIRST IN DISTRICT${stats.district?.points != null ? ` · ${num(stats.district.points)} PTS` : ''}`]];
      statsList.forEach(([value, label], index) => { const x = 1080 + index * 263; write(value, x, 465, '700 48px "Barlow Condensed"', index ? '#fff' : '#a1d18b'); write(label, x, 487, '500 12px Inter', '#c6d5df'); });
      peopleFor(team).forEach(({ label, person, gap }, index) => {
        const x = 1080 + index * 395;
        write(label.toUpperCase(), x, 526, '700 16px "Barlow Condensed"', '#a1d18b');
        if (person) {
          write(person.name, x, 552, '700 26px "Barlow Condensed"', '#ffffff');
          lines(person.role, x, 575, 365, 18, 3, '500 14px Inter', '#ffffff');
          const source = person.sourceUrls?.find(safeUrl);
          lines(`${evidenceLine(person)}${source ? ` · Source: ${new URL(source).hostname.replace(/^www\./, '')}` : ''}`, x, 635, 365, 16, 3, '500 12px Inter', '#c6d5df');
        } else lines(gap, x, 552, 365, 20, 3, '500 16px Inter', '#d6e2e9');
      });
      write('Published evidence; current appointments are not confirmed. Full notes & credits on the website.', 1080, 684, '500 12px Inter', '#c6d5df');
      write('CLOSEST FINISH / REPLAY', 1080, 710, '700 23px "Barlow Condensed"', '#ffffff');
      if (thumbnail) imageContain(thumbnail, 1080, 724, 764, 150);
      else { rectangle(1080, 724, 764, 150, '#09283d'); write('MATCH RESULT & SOURCES ON THE SITE', 1462, 805, '700 29px "Barlow Condensed"', '#a1d18b', 'center'); }
      if (match) {
        rectangle(1094, 827, 244, 34, '#a1d18b'); write('WATCH ON THE WEBSITE ↗', 1107, 851, '700 22px "Barlow Condensed"', '#0d3550');
        lines(`${match.eventName} · ${match.phase} · ${match.matchLabel}`, 1080, 905, 580, 23, 2, '500 17px Inter', '#d6e2e9');
        write(`${num(match.redScore)}–${num(match.blueScore)}`, 1844, 915, '700 37px "Barlow Condensed"', '#ffffff', 'right');
        write(`Team ${team.number}: ${match.teamAlliance} · ${match.outcome}`, 1844, 940, '500 13px Inter', '#c6d5df', 'right');
        write('Final alliance scores · includes penalties', 1080, 969, '500 14px Inter', '#c6d5df');
      }
      write(`EPA snapshot ${date(state.data.edition.rankingsDate)} · Research ${date(state.data.edition.researchDate)} · Historical 2026 results`, 48, 1020, '500 17px Inter', '#536072');
      write('EPA power order ≠ official district standings. Sources: Statbotics · FIRST Indiana · The Blue Alliance', 48, 1050, '500 17px Inter', '#536072');
      const blob = await new Promise((resolve, reject) => canvas.toBlob((value) => value ? resolve(value) : reject(new Error('PNG unavailable')), 'image/png'));
      const objectUrl = URL.createObjectURL(blob); const link = document.createElement('a');
      link.href = objectUrl; link.download = `refinery-power-top10-2026-team-${team.number}.png`;
      document.body.append(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(objectUrl), 30000);
      announce('Saved a 1920 × 1080 PNG of the Power Top 10 and selected team.');
    } catch (error) {
      console.error('Top 10 PNG export failed:', error);
      const fallback = document.createElement('a');
      fallback.href = `assets/share/team-${Number(team.number)}.png`;
      fallback.download = `refinery-team-${Number(team.number)}.png`;
      document.body.append(fallback); fallback.click(); fallback.remove();
      announce('The full-board PNG could not finish. Downloading the existing team graphic instead.');
    } finally {
      state.exporting = false; $('export').disabled = false; $('export').innerHTML = 'Save PNG <span aria-hidden="true">↓</span>';
    }
  }

  $('previous').addEventListener('click', () => selectTeam(state.selected - 1));
  $('next').addEventListener('click', () => selectTeam(state.selected + 1));
  $('cycle').addEventListener('click', toggleCycle);
  $('fullscreen').addEventListener('click', toggleFullscreen);
  $('export').addEventListener('click', exportPng);
  $('ranking-rows').addEventListener('click', (event) => {
    const row = event.target.closest('[data-team]');
    if (!row) return;
    selectTeam(Number(row.dataset.team), { prefix: 'team' });
    if (matchMedia('(max-width: 900px)').matches) $('spotlight').scrollIntoView({ block: 'start', behavior: 'instant' });
  });
  $('spotlight').addEventListener('pointerenter', () => stopCycle());
  $('spotlight').addEventListener('focusin', () => stopCycle());
  document.addEventListener('pointerdown', (event) => { if (!event.target.closest('#cycle')) stopCycle(); }, { passive: true });
  document.addEventListener('keydown', (event) => {
    if (event.target.isContentEditable || /^(INPUT|SELECT|TEXTAREA)$/.test(event.target.tagName)) return;
    if (event.target.closest('#cycle') && [' ', 'Enter'].includes(event.key)) return;
    stopCycle();
    if (!state.data || event.altKey || event.ctrlKey || event.metaKey) return;
    if (['ArrowLeft', 'ArrowUp', 'ArrowRight', 'ArrowDown'].includes(event.key)) {
      event.preventDefault();
      selectTeam(state.selected + (['ArrowLeft', 'ArrowUp'].includes(event.key) ? -1 : 1));
    }
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopCycle(); });
  document.addEventListener('fullscreenchange', () => { $('fullscreen').innerHTML = document.fullscreenElement ? 'Exit full screen <span aria-hidden="true">⤢</span>' : 'Full screen <span aria-hidden="true">⤢</span>'; });
  window.addEventListener('hashchange', () => applyHash());
  fetch('data.json').then((response) => {
    if (!response.ok) throw new Error(`Data request failed: ${response.status}`);
    return response.json();
  }).then((data) => {
    if (!Array.isArray(data.top10) || data.top10.length !== 10 || !data.edition) throw new Error('The ten-team ranking snapshot is unavailable.');
    state.data = data;
    applyHash({ initial: true });
    renderRows(); renderSpotlight();
    $('snapshot-note').textContent = `EPA snapshot ${date(data.edition.rankingsDate)} · Research ${date(data.edition.researchDate)} · Historical 2026 results`;
    $('edition-note').textContent = data.edition.note || '';
    $('scope-note').textContent = data.scope?.note || '';
    ['previous', 'next', 'cycle', 'export'].forEach((id) => { $(id).disabled = false; });
    $('broadcast').setAttribute('aria-busy', 'false');
  }).catch((error) => {
    console.error('Top 10 load failed:', error);
    $('ranking-rows').innerHTML = '<p class="loading">The ranking data could not load. Refresh this page or <a href="index.html#standings">open the standings</a>.</p>';
    $('spotlight').innerHTML = '<p class="loading">Serve this page from a local web server or the site to load its shared data.</p>';
    $('broadcast').setAttribute('aria-busy', 'false');
    announce('The Top 10 could not load.');
  });
})();
