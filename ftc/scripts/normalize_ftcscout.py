#!/usr/bin/env python3
"""Reconstruct local ranking extracts from an existing FTCScout capture directory.

No network calls or third-party dependencies. Verify every raw response hash and
HTTP status before deriving fields. Usage: normalize_ftcscout.py CAPTURE_DIRECTORY
Prints JSON to stdout; redirect to a new derived file to preserve old extracts.
"""
import hashlib,json,pathlib,sys
TEAMS={22331:'USIN',25638:'USIN',5501:'USOH',14174:'USOH',12802:'USOH',19778:'USOH',30782:'USOH',32552:'USOH'}
def normalize(root):
    root=pathlib.Path(root)
    manifest=json.loads((root/'manifest.json').read_text(encoding="utf-8"))
    captures={m['raw_file']:m for m in manifest['captures'] if m.get('raw_file')}
    assert len(captures)==sum(bool(m.get('raw_file')) for m in manifest['captures']), 'Duplicate capture filenames'
    def read(name):
        m=captures[name];body=(root/name).read_bytes()
        assert len(body)==m['byte_count'] and hashlib.sha256(body).hexdigest()==m['sha256'], name+' hash/size mismatch'
        assert m['http_status'] in [200,404], name+' unexpected HTTP status'
        return (json.loads(body) if m['http_status']==200 else None),m
    summary=[]
    for number,region in TEAMS.items():
        world,wm=read('team-%d-2025-world.json'%number)
        regional,rm=read('team-%d-2025-%s.json'%(number,region))
        events,em=read('team-%d-events-2025.json'%number)
        assert isinstance(events,list) and em['http_status']==200
        assert all(e.get('season')==2025 and e.get('teamNumber')==number for e in events)
        for stats in [world,regional]:
            if stats is None:continue
            assert stats['season']==2025 and stats['number']==number and isinstance(stats['count'],int) and stats['count']>0
            assert all(isinstance(stats[k]['value'],(int,float)) and isinstance(stats[k]['rank'],int) and 1<=stats[k]['rank']<=stats['count'] for k in ['tot','auto','dc','eg'])
        assert (world is None)==(regional is None), 'Partial ranking response'
        def best(value):return [e['eventCode'] for e in events if e.get('stats') and e['stats']['opr']['totalPointsNp']==value]
        row={'team_number':number,'source':'FTCScout','metric':'Peak event non-penalty OPR','season_start_year':2025,'value':world['tot']['value'] if world else None,'world_rank':world['tot']['rank'] if world else None,'world_team_count':world['count'] if world else None,'regional_value':regional['tot']['value'] if regional else None,'regional_rank':regional['tot']['rank'] if regional else None,'regional_team_count':regional['count'] if regional else None,'regional_population':region+' event cohort','world_source_url':wm['requested_url'],'regional_source_url':rm['requested_url'],'world_best_event_codes':best(world['tot']['value']) if world else [],'regional_best_event_codes':best(regional['tot']['value']) if regional else [],'source_event_count':len(events),'source_events_with_statistics':sum(e.get('stats') is not None for e in events),'status':'ranked' if world else 'no_quick_stats_http_404'}
        if world:assert row['world_best_event_codes'] and row['regional_best_event_codes'], 'Best value not supported by raw event stats'
        else:assert wm['http_status']==404 and rm['http_status']==404 and events==[]
        summary.append(row)
    counts={r['world_team_count'] for r in summary if r['world_team_count'] is not None}
    assert len(counts)==1, 'World population changed during capture'
    for region in set(TEAMS.values()):
        counts={r['regional_team_count'] for r in summary if TEAMS[r['team_number']]==region and r['regional_team_count'] is not None}
        assert len(counts)<=1, 'Regional population changed during capture'
    return summary
if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit(__doc__)
    print(json.dumps(normalize(sys.argv[1]),indent=2))
