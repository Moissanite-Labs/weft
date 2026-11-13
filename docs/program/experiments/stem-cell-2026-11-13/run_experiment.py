#!/usr/bin/env python3
"""Offline preparation, proof-gated selection and locked heldout measurement."""
from __future__ import annotations
import argparse
import copy
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import colony as c

ARMS=c.CONFIG['branches']

def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def read(path):return json.loads(path.read_text())
def name(seed,branch,generation):return f'seed-{seed}.{branch}.generation-{generation}'
def bytehash(path):return __import__('hashlib').sha256(path.read_bytes()).hexdigest()
def code_pins():
 return {name:bytehash(Path(__file__).with_name(name)) for name in ('colony.py','run_experiment.py','Core.lean','proof_gate.py','lifecycle_gate.py')}
def register(out):
 record={'config_sha256':c.fingerprint(c.CONFIG),'code_sha256':code_pins(),
         'experiment_byte_sha256':{p.name:bytehash(p) for p in sorted((out/'experiments').glob('*.json'))},
         'prepared_request_sha256':{p.name:bytehash(p) for p in sorted((out/'requests').glob('*.json')) if not p.name.endswith(('.wire.json','.response.json'))}}
 path=out/'registration.json'
 if path.exists() and read(path)!=record and list((out/'requests').glob('*.response.json')):raise ValueError('Cannot change registration after a response exists')
 write(path,record)
def validate_registration(out):
 registration=read(out/'registration.json')
 if registration['config_sha256']!=c.fingerprint(c.CONFIG):raise ValueError('Registered configuration changed')
 if registration['code_sha256']!=code_pins():raise ValueError('Registered code changed')
 for name,expected in registration['experiment_byte_sha256'].items():
  path=out/'experiments'/name
  if not path.exists() or bytehash(path)!=expected:raise ValueError('Registered episode data changed: '+name)
 return registration
def validate_response_binding(path,envelope,registration):
 if envelope.get('request_file')!=path.name:raise ValueError('Response request filename mismatch')
 prepared=read(path)
 registered=registration['prepared_request_sha256'].get(path.name)
 if registered is not None and registered!=bytehash(path):raise ValueError('Prepared request bytes changed')
 wire_path=path.with_suffix('.wire.json')
 data=wire_path.read_bytes()
 if not data.endswith(b'\n'):raise ValueError('Wire artifact must retain worker trailing newline')
 data=data[:-1]
 wire=json.loads(data)
 cap=wire.get('max_output_tokens')
 if type(cap) is not int or not 1<=cap<=prepared['max_output_tokens']:raise ValueError('Wire output cap differs from registered range')
 expected={**prepared,'store':False,'service_tier':'default','max_output_tokens':cap}
 if wire!=expected:raise ValueError('Wire body differs from expected prepared request')
 digest=__import__('hashlib').sha256(data).hexdigest()
 if envelope.get('request_sha256')!=digest:raise ValueError('Response wire digest mismatch')
 return {'prepared_request_bytes_sha256':bytehash(path),'wire_bytes_sha256':digest}
def journal_events(out):
 path=out/'journal.jsonl';previous='0'*64;events=[]
 if path.exists():
  for line in path.read_text().splitlines():
   row=json.loads(line);digest=row.pop('event_id')
   if row['previous_id']!=previous or c.fingerprint(row)!=digest:raise ValueError('journal integrity mismatch')
   events.append(row['event']);previous=digest
 return events,previous
def retained_hashes(out,stem):
 result={}
 for base in (out/'proofs'/stem,out/'lifecycle_proofs'/stem):
  if base.exists():
   for path in sorted(base.rglob('*')):
    if path.is_file():result[str(path.relative_to(out))]=bytehash(path)
 return result
def validate_retained_selection(out,path,record):
 events,_=journal_events(out)
 matching=[event for event in events if event.get('type')=='selection' and event.get('selection_file')==str(path.relative_to(out))]
 if not matching or any(event['selection_sha256']!=c.fingerprint(record) for event in matching):raise ValueError('Retained selection differs from journal')
 for name,expected in record['retained_artifact_sha256'].items():
  artifact=out/name
  if not artifact.exists() or bytehash(artifact)!=expected:raise ValueError('Retained certificate artifact changed: '+name)

