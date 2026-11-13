"""Archive real Lean positive and negative policy-certificate controls, offline."""
import copy
import json
from pathlib import Path
from proof_gate import verify_batch,simulate_episode

ROOT=Path(__file__).resolve().parent
parent={'cap_low':2,'cap_high':2}
genome={'gain_num':1,'gain_den':2,'bias':0,'deadband':0,'cap_low':1,'cap_high':2}
episodes=[{'initial_x':3,'stimuli':[{'target':0,'urgent':True,'error_weight':2,'action_weight':1},{'target':7,'urgent':False,'error_weight':1,'action_weight':2}]}]
def main():
 results={}
 for label in ('positive','false_action','false_score','weakened_contract'):
  claimed=[simulate_episode(genome,e) for e in episodes]
  caps=parent
  if label=='false_action':claimed[0]['steps'][0]['k']+=1
  if label=='false_score':claimed[0]['total_cost']+=1
  if label=='weakened_contract':caps={'cap_low':0,'cap_high':2}
  result=verify_batch(caps,genome,episodes,ROOT/'data/proof_fixtures'/label,claimed_results=claimed)
  results[label]={'accepted':result['accepted'],'kernel_checked':result['kernel_checked'],'axioms':result['axioms'],'total_cost':result['total_cost']}
 assert results['positive']['accepted']
 assert all(not r['accepted'] for label,r in results.items() if label!='positive')
 (ROOT/'data/proof_fixtures/summary.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps(results,indent=2))
if __name__=='__main__':main()
