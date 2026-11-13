"""Data-only exact policy/trace/score gate. Python and compiler runtime remain trusted."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parent
SPEC=ROOT/'Core.lean'
TOOLCHAIN='leanprover/lean4:v4.35.0'
THEOREM='StemCellConcrete.certificate'
GENOME_KEYS={'gain_num','gain_den','bias','deadband','cap_low','cap_high'}
STIM_KEYS={'target','urgent','error_weight','action_weight'}

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def integer(x,lo,hi,label):
 if type(x) is not int or not lo<=x<=hi:raise ValueError(label+' must be an exact bounded integer')
def validate(parent_caps,genome,episodes):
 if type(parent_caps) is not dict or set(parent_caps)!={'cap_low','cap_high'}:raise ValueError('parent caps schema')
 for v in parent_caps.values():integer(v,0,2,'parent cap')
 if type(genome) is not dict or set(genome)!=GENOME_KEYS:raise ValueError('genome schema')
 for k,lo,hi in [('gain_num',0,4),('gain_den',1,4),('bias',-2,2),('deadband',0,3),('cap_low',0,2),('cap_high',0,2)]:integer(genome[k],lo,hi,k)
 if type(episodes) is not list or not 1<=len(episodes)<=16:raise ValueError('need 1..16 episodes')
 for e in episodes:
  if type(e) is not dict or set(e)!={'initial_x','stimuli'}:raise ValueError('episode schema')
  integer(e['initial_x'],-4,8,'initial_x')
  if type(e['stimuli']) is not list or not 1<=len(e['stimuli'])<=32:raise ValueError('need 1..32 stimuli')
  for s in e['stimuli']:
   if type(s) is not dict or set(s)!=STIM_KEYS:raise ValueError('stimulus schema')
   integer(s['target'],-4,8,'target')
   if type(s['urgent']) is not bool:raise ValueError('urgent must be boolean')
   integer(s['error_weight'],0,100,'error_weight');integer(s['action_weight'],0,100,'action_weight')

def simulate_episode(genome,episode):
 x=episode['initial_x'];rows=[]
 for s in episode['stimuli']:
  error=s['target']-x+genome['bias']
  magnitude=genome['gain_num']*abs(error)//genome['gain_den']
  raw=0 if abs(error)<=genome['deadband'] else (-magnitude if error<0 else magnitude)
  cap=genome['cap_high'] if s['urgent'] else genome['cap_low']
  k=max(-cap,min(cap,raw));after=x+k
  cost=s['error_weight']*(s['target']-after)**2+s['action_weight']*k*k
  rows.append(dict(s,x_before=x,k=k,x_after=after,cost=cost));x=after
 return {'initial_x':episode['initial_x'],'steps':rows,'final_x':x,'total_cost':sum(r['cost'] for r in rows)}

def _vec(values):return '⟨'+', '.join(str(v).lower() for v in values)+'⟩'
def _list(values):return '['+', '.join(values)+']'

def verify_batch(parent_caps,genome,episodes,out_dir,*,claimed_results=None):
 """Check every concrete trajectory and its exact integer score in one Lean module.

 Optional claimed_results is a host audit/test hook, never model-authored code.
 A false claimed row, final state or score fails compilation. Caps can only tighten.
 """
 validate(parent_caps,genome,episodes)
 calculated=[simulate_episode(genome,e) for e in episodes]
 claimed=calculated if claimed_results is None else claimed_results
 if type(claimed) is not list or len(claimed)!=len(episodes):raise ValueError('claimed result shape')
 for e,c in zip(episodes,claimed):
  if type(c) is not dict or set(c)!={'initial_x','steps','final_x','total_cost'} or type(c['steps']) is not list or len(c['steps'])!=len(e['stimuli']):raise ValueError('claimed result schema')
  for field in ('initial_x','final_x','total_cost'):integer(c[field],-10**9,10**9,field)
  for s,r in zip(e['stimuli'],c['steps']):
   if type(r) is not dict or set(r)!=STIM_KEYS|{'x_before','k','x_after','cost'} or any(r[k]!=s[k] or type(r[k]) is not type(s[k]) for k in STIM_KEYS):raise ValueError('claimed stimulus differs')
   for key in ('x_before','k','x_after','cost'):integer(r[key],-10**9,10**9,key)
 governance=genome['cap_low']<=parent_caps['cap_low'] and genome['cap_high']<=parent_caps['cap_high']
 definitions=['def policy : Policy := '+_vec(genome[k] for k in ('gain_num','gain_den','bias','deadband','cap_low','cap_high'))]
 obligations=[f'validGenome {parent_caps["cap_low"]} {parent_caps["cap_high"]} policy = {str(governance).lower()}']
 for i,(e,c) in enumerate(zip(episodes,claimed)):
  stimuli=_list(_vec(s[k] for k in ('target','urgent','error_weight','action_weight')) for s in e['stimuli'])
  rows=_list(_vec(r[k] for k in ('x_before','k','x_after','cost')) for r in c['steps'])
  definitions.extend([f'def inputs{i} : List Stim := {stimuli}',f'def rows{i} : List Row := {rows}'])
  obligations.extend([f'simulate policy ({e["initial_x"]}) inputs{i} = rows{i}',f'allSafe policy inputs{i} rows{i} = true',f'totalCost rows{i} = ({c["total_cost"]}:Int)',f'({c["initial_x"]}:Int) = ({e["initial_x"]}:Int)',f'(rows{i}.getLast?).map Row.after = some ({c["final_x"]}:Int)'])
 source='import Core\nnamespace StemCellConcrete\nopen StemCell\nset_option maxRecDepth 100000\nset_option maxHeartbeats 8000000\n'+ '\n'.join(definitions)+'\ntheorem certificate : '+ ' ∧\n  '.join('('+o+')' for o in obligations)+' := by decide\n#check certificate\n#print axioms certificate\nend StemCellConcrete\n'
 request={'parent_caps':parent_caps,'genome':genome,'episodes':episodes,'claimed_results':claimed}
 out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
 (out_dir/'request.json').write_bytes(canonical(request)+b'\n');(out_dir/'Certificate.lean').write_text(source)
 compiler=Path.home()/'.elan/toolchains/leanprover--lean4---v4.35.0/bin/lean'
 if not compiler.is_file():raise RuntimeError('pinned Lean compiler unavailable')
 env={k:v for k,v in os.environ.items() if k in ('PATH','LANG','LC_ALL','SYSTEMROOT','WINDIR')}
 logs=[]
 with tempfile.TemporaryDirectory(prefix='stem-proof-') as directory:
  temp=Path(directory);(temp/'Core.lean').write_bytes(SPEC.read_bytes());(temp/'Certificate.lean').write_text(source);env['LEAN_PATH']=str(temp)
  for command in ([str(compiler),'--version'],[str(compiler),'-o','Core.olean','Core.lean'],[str(compiler),'Certificate.lean']):
   try:p=subprocess.run(command,cwd=temp,env=env,capture_output=True,text=True,timeout=60)
   except subprocess.TimeoutExpired as error:
    stdout=error.stdout.decode(errors='replace') if isinstance(error.stdout,bytes) else error.stdout or ''
    logs.append({'command':command[1:],'returncode':None,'stdout':stdout,'stderr':'compiler timeout','timeout':True});break
   logs.append({'command':command[1:],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
   if p.returncode:break
 expected=f"'{THEOREM}' does not depend on any axioms"
 checked=(len(logs)==3 and all(x['returncode']==0 for x in logs) and 'Lean (version 4.35.0,' in logs[0]['stdout'] and logs[2]['stdout'].startswith(THEOREM+' :') and logs[2]['stdout'].strip().splitlines()[-1:]==[expected] and not logs[2]['stderr'].strip())
 result={'accepted':governance and checked,'kernel_checked':checked,'axioms':[] if checked else None,'contract_valid':governance,
         'episode_results':claimed,'total_cost':sum(c['total_cost'] for c in claimed),'theorem':THEOREM,'toolchain':TOOLCHAIN,
         'request_sha256':sha(canonical(request)),'proof_sha256':sha(source.encode()),'spec_sha256':sha(SPEC.read_bytes()),'verifier_sha256':sha(Path(__file__).read_bytes()),
         'parent_caps':parent_caps,'genome':genome,'compilerlogs':logs,'scope':'Concrete exact integer policy, rollout, score and inherited local/root constraints; Python/OS/compiler runtime trusted.'}
 (out_dir/'verification.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 return result
