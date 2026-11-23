# Leadership and spokesperson findings

Research snapshot: **October 22, 2026**. This evidence ledger covers the **17 FIRST Robotics Competition teams** in the repository's Fort Wayne area census. It preserves school and program identities alongside team numbers. It is a dated research record, not a verified directory of current appointments.

The structured companion is [leadership.json](../data/leadership.json). School and program labels below link to the corresponding 2026 FIRST team profile. Community teams may include students from multiple schools; the school connection shown here is not an exclusive enrollment claim. Geography, competition history and Statbotics rankings are documented elsewhere in the repository.

## How to read the findings

A named coach, mentor, president, sponsor, student representative and student captain are different roles. The role supported by the source is retained. A drive-team captain is not automatically the overall team captain. A student interviewee or school-board representative is not automatically a captain. Earlier appointments and graduating seniors are not carried forward to the 2026–27 school year without evidence.

`Unverified` means the public sources examined did not establish the requested role. It does not mean the team lacks that role. No private contact details are included, and no one was contacted during this research.

### Evidence dates and structured fields

Each JSON team record contains `team_number`, `adults`, `students`, `other_representatives` and `gaps`. Each person-role record contains `name`, `role`, `evidence_date`, `date_precision`, `source_urls`, `evidence_status` and `notes`.

- `adults` holds documented adult coaches, mentors, officers or spokespeople. A title such as mentor is not promoted to head coach.
- `students` holds documented student leadership, including historical or qualified evidence. It is not a list of currently enrolled captains. A former student can appear here because the documented role was held as a student.
- `other_representatives` holds public student representatives and interviewees, plus people whose student/adult status or formal leadership role remains unknown. Nick Sims appears in two categories because a captain claim and a separate representative appearance have different sources.
- `evidence_date` is a known source publication, broadcast or meeting date, or an explicitly documented year/school year. `date_precision` explains the granularity. A null date means no reliable publication date was established. Historical tenure dates are retained in `notes` rather than treated as source publication dates.
- A date on an article does not necessarily date a dynamically updated contributor biography. A social-account URL does not provide the permanence of an individual post permalink. Those limitations are recorded explicitly.

| Evidence status | Meaning |
| --- | --- |
| `verified_dated` | A retrieved dated source explicitly establishes the stated role. |
| `verified_historical` | A source establishes an earlier role; continued appointment is unverified. |
| `verified_undated` | A retrieved undated source establishes the role, sometimes with an explicit role year. |
| `self_reported_undated` | A public professional profile reports the role; the profile is undated. |
| `self_reported_historical` | An undated public professional profile reports a completed earlier tenure. |
| `qualified_indexed` | Evidence includes search-indexed content whose full post or biography was not retrieved. |
| `qualified_indexed_historical` | Indexed content supports an earlier role; current service is unverified. |
| `verified_dated_retrospective` | A dated interview describes a prior role, without establishing a current appointment. |
| `verified_dated_bio` | The role is in a contributor biography attached to a dated article; the biography has no separate timestamp. |
| `verified_role_status_unknown` | The public role is documented, but student/adult classification is unknown. |
| `verified_role_name_discrepancy` | The role is documented, but the source conflicts internally on the person's name. |

These labels describe the available evidence, not a numerical confidence score. Every person-role record links to its supporting public sources. Original publisher URLs are retained when useful, even when an accessible republication supplied the text.

## Team overview

The detailed evidence and qualifications follow the table. Dates below refer to the documented evidence, not a guaranteed current appointment.

