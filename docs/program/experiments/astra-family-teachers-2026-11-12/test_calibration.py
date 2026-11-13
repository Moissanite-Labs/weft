import copy
import json
import unittest
import numpy as np
import calibration as c

class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.exp=c.experiment()
    def envelope(self,patch):
        return {'response':{'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'hypothesis':'swap output rows',**patch})}]}]}}
    def test_exact_swap_and_heldout_gate(self):
        result=c.evaluate(self.exp,self.envelope(c.oracle_patch(self.exp['source'])))
        self.assertTrue(result['valid']); self.assertTrue(result['passed'])
        for metrics in result['metrics'].values():
            self.assertTrue(metrics['passed']); self.assertGreater(metrics['baseline_original_accuracy'],.95)
            self.assertAlmostEqual(metrics['oracle_logit_max_abs_difference'],0,places=12)
    def test_noop_fails(self): self.assertFalse(c.evaluate(self.exp,self.envelope({'edits':[]}))['passed'])
    def test_frozen_and_duplicate_rejected_atomic(self):
        before=copy.deepcopy(self.exp['source'])
        for edits in ([{'tensor':'w1','index':[0,0],'delta':1}], [{'tensor':'b2','index':[0],'delta':1}]*2):
            with self.assertRaises(ValueError): c.apply_patch(before,{'edits':edits})
        self.assertEqual(before,self.exp['source'])
    def test_request_only_examples_and_determinism(self):
        packet=json.loads(c.request(self.exp)['input'])
        self.assertNotIn('test',packet); self.assertNotIn('test_shift',packet)
        self.assertEqual(len(packet['examples']),c.CONFIG['examples_n'])
        self.assertEqual(len({c.CONFIG[k] for k in ('initialization_seed','train_seed','examples_seed','test_seed','shift_seed')}),5)
        self.assertEqual(c.train(),self.exp['source'])
        self.assertFalse(np.array_equal(np.asarray(self.exp['test']['x'])[:32],self.exp['examples']['x']))
    def test_incomplete_and_nonfinite_rejected(self):
        self.assertFalse(c.evaluate(self.exp,{'response':{'status':'incomplete'}})['valid'])
        with self.assertRaises(ValueError): c.apply_patch(self.exp['source'],{'edits':[{'tensor':'b2','index':[0],'delta':float('nan')}]})

if __name__=='__main__': unittest.main()
