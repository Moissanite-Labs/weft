import copy
from pathlib import Path
import tempfile
import unittest
import graft as g
import run_graft as r

class GraftTests(unittest.TestCase):
 def test_mechanical_alignment_uses_only_visible_packet(self):
  for seed in g.CONFIG['seeds']:
   exp=g.instance(seed)
   for case in g.CONFIG['cases']:
    visible=g.packet(exp,case);self.assertEqual(g.rank([row['receiver_features'] for row in visible['calibration']]),6)
    for key in ('target','canonical_host','canonical_donor','donor_permutation','receiver_permutation','donor_signs','receiver_signs'):
     self.assertNotIn(key,visible)
    self.assertEqual(len(g.infer_alignments(visible)),1)
    action=next(x['action'] for x in g.controls(visible) if x['label']=='mechanical_alignment')
    deployed=g.deployment(visible,action)
    self.assertEqual(g.function_for(deployed,'new'),exp['target'])
    if case=='saturated':self.assertEqual(deployed['root'],exp['host']);self.assertEqual(deployed['cell_count'],2)
    for v in visible['protected_basis']:self.assertEqual(g.apply(deployed['root'],v),g.apply(exp['host'],v))
 def test_saturated_nonzero_graft_cannot_satisfy_preservation(self):
  exp=g.instance(211);visible=g.packet(exp,'saturated');action=g.proposed(visible,g.aligned_donor(visible,g.infer_alignments(visible)[0]));action['mode']='graft'
  with self.assertRaises(ValueError):g.validate_action(action,visible)
  witness=g.conflict_witness(exp);self.assertNotEqual(witness['host_output'],witness['target_output'])
 def test_rank_five_packet_has_two_distinct_completions(self):
  for seed in g.CONFIG['seeds']:
   fixture=r.rank5_fixture(g.instance(seed));self.assertTrue(fixture['packets_identical']);self.assertEqual(fixture['receiver_calibration_rank'],5)
   self.assertEqual(len(fixture['completions']),2);self.assertNotEqual(*fixture['different_outputs'])
 def test_confirmation_rejects_explicit_overfit_without_rerank(self):
  fixture=g.overfit_fixture();self.assertEqual(fixture['scores'],{'parent_A':2,'child_A':0,'parent_B':2,'child_B':18});self.assertFalse(fixture['adopted'])
  self.assertFalse(g.confirmed(10,10,10,9));self.assertFalse(g.confirmed(10,9,10,10));self.assertTrue(g.confirmed(10,9,10,9))
 def test_exact_data_schema_and_distinct_fork(self):
  visible=g.packet(g.instance(211),'compatible')
  for action in ({'mode':'graft','delta':[[True]*6,[0]*6]},{'mode':'graft','delta':[[1.0]*6,[0]*6]},{'mode':'fork','delta':copy.deepcopy(g.ZERO)},{'mode':'abstain','delta':[[1]*6,[0]*6]}):
   with self.assertRaises(ValueError):g.validate_action(action,visible)
 def test_feedback_does_not_disclose_confirmation_or_final(self):
  record={'round':1,'candidates':[{'index':0,'action':{'mode':'abstain','delta':g.ZERO},'eligible':True,'A':{'SSE':10},'B':{'SSE':99}}],'selected_deployment':{'root':g.ZERO},'parent_B':{'SSE':98}}
  feedback=r.teacher_feedback(record);text=str(feedback)
  self.assertNotIn('99',text);self.assertNotIn('parent_B',text);self.assertNotIn('B_SSE',text)
 def test_teacher_response_schema_no_invented_or_extra_children(self):
  with self.assertRaises(ValueError):r.extract_candidates({'candidates':[]})
  with self.assertRaises(ValueError):r.extract_candidates({'candidates':[{}]*4,'code':'bad'})
 def test_bound_transport_and_wrong_terminal_are_not_anonymous_actions(self):
  import json
  from prepare_teacher import envelope
  from oauth_teacher import request_record,SYSTEM
  from run_teacher import bind
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);r.prepare(out);exp=g.instance(211);visible=g.packet(exp,'compatible');parent=r.parent_deployment(visible)
   original=envelope(visible,parent,1,[]);prompt=out/'prepared/requests/seed-211-compatible-round-1.json';r.write(prompt,original)
   transport=out/'teacher-transport/synthetic-fixture';transport.mkdir(parents=True)
   # Synthetic transport fixture only; no model call and no study response file.
   actions=[{'mode':'abstain','delta':copy.deepcopy(g.ZERO)} for _ in range(4)]
   request=request_record(original);record={**request,'status':'parsed','parsed_batch':{'candidates':actions},'output_text':json.dumps({'candidates':actions})}
   r.write(transport/'record.json',record)
   r.write(transport/'wire.json',[{'model':'gpt-6-astra','store':False,'instructions':SYSTEM,'input':[{'role':'user','content':[{'type':'input_text','text':json.dumps(original,sort_keys=True,separators=(',',':'))}]}]}])
   r.write(transport/'terminal-events.json',[{'type':'response.completed','status':'completed','model':'gpt-6-astra'}])
   package=r.read(bind(out,211,'compatible',1,prompt,transport))
   self.assertTrue(r.validate_transport(out,package,exp,'compatible',1,parent,None))
   r.write(transport/'terminal-events.json',[{'type':'response.output_text.delta','delta':'wrong text'},{'type':'response.completed','status':'completed','model':'gpt-6-astra'}])
   bad_stream=r.read(bind(out,211,'compatible',1,prompt,transport))
   with self.assertRaises(ValueError):r.validate_transport(out,bad_stream,exp,'compatible',1,parent,None)
   r.write(transport/'terminal-events.json',[{'type':'response.completed','status':'completed','model':'gpt-6-astra'}])
   changed=copy.deepcopy(package);changed['binding']['seed']=337
   with self.assertRaises(ValueError):r.validate_transport(out,changed,exp,'compatible',1,parent,None)
   r.write(transport/'terminal-events.json',[{'type':'response.completed','status':'completed','model':'wrong-model'}])
   failed_path=bind(out,211,'compatible',1,prompt,transport);failed=r.read(failed_path)
   self.assertEqual(failed['transport_status'],'terminal_identity_error');self.assertFalse(r.validate_transport(out,failed,exp,'compatible',1,parent,None))
   outcome=r.teacher_round(out,211,'compatible',1,failed_path)
   self.assertFalse(outcome['adopted']);self.assertEqual(outcome['selected_deployment'],parent)
   r.validate_teacher_record(out,exp,'compatible',1,parent,None)
   path=out/'teacher'/r.prefix(211,'compatible')/'round-1/round.json';value=r.read(path);value['selected_deployment']['root'][0][0]+=1;r.write(path,value)
   with self.assertRaises(ValueError):r.validate_teacher_record(out,exp,'compatible',1,parent,None)

 def test_exact_rank_matches_signed_permutation(self):
  exp=g.instance(337);self.assertEqual(g.rank(exp['native_basis']),3);self.assertEqual(g.rank(exp['full_basis']),6)
if __name__=='__main__':unittest.main()
