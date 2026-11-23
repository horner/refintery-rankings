#!/usr/bin/env python3
"""Capture official 2026 FIRST team schedules once and rank close played matches.
Public FRC API needs credentials; Statbotics match APIs were unavailable at capture.
No credentials, bulk event crawl, or videos are guessed by this preservation script.
"""
import concurrent.futures,datetime as dt,json,re,time,urllib.request,hashlib
from pathlib import Path
from bs4 import BeautifulSoup
HERE=Path(__file__).resolve().parent
TEAMS=[1501,9119,9431,4982,10434,8103,10332,8742,10172,8431,8432,10411,5559,3777,6556,11407]
YEAR=2026
CUTOFF='2026-06-12'
BASE='https://frc-events.firstinspires.org'

def text(node): return node.get_text(' ',strip=True) if node else ''
def get(team):
    path=HERE/f'team-{team}.html'
    url=f'{BASE}/{YEAR}/team/{team}'
    if not path.exists():
        req=urllib.request.Request(url,headers={'User-Agent':'Refintery-Rankings-Public-Research/1.0','Accept-Encoding':'identity'})
        with urllib.request.urlopen(req,timeout=45) as response:
            raw=response.read(); meta={'url':url,'status':response.status,'fetchedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'sha256':hashlib.sha256(raw).hexdigest(),'lastModified':response.headers.get('Last-Modified')}
        path.write_bytes(raw)
        (HERE/f'team-{team}.metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    soup=BeautifulSoup(path.read_text(),'html.parser')
    rows=[]
    for event in soup.select('div.tab-pane'):
        if not event.select_one('h1.panel-title'): continue
        code=event['id']; title=text(event.select_one('h1.panel-title')); date=next((text(x) for x in event.select('i') if re.match(r'^[A-Z][a-z]+ \d',text(x))), '')
        # Event season pages provide month/day ranges, all within one year here.
        dates=re.match(r'([A-Za-z]+) (\d+)(?: to (?:([A-Za-z]+) )?(\d+))?, (\d{4})',date)
        if not dates: raise ValueError(f'Unparsed event date: {date}')
        month,start,end_month,end,year=dates.groups(); startdate=dt.datetime.strptime(f'{month} {start} {year}','%B %d %Y').date().isoformat(); enddate=dt.datetime.strptime(f'{end_month or month} {end or start} {year}','%B %d %Y').date().isoformat()
        for table in event.select('table#matches'):
            trs=table.select('tbody tr')
            for i,tr in enumerate(trs):
                a=tr.select_one('a[href*="/qualifications/"]') or tr.select_one('a[href*="/playoffs/"]')
                if not a: continue
                link=BASE+a['href']; phase='playoff' if '/playoffs/' in link else 'qualification'; num=int(link.rsplit('/',1)[-1]); cells=tr.find_all('td',recursive=False)
                scores=[text(cells[-2]),text(cells[-1])]
                played=all(re.fullmatch(r'\d+',v) for v in scores)
                lineup=trs[i+1] if phase=='playoff' else tr
                teamcells=[c for c in lineup.find_all('td',recursive=False) if c.get('id','').startswith('team')]
                teamnames=[text(c.select_one('a')) for c in teamcells]
                if len(teamnames)!=6: raise ValueError(f'{team} {link}: no six-team lineup {teamnames}')
                red=list(map(int,teamnames[:3])); blue=list(map(int,teamnames[3:])); target='red' if team in red else 'blue' if team in blue else None
                if not target: raise ValueError(f'{team} not actual participant {link}')
                teamattrs=[{'team':int(text(c.select_one('a'))),'title':c.select_one('a').get('title',''),'html':str(c)} for c in teamcells]
                dq=any('disqual' in item['html'].lower() or 'redcard' in item['html'].lower() or 'red-card' in item['html'].lower() for item in teamattrs)
                excluded=[]
                if not played: excluded.append('not played / missing final score')
                if enddate>CUTOFF: excluded.append('after 2026-06-12 ranking snapshot; offseason excluded')
                if dq: excluded.append('disqualification marker in alliance lineup')
                score=dict(zip(['red','blue'],map(int,scores))) if played else {'red':None,'blue':None}
                margin=abs(score['red']-score['blue']) if played else None
                row={'year':YEAR,'eventCode':code,'eventName':title,'eventStartDate':startdate,'eventEndDate':enddate,'phase':phase,'matchNumber':num,'matchLabel':text(a),'scheduledTimeLabel':text(cells[1]),'redTeams':red,'blueTeams':blue,'redScore':score['red'],'blueScore':score['blue'],'margin':margin,'winner':None if not played else 'tie' if margin==0 else 'red' if score['red']>score['blue'] else 'blue','team':team,'teamAlliance':target,'teamResult':None if not played else 'tie' if margin==0 else 'win' if score[target]>score['blue' if target=='red' else 'red'] else 'loss','hasDisqualificationMarker':dq,'played':played,'eligible':not excluded,'exclusionReasons':excluded,'sourceUrl':url,'eventResultsUrl':f'{BASE}/{YEAR}/{code}/'+('playoffs' if phase=='playoff' else 'qualifications'),'matchUrl':link,'videoUrls':[],'teamCellMarkers':[{'team':item['team'],'title':item['title']} for item in teamattrs if item['title']]}
                rows.append(row)
    candidates=[r for r in rows if r['eligible']]
    key=lambda r:(r['margin'],0 if r['phase']=='playoff' else 1,-int(r['eventEndDate'].replace('-','')),0 if r['matchLabel'].startswith('Final') else 1,r['eventCode'],r['matchNumber'])
    playoffs=sorted([r for r in candidates if r['phase']=='playoff'],key=key)
    allsorted=sorted(candidates,key=key)
    result={'team':team,'sourceUrl':url,'eligibilityCounts':{'allScheduleRows':len(rows),'played':sum(r['played'] for r in rows),'eligible':len(candidates),'playoff':len(playoffs),'qualification':sum(r['phase']=='qualification' for r in candidates),'excluded':len(rows)-len(candidates)},'selected':(playoffs or allsorted or [None])[0],'absoluteClosest':(allsorted or [None])[0],'eligiblePlayoffsByMargin':playoffs,'allCandidates':rows}
    return result

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: records=list(pool.map(get,TEAMS))
    data={'year':YEAR,'asOf':dt.datetime.now(dt.timezone.utc).isoformat(),'rankingSnapshotCutoff':CUTOFF,'policy':{'selection':'The published main uses absoluteClosest: smallest eligible final alliance-score margin across all phases, with playoffs preferred on equal margins. The preserved selected field is the closest playoff, or the closest qualification if no playoff exists; it supplies a separate playoff alternative when different. Both wins and losses qualify.','scope':'Official FIRST 2026 season schedules through 2026-06-12; later offseason appearances excluded.','ties':'Played ties with final numeric scores remain valid. No published FRC minimum-margin selection is a tied score or required a tie-break.','tieBreak':'Equal margins prefer playoffs, then later event end date, then a final, then event code and match number. No published FRC minimum required a tie-break.','allianceContext':'These are three-robot alliance scores, not an individual team score or proof of a season-long rivalry. Opponents/partners change.'},'records':records}
    (HERE.parent/'frc-candidates.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    for r in records:
        x=r['selected']; y=r['absoluteClosest']; print(r['team'],r['eligibilityCounts'], 'SELECT', x and (x['eventCode'],x['matchLabel'],x['redScore'],x['blueScore'],x['margin'],x['matchUrl']), 'ABS',y and (y['eventCode'],y['matchLabel'],y['margin']))
