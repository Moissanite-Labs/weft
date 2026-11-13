#!/usr/bin/env python3
"""Offline Soko API convergence probe using pinned, reviewed static checkers."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

PIN='c3afb8d4b17b1b6ebcceaa05704320d555e2c013'
# Trusted source constants. No caller can provide checker code.
SPEC='''def initial_state():
    return (0, (3, 1, 5))
def actions(state):
    if state[0] != 0:
        return ()
    return ((0,1,-1,0),(0,1,0,0),(0,0,0,1),(0,3,-3,0),(1,1,-1,0),(0,0,0,0))
def step(state, action):
    version, weights = state
    expected = action[0]
    delta = action[1:]
    anchors = ((1,1,0),(0,0,1))
    if version != 0 or expected != version:
        return None
    if sum(d*d for d in delta) > 8:
        return None
    if any(delta[i] != 0 for i in (2,)):
        return None
    for anchor in anchors:
        if sum(a*d for a,d in zip(anchor,delta)) != 0:
            return None
    return (version+1, tuple(w+d for w,d in zip(weights,delta)))
def is_goal(state):
    return state == (1,(4,0,5))
def invariant(state):
    version, weights = state
    anchors = ((1,1,0),(0,0,1))
    original = (3,1,5)
    return all(sum(a*w for a,w in zip(row,weights)) == sum(a*w for a,w in zip(row,original)) for row in anchors) and weights[2] == 5
def project_obs(state):
    return (state[0],state[1][0],state[1][1],state[1][2])
'''
IMPL='''def initial_state():
    return (0,3,1,5)
def actions(s):
    choices = ((0,1,-1,0),(0,1,0,0),(0,0,0,1),(0,3,-3,0),(1,1,-1,0),(0,0,0,0))
    return choices if s[0] == 0 else ()
def step(s, a):
    if s[0] != 0:
        return None
    if a[0] != s[0]:
        return None
    dx,dy,dz = a[1],a[2],a[3]
    if dx*dx + dy*dy + dz*dz > 8:
        return None
    if dz != 0:
        return None
    if dx+dy != 0:
        return None
    return (s[0]+1,s[1]+dx,s[2]+dy,s[3]+dz)
def is_goal(s):
    return s[0] == 1 and s[1] == 4 and s[2] == 0 and s[3] == 5
def invariant(s):
    return s[1]+s[2] == 4 and s[3] == 5
def project_obs(s):
    return s
'''
TRACES={'accepted_nonzero':[[0,1,-1,0]],'rejected_anchor':[[0,1,0,0]],
        'rejected_frozen':[[0,0,0,1]],'rejected_norm':[[0,3,-3,0]],
        'rejected_stale_version':[[1,1,-1,0]],'zero_valid_but_not_goal':[[0,0,0,0]],
        'rejected_after_terminal':[[0,1,-1,0],[0,1,-1,0]]}

def write(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def sha(x):return hashlib.sha256(x).hexdigest()
def run(checkout:Path,out:Path):
 checkout=checkout.resolve()
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()
 if commit!=PIN:raise ValueError('Soko checkout does not match pinned commit')
 changes=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=checkout,text=True)
 if changes.strip():raise ValueError('Soko tracked sources have local changes')
 # Pin every Python source imported from this checkout, rather than installing dependencies.
 sys.path.insert(0,str(checkout))
 server=importlib.import_module('soko_mcp.server')
 if Path(server.__file__).resolve()!=checkout/'soko_mcp/server.py':raise ValueError('A different Soko module was already imported')
 dispatch_tool_call=server.dispatch_tool_call
 mutation=IMPL.replace('    if dx*dx + dy*dy + dz*dz > 8:\n        return None\n','')
 definition={'system_id':'proofcell_int3_bridge_v1','description':'Fixed one-step Int3 readout transition; runtime dual replay, not a Lean proof',
             'spec_code':SPEC,'impl_code':IMPL,'positive_witnesses':[{'name':'accepted_nonzero','trace':TRACES['accepted_nonzero']}],
             'must_fail_controls':[{'name':name,'trace':trace} for name,trace in TRACES.items() if name!='accepted_nonzero'],
             'planted_mutations':[{'bug_id':'remove_norm_bound','description':'Permit an oversized anchor-preserving delta','mutated_code':mutation}],
             'bounded_fuzz_nodes':32,'exact_arithmetic_only':True,'strict_bar':True}
 calls=[{'name':'formal_define_system','arguments':definition}]
 responses=[dispatch_tool_call(calls[0]['name'],calls[0]['arguments'])]
 if not responses[0].get('tcb_locked'):raise RuntimeError('Soko registration rejected: '+json.dumps(responses[0]))
 traces={}
 for name,trace in TRACES.items():
  call={'name':'formal_verify_trace','arguments':{'system_id':definition['system_id'],'trace':trace,'verification_goal':'goal_witness','require_exact_terminal_goal':True}}
  calls.append(call);result=dispatch_tool_call(call['name'],call['arguments']);responses.append(result);traces[name]=result
 if not traces['accepted_nonzero']['verified'] or any(result['verified'] for name,result in traces.items() if name!='accepted_nonzero'):
  raise RuntimeError('Unexpected positive/negative trace outcome')
 sources={}
 for module in list(sys.modules.values()):
  path=getattr(module,'__file__',None)
  if path:
   p=Path(path).resolve()
   if checkout in p.parents and p.suffix=='.py':sources[str(p.relative_to(checkout))]=sha(p.read_bytes())
 report={'soko_commit':PIN,'source_sha256':sources,'bridge_sha256':sha(Path(__file__).read_bytes()),
         'checkers':{'spec_sha256':sha(SPEC.encode()),'impl_sha256':sha(IMPL.encode())},'registration':responses[0],
         'traces':traces,'lean_proof':False,'scope':'Actual Soko formal API dual-checker runtime replay with bounded differential fuzz and planted mutation; not a Lean proof or universal theorem. Finite action alphabet and one-step world only.',
         'redundancy':'Frozen coordinate 2 is also protected by anchor [0,0,1]; this probe does not isolate those two restrictions.',
         'zero_scope':'Zero edit preserves constraints but does not satisfy the nonzero target goal.'}
 write(out/'requests.json',calls);write(out/'returned_tool_results.json',responses);write(out/'summary.json',report)
 (out/'spec.py.txt').write_text(SPEC);(out/'impl.py.txt').write_text(IMPL)
 print(json.dumps({'soko_commit':PIN,'registered':True,'trace_count':len(traces),'positive_verified':1,'negative_rejected':len(traces)-1,'lean_proof':False}))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--soko-checkout',type=Path,required=True);p.add_argument('--out',type=Path,default=Path(__file__).with_name('data')/'soko_bridge');a=p.parse_args();run(a.soko_checkout,a.out)