def log(out,event):
 path=out/'journal.jsonl'
 _,previous=journal_events(out)
 row={'previous_id':previous,'event':event};row['event_id']=c.fingerprint(row)
 with path.open('a') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')
def pressure_observation(fixture=None):
 observation={'fixture':fixture,'cpu_workers_max':2,'platform':sys.platform,'free_percent':None,'paused':False,'workers':1,'level':'unknown'}
 if fixture:
  observation['paused']=fixture=='critical';observation['workers']=2 if fixture=='normal' else 1;observation['level']=fixture;observation['source']='deterministic fixture';return observation
 if sys.platform=='darwin':
  try:
   p=subprocess.run(['/usr/bin/memory_pressure','-Q'],capture_output=True,text=True,timeout=5)
   observation.update({'source':'memory_pressure -Q','returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
   match=re.search(r'free percentage:\s*(\d+)%',p.stdout)
   if match:
    free=int(match.group(1));observation['free_percent']=free;observation['paused']=free<=c.CONFIG['pressure_free_percent_pause']
    observation['level']='critical' if observation['paused'] else ('pressure' if free<=c.CONFIG['pressure_free_percent_single_worker'] else 'normal')
    observation['workers']=2 if observation['level']=='normal' else 1
  except (OSError,subprocess.TimeoutExpired) as exc:observation['source']='unavailable';observation['error']=type(exc).__name__
 else:observation['source']='no Apple memory-pressure sensor on this platform'
 return observation

def extract(envelope):
 if 'response' not in envelope:raise RuntimeError('Transport failure is not a proposal opportunity')
 response=envelope['response']
 if response.get('status') not in (None,'completed'):raise ValueError('response not completed')
 chunks=[x['text'] for item in response.get('output',[]) if item.get('type')=='message' for x in item.get('content',[]) if x.get('type')=='output_text']
 value=json.loads(''.join(chunks))
 if type(value) is not dict or set(value)!={'hypothesis','children'} or type(value['hypothesis']) is not str or type(value['children']) is not list or len(value['children'])!=4:raise ValueError('expected hypothesis:string and exactly four children')
 return value

def make_request(out,exp,branch,generation,parent,history):
 packet={'model':'bounded integer stem controller','seed':exp['seed'],'demand':branch,'generation':generation,'parent_genome':parent,
         'policy':'e=target-x+bias; if abs(e)<=deadband then k=0 else k=sign(e)*floor(gain_num*abs(e)/gain_den), clamped to +/-cap_high when urgent else +/-cap_low; x_after=x+k; cost=error_weight*(target-x_after)^2+action_weight*k^2',
         'bounds':{'gain_num':[0,4],'gain_den':[1,4],'deadband':[0,3],'bias':[-2,2],'cap_low':[0,parent['cap_low']],'cap_high':[0,parent['cap_high']]},
         'train_episodes':c.demand_episodes(exp['splits']['train'],branch),
         'parent_train_cost':c.evaluate(parent,c.demand_episodes(exp['splits']['train'],branch))['total_cost'],
         'parent_validation_cost':c.evaluate(parent,c.demand_episodes(exp['splits']['validation'],branch))['total_cost'],
         'previous_validation_feedback':history,'selection':'Lowest validation integer cost, only if strictly better than unchanged parent; ties preserve parent. Propose four data-only child genomes.'}
 request={'model':c.CONFIG['teacher_model'],'store':False,'max_output_tokens':c.CONFIG['max_output_tokens'],
          'instructions':'Return only strict JSON {"hypothesis":"short rationale","children":[{"label":"short name","genome":{"gain_num":0,"gain_den":1,"deadband":0,"bias":0,"cap_low":0,"cap_high":0}},...]} with exactly four children. All six genome fields must be exact bounded integers. Child caps may only tighten the given parent caps. No code or markdown.',
          'input':json.dumps(packet,separators=(',',':'))}
 path=out/'requests'/f'{name(exp["seed"],branch,generation)}.json'
 if path.exists():
  if read(path)!=request:raise ValueError('Existing request changed: '+path.name)
 else:
  # Compact request files keep the exact prospective wire footprint visible.
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(request,separators=(',',':'))+'\n')
 return path

def checked(genome,parent,episodes,outdir):
 from proof_gate import verify_batch
 start=time.monotonic();proof=verify_batch({k:parent[k] for k in ('cap_low','cap_high')},genome,episodes,outdir)
 evaluated=c.evaluate(genome,episodes)
 if not proof.get('accepted') or not proof.get('kernel_checked') or proof.get('axioms')!=[]:raise ValueError('Lean gate rejected candidate')
 expected=[{'initial_x':row['initial_x'],'final_x':row['final_x'],'total_cost':row['total_cost'],'steps':[{k:s[k] for k in ('target','urgent','error_weight','action_weight','x_before','k','x_after','cost')} for s in row['steps']]} for row in evaluated['episode_results']]
 if proof.get('episode_results')!=expected:raise ValueError('Independent Python and Lean-bound trajectories disagree')
 if proof.get('total_cost')!=evaluated['total_cost']:raise ValueError('Independent Python and Lean-bound costs disagree')
 return evaluated,{'verification':proof,'elapsed_seconds':time.monotonic()-start}
def candidate(genome,parent,train,validation,outdir,index,label,seen):
 record={'index':index,'label':label,'genome':genome,'eligible':False,'duplicate_of':None}
 try:
  genome=c.validate_genome(genome,parent);fingerprint=c.fingerprint(genome)
  record['duplicate_of']=seen.get(fingerprint)
  _,proof=checked(genome,parent,train+validation,outdir)
  evaluated=c.evaluate(genome,validation)
  record.update({'genome':genome,'valid':True,'eligible':True,'validation':evaluated,'train':c.evaluate(genome,train),'proof':proof})
 except (ValueError,TypeError,KeyError,IndexError) as exc:record.update({'valid':False,'error':f'{type(exc).__name__}: {exc}'})
 return record

def best_candidate(records,parent,parent_cost):
 eligible=[r for r in records if r['eligible'] and r['validation']['total_cost']<parent_cost]
 best=min(eligible,key=lambda r:(r['validation']['total_cost'],r['index'])) if eligible else None
 return copy.deepcopy(best['genome'] if best else parent),best['index'] if best else None

def checked_selection(records,parent,parent_cost,index,outdir):
 from lifecycle_gate import verify_selection
 by_index={r['index']:r for r in records}
 genomes=[parent];costs=[parent_cost];eligible=[True]
 for i in range(4):
  row=by_index.get(i,{})
  ok=bool(row.get('eligible'))
  genomes.append(row['genome'] if ok else parent)
  costs.append(row['validation']['total_cost'] if ok else parent_cost)
  eligible.append(ok)
 proof=verify_selection(genomes,costs,eligible,0 if index is None else index+1,outdir)
 if not proof.get('accepted') or not proof.get('kernel_checked') or proof.get('axioms')!=[]:raise ValueError('Lifecycle selection proof failed')
 return proof

def process(out,fixture=None):
 if read(out/'config.json')!=c.CONFIG:raise ValueError('Frozen configuration mismatch')
 registration=validate_registration(out)
 pending=[]
 for seed in c.CONFIG['seeds']:
  exp=read(out/'experiments'/f'seed-{seed}.json')
  for branch in ARMS:
   parent=copy.deepcopy(c.ROOT);history=[]
   for generation in range(1,3):
    path=make_request(out,exp,branch,generation,parent,history);response_path=path.with_suffix('.response.json')
    record_path=out/'selections'/path.name
    if not response_path.exists():pending.append(str(path));break
    envelope=read(response_path)
    if 'response' not in envelope:raise RuntimeError('Transport/API failure not consumed: '+response_path.name)
    wire_binding=validate_response_binding(path,envelope,registration)
    binding={**wire_binding,**{'request_sha256':c.fingerprint(read(path)),'response_sha256':c.fingerprint(envelope),
             'experiment_sha256':c.fingerprint(exp),'config_sha256':c.fingerprint(c.CONFIG),'parent_sha256':c.fingerprint(parent)}}
    if record_path.exists():
     record=read(record_path)
     if any(record.get(k)!=v for k,v in binding.items()):raise ValueError('Archived selection input changed')
     validate_retained_selection(out,record_path,record)
    else:
     observation=pressure_observation(fixture)
     write(out/'scheduler'/f'{path.stem}.json',observation)
     if observation['paused']:
      log(out,{'type':'pressure_pause','request':path.name,'observation':observation});pending.append(str(path));break
     train=c.demand_episodes(exp['splits']['train'],branch);validation=c.demand_episodes(exp['splits']['validation'],branch)
     _,parent_proof=checked(parent,parent,train+validation,out/'proofs'/path.stem/'unchanged-parent')
     parent_eval=c.evaluate(parent,validation)
     _,fixed_proof=checked(c.FIXED,c.ROOT,train+validation,out/'proofs'/path.stem/'fixed-hand')
     record={**binding,'seed':seed,'branch':branch,'generation':generation,'parent':parent,'scheduler':observation,
             'unchanged_parent':{'genome':parent,'validation':parent_eval,'proof':parent_proof},'fixed_hand_controller':{'genome':c.FIXED,'validation':c.evaluate(c.FIXED,validation),'proof':fixed_proof}}
     children=[]
     try:
      proposal=extract(envelope);record['proposal']=proposal
      seen={}
      for index,child in enumerate(proposal['children']):
       if type(child) is not dict or set(child)!={'label','genome'} or type(child['label']) is not str:
        children.append({'index':index,'raw_child':child,'valid':False,'eligible':False,'error':'child requires exactly label:string and genome:object'})
       else:
        key=c.fingerprint(child['genome'])
        duplicate=seen.get(key);seen.setdefault(key,index)
        children.append({'index':index,'genome':child['genome'],'label':child['label'],'duplicate_of':duplicate,'pending':True})
      def run_one(row):
       if not row.get('pending'):return row
       result=candidate(row['genome'],parent,train,validation,out/'proofs'/path.stem/f'teacher-{row["index"]}',row['index'],row['label'],{})
       result['duplicate_of']=row['duplicate_of'];return result
      with ThreadPoolExecutor(max_workers=observation['workers']) as pool:children=list(pool.map(run_one,children))
     except (ValueError,TypeError,KeyError,IndexError) as exc:record['proposal_error']=f'{type(exc).__name__}: {exc}'
     record['children']=children
     random_children=[c.random_child(parent,seed*100000+ARMS.index(branch)*1000+generation*10+i) for i in range(4)]
     random_seen={};random_duplicates={}
     for i,genome in enumerate(random_children):
      key=c.fingerprint(genome);random_duplicates[i]=random_seen.get(key);random_seen.setdefault(key,i)
     def run_random(pair):
      index,genome=pair
      row=candidate(genome,parent,train,validation,out/'proofs'/path.stem/f'random-{index}',index,'random valid child',{})
      row['duplicate_of']=random_duplicates[index];return row
     with ThreadPoolExecutor(max_workers=observation['workers']) as pool:random_records=list(pool.map(run_random,enumerate(random_children)))
     selected,index=best_candidate(children,parent,parent_eval['total_cost']);random_selected,random_index=best_candidate(random_records,parent,parent_eval['total_cost'])
     teacher_lifecycle=checked_selection(children,parent,parent_eval['total_cost'],index,out/'lifecycle_proofs'/path.stem/'teacher-selection')
     random_lifecycle=checked_selection(random_records,parent,parent_eval['total_cost'],random_index,out/'lifecycle_proofs'/path.stem/'random-selection')
     record.update({'teacher_selection_proof':teacher_lifecycle,'random_selection_proof':random_lifecycle,'random_children':random_records,'selected_genome':selected,'selected_index':index,
                    'selected_validation':c.evaluate(selected,validation),'random_selected_genome':random_selected,'random_selected_index':random_index})
     record['retained_artifact_sha256']=retained_hashes(out,path.stem)
     write(record_path,record);log(out,{'type':'selection','selection_file':str(record_path.relative_to(out)),'selection_sha256':c.fingerprint(record)})
    parent=record['selected_genome']
    history.append({'generation':generation,'hypothesis':record.get('proposal',{}).get('hypothesis'),'children':[{'index':r['index'],'genome':r.get('genome'),'valid':r.get('valid'),'eligible':r.get('eligible'),'validation_cost':r.get('validation',{}).get('total_cost'),'duplicate_of':r.get('duplicate_of'),'error':r.get('error')} for r in record['children']],
                    'selected_index':record['selected_index'],'selected_genome':parent,'selected_validation_cost':record['selected_validation']['total_cost']})
 if not pending:
  selections={p.name:c.fingerprint(read(p)) for p in sorted((out/'selections').glob('*.json'))}
  if len(selections)!=8:raise ValueError('Expected exactly 8 processed request opportunities')
  lock={'config_sha256':c.fingerprint(c.CONFIG),'selection_sha256':selections}
  if (out/'selection_lock.json').exists() and read(out/'selection_lock.json')!=lock:raise ValueError('Selection lock changed')
  write(out/'selection_lock.json',lock)
 return pending

def finish(out):
 if process(out):raise ValueError('All 8 responses must be processed before heldout evaluation')
 observation=pressure_observation();write(out/'scheduler'/'heldout.json',observation)
 if observation['paused']:raise RuntimeError('Heldout proof batch paused for critical local memory pressure')
 lock=read(out/'selection_lock.json');results=[];colonies=[]
 for seed in c.CONFIG['seeds']:
  exp=read(out/'experiments'/f'seed-{seed}.json');selected={};benefits={}
  for branch in ARMS:
   final=read(out/'selections'/f'{name(seed,branch,2)}.json');selected[branch]=final['selected_genome']
   validation=c.demand_episodes(exp['splits']['validation'],branch)
   benefits[branch]=c.evaluate(c.ROOT,validation)['total_cost']-c.evaluate(selected[branch],validation)['total_cost']
   for evaluated_branch in ARMS:
    episodes=c.demand_episodes(exp['splits']['test'],evaluated_branch)
    controllers={'root_stem':c.ROOT,'fixed_hand':c.FIXED,'teacher_final':selected[branch],
                 'random_selected_generation1':read(out/'selections'/f'{name(seed,branch,1)}.json')['random_selected_genome'],
                 'random_selected_generation2':final['random_selected_genome'],'unchanged_parent_generation2':final['parent']}
    for label,genome in controllers.items():
     evaluated,proof=checked(genome,c.ROOT,episodes,out/'heldout_proofs'/f'{seed}-{branch}-{evaluated_branch}-{label}')
     results.append({'seed':seed,'selected_for_demand':branch,'evaluated_demand':evaluated_branch,'controller':label,'genome':genome,'test':evaluated,'proof':proof})
  allocation=c.allocate(selected,benefits);actual=[]
  from lifecycle_gate import verify_allocation
  allocation_proof=verify_allocation(c.ROOT,[selected[b] for b in ARMS],[benefits[b] for b in ARMS],allocation['cells'],out/'lifecycle_proofs'/f'{seed}-allocation')
  if not allocation_proof.get('accepted') or not allocation_proof.get('kernel_checked') or allocation_proof.get('axioms')!=[]:raise ValueError('Colony allocation proof failed')
  for branch in ARMS:
   available=[cell for cell in allocation['cells'] if cell['branch']==branch]
   if not available:available=[allocation['cells'][0]]
   episodes=c.demand_episodes(exp['splits']['test'],branch)
   for index,episode in enumerate(episodes):
    cell=available[index%len(available)]
    evaluated,proof=checked(cell['genome'],c.ROOT,[episode],out/'colony_proofs'/f'{seed}-{branch}-episode-{index}')
    actual.append({'demand':branch,'episode_index':index,'cell_id':cell['cell_id'],'evaluated':evaluated,'proof':proof})
  colonies.append({'seed':seed,'allocation':allocation,'allocation_proof':allocation_proof,'actual_closed_loop_rollout':actual})
 report={'config':c.CONFIG,'selection_lock':lock,'results':results,'colonies':colonies,
         'scope':'Two exploratory source seeds; target and urgency are paired across demands, costs differ. All heldout scores measured after selection lock; no significance claim.'}
 write(out/'results.json',report)
 hashes={str(p.relative_to(out)):c.fingerprint(read(p)) for p in sorted(out.rglob('*.json')) if p.name!='manifest.json'}
 code={p.name:__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(c.__file__),Path(__file__).with_name('proof_gate.py'),Path(__file__).with_name('Core.lean'),Path(__file__).with_name('lifecycle_gate.py'))}
 write(out/'manifest.json',{'artifact_sha256':hashes,'code_sha256':code,'config':c.CONFIG})
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','advance','finish','replay']);p.add_argument('--out',type=Path,default=Path(__file__).with_name('data'));p.add_argument('--pressure-fixture',choices=['normal','pressure','critical','unknown']);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 if a.command=='prepare':
  if (out/'config.json').exists() and read(out/'config.json')!=c.CONFIG:raise ValueError('Existing config differs')
  write(out/'config.json',c.CONFIG)
  for seed in c.CONFIG['seeds']:
   path=out/'experiments'/f'seed-{seed}.json';exp=c.experiment(seed)
   if path.exists() and read(path)!=exp:raise ValueError('Existing experiment differs')
   write(path,exp)
  for seed in c.CONFIG['seeds']:
   for branch in ARMS:make_request(out,read(out/'experiments'/f'seed-{seed}.json'),branch,1,c.ROOT,[])
  register(out)
  print('\n'.join(process(out,a.pressure_fixture)))
 elif a.command=='advance':print('\n'.join(process(out,a.pressure_fixture)))
 elif a.command=='finish':finish(out);print(out/'results.json')
 else:
  if not (out/'results.json').exists():raise ValueError('Replay requires finished results')
  manifest=read(out/'manifest.json')
  for name,expected in manifest['artifact_sha256'].items():
   if c.fingerprint(read(out/name))!=expected:raise ValueError('Artifact changed: '+name)
  for name,expected in manifest['code_sha256'].items():
   if __import__('hashlib').sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()!=expected:raise ValueError('Code changed: '+name)
  # Proof costs include measured elapsed times; verify decisions and exact integer traces, not timing equality.
  records=[]
  for path in sorted((out/'selections').glob('*.json')):
   record=read(path);exp=read(out/'experiments'/f'seed-{record["seed"]}.json');episodes=c.demand_episodes(exp['splits']['validation'],record['branch'])
   for row in record['children']+record['random_children']:
    if row.get('eligible') and c.evaluate(row['genome'],episodes)!=row['validation']:raise ValueError('Selection arithmetic replay failed')
   records.append(path.name)
  report=read(out/'results.json')
  for row in report['results']:
   exp=read(out/'experiments'/f'seed-{row["seed"]}.json')
   episodes=c.demand_episodes(exp['splits']['test'],row['evaluated_demand'])
   if c.evaluate(row['genome'],episodes)!=row['test']:raise ValueError('Heldout arithmetic replay failed')
  for family in report['colonies']:
   exp=read(out/'experiments'/f'seed-{family["seed"]}.json')
   for rollout in family['actual_closed_loop_rollout']:
    cell=next(cell for cell in family['allocation']['cells'] if cell['cell_id']==rollout['cell_id'])
    episode=c.demand_episodes(exp['splits']['test'],rollout['demand'])[rollout['episode_index']]
    if c.evaluate(cell['genome'],[episode])!=rollout['evaluated']:raise ValueError('Colony arithmetic replay failed')
  print(json.dumps({'replayed_selections':len(records),'artifact_hashes_verified':True,'paid_calls':0}))
if __name__=='__main__':main()
