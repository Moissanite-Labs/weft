import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import colony as c
import run_experiment as r

class ColonyTests(unittest.TestCase):
 def test_exact_sign_magnitude_floor(self):
  g={**c.ROOT,'gain_den':2,'cap_low':2,'cap_high':2}
  self.assertEqual(c.action(g,3,0,False),-1)
  self.assertEqual(c.action(g,3,6,False),1)
 def test_caps_cannot_loosen_and_strict_types(self):
  for g in ({**c.ROOT,'cap_low':True},{**c.ROOT,'gain_den':0},{**c.ROOT,'gain_num':1.0}):
   with self.assertRaises(ValueError):c.validate_genome(g)
  with self.assertRaises(ValueError):c.validate_genome(c.ROOT,{**c.ROOT,'cap_low':1})
 def test_paired_demands_only_change_cost(self):
  exp=c.experiment(171)
  for split in ('train','validation','test'):
   quiet=c.demand_episodes(exp['splits'][split],'quiet');urgent=c.demand_episodes(exp['splits'][split],'urgent')
   for a,b in zip(quiet,urgent):
    self.assertEqual(a['initial_x'],b['initial_x'])
    self.assertEqual([(x['target'],x['urgent']) for x in a['stimuli']],[(x['target'],x['urgent']) for x in b['stimuli']])
 def test_simulation_invariants(self):
  result=c.evaluate(c.ROOT,c.demand_episodes(c.experiment(171)['splits']['train'],'urgent'))
  for episode in result['episode_results']:
   for row in episode['steps']:
    self.assertLessEqual(sum(x*x for x in row['delta']),8)
    self.assertEqual(sum(row['after_weights'][:2]),4);self.assertEqual(row['after_weights'][2],5)
 def test_parent_wins_tie_and_stable_child_ties(self):
  rows=[{'index':i,'genome':{**c.ROOT,'bias':i},'eligible':True,'validation':{'total_cost':5}} for i in (1,0)]
  self.assertEqual(r.best_candidate(rows,c.ROOT,5),(c.ROOT,None))
  self.assertEqual(r.best_candidate(rows,c.ROOT,6)[1],0)
 def test_stem_reserve_and_bounded_clone_allocation(self):
  selected={b:{**c.ROOT,'cap_low':1} for b in c.CONFIG['branches']}
  a=c.allocate(selected,{'quiet':3,'urgent':3})
  self.assertEqual(a['copy_counts'],{'quiet':2,'urgent':1});self.assertEqual(len(a['cells']),4)
  self.assertEqual(a['cells'][0]['genome'],c.ROOT)
  self.assertEqual(len(c.allocate(selected,{'quiet':0,'urgent':-1})['cells']),1)
 def test_scheduler_all_fixture_states(self):
  self.assertEqual(r.pressure_observation('normal')['workers'],2)
  for level in ('pressure','unknown'):self.assertEqual(r.pressure_observation(level)['workers'],1)
  self.assertTrue(r.pressure_observation('critical')['paused'])
 def test_request_has_no_test_or_heldout_and_small(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=r.make_request(Path(tmp),c.experiment(171),'quiet',1,c.ROOT,[])
   packet=json.loads(r.read(path)['input'])
   self.assertNotIn('test',packet);self.assertNotIn('splits',packet)
   self.assertEqual(len(packet['train_episodes']),4);self.assertLess(path.stat().st_size,10000)
 def test_proof_tampering_fails_closed(self):
  episodes=c.demand_episodes(c.experiment(171)['splits']['train'],'quiet')
  with patch('proof_gate.verify_batch',return_value={'accepted':True,'kernel_checked':True,'axioms':[],'total_cost':0,'episode_results':[]}):
   with self.assertRaises(ValueError):r.checked(c.ROOT,c.ROOT,episodes,Path('/unused'))
 def test_full_offline_two_generation_workflow_and_pressure_pause(self):
  def proof(parent,genome,episodes,outdir):
   result=c.evaluate(genome,episodes)
   rows=[{'initial_x':row['initial_x'],'final_x':row['final_x'],'total_cost':row['total_cost'],'steps':[{k:step[k] for k in ('target','urgent','error_weight','action_weight','x_before','k','x_after','cost')} for step in row['steps']]} for row in result['episode_results']]
   return {'accepted':True,'kernel_checked':True,'axioms':[],'episode_results':rows,'total_cost':result['total_cost']}
  life={'accepted':True,'kernel_checked':True,'axioms':[]}
  with tempfile.TemporaryDirectory() as tmp,patch.dict(c.CONFIG,{'seeds':[901,907]}),patch('proof_gate.verify_batch',side_effect=proof),patch('lifecycle_gate.verify_selection',return_value=life),patch('lifecycle_gate.verify_allocation',return_value=life):
   out=Path(tmp);r.write(out/'config.json',c.CONFIG)
   for seed in c.CONFIG['seeds']:r.write(out/'experiments'/f'seed-{seed}.json',c.experiment(seed))
   for seed in c.CONFIG['seeds']:
    for branch in c.CONFIG['branches']:r.make_request(out,c.experiment(seed),branch,1,c.ROOT,[])
   r.register(out)
   pending=r.process(out,'normal');self.assertEqual(len(pending),4)
   for generation in (1,2):
    for path_string in pending:
     path=Path(path_string)
     children=[{'label':'root','genome':c.ROOT},{'label':'tight','genome':{**c.ROOT,'cap_low':0,'cap_high':0}},{'label':'invalid','genome':{**c.ROOT,'cap_low':3}},{'label':'duplicate','genome':c.ROOT}]
     text=json.dumps({'hypothesis':'synthetic wiring fixture','children':children})
     wire={**r.read(path),'store':False,'service_tier':'default'};wire_bytes=json.dumps(wire,ensure_ascii=False).encode()
     path.with_suffix('.wire.json').write_bytes(wire_bytes+b'\n')
     r.write(path.with_suffix('.response.json'),{'request_file':path.name,'request_sha256':__import__('hashlib').sha256(wire_bytes).hexdigest(),'response':{'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':text}]}]}})
    if generation==1:
     r.process(out,'critical');self.assertFalse((out/'selections').exists())
    pending=r.process(out,'normal')
   self.assertFalse(pending);self.assertEqual(len(list((out/'selections').glob('*.json'))),8)
   self.assertTrue((out/'selection_lock.json').exists())
   report=r.finish(out)
   self.assertEqual(len(report['colonies']),2)
   self.assertTrue(all(len(row['allocation']['cells'])<=4 for row in report['colonies']))
   for path in (out/'selections').glob('*.json'):
    record=r.read(path);self.assertFalse(record['children'][2]['valid']);self.assertEqual(record['children'][3]['duplicate_of'],0)

 def test_wire_response_and_registration_bindings(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);path=r.make_request(out,c.experiment(171),'quiet',1,c.ROOT,[]);r.register(out)
   wire={**r.read(path),'store':False,'service_tier':'default'};data=json.dumps(wire,ensure_ascii=False).encode();path.with_suffix('.wire.json').write_bytes(data+b'\n')
   envelope={'request_file':path.name,'request_sha256':__import__('hashlib').sha256(data).hexdigest()}
   r.validate_response_binding(path,envelope,r.read(out/'registration.json'))
   for changed in ({**envelope,'request_file':'wrong.json'},{**envelope,'request_sha256':'0'*64}):
    with self.assertRaises(ValueError):r.validate_response_binding(path,changed,r.read(out/'registration.json'))
   with patch('run_experiment.code_pins',return_value={}):
    with self.assertRaises(ValueError):r.validate_registration(out)
 def test_registered_validation_and_test_data_cannot_change(self):
  for split in ('validation','test'):
   with self.subTest(split=split),tempfile.TemporaryDirectory() as tmp:
    out=Path(tmp);path=out/'experiments/seed-171.json';exp=c.experiment(171);r.write(path,exp);r.register(out)
    r.validate_registration(out)
    exp['splits'][split][0]['stimuli'][0]['target']+=1;r.write(path,exp)
    with self.assertRaises(ValueError):r.validate_registration(out)

 def test_selection_and_retained_proof_tampering(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);artifact=out/'proofs/a/Certificate.lean';artifact.parent.mkdir(parents=True);artifact.write_text('original')
   path=out/'selections/a.json';record={'selected_index':0,'retained_artifact_sha256':{str(artifact.relative_to(out)):r.bytehash(artifact)}};r.write(path,record)
   r.log(out,{'type':'selection','selection_file':str(path.relative_to(out)),'selection_sha256':c.fingerprint(record)})
   r.validate_retained_selection(out,path,record)
   with self.assertRaises(ValueError):r.validate_retained_selection(out,path,{**record,'selected_index':1})
   artifact.write_text('modified')
   with self.assertRaises(ValueError):r.validate_retained_selection(out,path,record)

 def test_real_lean_trace_matches_independent_simulator(self):
  episodes=[{'initial_x':3,'stimuli':[{'target':6,'urgent':True,'error_weight':4,'action_weight':1},{'target':0,'urgent':False,'error_weight':1,'action_weight':8}]}]
  with tempfile.TemporaryDirectory() as tmp:
   evaluated,proof=r.checked(c.ROOT,c.ROOT,episodes,Path(tmp))
   self.assertTrue(proof['verification']['kernel_checked']);self.assertEqual(evaluated['steps'],2)
if __name__=='__main__':unittest.main()
