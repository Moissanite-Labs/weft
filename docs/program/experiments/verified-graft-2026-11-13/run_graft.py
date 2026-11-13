#!/usr/bin/env python3
"""Offline exact graft control study; external teacher responses remain separate."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import random
import shutil
import tempfile
import graft as g

HERE=Path(__file__).resolve().parent

def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def code_pins():return {name:sha(HERE/name) for name in ('graft.py','run_graft.py','Core.lean','proof_gate.py','prepare_teacher.py','oauth_teacher.py','run_teacher.py')}
def prefix(seed,case):return f'seed-{seed}.{case}'
def assert_proof(proof):
 if not proof.get('kernel_checked') or proof.get('axioms')!=[]:raise ValueError('Concrete Lean certificate did not check with empty axioms')
def gate(visible,action,out):
 from proof_gate import verify_deployment
 proof=verify_deployment(visible,action,out);assert_proof(proof)
 if proof.get('accepted'):
  expected=g.deployment(visible,action)
  if proof.get('deployment')!=expected:raise ValueError('Host and Lean-bound deployment differ')
 return proof

def prove_score(deployed,target,inputs,task,out):
 from proof_gate import verify_scores
 value=g.score(deployed,target,inputs,task)
 proof=verify_scores(deployed,target,{'score':{'inputs':inputs,'sse':value['SSE'],'task':task}},out)
 assert_proof(proof)
 if not proof.get('accepted'):raise ValueError('Exact score certificate rejected')
 return value,proof

def parent_deployment(visible):return g.deployment(visible,{'mode':'abstain','delta':copy.deepcopy(g.ZERO)})
def unchecked_deployment(visible,action):
 return {'root':g.add(visible['host_weights'],action['delta']),'specialist':None,'router':{'native':'root','new':'root'},'cell_count':1}

def evaluate_pool(exp,case,round_number,actions,parent,out_dir,source_label):
 """Exactly four proposals; choose on A, confirm that winner only on B.

 Returned raw record may contain B. Use teacher_feedback(), never this record,
 when constructing a subsequent teacher request.
 """
 if round_number not in (1,2):raise ValueError('round must be 1 or 2')
 if type(actions) is not list or len(actions)!=4:raise ValueError('Each opportunity has exactly four proposed actions')
 visible=g.packet(exp,case);a_inputs=g.receiver_inputs(exp,f'A{round_number}');b_inputs=g.receiver_inputs(exp,f'B{round_number}')
 parent_a,parent_a_proof=prove_score(parent,exp['target'],a_inputs,'new',out_dir/'proofs/parent-A')
 records=[];seen={}
 for index,action in enumerate(actions):
  row={'index':index,'action':copy.deepcopy(action),'eligible':False,'duplicate_of':None}
  try:
   key=g.fingerprint(action);row['duplicate_of']=seen.get(key);seen.setdefault(key,index)
   proof=gate(visible,action,out_dir/'proofs'/f'candidate-{index}-deployment');row['deployment_proof']=proof
   if not proof.get('accepted'):row['error']='Formal deployment contract rejected'
   else:
    deployed=g.deployment(visible,action)
    score,score_proof=prove_score(deployed,exp['target'],a_inputs,'new',out_dir/'proofs'/f'candidate-{index}-A')
    row.update({'eligible':True,'deployment':deployed,'A':score,'A_proof':score_proof})
  except (ValueError,TypeError,KeyError,IndexError) as exc:row['error']=f'{type(exc).__name__}: {exc}'
  records.append(row)
 eligible=[row for row in records if row['eligible'] and row['A']['SSE']<parent_a['SSE']]
 winner=min(eligible,key=lambda row:(row['A']['SSE'],row['index'])) if eligible else None
 # Independent confirmation is not used to rank any alternatives.
 parent_b=None;winner_b=None;adopted=False;adoption_proof=None
 if winner is not None:
  parent_b,parent_b_proof=prove_score(parent,exp['target'],b_inputs,'new',out_dir/'proofs/parent-B')
  winner_b,winner_b_proof=prove_score(winner['deployment'],exp['target'],b_inputs,'new',out_dir/'proofs/winner-B')
  adopted=g.confirmed(parent_a['SSE'],winner['A']['SSE'],parent_b['SSE'],winner_b['SSE'])
  from proof_gate import verify_adoption
  adoption_proof=verify_adoption(parent_a['SSE'],winner['A']['SSE'],parent_b['SSE'],winner_b['SSE'],adopted,out_dir/'proofs/adoption')
  assert_proof(adoption_proof)
  if not adoption_proof.get('accepted'):raise ValueError('Adoption arithmetic certificate rejected')
  winner['B']=winner_b;winner['B_proof']=winner_b_proof
 else:parent_b_proof=None
 selected=winner['deployment'] if adopted else parent
 record={'source':source_label,'seed':exp['seed'],'case':case,'round':round_number,'parent':parent,
         'parent_A':parent_a,'parent_A_proof':parent_a_proof,'candidates':records,'provisional_winner_index':winner['index'] if winner else None,
         'parent_B':parent_b,'parent_B_proof':parent_b_proof,'adopted':adopted,'adoption_proof':adoption_proof,
         'selected_deployment':selected,'exact_target_reached':g.function_for(selected,'new')==exp['target'],
         'A_split':f'A{round_number}','B_split':f'B{round_number}','packet_sha256':g.fingerprint(visible)}
 write(out_dir/'round.json',record)
 return record

def teacher_feedback(record):
 """Only A scores and legality are disclosed. B and C never enter feedback."""
 return {'round':record['round'],'candidates':[{'index':row['index'],'action':row['action'],'eligible':row['eligible'],
          'A_SSE':row.get('A',{}).get('SSE'),'error':row.get('error')} for row in record['candidates']],
         'current_deployment':record['selected_deployment']}

def rank5_fixture(exp):
 visible=g.packet(exp,'compatible',True);alignments=g.infer_alignments(visible)
 if len(alignments)!=2:raise ValueError('Rank-five fixture must have exactly two sign completions')
 # Flip latent donor sign and canonical coefficient together. Published weights and
 # all observed activations remain identical; the unobserved donor function differs.
 alternative=copy.deepcopy(exp);slot=alternative['donor_permutation'].index(5)
 alternative['donor_signs'][slot]*=-1
 for row in alternative['canonical_donor']:row[5]*=-1
 alternative['donor']=g.represented(alternative['canonical_donor'],alternative['donor_permutation'],alternative['donor_signs'])
 canonical=[[alternative['canonical_host'][o][j] if j<3 else alternative['canonical_donor'][o][j] for j in range(6)] for o in range(2)]
 alternative['target']=g.represented(canonical,alternative['receiver_permutation'],alternative['receiver_signs'])
 alternative_visible=g.packet(alternative,'compatible',True)
 if visible!=alternative_visible or exp['target']==alternative['target']:raise ValueError('Rank-five ambiguity construction failed')
 receiver_direction=g.coordinate_basis(exp['receiver_permutation'],exp['receiver_signs'],[5])[0]
 return {'visible_packet':visible,'alternative_visible_packet':alternative_visible,'packets_identical':True,
         'receiver_calibration_rank':g.rank([row['receiver_features'] for row in visible['calibration']]),
         'completions':alignments,'completion_actions':[g.proposed(visible,g.aligned_donor(visible,m)) for m in alignments],
         'hidden_targets':[exp['target'],alternative['target']],'witness_receiver_vector':receiver_direction,
         'different_outputs':[g.apply(exp['target'],receiver_direction),g.apply(alternative['target'],receiver_direction)],
         'scope':'Ambiguity from visible packet only. Feedback outside the rank-five observation span may resolve the sign; no impossibility claim after such queries.'}

def prepare(out):
 if (out/'registration.json').exists():
  validate_registration(out);return
 write(out/'protocol.json',g.CONFIG)
 for seed in g.CONFIG['seeds']:
  exp=g.instance(seed);write(out/'instances'/f'seed-{seed}.json',exp)
  for case in g.CONFIG['cases']:write(out/'packets'/f'{prefix(seed,case)}.json',g.packet(exp,case))
 pins={'config_sha256':g.fingerprint(g.CONFIG),'code_sha256':code_pins(),
       'inputs_sha256':{str(path.relative_to(out)):sha(path) for base in ('instances','packets') for path in sorted((out/base).glob('*.json'))}}
 write(out/'registration.json',pins)
def validate_registration(out):
 pins=read(out/'registration.json')
 if pins['config_sha256']!=g.fingerprint(g.CONFIG) or pins['code_sha256']!=code_pins():raise ValueError('Registered configuration or code changed')
 for name,expected in pins['inputs_sha256'].items():
  if sha(out/name)!=expected:raise ValueError('Registered input changed: '+name)

def final_measurement(exp,case,deployed,out):
 inputs=g.receiver_inputs(exp,'C');new,new_proof=prove_score(deployed,exp['target'],inputs,'new',out/'new-C')
 protected=g.packet(exp,case)['protected_basis'];columns={i for row in protected for i,v in enumerate(row) if v}
 old_inputs=[[v if i in columns else 0 for i,v in enumerate(row)] for row in inputs]
 native,native_proof=prove_score(deployed,exp['host'],old_inputs,'native',out/'native-C')
 return {'new_task_C':new,'new_task_C_proof':new_proof,'native_protected_C':native,'native_protected_C_proof':native_proof,
         'exact_new_coefficients':g.function_for(deployed,'new')==exp['target']}

def offline_run(out):
 prepare(out);validate_registration(out);lineages=[];diagnostics=[]
 for seed in g.CONFIG['seeds']:
  exp=read(out/'instances'/f'seed-{seed}.json')
  for case in g.CONFIG['cases']:
   visible=g.packet(exp,case);all_controls=g.controls(visible)
   by_label={row['label']:row for row in all_controls}
   labels=['mechanical_alignment','raw_coordinate_copy','scrambled_correspondence','no_edit']
   actions=[by_label[label]['action'] for label in labels];parent=parent_deployment(visible);rounds=[]
   for number in (1,2):
    record=evaluate_pool(exp,case,number,actions,parent,out/'offline'/prefix(seed,case)/f'round-{number}','mechanical_control_cohort')
    record['control_labels']=labels;write(out/'offline'/prefix(seed,case)/f'round-{number}'/'round.json',record)
    rounds.append(record);parent=record['selected_deployment']
    if record['exact_target_reached']:break
   lineages.append({'seed':seed,'case':case,'rounds':rounds,'selected_deployment':parent})
   negative=by_label['ungated_full_donor_replacement']['action'];proof=gate(visible,negative,out/'offline'/prefix(seed,case)/'ungated-deployment')
   diagnostics.append({'seed':seed,'case':case,'ungated_action':negative,'formal_proof':proof,
                       'untrusted_ungated_deployment':unchecked_deployment(visible,negative),
                       'protected_output_differences':[g.apply(negative['delta'],v) for v in visible['protected_basis']]})
  write(out/'diagnostics'/f'rank5-{seed}.json',rank5_fixture(exp))
  from proof_gate import verify_conflict
  witness=g.conflict_witness(exp);proof=verify_conflict(exp['host'],exp['target'],witness['vector'],out/'diagnostics'/f'conflict-{seed}')
  assert_proof(proof)
  if not proof.get('accepted'):raise ValueError('Capacity contradiction certificate rejected')
  write(out/'diagnostics'/f'conflict-{seed}.json',{'witness':witness,'proof':proof})
 # Lock all choices before C is scored.
 lock={prefix(row['seed'],row['case']):g.fingerprint(row['selected_deployment']) for row in lineages}
 write(out/'offline/selection_lock.json',lock)
 for row in lineages:
  exp=read(out/'instances'/f'seed-{row["seed"]}.json')
  row['final']=final_measurement(exp,row['case'],row['selected_deployment'],out/'offline'/prefix(row['seed'],row['case'])/'final-proofs')
  visible=g.packet(exp,row['case']);row['control_C']=[]
  for control in g.controls(visible):
   try:deployed=g.deployment(visible,control['action']);eligible=True
   except ValueError:deployed=unchecked_deployment(visible,control['action']);eligible=False
   c_score,c_proof=prove_score(deployed,exp['target'],g.receiver_inputs(exp,'C'),'new',out/'offline'/prefix(row['seed'],row['case'])/'control-C-proofs'/control['label'])
   row['control_C'].append({'label':control['label'],'action':control['action'],'eligible':eligible,'new_task_C':c_score,'C_proof':c_proof})
 overfit=g.overfit_fixture()
 visible=overfit['visible'];proof=gate(visible,overfit['action'],out/'diagnostics/overfit/deployment');assert_proof(proof)
 from proof_gate import verify_adoption
 scores=overfit['scores'];decision=verify_adoption(scores['parent_A'],scores['child_A'],scores['parent_B'],scores['child_B'],False,out/'diagnostics/overfit/adoption')
 assert_proof(decision)
 from proof_gate import verify_scores
 for label,action in [('parent',{'mode':'abstain','delta':copy.deepcopy(g.ZERO)}),('child',overfit['action'])]:
  deployed=g.deployment(visible,action)
  overfit[label+'_score_proof']=verify_scores(deployed,overfit['target'],{split:{'inputs':overfit[split],'sse':scores[label+'_'+split],'task':'new'} for split in ('A','B')},out/'diagnostics/overfit'/f'{label}-scores')
  assert_proof(overfit[label+'_score_proof'])
 overfit['deployment_proof']=proof;overfit['adoption_proof']=decision;write(out/'diagnostics/overfit.json',overfit)
 report={'config':g.CONFIG,'cohort':'deterministic mechanical controls, not Astra','selection_lock':lock,'lineages':lineages,'negative_controls':diagnostics,'overfit':overfit}
 write(out/'offline/results.json',report);manifest(out,'offline');return report

def manifest(out,cohort):
 shared=[out/'protocol.json',out/'registration.json']
 directories=['instances','packets',cohort]+(['diagnostics'] if cohort=='offline' else ['teacher-transport','teacher-requests','prepared'])
 paths=shared+[path for directory in directories for path in (out/directory).rglob('*') if path.is_file()]
 if cohort=='teacher' and (out/'teacher-call-ledger.json').exists():paths.append(out/'teacher-call-ledger.json')
 hashes={str(path.relative_to(out)):sha(path) for path in sorted(set(paths)) if path.suffix in ('.json','.lean','.jsonl')}
 write(out/f'manifest-{cohort}.json',{'cohort':cohort,'code_sha256':code_pins(),'artifact_sha256':hashes})

def extract_candidates(value):
 if type(value) is dict and 'response' in value:
  response=value['response'];chunks=[item['text'] for message in response.get('output',[]) if message.get('type')=='message' for item in message.get('content',[]) if item.get('type')=='output_text']
  value=json.loads(''.join(chunks))
 if type(value) is not dict or set(value)!={'candidates'} or type(value['candidates']) is not list or len(value['candidates'])!=4:raise ValueError('Teacher must return exactly candidates:[four actions]')
 return value['candidates']

def safe_artifact(out,relative):
 if type(relative) is not str or Path(relative).is_absolute():raise ValueError('Transport artifact must be a relative path')
 path=(out/relative).resolve()
 if out.resolve() not in path.parents:raise ValueError('Transport artifact escaped registered data root')
 return path

def validate_transport(out,package,exp,case,number,parent,previous):
 if type(package) is not dict or not {'binding','artifacts','transport_status'}<=set(package):raise ValueError('Bound transport package required')
 binding=package['binding'];artifacts=package['artifacts']
 if type(binding) is not dict or type(artifacts) is not dict or set(artifacts)!={'original_request','wire','response_record','terminal_events'}:raise ValueError('Transport binding schema')
 for key,value in [('seed',exp['seed']),('case',case),('round',number),('packet_sha256',g.fingerprint(g.packet(exp,case)))]:
  if type(binding.get(key)) is not type(value) or binding[key]!=value:raise ValueError('Response lineage/packet mismatch: '+key)
 paths={name:safe_artifact(out,path) for name,path in artifacts.items()}
 for name,path in paths.items():
  if binding.get(name+'_sha256')!=sha(path):raise ValueError('Transport artifact hash mismatch: '+name)
 original=read(paths['original_request'])
 from prepare_teacher import envelope
 expected=envelope(g.packet(exp,case),parent,number,[] if previous is None else teacher_feedback(previous))
 if original!=expected:raise ValueError('Original request differs from registered packet, parent or permitted A feedback')
 record=read(paths['response_record']);wire=read(paths['wire']);events=read(paths['terminal_events'])
 if type(events) is not list:raise ValueError('Terminal events must be an array')
 terminals=[event for event in events if event.get('type') in ('response.completed','response.incomplete','response.failed')]
 terminal=terminals[-1] if terminals else None
 if binding.get('terminal_model')!=(terminal.get('model') if terminal else None):raise ValueError('Terminal model binding mismatch')
 identity_ok=bool(terminal and terminal.get('type')=='response.completed' and terminal.get('status')=='completed' and terminal.get('model')=='gpt-6-astra')
 expected_status='terminal_identity_error' if record.get('status')=='parsed' and not identity_ok else record.get('status','error')
 if package['transport_status']!=expected_status:raise ValueError('Transport status mismatch')
 if expected_status!='parsed':
  if 'candidates' in package:raise ValueError('Failed transport cannot supply candidate actions')
  return False
 if not terminal or terminal.get('type')!='response.completed' or terminal.get('status')!='completed' or terminal.get('model')!='gpt-6-astra':raise ValueError('Teacher did not complete with the registered model')
 if type(wire) is not list or len(wire)!=1:raise ValueError('Exactly one observed wire request required')
 body=wire[0]
 if body.get('model')!='gpt-6-astra' or body.get('store') is not False or body.get('tools') or body.get('previous_response_id'):raise ValueError('Observed model, store, tools or history mismatch')
 from oauth_teacher import SYSTEM
 if body.get('instructions')!=SYSTEM:raise ValueError('Observed system instructions changed')
 if type(body.get('input')) is not list or len(body['input'])!=1 or body['input'][0].get('role')!='user' or type(body['input'][0].get('content')) is not list or len(body['input'][0]['content'])!=1 or body['input'][0]['content'][0].get('type')!='input_text':raise ValueError('Exactly one observed user input text required')
 try:text=body['input'][0]['content'][0]['text']
 except (TypeError,KeyError,IndexError) as exc:raise ValueError('Observed wire input schema') from exc
 canonical_envelope=json.dumps(expected,sort_keys=True,separators=(',',':'),allow_nan=False)
 if text!=canonical_envelope:raise ValueError('Observed wire input differs from registered envelope')
 request=record.get('request',{});messages=request.get('messages',[])
 if request.get('model')!='gpt-6-astra' or request.get('tools')!=[] or len(messages)!=2 or messages[1].get('role')!='user' or json.loads(messages[1].get('content','null'))!=expected:raise ValueError('Worker response request binding mismatch')
 canonical_request=json.dumps(request,sort_keys=True,separators=(',',':')).encode()
 if record.get('request_sha256')!=hashlib.sha256(canonical_request).hexdigest():raise ValueError('Worker request digest mismatch')
 deltas=[event['delta'] for event in events if event.get('type')=='response.output_text.delta' and type(event.get('delta')) is str]
 if deltas and ''.join(deltas)!=record.get('output_text'):raise ValueError('Saved stream text differs from parsed response text')
 parsed=json.loads(record.get('output_text','null'))
 actions=extract_candidates(parsed)
 if record.get('parsed_batch')!=parsed or package.get('candidates')!=actions:raise ValueError('Candidate batch differs from actual returned text')
 return True

def journal(out,event=None):
 path=out/'teacher/journal.jsonl';previous='0'*64;events=[]
 if path.exists():
  for line in path.read_text().splitlines():
   row=json.loads(line);identifier=row.pop('event_id')
   if row['previous_id']!=previous or g.fingerprint(row)!=identifier:raise ValueError('Teacher journal hash chain changed')
   previous=identifier;events.append(row['event'])
 if event is not None:
  row={'previous_id':previous,'event':event};row['event_id']=g.fingerprint(row)
  path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('a') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')
 return events

def retained_hashes(out,directory):
 return {str(path.relative_to(out)):sha(path) for path in sorted(directory.rglob('*')) if path.is_file() and path.name!='round.json'}

def validate_teacher_record(out,exp,case,number,parent,previous):
 directory=out/'teacher'/prefix(exp['seed'],case)/f'round-{number}';path=directory/'round.json';record=read(path)
 events=[event for event in journal(out) if event.get('round_file')==str(path.relative_to(out))]
 if len(events)!=1 or events[0]['round_sha256']!=g.fingerprint(record):raise ValueError('Teacher selection differs from journal')
 for name,expected in record['retained_artifact_sha256'].items():
  if sha(safe_artifact(out,name))!=expected:raise ValueError('Retained teacher certificate changed')
 package=read(directory/'response.raw.json');success=validate_transport(out,package,exp,case,number,parent,previous)
 if record['source']!='external_teacher' or record['seed']!=exp['seed'] or record['case']!=case or record['round']!=number:raise ValueError('Stored round identity mismatch')
 if not success:
  if record['candidates'] or record['adopted'] or record['selected_deployment']!=parent:raise ValueError('Failed opportunity did not preserve parent')
 else:
  if [row['action'] for row in record['candidates']]!=package['candidates']:raise ValueError('Stored proposals differ from actual response')
  a_inputs=g.receiver_inputs(exp,f'A{number}');b_inputs=g.receiver_inputs(exp,f'B{number}')
  parent_a=g.score(parent,exp['target'],a_inputs)
  if record['parent']!=parent or record['parent_A']!=parent_a:raise ValueError('Stored parent score mismatch')
  eligible=[]
  for row in record['candidates']:
   if row['eligible']:
    deployed=g.deployment(g.packet(exp,case),row['action'])
    if row['deployment']!=deployed or row['A']!=g.score(deployed,exp['target'],a_inputs):raise ValueError('Stored candidate deployment/A score mismatch')
    if row['A']['SSE']<parent_a['SSE']:eligible.append(row)
  winner=min(eligible,key=lambda row:(row['A']['SSE'],row['index'])) if eligible else None
  adopted=False
  if winner is not None:
   parent_b=g.score(parent,exp['target'],b_inputs);new_b=g.score(winner['deployment'],exp['target'],b_inputs)
   if record['parent_B']!=parent_b or winner['B']!=new_b:raise ValueError('Stored confirmation score mismatch')
   adopted=g.confirmed(parent_a['SSE'],winner['A']['SSE'],parent_b['SSE'],new_b['SSE'])
  chosen=winner['deployment'] if adopted else parent
  if record['provisional_winner_index']!=(winner['index'] if winner else None) or record['adopted']!=adopted or record['selected_deployment']!=chosen:raise ValueError('Stored choice differs from A-only ranking/B confirmation')
 if record['exact_target_reached']!=(g.function_for(record['selected_deployment'],'new')==exp['target']):raise ValueError('Stored exact-target stop mismatch')
 return record

def teacher_round(out,seed,case,number,response_path):
 validate_registration(out);exp=read(out/'instances'/f'seed-{seed}.json');visible=g.packet(exp,case)
 directory=out/'teacher'/prefix(seed,case)/f'round-{number}'
 if (directory/'round.json').exists():raise ValueError('Teacher opportunity already processed; no overwrite')
 if number==1:parent=parent_deployment(visible)
 elif number==2:
  previous=read(directory.parent/'round-1/round.json')
  if previous['exact_target_reached']:raise ValueError('Exact target reached; no second opportunity')
  parent=previous['selected_deployment']
 else:raise ValueError('Only two proposal opportunities')
 raw=read(response_path)
 previous=None if number==1 else read(directory.parent/'round-1/round.json')
 if number==2:previous=validate_teacher_record(out,exp,case,1,parent_deployment(visible),None)
 successful=validate_transport(out,raw,exp,case,number,parent,previous)
 write(directory/'response.raw.json',raw)
 if not successful:
  record={'source':'external_teacher','seed':seed,'case':case,'round':number,'error':'Consumed failed transport opportunity','candidates':[],
          'selected_deployment':parent,'exact_target_reached':g.function_for(parent,'new')==exp['target'],'adopted':False}
 else:record=evaluate_pool(exp,case,number,raw['candidates'],parent,directory,'external_teacher')
 record['provenance']=raw['binding'];record['retained_artifact_sha256']=retained_hashes(out,directory)
 write(directory/'round.json',record)
 journal(out,{'round_file':str((directory/'round.json').relative_to(out)),'round_sha256':g.fingerprint(record)})
 write(directory/'feedback-A-only.json',teacher_feedback(record))
 # Feedback is derived after committing the record and is checked through its
 # deterministic value in the next original request, not part of this record hash.
 return record

def finish_teacher(out):
 validate_registration(out);lineages=[]
 for seed in g.CONFIG['seeds']:
  for case in g.CONFIG['cases']:
   exp=read(out/'instances'/f'seed-{seed}.json');visible=g.packet(exp,case)
   base=out/'teacher'/prefix(seed,case);first=validate_teacher_record(out,exp,case,1,parent_deployment(visible),None)
   final=first if first['exact_target_reached'] else validate_teacher_record(out,exp,case,2,first['selected_deployment'],first)
   lineages.append({'seed':seed,'case':case,'selected_deployment':final['selected_deployment'],'rounds_used':final['round']})
 lock={prefix(row['seed'],row['case']):g.fingerprint(row['selected_deployment']) for row in lineages};write(out/'teacher/selection_lock.json',lock)
 for row in lineages:
  exp=read(out/'instances'/f'seed-{row["seed"]}.json');row['final']=final_measurement(exp,row['case'],row['selected_deployment'],out/'teacher'/prefix(row['seed'],row['case'])/'final-proofs')
 report={'cohort':'external teacher only; deterministic controls never inserted','selection_lock':lock,'lineages':lineages}
 write(out/'teacher/results.json',report);manifest(out,'teacher');return report

def replay(out,cohort):
 validate_registration(out);pins=read(out/f'manifest-{cohort}.json')
 if pins['code_sha256']!=code_pins():raise ValueError('Code changed')
 for name,expected in pins['artifact_sha256'].items():
  if sha(out/name)!=expected:raise ValueError('Artifact changed: '+name)
 report=read(out/cohort/'results.json')
 if cohort=='teacher':
  for seed in g.CONFIG['seeds']:
   exp=read(out/'instances'/f'seed-{seed}.json')
   for case in g.CONFIG['cases']:
    first=validate_teacher_record(out,exp,case,1,parent_deployment(g.packet(exp,case)),None)
    if not first['exact_target_reached']:validate_teacher_record(out,exp,case,2,first['selected_deployment'],first)
 for row in report['lineages']:
  exp=read(out/'instances'/f'seed-{row["seed"]}.json');deployed=row['selected_deployment']
  if g.score(deployed,exp['target'],g.receiver_inputs(exp,'C'))!=row['final']['new_task_C']:raise ValueError('Exact score replay mismatch')
 print(json.dumps({'cohort':cohort,'hashes_verified':True,'exact_C_scores_replayed':len(report['lineages']),'new_model_calls':0}))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','run','teacher','finish-teacher','replay']);p.add_argument('--out',type=Path,default=HERE/'data');p.add_argument('--seed',type=int);p.add_argument('--case',choices=g.CONFIG['cases']);p.add_argument('--round',type=int);p.add_argument('--response',type=Path);p.add_argument('--cohort',choices=['offline','teacher'],default='offline');a=p.parse_args();out=a.out.resolve()
 if a.command=='prepare':prepare(out);print(out/'registration.json')
 elif a.command=='run':report=offline_run(out);print(json.dumps({'cohort':'offline','lineages':len(report['lineages'])}))
 elif a.command=='teacher':
  if a.seed not in g.CONFIG['seeds'] or a.case is None or a.round not in (1,2) or a.response is None:p.error('teacher needs registered --seed --case --round --response')
  record=teacher_round(out,a.seed,a.case,a.round,a.response);print(json.dumps({'adopted':record['adopted'],'exact_target_reached':record['exact_target_reached']}))
 elif a.command=='finish-teacher':print(json.dumps({'lineages':len(finish_teacher(out)['lineages'])}))
 else:replay(out,a.cohort)
if __name__=='__main__':main()
