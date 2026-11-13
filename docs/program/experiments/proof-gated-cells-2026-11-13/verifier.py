"""Trusted integer-to-Lean template. Candidate data cannot supply code or paths."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

SPEC=Path(__file__).with_name('Core.lean')
TOOLCHAIN='leanprover/lean4:v4.35.0'
THEOREM='ProofCellConcrete.certificate'
LIMIT=10**6
TEMPLATE_VERSION='closed-int-vec3-v1'

def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def vec(v):return '⟨'+','.join(str(x) for x in v)+'⟩'
def integer(x,name,limit=LIMIT):
 if type(x) is not int or abs(x)>limit:raise ValueError(name+' must be a bounded exact integer')
def validate(before,delta,anchors,frozen,radius_sq):
 for name,value in [('before',before),('delta',delta)]:
  if type(value) is not list or len(value)!=3:raise ValueError(name+' must have exactly 3 coordinates')
  for x in value:integer(x,name)
 if type(anchors) is not list or not 1<=len(anchors)<=64:raise ValueError('anchors needs 1..64 rows')
 for row in anchors:
  if type(row) is not list or len(row)!=3:raise ValueError('anchor row needs 3 coordinates')
  for x in row:integer(x,'anchor')
 if type(frozen) is not list or len(frozen)>3 or any(type(i) is not int or i not in range(3) for i in frozen) or len(set(frozen))!=len(frozen):raise ValueError('frozen indices must be a unique subset of 0,1,2')
 integer(radius_sq,'radius_sq',10**12)
 if radius_sq<0:raise ValueError('radius_sq must be nonnegative')

def verify_transition(before:list[int],delta:list[int],anchors:list[list[int]],frozen:list[int],radius_sq:int,out_dir:Path)->dict:
 """Compile exact accepted/rejected theorem and require empty concrete axiom set.

 Norm bound is per-transition squared Euclidean delta norm, not cumulative norm.
 Session identity, anchor immutability, CAS and atomic commits belong to the adapter.
 """
 validate(before,delta,anchors,frozen,radius_sq)
 request={'before':before,'delta':delta,'anchors':anchors,'frozen':frozen,'radius_sq':radius_sq}
 after=[b+d for b,d in zip(before,delta)]
 accepted=all(delta[i]==0 for i in frozen) and sum(d*d for d in delta)<=radius_sq and all(sum(a*d for a,d in zip(row,delta))==0 for row in anchors)
 anchor_literal='['+','.join(vec(row) for row in anchors)+']'
 args=f'{vec(delta)} {anchor_literal} {frozen!r} ({radius_sq}:Int)'
 allowed='Allowed '+args
 actual=f'({vec(after)} : Vec3) = add {vec(before)} {vec(delta)}'
 property=f'({actual}) ∧ ({allowed}) ∧ Guarantees {vec(before)} '+args if accepted else f'({actual}) ∧ ¬ ({allowed})'
 source=f'''import Core
namespace ProofCellConcrete
open ProofCell
set_option maxRecDepth 100000
set_option maxHeartbeats 2000000
theorem certificate : {property} := by decide
#check certificate
#print axioms certificate
end ProofCellConcrete
'''
 # Resolve installed pinned compiler without allowing elan to download a toolchain.
 compiler=Path.home()/'.elan/toolchains/leanprover--lean4---v4.35.0/bin/lean'
 if not compiler.is_file():raise RuntimeError('Pinned Lean 4.35.0 toolchain is not installed')
 out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
 env={k:v for k,v in os.environ.items() if k in ('PATH','LANG','LC_ALL','SYSTEMROOT','WINDIR')}
 (out_dir/'Certificate.lean').write_text(source)
 (out_dir/'request.json').write_bytes(canonical(request)+b'\n')
 logs=[];kernel_checked=False
 with tempfile.TemporaryDirectory(prefix='proof-cell-') as tmp:
  scratch=Path(tmp);(scratch/'Core.lean').write_bytes(SPEC.read_bytes());(scratch/'Certificate.lean').write_text(source)
  env['LEAN_PATH']=str(scratch)
  commands=([str(compiler),'--version'],[str(compiler),'-o','Core.olean','Core.lean'],[str(compiler),'Certificate.lean'])
  for command in commands:
   try:
    p=subprocess.run(command,cwd=scratch,env=env,capture_output=True,text=True,timeout=30)
   except subprocess.TimeoutExpired as exc:
    logs.append({'command':command[1:],'returncode':None,'stdout':(exc.stdout or b'').decode() if isinstance(exc.stdout,bytes) else exc.stdout or '', 'stderr':'Compiler timeout after 30 seconds','timeout':True})
    break
   logs.append({'command':command[1:],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
   if p.returncode:break
  expected=f"'{THEOREM}' does not depend on any axioms"
  kernel_checked=(len(logs)==3 and all(x['returncode']==0 for x in logs) and
                  'Lean (version 4.35.0,' in logs[0]['stdout'] and logs[2]['stdout'].strip().splitlines()[-1:]==[expected] and logs[2]['stdout'].startswith(THEOREM+' :') and not logs[2]['stderr'].strip())
 result={'accepted':accepted and kernel_checked,'kernel_checked':kernel_checked,'theorem':THEOREM,'axioms':[] if kernel_checked else None,
         'after':after,'before':before,'delta':delta,'anchors':anchors,'frozen':frozen,'radius_sq':radius_sq,
         'mathematical_gate_passed':accepted,'proofhash':sha(source.encode()),'specsha':sha(SPEC.read_bytes()),
         'request_sha256':sha(canonical(request)),'toolchain':TOOLCHAIN,'compilerlogs':logs,
         'trust_config':{'template':TEMPLATE_VERSION,'template_sha256':sha(Path(__file__).read_bytes()),'dimension':3,'arithmetic':'unbounded Lean Int; bounded host JSON ints',
                         'required_concrete_axioms':[],'generic_algebra_theorem_axioms':['propext','Quot.sound'],
                         'scope':'finite registered fixed-feature anchors; per-transition delta bound; no claim about adapter, hardware or natural world'}}
 (out_dir/'Certificate.lean').write_text(source)
 (out_dir/'verification.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 return result
