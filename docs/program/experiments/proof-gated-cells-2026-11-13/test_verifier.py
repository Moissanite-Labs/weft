import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from verifier import verify_transition

class VerifierTests(unittest.TestCase):
 def invoke(self,delta,anchors=None,frozen=None,radius=8):
  with tempfile.TemporaryDirectory() as tmp:
   result=verify_transition([3,1,5],delta,anchors or [[1,1,0],[0,0,1]],[2] if frozen is None else frozen,radius,Path(tmp))
   self.assertTrue((Path(tmp)/'request.json').exists())
   return result
 def test_nonzero_edit_checked_no_axioms(self):
  r=self.invoke([1,-1,0]);self.assertTrue(r['accepted']);self.assertTrue(r['kernel_checked']);self.assertEqual(r['axioms'],[]);self.assertEqual(r['after'],[4,0,5])
 def test_zero_edit_checked(self):self.assertTrue(self.invoke([0,0,0])['accepted'])
 def test_rejection_reasons_are_lean_checked(self):
  cases=[([1,0,0],None,None,8),([0,0,1],None,None,8),([3,-3,0],None,None,8),([1,-1,0],[[1,0,0],[0,1,0],[0,0,1]],[],8)]
  for delta,anchors,frozen,radius in cases:
   with self.subTest(delta=delta,anchors=anchors):
    r=self.invoke(delta,anchors,frozen,radius);self.assertFalse(r['accepted']);self.assertTrue(r['kernel_checked']);self.assertEqual(r['axioms'],[])
 def test_strict_data_validation(self):
  for delta in ([True,-1,0],[1.,-1,0],[1,-1],['1',-1,0],[10**8,-1,0]):
   with self.subTest(delta=delta),self.assertRaises(ValueError):self.invoke(delta)
  with self.assertRaises(ValueError):self.invoke([0,0,0],frozen=[3])
 def test_compiler_failure_cannot_accept_empty_output(self):
  fake=subprocess.CompletedProcess([],0,stdout='',stderr='')
  with patch('verifier.subprocess.run',return_value=fake):
   r=self.invoke([1,-1,0]);self.assertFalse(r['kernel_checked']);self.assertFalse(r['accepted'])
 def test_timeout_saved_and_fail_closed(self):
  with patch('verifier.subprocess.run',side_effect=subprocess.TimeoutExpired('lean',30)):
   r=self.invoke([1,-1,0]);self.assertFalse(r['kernel_checked']);self.assertFalse(r['accepted']);self.assertTrue(r['compilerlogs'][0]['timeout'])
if __name__=='__main__':unittest.main()
