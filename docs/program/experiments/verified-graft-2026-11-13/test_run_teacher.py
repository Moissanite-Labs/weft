"""Coordinator safety probes: no network, credentials or proof compilation."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import run_teacher as t

class CoordinatorTests(unittest.TestCase):
 def fixture(self,root):
  data=root/'data';(data/'instances').mkdir(parents=True)
  t.r.write(data/'instances/seed-211.json',t.g.instance(211))
  p=data/'prepared/requests/seed-211-compatible-round-1.json';t.r.write(p,{'packet':{}})
  return data,p
 def test_reserves_before_process(self):
  with tempfile.TemporaryDirectory() as name:
   root=Path(name);data,p=self.fixture(root)
   def launch(*args,**kwargs):
    ledger=t.r.read(data/'teacher-call-ledger.json')
    self.assertEqual(ledger,[{'call_id':'211/compatible/1','prompt_sha256':t.r.sha(p),'state':'started'}])
    self.assertEqual(kwargs['timeout'],660)
    raise subprocess.TimeoutExpired('redacted',660)
   with patch.object(t,'HERE',root),patch.object(t,'pincheck'),patch.dict(t.g.CONFIG,{'seeds':[211],'cases':['compatible']}),patch.object(t.subprocess,'run',side_effect=launch) as call:
    with self.assertRaisesRegex(ValueError,"duration exceeded"):t.run(Path('/mock/hermes'),Path('/mock/python'))
    self.assertEqual(call.call_count,1)
    self.assertEqual(t.r.read(data/"teacher-call-ledger.json")[0]["state"],"timeout")
    self.assertFalse(t.r.read(data/"teacher-transport/seed-211-compatible-round-1/process.json")["response_fabricated"])
 def test_started_opportunity_not_retried(self):
  with tempfile.TemporaryDirectory() as name:
   root=Path(name);data,p=self.fixture(root)
   t.r.write(data/'teacher-call-ledger.json',[{'call_id':'211/compatible/1','prompt_sha256':t.r.sha(p),'state':'started'}])
   with patch.object(t,'HERE',root),patch.object(t,'pincheck'),patch.dict(t.g.CONFIG,{'seeds':[211],'cases':['compatible']}),patch.object(t.subprocess,'run') as call:
    with self.assertRaisesRegex(ValueError,'manual audit'):t.run(Path('/mock/hermes'),Path('/mock/python'))
    call.assert_not_called()
 def test_wrong_terminal_retains_provenance_without_candidates(self):
  with tempfile.TemporaryDirectory() as name:
   root=Path(name);data,p=self.fixture(root);transport=data/'transport'
   t.r.write(transport/'record.json',{'status':'parsed','parsed_batch':{'candidates':[{}]*4}})
   t.r.write(transport/'terminal-events.json',[{'type':'response.completed','status':'completed','model':'other'}])
   result=t.r.read(t.bind(data,211,'compatible',1,p,transport))
   self.assertNotIn('candidates',result)
   self.assertEqual(result['transport_status'],'terminal_identity_error')
   self.assertEqual(result['binding']['terminal_model'],'other')
   self.assertIn('response_record_sha256',result['binding'])
 def test_prompt_tamper_stops_resume(self):
  with tempfile.TemporaryDirectory() as name:
   root=Path(name);data,p=self.fixture(root)
   t.r.write(data/'teacher-call-ledger.json',[{'call_id':'211/compatible/1','prompt_sha256':'wrong','state':'started'}])
   with patch.object(t,'HERE',root),patch.object(t,'pincheck'),patch.dict(t.g.CONFIG,{'seeds':[211],'cases':['compatible']}),patch.object(t.subprocess,'run') as call:
    with self.assertRaisesRegex(ValueError,'prompt mismatch'):t.run(Path('/mock/hermes'),Path('/mock/python'))
    call.assert_not_called()
 def test_cached_selection_is_validated_before_skipping_or_calling(self):
  with tempfile.TemporaryDirectory() as name:
   root=Path(name);data,p=self.fixture(root)
   t.r.write(data/'teacher/seed-211.compatible/round-1/round.json',{'exact_target_reached':True})
   with patch.object(t,'HERE',root),patch.object(t,'pincheck'),patch.dict(t.g.CONFIG,{'seeds':[211],'cases':['compatible']}),patch.object(t.r,'validate_teacher_record',side_effect=ValueError('changed selection')) as validate,patch.object(t.subprocess,'run') as call:
    with self.assertRaisesRegex(ValueError,'changed selection'):t.run(Path('/mock/hermes'),Path('/mock/python'))
    validate.assert_called_once()
    call.assert_not_called()
if __name__=='__main__':unittest.main()
