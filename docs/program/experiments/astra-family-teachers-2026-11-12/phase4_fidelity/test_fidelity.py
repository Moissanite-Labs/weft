import copy
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import fidelity as f

class FidelityTests(unittest.TestCase):
 def test_all_sizes_precision_and_nonempty_planted_rows(self):
  for size in (64,256):
   for precision in ('raw','round2','round5'):
    for seed in (1103,1129):
     packet,oracle=f.readout(size,precision,seed)
     self.assertEqual(np.asarray(oracle['shown']).shape,(size,size))
     self.assertTrue(all(np.linalg.norm(oracle['shown'][r])>0 for r in oracle['planted_rows']))
     self.assertTrue(f.correct_top(oracle['planted_rows'],oracle['oracle']))
     self.assertNotIn('planted_rows',packet)
     self.assertEqual([row['row'] for row in packet['matrix_rows']],list(range(size)))
 def test_quantization_ties_scored_against_observed_values(self):
  original=np.array([[1.004],[1.003],[1.002],[1.001]])
  oracle=f.top_sets(np.round(original,2))
  self.assertTrue(f.correct_top([1,2,3],oracle))
  self.assertFalse(f.correct_top([1,1,3],oracle))
 def test_full_package_exact22_and_replay(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   cell={'w1':[[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.]],'b1':[0.,0.,0.],'w2':[[1.,0.,0.],[-1.,0.,0.]],'b2':[0.,0.]}
   f.write(root/'cal.json',{'source':cell});f.write(root/'org.json',{'source':cell})
   f.prepare(root/'out',root/'cal.json',root/'org.json')
   self.assertEqual(len(list((root/'out/requests').glob('*.json'))),22)
   for p in (root/'out/oracles').glob('*.json'):
    oracle=f.read(p);kind=oracle['kind']
    if kind=='A':answer={'rows':oracle['planted_rows']}
    elif kind=='B':answer={'edited_row':oracle['expected_row']}
    elif kind=='C':answer={'dominant_input_index':0,'threshold':0.,'class_above':0,'class_below':1}
    else:answer={'equivalent':oracle['equivalent']}
    f.write(root/'out/requests'/f'{p.stem}.response.json',{'response':{'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(answer)}]}]}})
   result=f.evaluate(root/'out'); self.assertEqual(result['completed'],22)
   self.assertTrue(all(row.get('correct',True) for row in result['results']))
   f.evaluate(root/'out',replay=True)
 def test_surgery_rejects_bad_shape_and_code(self):
  oracle={'kind':'B','expected_row':[1.,2.],'atol':1e-6}
  self.assertFalse(f.score({'edited_row':[1.]},oracle)['correct'])
  with self.assertRaises(ValueError):f.score({'edited_row':['exec(1)',2.]},oracle)

if __name__=='__main__':unittest.main()
