'use strict';

(() => {
  const $ = (id) => document.getElementById(id);
  const state = { data: null, selected: 0, view: 'board', presenter: false, cycle: null, exporting: false, presentation: false, countdownTimer: null };
  const frame = $('on-air-frame');
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const safeUrl = (value) => { try { const url = new URL(value, location.href); return ['https:', 'http:'].includes(url.protocol) ? esc(url.href) : '#'; } catch { return '#'; } };
  const num = (value, decimals = 0) => Number.isFinite(Number(value)) && value !== null && value !== '' ? Number(value).toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) : '—';
  const date = (value) => { if (!value) return 'Date not supplied'; const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2})/); return match ? `${['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][Number(match[2]) - 1]} ${Number(match[3])}, ${match[1]}` : String(value); };
  const selected = () => state.data.top10[state.selected];
  const setStatus = (message) => { $('app-status').textContent = message; };
  const link = (url, title) => `<a href="${safeUrl(url)}" target="_blank" rel="noopener">${esc(title)}</a>`;
  const sourceLabel = (url) => { try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return String(url); } };
  const sources = (urls = []) => [...new Set(urls)].map((url, i) => link(url, `${sourceLabel(url)}${urls.filter((u) => sourceLabel(u) === sourceLabel(url)).length > 1 ? ` [${i + 1}]` : ''}`)).join(' · ');
  const calendarDay = (iso) => { const match = String(iso || '').match(/^(\d{4})-(\d{2})-(\d{2})$/); return match ? Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])) / 86400000 : null; };
  const indianaDay = () => {
    const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: 'America/Indiana/Indianapolis', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date()).filter((part) => ['year', 'month', 'day'].includes(part.type)).map((part) => [part.type, part.value]));
    return calendarDay(`${parts.year}-${parts.month}-${parts.day}`);
  };
  function renderCountdown() {
    const countdown = state.data?.seasonPreview?.countdown;
    if (!countdown || !$('season-countdown')) return;
    const start = calendarDay(countdown.targetDate);
    const end = calendarDay(countdown.endDate) ?? start;
    if (start === null) return;
    const today = indianaDay();
    const remaining = Math.max(0, start - today);
    const phase = today < start ? 'COUNTDOWN TO' : today <= end ? 'THIS WEEKEND' : 'SEASON UNDERWAY';
    const value = today < start ? `<strong class="countdown-value">${esc(remaining)}<span>${remaining === 1 ? 'DAY' : 'DAYS'}</span></strong>` : `<strong class="countdown-value countdown-live">${today <= end ? 'IT’S GO TIME.' : 'GAME ON.'}</strong>`;
    $('season-countdown').innerHTML = `<div class="eyebrow">${phase}</div>${value}<h3>${esc(countdown.label)}</h3><p class="countdown-date">${esc(date(countdown.targetDate))}${countdown.endDate && countdown.endDate !== countdown.targetDate ? ` – ${esc(date(countdown.endDate))}` : ''}</p>${countdown.sourceUrl ? `<a href="${safeUrl(countdown.sourceUrl)}" target="_blank" rel="noopener">Event details <span aria-hidden="true">↗</span></a>` : ''}<p class="countdown-note">${esc(countdown.note || '')}</p><small>Countdown uses the calendar date in Fort Wayne, Indiana.</small>`;
  }

  function renderSeasonPreview() {
    const preview = state.data?.seasonPreview;
    if (!preview || !$('season-preview')) return;
    $('season-label').textContent = `${preview.seasonLabel || '2026–27'} / THE NEXT CHAPTER`;
    $('season-title').textContent = preview.title || 'THE SEASON AHEAD.';
    $('season-intro').textContent = preview.intro || '';
    renderCountdown();
    clearInterval(state.countdownTimer);
    state.countdownTimer = setInterval(renderCountdown, 60000);
    $('season-ftc').innerHTML = `<div class="eyebrow dark">FTC / THREE LOCAL TEAMS TO FOLLOW</div><h3>A NEW TEAM.<br>A NEW CHAPTER.</h3><div class="season-team-list">${(preview.localFtcTeams || []).map((team) => `<a href="${safeUrl(team.profileUrl)}" target="_blank" rel="noopener"><span class="season-team-number">${esc(team.number)}</span><span><strong>${esc(team.name)}${team.isNew ? '<small class="rookie-tag">NEW THIS SEASON</small>' : ''}</strong><span>${esc(team.school)}</span></span><span class="season-team-arrow" aria-hidden="true">↗</span></a>`).join('')}</div><p>After their first matches: meet the students, the mentors, and the robots behind the results.</p>`;
    $('season-timeline').innerHTML = (preview.milestones || []).map((event, index) => {
      const statusClass = event.status === 'Confirmed event' ? 'confirmed' : event.status === 'Planned coverage' ? 'planned' : 'target';
      return `<article class="season-milestone" id="season-${esc(event.id || index)}"><div class="milestone-topline"><span class="milestone-program">${esc(event.program || 'ROBOTICS')}</span><span class="milestone-status ${statusClass}">${esc(event.status)}</span></div><div class="milestone-date">${esc(event.dateLabel || date(event.startDate))}</div><h4>${esc(event.title)}</h4><p>${esc(event.description)}</p>${event.location ? `<span class="milestone-location">${esc(event.location)}</span>` : ''}${event.note ? `<p class="milestone-note">${esc(event.note)}</p>` : ''}${event.linkUrl ? `<a class="milestone-link" href="${safeUrl(event.linkUrl)}" target="_blank" rel="noopener">${esc(event.linkLabel || 'Source & details')} <span aria-hidden="true">↗</span></a>` : ''}</article>`;
    }).join('');
    const showList = (program, shows) => `<details class="season-show-list"><summary><span><small>${esc(program)} / PLANNED COVERAGE</small><strong>THE WEEKLY RUNDOWN</strong><span class="show-range">${shows.length ? `${esc(date(shows[0].date))} – ${esc(date(shows[shows.length - 1].date))}` : 'Episode dates coming soon'}</span></span><span class="show-expand" aria-hidden="true">＋</span></summary><ol>${shows.map((show) => `<li><time datetime="${esc(show.date)}">${esc(date(show.date))}</time><div><strong>${esc(show.title)}</strong><p>${esc(show.summary)}</p>${show.sourceUrl ? `<a href="${safeUrl(show.sourceUrl)}" target="_blank" rel="noopener">Competition calendar <span aria-hidden="true">↗</span></a>` : ''}</div></li>`).join('')}</ol></details>`;
    $('season-shows').innerHTML = `<div class="weekly-promise"><div class="eyebrow dark">AFTER THE FINAL BUZZER</div><h3>THE SCORES.<br>THE STORIES.<br>THE NEXT PICK.</h3><p>${esc(preview.weeklyPromise || '')}</p><span>All show dates below are planned coverage dates.</span></div><div class="season-show-calendars">${showList('FTC', preview.shows?.ftc || [])}${showList('FRC', preview.shows?.frc || [])}</div>`;
    $('season-notes').innerHTML = `<span class="schedule-asof">SCHEDULE CHECKED ${esc(date(preview.asOf))}</span><ul>${(preview.notes || []).map((note) => `<li>${esc(note)}</li>`).join('')}</ul>`;
    $('season-preview').hidden = false;
  }
  function renderDnf() {
    const dnf = state.data?.dnf;
    if (!dnf || !$('dnf')) return;
    const interestUrl = (school = '') => `mailto:${dnf.contactEmail}?subject=${encodeURIComponent(`Interested in starting a robotics team${school ? ` — ${school}` : ''}`)}&body=${encodeURIComponent(`Hello The REFINERY,\n\nWe’re interested in exploring an FTC or FRC team${school ? ` at ${school}` : ' at our school'}. Please help us understand the first steps.\n\nSchool / organization: ${school}\nMy name and role: \n`)}`;
    $('dnf-interest').href = interestUrl();
    $('dnf-summary').textContent = `${dnf.schools.length} schools to invite. One conversation to begin.`;
    $('dnf-qualification').textContent = dnf.qualification;
    $('dnf-source-note').innerHTML = `<p>${esc(dnf.scopeNote)}</p><p>Checked ${esc(date(dnf.asOf))}. ${link(dnf.methodologyUrl, 'School roster, team screening, and leadership sources')}.</p>`;
    let limit = 20;
    const update = () => {
      const query = $('dnf-search').value.trim().toLocaleLowerCase();
      const region = $('dnf-state').value;
      const sector = $('dnf-sector').value;
      const schools = dnf.schools.filter((school) => (!region || school.state === region) && (!sector || school.sector === sector) && (!query || [school.name, school.district, school.city, school.county, school.leader?.name].join(' ').toLocaleLowerCase().includes(query)));
      $('dnf-schools').innerHTML = schools.slice(0, limit).map((school) => `<tr><td data-label="School"><strong>${link(school.schoolUrl, school.name)}</strong><span>${esc(school.city)}, ${esc(school.state)} · ${esc(school.sector)}</span><small>${esc(school.district || '')}</small>${school.schoolStatusNote ? `<small>${esc(school.schoolStatusNote)}</small>` : ''}</td><td data-label="Superintendent / school contact">${school.leader?.name ? `<strong>${link(school.leader.sourceUrl, school.leader.name)}</strong><span>${esc(school.leader.role)}</span>${school.leader.evidenceLabel ? `<small>${esc(school.leader.evidenceLabel)}</small>` : ''}` : `<strong>Name not verified</strong><span>${link(school.schoolUrl, 'See school source')}</span>`}</td><td data-label="From downtown"><strong>${num(school.distanceMiles, 1)} mi</strong><span>Straight line</span></td><td data-label="Take the first step"><a class="dnf-school-interest" href="${esc(interestUrl(school.name))}">We’re interested <span aria-hidden="true">↗</span><span class="sr-only"> in starting a team at ${esc(school.name)}</span></a></td></tr>`).join('') || '<tr><td colspan="4">No schools match those filters. Try a school, district, leader, or town.</td></tr>';
      $('dnf-results').textContent = `Showing ${Math.min(limit, schools.length)} of ${schools.length} schools${schools.length === dnf.schools.length ? '' : ` (${dnf.schools.length} total)`}.`;
      $('dnf-more').hidden = limit >= schools.length;
    };
    ['dnf-search', 'dnf-state', 'dnf-sector'].forEach((id) => $(id).addEventListener(id === 'dnf-search' ? 'input' : 'change', () => { limit = 20; update(); }));
    $('dnf-more').addEventListener('click', () => { limit += 20; update(); });
    if ($('dnf-review')) {
      $('dnf-review').hidden = !(dnf.reviewSchools || []).length;
      $('dnf-review-summary').textContent = `${(dnf.reviewSchools || []).length} former-team and community connections to check`;
      $('dnf-review-schools').innerHTML = (dnf.reviewSchools || []).map((school) => `<article><h4>${esc(school.name)} <small>${esc(school.state)}</small></h4><p>${esc(school.teamNote)}</p><p>${school.leader?.name ? `${esc(school.leader.name)} · ${esc(school.leader.role)}. ` : ''}${link(dnf.methodologyUrl, 'Affiliation and leadership sources')}</p><a href="${esc(interestUrl(school.name))}">Talk about the next step ↗</a></article>`).join('');
    }
    update();
    $('dnf').hidden = false;
  }
  const schoolName = (team) => team.school || team.name;
  const identityBadge = (team, kind, compact = false) => {
    const logo = team.logos?.[kind];
    return logo?.file ? `<span class="identity-badge${compact ? ' compact-badge' : ''}" title="${esc(logo.label)}"><span class="logo-tile${logo.background === 'dark' ? ' dark-logo' : ''}"><img src="${esc(logo.file)}" alt="${esc(logo.label)}" decoding="async"></span>${compact ? '' : `<span class="logo-caption">${kind === 'school' ? 'SCHOOL' : 'TEAM'}</span>`}</span>` : '';
  };
  const prioritizeSpotlight = (people, team) => [...people].sort((a, b) => Number(b.name === team.spotlight?.name) - Number(a.name === team.spotlight?.name));
  const studentVoices = (team) => {
    const records = [...(team.students || []), ...(team.representatives || []).filter((p) => /^student\b/i.test(p.role))];
    return prioritizeSpotlight(records.filter((p, i) => records.findIndex((other) => other.name === p.name) === i), team);
  };
  const logoSources = (team) => Object.values(team.logos || {}).filter((r) => r.file).map((r) => link(r.pageUrl, `${r.kind === 'school' ? 'School' : 'Team'} logo · ${r.label}`)).join(' · ');
  const shortSchool = (team) => schoolName(team).replace(/High School/g, 'HS').replace(/Junior\s*\/\s*Senior/g, 'Jr./Sr.').replace(/\s*\/\s*Huntington County 4-H/g, ' / 4-H');
  const personDetail = (person) => {
    const status = person.status || '';
    const qualification = /retrospective/i.test(status) ? 'retrospective' : /historical/i.test(status) ? 'historical' : /indexed/i.test(status) ? 'indexed evidence' : /self reported/i.test(status) ? 'self-reported' : /season qualification/i.test(status) ? 'season-qualified' : '';
    const evidenceDate = person.date ? date(person.date) : person.season && /^\d{4}[-–]\d{2}$/.test(person.season) ? `${person.season} · undated` : 'undated evidence';
    return [person.role, evidenceDate, qualification].filter(Boolean).join(' · ');
  };
  const peopleBlock = (people, heading, gap) => `<div class="people-section"><h4 class="people-heading">${heading}</h4>${people?.length ? `<div class="people-list">${people.slice(0, 2).map((p) => `<div><span class="person-name">${esc(p.name)}</span><span class="person-role">${esc(personDetail(p))}</span></div>`).join('')}</div>` : `<p class="person-gap">${esc(gap)}</p>`}</div>`;
  const stateRank = (team) => team.stateRank ? `${num(team.stateRank)}<small>/ ${num(team.stateCount)}</small>` : '—';
  const seasonCount = (team) => Array.isArray(team.seasons) ? team.seasons.length : team.seasons;
  const stats = (team) => `<div class="spotlight-stats"><div><span class="stat-value">${num(team.epa, 2)}</span><span class="stat-label">2026 EPA</span></div><div><span class="stat-value">${stateRank(team)}</span><span class="stat-label">INDIANA EPA RANK</span></div><div><span class="stat-value">${num(seasonCount(team))}</span><span class="stat-label">RECORDED SEASONS</span></div></div>`;
  const teamIdentity = (team) => `<div class="spotlight-eyebrow"><span>TEAM SPOTLIGHT / NO. ${esc(team.number)}</span><span>REGIONAL #${esc(team.rank)}</span></div><div class="spotlight-identity">${identityBadge(team, 'school')}<div class="spotlight-copy"><h3 class="spotlight-school"${schoolName(team).length > 45 ? ' style="font-size:2.8cqw"' : ''}>${esc(schoolName(team))}</h3><p class="spotlight-name">${esc(team.name)}</p><p class="spotlight-place">${esc([team.city, team.county ? `${team.county.replace(/ County$/i, '')} County` : ''].filter(Boolean).join(' · '))}</p></div>${identityBadge(team, 'team')}</div>`;
  const story = (team) => (team.talkingPoints || [])[2] || (team.talkingPoints || [])[0] || `${team.name} brings student engineering, coding, and teamwork to ${team.city || 'Northeast Indiana'}.`;
  const matchRecord = (team, program = 'FRC') => state.data.matchHighlights?.teams.find((record) => record.program === program && record.number === team.number);
  const marginLabel = (match) => match.margin === 0 ? 'Tied score' : `${num(match.margin)}-point game`;
  const matchScore = (match) => `${num(match.redScore)}–${num(match.blueScore)}`;
  const matchReplay = (match, label = 'Watch replay') => match.videoUrl ? link(match.videoUrl, `${label} ↗`) : link(match.officialUrl, 'Match result ↗');
  const screenMatch = (team, program = 'FRC') => {
    const match = matchRecord(team, program)?.main;
    const thumbnail = match && state.data.videoThumbnails?.[match.videoUrl];
    if (thumbnail && program === 'FRC') return `<div class="screen-replay"><a class="replay-preview" href="${safeUrl(match.videoUrl)}" target="_blank" rel="noopener" aria-label="Watch ${esc(team.name)}: ${esc(match.matchLabel)}, ${esc(match.eventName)}"><img src="${esc(thumbnail.file)}" width="${esc(thumbnail.width)}" height="${esc(thumbnail.height)}" alt="Video preview: ${esc(match.videoTitle)}" loading="eager" decoding="async"><span class="replay-play" aria-hidden="true">▶</span><span class="replay-watch" aria-hidden="true">WATCH REPLAY ↗</span></a><div class="replay-copy"><span>CLOSEST FINISH / ${esc(match.phase === 'Playoff' ? 'PLAYOFF' : 'QUALIFIER')}</span><strong>${esc(matchScore(match))}<small>RED–BLUE ALLIANCE SCORE</small></strong><p>${esc(marginLabel(match))} · ${esc(match.matchLabel)}</p><p class="replay-event">${esc(match.eventName)}</p>${link(match.officialUrl, 'Official result ↗')}</div></div>`;
    return match ? `<p class="screen-match"><span>CLOSEST FINISH / ${esc(match.phase === 'Playoff' ? 'PLAYOFF' : 'QUALIFIER')}</span><strong>${esc(matchScore(match))}</strong> alliance score · ${esc(marginLabel(match).toLowerCase())} · ${matchReplay(match)}</p>` : `<p class="story-line">${esc(story(team))}</p>`;
  };
  const matchDate = (match) => match.playedDate ? date(match.playedDate) : match.eventStartDate === match.eventEndDate ? date(match.eventStartDate) : `${date(match.eventStartDate)} – ${date(match.eventEndDate)} · event dates`;
  const matchLineups = (match, team) => ['Red', 'Blue'].map((color) => `<div class="match-alliance ${color.toLowerCase()}-alliance"><div><span>${color.toUpperCase()} ALLIANCE</span><strong>${num(match[`${color.toLowerCase()}Score`])}</strong></div><p>${match[`${color.toLowerCase()}Teams`].map((number) => number === team.number ? `<strong title="Featured team">${esc(number)}</strong>` : esc(number)).join(' <span aria-hidden="true">/</span> ')}</p></div>`).join('');
  const matchNotes = (team, program = 'FRC') => {
    const match = matchRecord(team, program)?.main;
    return match ? `<h4>THE CLOSE FINISH</h4><p>${esc(match.eventName)} · ${esc(match.matchLabel)} · ${esc(matchDate(match))}. Red ${num(match.redScore)}, Blue ${num(match.blueScore)}. Team ${esc(team.number)} was on ${esc(match.teamAlliance)} (${esc(match.outcome.toLowerCase())}); ${esc(marginLabel(match).toLowerCase())}. ${matchReplay(match)} · ${link(match.officialUrl, 'Official result')}.</p><p>Final alliance totals include penalties. Opposing teams in this match are a matchup, not evidence of a lasting rivalry.</p>` : '';
  };
  function matchCard(team, program) {
    const record = matchRecord(team, program);
    if (!record?.main) return `<article class="match-pending"><span class="eyebrow dark">${esc(program)} ${esc(team.number)} / DEBUT WATCH</span><h4>${esc(team.name)}</h4><p>${esc(record?.note || 'The match profile follows this team’s first official match.')}</p></article>`;
    const match = record.main;
    const playoff = record.playoff;
    return `<article class="match-card"><div class="match-card-top"><span>${esc(program)} ${esc(team.number)} / ${esc(team.name)}</span><span class="match-phase">${esc(match.phase)}</span></div><div class="match-card-body"><div class="match-caption"><span class="match-season">${esc(record.seasonLabel)} / CLOSEST FINISH</span><h4>${esc(match.eventName)}</h4><p>${esc(match.matchLabel)} · ${esc(matchDate(match))}</p></div><div class="match-scoreboard">${matchLineups(match, team)}</div><div class="match-outcome"><strong>${esc(marginLabel(match))}</strong><span>Team ${esc(team.number)} on ${esc(match.teamAlliance)} · ${esc(match.outcome.toLowerCase())}</span></div><div class="match-actions">${match.videoUrl ? `<a class="watch-replay" href="${safeUrl(match.videoUrl)}" target="_blank" rel="noopener"><span aria-hidden="true">▶</span> WATCH REPLAY <span aria-hidden="true">↗</span><span class="sr-only">: ${esc(team.name)}, ${esc(match.matchLabel)}</span></a>` : ''}${link(match.officialUrl, 'Official result ↗')}</div>${playoff ? `<details class="match-playoff"><summary><span>ALSO IN THE PLAYOFFS</span><strong>${esc(marginLabel(playoff))} <span aria-hidden="true">＋</span></strong></summary><div><h5>${esc(playoff.eventName)}</h5><p>${esc(playoff.matchLabel)} · ${esc(matchDate(playoff))}</p><div class="match-scoreboard">${matchLineups(playoff, team)}</div><p>Team ${esc(team.number)} on ${esc(playoff.teamAlliance)} · ${esc(playoff.outcome.toLowerCase())}</p><p>${matchReplay(playoff)} · ${link(playoff.officialUrl, 'Official result ↗')}</p></div></details>` : ''}</div></article>`;
  }
  function renderMatches() {
    const library = state.data.matchHighlights;
    if (!library || !$('match-panel')) return;
    const teams = state.view === 'ftc' ? state.data.ftc.teams : [selected()];
    const program = state.view === 'ftc' ? 'FTC' : 'FRC';
    $('match-panel').innerHTML = `<div class="film-room-heading"><div><span class="eyebrow dark">THE FILM ROOM / LAST SEASON’S CLOSE FINISHES</span><h3>DOWN TO THE WIRE.</h3></div><p>${program === 'FRC' ? 'Pick a team above. Relive its closest finish.' : 'Two local teams. Two games worth watching.'}<br>Playoff replays included wherever available.</p></div><div class="match-grid${program === 'FTC' ? ' ftc-matches' : ''}">${teams.map((team) => matchCard(team, program)).join('')}</div>${program === 'FTC' ? state.data.ftc.newTeams.map((team) => matchCard(team, program)).join('') : ''}<div class="match-method"><p>${esc(library.scoreNote)}</p><p>${esc(library.policy)} ${link(library.methodologyUrl, 'All teams, match selections & sources ↗')}</p><small>Auto-cycle pauses while you hover or focus in the film room.</small></div>`;
    $('match-panel').hidden = false;
  }
  const header = () => `<header class="screen-header"><div class="screen-brand">THE REFINERY<small>NORTHEAST INDIANA ROBOTICS</small></div><div class="edition-tag">${state.view === 'ftc' ? 'FTC · COMPACT-ROBOT FORMAT' : 'FRC · LARGER-ROBOT FORMAT'}</div></header>`;
  const footer = () => `<footer class="screen-footer"><span><strong>REFINERYROBOTICS.ORG</strong><br>${esc(state.data.scope.label)}</span><span>${state.view === 'ftc' ? `${esc(state.data.ftc.season)} · Last season’s FTC OPR` : `Preseason baseline · 2026 EPA · ${esc(date(state.data.edition.rankingsDate))}`}<br>Research: ${esc(date(state.data.edition.researchDate))} · Historical snapshot</span></footer><div class="screen-bottom-stripe" aria-hidden="true"></div>`;

  function boardMarkup() {
    const team = selected();
    return `${header()}<div class="screen-title-row"><div><div class="screen-kicker">2026 PERFORMANCE REWIND / NORTHEAST INDIANA</div><h2 class="screen-title">THE REGIONAL <em>TOP 10</em></h2></div><div class="screen-title-note">Preseason baseline · last season’s results<br>Statbotics EPA · FRC teams only</div></div><div class="screen-content"><div class="rankings"><div class="table-labels"><span>RK</span><span>SCHOOL / TEAM</span><span>EPA</span></div>${state.data.top10.map((t, i) => `<button class="ranking-row" data-team="${i}" aria-current="${i === state.selected}" aria-label="Rank ${t.rank}: ${esc(schoolName(t))}, ${esc(t.name)}, team ${t.number}, EPA ${num(t.epa, 2)}"><span class="row-rank">${esc(t.rank).padStart(2, '0')}</span><span class="row-identity">${identityBadge(t, 'school', true)}<span class="row-copy"><span class="row-school">${esc(shortSchool(t))}</span><span class="row-name">${esc(t.name)} · ${esc(t.number)}</span></span>${identityBadge(t, 'team', true)}</span><span class="row-score">${num(t.epa, 2)}</span></button>`).join('')}</div><article class="spotlight">${teamIdentity(team)}${stats(team)}${peopleBlock(studentVoices(team), 'STUDENT VOICES / PUBLIC EVIDENCE', 'Student leadership names not verified in public sources.')}${peopleBlock(prioritizeSpotlight(team.adults || [], team), 'ADULT TEAM ROLES / PUBLIC EVIDENCE', 'Adult leadership names not verified in public sources.')}${screenMatch(team)}</article></div>${footer()}`;
  }

  function teamMarkup() {
    const team = selected();
    return `${header()}<div class="screen-title-row"><div><div class="screen-kicker">2026 REWIND / THE PEOPLE BEHIND THE ROBOT</div><h2 class="screen-title">BUILT HERE. <em>GOING PLACES.</em></h2></div></div><div class="screen-content"><article class="spotlight">${teamIdentity(team)}${stats(team)}</article><div class="team-details">${peopleBlock(studentVoices(team), 'STUDENT VOICES / PUBLIC EVIDENCE', 'No student leadership names verified in public sources.')}${peopleBlock(prioritizeSpotlight(team.adults || [], team), 'ADULT TEAM ROLES / PUBLIC EVIDENCE', 'No adult leadership names verified in public sources.')}${screenMatch(team)}</div></div>${footer()}`;
  }

  function ftcMarkup() {
    const ftc = state.data.ftc;
    const teams = ftc.teams || [];
    const featured = teams.find((team) => team.students?.length || team.adults?.length) || teams[0];
    return `${header()}<div class="screen-title-row"><div><div class="screen-kicker">2025–26 PERFORMANCE REWIND / FTC</div><h2 class="screen-title">SMALLER ROBOTS. <em>BIG STORIES.</em></h2></div><div class="screen-title-note">${esc(ftc.season)}<br>Last season’s results · separate from FRC Top 10</div></div><div class="screen-content"><div class="ftc-feature-cards">${teams.slice(0, 2).map((t) => `<article class="ftc-feature-card"><div class="screen-kicker">FTC / TEAM ${esc(t.number)} · ${esc(t.city)}</div><div class="ftc-identity-meta">${identityBadge(t, 'school')}<div class="ftc-identity-copy"><h3>${esc(t.school)}</h3><p class="ftc-feature-name">${esc(t.name)}</p></div>${identityBadge(t, 'team')}</div><div class="ftc-feature-stat"><span>${num(t.opr, 2)}</span><div>PEAK EVENT NON-PENALTY OPR<br><small>WORLD #${num(t.worldRank)} / ${num(t.worldCount)}</small></div></div>${screenMatch(t, 'FTC')}</article>`).join('')}<p class="ftc-comparison-note">Different games, different scoring models.<br>FTC OPR and FRC EPA are not directly comparable.</p></div><article class="ftc-story"><div class="screen-kicker">THE PEOPLE BEHIND THE ROBOT</div><h3>THE SKILLS<br>GO EVERYWHERE.</h3>${featured ? `${peopleBlock(featured.students?.slice(0, 1), `${esc(featured.name)} / STUDENT EVIDENCE`, 'Student leaders: names not publicly verified.')}${peopleBlock(featured.adults?.slice(0, 1), `${esc(featured.name)} / ADULT ROSTER EVIDENCE`, 'Adult leaders: names not publicly verified.')}` : ''}<div class="ftc-new"><div class="people-heading">${ftc.newTeams?.length ? 'A NEW SEASON / ON THE RADAR' : 'READING THE NUMBERS'}</div>${ftc.newTeams?.length ? ftc.newTeams.slice(0, 1).map((t) => `<strong>${esc(t.name)} / ${esc(t.number)}</strong><p>${esc(t.note || 'Registered for a future season; no ranking in this snapshot.')}</p>`).join('') : '<p>OPR estimates scoring contribution.</p>'}</div></article></div>${footer()}`;
  }

  function renderSources() {
    const data = state.data;
    const team = selected();
    $('sources-content').innerHTML = `<div><h3>WHAT THIS TOP 10 MEANS</h3><p>${esc(data.scope.note)}</p><p>${esc(data.edition.note)}</p><p>EPA is Statbotics’ estimate of robot scoring contribution. This board sorts FRC teams by the preserved 2026 EPA, not a media vote. It does not measure every student’s contribution or a program’s full impact.</p><p>Rankings snapshot: <strong>${esc(date(data.edition.rankingsDate))}</strong>. Research date: <strong>${esc(date(data.edition.researchDate))}</strong>.</p><p>${link(data.links.repo, 'Full research, source captures & methodology ↗')}</p></div><div><h3>TEAM ${esc(team.number)} / ${esc(team.name).toUpperCase()}</h3><p>${sources(team.sourceUrls)}</p><p>People are shown with the exact role and date supported by public evidence. A historical captain, event representative, or mentor is not automatically a current captain or head coach. Full qualifications appear in presenter notes.</p><h3>SCHOOL & TEAM MARKS</h3><p>${logoSources(team) || 'No verified marks available for this profile.'}</p><p><a href="logo-credits.md" target="_blank">All logo sources and qualifications ↗</a></p><h3>THE CLOSEST FINISHES</h3><p>${esc(data.matchHighlights.policy)}</p><p>${esc(data.matchHighlights.scoreNote)} ${link(data.matchHighlights.methodologyUrl, 'Full match selections, replays & sources ↗')}</p><h3>FTC IS A SEPARATE FORMAT</h3><p>${esc(data.ftc.note)}</p><p>${sources((data.ftc.teams || []).flatMap((t) => t.sourceUrls || []).slice(0, 8))}</p></div>`;
  }

  function renderPresenter() {
    const team = selected();
    const personList = (records, empty) => records?.length ? records.map((p) => `<div class="presenter-person"><strong>${esc(p.name)}</strong> · ${esc(p.role)}<br>${esc(date(p.date))}${p.season ? ` · ${esc(p.season)}` : ''}${p.dateBasis ? `<br>${esc(p.dateBasis)}` : ''}${p.status ? ` · ${esc(p.status)}` : ''}${p.note ? `<br>${esc(p.note)}` : ''}${p.sourceUrls?.length ? `<br>${sources(p.sourceUrls)}` : ''}</div>`).join('') : `<p>${empty}</p>`;
    const teamNotes = `<div><h4>THE TALKING POINTS</h4><ul>${(team.talkingPoints || [story(team)]).map((s) => `<li>${esc(s)}</li>`).join('')}</ul><p style="margin-top:12px">Regional #${esc(team.rank)} · ${esc(schoolName(team))} · Team ${esc(team.number)}<br>EPA ${num(team.epa, 2)} · Indiana rank ${num(team.stateRank)} of ${num(team.stateCount)} · World rank ${num(team.worldRank)} of ${num(team.worldCount)}</p>${matchNotes(team)}<h4>QUALIFICATIONS & REPORTING GAPS</h4><ul>${(team.gaps?.length ? team.gaps : ['Confirm the current season’s roster with the team before introducing a person by a current role.']).map((g) => `<li>${esc(g)}</li>`).join('')}</ul><p style="margin-top:12px">${team.profileUrl ? link(team.profileUrl, 'Team profile ↗') : ''}${team.profileUrl && team.sourceUrls?.length ? ' · ' : ''}${sources(team.sourceUrls)}</p></div><div><h4>STUDENTS / EXACT PUBLIC ROLE</h4>${personList(team.students, 'Student leadership names have not been verified in public sources.')}${team.representatives?.length ? `<h4>PUBLIC REPRESENTATIVES / STATUS AS QUALIFIED</h4>${personList(team.representatives, '')}` : ''}<h4>ADULTS / EXACT PUBLIC ROLE</h4>${personList(team.adults, 'Adult leadership names have not been verified in public sources.')}</div>`;
    const ftcNotes = `<div><h4>THE FORMAT</h4><p>${esc(state.data.ftc.note)}</p><p>FTC has compact robots and often smaller teams; FRC has larger robots and often larger programs. FIRST does not divide the programs by school size. Both offer their own game and championships.</p><p>Never compare FTC OPR directly to FRC EPA. The metrics describe different games.</p>${state.data.ftc.teams.map((t) => matchNotes(t, 'FTC')).join('')}</div><div><h4>PUBLIC LEADERSHIP EVIDENCE</h4>${state.data.ftc.teams.filter((t) => t.students?.length || t.adults?.length).map((t) => `<p><strong>${esc(t.name)} / ${esc(t.number)}</strong></p>${personList([...(t.students || []), ...(t.adults || [])], '')}`).join('') || '<p>No public leadership records in this snapshot.</p>'}</div>`;
    $('presenter-panel').innerHTML = `<div class="presenter-top"><h3 id="presenter-title">${state.view === 'ftc' ? 'FTC / PRODUCER NOTES' : `TEAM ${esc(team.number)} / PRODUCER NOTES`}</h3><span>OFF-AIR NOTES · EXCLUDED FROM PNG</span></div><div class="presenter-grid">${state.view === 'ftc' ? ftcNotes : teamNotes}</div><p class="presenter-warning">Historical snapshot. Confirm current student and adult roles before an on-air introduction. These notes are separate from the clean broadcast frame.</p>`;
    $('presenter-panel').hidden = !state.presenter;
  }

  function render() {
    if (!state.data) return;
    frame.className = `on-air-frame ${state.view === 'team' ? 'team-screen' : state.view === 'ftc' ? 'ftc-screen' : 'board-screen'}`;
    frame.innerHTML = state.view === 'team' ? teamMarkup() : state.view === 'ftc' ? ftcMarkup() : boardMarkup();
    frame.setAttribute('aria-busy', 'false');
    document.querySelectorAll('[data-view]').forEach((button) => button.setAttribute('aria-selected', String(button.dataset.view === state.view)));
    frame.querySelectorAll('[data-team]').forEach((button) => button.addEventListener('click', () => selectTeam(Number(button.dataset.team))));
    renderMatches();
    renderPresenter();
    renderSources();
  }

  function readHash() {
    const hash = location.hash.replace(/^#/, '');
    const match = hash.match(/^(team|spotlight)\/(\d+)$/);
    if (match) {
      const index = state.data.top10.findIndex((team) => String(team.number) === match[2]);
      if (index >= 0) state.selected = index;
      state.view = match[1] === 'spotlight' ? 'team' : 'board';
    } else if (hash === 'ftc') state.view = 'ftc';
    else state.view = 'board';
    render();
  }

  function route(view) {
    state.view = view;
    const hash = view === 'team' ? `#spotlight/${selected().number}` : view === 'board' ? `#team/${selected().number}` : `#${view}`;
    history.replaceState(null, '', hash);
    render();
  }

  function selectTeam(index, automatic = false) {
    state.selected = (index + state.data.top10.length) % state.data.top10.length;
    if (state.view === 'ftc') state.view = 'board';
    const keepSection = automatic && location.hash && !/^#(?:broadcast|board|(?:team|spotlight)\/\d+)$/.test(location.hash);
    if (!keepSection) history.replaceState(null, '', `#${state.view === 'team' ? 'spotlight' : 'team'}/${selected().number}`);
    render();
  }

  function setAutoCycle(enabled) {
    clearInterval(state.cycle);
    state.cycle = enabled && state.data ? setInterval(() => {
      if (!document.hidden && !state.exporting && state.view !== 'ftc' && !$('match-panel')?.matches(':hover, :focus-within') && !frame.querySelector('.screen-replay:hover, .screen-replay:focus-within, a:hover, a:focus-visible')) selectTeam(state.selected + 1, true);
    }, 12000) : null;
  }

  function toggleNotes() {
    state.presenter = !state.presenter;
    $('notes-button').setAttribute('aria-pressed', String(state.presenter));
    $('presentation-notes-button').setAttribute('aria-pressed', String(state.presenter));
    renderPresenter();
  }

  function setPresentation(active) {
    state.presentation = active;
    $('stage').classList.toggle('is-presenting', active);
    document.body.classList.toggle('presenting', active);
    $('fullscreen-button').setAttribute('aria-pressed', String(active));
    if (active) $('stage').append($('presenter-panel'));
    else $('match-panel').after($('presenter-panel'));
  }

  function toggleFullscreen() {
    setPresentation(!state.presentation);
    setStatus(state.presentation ? 'Presentation mode enabled. Press Esc or choose Exit to return.' : 'Presentation mode closed.');
  }

  async function exportPng() {
    if (state.exporting || !state.data) return;
    state.exporting = true;
    $('export-button').disabled = true;
    setStatus('Preparing the clean 1920 × 1080 broadcast image…');
    try {
      // Inline resolved styles so the exported frame has no stylesheet or font requests.
      const bounds = frame.getBoundingClientRect();
      const clone = frame.cloneNode(true);
      const originalNodes = [frame, ...frame.querySelectorAll('*')];
      const clonedNodes = [clone, ...clone.querySelectorAll('*')];
      originalNodes.forEach((element, index) => {
        const computed = getComputedStyle(element);
        let rules = '';
        for (let p = 0; p < computed.length; p++) {
          const property = computed[p];
          if (!property.startsWith('--')) rules += `${property}:${computed.getPropertyValue(property)};`;
        }
        clonedNodes[index].setAttribute('style', `${rules}transition:none;animation:none;`);
        clonedNodes[index].removeAttribute('aria-current');
      });
      // Data URLs keep local school/team marks inside the self-contained SVG canvas.
      await Promise.all(originalNodes.map(async (element, index) => {
        if (element.tagName !== 'IMG') return;
        const response = await fetch(element.currentSrc || element.src);
        if (!response.ok) throw new Error('An image could not be loaded for export.');
        const blob = await response.blob();
        const dataUrl = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsDataURL(blob);
        });
        clonedNodes[index].setAttribute('src', dataUrl);
        clonedNodes[index].removeAttribute('srcset');
      }));
      clone.setAttribute('xmlns', 'http://www.w3.org/1999/xhtml');
      clone.style.width = `${bounds.width}px`;
      clone.style.height = `${bounds.height}px`;
      clone.style.margin = '0';
      const serialized = new XMLSerializer().serializeToString(clone);
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 ${bounds.width} ${bounds.height}"><foreignObject x="0" y="0" width="${bounds.width}" height="${bounds.height}">${serialized}</foreignObject></svg>`;
      const image = new Image();
      const imageUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
      await new Promise((resolve, reject) => { image.onload = resolve; image.onerror = () => reject(new Error('The browser could not render the export.')); image.src = imageUrl; });
      const canvas = document.createElement('canvas');
      canvas.width = 1920; canvas.height = 1080;
      const context = canvas.getContext('2d');
      if (!context) throw new Error('Canvas is unavailable.');
      context.fillStyle = '#123d2b'; context.fillRect(0, 0, 1920, 1080);
      context.drawImage(image, 0, 0, 1920, 1080);
      const blob = await new Promise((resolve, reject) => canvas.toBlob((result) => result ? resolve(result) : reject(new Error('PNG export is unavailable.')), 'image/png'));
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `refinery-${state.view === 'ftc' ? 'ftc-features' : state.view === 'team' ? `frc-${selected().number}` : `nei-top10-spotlight-${selected().number}`}-2026.png`;
      document.body.append(anchor); anchor.click(); anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 5000);
      setStatus('1920 × 1080 PNG exported. Presenter notes are excluded.');
    } catch (error) {
      console.warn('Broadcast export:', error);
      setStatus('This browser could not export the image. Use full screen for presentation, or Print → Save as PDF for a clean frame.');
    } finally {
      state.exporting = false;
      $('export-button').disabled = false;
    }
  }

  document.querySelectorAll('[data-view]').forEach((button) => button.addEventListener('click', () => { if (state.data) route(button.dataset.view); }));
  $('notes-button').addEventListener('click', () => { if (state.data) toggleNotes(); });
  $('presentation-notes-button').addEventListener('click', () => { if (state.data) toggleNotes(); });
  $('presentation-exit-button').addEventListener('click', toggleFullscreen);
  $('fullscreen-button').addEventListener('click', toggleFullscreen);
  $('export-button').addEventListener('click', exportPng);
  $('cycle-toggle').addEventListener('change', (event) => {
    setAutoCycle(event.target.checked);
    if (event.target.checked) setStatus('Auto-cycle enabled: the selected FRC team changes every 12 seconds.');
    else setStatus('Auto-cycle stopped.');
  });
  document.addEventListener('keydown', (event) => {
    if (!state.data || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName) || event.target.isContentEditable || event.ctrlKey || event.metaKey || event.altKey) return;
    if (event.target.closest('#match-panel')) return;
    const bounds = frame.getBoundingClientRect();
    if (!state.presentation && !event.target.closest('#broadcast') && (bounds.bottom < 0 || bounds.top > innerHeight)) return;
    if (['ArrowLeft', 'ArrowUp', 'ArrowRight', 'ArrowDown'].includes(event.key)) { event.preventDefault(); selectTeam(state.selected + (['ArrowLeft', 'ArrowUp'].includes(event.key) ? -1 : 1)); }
    else if (/^[0-9]$/.test(event.key)) { event.preventDefault(); selectTeam(event.key === '0' ? 9 : Number(event.key) - 1); }
    else if (event.key.toLowerCase() === 'f') { event.preventDefault(); toggleFullscreen(); }
    else if (event.key.toLowerCase() === 'p') { event.preventDefault(); toggleNotes(); }
    else if (event.key === 'Escape' && state.presentation) { event.preventDefault(); toggleFullscreen(); }
    else if (event.key === 'Escape' && state.presenter) { state.presenter = false; $('notes-button').setAttribute('aria-pressed', 'false'); $('presentation-notes-button').setAttribute('aria-pressed', 'false'); renderPresenter(); }
  });
  window.addEventListener('hashchange', () => { if (state.data) readHash(); });

  fetch('data.json', { cache: 'no-cache' }).then((response) => {
    if (!response.ok) throw new Error(`Dataset request returned ${response.status}.`);
    return response.json();
  }).then((data) => {
    if (!Array.isArray(data.top10) || !data.top10.length || !data.edition || !data.scope || !data.ftc || !data.links) throw new Error('The broadcast dataset is incomplete.');
    state.data = data;
    Object.values(data.videoThumbnails || {}).forEach((thumbnail) => { const preview = new Image(); preview.src = thumbnail.file; });
    renderSeasonPreview();
    renderDnf();
    if (data.links.pressKit) $('press-kit-link').href = data.links.pressKit;
    if (data.links.repo) $('research-link').href = data.links.repo;
    readHash();
    setAutoCycle($('cycle-toggle').checked);
    if (!location.hash || /^#(?:broadcast|board|ftc|(?:team|spotlight)\/\d+)$/.test(location.hash)) document.querySelector('.studio-toolbar').scrollIntoView({ behavior: 'instant', block: 'start' });
    if (location.hash === '#season-preview' && data.seasonPreview) $('season-preview').scrollIntoView({ behavior: 'auto', block: 'start' });
    if (location.hash === '#dnf' && data.dnf) $('dnf').scrollIntoView({ behavior: 'auto', block: 'start' });
  }).catch((error) => {
    console.warn('Broadcast dataset:', error);
    frame.innerHTML = '<div class="loading-state"><span class="screen-brand">THE REFINERY</span><h3>THE RUNDOWN IS TAKING A TIMEOUT.</h3><p>The research snapshot could not be loaded.<br>Refresh the page, or open the full research below.</p></div>';
    frame.setAttribute('aria-busy', 'false');
    setStatus(location.protocol === 'file:' ? 'Serve this folder with a local web server to load data.json. For example: python3 -m http.server 8000' : 'The local data.json file could not be loaded. Refresh the page or consult the research repository.');
    ['export-button', 'notes-button', 'cycle-toggle', 'tab-board', 'tab-team', 'tab-ftc'].forEach((id) => { $(id).disabled = true; });
  });
})();
