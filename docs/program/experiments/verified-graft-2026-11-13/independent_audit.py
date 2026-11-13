"""Read-only arithmetic audit; imports neither solver nor proof/transport modules."""
import argparse
import hashlib
import json
from pathlib import Path


def load(path):return json.loads(path.read_text())
def represented(w,permutation,signs):return [[signs[i]*row[permutation[i]] for i in range(6)] for row in w]
def inputs(exp,split):return [[exp['receiver_signs'][i]*x[exp['receiver_permutation'][i]] for i in range(6)] for x in exp['splits'][split]]
def apply(w,x):return [sum(a*b for a,b in zip(row,x)) for row in w]
def matrix_for(deployment,task):return deployment[deployment['router'][task]]
def score(deployment,target,xs,task='new'):
 residuals=[[a-b for a,b in zip(apply(matrix_for(deployment,task),x),apply(target,x))] for x in xs]
 return {'SSE':sum(v*v for row in residuals for v in row),'n':len(xs),'residuals':residuals}
def run(root,cohort):
 report=load(root/cohort/'results.json');summaries=[];round_count=0;candidate_count=0
 for lineage in report['lineages']:
  seed,case=lineage['seed'],lineage['case'];exp=load(root/'instances'/f'seed-{seed}.json')
  expected=[[exp['canonical_host'][o][j] if j<3 else exp['canonical_donor'][o][j] for j in range(6)] for o in range(2)]
  target=represented(expected,exp['receiver_permutation'],exp['receiver_signs']);assert target==exp['target']
  assert represented(exp['canonical_host'],exp['receiver_permutation'],exp['receiver_signs'])==exp['host']
  assert represented(exp['canonical_donor'],exp['donor_permutation'],exp['donor_signs'])==exp['donor']
  protected=exp['native_basis'] if case=='compatible' else exp['full_basis']
  directory=root/cohort/f'seed-{seed}.{case}'
  rounds=[load(path) for path in sorted(directory.glob('round-*/round.json'))]
  for record in rounds:
   round_count+=1
   if not record['candidates']:assert not record['adopted'];continue
   a,b=inputs(exp,record['A_split']),inputs(exp,record['B_split']);parent=record['parent']
   assert score(parent,target,a)==record['parent_A'];eligible=[]
   for candidate in record['candidates']:
    candidate_count+=1
    if not candidate['eligible']:continue
    action=candidate['action'];delta=action['delta'];mode=action['mode']
    assert len(delta)==2 and all(len(row)==6 and all(type(n) is int and abs(n)<=4 for n in row) for row in delta)
    assert sum(n*n for row in delta for n in row)<=192
    changed=[[h+d for h,d in zip(hr,dr)] for hr,dr in zip(exp['host'],delta)]
    if mode=='graft':assert all(apply(delta,v)==[0,0] for v in protected)
    elif mode=='fork':assert case=='saturated' and any(n for row in delta for n in row)
    else:assert mode=='abstain' and not any(n for row in delta for n in row)
    expected_deployment={'root':changed if mode=='graft' else exp['host'],'specialist':changed if mode=='fork' else None,'router':{'native':'root','new':'specialist' if mode=='fork' else 'root'},'cell_count':2 if mode=='fork' else 1}
    assert candidate['deployment']==expected_deployment
    assert score(expected_deployment,target,a)==candidate['A']
    if candidate['A']['SSE']<record['parent_A']['SSE']:eligible.append(candidate)
   winner=min(eligible,key=lambda c:(c['A']['SSE'],c['index'])) if eligible else None
   assert record['provisional_winner_index']==(winner['index'] if winner else None)
   adopted=False
   if winner:
    pa,pb=record['parent_A']['SSE'],score(parent,target,b)['SSE'];na=winner['A']['SSE'];nb=score(winner['deployment'],target,b)['SSE']
    assert score(parent,target,b)==record['parent_B'] and score(winner['deployment'],target,b)==winner['B']
    adopted=na<pa and nb<pb and 10*na<=9*pa and 10*nb<=9*pb
   assert record['adopted']==adopted
   assert record['selected_deployment']==(winner['deployment'] if adopted else parent)
  deployed=lineage['selected_deployment'];assert deployed==rounds[-1]['selected_deployment']
  new=score(deployed,target,inputs(exp,'C'));assert new==lineage['final']['new_task_C']
  assert all(apply(deployed['root'],v)==apply(exp['host'],v) for v in protected)
  columns={i for v in protected for i,n in enumerate(v) if n}
  native_inputs=[[n if i in columns else 0 for i,n in enumerate(x)] for x in inputs(exp,'C')]
  native=score(deployed,exp['host'],native_inputs,'native');assert native==lineage['final']['native_protected_C'] and native['SSE']==0
  exact=matrix_for(deployed,'new')==target;assert exact==lineage['final']['exact_new_coefficients']
  summaries.append({'seed':seed,'case':case,'rounds':len(rounds),'C_SSE':new['SSE'],'native_C_SSE':native['SSE'],'exact_target':exact,'cell_count':deployed['cell_count'],'root_unchanged':deployed['root']==exp['host']})
 return {'cohort':cohort,'results_sha256':hashlib.sha256((root/cohort/'results.json').read_bytes()).hexdigest(),'rounds_recomputed':round_count,'candidate_records':candidate_count,'lineages':summaries,'scope':'Independent integer arithmetic/deployment/selection replay, not a fresh Lean compilation or independent model-service attestation.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--cohort',choices=['offline','teacher'],required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();result=run(args.data,args.cohort);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
