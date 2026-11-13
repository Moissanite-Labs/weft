#!/usr/bin/env python3
"""Bounded concurrent API batches. Key stays in process memory; no automatic retries."""
import argparse
import concurrent.futures
import getpass
import hashlib
import json
import re
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
import certifi


def cost(usage):
    detail = usage.get('input_tokens_details') or {}
    cached = detail.get('cached_tokens', 0)
    writes = detail.get('cache_write_tokens', 0)
    ordinary = max(0, usage.get('input_tokens', 0)-cached-writes)
    return (ordinary*10+cached+writes*12.5+usage.get('output_tokens', 0)*50)/1e6


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--budget-usd',type=float,default=42.)
    p.add_argument('--max-calls',type=int,default=52)
    p.add_argument('--workers',type=int,default=4)
    a=p.parse_args()
    key=getpass.getpass('Temporary API key (hidden, memory only): ')
    if not key.startswith('sk-'): raise SystemExit('OpenAI key required')
    lock=threading.Lock(); stop=threading.Event()
    ledger={'spent':0.,'reserved':0.,'calls':0}
    context=ssl.create_default_context(cafile=certifi.where())

    def run(path):
        path=Path(path).resolve()
        target=path.with_suffix('.response.json')
        if target.exists(): return {'file':str(target),'skipped_existing':True}
        request=json.loads(path.read_text())
        if request.get('model')!='gpt-6-astra' or request.get('store') is not False:
            raise ValueError('Expected Astra request with store=false')
        cap=request.get('max_output_tokens',6000)
        if not isinstance(cap,int) or not 1<=cap<=8000: raise ValueError('Output cap outside batch bounds')
        payload=json.dumps(request).encode()
        if key.encode() in payload: raise ValueError('Credential in request body')
        # UTF-8 bytes conservatively bound text tokens for these plain-text requests.
        # Add framing allowance. Charge all input at the highest configured write rate.
        reserve=((len(payload)+1024)*12.5+cap*50)/1e6
        with lock:
            if stop.is_set() or ledger['calls']>=a.max_calls or ledger['spent']+ledger['reserved']+reserve>a.budget_usd:
                return {'file':str(path),'not_sent':'stop, call cap, or conservative budget reservation'}
            ledger['calls']+=1;ledger['reserved']+=reserve
        start=time.monotonic()
        req=urllib.request.Request('https://api.openai.com/v1/responses',data=payload,
                                   headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
        record={'request_file':path.name,'request_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        try:
            with urllib.request.urlopen(req,context=context,timeout=240) as response: raw=json.load(response)
            result={k:raw.get(k) for k in ('id','model','status','usage','error','incomplete_details','created_at')}
            result['output']=[item for item in raw.get('output',[]) if item.get('type')=='message']
            record['response']=result
        except urllib.error.HTTPError as exc:
            try: error=json.loads(exc.read()).get('error',{})
            except Exception: error={}
            record.update(http_status=exc.code,error={k:error.get(k) for k in ('type','code','message')})
            if exc.code in (401,403,429):stop.set()
        except Exception as exc:
            record['error']={'type':type(exc).__name__}
        record['elapsed_seconds']=time.monotonic()-start
        usage=record.get('response',{}).get('usage')
        charged=cost(usage) if usage else reserve
        record['estimated_usd']=charged
        record['estimate_kind']='reported tokens' if usage else 'conservative reservation; actual charge unknown'
        text=json.dumps(record,indent=2).replace(key,'[REDACTED]')
        text=re.sub(r'sk-[A-Za-z0-9_-]{12,}','[REDACTED]',text)
        target.write_text(text+'\n')
        with lock:
            ledger['reserved']-=reserve;ledger['spent']+=charged
            summary={'file':str(target),'status':record.get('response',{}).get('status'),
                     'error':record.get('error'),'usage':usage,'elapsed_seconds':record['elapsed_seconds'],
                     'estimated_batch_spend_usd':ledger['spent'],'calls':ledger['calls']}
            print(json.dumps(summary),flush=True)
        return summary

    print('READY: enter a JSON file containing an array of request paths; STOP ends the worker',flush=True)
    for line in sys.stdin:
        if line.strip()=='STOP':break
        if not line.strip():continue
        if stop.is_set():print('STOPPED: access or quota failure',flush=True);break
        paths=json.loads(Path(line.strip()).read_text())
        if not isinstance(paths,list) or len(paths)!=len(set(paths)):raise ValueError('Expected unique path list')
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
            futures=[pool.submit(run,path) for path in paths]
            for future in concurrent.futures.as_completed(futures):
                result=future.result()
                if result.get('not_sent') or result.get('skipped_existing'):print(json.dumps(result),flush=True)
        print(json.dumps({'batch_complete':True,**ledger}),flush=True)
    key=''


if __name__=='__main__':main()
