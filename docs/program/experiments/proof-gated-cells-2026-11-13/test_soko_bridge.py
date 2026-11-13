"""Integration tests require an explicit pinned local Soko checkout; no network."""
import os
from pathlib import Path
import tempfile
import unittest
from soko_bridge import run,PIN

@unittest.skipUnless(os.environ.get('SOKO_CHECKOUT'),'set SOKO_CHECKOUT to the pinned local repository')
class SokoBridgeTests(unittest.TestCase):
 def test_actual_dual_checker_api(self):
  with tempfile.TemporaryDirectory() as tmp:
   r=run(Path(os.environ['SOKO_CHECKOUT']),Path(tmp))
   self.assertEqual(r['soko_commit'],PIN)
   self.assertFalse(r['lean_proof'])
   self.assertTrue(r['registration']['tcb_locked'])
   self.assertEqual(r['registration']['planted_mutations']['killed'],1)
   self.assertEqual(r['registration']['must_fail_controls_rejected'],6)
   self.assertGreater(r['registration']['differential_fuzz']['edges_checked'],0)
   self.assertNotEqual(r['registration']['checker_pins']['spec_ast_skeleton_sha256'],r['registration']['checker_pins']['impl_ast_skeleton_sha256'])
   self.assertEqual(r['traces']['accepted_nonzero']['final_obs_repr'],'(1, 4, 0, 5)')
   self.assertTrue(all(v['differential_match'] for v in r['traces'].values()))
   self.assertTrue(all(not v['verified'] for k,v in r['traces'].items() if k!='accepted_nonzero'))
   self.assertTrue((Path(tmp)/'requests.json').exists())
   self.assertIn('soko_mcp/formal_kernel.py',r['source_sha256'])
if __name__=='__main__':unittest.main()
