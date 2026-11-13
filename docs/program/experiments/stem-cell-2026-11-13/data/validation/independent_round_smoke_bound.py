import hashlib,json,shutil,tempfile,time
from pathlib import Path
import colony as c
import run_experiment as r
base=Path(__file__).resolve()
archive=Path('data/validation/independent_round_smoke_bound')
with tempfile.TemporaryDirectory(prefix='stem-independent-round-') as directory:
 out=Path(directory);r.write(out/'config.json',c.CONFIG)
 for seed in c.CONFIG['seeds']:r.write(out/'experiments'/f'seed-{seed}.json',c.experiment(seed))
 for seed in c.CONFIG['seeds']:
  for branch in r.ARMS:r.make_request(out,r.read(out/'experiments'/f'seed-{seed}.json'),branch,1,c.ROOT,[])
 r.register(out)
 pending=r.process(out,'normal');path=Path(pending[0]);request=r.read(path)
 wire=request|{'store':False,'service_tier':'default'};payload=json.dumps(wire,ensure_ascii=False).encode()
 path.with_suffix('.wire.json').write_bytes(payload+b'\n')
 children=[c.ROOT,c.FIXED,c.ROOT|{'gain_num':0},c.ROOT|{'bias':1}]
 proposal={'hypothesis':'Synthetic offline integration control, not an Astra response.','children':[{'label':str(i),'genome':g} for i,g in enumerate(children)]}
 envelope={'synthetic_offline_control':True,'request_file':path.name,'request_sha256':hashlib.sha256(payload).hexdigest(),'response':{'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(proposal)}]}]}}
 r.write(path.with_suffix('.response.json'),envelope)
 start=time.monotonic();remaining=r.process(out,'normal');elapsed=time.monotonic()-start
 selections=list((out/'selections').glob('*.json'));assert len(selections)==1
 record=r.read(selections[0]);assert len(record['children'])==4
 assert all(x['proof']['verification']['kernel_checked'] and x['proof']['verification']['axioms']==[] for x in record['children'])
 assert record['teacher_selection_proof']['accepted'] and record['random_selection_proof']['accepted']
 # Reconsume saved selection without changing it, checking deterministic continuation.
 before=c.fingerprint(record);r.process(out,'normal');assert c.fingerprint(r.read(selections[0]))==before
 regressions={}
 def rejected(label,call):
  try:call()
  except ValueError as error:regressions[label]={'rejected':True,'reason':str(error)}
  else:raise AssertionError('Binding mutation accepted: '+label)
 registration=r.read(out/'registration.json')
 rejected('wrong_response_filename',lambda:r.validate_response_binding(path,envelope|{'request_file':'other-request.json'},registration))
 rejected('wrong_wire_hash',lambda:r.validate_response_binding(path,envelope|{'request_sha256':'0'*64},registration))
 altered=dict(record);altered['selected_genome']=c.ROOT
 rejected('changed_selection',lambda:r.validate_retained_selection(out,selections[0],altered))
 cert=next((out/'proofs').rglob('Certificate.lean'));original=cert.read_bytes();cert.write_bytes(original+b'\n-- corruption probe\n')
 rejected('changed_certificate',lambda:r.validate_retained_selection(out,selections[0],record));cert.write_bytes(original)
 from unittest.mock import patch
 with patch.object(r,'code_pins',return_value={'changed':'yes'}):rejected('changed_code_pins',lambda:r.validate_registration(out))
 r.write(out/'binding_regressions.json',regressions)
 shutil.copytree(out,archive,dirs_exist_ok=True)
 summary={'scope':'One synthetic four-child round through real Lean gates, not a paid model experiment. Temporary artifact root; archived separately under validation.', 'elapsed_seconds':elapsed,'teacher_candidates':4,'teacher_valid':sum(x['valid'] for x in record['children']),'selected_index':record['selected_index'],'selected_genome':record['selected_genome'],'selected_validation_cost':record['selected_validation']['total_cost'],'parent_validation_cost':record['unchanged_parent']['validation']['total_cost'],'selection_certificates_empty_axioms':all(record[k]['axioms']==[] for k in ('teacher_selection_proof','random_selection_proof')),'selection_reuse_identical':True,'remaining_requests':len(remaining),'paid_calls':0}
 r.write(archive/'summary.json',summary);print(json.dumps(summary,indent=2))
