"""Trusted data-only Lean templates for exact integer graft/fork deployments."""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parent
SPEC=ROOT/'Core.lean'
TOOLCHAIN='leanprover/lean4:v4.35.0'
THEOREM='VerifiedGraftConcrete.certificate'
SPAN_AXIOMS=['propext','Quot.sound']

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def integer(x,lo,hi,label):
 if type(x) is not int or not lo<=x<=hi:raise ValueError(label+' needs an exact bounded integer')
def matrix(x,limit=6):
 if type(x) is not list or len(x)!=2 or any(type(row) is not list or len(row)!=6 for row in x):raise ValueError('matrix requires 2 rows of 6 integers')
 for row in x:
  for value in row:integer(value,-limit,limit,'matrix entry')
 return x

def vector(v,limit=32):
 if type(v) is not list or len(v)!=6:raise ValueError('vector requires six integers')
 for n in v:integer(n,-limit,limit,'vector entry')
 return v

def basis(vectors,count):
 if type(vectors) is not list or len(vectors)!=count:raise ValueError('protected basis shape')
 indices=[]
 for v in vectors:
  vector(v,1)
  if sum(abs(n) for n in v)!=1:raise ValueError('basis must use signed coordinate vectors')
  indices.append(next(i for i,n in enumerate(v) if n))
 if len(set(indices))!=len(indices):raise ValueError('basis directions must be unique')
 return set(indices)

