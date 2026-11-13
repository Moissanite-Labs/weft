import copy,json,tempfile,unittest
from pathlib import Path
import lab
import run_experiment as r
class FactorialTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.exp=lab.generate_experiment(71)
 def test_factorial_packets(self):
  with tempfile.TemporaryDirectory() as d:
   reference=None
   for arm in r.ARMS:
    p=json.loads(r.read(r.request(Path(d),self.exp,arm,1,[]))['input'])
    self.assertEqual(len(p['examples']),48)
    self.assertEqual(isinstance(p['cell']['w1'],list),arm in ('weights_hidden','weights_only'))
    self.assertEqual(all('hidden' in e for e in p['examples']),arm in ('weights_hidden','hidden_only'))
    e=[{k:v for k,v in x.items() if k!='hidden'} for x in p['examples']]
    if reference is None:reference=e
    self.assertEqual(reference,e);self.assertNotIn('test_shift',p);self.assertNotIn('siblings',p)
    self.assertNotIn(self.exp['test']['id'],json.dumps(p))
 def test_request_reconstruction(self):
  with tempfile.TemporaryDirectory() as d:
   r.request(Path(d),self.exp,'weights_hidden',1,[])
   changed=copy.deepcopy(self.exp);changed['source']['w1'][0][0]+=1
   with self.assertRaises(ValueError):r.request(Path(d),changed,'weights_hidden',1,[])
 def test_rounding_no_mutation(self):
  before=copy.deepcopy(self.exp);r.transcript(self.exp);self.assertEqual(before,self.exp)
  self.assertEqual(r.transcript(1.234567891),1.2345679)
 def test_counts_independence(self):
  self.assertEqual(len(r.CONFIG['source_seeds'])*sum(r.CONFIG['rounds_by_arm'].values()),40)
  old={s+o for s in (17,29,43) for o in (0,1000,2000,3000,4000,5000)}
  new={s+o for s in r.CONFIG['source_seeds'] for o in (0,1000,2000,3000,4000,5000)}
  self.assertFalse(old&new);self.assertEqual(len(new),30)
 def test_two_rounds_and_binding(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);r.write(out/'config.json',r.CONFIG);r.write(out/'experiments/seed-71.json',self.exp)
   for round in (1,2):
    pending=r.process(out);self.assertEqual(len(pending),4)
    for req in pending:r.write(Path(req).with_suffix('.response.json'),{'response':{'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'hypothesis':'null','edits':[]})}]}]}})
   self.assertEqual(r.process(out),[]);self.assertEqual(len(list((out/'candidates').glob('*.json'))),8)
   self.assertTrue(all(not r.read(p)['accepted'] for p in (out/'candidates').glob('*.json')))
   changed=copy.deepcopy(self.exp);changed['validation']['y'][0][0]+=1;r.write(out/'experiments/seed-71.json',changed)
   with self.assertRaises(ValueError):r.process(out)
if __name__=='__main__':unittest.main()
