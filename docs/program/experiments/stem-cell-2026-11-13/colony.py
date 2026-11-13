"""Bounded exact-integer cells. Genomes are data; there is no code evaluator."""
from __future__ import annotations
import copy
import hashlib
import json
import random

FIELDS={'gain_num','gain_den','deadband','bias','cap_low','cap_high'}
ROOT={'gain_num':1,'gain_den':1,'deadband':0,'bias':0,'cap_low':2,'cap_high':2}
FIXED={'gain_num':1,'gain_den':2,'deadband':1,'bias':0,'cap_low':1,'cap_high':2}
WEIGHTS={'quiet':(1,8),'urgent':(4,1)}
CONFIG={'version':'stem-integer-v1','seeds':[171,293],'branches':['quiet','urgent'],'generations':2,'children_per_request':4,
        'train_episodes':4,'validation_episodes':4,'test_episodes':8,'train_steps':12,'validation_steps':12,'test_steps':16,
        'initial_x':3,'target_min':-2,'target_max':8,'root_norm_sq':8,'anchors':[[1,1,0],[0,0,1]],'frozen':[2],
        'root_stem':ROOT,'fixed_hand_controller':FIXED,'max_colony_cells':4,'max_cpu_workers':2,'pressure_free_percent_pause':10,'pressure_free_percent_single_worker':25,
        'selection':'strictly lower validation total integer cost; ties retain parent, otherwise earliest submitted child',
        'allocation':'one immutable root stem; up to three copies allocated to positive paired validation benefits, initially one each then remaining to greatest benefit (quiet wins equal benefits)',
        'teacher_model':'gpt-6-astra','max_output_tokens':6000,
        'causal_pairing':'Within each seed/split, both demand branches have identical targets, urgency and initial_x; only integer cost weights differ.',
        'scope':'Exploratory controller differentiation; every policy step uses exact integer arithmetic; no natural-world safety claim.'}

def fingerprint(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def validate_genome(genome,parent_caps=ROOT):
 if type(genome) is not dict or set(genome)!=FIELDS:raise ValueError('genome requires exactly six declared fields')
 bounds={'gain_num':(0,4),'gain_den':(1,4),'deadband':(0,3),'bias':(-2,2),'cap_low':(0,2),'cap_high':(0,2)}
 for key,(low,high) in bounds.items():
  if type(genome[key]) is not int or not low<=genome[key]<=high:raise ValueError('invalid exact integer '+key)
 for key in ('cap_low','cap_high'):
  if genome[key]>parent_caps[key]:raise ValueError('child contract cannot loosen '+key)
 return copy.deepcopy(genome)
def action(genome,x,target,urgent):
 if type(x) is not int or type(target) is not int or type(urgent) is not bool:raise ValueError('step needs exact integer state/target and boolean urgency')
 error=target-x+genome['bias']
 raw=0 if abs(error)<=genome['deadband'] else (1 if error>0 else -1)*(genome['gain_num']*abs(error)//genome['gain_den'])
 cap=genome['cap_high'] if urgent else genome['cap_low']
 return max(-cap,min(cap,raw))
def step(genome,x,stimulus):
 k=action(genome,x,stimulus['target'],stimulus['urgent']);after=x+k
 cost=stimulus['error_weight']*(stimulus['target']-after)**2+stimulus['action_weight']*k*k
 return {'target':stimulus['target'],'urgent':stimulus['urgent'],'error_weight':stimulus['error_weight'],
         'action_weight':stimulus['action_weight'],'x_before':x,'k':k,'x_after':after,'cost':cost,
         'before_weights':[x,4-x,5],'after_weights':[after,4-after,5],'delta':[k,-k,0]}
def evaluate(genome,episodes):
 results=[]
 for episode in episodes:
  x=episode['initial_x'];steps=[]
  for stimulus in episode['stimuli']:
   row=step(genome,x,stimulus);steps.append(row);x=row['x_after']
  results.append({'initial_x':episode['initial_x'],'steps':steps,'final_x':x,'total_cost':sum(row['cost'] for row in steps)})
 return {'episode_results':results,'total_cost':sum(row['total_cost'] for row in results),'steps':sum(len(row['steps']) for row in results),
         'movement_squared':sum(s['k']**2 for row in results for s in row['steps']),
         'tracking_error_squared':sum((s['target']-s['x_after'])**2 for row in results for s in row['steps'])}
def make_episodes(seed,count,steps):
 rng=random.Random(seed);episodes=[]
 for _ in range(count):
  target=rng.randint(-2,8);stimuli=[]
  for t in range(steps):
   if t and t%3==0 and rng.random()<.75:target=rng.randint(-2,8)
   stimuli.append({'target':target,'urgent':rng.random()<.5})
  episodes.append({'initial_x':3,'stimuli':stimuli})
 return episodes
def demand_episodes(base,branch):
 ew,aw=WEIGHTS[branch]
 return [{'initial_x':e['initial_x'],'stimuli':[{**s,'error_weight':ew,'action_weight':aw} for s in e['stimuli']]} for e in base]
def experiment(seed):
 return {'seed':seed,'splits':{split:make_episodes(seed+offset,CONFIG[split+'_episodes'],CONFIG[split+'_steps'])
                             for split,offset in [('train',1000),('validation',2000),('test',3000)]}}
def random_child(parent,seed):
 rng=random.Random(seed)
 return {'gain_num':rng.randint(0,4),'gain_den':rng.randint(1,4),'deadband':rng.randint(0,3),'bias':rng.randint(-2,2),
         'cap_low':rng.randint(0,parent['cap_low']),'cap_high':rng.randint(0,parent['cap_high'])}
def allocate(selected,benefits):
 cells=[{'cell_id':'root-stem','branch':'stem','genome':copy.deepcopy(ROOT),'immutable_reserve':True}]
 counts={branch:0 for branch in CONFIG['branches']};eligible=[b for b in CONFIG['branches'] if benefits[b]>0]
 for branch in eligible:counts[branch]=1
 while eligible and sum(counts.values())<3:
  best=min(eligible,key=lambda b:(-benefits[b],CONFIG['branches'].index(b)));counts[best]+=1
 for branch in CONFIG['branches']:
  for i in range(counts[branch]):cells.append({'cell_id':f'{branch}-copy-{i}','branch':branch,'genome':copy.deepcopy(selected[branch]),'immutable_reserve':False})
 return {'cells':cells,'copy_counts':counts,'paired_validation_benefits':benefits,'max_cells':4}
def inspect(genome,x):
 """Pure uncommitted simulation view; production selections require proof_gate."""
 return {'genome':copy.deepcopy(genome),'x':x,'weights':[x,4-x,5]}
def propose(parent,child):
 """Pure data validation only. Returns a candidate, never installs it."""
 return validate_genome(child,parent)
def grow(selected,benefits):
 """Pure allocation plan. Actual experiment rollout checks every dispatched trace."""
 return allocate(selected,benefits)
