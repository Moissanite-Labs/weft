import tempfile
from pathlib import Path
import unittest
import numpy as np
import geometry as g

class GeometryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.payload,cls.report=g.build()
 def test_first_order_not_finite_invariance(self):
  c=self.report['nonlinear_counterexample']
  self.assertLess(abs(c['J_times_direction']),1e-14)
  self.assertGreater(abs(c['finite_drift']),.01)
 def test_registered_anchor_and_probe_fit(self):
  for name in ('source','permuted','independent'):
   f=self.report['fits'][name]
   self.assertLess(f['keep_max_abs_delta'],1e-10)
   self.assertLess(f['probe_target_rmse'],1e-10)
   self.assertEqual(f['keep']['rank']+f['keep']['nullity'],25)
 def test_permutation_equivariance_and_baseline(self):
  self.assertLess(self.report['permutation_equivariance_delta_max_abs'],1e-10)
  self.assertLess(max(self.report['permuted_baseline_max_abs_difference'].values()),1e-12)
 def test_saturated_constraints_exhaust_capacity(self):
  fit=self.report['rank_exhaustion']
  self.assertEqual(fit['keep']['nullity'],0)
  self.assertGreater(fit['probe_target_rmse'],.01)
 def test_new_points_have_no_preservation_guarantee(self):
  local=next(r for r in self.report['variants'] if r['model']=='source')
  self.assertGreater(local['metrics']['fresh_shifted']['delta_rmse'],1e-4)
 def test_permuted_copy_norm_is_fair(self):
  rows=[r for r in self.report['variants'] if r['model']=='permuted' and r['method'] in ('raw_copy','known_permutation_copy')]
  self.assertAlmostEqual(rows[0]['delta_l2'],rows[1]['delta_l2'],places=12)
  self.assertEqual(len(self.report['nonlinear_counterexample']['epsilon_sweep']),4)
 def test_capture_and_replay(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp);g.run(path);g.run(path,True)
   self.assertTrue((path/'manifest.json').exists())
if __name__=='__main__':unittest.main()
