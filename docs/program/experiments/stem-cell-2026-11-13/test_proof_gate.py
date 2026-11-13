import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess
from proof_gate import verify_batch,simulate_episode

PARENT={'cap_low':2,'cap_high':2}
GENOME={'gain_num':1,'gain_den':2,'bias':0,'deadband':0,'cap_low':1,'cap_high':2}
EPISODES=[{'initial_x':3,'stimuli':[{'target':0,'urgent':True,'error_weight':2,'action_weight':1},{'target':7,'urgent':False,'error_weight':1,'action_weight':2}]}]
class ProofGateTests(unittest.TestCase):
 def gate(self,**kwargs):
  with tempfile.TemporaryDirectory() as directory:
   return verify_batch(kwargs.pop('parent_caps',PARENT),GENOME,EPISODES,Path(directory),**kwargs)
 def test_exact_policy_trace_cost_empty_axioms(self):
  r=self.gate();self.assertTrue(r['accepted']);self.assertEqual(r['axioms'],[])
  self.assertEqual([x['k'] for x in r['episode_results'][0]['steps']],[-1,1])
  self.assertEqual(r['total_cost'],27)
 def test_fabricated_action_state_and_score_fail_kernel(self):
  for field in ('k','x_after','cost','final_x','total_cost'):
   claimed=[simulate_episode(GENOME,EPISODES[0])]
   if field in ('final_x','total_cost'):claimed[0][field]+=1
   else:claimed[0]['steps'][0][field]+=1
   with self.subTest(field=field):
    r=self.gate(claimed_results=claimed);self.assertFalse(r['accepted']);self.assertFalse(r['kernel_checked'])
 def test_inherited_cap_cannot_weaken(self):
  r=self.gate(parent_caps={'cap_low':0,'cap_high':2})
  self.assertFalse(r['accepted']);self.assertFalse(r['contract_valid']);self.assertTrue(r['kernel_checked']);self.assertEqual(r['axioms'],[])
 def test_empty_compiler_output_fails_closed(self):
  with patch('proof_gate.subprocess.run',return_value=subprocess.CompletedProcess([],0,'','')):
   r=self.gate();self.assertFalse(r['accepted']);self.assertFalse(r['kernel_checked'])
 def test_exact_input_validation(self):
  with tempfile.TemporaryDirectory() as directory:
   for field,value in [('gain_num',True),('gain_den',0),('bias',1.0),('cap_low',3)]:
    genome=GENOME|{field:value}
    with self.subTest(field=field),self.assertRaises(ValueError):verify_batch(PARENT,genome,EPISODES,Path(directory))
if __name__=='__main__':unittest.main()
