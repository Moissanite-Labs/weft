"""Offline-only review reproductions. Never opens API transport sockets."""
import importlib.util
from importlib.machinery import SourceFileLoader
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import urllib.error
from unittest.mock import patch
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--supplied-file',type=Path,default=Path(__file__).with_name('supplied-harness.py.txt'))
args=parser.parse_args()
SOURCE=args.supplied_file.resolve()
spec=importlib.util.spec_from_loader('review_harness',SourceFileLoader('review_harness',str(SOURCE)));h=importlib.util.module_from_spec(spec);sys.modules[spec.name]=h;spec.loader.exec_module(h)
results={'supplied_file_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'scope':'Offline synthetic probes; urlopen mocked; no credentials or paid calls'}
# Underestimated input and unreserved standard-tier fallback independently exceed budget.
for name,actual_input,tier in [('input_underestimate',20000,'flex'),('fallback_tier','4500','default')]:
 ledger=h.ThreadSafeBudgetLedger(.06);reserved=ledger.reserve_for_turn('gpt-6-astra','flex',1000,4500)
 ledger.settle_turn(reserved,'gpt-6-astra',tier,{'input_tokens':int(actual_input),'output_tokens':1000})
 results[name]={'reserved':reserved,'snapshot':ledger.snapshot()}
# Cache writes are absent from settlement despite a separate usage field.
ledger=h.ThreadSafeBudgetLedger(1)
r=ledger.reserve_for_turn('gpt-6-astra','default',0,1000)
ledger.settle_turn(r,'gpt-6-astra','default',{'input_tokens':1000,'input_tokens_details':{'cached_tokens':0,'cache_write_tokens':1000},'output_tokens':0})
results['cache_write_accounting']={'ledger':ledger.snapshot(),'at_requested_write_rate_12_5_per_million':.0125}
# URLopen is mocked before constructing/calling live transport; no network.
seen=[]
def timeout(req,**kwargs):
 seen.append(json.loads(req.data)['service_tier']);raise urllib.error.URLError('synthetic unknown-completion timeout')
with patch.object(h.urllib.request,'urlopen',timeout),patch.object(h.time,'sleep',lambda x:None):
 transport=h.make_live_openai_responses_transport('offline-dummy-not-a-secret')
 try:transport({'service_tier':'flex'})
 except RuntimeError as exc:results['ambiguous_retry']={'attempts':seen,'exception':str(exc)}
with tempfile.TemporaryDirectory(prefix='issue111-review-') as tmp:
 root=Path(tmp);ws=root/'workspace';ws.mkdir();sentinel=root/'outside-workspace.txt';sentinel.write_text('LOCAL-SYNTHETIC-SENTINEL')
 results['filesystem_escape']=h.run_cell_bench_snippet("from pathlib import Path\nprint(Path('../outside-workspace.txt').read_text())\nPath('../outside-write.txt').write_text('outside write succeeded')",ws)
 results['outside_write_succeeded']=(root/'outside-write.txt').exists()
 codec=ws/'codec.py'
 codec.write_text('''import hashlib,json,sys
raw=sys.modules['__main__'].raw_data
print(json.dumps({'ok':True,'exact_match':True,'edge_ok':True,'raw_len':len(raw),'compressed_len':1,'ratio':999999,'recovered_sha256':hashlib.sha256(raw).hexdigest()}),flush=True)
raise SystemExit(0)
''')
 results['forged_verifier']=h.verify_codec_morphism_isolated(codec,b'not actually encoded or decoded',ws)
 codec.write_text('''cache=b''
def encode(data):
 global cache
 cache=data
 return b'x'
def decode(blob):
 return cache
''')
 results['stateful_one_byte_false_positive']=[h.verify_codec_morphism_isolated(codec,payload,ws) for payload in (b'first synthetic payload',b'different second synthetic payload')]
 # Demonstrate that a fresh decoder cannot recover either payload from the single encoded byte.
 fresh={};exec(codec.read_text(),fresh)
 results['fresh_decoder_recovered']=fresh['decode'](b'x').hex()

assert results['input_underestimate']['snapshot']['spent_usd'] > .06
assert results['fallback_tier']['snapshot']['spent_usd'] > .06
assert results['outside_write_succeeded']
assert 'LOCAL-SYNTHETIC-SENTINEL' in results['filesystem_escape']
assert results['forged_verifier']['ok']
assert all(row['ok'] and row['compressed_len']==1 for row in results['stateful_one_byte_false_positive'])
assert results['fresh_decoder_recovered']==''
assert len(results['ambiguous_retry']['attempts'])==6
print(json.dumps(results,indent=2))