| Team | School or program | Adult finding | Student leadership or representative finding |
| --- | --- | --- | --- |
| 1501 · T.H.R.U.S.T. | [Huntington County 4-H; Huntington North High School connection](https://frc-events.firstinspires.org/2026/team/1501) | Chris Elston: engineering lead, self-reported undated profile | Captain unverified |
| 3777 · Bean City Bots | [Lima Family YMCA; Lima Senior High School participant](https://frc-events.firstinspires.org/2026/team/3777) | Skylynn Prine: YMCA program spokesperson (March 2026) | Coltin Myers: quoted student; captain unverified |
| 4982 · Olympus Robotics | [Homestead High School](https://frc-events.firstinspires.org/2026/team/4982) | Matt Elder: lead coach/mentor; Cameron Elder: assistant coach (undated) | Jasroop/Jake: 2025–26 captain/assistant pair, qualified; Caleb Neely: business/outreach leader |
| 5559 · Gear Grinders | [Camden-Frontier High School](https://frc-events.firstinspires.org/2026/team/5559) | Unverified | Captain unverified |
| 6556 · Spartan Robotics | [Waldron High School](https://frc-events.firstinspires.org/2026/team/6556) | Mike Fuller: coach in 2023–24 | Captain unverified; Elijah: contact with unknown status |
| 8103 · Knight Robotics | [East Noble High School](https://frc-events.firstinspires.org/2026/team/8103) | Shawn Kimmel and Jo Smith: coaches; Collin Haynes and Tucker Martin: mentors (2024) | Captain unverified |
| 8431 · Robo-Knights | [East Noble High School](https://frc-events.firstinspires.org/2026/team/8431) | Individual assignment unverified | Captain unverified |
| 8432 · Cyber Knights | [East Noble High School](https://frc-events.firstinspires.org/2026/team/8432) | Individual assignment unverified | Captain unverified |
| 8742 · Argyll Attack | [Madison-Grant Junior/Senior High School](https://frc-events.firstinspires.org/2026/team/8742) | Eric Cale: teacher and spokesperson (April 2026) | Captain unverified; Ava Stanley: spokesperson, student/adult status unknown |
| 9119 · Iron Legends | [North Side High School](https://frc-events.firstinspires.org/2026/team/9119) | Dennis Fisher: coach/teacher; Drew Clem: college mentor (January 2025) | Zen Gunawardhana: representative, February 2026; captain unverified |
| 9431 · Snider Panthers / The Gold Standard | [R. Nelson Snider High School](https://frc-events.firstinspires.org/2026/team/9431) | John Todor: qualified founding-coach evidence; Doug Horner: sponsor/spokesperson (2024) | Nick Sims: recent captain, retrospective interview; Nick Sims/Connor Rey: representatives |
| 10172 · Apex Archers | [South Side High School](https://frc-events.firstinspires.org/2026/team/10172) | Unverified | David Haruna: representative, February 2026; captain unverified |
| 10332 · Carroll Charger Robotics | [Carroll High School](https://frc-events.firstinspires.org/2026/team/10332) | Mady Stricker: mentor; historical coaches Cameron Elder and Matt Arnold | Nieng Mang: 2025–26 captain; 2026–27 successor unverified |
| 10411 · G-Code Generals | [Wayne High School](https://frc-events.firstinspires.org/2026/team/10411) | Unverified | Khai Phyoe: representative, February 2026; captain unverified |
| 10434 · CyBears | [Northrop High School](https://frc-events.firstinspires.org/2026/team/10434) | Coach Jacobs: partial name in undated indexed team post | Alfy Krider: representative and 2026 senior; captain unverified |
| 11407 · Sturgis High School robotics | [Sturgis High School](https://frc-events.firstinspires.org/2026/team/11407) | Khanya Sigwela and Xandra/Sandra Duelge: coaches (March 2026) | Krys/Krystina Johnson: drive-team captain; overall captain unverified |

## Shared FWCS evidence

The official [FWCS high-school robotics presentation dated February 9, 2026](https://resources.finalsite.net/images/v1770749036/fwcsk12inus/v2dggvv52hkh9sfiqsme/2-9-26Presentation_Roboticshighschool.pdf), page 7, identifies **team representatives**: Zen Gunawardhana for North Side, Alfy Krider for Northrop, Nick Sims and Connor Rey for Snider, David Haruna for South Side, and Khai Phyoe for Wayne. The presentation does not assign captain titles to those students. The same distinction is retained in each team record below.

## Detailed team evidence

### 1501 — T.H.R.U.S.T.

**School or program:** [Huntington County 4-H; Huntington North High School connection](https://frc-events.firstinspires.org/2026/team/1501).

**Adults**

- **Chris Elston — Lead Engineering Mentor, Huntington 4-H Robotics.** Evidence: undated (undated); `self_reported_undated`. Public professional profile lists July 2004 to Present. A 2025 public post corroborates his association with THRUST 1501. The profile is undated; the head-coach title and a 2026-27 appointment are not independently verified.
  Sources: [Chris Elston: public professional profile](https://www.linkedin.com/in/chriselston); [Chris Elston: 2025 public team post](https://www.linkedin.com/posts/chriselston_this-is-my-yearly-first-robotics-plug-to-activity-7302732445911527424-p7cI).

**Remaining gaps**

- Student team captain not verified.
- Current formally designated head coach not independently verified; the documented title is Lead Engineering Mentor.

### 3777 — Bean City Bots

**School or program:** [Lima Family YMCA; Lima Senior High School participant](https://frc-events.firstinspires.org/2026/team/3777).

**Adults**

- **Skylynn Prine — Teen Development Director, Lima Family YMCA; program spokesperson.** Evidence: 2026-03-17 (day); `verified_dated`. Quoted about the robotics program in local reporting. The article does not identify her as the head coach.
  Sources: [Hometown Stations: Bean City Bots, March 17, 2026](https://www.hometownstations.com/news/allen_county/lima-bean-city-bots-ready-robot-for-first-robotics-competition-buckeye-regional/article_e5d3d483-ada8-4a44-91a8-361777fc6b54.html).

**Other public representatives**

- **Coltin Myers — Quoted student team member; Lima Senior High School senior.** Evidence: 2026-03-17 (day); `verified_dated`. Public student interviewee, with no formal captain or appointed spokesperson title established. Senior status belongs to March 2026; current student status is unverified.
  Sources: [Hometown Stations: Bean City Bots, March 17, 2026](https://www.hometownstations.com/news/allen_county/lima-bean-city-bots-ready-robot-for-first-robotics-competition-buckeye-regional/article_e5d3d483-ada8-4a44-91a8-361777fc6b54.html).

**Remaining gaps**

- Head coach not verified.
- Student team captain not verified.

### 4982 — Olympus Robotics

**School or program:** [Homestead High School](https://frc-events.firstinspires.org/2026/team/4982).

**Adults**

- **Matt Elder — Lead coach / mentor.** Evidence: undated (undated); `self_reported_undated`. Role appears on a public professional profile. No dated school appointment or current-season appointment was independently verified.
  Sources: [Matt Elder: public professional profile](https://www.linkedin.com/in/matt-elder-24b8b615a).
- **Cameron Elder — Assistant coach.** Evidence: undated (undated); `verified_undated`. The REFINERY biography expressly identifies him as assistant coach of Team 4982. It also identifies him as a graduate and former student captain, so he is not listed as a current student captain.
  Sources: [The REFINERY: people and team biographies](https://refineryrobotics.org/about/).

**Documented student leadership**

- **Jasroop — Named in the team captain / assistant captain announcement.** Evidence: 2025-2026 (school year); `qualified_indexed`. Official team account search-indexed caption pairs Jasroop and Jake with captain and assistant captain for 2025-2026, in that order. A full surname, stable post permalink, and independent confirmation of the individual title assignment were not retrieved. Do not silently convert the caption order into a verified individual appointment.
  Sources: [Olympus Robotics official Instagram account; indexed caption](https://www.instagram.com/4982_olympus_robotics/).
- **Jake — Named in the team captain / assistant captain announcement.** Evidence: 2025-2026 (school year); `qualified_indexed`. Official team account search-indexed caption pairs Jasroop and Jake with captain and assistant captain for 2025-2026, in that order. Only the first name is verified. The individual assignment and a stable post permalink remain unverified.
  Sources: [Olympus Robotics official Instagram account; indexed caption](https://www.instagram.com/4982_olympus_robotics/).
- **Caleb Neely — Co-Business Manager and Outreach Director.** Evidence: 2026 (year); `verified_undated`. An undated official partner biography expressly associates these roles with 2026. This establishes student leadership but does not establish the team-captain role.
  Sources: [The REFINERY: people and team biographies](https://refineryrobotics.org/about/).

**Remaining gaps**

- Captain and assistant-captain surnames and individual title assignments require confirmation.
- The captain announcement is indexed account content, with no retrieved individual post permalink.
- A 2026-27 student captain is not verified.

### 5559 — Gear Grinders

**School or program:** [Camden-Frontier High School](https://frc-events.firstinspires.org/2026/team/5559).

The public research did not establish a named adult lead or student captain for this team. The FIRST profile above documents the team identity, not a leadership assignment.

**Remaining gaps**

- Adult coach or designated adult team spokesperson not verified.
- Student team captain not verified.

### 6556 — Spartan Robotics

**School or program:** [Waldron High School](https://frc-events.firstinspires.org/2026/team/6556).

**Adults**

- **Mike Fuller — Robotics coach; open-house contact.** Evidence: 2024-01 (month); `qualified_indexed_historical`. Official school posts name Mike Fuller as a contact on December 13, 2023 and refer to Coach Fuller at FIRST kickoff in early January 2024. Evidence was recovered from indexed official posts; live-feed pagination changes. This is historical evidence, not a verified 2026-27 appointment.
  Sources: [Waldron school live feed: indexed January 2024 posts](https://www.waldronspartans.org/live-feed?page_no=66); [Waldron school live feed: indexed December 2023 post](https://www.waldronspartans.org/live-feed?page_no=67).

**Other public representatives**

- **Elijah — Named robotics open-house contact; precise role unknown.** Evidence: 2023-12-13 (day); `qualified_indexed_historical`. School post names Elijah alongside Mike Fuller for questions. Surname, student/adult status, and leadership position were not established; this is not evidence of a captain role.
  Sources: [Waldron school live feed: indexed December 2023 post](https://www.waldronspartans.org/live-feed?page_no=67).

**Remaining gaps**

- Current adult coaching assignment not verified beyond the 2023-24 evidence.
- Student team captain not verified.
- Elijah has an incomplete name and unknown student/adult and leadership status.

### 8103 — Knight Robotics

**School or program:** [East Noble High School](https://frc-events.firstinspires.org/2026/team/8103).

**Adults**

- **Shawn Kimmel — Coach; engineering and physics teacher.** Evidence: 2024-05-11 (day); `verified_historical`. KPC News Sun reporting, available in a republication dated May 11, 2024, explicitly identifies Team 8103 and its coaches. That date is the republication date. An older Trine University article corroborates his involvement in founding the program; its precise publication date is not used here.
  Sources: [KPC News Sun report: accessible republication, May 11, 2024](https://www.euvolution.com/prometheism-transhumanism-posthumanism/robotics/en-robotics-team-demonstrates-real-world-learning-news-sun-kpcnews-com-kpcnews-com/); [Original KPC News Sun article URL; access unavailable during verification](https://www.kpcnews.com/newssun/article_01fef033-f9cb-525e-82e8-676e717dee03.html); [Trine University: East Noble program history](https://www.trine.edu/news/2019/east-noble-robotics.aspx).
- **Jo Smith — Coach.** Evidence: 2024-05-11 (day); `verified_historical`. Named as a Team 8103 coach in the KPC News Sun report. Evidence date is the available republication date; continued appointment in 2026-27 is unverified.
  Sources: [KPC News Sun report: accessible republication, May 11, 2024](https://www.euvolution.com/prometheism-transhumanism-posthumanism/robotics/en-robotics-team-demonstrates-real-world-learning-news-sun-kpcnews-com-kpcnews-com/); [Original KPC News Sun article URL; access unavailable during verification](https://www.kpcnews.com/newssun/article_01fef033-f9cb-525e-82e8-676e717dee03.html).
- **Collin Haynes — Mentor.** Evidence: 2024-05-11 (day); `verified_historical`. Named as a mentor, separately from the coaches. Evidence date is the republication date; no current head-coach or captain role is asserted.
  Sources: [KPC News Sun report: accessible republication, May 11, 2024](https://www.euvolution.com/prometheism-transhumanism-posthumanism/robotics/en-robotics-team-demonstrates-real-world-learning-news-sun-kpcnews-com-kpcnews-com/); [Original KPC News Sun article URL; access unavailable during verification](https://www.kpcnews.com/newssun/article_01fef033-f9cb-525e-82e8-676e717dee03.html).
- **Tucker Martin — Mentor.** Evidence: 2024-05-11 (day); `verified_historical`. Named as a mentor, separately from the coaches. Evidence date is the republication date; no current head-coach or captain role is asserted.
  Sources: [KPC News Sun report: accessible republication, May 11, 2024](https://www.euvolution.com/prometheism-transhumanism-posthumanism/robotics/en-robotics-team-demonstrates-real-world-learning-news-sun-kpcnews-com-kpcnews-com/); [Original KPC News Sun article URL; access unavailable during verification](https://www.kpcnews.com/newssun/article_01fef033-f9cb-525e-82e8-676e717dee03.html).

**Remaining gaps**

- Current 2026-27 coaching assignments not confirmed by the historical article.
- Student team captain not verified.
- Team 8103 leadership evidence does not establish individual coaching assignments for teams 8431 or 8432.

### 8431 — Robo-Knights

**School or program:** [East Noble High School](https://frc-events.firstinspires.org/2026/team/8431).

East Noble has multiple FRC teams. The 2024 report used for Team 8103 explicitly names that team. It does not establish individual leadership assignments for Team 8431. [The REFINERY team directory](https://refineryrobotics.org/about/) corroborates the shared school program; leadership is left unassigned.

**Remaining gaps**

- Individual adult coach or adult team spokesperson not verified.
- Student team captain not verified.
- The shared East Noble school program does not establish that the documented Team 8103 coaches also coach Team 8431.

### 8432 — Cyber Knights

**School or program:** [East Noble High School](https://frc-events.firstinspires.org/2026/team/8432).

East Noble has multiple FRC teams. The 2024 report used for Team 8103 explicitly names that team. It does not establish individual leadership assignments for Team 8432. [The REFINERY team directory](https://refineryrobotics.org/about/) corroborates the shared school program; leadership is left unassigned.

**Remaining gaps**

- Individual adult coach or adult team spokesperson not verified.
- Student team captain not verified.
- The shared East Noble school program does not establish that the documented Team 8103 coaches also coach Team 8432.

### 8742 — Argyll Attack

**School or program:** [Madison-Grant Junior/Senior High School](https://frc-events.firstinspires.org/2026/team/8742).

**Adults**

- **Eric Cale — Robotics and chemistry teacher; team spokesperson.** Evidence: 2026-04-07 (day); `verified_dated`. School-authored podcast features Cale discussing his robotics team. The documented teacher and spokesperson roles do not establish a formal head-coach appointment.
  Sources: [School podcast: Eric Cale and Robotics, April 7, 2026](https://podcasts.apple.com/ma/podcast/eric-cale-and-robotics/id1773140582?i=1000760060708).

**Other public representatives**

- **Ava Stanley — Team spokesperson at Fairmount Town Council.** Evidence: 2025-09-08 (day); `verified_role_status_unknown`. Official minutes identify the team spokesperson. The evidence date is the meeting date; upload timing is different. Student/adult status and captain status are not established.
  Sources: [Fairmount council minutes: September 8, 2025 meeting](https://static1.squarespace.com/static/5dc440cbaed3360b099cc5e8/t/68e97523a86b466f4093381a/1760130339609/Regular%2BMeeting%2BMinutes%2B09.08.2025.pdf).

**Remaining gaps**

- Student team captain not verified.
- Ava Stanley cannot be classified as a student or adult from the cited evidence.
- A formal head-coach title for Eric Cale was not established.

### 9119 — Iron Legends

**School or program:** [North Side High School](https://frc-events.firstinspires.org/2026/team/9119).

**Adults**

- **Dennis Fisher — Coach and North Side teacher.** Evidence: 2025-01-23 (day); `verified_historical`. FWCS board minutes dated March 13, 2023 explicitly identify Fisher as coach of the Iron Legends. Purdue Fort Wayne reporting on January 23, 2025 corroborates his teaching and team-guidance role. A 2026-27 appointment was not verified.
  Sources: [Purdue Fort Wayne: North Side robotics, January 23, 2025](https://www.pfw.edu/news-center/north-side-robotics-team-boosted-pfw-presence); [FWCS board minutes: March 13, 2023](https://resources.finalsite.net/images/v1685982230/fwcsk12inus/us2rusjsudqci2p1ltxv/03132023.pdf).
- **Drew Clem — College mentor.** Evidence: 2025-01-23 (day); `verified_historical`. Purdue Fort Wayne identifies Clem as an electrical engineering senior assisting the school robotics team. The role is mentor; he is not identified as lead coach or a high-school student captain.
  Sources: [Purdue Fort Wayne: North Side robotics, January 23, 2025](https://www.pfw.edu/news-center/north-side-robotics-team-boosted-pfw-presence).

**Other public representatives**

- **Zen Gunawardhana — Student team representative at FWCS board presentation.** Evidence: 2026-02-09 (day); `verified_dated`. The district presentation identifies a team representative; it does not identify a captain.
  Sources: [FWCS robotics presentation, February 9, 2026, page 7](https://resources.finalsite.net/images/v1770749036/fwcsk12inus/v2dggvv52hkh9sfiqsme/2-9-26Presentation_Roboticshighschool.pdf).

**Remaining gaps**

- Current adult lead appointment not confirmed beyond the January 2025 reporting.
- Student team captain not verified; the February 2026 presentation identifies a representative.

### 9431 — Snider Panthers / The Gold Standard

**School or program:** [R. Nelson Snider High School](https://frc-events.firstinspires.org/2026/team/9431).

**Adults**

- **John Todor — Founding-period coach; publicly identified coach/director.** Evidence: undated (undated); `qualified_indexed`. The REFINERY biography of Connor Rey identifies Mr. Todor as his coach during the founding period beginning in 2023. An indexed public event-host caption supplies John Todor and the coach/director title; its date and post permalink were not retrieved. Team-account references to Todor corroborate the connection, but a current 2026-27 appointment is not established.
  Sources: [The REFINERY: people and team biographies](https://refineryrobotics.org/about/); [Public event-host Instagram account; indexed Todor caption](https://www.instagram.com/walnuthillcatering/); [Snider Robotics official Instagram account](https://www.instagram.com/snider_robotics9431/).
- **Doug Horner — Sponsor and adult team spokesperson.** Evidence: 2024-04-12 (day); `verified_historical`. The 21Alive page displays publication on April 12, 2024 at 11:38 PM EDT, although its URL uses April 13. It describes his work with the club and quotes him about the program; The REFINERY biography corroborates rookie-year sponsorship. No formal head-coach appointment is asserted.
  Sources: [21Alive: Snider championship preparations, April 12, 2024](https://www.21alivenews.com/2024/04/13/snider-robotics-club-prepares-compete-world-championship/); [The REFINERY: people and team biographies](https://refineryrobotics.org/about/).

**Documented student leadership**

- **Nick Sims — Team captain and driver, described retrospectively in interview.** Evidence: 2026-10-02 (day); `verified_dated_retrospective`. In PBS Fort Wayne The 260, Sims identifies his team-captain role and separately describes driving. The interview is retrospective and mentions college plans. The broadcast date does not verify a current 2026-27 captain appointment or define an exact term.
  Sources: [PBS Fort Wayne: The 260, broadcast October 2, 2026](https://video.wfwa.org/video/science-centrals-new-planetarium-snider-robotics-and-arena-dinner-theatre-4j2kgy/).

**Other public representatives**

- **Nick Sims — Student team representative at FWCS board presentation.** Evidence: 2026-02-09 (day); `verified_dated`. The district presentation identifies a team representative; it does not identify a captain.
  Sources: [FWCS robotics presentation, February 9, 2026, page 7](https://resources.finalsite.net/images/v1770749036/fwcsk12inus/v2dggvv52hkh9sfiqsme/2-9-26Presentation_Roboticshighschool.pdf).
- **Connor Rey — Student team representative at FWCS board presentation.** Evidence: 2026-02-09 (day); `verified_dated`. The district presentation identifies a team representative; it does not identify a captain.
  Sources: [FWCS robotics presentation, February 9, 2026, page 7](https://resources.finalsite.net/images/v1770749036/fwcsk12inus/v2dggvv52hkh9sfiqsme/2-9-26Presentation_Roboticshighschool.pdf).

**Remaining gaps**

- Current 2026-27 student captain not verified; Nick Sims is a documented recent captain.
- John Todor identification combines an undated primary partner biography with indexed public social content.
- A current formally designated adult lead was not independently confirmed.

### 10172 — Apex Archers

**School or program:** [South Side High School](https://frc-events.firstinspires.org/2026/team/10172).

**Other public representatives**

- **David Haruna — Student team representative at FWCS board presentation.** Evidence: 2026-02-09 (day); `verified_dated`. The district presentation identifies a team representative; it does not identify a captain.
  Sources: [FWCS robotics presentation, February 9, 2026, page 7](https://resources.finalsite.net/images/v1770749036/fwcsk12inus/v2dggvv52hkh9sfiqsme/2-9-26Presentation_Roboticshighschool.pdf).

**Remaining gaps**

- Adult coach or designated adult team spokesperson not verified.
- Student team captain not verified; the February 2026 presentation identifies a representative.

### 10332 — Carroll Charger Robotics

**School or program:** [Carroll High School](https://frc-events.firstinspires.org/2026/team/10332).

**Adults**

- **Mady Stricker — Mentor.** Evidence: 2026 (year); `qualified_indexed`. A FIRST Indiana 2026 indexed biography associates Stricker with mentoring Team 10332. The live board page was shorter at retrieval. This is mentor evidence and does not establish a head-coach role.
  Sources: [FIRST Indiana board biographies; indexed 2026 mentor description](https://www.firstindianarobotics.org/about-first-indiana-robotics/board-of-directors/).
- **Cameron Elder — Former head coach.** Evidence: undated (undated); `self_reported_historical`. Public professional profile reports the Team 10332 head-coach tenure as April through October 2025. The profile itself is undated; this is a past appointment, not a current coach assignment.
  Sources: [Cameron Elder: public professional profile](https://www.linkedin.com/in/camelder).
- **Matt Arnold — Former assistant coach.** Evidence: undated (undated); `self_reported_historical`. Public professional profile reports an assistant-coach tenure from October 2024 through April 2025. The profile itself is undated; continued service is not established.
  Sources: [Matt Arnold: public professional profile](https://www.linkedin.com/in/m4ttbit).

**Documented student leadership**

- **Nieng Mang — Team captain; Carroll High School senior.** Evidence: 2026-01-27 (day); `verified_dated_bio`. The school newspaper contributor biography identifies Mang as captain and a senior. January 27, 2026 is the article date; the biography itself has no separate timestamp and may be updated dynamically. The evidence supports the 2025-26 school-year identification, not a current 2026-27 appointment.
  Sources: [Carroll Charger Online: January 27, 2026 article and contributor biography](https://chargeronline.nacs.k12.in.us/12210/sports/from-worst-to-first-how-indianas-football-program-became-the-nations-best/).

**Remaining gaps**

- Current head coach not verified.
- Student captain for 2026-27 not verified.
- Mentor evidence for Mady Stricker is indexed official content rather than the full biography on the current live page.

### 10411 — G-Code Generals

**School or program:** [Wayne High School](https://frc-events.firstinspires.org/2026/team/10411).

**Other public representatives**

- **Khai Phyoe — Student team representative at FWCS board presentation.** Evidence: 2026-02-09 (day); `verified_dated`. The district presentation identifies a team representative; it does not identify a captain.
  Sources: [FWCS robotics presentation, February 9, 2026, page 7](https://resources.finalsite.net/images/v1770749036/fwcsk12inus/v2dggvv52hkh9sfiqsme/2-9-26Presentation_Roboticshighschool.pdf).

**Remaining gaps**

- Adult coach or designated adult team spokesperson not verified.
- Student team captain not verified; the February 2026 presentation identifies a representative.

### 10434 — CyBears

**School or program:** [Northrop High School](https://frc-events.firstinspires.org/2026/team/10434).

**Adults**

- **Coach Jacobs — Coach; full identity and lead responsibility unverified.** Evidence: undated (undated); `qualified_indexed`. An indexed official team Facebook caption uses Coach Jacobs. No first name, post date, stable post permalink, current appointment, or head-coach responsibility was verified. The surname was not matched to a school employee by inference.
  Sources: [Northrop Robotics official Facebook account; indexed coach caption](https://www.facebook.com/NorthropRobotics/).

**Other public representatives**

- **Alfy Krider — Student team representative; Northrop senior in March 2026.** Evidence: 2026-02-09 (day); `verified_dated`. FWCS names Krider as a team representative on February 9, 2026. March 25, 2026 reporting identifies a Northrop senior and team member; neither source establishes a captain role. Current student status is unverified.
  Sources: [FWCS robotics presentation, February 9, 2026, page 7](https://resources.finalsite.net/images/v1770749036/fwcsk12inus/v2dggvv52hkh9sfiqsme/2-9-26Presentation_Roboticshighschool.pdf); [The 74: Amp Lab report, March 25, 2026](https://www.the74million.org/article/building-a-mindset-amp-lab-makes-entrepreneurship-work-skills-its-mission/).

**Remaining gaps**

- Coach Jacobs has only a partial public name and unverified current lead responsibility.
- Student team captain not verified.
- Alfy Krider is documented as a representative and 2026 senior, not as a current 2026-27 captain.

### 11407 — Sturgis High School robotics

**School or program:** [Sturgis High School](https://frc-events.firstinspires.org/2026/team/11407).

**Adults**

- **Khanya Sigwela — Coach.** Evidence: 2026-03-27 (day); `verified_dated`. Local reporting explicitly names Sigwela as one of the coaches. It does not rank the two coaches or designate a head coach.
  Sources: [Wilcox Newspapers: Sturgis district recognition, March 27, 2026](https://wilcoxnewspapers.com/shs-robotics-team-receives-recognition-at-district-meet/).
- **Xandra Duelge — Coach.** Evidence: 2026-03-27 (day); `verified_role_name_discrepancy`. The article body uses Xandra Duelge; its photo caption uses Sandra Duelge. The coaching role is clear, but the first-name spelling remains unresolved.
  Sources: [Wilcox Newspapers: Sturgis district recognition, March 27, 2026](https://wilcoxnewspapers.com/shs-robotics-team-receives-recognition-at-district-meet/).

**Documented student leadership**

- **Krys Johnson — Drive-team captain.** Evidence: 2026-03-27 (day); `verified_dated`. The drive-team list identifies Krys Johnson as captain; a photo caption uses Krystina Johnson. This is evidence of the drive-team captain role only, not overall team captain. The caption variant is preserved without resolving the name independently.
  Sources: [Wilcox Newspapers: Sturgis district recognition, March 27, 2026](https://wilcoxnewspapers.com/shs-robotics-team-receives-recognition-at-district-meet/).

**Remaining gaps**

- Overall student team captain not verified; the published designation is drive-team captain.
- Xandra versus Sandra Duelge is an unresolved source-internal spelling discrepancy.
- The source does not specify which coach, if either, holds a head-coach title.

## Priority items for a future refresh

A current team or school roster would most directly resolve the 2026–27 coach and captain gaps. The most specific unresolved items are the full names and individual captain assignments for Olympus's Jasroop/Jake pair; the first name and responsibility of Northrop's Coach Jacobs; the student/adult status of Madison-Grant spokesperson Ava Stanley; the Xandra/Sandra spelling discrepancy in Sturgis; and individual leadership assignments for East Noble teams 8431 and 8432.

The source ledger intentionally retains historical evidence when current information is unavailable. Updates should add an explicit dated appointment or role statement and preserve this earlier evidence in repository history. An event quote, a matching surname in a school directory, or shared school affiliation is insufficient to fill a leadership gap by inference.
