import copy
from pathlib import Path
import tempfile
import unittest
from lifecycle_gate import verify_selection,verify_allocation
ROOT={'gain_num':1,'gain_den':1,'bias':0,'deadband':0,'cap_low':2,'cap_high':2}
CHILD=ROOT|{'cap_low':1}
class LifecycleTests(unittest.TestCase):
 def selection(self,costs,winner):
  with tempfile.TemporaryDirectory() as d:return verify_selection([ROOT,CHILD],costs,[True,True],winner,Path(d))
 def test_stable_minimum(self):
  self.assertTrue(self.selection([20,10],1)['accepted'])
  self.assertFalse(self.selection([20,10],0)['accepted'])
  self.assertFalse(self.selection([10,10],1)['accepted'])
 def test_exact_root_and_clones(self):
  cells=[{'branch':'stem','genome':ROOT},{'branch':'quiet','genome':CHILD},{'branch':'quiet','genome':CHILD},{'branch':'urgent','genome':ROOT}]
  with tempfile.TemporaryDirectory() as d:
   r=verify_allocation(ROOT,[CHILD,ROOT],[10,5],cells,Path(d));self.assertTrue(r['accepted']);self.assertEqual(r['axioms'],[])
  cells[1]['genome']=ROOT
  with tempfile.TemporaryDirectory() as d:self.assertFalse(verify_allocation(ROOT,[CHILD,ROOT],[10,5],cells,Path(d))['accepted'])
if __name__=='__main__':unittest.main()
