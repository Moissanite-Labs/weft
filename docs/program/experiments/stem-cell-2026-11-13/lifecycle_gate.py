"""Concrete Lean checks of stable selection and bounded clone allocation.

Input score/eligibility provenance is bound by the host to previous rollout proofs.
These checks certify the decision arithmetic, not the physical execution of Python.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
from proof_gate import ROOT,SPEC,TOOLCHAIN,canonical,sha,integer,validate,_vec,_list

THEOREM='StemLifecycle.certificate'
FIELDS=('gain_num','gain_den','bias','deadband','cap_low','cap_high')
DUMMY=[{'initial_x':3,'stimuli':[{'target':3,'urgent':False,'error_weight':1,'action_weight':1}]}]

def policy(g):
 validate({'cap_low':2,'cap_high':2},g,DUMMY)
 return _vec(g[k] for k in FIELDS)

def _check(request,definitions,obligations,out_dir):
 source='import Core\nnamespace StemLifecycle\nopen StemCell\nset_option maxRecDepth 100000\nset_option maxHeartbeats 8000000\n'+'\n'.join(definitions)+'\ntheorem certificate : '+' ∧\n '.join('('+o+')' for o in obligations)+' := by decide\n#check certificate\n#print axioms certificate\nend StemLifecycle\n'
 directory=Path(out_dir);directory.mkdir(parents=True,exist_ok=True)
 (directory/'request.json').write_bytes(canonical(request)+b'\n');(directory/'Certificate.lean').write_text(source)
 compiler=Path.home()/'.elan/toolchains/leanprover--lean4---v4.35.0/bin/lean'
 if not compiler.is_file():raise RuntimeError('pinned compiler unavailable')
 env={k:v for k,v in os.environ.items() if k in ('PATH','LANG','LC_ALL','SYSTEMROOT','WINDIR')};logs=[]
 with tempfile.TemporaryDirectory(prefix='stem-life-') as tmp:
  temp=Path(tmp);(temp/'Core.lean').write_bytes(SPEC.read_bytes());(temp/'Certificate.lean').write_text(source);env['LEAN_PATH']=str(temp)
  for command in ([str(compiler),'--version'],[str(compiler),'-o','Core.olean','Core.lean'],[str(compiler),'Certificate.lean']):
   try:r=subprocess.run(command,cwd=temp,env=env,text=True,capture_output=True,timeout=60)
   except subprocess.TimeoutExpired as e:
    logs.append({'command':command[1:],'returncode':None,'stdout':e.stdout.decode(errors='replace') if isinstance(e.stdout,bytes) else e.stdout or '', 'stderr':'timeout'});break
   logs.append({'command':command[1:],'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
   if r.returncode:break
 expected=f"'{THEOREM}' does not depend on any axioms"
 checked=(len(logs)==3 and all(x['returncode']==0 for x in logs) and 'Lean (version 4.35.0,' in logs[0]['stdout'] and logs[2]['stdout'].startswith(THEOREM+' :') and logs[2]['stdout'].strip().splitlines()[-1:]==[expected] and not logs[2]['stderr'].strip())
 result={'accepted':checked,'kernel_checked':checked,'axioms':[] if checked else None,'theorem':THEOREM,'toolchain':TOOLCHAIN,'request':request,'request_sha256':sha(canonical(request)),'proof_sha256':sha(source.encode()),'spec_sha256':sha(SPEC.read_bytes()),'verifier_sha256':sha(Path(__file__).read_bytes()),'compilerlogs':logs,'scope':'Exact concrete stable-min selection or bounded clone allocation over supplied data; prior score/eligibility provenance and runtime binding remain host responsibilities.'}
 (directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n');return result

def verify_selection(genomes,costs,eligible,winner_index,out_dir):
 if type(genomes) is not list or not 1<=len(genomes)<=5 or type(costs) is not list or type(eligible) is not list or len(genomes)!=len(costs) or len(costs)!=len(eligible):raise ValueError('selection pool shape')
 for cost in costs:integer(cost,-10**9,10**9,'cost')
 if any(type(v) is not bool for v in eligible) or eligible[0] is not True:raise ValueError('parent must be eligible')
 integer(winner_index,0,len(genomes)-1,'winner index')
 definitions=['def policies : List Policy := '+_list(policy(g) for g in genomes),'def costs : List Int := '+_list(str(c) for c in costs),'def eligible : List Bool := '+_list(str(e).lower() for e in eligible),f'def winner : Nat := {winner_index}','def chosen : Policy := '+policy(genomes[winner_index])]
 obligations=['policies.length ≤ 5','(policies.drop winner).head? = some chosen','(eligible.drop winner).head? = some true',f'(costs.drop winner).head? = some ({costs[winner_index]}:Int)']
 for i,(cost,ok) in enumerate(zip(costs,eligible)):
  obligations.append(f'((eligible.drop {i}).head? = some true) → (({costs[winner_index]}:Int) < ({cost}:Int) ∨ (({costs[winner_index]}:Int) = ({cost}:Int) ∧ winner ≤ {i}))')
 return _check({'kind':'selection','genomes':genomes,'costs':costs,'eligible':eligible,'winner_index':winner_index},definitions,obligations,out_dir)

def verify_allocation(root_genome,selected,benefits,cells,out_dir):
 if type(selected) is not list or len(selected)!=2 or type(benefits) is not list or len(benefits)!=2 or type(cells) is not list or not 1<=len(cells)<=4:raise ValueError('allocation shape')
 for benefit in benefits:integer(benefit,-10**9,10**9,'benefit')
 branch_ids={'stem':0,'quiet':1,'urgent':2}
 for cell in cells:
  if type(cell) is not dict or cell.get('branch') not in branch_ids or 'genome' not in cell:raise ValueError('cell schema')
 definitions=['def declaredRoot : Policy := '+policy(root_genome),'def quiet : Policy := '+policy(selected[0]),'def urgent : Policy := '+policy(selected[1]),f'def quietBenefit : Int := {benefits[0]}',f'def urgentBenefit : Int := {benefits[1]}',
 'def expectedBranches : List Nat := if quietBenefit > 0 then (if urgentBenefit > 0 then (if quietBenefit ≥ urgentBenefit then [0,1,1,2] else [0,1,2,2]) else [0,1,1,1]) else (if urgentBenefit > 0 then [0,2,2,2] else [0])',
 'def actualBranches : List Nat := '+_list(str(branch_ids[c['branch']]) for c in cells),
 'def actualPolicies : List Policy := '+_list(policy(c['genome']) for c in cells),
 'def expectedPolicies : List Policy := expectedBranches.map (fun b => if b = 0 then declaredRoot else if b = 1 then quiet else urgent)']
 obligations=['declaredRoot = (⟨1,1,0,0,2,2⟩ : Policy)','actualBranches = expectedBranches','actualPolicies = expectedPolicies','actualPolicies.length ≤ 4','actualPolicies.head? = some declaredRoot']
 return _check({'kind':'allocation','root_genome':root_genome,'selected':selected,'benefits':benefits,'cells':cells},definitions,obligations,out_dir)
