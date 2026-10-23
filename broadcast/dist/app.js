'use strict';

(() => {
  // Preserve links to the original broadcast/spotlight view in the separate display.
  const legacyDisplayRoute = () => {
    const spotlight = location.hash.match(/^#spotlight\/(\d+)$/);
    if (!spotlight && !['#board', '#broadcast'].includes(location.hash)) return false;
    const url = new URL('top10.html', location.href);
    url.hash = spotlight ? `#team/${spotlight[1]}` : '';
    location.replace(url.href);
    return true;
  };
  if (legacyDisplayRoute()) return;
  if (location.hash === '#season-preview') history.replaceState(null, '', '#schedule');
  const $ = (id) => document.getElementById(id);
  const state = { data: null, sort: 'district', dnfLimit: 24 };
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const safeUrl = (value) => { try { const url = new URL(value, location.href); return ['https:', 'http:', 'mailto:'].includes(url.protocol) ? esc(url.href) : '#'; } catch { return '#'; } };
  const ext = (url, label, cls = '') => `<a${cls ? ` class="${cls}"` : ''} href="${safeUrl(url)}" target="_blank" rel="noopener">${esc(label)}</a>`;
  const num = (value, decimals = 0) => Number.isFinite(Number(value)) && value !== null ? Number(value).toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) : '—';
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const parts = (iso) => { const [y, m, d] = String(iso).split('-').map(Number); return { y, m, d }; };
  const shortDate = (iso) => { if (!/^\d{4}-\d{2}-\d{2}$/.test(String(iso))) return String(iso); const { y, m, d } = parts(iso); return `${MONTHS[m - 1]} ${d}, ${y}`; };
  const dateRange = (start, end) => {
    const a = parts(start), b = parts(end || start);
    if (start === end || !end) return shortDate(start);
    if (a.y === b.y && a.m === b.m) return `${MONTHS[a.m - 1]} ${a.d}–${b.d}, ${a.y}`;
    return `${MONTHS[a.m - 1]} ${a.d} – ${MONTHS[b.m - 1]} ${b.d}, ${b.y}`;
  };
  const today = () => { const n = new Date(); return `${n.getFullYear()}-${String(n.getMonth() + 1).padStart(2, '0')}-${String(n.getDate()).padStart(2, '0')}`; };
  const utc = (iso) => { const { y, m, d } = parts(iso); return Date.UTC(y, m - 1, d); };
  const daysUntil = (iso) => Math.round((utc(iso) - utc(today())) / 86400000);
  const record = (r) => `${r.wins}-${r.losses}${r.ties ? `-${r.ties}` : ''}`;
  const recordText = (text) => String(text || '').replace(/-0$/, '');
  const ordinal = (n) => { const suffix = ['th', 'st', 'nd', 'rd'], v = n % 100; return `${n}${suffix[(v - 20) % 10] || suffix[v] || suffix[0]}`; };
  // Plain-language playoff results. In the 8-alliance double-elimination bracket the round a team
  // goes out in fixes its finish: round 2 = 7th–8th, round 3 = 5th–6th, round 4 = 4th, round 5 = 3rd.
  const FINISH = { 2: 'Tied 7th (out in playoff round 2)', 3: 'Tied 5th (out in playoff round 3)', 4: '4th place', 5: '3rd place' };
  const playoffResult = (p) => {
    if (!p) return 'Not picked for playoffs';
    if (p.result === 'Won event') return 'Won the event';
    if (p.result === 'Finalist') return 'Runner-up (lost in the finals)';
    const round = Number((p.result.match(/round (\d)/) || [])[1]);
    return FINISH[round] || 'Reached playoffs';
  };
  const playoffRole = (p) => {
    if (!p?.alliance) return '';
    const seed = `#${p.alliance} alliance`;
    return p.role === 'Captain' ? `Captain of the ${seed}` : p.role === 'Backup' ? `Backup robot for the ${seed}` : `${p.role.toLowerCase().replace(/^./, (c) => c.toUpperCase())} of the ${seed}`;
  };

  // Small WebP copies are for display; the verified originals stay linked in the credits.
  const logo = (logos, number) => {
    const mark = logos?.team?.file ? logos.team : logos?.school?.file ? logos.school : null;
    if (!mark) return `<span class="logo placeholder" aria-hidden="true">${esc(number)}</span>`;
    const shown = state.data.displayAssets?.[mark.file];
    return `<span class="logo${mark.background === 'dark' ? ' dark-logo' : ''}"><img src="${esc(shown?.file || mark.file)}" alt="" loading="lazy" decoding="async"${shown ? ` width="${shown.width}" height="${shown.height}"` : ''}></span>`;
  };
  const standingsLogos = (t) => {
    const marks = ['school', 'team'].map((kind) => {
      const mark = t.logos?.[kind];
      if (!mark?.file || mark.status !== 'verified') return '';
      const shown = state.data.displayAssets?.[mark.file];
      const label = `${kind === 'school' ? 'School' : 'Team'}: ${mark.label}`;
      return `<span class="logo ${kind}-mark${mark.background === 'dark' ? ' dark-logo' : ''}"><img src="${esc(shown?.file || mark.file)}" alt="${esc(label)}" title="${esc(label)}" loading="lazy" decoding="async"${shown ? ` width="${shown.width}" height="${shown.height}"` : ''}></span>`;
    }).join('');
    return `<span class="standings-logos">${marks || `<span class="logo placeholder" aria-hidden="true">${esc(t.number)}</span>`}</span>`;
  };
  const identityLogos = (t) => `<div class="profile-logos">${['school', 'team'].map((kind) => {
    const mark = t.logos?.[kind];
    if (!mark?.file) return '';
    const file = state.data.displayAssets?.[mark.file]?.file || mark.file;
    return `<figure><span class="logo${mark.background === 'dark' ? ' dark-logo' : ''}"><img src="${safeUrl(file)}" alt="${esc(mark.label)}" loading="lazy" decoding="async"></span><figcaption>${kind === 'school' ? 'School / organization' : 'Team'}</figcaption></figure>`;
  }).join('')}</div>`;
  const personEvidence = (p) => {
    const status = p.status || '';
    const qualifiers = [['historical', 'Historical evidence'], ['retrospective', 'Retrospective account'], ['indexed', 'Indexed evidence'], ['self reported', 'Self-reported']].filter(([term]) => status.includes(term)).map(([, label]) => label);
    return [p.date ? `Source dated ${shortDate(p.date)}` : 'Undated source', p.season ? `Season ${p.season}` : '', ...qualifiers, p.note, p.dateBasis].filter(Boolean).map(esc).join(' · ');
  };
  const handle = (url) => url.replace(/\/+$/, '').split('/').pop().replace(/^@/, '');
  const follow = (links) => links?.length ? `<ul class="link-list follow">${links.map((l) => `<li>${ext(l.url, l.type === 'Website' ? 'Team website' : ['Instagram', 'X', 'YouTube', 'TikTok'].includes(l.type) ? `${l.type} @${handle(l.url)}` : l.type, 'text-link')}</li>`).join('')}</ul>` : '';
  const honorClass = (b) => /winner/i.test(b) ? 'trophy' : /World/.test(b) ? 'worlds' : '';
  const photo = (id) => state.data.photos.find((p) => p.id === id);
  const replayThumbnail = (match, teamName) => {
    const thumbnail = state.data.videoThumbnails?.[match?.videoUrl];
    return thumbnail ? `<a class="replay-thumbnail" href="${safeUrl(match.videoUrl)}" target="_blank" rel="noopener" aria-label="Watch ${esc(teamName)}: ${esc(match.eventName)}, ${esc(match.matchLabel)}"><img src="${safeUrl(thumbnail.file)}" width="${thumbnail.width}" height="${thumbnail.height}" alt="Replay preview: ${esc(match.videoTitle || match.matchLabel)}" loading="lazy" decoding="async"><span>▶ Watch replay</span></a>` : '';
  };

  function renderStats() {
    const s = state.data.seasonSummary;
    const ftcCount = state.data.ftc.teams.length + state.data.ftc.newTeams.length;
    const stats = [[s.teams, 'FRC teams'], [s.eventTitles, 'Event titles in 2026'], [s.worldsTeams.length, 'World Championship teams'], [s.awards, 'Judged awards'], [ftcCount, 'FTC teams to follow']];
    $('stat-bar').innerHTML = stats.map(([value, label]) => `<div><dt>${esc(label)}</dt><dd data-count="${Number(value)}">${esc(num(value))}</dd></div>`).join('');
  }

  function standingsRow(t) {
    const rank = state.sort === 'power' ? t.powerRank : t.standingsRank;
    const district = t.district.rank ? `#${t.district.rank}` : '—';
    return `<details class="team" id="team-${t.number}">
      <summary class="team-row">
        <span class="rank">${rank}</span>
        <span class="identity">${standingsLogos(t)}<span><strong class="school-name">${esc(t.school)}</strong><small class="team-secondary"><span class="team-name">${esc(t.name)}</span> <span class="team-number">· FRC ${t.number}</span></small><small class="school-city">${esc(t.city)}</small></span></span>
        <span class="stat r num">${esc(record(t.record))}<small>W-L</small></span>
        <span class="stat r district num">${district}<small>${num(t.district.points)} points</small></span>
        <span class="stat r epa num">${num(t.epa, 1)}<small>EPA</small></span>
        <span class="honors">${t.badges.map((b) => `<span class="${honorClass(b)}">${esc(b)}</span>`).join('')}</span>
        <span class="chev" aria-hidden="true"></span>
      </summary>
      <div class="team-detail" data-team="${t.number}"></div>
    </details>`;
  }

  function teamDetail(t) {
    const eventRow = (e) => `<tr class="${e.type === 'offseason' ? 'offseason' : ''}"><td>${ext(e.tbaUrl, e.shortName)}<br><small class="muted">${esc(dateRange(e.startDate, e.endDate))}</small></td><td>${ordinal(e.qualRank)}<br><small class="muted">${esc(recordText(e.qualRecord))} record</small></td><td class="${e.playoff?.result === 'Won event' ? 'won' : ''}">${esc(playoffResult(e.playoff))}${playoffRole(e.playoff) ? `<br><small class="muted">${esc(playoffRole(e.playoff))}</small>` : ''}</td></tr>`;
    const head = `<thead><tr><th>Event</th><th>${term('qualifying', 'After qualifying')}</th><th>${term('playoffs', 'Playoffs')}</th></tr></thead>`;
    const official = t.events.filter((e) => e.type !== 'offseason');
    const offseason = t.events.filter((e) => e.type === 'offseason');
    const events = `<table class="events">${head}<tbody>${official.map(eventRow).join('')}</tbody></table>${offseason.length ? `<details><summary>Offseason events (${offseason.length})</summary><table class="events">${head}<tbody>${offseason.map(eventRow).join('')}</tbody></table></details>` : ''}`;
    const awards = t.awards.length ? `<h4>Awards</h4><ul class="award-list">${t.awards.map((a) => `<li>${esc(a.award)} <span>· ${esc(a.event)}</span></li>`).join('')}</ul>` : '';
    const m = t.closestMatch;
    const closest = m ? `<h4>Closest game</h4><div class="close-game">${replayThumbnail(m, t.name)}<div>${esc(m.eventName)} · ${esc(m.matchLabel)}</div><div class="scoreline"><span class="red">${m.redScore}</span><span class="muted">–</span><span class="blue">${m.blueScore}</span></div><div class="muted">${esc(m.margin)}-point ${esc(m.outcome.toLowerCase())} on the ${esc(m.teamAlliance.toLowerCase())} alliance</div><ul class="link-list">${m.videoUrl ? `<li>${ext(m.videoUrl, 'Watch replay', 'text-link')}</li>` : ''}<li>${ext(m.officialUrl, 'Official result', 'text-link')}</li></ul></div>` : '';
    const pic = t.photos.map(photo).filter(Boolean)[0];
    const fig = pic ? `<figure class="team-photo"><img src="${esc(pic.file)}" alt="${esc(pic.caption)}" loading="lazy" width="${pic.width}" height="${pic.height}"><figcaption>${esc(pic.caption)} Photo: ${esc(pic.credit)}</figcaption></figure>` : '';
    const news = t.news.length ? `<h4>In the news</h4><ul class="news-list">${t.news.map((s) => `<li>${ext(s.url, s.title)}<small>${esc(s.outlet)} · ${esc(shortDate(s.date))}</small></li>`).join('')}</ul>` : '';
    const people = [...t.students, ...t.representatives, ...t.adults];
    const peopleHtml = people.length ? `<details open><summary>People named in public sources (${people.length})</summary><ul class="people">${people.map((p) => `<li><strong>${esc(p.name)}</strong> · ${esc(p.role)}<br><small>${personEvidence(p)} · ${p.sourceUrls.slice(0, 2).map((u, i) => ext(u, `source ${i + 1}`)).join(' · ')}</small></li>`).join('')}</ul>${t.gaps.length ? `<p class="muted">${t.gaps.map(esc).join(' ')}</p>` : ''}</details>` : '';
    const facts = `<details><summary>Team facts</summary><ul class="people"><li>Rookie year ${t.rookieYear} · ${t.seasons} seasons through 2026</li><li>${esc(t.county)} County · ${esc(t.affiliationNote)}</li><li>Indiana EPA rank ${t.stateEpaRank} of ${t.stateEpaCount} · world ${num(t.worldEpaRank)} of ${num(t.worldEpaCount)}</li><li>District points ${num(t.district.points)} · Indiana district rank ${t.district.rank} of ${t.district.teamCount}</li></ul></details>`;
    const links = `<ul class="link-list"><li>${ext(t.links.tba, 'The Blue Alliance', 'text-link')}</li><li>${ext(t.links.statbotics, 'Statbotics', 'text-link')}</li><li>${ext(t.links.first, 'FIRST profile', 'text-link')}</li>${t.links.school ? `<li>${ext(t.links.school, 'School site', 'text-link')}</li>` : ''}</ul>`;
    const followHtml = t.teamLinks?.length ? `<h4>Follow the team</h4>${follow(t.teamLinks)}` : '';
    return `<div>${identityLogos(t)}${peopleHtml}<h4>2026 season</h4>${events}${awards}${facts}</div><div>${followHtml}${closest}${fig}${news}<h4>Stats &amp; profiles</h4>${links}<p><a class="text-link page-link" href="team/${t.number}/">Full team page</a></p><p class="muted small">Interview requests: <a href="mailto:celder@bionanomics.com?subject=${encodeURIComponent(`Media request: ${t.name} (${t.number})`)}">celder@bionanomics.com</a></p></div>`;
  }

  function renderStandings() {
    const teams = [...state.data.standings].sort((a, b) => state.sort === 'power' ? a.powerRank - b.powerRank : a.standingsRank - b.standingsRank);
    $('standings-list').innerHTML = `<div class="standings-header"><span>#</span><span>School / team</span><span class="r">${term('record', 'Record')}</span><span class="r">${term('district', 'District')}</span><span class="r">${term('epa', 'EPA')}</span><span class="h-honors">2026 honors</span><span></span></div>${teams.map(standingsRow).join('')}`;
    $('standings-list').querySelectorAll('details.team').forEach((el) => el.addEventListener('toggle', () => {
      const body = el.querySelector('.team-detail');
      if (el.open && !body.innerHTML) body.innerHTML = teamDetail(state.data.standings.find((t) => t.number === Number(body.dataset.team)));
      if (el.open) history.replaceState(null, '', `#team/${body.dataset.team}`);
      else if (location.hash === `#team/${body.dataset.team}`) history.replaceState(null, '', location.pathname + location.search);
    }));
    const s = state.data.seasonSummary;
    $('standings-updated').textContent = `Final 2026 results · updated ${shortDate(s.updated)}`;
    $('standings-source').innerHTML = `Records, events and awards: ${esc(s.resultsSource)}. Ratings: ${esc(s.ratingsSource)}. District rank is among ${state.data.standings[0].district.teamCount} Indiana teams.`;
  }

  function renderHighlights() {
    const teams = state.data.standings;
    const cards = [];
    teams.filter((t) => t.titles.length).sort((a, b) => b.titles.length - a.titles.length).forEach((t) => {
      const year = 2026 - t.rookieYear + 1;
      const extra = t.worlds ? `, then reached the ${t.worlds}` : year <= 2 ? ` in just its ${year === 1 ? 'first' : 'second'} season` : '';
      cards.push({ big: `${t.titles.length}×`, title: `${t.name} (${t.number})`, text: `Won the ${t.titles.join(' and ')} district event${t.titles.length > 1 ? 's' : ''}${extra}.`, href: `#team/${t.number}` });
    });
    teams.filter((t) => t.worlds && !t.titles.length).forEach((t) => cards.push({ big: 'Worlds', title: `${t.name} (${t.number})`, text: `Earned a trip to the ${t.worlds} in Houston.`, href: `#team/${t.number}` }));
    const s = state.data.seasonSummary;
    cards.push({ big: s.awards, title: 'Judged awards', text: `Won by ${new Set(teams.filter((t) => t.awards.length).map((t) => t.number)).size} regional teams, from Innovation in Control to Rising All-Star.`, href: '#standings' });
    $('highlight-grid').innerHTML = cards.slice(0, 4).map((c) => `<a class="highlight" href="${esc(c.href)}"><span class="big">${esc(c.big)}</span><h3>${esc(c.title)}</h3><p>${esc(c.text)}</p></a>`).join('');
    const order = ['winner-banners', 'team-8742', 'robot-9431', 'judging', 'robot-9119'];
    $('gallery').innerHTML = order.map(photo).filter(Boolean).map((p) => `<figure><img src="${esc(p.file)}" alt="${esc(p.caption)}" loading="lazy" decoding="async" width="${p.width}" height="${p.height}"><figcaption>${esc(p.caption)} Photo: ${esc(p.credit)}</figcaption></figure>`).join('');
  }

  function renderFtc() {
    const { ftc, news } = state.data;
    const stories = (n) => news.stories.filter((s) => s.teams.includes(`ftc${n}`));
    const card = (t, rookie) => {
      const s = stories(t.number);
      const stats = rookie ? '<p class="muted">Rookie team for 2026–27. First matches this season.</p>' : `<div class="card-stats"><div><strong>${num(t.opr, 1)}</strong><span>Best ${term('opr', 'OPR')}, 2025–26</span></div><div><strong>${t.regionalRank}<small class="muted">/${t.regionalCount}</small></strong><span>Rank at Indiana events</span></div></div>`;
      return `<article class="card"><span class="label ${rookie ? 'new' : 'ftc'}">${rookie ? 'New this season' : 'FTC'} · ${t.number}</span><div class="identity">${logo(t.logos, t.number)}<span><strong>${esc(t.name)}</strong><small>${esc(t.school)}${t.city ? ` · ${esc(t.city)}` : ''}</small></span></div>${stats}${s.length ? `<details><summary>In the news (${s.length})</summary><ul class="news-list">${s.map((x) => `<li>${ext(x.url, x.title)}<small>${esc(x.outlet)} · ${esc(shortDate(x.date))}</small></li>`).join('')}</ul></details>` : ''}${follow(t.teamLinks)}<p><a class="text-link page-link" href="team/${t.number}/">Team page</a></p><ul class="link-list"><li>${ext(`https://ftcscout.org/teams/${t.number}`, 'FTCScout', 'text-link')}</li>${t.profileUrl ? `<li>${ext(t.profileUrl, 'FIRST profile', 'text-link')}</li>` : ''}</ul></article>`;
    };
    $('ftc-grid').innerHTML = ftc.teams.map((t) => card(t, false)).join('') + ftc.newTeams.map((t) => card(t, true)).join('');
  }

  function renderSchedule() {
    const cal = state.data.calendar;
    const now = today();
    const plusDay = (iso) => { const d = new Date(utc(iso) + 86400000); return d.toISOString().slice(0, 10).replace(/-/g, ''); };
    const google = (e) => `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(e.name)}&dates=${e.startDate.replace(/-/g, '')}/${plusDay(e.endDate)}&location=${encodeURIComponent([e.venue, e.city, e.state].filter(Boolean).join(', '))}&details=${encodeURIComponent(`${e.description ? `${e.description} ` : ''}${e.url}`)}`;
    const row = (e) => {
      const { m, d } = parts(e.startDate);
      const place = [e.venue, [e.city, e.state].filter(Boolean).join(', ')].filter(Boolean).join(' · ');
      const ftcOnly = e.program === 'FTC';
      return `<li class="${e.endDate < now ? 'past' : ''}"><div class="date-block"><span class="m">${MONTHS[m - 1]}</span><span class="d">${d}</span></div><div><span class="label${ftcOnly ? ' ftc' : ''}">${esc(e.program)} · ${esc(e.type)}${e.week ? ` · Week ${e.week}` : ''}</span><h3>${esc(e.name)}</h3><p>${esc(dateRange(e.startDate, e.endDate))}${place ? ` · ${esc(place)}` : ''}</p>${e.description ? `<p class="desc">${esc(e.description)}</p>` : ''}${e.entrants ? `<div class="region-teams"><span class="rt-label">REFINERY-region teams</span>${regionTeams(e)}</div>` : ''}<ul class="link-list"><li>${ext(e.url, 'Event details', 'text-link')}</li><li>${ext(google(e), 'Google Calendar', 'text-link')}</li></ul></div></li>`;
    };
    const draw = () => {
      const events = cal.events.filter((e) => (!state.program || e.program.includes(state.program)) && (state.showPast || e.endDate >= now));
      const months = [];
      events.forEach((e) => { const key = e.startDate.slice(0, 7); const group = months.find((g) => g.key === key) || (months.push({ key, events: [] }), months[months.length - 1]); group.events.push(e); });
      $('calendar-list').innerHTML = months.map((g) => { const { y, m } = parts(`${g.key}-01`); return `<h3 class="month">${['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][m - 1]} ${y}</h3><ol class="schedule">${g.events.map(row).join('')}</ol>`; }).join('') || '<p class="loading">No events match.</p>';
      const earlier = cal.events.filter((e) => e.endDate < now && (!state.program || e.program.includes(state.program))).length;
      $('calendar-past').hidden = !earlier;
      $('calendar-past').textContent = state.showPast ? 'Hide earlier events' : `Show earlier events (${earlier})`;
    };
    document.querySelectorAll('[data-program]').forEach((button) => button.addEventListener('click', () => {
      state.program = button.dataset.program;
      document.querySelectorAll('[data-program]').forEach((b) => b.setAttribute('aria-pressed', String(b === button)));
      draw();
    }));
    $('calendar-past').addEventListener('click', () => { state.showPast = !state.showPast; draw(); });
    draw();
    $('calendar-source').innerHTML = `Dates from ${cal.sources.map(esc).join(', ')}. Checked ${esc(shortDate(cal.retrievedDate))}. Dates can change; confirm with the event before you go.`;
    renderNextEvent(cal.events.find((e) => e.endDate >= now && e.type !== 'Kickoff'), google);
  }

  // The next event, front and center: when, where, how to watch, and which local teams are in.
  // The REFINERY-region teams entered in an event, from its posted entry list.
  function regionTeams(e, muted = 'muted') {
    const entry = e.entrants;
    if (!entry) return '';
    if (!entry.posted) {
      return e.type === 'Championship'
        ? `<p class="${muted}">Teams qualify during the season. Region qualifiers will be listed here.</p>`
        : `<p class="${muted}">Entry list not posted yet. Region teams will be listed here when it is.</p>`;
    }
    if (!entry.local.length) return `<p class="${muted}">${entry.count} teams entered; none from The REFINERY’s region yet.</p>`;
    const roster = new Map([...state.data.standings, ...state.data.ftc.teams, ...state.data.ftc.newTeams].map((t) => [t.number, t]));
    return `<ul class="entered">${entry.local.map((n) => { const t = roster.get(n); return `<li>${t ? logo(t.logos, n) : ''}<span><strong>${t?.name ? (state.data.standings.some((s) => s.number === n) ? `<a href="team/${n}/">${esc(t.name)}</a>` : esc(t.name)) : `Team ${n}`}</strong><small>${n}${t?.school ? ` · ${esc(t.school)}` : ''}</small></span></li>`; }).join('')}</ul><p class="${muted}">${entry.local.length} of ${entry.count} teams entered are from The REFINERY’s region.</p>`;
  }

  function renderNextEvent(e, google) {
    if (!e) return;
    const days = daysUntil(e.startDate);
    const live = days <= 0;
    const when = live ? 'Happening now' : days === 1 ? 'Tomorrow' : `In ${days} days`;
    const place = [e.venue, e.address || [e.city, e.state].filter(Boolean).join(', ')].filter(Boolean).join(' · ');
    const map = e.address || e.venue ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent([e.venue, e.address || `${e.city}, ${e.state}`].filter(Boolean).join(', '))}` : '';
    const teams = regionTeams(e, 'muted-light') || '<p class="muted-light">Entries aren’t tracked for this event.</p>';
    const watch = e.watch?.length ? e.watch.map((w) => ext(w.url, w.label, 'text-link')).join(' ') : '<span class="muted-light">No livestream announced yet.</span>';
    $('next-event').hidden = false;
    $('next-event').innerHTML = `<div class="next-main"><span class="next-when">${esc(when)}</span><span class="label">${esc(e.program)} · ${esc(e.type)}</span><h3>${esc(e.name)}</h3><p class="next-date">${esc(dateRange(e.startDate, e.endDate))}</p>${place ? `<p>${map ? ext(map, place) : esc(place)}</p>` : ''}${e.admission ? `<p><strong>Admission:</strong> ${esc(e.admission)}</p>` : ''}${e.description ? `<p class="muted-light">${esc(e.description)}</p>` : ''}<ul class="link-list"><li>${ext(e.url, 'Event details', 'text-link')}</li><li>${ext(google(e), 'Add to Google Calendar', 'text-link')}</li></ul></div><div class="next-side">${live ? '' : `<div class="next-count"><strong>${days}</strong><span>${days === 1 ? 'day' : 'days'} to go</span></div>`}<h4>Local teams entered</h4>${teams}<h4>How to watch</h4><p>${watch}</p></div>`;
    // During event week, a strip under the hero points here.
    if (days <= 7) {
      $('this-week').hidden = false;
      $('this-week').innerHTML = `<span class="wrap"><span class="tw-label">${live ? 'Happening now' : 'This week'}</span><strong>${esc(e.name)}</strong><span>${esc(dateRange(e.startDate, e.endDate))} · ${esc(e.city || e.venue)}</span><span class="tw-go">Details</span></span>`;
    }
  }

  function renderMedia() {
    const { news, seasonSummary: s } = state.data;
    $('news-list').innerHTML = [...news.stories].sort((a, b) => b.date.localeCompare(a.date)).map((x) => `<li>${ext(x.url, x.title)}<small>${esc(x.outlet)} · ${esc(shortDate(x.date))}</small></li>`).join('');
    $('sources-body').innerHTML = `<ul class="news-list">
      <li><strong>Records, events, awards:</strong> ${ext('https://www.thebluealliance.com/', 'The Blue Alliance')}, captured Oct 22, 2026. Records count official matches only.</li>
      <li><strong>EPA ratings:</strong> ${ext('https://www.statbotics.io/', 'Statbotics')}, final 2026 values from the June 12, 2026 data file.</li>
      <li><strong>FTC ratings:</strong> ${ext('https://ftcscout.org/', 'FTCScout')}, best event OPR excluding penalties, 2025–26 season.</li>
      <li><strong>Team-school links, hometowns, rookie years:</strong> official ${ext('https://frc-events.firstinspires.org/', 'FIRST')} team profiles.</li>
      <li><strong>Replays:</strong> official FIRST Indiana Robotics video, matched to TBA result pages.</li>
      <li><a href="standings-2026.csv" download>Standings CSV</a> · <a href="calendar.ics" download>Season calendar (.ics)</a> · ${ext('https://github.com/horner/refintery-rankings/tree/main/data', 'All data as JSON and CSV')}</li>
      <li>${ext('https://github.com/horner/refintery-rankings', 'Full research, raw captures and methodology on GitHub')}</li></ul>`;
  }

  function renderDnf(dnf) {
    const leaderText = (school) => school.leader?.name ? `${esc(school.leader.role)}: ${esc(school.leader.name)} · ${esc(school.leader.evidenceLabel)}` : 'School leader name not verified in public sources.';
    const leaderLink = (school) => school.leader?.name ? `${esc(school.leader.role)}: ${ext(school.leader.sourceUrl, school.leader.name)} · ${esc(school.leader.evidenceLabel)}` : 'School leader name not verified in public sources.';
    const mail = (school = '') => `mailto:${dnf.contactEmail}?subject=${encodeURIComponent(`Interested in starting a robotics team${school ? ` — ${school}` : ''}`)}&body=${encodeURIComponent(`Hello The REFINERY,\n\nWe’re interested in exploring an FTC or FRC team${school ? ` at ${school}` : ' at our school'}. Please help us understand the first steps.\n\nSchool / organization: ${school}\nMy name and role: \n`)}`;
    $('dnf-count').innerHTML = `<strong data-count="${dnf.schools.length}">${dnf.schools.length}</strong><span>schools without a team</span>`;
    countUp($('dnf-count').querySelector('strong'));
    const update = () => {
      const query = $('dnf-search').value.trim().toLocaleLowerCase();
      const region = $('dnf-state').value, sector = $('dnf-sector').value, sort = $('dnf-sort').value;
      const schools = dnf.schools.filter((s) => (!region || s.state === region) && (!sector || s.sector === sector) && (!query || [s.name, s.district, s.city, s.county, s.leader?.name].join(' ').toLocaleLowerCase().includes(query)))
        .sort((a, b) => sort === 'name' ? a.name.localeCompare(b.name) : a.distanceMiles - b.distanceMiles);
      $('dnf-list').innerHTML = schools.slice(0, state.dnfLimit).map((s) => `<li><details class="school"><summary><span><strong>${esc(s.name)}</strong><small>${esc(s.city)}, ${esc(s.state)} · ${esc(s.sector)}${/^Regular/.test(s.schoolType) ? '' : ` · ${esc(s.schoolType)}`}</small><small class="school-leader">${leaderText(s)}</small></span><span class="miles">${num(s.distanceMiles, 1)}<small> mi</small></span></summary><div class="school-body"><p>${esc(s.district)}${s.county ? ` · ${esc(s.county)}` : ''}</p><p>${leaderLink(s)}</p>${s.schoolStatusNote ? `<p>${esc(s.schoolStatusNote)}</p>` : ''}<p>${ext(s.schoolUrl, 'School website')} · ${num(s.distanceMiles, 1)} miles from downtown Fort Wayne</p><a class="button button-primary" href="${safeUrl(mail(s.name))}">We’re interested</a></div></details></li>`).join('') || '<li class="loading">No schools match. Try a town, district or county.</li>';
      $('dnf-results').textContent = `Showing ${Math.min(state.dnfLimit, schools.length)} of ${schools.length} schools`;
      $('dnf-more').hidden = state.dnfLimit >= schools.length;
    };
    ['dnf-search', 'dnf-state', 'dnf-sector', 'dnf-sort'].forEach((id) => $(id).addEventListener(id === 'dnf-search' ? 'input' : 'change', () => { state.dnfLimit = 24; update(); }));
    $('dnf-more').addEventListener('click', () => { state.dnfLimit += 24; update(); });
    $('dnf-interest').href = mail();
    $('dnf-interest').removeAttribute('target');
    if (dnf.reviewSchools?.length) {
      $('dnf-review').hidden = false;
      $('dnf-review-summary').textContent = `Bring back a team: ${dnf.reviewSchools.length} schools with a former team or community connection`;
      $('dnf-review-list').innerHTML = dnf.reviewSchools.map((s) => `<li><strong>${esc(s.name)}</strong> · ${esc(s.city)}, ${esc(s.state)}<br><small>${esc(s.teamNote)}</small><p>${leaderLink(s)}</p><a href="${safeUrl(mail(s.name))}">Talk about a relaunch</a></li>`).join('');
    }
    $('dnf-method').innerHTML = `<p>${esc(dnf.scopeNote)}</p><p>${esc(dnf.qualification)}</p><p>The list includes career centers, alternative and special-education programs, and private schools as well as traditional high schools. ${dnf.counts.existingTeams} schools with current teams and ${dnf.counts.facilitiesNotInvited} secure or residential facilities are left off. Checked ${esc(shortDate(dnf.asOf))}. ${ext('https://github.com/horner/refintery-rankings/blob/main/broadcast/dist/dnf-methodology.md', 'Full school list, leaders and sources')}</p><p>Already fielding a team? ${ext('mailto:info@refineryrobotics.org?subject=DNF%20correction', 'Send a correction')} and we’ll move you to the lineup.</p>`;
    update();
  }

  function loadDnf() {
    if (state.dnfRequested || !state.data?.dnf?.src) return;
    state.dnfRequested = true;
    fetch(state.data.dnf.src, { cache: 'no-cache' }).then((r) => { if (!r.ok) throw new Error(`School list returned ${r.status}`); return r.json(); })
      .then((dnf) => { renderDnf(dnf); if (location.hash === '#dnf') $('dnf').scrollIntoView(); })
      .catch((error) => { console.warn('DNF list:', error); $('dnf-list').innerHTML = '<li class="loading">The school list could not be loaded. Refresh to try again.</li>'; });
  }

  function openFromHash() {
    if (legacyDisplayRoute()) return;
    const match = location.hash.match(/^#team\/(\d+)$/);
    if (!match) return;
    const el = $(`team-${match[1]}`);
    if (el) { el.open = true; el.scrollIntoView({ block: 'start' }); }
  }

  // Plain-language definitions behind the jargon. Tap a dotted-underlined term to see one.
  const GLOSSARY = {
    alliance: ['Alliance', 'Three teams playing together as red or blue. Partners change every qualifying match; playoff alliances stay together.'],
    record: ['Record', 'Wins and losses in official matches: district events, the state championship and the world championship. A win is shared by the whole alliance.'],
    district: ['District points', 'FIRST Indiana awards points at each district event for qualifying wins, being picked for playoffs, playoff wins and judged awards. The top teams by points go to the state championship.'],
    epa: ['EPA', 'Expected Points Added, from Statbotics: about how many points a robot adds to its alliance’s score each match. Think points per game.'],
    qualifying: ['Qualifying', 'The first part of an event: every team plays a dozen or more matches with random partners. The ranking after qualifying decides the playoff seeds.'],
    playoffs: ['Playoffs', 'The top 8 teams each pick two partners (the #1 seed picks first). Alliances play a double-elimination bracket, so a team is out after two losses, and the last two alliances meet in a best-of-three final.'],
    opr: ['OPR', 'Offensive Power Rating: an FTC estimate of the points a team adds per match, worked out from its alliances’ scores. Not comparable to FRC’s EPA.'],
  };
  const term = (key, label) => `<button type="button" class="term" data-term="${key}">${esc(label)}</button>`;
  const tip = document.createElement('div');
  tip.className = 'term-tip';
  tip.id = 'term-tip';
  tip.setAttribute('role', 'tooltip');
  tip.hidden = true;
  document.body.append(tip);
  let tipFor = null;
  const hideTip = () => { tip.hidden = true; tipFor?.setAttribute('aria-expanded', 'false'); tipFor = null; };
  document.addEventListener('click', (event) => {
    const button = event.target.closest('.term');
    if (!button) { if (!event.target.closest('.term-tip')) hideTip(); return; }
    event.preventDefault();
    event.stopPropagation();
    if (tipFor === button) { hideTip(); return; }
    const [title, text] = GLOSSARY[button.dataset.term] || [];
    if (!title) return;
    hideTip();
    tip.innerHTML = `<strong>${esc(title)}</strong>${esc(text)}`;
    tip.hidden = false;
    const box = button.getBoundingClientRect();
    const left = Math.max(12, Math.min(box.left, innerWidth - tip.offsetWidth - 12));
    tip.style.left = `${left + scrollX}px`;
    tip.style.top = `${box.bottom + scrollY + 8}px`;
    button.setAttribute('aria-expanded', 'true');
    button.setAttribute('aria-describedby', 'term-tip');
    tipFor = button;
  }, true);
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') hideTip(); });
  addEventListener('resize', hideTip);

  // The replay loads YouTube only when someone presses play.
  $('replay-play')?.addEventListener('click', (event) => {
    const button = event.currentTarget;
    button.outerHTML = `<div class="replay-frame"><iframe src="https://www.youtube-nocookie.com/embed/${encodeURIComponent(button.dataset.video)}?autoplay=1&rel=0" title="2026 FIN District Mishawaka Event, Finals 2" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div>`;
  });

  // Motion: reveal blocks as they scroll in, count numbers up, drift the hero photo.
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Items that arrive together stagger by their order in that batch, so a long list never lags.
  const revealer = !calm && 'IntersectionObserver' in window
    ? new IntersectionObserver((entries) => {
      entries.filter((e) => e.isIntersecting).forEach((e, i) => {
        if (e.target.dataset.stagger) e.target.style.setProperty('--i', Math.min(i, 7));
        e.target.classList.add('in');
        revealer.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -10% 0px' })
    : null;
  const reveal = (selector, kind = 'reveal', stagger = true) => document.querySelectorAll(selector).forEach((el) => {
    if (!revealer || el.dataset.revealed) return;
    el.dataset.revealed = kind;
    el.classList.add(kind);
    if (stagger) el.dataset.stagger = '1';
    revealer.observe(el);
  });
  // Heavy section rules draw across instead of appearing.
  const rule = (selector, size, color) => document.querySelectorAll(selector).forEach((el) => {
    if (!revealer) return;
    el.classList.add('rule');
    el.style.setProperty('--rule', size);
    el.style.setProperty('--rule-color', color);
    revealer.observe(el);
  });
  const countUp = (el) => {
    const target = Number(el.dataset.count);
    if (calm || !Number.isFinite(target) || !('IntersectionObserver' in window)) { el.textContent = num(target); return; }
    el.textContent = '0';
    new IntersectionObserver(([entry], observer) => {
      if (!entry.isIntersecting) return;
      observer.disconnect();
      const start = performance.now(), duration = 1100;
      const tick = (now) => { const p = Math.min(1, (now - start) / duration); el.textContent = num(Math.round(target * (1 - Math.pow(1 - p, 3)))); if (p < 1) requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    }).observe(el);
  };
  const heroBg = document.querySelector('.hero-bg');
  if (!calm && heroBg) {
    let ticking = false;
    addEventListener('scroll', () => {
      if (ticking || scrollY > innerHeight) return;
      ticking = true;
      requestAnimationFrame(() => { heroBg.style.transform = `translate3d(0, ${scrollY * 0.3}px, 0)`; ticking = false; });
    }, { passive: true });
  }
  const animateSections = () => {
    reveal('.section .kicker', 'reveal', false);
    reveal('.section h2', 'reveal-head', false);
    reveal('.section-lede', 'reveal', false);
    reveal('.segmented, .next-event, .dnf-count', 'reveal', false);
    reveal('.explainer', 'reveal', false);
    reveal('#standings-list .team', 'reveal-left');
    reveal('.highlight');
    reveal('.gallery figure', 'reveal-img');
    reveal('.card');
    reveal('.schedule li');
    reveal('.faq details');
    reveal('.beats li');
    reveal('.replay', 'reveal-img', false);
    reveal('.media-card');
    reveal('.dnf .hero-actions, .dnf-tools', 'reveal', false);
    rule('.standings', '5px', 'var(--navy)');
    rule('.card-grid', '5px', 'var(--green)');
    rule('.media-grid', '5px', 'var(--navy)');
    rule('.schedule, .faq', '2px', 'var(--ink)');
    rule('.highlight-grid', '1px', 'var(--dark-line)');
    document.querySelectorAll('[data-count]').forEach(countUp);
  };

  // Header: solid once the hero scrolls away, tucks away while reading down, returns on scroll up.
  // A thin progress bar tracks how far down the page you are.
  const header = document.querySelector('.site-header');
  const progress = document.createElement('div');
  progress.className = 'scroll-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.append(progress);
  let lastY = scrollY, frame = false;
  const onScroll = () => {
    if (frame) return;
    frame = true;
    requestAnimationFrame(() => {
      const y = scrollY;
      header.classList.toggle('scrolled', y > 40);
      if (y < innerHeight * 0.9 || y < lastY - 6) header.classList.remove('tucked');
      else if (y > lastY + 6 && !header.classList.contains('open') && innerWidth > 760) header.classList.add('tucked');
      if (Math.abs(y - lastY) > 6) lastY = y;
      progress.style.transform = `scaleX(${Math.min(1, y / Math.max(1, document.documentElement.scrollHeight - innerHeight))})`;
      // A jump (nav link, deep link) can skip past blocks without them ever intersecting; show them.
      document.querySelectorAll('[data-revealed]:not(.in), .rule:not(.in)').forEach((el) => { if (el.getBoundingClientRect().top < innerHeight * 0.9) { el.classList.add('in'); revealer?.unobserve(el); } });
      frame = false;
    });
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  $('menu-toggle').addEventListener('click', () => { const open = header.classList.toggle('open'); $('menu-toggle').setAttribute('aria-expanded', String(open)); });
  $('site-nav').addEventListener('click', (e) => { if (e.target.closest('a')) { header.classList.remove('open'); $('menu-toggle').setAttribute('aria-expanded', 'false'); } });
  document.querySelectorAll('[data-sort]').forEach((button) => button.addEventListener('click', () => {
    state.sort = button.dataset.sort;
    document.querySelectorAll('[data-sort]').forEach((b) => b.setAttribute('aria-pressed', String(b === button)));
    renderStandings();
    document.querySelectorAll('#standings-list .team').forEach((el) => el.classList.add('reveal', 'in'));
  }));
  addEventListener('hashchange', () => { openFromHash(); if (location.hash === '#dnf') loadDnf(); });

  fetch('data.json', { cache: 'no-cache' }).then((r) => { if (!r.ok) throw new Error(`Data returned ${r.status}`); return r.json(); }).then((data) => {
    state.data = data;
    renderStats();
    renderStandings();
    renderHighlights();
    renderFtc();
    renderSchedule();
    renderMedia();
    animateSections();
    openFromHash();
    // Content above a section deep link has just rendered, so jump again to land on it.
    if (/^#[a-z]+$/.test(location.hash) && location.hash !== '#dnf') document.querySelector(location.hash)?.scrollIntoView();
    // The school directory is most of the data; fetch it when a visitor heads toward it.
    if (location.hash === '#dnf' || !('IntersectionObserver' in window)) loadDnf();
    else new IntersectionObserver((entries, observer) => { if (entries.some((e) => e.isIntersecting)) { observer.disconnect(); loadDnf(); } }, { rootMargin: '1200px 0px' }).observe($('dnf'));
  }).catch((error) => {
    console.warn('Data:', error);
    $('standings-list').innerHTML = `<p class="loading">The standings could not be loaded. ${location.protocol === 'file:' ? 'Serve this folder with a local web server, e.g. python -m http.server.' : 'Refresh the page to try again.'}</p>`;
  });
})();
