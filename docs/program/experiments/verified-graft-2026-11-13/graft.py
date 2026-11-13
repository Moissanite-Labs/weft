"""Exact integer readout grafts. Actions are data, never source code."""
from __future__ import annotations
import copy
from fractions import Fraction
import hashlib
import json
import random

CONFIG={'version':'verified-graft-v1','seeds':[211,337],'outputs':2,'features':6,'cases':['compatible','saturated'],
        'max_rounds':2,'candidate_budget':4,'delta_bound':4,'radius_sq':192,'max_cells':2,
        'A_count':12,'B_count':12,'C_count':24,'calibration_count':8,'confirmation':'strict SSE reduction and 10*newSSE<=9*parentSSE on both A and B; rank A only; B evaluates provisional winner only; no B reranking',
        'stop':'stop when selected new-task coefficient matrix equals hidden target exactly; round 2 otherwise uses fresh A2/B2',
        'mode_policy':'compatible: graft/abstain; saturated: exact-preserving graft, routed fork or abstain; forks only saturated',
        'proposal_source':'separate deterministic mechanical control cohort and externally supplied real teacher cohort; no fabricated teacher responses',
        'scope':'Fixed integer linear readouts and explicit task-ID routing; not a general nonlinear or pretrained-model result'}
ZERO=[[0]*6 for _ in range(2)]
def fingerprint(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def matrix(x,name='matrix',bound=None):
 if type(x) is not list or len(x)!=2 or any(type(row) is not list or len(row)!=6 for row in x):raise ValueError(name+' must be 2x6')
 if any(type(v) is not int or (bound is not None and abs(v)>bound) for row in x for v in row):raise ValueError(name+' must contain bounded exact integers')
 return copy.deepcopy(x)
def add(a,b):return [[x+y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def subtract(a,b):return [[x-y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def apply(w,x):return [sum(a*b for a,b in zip(row,x)) for row in w]
def rank(rows):
 if not rows:return 0
 a=[[Fraction(v) for v in row] for row in rows];r=0
 for col in range(len(a[0])):
  pivot=next((i for i in range(r,len(a)) if a[i][col]),None)
  if pivot is None:continue
  a[r],a[pivot]=a[pivot],a[r];scale=a[r][col];a[r]=[v/scale for v in a[r]]
  for i in range(len(a)):
   if i!=r:
    scale=a[i][col];a[i]=[v-scale*u for v,u in zip(a[i],a[r])]
  r+=1
  if r==len(a):break
 return r
def coordinate_basis(permutation,signs,canonical_indices):
 return [[signs[i] if permutation[i]==j else 0 for i in range(6)] for j in canonical_indices]
def coordinates(x,permutation,signs):return [signs[i]*x[permutation[i]] for i in range(6)]
def represented(w,permutation,signs):return [[signs[i]*row[permutation[i]] for i in range(6)] for row in w]
def points(seed,count,omit_last=False):
 rng=random.Random(seed);dim=5 if omit_last else 6
 rows=[[1 if i==j else 0 for i in range(6)] for j in range(dim)]
 while len(rows)<count:rows.append([rng.randint(-2,2) if i<dim else 0 for i in range(6)])
 rng.shuffle(rows);return rows

def instance(seed):
 rng=random.Random(seed)
 while True:
  h=[[rng.randint(-2,2) for _ in range(6)] for _ in range(2)];g=[[rng.randint(-2,2) for _ in range(6)] for _ in range(2)]
  if any(h[o][j]!=g[o][j] for o in range(2) for j in range(3,6)) and any(h[o][j]!=g[o][j] for o in range(2) for j in range(3)) and any(g[o][5] for o in range(2)):break
 pd=list(range(6));pr=list(range(6));rng.shuffle(pd);rng.shuffle(pr)
 sd=[rng.choice([-1,1]) for _ in range(6)];sr=[rng.choice([-1,1]) for _ in range(6)]
 host=represented(h,pr,sr);donor=represented(g,pd,sd)
 composite=[[h[o][j] if j<3 else g[o][j] for j in range(6)] for o in range(2)]
 target=represented(composite,pr,sr)
 return {'seed':seed,'canonical_host':h,'canonical_donor':g,'donor_permutation':pd,'receiver_permutation':pr,'donor_signs':sd,'receiver_signs':sr,
         'host':host,'donor':donor,'target':target,'native_basis':coordinate_basis(pr,sr,range(3)),
         'full_basis':coordinate_basis(pr,sr,range(6)),
         'canonical_calibration':points(seed+1000,8),'canonical_rank5_calibration':points(seed+1000,8,True),
         'splits':{split:points(seed+offset,CONFIG[key]) for split,offset,key in [('A1',2000,'A_count'),('B1',3000,'B_count'),('A2',4000,'A_count'),('B2',5000,'B_count'),('C',6000,'C_count')]}}
def packet(exp,case,rank5=False):
 calibrations=exp['canonical_rank5_calibration'] if rank5 else exp['canonical_calibration']
 return {'version':CONFIG['version'],'host_weights':exp['host'],'donor_weights':exp['donor'],
         'native_basis':exp['native_basis'],'protected_basis':exp['native_basis'] if case=='compatible' else exp['full_basis'],
         'capacity_case':case,'calibration':[{'id':i,'donor_features':coordinates(x,exp['donor_permutation'],exp['donor_signs']),
                      'receiver_features':coordinates(x,exp['receiver_permutation'],exp['receiver_signs'])} for i,x in enumerate(calibrations)],
         'task':'New task: use host function on native_basis span and donor function on its orthogonal complement, after aligning paired activation coordinates. Native task keeps the host function on protected_basis span. Fork uses declared task IDs native/new.',
         'action_schema':{'mode':'graft|fork|abstain','delta':'2 rows x 6 exact integers -4..4, relative ORIGINAL host'},
         'constraints':{'delta_norm_sq_max':192,'max_cells':2,'fork_allowed':case=='saturated'}}
def infer_alignments(visible):
 pairs=visible['calibration'];receiver=[[row['receiver_features'][j] for row in pairs] for j in range(6)];donor=[[row['donor_features'][j] for row in pairs] for j in range(6)]
 possibilities=[]
 def visit(j,used,mapping):
  if j==6:possibilities.append(mapping);return
  for i in range(6):
   if i in used:continue
   for sign in (-1,1):
    if receiver[j]==[sign*v for v in donor[i]]:visit(j+1,used|{i},mapping+[(i,sign)])
 visit(0,set(),[])
 if not possibilities:raise ValueError('No signed permutation matches visible calibration')
 return possibilities
def aligned_donor(visible,mapping):return [[sign*visible['donor_weights'][o][i] for i,sign in mapping] for o in range(2)]
def native_columns(visible):
 columns=[]
 for row in visible['native_basis']:
  nz=[i for i,v in enumerate(row) if v]
  if len(nz)!=1 or abs(row[nz[0]])!=1:raise ValueError('This fixed experiment requires signed-coordinate native basis')
  columns.append(nz[0])
 return set(columns)
def proposed(visible,donor_in_receiver):
 delta=subtract(donor_in_receiver,visible['host_weights'])
 for row in delta:
  for j in native_columns(visible):row[j]=0
 return {'mode':'fork' if visible['capacity_case']=='saturated' else 'graft','delta':delta}
def controls(visible):
 alignments=infer_alignments(visible);correct=aligned_donor(visible,alignments[0]);mapping=alignments[0]
 scrambled=mapping[1:]+mapping[:1]
 return [{'label':'no_edit','action':{'mode':'abstain','delta':copy.deepcopy(ZERO)}},
         {'label':'mechanical_alignment','action':proposed(visible,correct)},
         {'label':'raw_coordinate_copy','action':proposed(visible,visible['donor_weights'])},
         {'label':'scrambled_correspondence','action':proposed(visible,aligned_donor(visible,scrambled))},
         {'label':'ungated_full_donor_replacement','action':{'mode':'graft','delta':subtract(correct,visible['host_weights'])}}]
def validate_action(action,visible):
 if type(action) is not dict or set(action)!={'mode','delta'} or action['mode'] not in ('graft','fork','abstain'):raise ValueError('action requires mode and delta only')
 delta=matrix(action['delta'],'delta',4)
 if sum(v*v for row in delta for v in row)>192:raise ValueError('delta norm bound')
 if action['mode']=='abstain' and delta!=ZERO:raise ValueError('abstain must have zero delta')
 if action['mode']=='fork' and (visible['capacity_case']!='saturated' or delta==ZERO):raise ValueError('fork only saturated with distinct specialist')
 if action['mode']=='graft' and any(apply(delta,v)!=[0,0] for v in visible['protected_basis']):raise ValueError('graft changes protected span')
 return copy.deepcopy(action)
def deployment(visible,action):
 validate_action(action,visible);host=copy.deepcopy(visible['host_weights']);changed=add(host,action['delta'])
 if action['mode']=='fork':return {'root':host,'specialist':changed,'router':{'native':'root','new':'specialist'},'cell_count':2}
 root=changed if action['mode']=='graft' else host
 return {'root':root,'specialist':None,'router':{'native':'root','new':'root'},'cell_count':1}
def function_for(deployed,task):return deployed[deployed['router'][task]]
def score(deployed,target,inputs,task='new'):
 w=function_for(deployed,task);residuals=[[a-b for a,b in zip(apply(w,x),apply(target,x))] for x in inputs]
 return {'SSE':sum(v*v for row in residuals for v in row),'n':len(inputs),'residuals':residuals}
def confirmed(parent_a,new_a,parent_b,new_b):
 return new_a<parent_a and new_b<parent_b and 10*new_a<=9*parent_a and 10*new_b<=9*parent_b
def receiver_inputs(exp,split):return [coordinates(x,exp['receiver_permutation'],exp['receiver_signs']) for x in exp['splits'][split]]
def conflict_witness(exp):
 for v in exp['full_basis']:
  if apply(exp['host'],v)!=apply(exp['target'],v):return {'vector':v,'host_output':apply(exp['host'],v),'target_output':apply(exp['target'],v)}
 raise ValueError('Expected nonzero capacity conflict')
def overfit_fixture():
 visible={'host_weights':copy.deepcopy(ZERO),'capacity_case':'compatible','native_basis':[[1 if j==i else 0 for j in range(6)] for i in range(3)],'protected_basis':[[1 if j==i else 0 for j in range(6)] for i in range(3)]}
 target=[[0,0,0,1,1,1],[0]*6];action={'mode':'graft','delta':[[0,0,0,1,1,-2],[0]*6]}
 parent=deployment(visible,{'mode':'abstain','delta':copy.deepcopy(ZERO)});child=deployment(visible,action)
 a=[[0,0,0,1,0,0],[0,0,0,0,1,0]];b=[[0,0,0,0,0,1],[0,0,0,0,0,-1]]
 scores={'parent_A':score(parent,target,a)['SSE'],'child_A':score(child,target,a)['SSE'],'parent_B':score(parent,target,b)['SSE'],'child_B':score(child,target,b)['SSE']}
 return {'visible':visible,'target':target,'action':action,'A':a,'B':b,'scores':scores,'adopted':confirmed(scores['parent_A'],scores['child_A'],scores['parent_B'],scores['child_B'])}
