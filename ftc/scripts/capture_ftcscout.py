#!/usr/bin/env python3
"""Capture source responses without normalizing their bytes (Python stdlib only).

Re-run with --out DIRECTORY. Requests are sequential, limited to the seven teams
with recorded local 2025-26 participation plus the registered unranked candidate.
An unavailable response remains an explicit capture failure; no statistics are
estimated. The regional quick-stat population is event region, not team domicile.
"""
import argparse, datetime, hashlib, json, pathlib, time, urllib.error, urllib.parse, urllib.request
TEAMS = {22331:'USIN',25638:'USIN',5501:'USOH',14174:'USOH',12802:'USOH',19778:'USOH',30782:'USOH',32552:'USOH'}
BASE='https://api.ftcscout.org'
PIN='05c44a28fe0f0a80101e63134db9a518d9d7ed6c'
USER_AGENT='Refintery FTC regional research (non-commercial snapshot)'
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def capture(out, name, url, timeout):
    start=utc(); body=None; status=None; headers={}; err=None
    req=urllib.request.Request(url,headers={'User-Agent':USER_AGENT,'Accept':'application/json','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            body=r.read(); status=r.status; headers=dict(r.headers.items())
    except urllib.error.HTTPError as e:
        body=e.read(); status=e.code; headers=dict(e.headers.items()); err=str(e)
    except Exception as e: err=str(e)
    meta={'source':'FTCScout','requested_url':url,'request_method':'GET','request_headers':dict(req.header_items()),'started_at_utc':start,'completed_at_utc':utc(),'http_status':status,'response_headers':headers,'error':err}
    if body is not None:
        raw=out/(name+'.json'); raw.write_bytes(body)
        meta.update({'raw_file':raw.name,'byte_count':len(body),'sha256':hashlib.sha256(body).hexdigest()})
        try:
            parsed=None if status==404 and 'quick-stats?' in url and body==b'' else json.loads(body)
            if isinstance(parsed,dict) and parsed.get('errors'): meta['graphql_errors']=parsed['errors']
            if 'quick-stats?' in url and status == 200:
                assert isinstance(parsed,dict) and parsed.get('season') == 2025 and parsed.get('number') == int(url.split('/teams/')[1].split('/')[0])
                assert isinstance(parsed.get('count'),int) and parsed['count'] > 0
                assert all(isinstance(parsed.get(k),dict) and isinstance(parsed[k].get('value'),(float,int)) and isinstance(parsed[k].get('rank'),int) and 1 <= parsed[k]['rank'] <= parsed['count'] for k in ['tot','auto','dc','eg'])
                meta['payload_shape_validated']=True
            elif '/teams/' in url and '/events/2025' in url and status == 200:
                number=int(url.split('/teams/')[1].split('/')[0])
                assert isinstance(parsed,list) and all(isinstance(e,dict) and e.get('season')==2025 and e.get('teamNumber')==number for e in parsed)
                meta['payload_shape_validated']=True
            elif 'quick-stats?' in url and status == 404:
                meta['missing_quick_stats_http_404']=True
        except Exception as e: meta['payload_validation_error']=str(e) or type(e).__name__
    (out/(name+'.metadata.json')).write_text(json.dumps(meta,indent=2)+'\n', encoding="utf-8", newline="\n")
    print(name,status,err or 'ok',flush=True)
    return meta

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--timeout',type=float,default=25);p.add_argument('--only',choices=['all','quickstats','events','identity'],default='all');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    manifest=[]
    for number,region in TEAMS.items():
        requests=[]
        if a.only in ['all','quickstats']:
            requests += [('team-%d-2025-world'%number,BASE+'/rest/v1/teams/%d/quick-stats?season=2025'%number),('team-%d-2025-%s'%(number,region),BASE+'/rest/v1/teams/%d/quick-stats?season=2025&region=%s'%(number,region))]
        if a.only in ['all','events']:requests.append(('team-%d-events-2025'%number,BASE+'/rest/v1/teams/%d/events/2025'%number))
        if a.only in ['all','identity']:requests.append(('team-%d-identity'%number,BASE+'/rest/v1/teams/%d'%number))
        for name,url in requests:
            meta=capture(a.out,name,url,a.timeout)
            manifest.append(meta);time.sleep(.3)
            (a.out/'manifest.json').write_text(json.dumps({'source':'FTCScout','source_code_commit_for_algorithm':PIN,'captures':manifest},indent=2)+'\n', encoding="utf-8", newline="\n")
if __name__=='__main__':main()
