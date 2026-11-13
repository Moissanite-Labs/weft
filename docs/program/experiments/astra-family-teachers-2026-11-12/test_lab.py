import copy
import json
import unittest
import numpy as np
import lab

class LabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exp=lab.generate_experiment(17)

    def test_reproducible_and_json_roundtrip(self):
        self.assertEqual(self.exp,lab.generate_experiment(17))
        self.assertEqual(self.exp,json.loads(json.dumps(self.exp)))
        ids=[self.exp[k]['id'] for k in ('train','validation','test','test_shift')]
        self.assertEqual(len(ids),len(set(ids)))

    def test_base_is_trained_and_secondary_preserved(self):
        metrics=lab.evaluate(self.exp['source'],self.exp['test'])
        self.assertLess(metrics['hazard_mse'],.01)
        self.assertLess(metrics['preserved_movement_mse'],.002)
        self.assertGreater(metrics['active_movement_mse'],.01)

    def test_patch_atomic_frozen_and_bounds(self):
        c=self.exp['source']; before=copy.deepcopy(c)
        p={'edits':[{'tensor':'w2','index':[0,4],'delta':.1}]}
        changed=lab.apply_patch(c,p)
        self.assertEqual(c,before)
        self.assertEqual(changed['w1'],c['w1'])
        self.assertNotEqual(changed['w2'],c['w2'])
        bads=[{'tensor':'w1','index':[0,0],'delta':.1},
              {'tensor':'w2','index':[0,0],'delta':float('nan')},
              {'tensor':'w2','index':[0,0],'delta':.8},
              {'tensor':'w2','index':[-1,0],'delta':.1}]
        for e in bads:
            with self.assertRaises(ValueError): lab.apply_patch(c,{'edits':[e]})
        with self.assertRaises(ValueError): lab.apply_patch(c,{'edits':p['edits']*2})
        self.assertEqual(c,before)
        too_large={'edits':[{'tensor':'w2','index':[i//10,i%10],'delta':.75} for i in range(8)]}
        with self.assertRaises(ValueError): lab.apply_patch(c,too_large)

    def test_permutation_transfer_exact_function(self):
        c=self.exp['source']; sibling=copy.deepcopy(c)
        order=np.array([3,2,1,0,9,8,7,6,5,4])
        sibling['unit_ids']=order.tolist()
        sibling['w1']=np.asarray(c['w1'])[order].tolist()
        sibling['b1']=np.asarray(c['b1'])[order].tolist()
        sibling['w2']=np.asarray(c['w2'])[:,order].tolist()
        p={'edits':[{'tensor':'w1','index':[4,2],'delta':.2},{'tensor':'w2','index':[1,4],'delta':-.3},{'tensor':'b1','index':[5],'delta':.1}]}
        a=lab.predict(lab.apply_patch(c,p),self.exp['test']['x'])
        b=lab.predict(lab.apply_patch(sibling,lab.transfer_patch(p,c,sibling)),self.exp['test']['x'])
        np.testing.assert_allclose(a,b,atol=1e-14)
        raw=lab.predict(lab.apply_patch(sibling,p),self.exp['test']['x'])
        self.assertGreater(np.max(np.abs(a-raw)),.01)

    def test_matched_random_and_budget(self):
        p={'edits':[{'tensor':'w2','index':[0,4],'delta':.4},{'tensor':'w2','index':[1,5],'delta':.2}]}
        random=lab.random_patch(12,lab.patch_norm(p),p)
        self.assertAlmostEqual(lab.patch_norm(random),lab.patch_norm(p))
        self.assertEqual([e['index'] for e in random['edits']],[e['index'] for e in p['edits']])
        saturated=lab.random_patch(12,.75*np.sqrt(2),p)
        lab.apply_patch(self.exp['source'],saturated)
        self.assertAlmostEqual(lab.patch_norm(saturated),.75*np.sqrt(2))
        result=lab.local_evolution(self.exp['source'],self.exp['validation'],proposals=3)
        self.assertEqual(len(result['trace']),3)
        self.assertEqual(result['candidate_evaluations'],3)

    def test_packet_no_test_and_no_global_state(self):
        original=copy.deepcopy(self.exp)
        packet=lab.teacher_packet(self.exp['source'],self.exp['train'],self.exp['validation'])
        serialized=json.dumps(packet)
        self.assertNotIn(self.exp['test']['id'],serialized)
        self.assertNotIn('test_shift',serialized)
        packet['cell']['w1'][0][0]+=99
        lab.evaluate(self.exp['source'],self.exp['test'])
        self.assertEqual(self.exp,original)
        blind=lab.teacher_packet(self.exp['source'],self.exp['train'],visibility='behavior')
        self.assertNotIn('cell',blind)
        self.assertTrue(all('hidden' not in e for e in blind['examples']))
        self.assertIn('tensor_shapes',blind)

    def test_rollout_shared_deterministic_no_mutation(self):
        cells=[self.exp['source'],self.exp['siblings'][0]]
        original=copy.deepcopy(cells)
        a=lab.rollout(cells,steps=30)
        self.assertEqual(a,lab.rollout(cells,steps=30))
        self.assertEqual(cells,original)
        self.assertTrue(a['exploratory'])
        self.assertEqual(a['cells'],2)

if __name__=='__main__': unittest.main()