def _vec(v):return '⟨'+','.join(str(n) for n in v)+'⟩'
def _mat(w):return '⟨'+','.join(_vec(row) for row in w)+'⟩'
def _vectors(vs):return '['+','.join(_vec(v) for v in vs)+']'
def matadd(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def apply(w,v):return [sum(a*b for a,b in zip(row,v)) for row in w]

def _check(request,definitions,obligations,out_dir,accepted=True,extra=None):
 source='import Core\nnamespace VerifiedGraftConcrete\nopen VerifiedGraft\nset_option maxRecDepth 100000\nset_option maxHeartbeats 8000000\n'+'\n'.join(definitions)+'\ntheorem certificate : '+' ∧\n '.join('('+o+')' for o in obligations)+' := by decide\n#check certificate\n#print axioms certificate\nend VerifiedGraftConcrete\n'
 out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
 (out/'request.json').write_bytes(canonical(request)+b'\n');(out/'Certificate.lean').write_text(source)
 compiler=Path.home()/'.elan/toolchains/leanprover--lean4---v4.35.0/bin/lean'
 if not compiler.is_file():raise RuntimeError('Pinned Lean 4.35.0 compiler unavailable')
 env={k:v for k,v in os.environ.items() if k in ('PATH','LANG','LC_ALL','SYSTEMROOT','WINDIR')};logs=[]
 with tempfile.TemporaryDirectory(prefix='graft-proof-') as directory:
  temp=Path(directory);(temp/'Core.lean').write_bytes(SPEC.read_bytes());(temp/'Certificate.lean').write_text(source);env['LEAN_PATH']=str(temp)
  for command in ([str(compiler),'--version'],[str(compiler),'-o','Core.olean','Core.lean'],[str(compiler),'Certificate.lean']):
   try:p=subprocess.run(command,cwd=temp,env=env,capture_output=True,text=True,timeout=60)
   except subprocess.TimeoutExpired as exc:
    logs.append({'command':command[1:],'returncode':None,'stdout':exc.stdout.decode(errors='replace') if isinstance(exc.stdout,bytes) else exc.stdout or '', 'stderr':'Compiler timeout','timeout':True});break
   logs.append({'command':command[1:],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
   if p.returncode:break
 expected=f"'{THEOREM}' does not depend on any axioms"
 expected_core=["'VerifiedGraft.span_retention' depends on axioms: [propext, Quot.sound]","'VerifiedGraft.conflict_witness' does not depend on any axioms"]
 checked=(len(logs)==3 and all(v['returncode']==0 for v in logs) and 'Lean (version 4.35.0,' in logs[0]['stdout'] and logs[1]['stdout'].strip().splitlines()==expected_core and not logs[1]['stderr'].strip() and logs[2]['stdout'].startswith(THEOREM+' :') and logs[2]['stdout'].strip().splitlines()[-1:]==[expected] and not logs[2]['stderr'].strip())
 result={'accepted':bool(accepted and checked),'kernel_checked':checked,'axioms':[] if checked else None,'theorem':THEOREM,'toolchain':TOOLCHAIN,
         'request_sha256':sha(canonical(request)),'proof_sha256':sha(source.encode()),'spec_sha256':sha(SPEC.read_bytes()),'verifier_sha256':sha(Path(__file__).read_bytes()),
         'compilerlogs':logs,'scope':'Concrete exact integer deployment/score/decision records. Generic integer-span lemma uses standard logical axioms; host, compiler execution and physical effects remain outside this proof.'}
 if extra:result.update(copy.deepcopy(extra))
 (out/'verification.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');return result

def verify_deployment(visible,action,out_dir):
 visible=copy.deepcopy(visible);action=copy.deepcopy(action)
 if type(visible) is not dict:raise ValueError('visible packet must be object')
 host=matrix(visible['host_weights'],2);case=visible['capacity_case']
 if case not in ('compatible','saturated'):raise ValueError('unknown capacity case')
 protected=visible['protected_basis'];native=visible['native_basis']
 protected_indices=basis(protected,3 if case=='compatible' else 6);native_indices=basis(native,3)
 if not native_indices<=protected_indices:raise ValueError('protected basis must include native span')
 if type(action) is not dict or set(action)!={'mode','delta'} or action['mode'] not in ('graft','fork','abstain'):raise ValueError('typed action schema')
 delta=matrix(action['delta'],4);mode=action['mode'];mode_id={'graft':0,'fork':1,'abstain':2}[mode]
 changed=matadd(host,delta);norm=sum(n*n for row in delta for n in row);nonzero=any(n for row in delta for n in row)
 legal=norm<=192 and ((mode=='graft' and all(apply(host,v)==apply(changed,v) for v in protected)) or (mode=='fork' and case=='saturated' and nonzero) or (mode=='abstain' and not nonzero))
 deployment={'root':changed if mode=='graft' else host,'specialist':changed if mode=='fork' else None,'router':{'native':'root','new':'specialist' if mode=='fork' else 'root'},'cell_count':2 if mode=='fork' else 1}
 definitions=[f'def host : Mat := {_mat(host)}',f'def delta : Mat := {_mat(delta)}',f'def basis : List Vec := {_vectors(protected)}',f'def native : List Vec := {_vectors(native)}',f'def claimedRoot : Mat := {_mat(deployment["root"])}',f'def claimedSpecialist : Option Mat := '+('some '+_mat(changed) if mode=='fork' else 'none')]
 obligations=[f'allowed host delta basis {str(case=="saturated").lower()} {mode_id} = {str(bool(legal)).lower()}', 'basisValid native 3 = true','covers basis native = true',f'rootAfter host delta {mode_id} = claimedRoot',f'specialistAfter host delta {mode_id} = claimedSpecialist',f'transferUsesSpecialist {mode_id} = {str(mode=="fork").lower()}',f'nativeUsesSpecialist {mode_id} = {str(deployment["router"]["native"]=="specialist").lower()}',f'cellCount {mode_id} = {deployment["cell_count"]}']
 if legal:
  definitions.extend(['theorem checked_basis : ∀ v ∈ basis, SameOn host claimedRoot v := by decide',
   'theorem registered_span_retention (terms : List (Int × Vec)) (membership : ∀ term ∈ terms, term.2 ∈ basis) : SameOn host claimedRoot (combine terms) := span_retention host claimedRoot terms (fun term member => checked_basis term.2 (membership term member))'])
  obligations.append('∀ v ∈ basis, SameOn host claimedRoot v')
 return _check({'kind':'deployment','visible':visible,'action':action},definitions,obligations,out_dir,legal,{'deployment':deployment,'legal':bool(legal),'delta_norm_sq':norm,'span_retention_theorem':'VerifiedGraftConcrete.registered_span_retention' if legal else None,'span_retention_axioms':SPAN_AXIOMS,'span_scope':'All integer linear combinations of the registered protected vectors, using the checked basis equalities.'})

def verify_adoption(parent_a,new_a,parent_b,new_b,adopted,out_dir):
 for value in (parent_a,new_a,parent_b,new_b):integer(value,0,10**12,'SSE')
 if type(adopted) is not bool:raise ValueError('adopted must be boolean')
 request={'kind':'adoption','parent_a':parent_a,'new_a':new_a,'parent_b':parent_b,'new_b':new_b,'adopted':adopted}
 obligation=f'improves ({parent_a}) ({new_a}) ({parent_b}) ({new_b}) = {str(adopted).lower()}'
 return _check(request,[],[obligation],out_dir,True,{'adopted':adopted})

def verify_conflict(host,target,witness,out_dir):
 matrix(host,2);matrix(target,6);vector(witness,1)
 different=apply(host,witness)!=apply(target,witness)
 definitions=[f'def host : Mat := {_mat(host)}',f'def target : Mat := {_mat(target)}',f'def witness : Vec := {_vec(witness)}']
 definitions.append('theorem universal_conflict (candidate : Mat) (preserved : apply candidate witness = apply host witness) : apply candidate witness ≠ apply target witness := conflict_witness host target candidate witness (by decide) preserved')
 obligations=['apply host witness ≠ apply target witness']
 result=_check({'kind':'conflict','host':host,'target':target,'witness':witness},definitions,obligations,out_dir,different,{'universal_theorem':'VerifiedGraftConcrete.universal_conflict','universal_theorem_axioms':[],'host_output':apply(host,witness),'target_output':apply(target,witness),'scope':'If this witness is protected, every candidate preserving its host output fails the conflicting target output. Membership in a deployment protected basis must be bound by the caller.'})
 return result

def verify_scores(deployment,target,batches,out_dir):
 deployment=copy.deepcopy(deployment);target=copy.deepcopy(target);batches=copy.deepcopy(batches)
 if type(deployment) is not dict or set(deployment)!={'root','specialist','router','cell_count'}:raise ValueError('deployment schema')
 matrix(deployment['root'],6)
 if deployment['specialist'] is not None:matrix(deployment['specialist'],6)
 if deployment['router'] not in ({'native':'root','new':'root'},{'native':'root','new':'specialist'}):raise ValueError('router schema')
 if deployment['router']['new']=='specialist' and deployment['specialist'] is None:raise ValueError('missing specialist')
 if type(deployment['cell_count']) is not int or deployment['cell_count']!=(1 if deployment['specialist'] is None else 2):raise ValueError('cell count')
 matrix(target,6)
 if type(batches) is not dict or not 1<=len(batches)<=8 or any(type(name) is not str for name in batches):raise ValueError('score batches schema')
 definitions=[f'def target : Mat := {_mat(target)}'];obligations=[];computed={}
 for i,(name,batch) in enumerate(sorted(batches.items())):
  if type(batch) is not dict or set(batch)!={'inputs','sse','task'} or batch['task'] not in ('native','new'):raise ValueError('batch schema')
  inputs=batch['inputs'];integer(batch['sse'],0,10**12,'SSE')
  if type(inputs) is not list or not 1<=len(inputs)<=256:raise ValueError('need 1..256 score inputs')
  for v in inputs:vector(v,32)
  actual=deployment[deployment['router'][batch['task']]]
  expected=sum(sum((a-b)**2 for a,b in zip(apply(actual,v),apply(target,v))) for v in inputs);computed[name]=expected
  definitions.extend([f'def actual{i} : Mat := {_mat(actual)}',f'def inputs{i} : List Vec := {_vectors(inputs)}'])
  obligations.append(f'totalError actual{i} target inputs{i} = ({batch["sse"]}:Int)')
 return _check({'kind':'scores','deployment':deployment,'target':target,'batches':batches},definitions,obligations,out_dir,True,{'computed_sse':computed})
