import copy
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from proof_gate import verify_deployment,verify_scores,verify_conflict,verify_adoption

ZERO=[[0]*6 for _ in range(2)]
BASIS=[[int(i==j) for j in range(6)] for i in range(6)]
VISIBLE={'host_weights':ZERO,'capacity_case':'compatible','protected_basis':BASIS[:3],'native_basis':BASIS[:3]}
DELTA=[[0,0,0,1,1,-2],[0,0,0,0,1,0]]
class GateTests(unittest.TestCase):
 def deployment(self,visible=None,action=None):
  with tempfile.TemporaryDirectory() as d:return verify_deployment(visible or VISIBLE,action or {'mode':'graft','delta':DELTA},Path(d))
 def test_multicoordinate_graft_and_span(self):
  r=self.deployment();self.assertTrue(r['accepted']);self.assertEqual(r['axioms'],[]);self.assertEqual(r['deployment']['root'],DELTA)
  self.assertEqual(r['span_retention_theorem'],'VerifiedGraftConcrete.registered_span_retention')
 def test_saturated_graft_denied_fork_preserves_root(self):
  visible=VISIBLE|{'capacity_case':'saturated','protected_basis':BASIS}
  r=self.deployment(visible);self.assertFalse(r['accepted']);self.assertTrue(r['kernel_checked'])
  f=self.deployment(visible,{'mode':'fork','delta':DELTA});self.assertTrue(f['accepted']);self.assertEqual(f['deployment']['root'],ZERO);self.assertEqual(f['deployment']['specialist'],DELTA);self.assertEqual(f['deployment']['router'],{'native':'root','new':'specialist'})
 def test_illegal_preservation_and_fork_cases(self):
  wrong=copy.deepcopy(DELTA);wrong[0][0]=1
  self.assertFalse(self.deployment(action={'mode':'graft','delta':wrong})['accepted'])
  self.assertFalse(self.deployment(action={'mode':'fork','delta':DELTA})['accepted'])
  saturated=VISIBLE|{'capacity_case':'saturated','protected_basis':BASIS}
  self.assertFalse(self.deployment(saturated,{'mode':'fork','delta':ZERO})['accepted'])
 def test_strict_data(self):
  for value in (True,1.0,5):
   wrong=copy.deepcopy(DELTA);wrong[0][3]=value
   with self.subTest(value=value),self.assertRaises(ValueError):self.deployment(action={'mode':'graft','delta':wrong})
 def test_score_and_adoption_reject_overfitter(self):
  target=[[0,0,0,1,1,1],[0]*6]
  overfit=[[0,0,0,1,1,-2],[0]*6]
  deployment={'root':overfit,'specialist':None,'router':{'native':'root','new':'root'},'cell_count':1}
  batches={'A':{'inputs':BASIS[3:5],'sse':0,'task':'new'},'B':{'inputs':[BASIS[5],[-x for x in BASIS[5]]],'sse':18,'task':'new'}}
  with tempfile.TemporaryDirectory() as d:
   r=verify_scores(deployment,target,batches,Path(d));self.assertTrue(r['accepted']);self.assertEqual(r['axioms'],[])
  batches['B']['sse']=0
  with tempfile.TemporaryDirectory() as d:self.assertFalse(verify_scores(deployment,target,batches,Path(d))['accepted'])
  with tempfile.TemporaryDirectory() as d:self.assertTrue(verify_adoption(2,0,2,18,False,Path(d))['accepted'])
  with tempfile.TemporaryDirectory() as d:self.assertFalse(verify_adoption(2,0,2,18,True,Path(d))['accepted'])
 def test_universal_conflict(self):
  with tempfile.TemporaryDirectory() as d:
   r=verify_conflict(ZERO,DELTA,BASIS[3],Path(d));self.assertTrue(r['accepted']);self.assertEqual(r['axioms'],[])
  with tempfile.TemporaryDirectory() as d:self.assertFalse(verify_conflict(ZERO,ZERO,BASIS[3],Path(d))['accepted'])
 def test_empty_compiler_output_fails_closed(self):
  with patch('proof_gate.subprocess.run',return_value=subprocess.CompletedProcess([],0,'','')):
   self.assertFalse(self.deployment()['accepted'])
if __name__=='__main__':unittest.main()
