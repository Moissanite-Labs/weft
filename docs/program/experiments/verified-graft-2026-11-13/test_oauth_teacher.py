import json
import unittest
from types import SimpleNamespace as N
from unittest.mock import Mock
from oauth_teacher import propose,request_record,body_from_kwargs,terminal_metadata
class Tests(unittest.TestCase):
 def test_invalid_action_retained(self):
  batch={'candidates':[{'mode':'INVALID','delta':[]}]*4};c=Mock()
  c.chat.completions.create.return_value=N(choices=[N(message=N(content=json.dumps(batch),reasoning='PRIVATE'))],usage=N())
  r=propose({},c);self.assertEqual(r['status'],'parsed');self.assertNotIn('PRIVATE',json.dumps(r))
 def test_malformed_retained(self):
  c=Mock();c.chat.completions.create.return_value=N(choices=[N(message=N(content='broken'))],usage=N())
  self.assertEqual(propose({},c)['output_text'],'broken')
 def test_no_retry(self):
  c=Mock();c.chat.completions.create.side_effect=RuntimeError('Bearer SECRET')
  self.assertNotIn('SECRET',json.dumps(propose({},c)));self.assertEqual(c.chat.completions.create.call_count,1)
 def test_real_hermes_shaping(self):
  from agent.auxiliary_client import _CodexCompletionsAdapter
  from agent.sdk_transform_bypass import bypass_sdk_request_transform
  fake=N(base_url='https://chatgpt.com/backend-api/codex')
  shaped,model,_=_CodexCompletionsAdapter(fake,'gpt-6-astra')._build_responses_kwargs(request_record({})['request'])
  shaped.pop('_issuer_kind',None)
  body=body_from_kwargs(bypass_sdk_request_transform({**shaped,'stream':True}))
  self.assertEqual(body['model'],'gpt-6-astra');self.assertTrue(body['input']);self.assertFalse(body.get('tools'))
 def test_visible_stream_only(self):
  self.assertEqual(terminal_metadata(N(type='response.output_text.delta',delta='visible')),{'type':'response.output_text.delta','delta':'visible'})
  self.assertIsNone(terminal_metadata(N(type='response.reasoning_text.delta',delta='PRIVATE')))
  self.assertEqual(terminal_metadata(N(type='response.refusal.delta',delta='refused'))['delta'],'refused')
 def test_terminal(self):
  r=N(id='r1',model='gpt-6-astra',status='completed',usage={'input_tokens':5,'input_tokens_details':{'cached_tokens':2},'output_tokens_details':{'reasoning_tokens':3}})
  meta=terminal_metadata(N(type='response.completed',response=r))
  self.assertEqual(meta['usage']['output_tokens_details']['reasoning_tokens'],3)
if __name__=='__main__':unittest.main()
