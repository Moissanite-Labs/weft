import copy
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import lab
import run_experiment as run

class Phase3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.exp=lab.generate_experiment(101)

    def test_dimensions_and_equations(self):
        self.assertEqual(sum(np.prod(s) for s in lab.SHAPES.values()),195)
        self.assertEqual(len(lab.editable_coordinates()),159)
        np.testing.assert_allclose(lab.target(self.exp['train']['x']),self.exp['train']['y'])
        self.assertEqual(self.exp,lab.generate_experiment(101))

    def test_paired_context_not_global_gain(self):
        source=self.exp['source']; after=copy.deepcopy(source)
        after['w2']=(np.asarray(after['w2'])*1.2).tolist()
        a=lab.conditional_metrics(source,self.exp['validation'],source)
        b=lab.conditional_metrics(after,self.exp['validation'],source)
        self.assertGreater(a['paired_context_contrast_mse'],.1)
        self.assertGreater(b['paired_context_contrast_mse'],.1)

    def test_operators_bounds_and_purity(self):
        source=self.exp['source']; original=copy.deepcopy(source)
        spec={'label':'ridge','operations':[{'op':'ridge_readout','units':list(range(16)),'alpha':.01,'blend':.5}]}
        compiled=lab.compile_candidate(source,self.exp['train'],spec)
        self.assertEqual(compiled['mechanism'],'ordinary_ridge_fitting')
        self.assertLessEqual(lab.patch_norm(compiled['patch']),5.+1e-12)
        self.assertEqual(source,original)
        self.assertEqual(compiled['cell']['w2'][2],source['w2'][2])
        with self.assertRaises(ValueError):
            lab.compile_candidate(source,self.exp['train'],{'label':'bad','operations':[{'op':'set_hidden','unit':0,'weights':[0.]*8,'bias':0.}]})
        with self.assertRaises(ValueError):
            lab.compile_candidate(source,self.exp['train'],{'label':'bad','operations':[{'op':'set_hidden','unit':4,'weights':[99.]*8,'bias':0.}]})

    def test_packet_and_shared_rollout(self):
        req=run.make_request(self.exp,1,[]); packet=json.loads(req['input'])
        self.assertEqual(packet['training_diagnostics']['training_only'],True)
        self.assertNotIn(self.exp['test']['id'],req['input'])
        cells=[self.exp['source']]+self.exp['siblings']
        before=copy.deepcopy(cells)
        self.assertEqual(lab.rollout(cells,steps=10),lab.rollout(cells,steps=10))
        self.assertEqual(cells,before)

    def test_response_invalid_and_request_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory); run.write(out/'config.json',run.CONFIG); run.write(out/'code-lock.json',run.code_hashes()); run.write(out/'experiments'/'seed-101.json',self.exp)
            pending=run.process(out)
            request=Path(pending[0])
            response={'response':{'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'hypothesis':'noop','candidates':[{'label':'noop','operations':[]}]*4})}]}]}}
            run.write(request.with_suffix('.response.json'),response)
            pending=run.process(out)
            self.assertEqual(len(pending),1)
            record=run.read(out/'candidates'/f'{run.name(101,1)}.json')
            self.assertEqual(len(record['candidates']),4)
            self.assertFalse(any(c['accepted'] for c in record['candidates']))
            changed=run.read(request); changed['input']='changed'; run.write(request,changed)
            with self.assertRaises(ValueError):run.process(out)

if __name__=='__main__':unittest.main()
